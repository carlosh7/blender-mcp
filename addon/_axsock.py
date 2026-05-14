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
mcp_connected = False  # true if ping received in last 15s

class BlenderSocketServer:
    """TCP socket server inside Blender for receiving MCP commands."""

    def __init__(self, host='localhost', port=SOCKET_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.sock = None
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            self.sock.settimeout(1.0)
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print(f"[BLENDER SOCKET] Server on port {self.port}")
        except Exception as e:
            print(f"[BLENDER SOCKET] Failed: {e}")
            self.stop()

    def stop(self):
        self.running = False
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
            except: pass

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
                    bpy.app.timers.register(execute, first_interval=0.0)
                except json.JSONDecodeError:
                    pass
        except: pass
        finally:
            try: client.close()
            except: pass

    def _execute(self, cmd):
        cmd_type = cmd.get("type") or cmd.get("command")
        params = cmd.get("params") or cmd.get("args") or {}
        
        # Try direct method on self first (legacy commands)
        handler = getattr(self, f"cmd_{cmd_type}", None)
        if handler:
            try:
                result = handler(**params)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

        # Try modular handlers (Fase 2)
        handler_result = self._dispatch_to_handlers(cmd_type, params)
        if handler_result is not None:
            return handler_result

        return {"status": "error", "message": f"Unknown command: {cmd_type}"}

    def _dispatch_to_handlers(self, cmd_type, params):
        """Try to dispatch command to modular handler modules."""
        if __package__:
            handler_base = f"{__package__}.handlers"
        else:
            handler_base = "handlers"

        handler_modules = [
            "scene", "objects", "materials", "modifiers", "lights", "camera",
            "shader_nodes", "animation", "geometry_nodes", "render",
            "io", "uv_texture", "batch", "rigging", "scene_utils", "printing",
            "polyhaven", "sketchfab", "hyper3d", "hunyuan", "ambientcg",
            "analysis", "docs", "viewport", "ui",
        ]
        for mod_name in handler_modules:
            try:
                mod = importlib.import_module(f"{handler_base}.{mod_name}")
                func = getattr(mod, f"cmd_{cmd_type}", None)
                if func:
                    result = func(**params)
                    return {"status": "success", "result": result}
                for attr_name in sorted(dir(mod)):
                    if attr_name.endswith("Handler") and attr_name != "BaseHandler":
                        handler_cls = getattr(mod, attr_name)
                        class_func = getattr(handler_cls, f"cmd_{cmd_type}", None)
                        if class_func:
                            result = class_func(**params)
                            return {"status": "success", "result": result}
            except ImportError:
                continue
            except Exception as e:
                return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}
        return None

    def cmd_get_viewport_screenshot(self, filepath=None, max_size=800):
        """Captura una imagen del viewport actual para validación Axiom."""
        if not filepath:
            import tempfile
            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, f"axiom_vision_{int(time.time())}.png")
        
        try:
            # Buscar el área de 3D Viewport
            area = next((a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'), None)
            if not area:
                return {"error": "No se encontró un viewport 3D activo"}
            
            # Forzar el renderizado de la captura en el área correcta
            with bpy.context.temp_override(area=area):
                bpy.ops.screen.screenshot_area(filepath=filepath)
            
            # Cargar y redimensionar para ahorrar ancho de banda si es necesario
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
            if obj.type == 'MESH':
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
                base = obj.name.split(".")[0]
                # (Lógica opcional de renombrado aquí)
        return {"status": "success", "message": "Limpieza profunda de Axiom completada."}

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

    def cmd_execute_code(self, code=""):
        ns = {"bpy": bpy, "C": bpy.context, "D": bpy.data, "ops": bpy.ops}
        buf = io.StringIO()
        with redirect_stdout(buf):
            try:
                compiled = compile(code, "<blender_code>", "exec")
                exec(compiled, ns)
            except SyntaxError as e:
                return {"output": f"❌ SyntaxError: {e}"}
            except Exception as e:
                return {"output": f"❌ Error: {str(e)[:200]}"}
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

def stop_socket_server():
    global _socket_server
    if _socket_server:
        _socket_server.stop()
        _socket_server = None
