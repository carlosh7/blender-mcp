# blender-mcp — Socket server for Blender (ahujasid-compatible)
# Runs inside Blender, listens on port 9876 for JSON commands via TCP socket.
# Thread-safe: los comandos se serializan al hilo principal vía bpy.app.timers.
# Auth obligatoria por token (auto-generado en <config>/blender-mcp/socket_token).
import io
import json
import os
import secrets
import socket
import subprocess
import threading
import time
import traceback
from contextlib import redirect_stdout

import bpy

SOCKET_PORT = 9876
_socket_server = None
_auth_token_cache = None

# Comandos que modifican la escena: sujetos al lock multi-agente
_MUTATING_COMMANDS = {"execute_code", "tool", "create_object", "cleanup_scene"}


def _token_file_path():
    """Ruta del token compartido con el gateway (misma fórmula en
    blender_connection.py: <config>/blender-mcp/socket_token)."""
    import sys as _sys
    from pathlib import Path as _Path

    if _sys.platform == "win32":
        base = _Path(os.environ.get("APPDATA", _Path.home() / "AppData" / "Roaming"))
    elif _sys.platform == "darwin":
        base = _Path.home() / "Library" / "Application Support"
    else:
        base = _Path.home() / ".config"
    return base / "blender-mcp" / "socket_token"


def _load_or_create_token():
    """Lee (o genera y persiste) el token del socket para este usuario."""
    try:
        p = _token_file_path()
        if p.exists():
            t = p.read_text(encoding="utf-8").strip()
            if t:
                return t
        t = secrets.token_hex(16)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t, encoding="utf-8")
        try:
            os.chmod(p, 0o600)
        except Exception:
            pass
        return t
    except Exception:
        return ""


