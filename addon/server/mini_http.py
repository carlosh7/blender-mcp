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
import hmac
import json
import os
import secrets
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HTTP_PORT = 9877
# Bind local por defecto. Exponer a la red requiere un opt-in explícito
# (BLENDER_MCP_HTTP_HOST) porque este servidor ejecuta código en Blender.
HTTP_HOST = os.environ.get("BLENDER_MCP_HTTP_HOST", "127.0.0.1")
# Origen permitido para CORS; '*' con credenciales sería un agujero.
ALLOWED_ORIGIN = os.environ.get("BLENDER_MCP_HTTP_ORIGIN", "http://localhost")
_server_instance = None
_auth_token = None

# Referencia al socket server para encolar mensajes de chat
from .. import _axsock as bsock


def get_token():
    """Token de acceso del API HTTP. Se genera uno aleatorio por sesión si no
    se fija BLENDER_MCP_HTTP_TOKEN, y se imprime en consola al arrancar."""
    global _auth_token
    if _auth_token is None:
        _auth_token = os.environ.get("BLENDER_MCP_HTTP_TOKEN") or secrets.token_urlsafe(24)
    return _auth_token


def run_in_main_thread(fn, timeout=30.0):
    """Ejecuta fn() en el hilo principal de Blender y devuelve su resultado.

    Tocar bpy desde el hilo del handler HTTP corrompe el estado de Blender y
    lo cierra sin aviso; bpy.app.timers es el único punto de entrada seguro.
    """
    box = {}
    done = threading.Event()

    def _run():
        try:
            box["value"] = fn()
        except Exception as exc:  # se reenvía al hilo HTTP
            box["error"] = exc
        finally:
            done.set()
        return None

    bpy.app.timers.register(_run, first_interval=0.0)
    if not done.wait(timeout):
        raise TimeoutError("Blender no respondió dentro del tiempo límite")
    if "error" in box:
        raise box["error"]
    return box.get("value")


class MiniAPIHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[HTTP :{HTTP_PORT}] {args[0]} {args[1]} {args[2]}")

    def _send(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def _authorized(self):
        """Comprueba el bearer token en tiempo constante.

        Sin esto cualquiera que alcance el puerto ejecuta código en Blender.
        """
        header = self.headers.get("Authorization", "")
        prefix = "Bearer "
        supplied = header[len(prefix):] if header.startswith(prefix) else ""
        if not hmac.compare_digest(supplied, get_token()):
            self._send({"error": "Unauthorized: falta o no coincide el bearer token"}, 401)
            return False
        return True

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._web_status()
            return
        if not self._authorized():
            return
        if parsed.path == "/api/health":
            try:
                info = run_in_main_thread(lambda: {
                    "blender": bpy.app.version_string,
                    "scene": bpy.context.scene.name,
                    "objects": len(bpy.data.objects),
                })
            except Exception as exc:
                self._send({"status": "error", "message": str(exc)}, 500)
                return
            self._send({"status": "ok", "version": "0.8.64", **info})
        elif parsed.path == "/api/tools":
            try:
                from .. import registry_bridge
                self._send(run_in_main_thread(registry_bridge.list_tools))
            except Exception as exc:
                self._send({"error": str(exc)}, 500)
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
<h1>blender-mcp ●</h1><div class="v">v0.8.64</div>
<div class="s"><span class="g"></span> API protegida por bearer token</div>
<div class="s"><span class="g"></span> Escucha en {HTTP_HOST}:{HTTP_PORT}</div>
<div class="s"><span class="g"></span> <a href="/api/health">/api/health</a></div>
<div class="s"><span class="g"></span> <a href="/api/tools">/api/tools</a></div>
<div class="f">Clientes: opencode · Claude · Cursor · Antigravity</div>
</div></body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        parsed = urlparse(self.path)
        if not self._authorized():
            return
        try:
            body = self._read_body()
        except (ValueError, json.JSONDecodeError):
            self._send({"error": "JSON inválido"}, 400)
            return

        if parsed.path == "/api/chat":
            message = body.get("message", "")
            if not message:
                self._send({"error": "message wajib diisi"}, 400)
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
                self._send({"error": "code wajib diisi"}, 400)
                return
            try:
                # Misma política y mismo hilo que el socket: validar, luego
                # ejecutar en el hilo principal de Blender.
                result = run_in_main_thread(
                    lambda: bsock.get_socket_server().cmd_execute_code(code=code),
                    timeout=60.0,
                )
            except Exception as exc:
                self._send({"status": "error", "message": str(exc)}, 500)
                return
            status = "error" if result.get("error") else "ok"
            self._send({"status": status, **result}, 200 if status == "ok" else 400)

        elif parsed.path == "/api/tool":
            name = body.get("name", "")
            if not name:
                self._send({"error": "name wajib diisi"}, 400)
                return
            try:
                from .. import registry_bridge
                result = run_in_main_thread(
                    lambda: registry_bridge.call_tool(name, body.get("params") or {}),
                    timeout=60.0,
                )
            except Exception as exc:
                self._send({"status": "error", "message": str(exc)}, 500)
                return
            self._send(result, 200 if result.get("success") else 400)
        else:
            self._send({"error": "Not found"}, 404)


def start():
    global _server_instance
    if _server_instance:
        return
    try:
        server = HTTPServer((HTTP_HOST, HTTP_PORT), MiniAPIHandler)
        _server_instance = server
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"[blender-mcp] ✅ HTTP API on http://{HTTP_HOST}:{HTTP_PORT}")
        print(f"[blender-mcp] 🔑 token: {get_token()}")
        if HTTP_HOST not in ("127.0.0.1", "localhost", "::1"):
            print("[blender-mcp] ⚠️  El API HTTP ejecuta código en Blender y está "
                  "expuesto fuera de localhost. Protégelo con un firewall.")
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
