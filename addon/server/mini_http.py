"""
mini_http.py — Mini REST API para Antigravity y clientes HTTP.
Puerto 9877. Sin dependencias externas. Corre dentro de Blender.

Seguridad:
  - Bind a 127.0.0.1 (configurable vía BLENDER_MCP_HTTP_HOST, bajo tu responsabilidad)
  - Token obligatorio: header X-API-Token (o ?token=). Mismo token que el
    socket :9876 (env BLENDER_MCP_HTTP_TOKEN > <config>/blender-mcp/socket_token).
    NO se guarda en la escena .blend (viajaba con el archivo).
  - Rate limit: 30 req/min por IP. Body limitado a 1 MB.
  - POST /api/execute pasa por addon.code_guard (AST) antes de exec().
  - Todo acceso a bpy se serializa al hilo principal vía bpy.app.timers
    (bpy no es thread-safe).

Endpoints:
  GET  /                → landing (sin info sensible)
  GET  /api/health      → estado (requiere token)
  GET  /api/tools       → lista de herramientas (requiere token)
  POST /api/chat        → enviar mensaje (requiere token)
  POST /api/execute     → ejecutar código Python en Blender (requiere token)
"""

import json
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import bpy

HTTP_PORT = 9877
HTTP_HOST = "127.0.0.1"
RATE_LIMIT_PER_MIN = 30
MAX_BODY_BYTES = 1_000_000
_server_instance = None
_token_cache = None
_rate_lock = threading.Lock()
_rate_buckets = {}

# Referencia al socket server para encolar mensajes de chat
from .. import _axsock as bsock
from ..code_guard import CodeGuardError, check_code


def get_token():
    """Token de la API: env BLENDER_MCP_HTTP_TOKEN > token compartido del socket."""
    global _token_cache
    if _token_cache:
        return _token_cache
    import os

    env_token = os.environ.get("BLENDER_MCP_HTTP_TOKEN", "")
    if env_token:
        _token_cache = env_token
        return _token_cache
    _token_cache = bsock._load_or_create_token()
    return _token_cache


def _run_on_main(fn, timeout=30.0):
    """Ejecuta fn() en el hilo principal de Blender (bpy no es thread-safe).

    Devuelve (ok, resultado|excepción). El hilo HTTP queda a la espera del
    evento mientras el timer de bpy ejecuta en el main thread.
    """
    ev = threading.Event()
    box = {}

    def task():
        try:
            box["ok"], box["out"] = True, fn()
        except Exception as e:  # noqa: BLE001
            box["ok"], box["out"] = False, e
        ev.set()
        return None

    bpy.app.timers.register(task, first_interval=0.0)
    if not ev.wait(timeout=timeout):
        return False, TimeoutError("timeout ejecutando en el hilo principal")
    return box.get("ok", False), box.get("out")


def _rate_ok(ip):
    """Token bucket simple: RATE_LIMIT_PER_MIN por minuto por IP."""
    now = time.time()
    with _rate_lock:
        window = _rate_buckets.setdefault(ip, [])
        while window and now - window[0] > 60.0:
            window.pop(0)
        if len(window) >= RATE_LIMIT_PER_MIN:
            return False
        window.append(now)
        return True


class MiniAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[HTTP :{HTTP_PORT}] {args[0]} {args[1]} {args[2]}")

    def _send(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _authorized(self):
        header_token = self.headers.get("X-API-Token", "")
        if not header_token:
            query = parse_qs(urlparse(self.path).query)
            header_token = query.get("token", [""])[0]
        if not header_token or not secrets.compare_digest(header_token, get_token()):
            self._send({"error": "unauthorized: missing or invalid X-API-Token"}, 401)
            return False
        return True

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY_BYTES:
            raise ValueError(f"body demasiado grande ({length} bytes)")
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Token")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._web_status()
            return
        if not self._authorized():
            return
        ip = self.client_address[0]
        if not _rate_ok(ip):
            self._send({"error": "rate limit exceeded"}, 429)
            return
        if parsed.path == "/api/health":
            ok, out = _run_on_main(
                lambda: {
                    "status": "ok",
                    "blender": bpy.app.version_string,
                    "scene": bpy.context.scene.name,
                    "objects": len(bpy.data.objects),
                }
            )
            self._send(out if ok else {"error": str(out)}, 200 if ok else 500)
        elif parsed.path == "/api/tools":
            handlers = [
                "scene",
                "objects",
                "materials",
                "modifiers",
                "lights",
                "camera",
                "shader_nodes",
                "animation",
                "geometry_nodes",
                "render",
                "io",
                "uv_texture",
                "batch",
                "rigging",
                "scene_utils",
                "printing",
                "polyhaven",
                "sketchfab",
                "hyper3d",
                "hunyuan",
                "ambientcg",
            ]
            self._send({"tools": handlers, "count": len(handlers)})
        else:
            self._send({"error": "Not found"}, 404)

    def _web_status(self):
        html = """<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>blender-mcp</title></head>
<body style="font-family:sans-serif;background:#1a1a2e;color:#e0e0e0;
     display:flex;align-items:center;justify-content:center;min-height:100vh">
<div><h1>blender-mcp HTTP API</h1>
<p>Autenticación requerida: header <code>X-API-Token</code> o <code>?token=</code>.</p>
</div></body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        if not self._authorized():
            return
        ip = self.client_address[0]
        if not _rate_ok(ip):
            self._send({"error": "rate limit exceeded"}, 429)
            return
        parsed = urlparse(self.path)
        body = self._read_body()

        if parsed.path == "/api/chat":
            message = body.get("message", "")
            if not message:
                self._send({"error": "message required"}, 400)
                return
            msg_id = str(time.time())
            with bsock._chat_lock:
                bsock._chat_queue.append(
                    {
                        "id": msg_id,
                        "message": message,
                        "timestamp": time.time(),
                    }
                )
            self._send({"status": "queued", "message_id": msg_id})

        elif parsed.path == "/api/execute":
            code = body.get("code", "")
            if not code:
                self._send({"error": "code required"}, 400)
                return
            try:
                check_code(code)
            except CodeGuardError as e:
                self._send({"status": "blocked", "error": str(e)}, 403)
                return
            import io
            from contextlib import redirect_stdout

            def _work():
                ns = {"bpy": bpy, "C": bpy.context, "D": bpy.data, "ops": bpy.ops}
                buf = io.StringIO()
                with redirect_stdout(buf):
                    exec(code, ns)  # noqa: S102 — protegido por code_guard
                return buf.getvalue()

            ok, out = _run_on_main(_work)
            if ok:
                self._send({"status": "ok", "output": out})
            else:
                self._send({"status": "error", "message": str(out)}, 500)
        else:
            self._send({"error": "Not found"}, 404)


def start():
    global _server_instance, _token_cache
    if _server_instance:
        return
    _token_cache = None  # re-resolve token (escena pudo cambiar)
    import os

    host = os.environ.get("BLENDER_MCP_HTTP_HOST", HTTP_HOST)
    try:
        server = HTTPServer((host, HTTP_PORT), MiniAPIHandler)
        _server_instance = server
        get_token()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"[blender-mcp] ✅ HTTP API on http://{host}:{HTTP_PORT} (token requerido)")
    except Exception as e:
        print(f"[blender-mcp] ⚠️  HTTP server: {e}")


def stop():
    global _server_instance, _token_cache
    if _server_instance:
        try:
            _server_instance.shutdown()
        except Exception:
            pass
        _server_instance = None
        _token_cache = None