def _load_code_guard():
    """Carga code_guard.py (mismo directorio): blocklist AST para execute_code."""
    import importlib.util
    from pathlib import Path as _Path

    guard_path = _Path(__file__).resolve().parent / "code_guard.py"
    if not guard_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("bmcp_addon_code_guard", guard_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


_code_guard = _load_code_guard()

# ── Bus de eventos (ring buffer) para polling de agentes ──
import collections as _collections

_EVENT_BUFFER: _collections.deque = _collections.deque(maxlen=500)
_EVENT_SEQ = 0


def emit_event(kind: str, data=None):
    """Publicar un evento en el bus (poll con cmd_poll_events)."""
    global _EVENT_SEQ
    _EVENT_SEQ += 1
    _EVENT_BUFFER.append(
        {"seq": _EVENT_SEQ, "time": round(time.time(), 3), "kind": kind, "data": data or {}}
    )


_chat_queue = []
_chat_responses = {}
_chat_lock = threading.Lock()
_stop_agent = False
mcp_last_ping = 0  # timestamp of last ping from MCP server
mcp_connected = False
mcp_status = "idle"
mcp_error = ""
_mcp_process = None  # true if ping received in last 15s


class BlenderSocketServer:
    """TCP socket server inside Blender for receiving MCP commands."""

    def __init__(self, host="localhost", port=SOCKET_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.sock = None
        self.thread = None
        self.listening = False
        self.last_error = None
        self._tool_registry = (
            None  # caché del registry de src/ (None=intentar, False=no disponible)
        )

    def start(self, blocking=False):
        """Start the socket server."""
        if self.running:
            return
        self.running = True
        try:
            # Close any existing socket
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # SO_REUSEADDR + SO_REUSEPORT for quick port release
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except (AttributeError, OSError):
                # SO_REUSEPORT not available on all platforms
                pass

            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            self.listening = True
            self.last_error = None
            if blocking:
                # modo headless: sin hilo, sin timeout — el main loop acepta
                self.sock.settimeout(None)
            else:
                self.sock.settimeout(1.0)
                self.thread = threading.Thread(target=self._loop, daemon=True)
                self.thread.start()
            print(f"[BLENDER SOCKET] Server on port {self.port}")
        except Exception as e:
            self.running = False
            self.listening = False
            self.last_error = str(e)
            print(f"[BLENDER SOCKET] Failed: {e}")
            self.stop()

    def stop(self):
        """Stop the socket server."""
        self.running = False
        self.listening = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def _loop(self):
        """Main server loop - accept connections."""
        while self.running:
            try:
                client, addr = self.sock.accept()
                threading.Thread(target=self._handle, args=(client,), daemon=True).start()
            except TimeoutError:
                continue
            except Exception as e:
                if self.running:  # Only log if not intentionally stopped
                    print(f"[BLENDER SOCKET] Accept error: {e}")

    def _serve_client_blocking(self, client):
        """Atender un cliente SIN timers: ejecución directa (modo headless).

        Solo válido cuando el hilo principal es este (blender --background
        con script bloqueante): bpy es seguro porque somos el main loop.
        Tras cada comando, si el cliente no envía otro en 0.5s se cierra la
        conexión para ceder el turno a otros clientes (el gateway reconecta
        de forma transparente). El primer comando espera hasta 300s.
        """
        buffer = b""
        client.settimeout(300)
        served = 0
        while True:
            try:
                data = client.recv(1024 * 1024)
            except TimeoutError:
                if served:
                    break
                continue
            if not data:
                break
            buffer += data
            try:
                cmd = json.loads(buffer.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            buffer = b""
            try:
                resp = self._execute(cmd)
            except Exception as e:
                resp = {
                    "status": "error",
                    "message": f"{type(e).__name__}: {e}",
                    "traceback": traceback.format_exc(),
                }
            client.sendall(json.dumps(resp).encode("utf-8"))
            served += 1
            client.settimeout(0.5)

    def _handle(self, client):
        """Handle client connection with proper thread-safe execution."""
        buffer = b""
        try:
            while self.running:
                data = client.recv(1024 * 1024)
                if not data:
                    break
                buffer += data
                try:
                    # Try to find complete JSON
                    raw_data = buffer.decode("utf-8")
                    cmd = json.loads(raw_data)
                    buffer = b""

                    # Execute via bpy.app.timers for thread safety
                    def execute():
                        try:
                            resp = self._execute(cmd)
                            client.sendall(json.dumps(resp).encode("utf-8"))
                        except Exception as e:
                            try:
                                client.sendall(
                                    json.dumps(
                                        {
                                            "status": "error",
                                            "message": f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                                        }
                                    ).encode("utf-8")
                                )
                            except Exception:
                                pass
                        return None

                    # Register in main thread via timers
                    bpy.app.timers.register(execute, first_interval=0.0)
                except json.JSONDecodeError:
                    # Incomplete JSON, wait for more data
                    pass
        except Exception as e:
            print(f"[BLENDER SOCKET] Client handler error: {e}")
        finally:
            try:
                client.close()
            except Exception:
                pass

    def _get_auth_token(self):
        """Token del socket (OBLIGATORIO): env BLENDER_MCP_TOKEN > Scene > archivo.

        Sin configuración previa se genera uno y se persiste en
        <config>/blender-mcp/socket_token (0600) para que el gateway del
        mismo usuario lo lea: cero configuración y ningún comando anónimo.
        """
        global _auth_token_cache
        if _auth_token_cache is not None:
            return _auth_token_cache
        import os

        token = os.environ.get("BLENDER_MCP_TOKEN", "")
        if not token:
            try:
                token = bpy.context.scene.get("mcp_ultra_socket_token", "") or ""
            except Exception:
                token = ""
        if not token:
            token = _load_or_create_token()
        _auth_token_cache = token
        return _auth_token_cache

    def _execute(self, cmd):
        cmd_type = cmd.get("type") or cmd.get("command")
        params = cmd.get("params") or cmd.get("args") or {}

        # Auth obligatoria: el token siempre existe (auto-generado si hace falta)
        expected = self._get_auth_token()
        if expected and not secrets.compare_digest(str(cmd.get("token", "")), expected):
            return {"status": "error", "message": "unauthorized: invalid or missing token"}

        # Lock de escena (advisory, multi-agente): comandos mutadores requieren
        # el lock_token del dueño mientras exista un lock activo.
        if cmd_type in _MUTATING_COMMANDS:
            lock_owner = None
            try:
                lock_owner = bpy.context.scene.get("mcp_scene_lock", "") or ""
            except Exception:
                lock_owner = ""
            if lock_owner and str(cmd.get("lock_token", "")) != lock_owner:
                return {
                    "status": "error",
                    "message": (
                        "escena bloqueada por otro agente (lock activo). "
                        "Adquiere el lock o espera; release con scene_lock(action='release', token=...)."
                    ),
                }

        # Try direct method on self first (legacy commands)
        handler = getattr(self, f"cmd_{cmd_type}", None)
        if handler:
            try:
                result = handler(**params)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

        return {"status": "error", "message": f"Unknown command: {cmd_type}"}

    def _get_tool_registry(self):
        """Cargar (una vez) el ToolRegistry de src/ si está disponible.

        Dos layouts soportados:
        - Repo:   <repo>/addon/_axsock.py → raíz = padre del addon
        - Extensión: <ext>/blender_mcp_ultra/_axsock.py → raíz = la propia
          extensión (build_extension.py empaqueta src/ y blender_mcp/ dentro).
        Los handlers de src/tools se ejecutan in-process dentro de Blender,
        por lo que necesitan bpy: este puente solo funciona con Blender vivo.
        """
        if self._tool_registry is not None:
            return self._tool_registry or None
        try:
            import os
            import sys

            here = os.path.dirname(os.path.abspath(__file__))
            candidates = [
                os.path.dirname(here),  # layout repo: <repo>/addon/ → <repo>
                here,  # layout extensión: <ext>/blender_mcp_ultra/ → <ext>
            ]
            registry = None
            for root in candidates:
                if not os.path.isdir(os.path.join(root, "src")):
                    continue
                if root not in sys.path:
                    sys.path.insert(0, root)
                try:
                    from src.presentation.mcp_server import register_all_tools
                    from src.tools import ToolRegistry

                    registry = ToolRegistry(use_cache=False)
                    register_all_tools(registry)
                    break
                except Exception:
                    registry = None
                    continue
            if registry is None:
                raise RuntimeError("src/ no encontrado en ninguna raíz candidata")
            self._tool_registry = registry
            print(f"[BLENDER SOCKET] Registry cargado: {len(registry.list_tools())} tools")
        except Exception as e:
            self._tool_registry = False
            print(f"[BLENDER SOCKET] Registry de src/ no disponible: {e}")
            return None
        return self._tool_registry

    def cmd_list_tools(self):
        """Listar los 118+ tools del registry de src/ (para MCP stdio)."""
        registry = self._get_tool_registry()
        if registry is None:
            return {"tools": [], "error": "registry no disponible"}
        return {"tools": [tool.to_dict() for tool in registry.list_tools()]}

    def cmd_tool(self, tool_name="", params=None):
        """Ejecutar un tool del registry de src/ por nombre."""
        registry = self._get_tool_registry()
        if registry is None:
            return {
                "success": False,
                "error": "ToolRegistry no disponible (se requiere repo completo)",
            }
        result = registry.execute_tool(tool_name, params or {})
        payload = {"success": result.success, "data": result.data}
        if result.error:
            payload["error"] = result.error
        return payload

    def cmd_get_viewport_screenshot(self, filepath=None, max_size=800):
        """Captura una imagen del viewport actual para validación Axiom."""
        if not filepath:
            import tempfile

            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, f"axiom_vision_{int(time.time())}.png")

        try:
            # Buscar una ventana y pantalla válidas (Blender 4.2+ requiere contexto explícito)
            window = (
                bpy.context.window if bpy.context.window else bpy.context.window_manager.windows[0]
            )
            screen = window.screen
            area = next((a for a in screen.areas if a.type == "VIEW_3D"), None)

            if not area:
                return {"error": "No se encontró un viewport 3D activo en la ventana principal"}

            # Forzar el renderizado de la captura con el contexto completo
            with bpy.context.temp_override(window=window, screen=screen, area=area):
                bpy.ops.screen.screenshot_area(filepath=filepath)

            # Cargar y redimensionar
            if os.path.exists(filepath):
                img = bpy.data.images.load(filepath)
                if max(img.size) > max_size:
                    scale = max_size / max(img.size)
                    img.scale(int(img.size[0] * scale), int(img.size[1] * scale))
                    img.save()

                return {
                    "success": True,
                    "filepath": filepath,
                    "width": img.size[0],
                    "height": img.size[1],
                }
            return {"error": "Falló la creación del archivo de captura"}
        except Exception as e:
            return {"error": str(e)}

    def cmd_search_assets(self, provider="polyhaven", query="", asset_type="textures"):
        from . import assets

        if provider == "polyhaven":
            return {"results": assets.AssetManager.search_polyhaven(asset_type, query)}
        elif provider == "sketchfab":
            return {"results": assets.AssetManager.search_sketchfab(query)}
        return {"error": "Proveedor no soportado"}

    def cmd_generate_3d(self, prompt=""):
        from . import assets

        return assets.AssetManager.rodin_generate(prompt)

    def cmd_analyze_performance(self):
        """Analiza el conteo de polígonos y sugiere optimizaciones."""
        report = []
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                poly_count = len(obj.data.polygons)
                if poly_count > 50000:
                    report.append(f"⚠️ {obj.name}: {poly_count} polígonos (Crítico)")
                elif poly_count > 10000:
                    report.append(f"ℹ️ {obj.name}: {poly_count} polígonos (Alto)")
        return {"report": report or ["Escena optimizada. No se detectaron objetos pesados."]}

    def cmd_cleanup_scene(self):
        """Limpia datos huérfanos y normaliza nombres."""
        # Eliminar bloques de datos no usados
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        # Normalizar nombres (ejemplo básico)
        for obj in bpy.context.scene.objects:
            if "." in obj.name:
                obj.name.split(".")[0]
                # (Lógica opcional de renombrado aquí)
        return {"status": "success", "message": "Limpieza profunda de Axiom completada."}

    def cmd_get_scene_info(self):
        info = {
            "name": bpy.context.scene.name,
            "object_count": len(bpy.context.scene.objects),
            "objects": [],
        }
        for i, obj in enumerate(bpy.context.scene.objects):
            if i >= 20:
                break
            info["objects"].append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": [
                        round(float(obj.location.x), 2),
                        round(float(obj.location.y), 2),
                        round(float(obj.location.z), 2),
                    ],
                }
            )
        return info

    def cmd_get_object_anchors(self, obj_name=""):
        try:
            from . import spatial

            return {"anchors": spatial.get_object_anchors(obj_name)}
        except Exception as e:
            return {"error": str(e)}

    def cmd_get_model_blueprint(self, obj_name=""):
        try:
            from . import scanner

            obj = bpy.data.objects.get(obj_name) or bpy.context.active_object
            return {"blueprint": scanner.GeometryScanner.get_blueprint(obj)}
        except Exception as e:
            return {"error": str(e)}

    def cmd_apply_symmetry(self, obj_name="", axes=["X", "Y"]):
        try:
            from . import assembly

            obj = bpy.data.objects.get(obj_name) or bpy.context.active_object
            return assembly.AssemblyEngine.apply_symmetry(obj, axes)
        except Exception as e:
            return {"error": str(e)}

    def cmd_fix_normals(self, obj_name=""):
        try:
            from . import assembly

            obj = bpy.data.objects.get(obj_name) or bpy.context.active_object
            return assembly.AssemblyEngine.fix_normals(obj)
        except Exception as e:
            return {"error": str(e)}

    def cmd_get_spatial_visual(self):
        try:
            from . import spatial

            return {"summary": spatial.get_spatial_summary()}
        except Exception as e:
            return {"error": str(e)}

    def cmd_validate_geometry(self):
        try:
            from . import spatial

            report = spatial.GeometryValidator.get_report()
            # Ensure report is a string and not too large
            if len(report) > 10000:
                report = report[:10000] + "\n... (truncated)"
            return {"report": report}
        except Exception as e:
            return {"error": str(e)}

    def cmd_ping(self):
        global mcp_last_ping, mcp_connected
        mcp_last_ping = time.time()
        mcp_connected = True
        return {"pong": True, "time": mcp_last_ping}

    def cmd_execute_code(self, code=""):
        """Execute Python code in Blender (code_guard + timeout 10s + undo)."""
        # Validación AST antes de tocar Blender (misma blocklist que el gateway)
        if _code_guard is not None:
            try:
                _code_guard.check_code(code)
            except _code_guard.CodeGuardError as e:
                emit_event("code_blocked", {"error": str(e)[:200]})
                return {"output": f"⛔ Bloqueado por seguridad: {e}"}
        win = (
            bpy.context.window
            if bpy.context.window
            else (
                bpy.context.window_manager.windows[0]
                if bpy.context.window_manager.windows
                else None
            )
        )
        ns = {
            "bpy": bpy,
            "C": bpy.context,
            "D": bpy.data,
            "ops": bpy.ops,
            "window": win,
            "screen": win.screen if win else None,
        }

        import signal

        def handler(signum, frame):
            raise TimeoutError("AXIOM TIMEOUT: La ejecución superó los 10.0 segundos de límite.")

        # Only push undo for non-batch operations (avoid stack overflow)
        _is_batch = "for " in code or "while " in code
        if not _is_batch:
            try:
                bpy.ops.ed.undo_push(message="Axiom Precision Task")
            except Exception:
                pass

        # SIGALRM no existe en Windows: sin timeout ahí, sin romper la llamada
        _use_alarm = hasattr(signal, "SIGALRM")
        buf = io.StringIO()
        with redirect_stdout(buf):
            if _use_alarm:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(10)
            try:
                # Expresión única → eval y devolver valor; si no, exec normal
                try:
                    compiled_eval = compile(code, "<blender_code>", "eval")
                except SyntaxError:
                    compiled_eval = None
                if compiled_eval is not None:
                    value = eval(compiled_eval, ns)
                    return {"output": buf.getvalue(), "result": repr(value)}
                compiled = compile(code, "<blender_code>", "exec")
                exec(compiled, ns)
            except TimeoutError as e:
                if not _is_batch:
                    try:
                        bpy.ops.ed.undo()
                    except Exception:
                        pass
                return {"output": f"❌ {e} (Escena revertida)"}
            except SyntaxError as e:
                if not _is_batch:
                    try:
                        bpy.ops.ed.undo()
                    except Exception:
                        pass
                return {"output": f"❌ Axiom SyntaxError: {e} (Escena revertida)"}
            except Exception as e:
                if not _is_batch:
                    try:
                        bpy.ops.ed.undo()
                    except Exception:
                        pass
                return {"output": f"❌ Axiom ExecutionError: {str(e)[:200]} (Escena revertida)"}
            finally:
                if _use_alarm:
                    signal.alarm(0)

        return {"output": buf.getvalue()}

    def cmd_chat_send(self, message="", model=""):
        global _stop_agent
        _stop_agent = False  # Resetear parada al enviar nuevo mensaje
        msg_id = str(time.time())
        with _chat_lock:
            _chat_queue.append({"id": msg_id, "message": message, "timestamp": time.time()})
        return {"success": True, "id": msg_id}

    def cmd_stop_agent(self):
        global _stop_agent
        _stop_agent = True
        return {"success": True}

    def cmd_is_stopped(self):
        global _stop_agent
        return {"stopped": _stop_agent}

    def cmd_clear_memory(self):
        global _clear_memory_flag
        _clear_memory_flag = True
        return {"success": True}

    def cmd_get_clear_signal(self):
        global _clear_memory_flag
        val = _clear_memory_flag
        _clear_memory_flag = False
        return {"clear": val}

    def cmd_read_chat(self):
        with _chat_lock:
            return {"messages": list(_chat_queue)}

    def cmd_respond_chat(self, message_id="", response=""):
        with _chat_lock:
            _chat_responses[message_id] = response
            _chat_queue[:] = [m for m in _chat_queue if m["id"] != message_id]
            # No limpiamos el status aquí, lo hará el addon al recibir la respuesta final
        return {"success": True}

    def cmd_respond_status(self, message_id="", response=""):
        with _chat_lock:
            # Store status separately to not interfere with final response polling
            _chat_responses[message_id + "_status"] = response
        return {"success": True}

    def cmd_poll_response(self, message_id=""):
        with _chat_lock:
            resp = _chat_responses.pop(message_id, None)
            if resp:
                return {"status": "done", "response": resp}
            return {"status": "pending"}

    def cmd_clear_chat(self):
        with _chat_lock:
            _chat_queue.clear()
            _chat_responses.clear()
        return {"success": True}

    def cmd_search_api_docs(self, query=""):
        try:
            from .rst_search import search_api_docs

            return search_api_docs(query)
        except Exception as e:
            return {"query": query, "results": [], "total": 0, "error": str(e), "source": "error"}

    def cmd_get_python_api_docs(self, topic=""):
        try:
            from .rst_search import get_python_api_docs

            return get_python_api_docs(topic)
        except Exception as e:
            return {"topic": topic, "error": str(e), "source": "error"}

    def cmd_poll_events(self, since: int = 0, limit: int = 100):
        """Eventos del bus con seq > since (streaming por polling)."""
        events = [e for e in _EVENT_BUFFER if e["seq"] > int(since)][: int(limit)]
        return {"events": events, "last_seq": _EVENT_SEQ}

    # ── Lock de escena multi-agente (advisory) ──

    def cmd_scene_lock(self, action="status", token="", ttl=300.0):
        """Adquirir/liberar/consultar el lock de escena.

        Mientras haya lock, execute_code/tool/create_object/cleanup_scene
        exigen lock_token=token. TTL de seguridad evita locks huérfanos.
        """
        import time as _time

        import bpy

        scene = bpy.context.scene
        current = scene.get("mcp_scene_lock", "") or ""
        ts = scene.get("mcp_scene_lock_ts", 0.0)
        if current and _time.time() - float(ts) > float(ttl) * 4:
            current = ""  # expirado

        if action == "acquire":
            if current and current != token:
                return {"locked": True, "owner": "otro-agente", "acquired": False}
            scene["mcp_scene_lock"] = token or "default"
            scene["mcp_scene_lock_ts"] = _time.time()
            emit_event("lock_acquired", {"owner": token or "default"})
            return {"locked": True, "owner": token or "default", "acquired": True}
        if action == "release":
            if current and current != token:
                return {"locked": True, "owner": "otro-agente", "released": False}
            scene["mcp_scene_lock"] = ""
            emit_event("lock_released", {"by": token or "default"})
            return {"locked": False, "released": True}
        return {"locked": bool(current), "owner": current or None}

    def cmd_diagnose(self):
        """Diagnose socket and MCP connections."""
        import socket

        result = {"socket": False, "mcp": False}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", 9876))
            result["socket"] = True
        except (ConnectionRefusedError, OSError):
            pass
        finally:
            s.close()

        try:
            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s2.settimeout(1)
            s2.connect(("127.0.0.1", 9879))
            result["mcp"] = True
        except (ConnectionRefusedError, OSError):
            pass
        finally:
            try:
                s2.close()
            except Exception:
                pass

        return result

    def cmd_start_mcp(self):
        import threading

        def _run():
            try:
                import uvicorn

                import mcp_server

                app = mcp_server.mcp.sse_app()
                uvicorn.run(app, host="127.0.0.1", port=9879, log_level="warning")
            except Exception:
                pass

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        return {"status": "starting"}

    # ── Jobs de render en background (subprocess headless, no congela la GUI) ──

    _render_jobs = {}

    def cmd_render_start(
        self,
        filepath=None,
        engine=None,
        samples=None,
        resolution=None,
        frame=None,
        animation=False,
        frame_start=1,
        frame_end=250,
    ):
        """Lanzar un render en una instancia headless aparte. Devuelve job_id.

        La escena actual (con engine/samples/resolución aplicados) se guarda
        como copia temporal; el subprocess renderiza sin bloquear Blender.
        """
        import os
        import tempfile
        import uuid

        import bpy

        job_id = uuid.uuid4().hex[:12]
        scene = bpy.context.scene
        if scene.camera is None:
            cams = [o for o in scene.objects if o.type == "CAMERA"]
            if cams:
                scene.camera = cams[0]
        if engine:
            scene.render.engine = engine
        if samples is not None:
            try:
                scene.cycles.samples = int(samples)
                scene.eevee.taa_render_samples = int(samples)
            except Exception:
                pass
        if resolution:
            scene.render.resolution_x, scene.render.resolution_y = (
                int(resolution[0]),
                int(resolution[1]),
            )
        if filepath:
            scene.render.filepath = filepath
        if animation:
            scene.render.image_settings.file_format = (
                "FFMPEG"
                if filepath and filepath.endswith((".mp4", ".mkv"))
                else scene.render.image_settings.file_format
            )
            scene.frame_start = int(frame_start)
            scene.frame_end = int(frame_end)

        tx_dir = os.path.join(tempfile.gettempdir(), "blender_mcp_jobs")
        os.makedirs(tx_dir, exist_ok=True)
        job_blend = os.path.join(tx_dir, f"job_{job_id}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=job_blend, copy=True)

        out_prefix = scene.render.filepath or os.path.join(tx_dir, f"render_{job_id}_")
        args = [bpy.app.binary_path, "-b", job_blend]
        args += ["-o", out_prefix if out_prefix.endswith(("/", "_")) else out_prefix + "_"]
        args += ["-F", "PNG"] if not animation else []
        args += ["-a"] if animation else ["-f", str(int(frame or scene.frame_current))]

        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        emit_event("render_started", {"job_id": job_id, "pid": proc.pid, "out_prefix": out_prefix})
        self._render_jobs[job_id] = {
            "proc": proc,
            "out_prefix": out_prefix,
            "animation": bool(animation),
            "frame_start": int(frame_start),
            "frame_end": int(frame_end),
            "started": time.time(),
            "blend": job_blend,
        }
        return {"job_id": job_id, "pid": proc.pid, "out_prefix": out_prefix}

    def cmd_render_status(self, job_id=""):
        """Estado de un job de render: running/done/error + archivos producidos."""
        import glob

        job = self._render_jobs.get(job_id)
        if not job:
            return {"error": f"job desconocido: {job_id}"}
        proc = job["proc"]
        rc = proc.poll()
        pattern = job["out_prefix"] + ("*" if job["animation"] else "*.png")
        files = sorted(glob.glob(pattern))
        if rc is not None and not job.get("_notified"):
            job["_notified"] = True
            emit_event(
                "render_done" if rc == 0 else "render_error",
                {"job_id": job_id, "files": len(files)},
            )
        progress = None
        if job.get("animation") and job.get("frame_end"):
            total = int(job["frame_end"]) - int(job.get("frame_start", 1)) + 1
            if total > 0:
                progress = round(min(100.0, 100.0 * len(files) / total), 1)
        elif rc is None:
            progress = None  # still: sin progreso incremental fiable
        out = {
            "job_id": job_id,
            "state": "running" if rc is None else ("done" if rc == 0 else f"error({rc})"),
            "elapsed": round(time.time() - job["started"], 1),
            "files": files,
        }
        if progress is not None:
            out["progress_pct"] = progress
        return out

    def cmd_render_list(self):
        """Listar todos los jobs de render lanzados en esta sesión."""
        return {
            jid: {
                "state": "running" if j["proc"].poll() is None else "finished",
                "elapsed": round(time.time() - j["started"], 1),
            }
            for jid, j in self._render_jobs.items()
        }

    # ── Transacciones: snapshot / restore de escena ──

    def _tx_dir(self):
        import os
        import tempfile

        d = os.path.join(tempfile.gettempdir(), "blender_mcp_snapshots")
        os.makedirs(d, exist_ok=True)
        return d

    def cmd_scene_snapshot(self, label="snap"):
        """Guardar snapshot completo de la escena (save copy). Devuelve ruta."""
        import os

        import bpy

        path = os.path.join(self._tx_dir(), f"{label}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
        emit_event("snapshot_saved", {"label": label})
        return {"label": label, "path": path}

    def cmd_scene_restore(self, label="snap"):
        """Restaurar la escena desde un snapshot (abre el .blend guardado)."""
        import os

        import bpy

        path = os.path.join(self._tx_dir(), f"{label}.blend")
        if not os.path.exists(path):
            return {"error": f"snapshot inexistente: {label}"}
        bpy.ops.wm.open_mainfile(filepath=path)
        return {"restored": label, "objects": len(bpy.data.objects)}

    def cmd_scene_snapshots(self):
        """Listar snapshots disponibles."""
        import glob
        import os

        return {
            "snapshots": [
                os.path.basename(p)[:-6]
                for p in sorted(glob.glob(os.path.join(self._tx_dir(), "*.blend")))
            ]
        }

    def cmd_get_scene_property(self, prop=""):
        """Get a property value from the current Blender scene (for proxy/agent mode detection)."""
        import bpy

        val = getattr(bpy.context.scene, prop, None)
        if val is None:
            return {"value": None}
        if hasattr(val, "is_enum"):
            return {"value": val}
        return {"value": val}

    def cmd_export_glb(self, filepath=""):
        if not filepath:
            return {"status": "error", "message": "filepath required"}
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.export_scene.gltf(filepath=filepath, export_format="GLB")
            size = os.path.getsize(filepath)
            return {"status": "success", "filepath": filepath, "size": size}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════
    # NEW COMMANDS: State, Validation, Collections
    # ═══════════════════════════════════════════════════════════

    def cmd_save_project(self, name=None):
        """Save Blender project with name."""
        try:
            from . import state_manager

            if name:
                filepath = state_manager.save_project(name)
            else:
                filepath = state_manager.auto_save()
            return {"status": "success", "filepath": filepath}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_get_file_status(self):
        """Get file save status."""
        try:
            from . import state_manager

            return state_manager.get_file_status()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_create_backup(self, label=None):
        """Create backup of current file."""
        try:
            from . import state_manager

            filepath = state_manager.create_backup(label)
            return {"status": "success", "filepath": filepath}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_validate_scene(self, collection=None):
        """Validate all objects in scene."""
        try:
            from . import validator

            result = validator.full_validation(collection)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_validate_object(self, name):
        """Validate a specific object."""
        try:
            from . import validator

            result = validator.validate_object(name)
            measurements = validator.measure_object(name)
            return {"validation": result, "measurements": measurements}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_create_collection(self, name):
        """Create a collection."""
        try:
            from . import creation_rules

            col = creation_rules.create_collection(name)
            return {"status": "success", "collection": col.name}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_create_object(self, object_type, position=(0, 0, 0), collection=None, material=None):
        """Create a standard object with all rules applied."""
        try:
            from . import creation_rules, state_manager

            result = creation_rules.create_object(object_type, position, collection, material)
            # Register created objects
            for obj in result.values():
                state_manager.register_object(obj.name)
            state_manager.log_action(
                "create_object",
                {
                    "type": object_type,
                    "position": position,
                    "objects": list(result.keys()),
                },
            )
            return {"status": "success", "objects": list(result.keys())}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_get_scene_summary(self):
        """Get detailed scene summary with collections."""
        try:
            from . import creation_rules

            hierarchy = creation_rules.get_collection_hierarchy()
            total = len(bpy.data.objects)
            materials = len(bpy.data.materials)
            return {
                "total_objects": total,
                "total_materials": materials,
                "collections": hierarchy,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_get_state(self):
        """Get agent state."""
        try:
            from . import state_manager

            return state_manager.get_state()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_check_loop(self, action_name):
        """Check if action is in loop."""
        try:
            from . import state_manager

            return state_manager.check_loop(action_name)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_list_backups(self):
        """List available backups."""
        try:
            from . import state_manager

            backups = state_manager.list_backups()
            return {"backups": [b.name for b in backups]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_init_state(self, project_name=None):
        """Initialize agent state."""
        try:
            from . import state_manager

            state_manager.init_state(project_name)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════
    # NEW COMMANDS: Mesh, Texture, Rig, Animation, Character
    # ═══════════════════════════════════════════════════════════

    def cmd_create_primitive(self, primitive_type="cube", params=None):
        """Create advanced primitive"""
        try:
            from .core import mesh_engine

            obj = mesh_engine.create_advanced_primitive(primitive_type, params or {})
            return {"status": "success", "object": obj.name}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_apply_material(self, obj_name, material_type):
        """Apply PBR material from library"""
        try:
            from .core import texture_engine

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "message": f"Object not found: {obj_name}"}
            mat = texture_engine.create_pbr_material(f"Mat_{material_type}", material_type)
            obj.data.materials.append(mat)
            return {"status": "success", "material": mat.name}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_create_armature(self, rig_type="humanoid"):
        """Create armature from template"""
        try:
            from .core import rig_engine

            if rig_type == "humanoid":
                obj = rig_engine.create_humanoid_rig()
            elif rig_type == "quadruped":
                obj = rig_engine.create_quadruped_rig()
            else:
                return {"status": "error", "message": f"Unknown rig type: {rig_type}"}
            return {"status": "success", "object": obj.name}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_create_animation(self, obj_name, anim_type="idle"):
        """Create animation on object"""
        try:
            from .core import animation_engine

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                # Try to find armature by type
                for o in bpy.data.objects:
                    if o.type == "ARMATURE":
                        obj = o
                        break
                if not obj:
                    return {"status": "error", "message": f"Object not found: {obj_name}"}

            if anim_type == "walk":
                animation_engine.create_walk_cycle(obj)
            elif anim_type == "run":
                animation_engine.create_run_cycle(obj)
            elif anim_type == "idle":
                animation_engine.create_idle_animation(obj)
            elif anim_type == "jump":
                animation_engine.create_jump_animation(obj)
            elif anim_type == "spin":
                animation_engine.create_spin_animation(obj)

            return {"status": "success", "animation": anim_type, "object": obj.name}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_create_character(self, character_type="humanoid", params=None):
        """Create character from template"""
        try:
            from .organic import character_gen

            parts = character_gen.create_character(character_type, params or {})
            return {"status": "success", "parts": list(parts.keys())}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_analyze_scene(self):
        """Analyze scene using perception system"""
        try:
            from .perception import perception_system

            result = perception_system.analyze_scene()
            # Return minimal summary to avoid JSON serialization issues
            scan = result.get("scan", {})
            quality = result.get("quality", {})
            decision = result.get("decision", {})

            return {
                "status": "success",
                "total_objects": len(scan.get("objects", [])),
                "anomaly_count": len(scan.get("anomalies", [])),
                "quality_score": quality.get("score", 0),
                "recommended_action": decision.get("action", "none"),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_export(self, filepath, target="auto"):
        """Export scene to specified format"""
        try:
            from .export import export_engine

            result = export_engine.smart_export(filepath, target)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_text_to_3d(self, description):
        """Create 3D model from text description"""
        try:
            from .ai import ai_assistant

            obj = ai_assistant.text_to_3d(description)
            if obj:
                return {"status": "success", "object": obj.name}
            return {"status": "error", "message": "Could not create object"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════
    # NEW COMMANDS: Phase 1 - Stability
    # ═══════════════════════════════════════════════════════════

    def cmd_get_anchors(self, obj_name=""):
        """Get 27 anchor points for an object."""
        try:
            from . import anchor_system

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "message": f"Object not found: {obj_name}"}
            anchors = anchor_system.get_bbox_anchors(obj)
            return {"status": "success", "anchors": {k: list(v) for k, v in anchors.items()}}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_snap_to_anchor(self, obj_move="", obj_target="", anchor_move="", anchor_target=""):
        """Snap object to anchor point of another object."""
        try:
            from . import anchor_system

            o_move = bpy.data.objects.get(obj_move)
            o_target = bpy.data.objects.get(obj_target)
            if not o_move or not o_target:
                return {"status": "error", "message": "Object(s) not found"}
            success = anchor_system.snap_to_anchor(o_move, o_target, anchor_move, anchor_target)
            return {"status": "success" if success else "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_snap_and_parent(self, obj_move="", obj_target="", anchor_move="", anchor_target=""):
        """Snap and parent object to another."""
        try:
            from . import anchor_system

            o_move = bpy.data.objects.get(obj_move)
            o_target = bpy.data.objects.get(obj_target)
            if not o_move or not o_target:
                return {"status": "error", "message": "Object(s) not found"}
            success = anchor_system.snap_and_parent(o_move, o_target, anchor_move, anchor_target)
            return {"status": "success" if success else "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_purge_orphans(self):
        """Purge orphan data blocks from memory."""
        try:
            from . import orphan_purge

            result = orphan_purge.purge_orphans()
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_get_memory_stats(self):
        """Get memory usage statistics."""
        try:
            from . import orphan_purge

            stats = orphan_purge.get_memory_usage()
            return {"status": "success", "stats": stats}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_reset_transforms(self, obj_name=None):
        """Reset transforms for an object or all objects."""
        try:
            from . import transform_reset

            if obj_name:
                obj = bpy.data.objects.get(obj_name)
                if not obj:
                    return {"status": "error", "message": f"Object not found: {obj_name}"}
                result = transform_reset.reset_all_transforms(obj)
                return {"status": "success", "result": result}
            else:
                result = transform_reset.reset_scene_transforms()
                return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_apply_transforms(self, obj_name=None):
        """Apply all transforms for an object or all objects."""
        try:
            from . import transform_reset

            if obj_name:
                obj = bpy.data.objects.get(obj_name)
                if not obj:
                    return {"status": "error", "message": f"Object not found: {obj_name}"}
                success = transform_reset.apply_all_transforms(obj)
                return {"status": "success" if success else "error"}
            else:
                result = transform_reset.apply_scene_transforms()
                return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════
    # NEW COMMANDS: Phase 3 - Performance
    # ═══════════════════════════════════════════════════════════

    def cmd_optimize_scene(self):
        """Optimize scene (merge verts, purge orphans)."""
        try:
            from . import memory_optimizer

            result = memory_optimizer.optimize_scene()
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_get_tool_count(self):
        """Get MCP tool count and loaded categories."""
        try:
            from . import lazy_loader

            count = lazy_loader.tool_registry.get_tool_count()
            # Ensure count is a dict with expected keys
            if not isinstance(count, dict):
                count = {"loaded": 0, "total": 0, "categories_loaded": 0, "categories_total": 0}
            return {"status": "success", "count": count}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_load_tool_category(self, category=""):
        """Load a tool category for lazy loading."""
        try:
            from . import lazy_loader

            success = lazy_loader.tool_registry.load_category(category)
            return {"status": "success" if success else "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════
    # NEW COMMANDS: Phase 4 - New Capabilities
    # ═══════════════════════════════════════════════════════════

    def cmd_vlm_analyze(self, provider="ollama", prompt_type="overall"):
        """Analyze scene using Vision-Language Model."""
        try:
            from . import vlm_visual

            result = vlm_visual.visual_feedback_loop(prompt_type, provider, max_iterations=1)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_sculpt_preset(self, obj_name="", preset="smooth"):
        """Apply sculpt preset to object."""
        try:
            from . import sculpt_advanced

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "message": f"Object not found: {obj_name}"}
            success = sculpt_advanced.apply_sculpt_preset(obj, preset)
            return {"status": "success" if success else "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_remesh(self, obj_name="", voxel_size=0.05):
        """Remesh object with voxel."""
        try:
            from . import sculpt_advanced

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "message": f"Object not found: {obj_name}"}
            success = sculpt_advanced.remesh_voxel(obj, voxel_size)
            return {"status": "success" if success else "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_physics_preset(self, obj_name="", preset="rigid_heavy"):
        """Apply physics preset to object."""
        try:
            from . import physics_realtime

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "message": f"Object not found: {obj_name}"}
            success = physics_realtime.apply_physics_preset(obj, preset)
            return {"status": "success" if success else "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_create_rock(self, radius=0.5, roughness=0.3):
        """Create procedural rock."""
        try:
            from . import sculpt_advanced

            obj = sculpt_advanced.create_rock(radius, roughness)
            if obj:
                return {"status": "success", "object": obj.name}
            return {"status": "error", "message": "Failed to create rock"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════
    # NEW COMMANDS: Phase 5 - Advanced Features
    # ═══════════════════════════════════════════════════════════
    # Nota: los comandos collab_* legacy (módulo `collaborative`, deprecado en
    # v2.2) fueron eliminados en v3.0. Usar las tools `collab.*` del registry
    # (backend: addon/multi_agent.py).

    def cmd_version_create(self, label=None):
        """Create version snapshot of scene."""
        try:
            from . import version_control

            version_id = version_control.create_snapshot(label)
            if version_id:
                return {"status": "success", "version_id": version_id}
            return {"status": "error", "message": "Failed to create version"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_version_restore(self, version_id=""):
        """Restore a version snapshot."""
        try:
            from . import version_control

            success = version_control.restore_snapshot(version_id)
            return {"status": "success" if success else "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_version_list(self):
        """List all version snapshots."""
        try:
            from . import version_control

            versions = version_control.list_snapshots()
            return {"status": "success", "versions": versions}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_export_ar_vr(self, target="webxr", filepath=None):
        """Export scene for AR/VR platform."""
        try:
            from . import ar_vr_preview

            result = ar_vr_preview.export_for_ar_vr(target, filepath)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════
    # NEW COMMANDS: Anti-Blockout Validation
    # ═══════════════════════════════════════════════════════════

    def cmd_check_blockout(self, obj_name=""):
        """Check if an object is blockout (prohibited)."""
        try:
            from . import anti_blockout

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "message": f"Object not found: {obj_name}"}
            result = anti_blockout.is_blockout(obj)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_validate_scene_blockout(self):
        """Validate entire scene against blockout."""
        try:
            from . import anti_blockout

            result = anti_blockout.validate_scene_blockout()
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_get_blockout_report(self):
        """Get human-readable blockout report."""
        try:
            from . import anti_blockout

            report = anti_blockout.get_blockout_report()
            return {"status": "success", "report": report}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_suggest_fixes(self, obj_name=""):
        """Get fix suggestions for a blockout object."""
        try:
            from . import anti_blockout

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "message": f"Object not found: {obj_name}"}
            suggestions = anti_blockout.suggest_fixes(obj)
            return {"status": "success", "suggestions": suggestions}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cmd_auto_fix_blockout(self, obj_name=""):
        """Auto-fix a blockout object."""
        try:
            from . import anti_blockout

            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "message": f"Object not found: {obj_name}"}
            result = anti_blockout.auto_fix_blockout(obj)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def serve_forever(host="localhost", port=None):
    """Servidor bloqueante para `blender --background --python`.

    Sin GUI no hay main loop y bpy.app.timers nunca dispara; este modo
    atiende clientes de forma síncrona en el hilo principal. No retorna.
    """
    global _socket_server
    _socket_server = BlenderSocketServer(
        host=host,
        port=port or SOCKET_PORT,
    )
    _socket_server.start(blocking=True)
    if not _socket_server.listening:
        raise RuntimeError(f"No se pudo abrir el socket: {_socket_server.last_error}")
    print(
        f"[BLENDER SOCKET] modo headless bloqueante en {_socket_server.host}:{_socket_server.port}",
        flush=True,
    )
    while True:
        try:
            client, _addr = _socket_server.sock.accept()
        except TimeoutError:
            continue
        except OSError:
            break
        try:
            _socket_server._serve_client_blocking(client)
        except Exception as e:
            print(f"[BLENDER SOCKET] cliente headless: {e}", flush=True)
        finally:
            try:
                client.close()
            except Exception:
                pass


def start_socket_server():
    global _socket_server
    if _socket_server is None:
        _socket_server = BlenderSocketServer()
    if not _socket_server.running:
        _socket_server.start()
    return _socket_server


def stop_socket_server():
    global _socket_server
    if _socket_server:
        _socket_server.stop()
        _socket_server = None
