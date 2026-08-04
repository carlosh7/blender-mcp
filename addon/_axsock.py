# blender-mcp — Socket server for Blender (ahujasid-compatible)
# Runs inside Blender, listens on port 9876 for JSON commands via TCP socket.
import bpy, json, socket, threading, time, io, traceback, importlib
import sys, os
from contextlib import redirect_stdout

SOCKET_PORT = 9876
_socket_server = None
_chat_queue = []
_chat_responses = {}
_chat_lock = threading.Lock()
_stop_agent = False
mcp_last_ping = 0  # timestamp of last ping from MCP server
mcp_connected = False
mcp_status = "idle"
mcp_error = ""
_mcp_process = None  # true if ping received in last 15s

def _wrap(result):
    """Bungkus hasil handler; dict berisi kunci 'error'/'status error'
    disebarkan sebagai kegagalan, bukan sukses palsu."""
    if isinstance(result, dict):
        if result.get("status") == "error":
            return {"status": "error", "message": result.get("message", "Gagal"),
                    "result": result}
        if "error" in result:
            return {"status": "error", "message": str(result["error"]),
                    "result": result}
    return {"status": "success", "result": result}


class BlenderSocketServer:
    """TCP socket server inside Blender for receiving MCP commands."""

    def __init__(self, host='localhost', port=SOCKET_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.sock = None
        self.thread = None
        self.listening = False
        self.last_error = None
        self._pending = []
        self._pending_lock = threading.Lock()


    def start(self):
        if self.running:
            return
        self.running = True
        try:
            # Intentar cerrar cualquier socket previo si existe
            if self.sock:
                try: self.sock.close()
                except: pass
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # SO_REUSEADDR + SO_REUSEPORT (si está disponible) para liberar el puerto rápido
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except: pass
            
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            self.listening = True
            self.last_error = None
            self.sock.settimeout(1.0)
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print(f"[BLENDER SOCKET] Server on port {self.port}")
        except Exception as e:
            self.running = False
            self.listening = False
            self.last_error = str(e)
            print(f"[BLENDER SOCKET] Gagal: {e}")
            self.stop()

    def stop(self):
        self.running = False
        self.listening = False
        if self.sock:
            try: self.sock.close()
            except: pass
            self.sock = None

    def _loop(self):
        while self.running:
            try:
                client, addr = self.sock.accept()
                threading.Thread(target=self._handle, args=(client,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception:
                pass

    def _handle(self, client):
        buffer = b''
        try:
            while self.running:
                data = client.recv(1024 * 1024) # Aumentar buffer para imágenes si es necesario
                if not data:
                    break
                buffer += data
                try:
                    # Intentar encontrar el final del JSON
                    raw_data = buffer.decode('utf-8')
                    cmd = json.loads(raw_data)
                    buffer = b''
                    
                    def execute():
                        try:
                            resp = self._execute(cmd)
                            client.sendall(json.dumps(resp).encode('utf-8'))
                        except:
                            client.sendall(json.dumps({"status": "error", "message": traceback.format_exc()}).encode('utf-8'))
                        return None
                    if getattr(bpy.app, "background", False):
                        # Headless: tidak ada main loop yang memicu timer. Jalankan
                        # via antrean yang dipompa oleh process_pending() dari
                        # skrip host, supaya bpy tetap dieksekusi di main thread.
                        with self._pending_lock:
                            self._pending.append(execute)
                    else:
                        bpy.app.timers.register(execute, first_interval=0.0)
                except json.JSONDecodeError:
                    pass
        except: pass
        finally:
            try: client.close()
            except: pass

    def process_pending(self):
        """Eksekusi perintah antrean di main thread (dipanggil skrip host headless)."""
        with self._pending_lock:
            pending = self._pending
            self._pending = []
        for job in pending:
            job()



    def _execute(self, cmd):
        cmd_type = cmd.get("type") or cmd.get("command")
        params = cmd.get("params") or cmd.get("args") or {}

        # Try direct method on self first (legacy commands)
        handler = getattr(self, f"cmd_{cmd_type}", None)
        if handler:
            try:
                result = handler(**params)
                return _wrap(result)
            except Exception as e:
                return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

        # Extended command surface: registry in addon/handlers.py
        try:
            from . import handlers as _handlers
        except Exception:
            _handlers = None
        if _handlers is not None:
            fn = _handlers.get_handler(cmd_type)
            if fn is not None:
                try:
                    result = fn(**params)
                    return _wrap(result)
                except Exception as e:
                    return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

        return {"status": "error", "message": f"Perintah tidak dikenal: {cmd_type}"}

    def cmd_get_viewport_screenshot(self, filepath=None, max_size=800):
        """Ambil gambar viewport saat ini untuk validasi."""
        if not filepath:
            import tempfile
            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, f"axiom_vision_{int(time.time())}.png")
        
        try:
            # Cari window dan screen yang valid (Blender 4.2+ butuh konteks eksplisit)
            window = bpy.context.window if bpy.context.window else bpy.context.window_manager.windows[0]
            screen = window.screen
            area = next((a for a in screen.areas if a.type == 'VIEW_3D'), None)
            
            if not area:
                return {"error": "Tidak ditemukan viewport 3D aktif di window utama"}
            
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
                    "height": img.size[1]
                }
            return {"error": "Gagal membuat file tangkapan"}
        except Exception as e:
            return {"error": str(e)}

    def cmd_search_assets(self, provider="polyhaven", query="", asset_type="textures"):
        from . import assets
        if provider == "polyhaven":
            return {"results": assets.AssetManager.search_polyhaven(asset_type, query)}
        elif provider == "sketchfab":
            return {"results": assets.AssetManager.search_sketchfab(query)}
        return {"error": "Penyedia tidak didukung"}

    def cmd_generate_3d(self, prompt=""):
        from . import assets
        return assets.AssetManager.rodin_generate(prompt)

    def cmd_analyze_performance(self):
        """Analiza el conteo de polígonos y sugiere optimizaciones."""
        report = []
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                poly_count = len(obj.data.polygons)
                if poly_count > 50000:
                    report.append(f"⚠️ {obj.name}: {poly_count} polígonos (Crítico)")
                elif poly_count > 10000:
                    report.append(f"ℹ️ {obj.name}: {poly_count} polígonos (Alto)")
        return {"report": report or ["Scene sudah optimal. Tidak ada objek berat."]}

    def cmd_cleanup_scene(self, purge_unused=True):
        """Hapus data yatim dan normalkan nama objek."""
        from . import scene_tools
        return scene_tools.cleanup_scene(purge_unused=purge_unused)

    def cmd_get_scene_info(self):
        info = {"name": bpy.context.scene.name, "object_count": len(bpy.context.scene.objects), "objects": []}
        for i, obj in enumerate(bpy.context.scene.objects):
            if i >= 20: break
            info["objects"].append({
                "name": obj.name, "type": obj.type,
                "location": [round(float(obj.location.x), 2), round(float(obj.location.y), 2), round(float(obj.location.z), 2)],
            })
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

    def cmd_snap_to_anchor(self, obj_move="", obj_target="", anchor_move="", anchor_target=""):
        try:
            from . import assembly
            o_move = bpy.data.objects.get(obj_move)
            o_target = bpy.data.objects.get(obj_target)
            return assembly.AssemblyEngine.snap_to_anchor(o_move, o_target, anchor_move, anchor_target)
        except Exception as e:
            return {"error": str(e)}

    def cmd_snap_and_parent(self, obj_move="", obj_target="", anchor_move="", anchor_target=""):
        try:
            from . import assembly
            o_move = bpy.data.objects.get(obj_move)
            o_target = bpy.data.objects.get(obj_target)
            return assembly.AssemblyEngine.snap_and_parent(o_move, o_target, anchor_move, anchor_target)
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
            return {"report": spatial.GeometryValidator.get_report()}
        except Exception as e:
            return {"error": str(e)}

    def cmd_ping(self):
        global mcp_last_ping, mcp_connected
        mcp_last_ping = time.time()
        mcp_connected = True
        return {"pong": True, "time": mcp_last_ping}

    # ─── Puente al ToolRegistry de src/ (228 tools) ───

    def cmd_list_tools(self, category=None):
        from . import registry_bridge
        return registry_bridge.list_tools(category)

    def cmd_describe_tool(self, name=""):
        from . import registry_bridge
        return registry_bridge.describe_tool(name)

    def cmd_call_tool(self, tool_name="", params=None):
        from . import registry_bridge
        return registry_bridge.call_tool(tool_name, params or {})

    def cmd_registry_status(self):
        from . import registry_bridge
        return registry_bridge.status()

    # ─── Lote transaccional ───

    def cmd_run_batch(self, steps=None, atomic=True, label="Axiom Batch"):
        from . import transaction
        return transaction.run_batch(steps or [], atomic=atomic, label=label)

    # ─── Inspección de escena ───

    def cmd_scene_graph(self, include_data=True):
        from . import inspect_scene
        return inspect_scene.scene_graph(include_data)

    def cmd_measure(self, name_a="", name_b=None):
        from . import inspect_scene
        return inspect_scene.measure(name_a, name_b)

    def cmd_find_objects(self, name_contains="", type=None, min_polygons=None, has_material=None):
        from . import inspect_scene
        return inspect_scene.find_objects(name_contains, type, min_polygons, has_material)

    # ─── Ensamblaje extendido ───

    def _resolve(self, names):
        objs, missing = [], []
        for n in names or []:
            o = bpy.data.objects.get(n)
            (objs if o else missing).append(o if o else n)
        return objs, missing

    def cmd_align_objects(self, names=None, axis="Z", mode="MIN", reference=None):
        from . import assembly
        objs, missing = self._resolve(names)
        if missing:
            return {"error": f"Objek tidak ditemukan: {', '.join(missing)}"}
        ref = bpy.data.objects.get(reference) if reference else None
        if reference and ref is None:
            return {"error": f"Objek referensi tidak ditemukan: {reference}"}
        return assembly.AssemblyEngine.align(objs, axis, mode, ref)

    def cmd_distribute_objects(self, names=None, axis="X", spacing=None):
        from . import assembly
        objs, missing = self._resolve(names)
        if missing:
            return {"error": f"Objek tidak ditemukan: {', '.join(missing)}"}
        return assembly.AssemblyEngine.distribute(objs, axis, spacing)

    def cmd_array_object(self, name="", count=3, axis="X", gap=0.0, linked=False):
        from . import assembly
        obj = bpy.data.objects.get(name)
        if obj is None:
            return {"error": f"Objek tidak ditemukan: {name}"}
        return assembly.AssemblyEngine.array(obj, count, axis, gap, linked)

    def _strip_bad_code(self, code):
        import re
        code = re.sub(r'^[ \t]*bpy\.context\.collection\.objects\.unlink\([^)]+\)\s*\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'^[ \t]*bpy\.context\.scene\.collection\.objects\.unlink\([^)]+\)\s*\n', '', code, flags=re.MULTILINE)
        def _fix_scale(m):
            inner = m.group(1)
            inner = re.sub(r'\s*/\s*2\s*', '', inner)
            return '.scale = (' + inner + ')'
        code = re.sub(r'\.scale\s*=\s*\(([^)]*)\)', _fix_scale, code)
        return code

    def cmd_execute_code(self, code=""):
        from blender_mcp.utils.validator import validate

        errors = validate(code)
        if errors:
            return {"output": "\n".join(str(error) for error in errors), "error": "Unsafe code"}
        code = self._strip_bad_code(code)
        win = bpy.context.window if bpy.context.window else (bpy.context.window_manager.windows[0] if bpy.context.window_manager.windows else None)
        ns = {
            "bpy": bpy, 
            "C": bpy.context, 
            "D": bpy.data, 
            "ops": bpy.ops,
            "window": win,
            "screen": win.screen if win else None,
        }
        
        # SIGALRM sólo existe en Unix; en Windows este atributo no está y la
        # ejecución fallaba antes de empezar. Sin alarma se ejecuta igual,
        # simplemente sin corte por tiempo.
        import signal
        can_alarm = hasattr(signal, "SIGALRM") and threading.current_thread() is threading.main_thread()
        timeout = float(os.environ.get("BLENDER_MCP_EXEC_TIMEOUT", "10"))

        def handler(signum, frame):
            raise TimeoutError(
                f"AXIOM TIMEOUT: Eksekusi melebihi batas {timeout}s.")

        # AXIOM v2.0 Atomic Transaction Start
        bpy.ops.ed.undo_push(message="Axiom Precision Task")

        previous = None
        buf = io.StringIO()
        with redirect_stdout(buf):
            if can_alarm:
                previous = signal.signal(signal.SIGALRM, handler)
                signal.setitimer(signal.ITIMER_REAL, timeout)
            try:
                compiled = compile(code, "<blender_code>", "exec")
                exec(compiled, ns)
            except TimeoutError as e:
                bpy.ops.ed.undo()
                return {"output": f"❌ {e} (Scene dipulihkan)", "error": str(e)}
            except SyntaxError as e:
                bpy.ops.ed.undo()
                return {"output": f"Kesalahan sintaks: {e} (scene dipulihkan)", "error": str(e)}
            except Exception as e:
                bpy.ops.ed.undo()
                return {"output": f"Kesalahan eksekusi: {str(e)[:200]} (scene dipulihkan)", "error": str(e)}
            finally:
                if can_alarm:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, previous)

        return {"output": buf.getvalue()}

    def cmd_chat_send(self, message="", model=""):
        global _stop_agent
        _stop_agent = False # Resetear parada al enviar nuevo mensaje
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

    def cmd_diagnose(self):
        import socket
        result = {"socket": False, "mcp": False}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(('127.0.0.1', 9876))
            result["socket"] = True
        except:
            pass
        s.close()
        try:
            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s2.settimeout(1)
            s2.connect(('127.0.0.1', 9879))
            result["mcp"] = True
            s2.close()
        except:
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
            return {"status": "error", "message": "filepath wajib diisi"}
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # Select all objects and export
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB')
            size = os.path.getsize(filepath)
            return {"status": "success", "filepath": filepath, "size": size}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def start_socket_server():
    global _socket_server
    if _socket_server is None:
        _socket_server = BlenderSocketServer()
    if not _socket_server.running:
        _socket_server.start()
    return _socket_server

def get_socket_server():
    """Devuelve la instancia del servidor, creándola si aún no existe.

    Permite reutilizar los handlers cmd_* (misma política de validación y
    undo) desde otros transportes, p. ej. el API HTTP.
    """
    global _socket_server
    if _socket_server is None:
        _socket_server = BlenderSocketServer()
    return _socket_server

def stop_socket_server():
    global _socket_server
    if _socket_server:
        _socket_server.stop()
        _socket_server = None
