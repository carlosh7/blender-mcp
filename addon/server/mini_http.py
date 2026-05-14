"""
mini_http.py — Mini REST API para Antigravity y clientes HTTP.
Puerto 9877. Sin dependencias externas. Corre dentro de Blender.
Endpoints:
  GET  /api/health    → estado
  GET  /api/tools     → lista de herramientas
  POST /api/chat      → enviar mensaje
  POST /api/execute   → ejecutar código Python en Blender
"""
import bpy
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HTTP_PORT = 9877
_server_instance = None

# Referencia al socket server para encolar mensajes de chat
from .. import blender_socket as bsock


class MiniAPIHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[HTTP :{HTTP_PORT}] {args[0]} {args[1]} {args[2]}")

    def _send(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send({
                "status": "ok",
                "version": "0.8.7",
                "blender": bpy.app.version_string,
                "scene": bpy.context.scene.name,
                "objects": len(bpy.data.objects),
            })
        elif parsed.path == "/api/tools":
            handlers = [
                "scene", "objects", "materials", "modifiers", "lights", "camera",
                "shader_nodes", "animation", "geometry_nodes", "render",
                "io", "uv_texture", "batch", "rigging", "scene_utils", "printing",
                "polyhaven", "sketchfab", "hyper3d", "hunyuan", "ambientcg",
            ]
            self._send({"tools": handlers, "count": len(handlers)})
        else:
            self._send({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        body = self._read_body()

        if parsed.path == "/api/chat":
            message = body.get("message", "")
            if not message:
                self._send({"error": "message required"}, 400)
                return
            msg_id = str(time.time())
            with bsock._chat_lock:
                bsock._chat_queue.append({
                    "id": msg_id,
                    "message": message,
                    "timestamp": time.time(),
                })
            self._send({"status": "queued", "message_id": msg_id})

        elif parsed.path == "/api/execute":
            code = body.get("code", "")
            if not code:
                self._send({"error": "code required"}, 400)
                return
            import io
            from contextlib import redirect_stdout
            ns = {"bpy": bpy, "C": bpy.context, "D": bpy.data, "ops": bpy.ops}
            buf = io.StringIO()
            with redirect_stdout(buf):
                try:
                    exec(code, ns)
                    self._send({"status": "ok", "output": buf.getvalue()})
                except Exception as e:
                    self._send({"status": "error", "message": str(e)}, 500)
        else:
            self._send({"error": "Not found"}, 404)


def start():
    global _server_instance
    if _server_instance:
        return
    try:
        server = HTTPServer(("0.0.0.0", HTTP_PORT), MiniAPIHandler)
        _server_instance = server
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"[blender-mcp] ✅ HTTP API on http://0.0.0.0:{HTTP_PORT}")
    except Exception as e:
        print(f"[blender-mcp] ⚠️  HTTP server: {e}")


def stop():
    global _server_instance
    if _server_instance:
        try:
            _server_instance.shutdown()
        except:
            pass
        _server_instance = None
