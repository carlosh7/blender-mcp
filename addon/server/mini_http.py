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
from .. import _axsock as bsock


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
        if parsed.path == "/":
            self._web_status()
        elif parsed.path == "/api/health":
            self._send({
                "status": "ok",
                "version": "0.8.30",
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

    def _web_status(self):
        html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>blender-mcp</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#1a1a2e;color:#e0e0e0;
     display:flex;align-items:center;justify-content:center;min-height:100vh}}
.card{{background:#16213e;border-radius:16px;padding:2.5em;max-width:500px;width:90%;box-shadow:0 8px 32px #0006}}
h1{{font-size:1.5em}} .v{{color:#888;font-size:.9em;margin:.3em 0 1.5em}}
.s{{display:flex;align-items:center;gap:.6em;padding:.5em 0;border-bottom:1px solid #2a2a4a}}
.s:last-child{{border:0}} .g{{width:10px;height:10px;border-radius:50%;background:#4CAF50;display:inline-block}}
.r{{width:10px;height:10px;border-radius:50%;background:#f44336;display:inline-block}}
a{{color:#64b5f6;text-decoration:none}} .f{{margin-top:1.5em;padding-top:1em;border-top:1px solid #2a2a4a;font-size:.8em;color:#666}}
</style></head>
<body><div class="card">
<h1>blender-mcp ●</h1><div class="v">v0.8.30</div>
<div class="s"><span class="g"></span> Blender {bpy.app.version_string}</div>
<div class="s"><span class="g"></span> Escena: {bpy.context.scene.name}</div>
<div class="s"><span class="g"></span> <a href="/api/health">/api/health</a></div>
<div class="s"><span class="g"></span> <a href="/api/tools">/api/tools</a></div>
<div class="f">Clientes: opencode · Claude · Cursor · Antigravity</div>
</div></body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(html.encode())

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
