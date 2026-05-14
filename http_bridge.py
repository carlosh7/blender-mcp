"""
HTTP Bridge for blender-mcp.
Provides REST endpoints for Antigravity and HTTP clients.
Runs on port 9877.
Forwards to Blender via the MCP server socket connection.
"""
import json
import os
import sys
import time
import uuid
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from config import read_opencode_config, write_opencode_model, PROVIDER_API_CONFIG, get_api_key

HTTP_PORT = 9877
_server_instance = None

_chat_statuses = {}
_chat_lock = threading.Lock()


class MCPBridgeHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]} {args[1]} {args[2]}")

    def _send_json(self, data, status=200):
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

    def _send_to_blender(self, cmd_type, params=None):
        """Forward command to Blender via socket."""
        from blender_connection import get_blender
        try:
            b = get_blender()
            return b.send_command(cmd_type, params or {})
        except Exception as e:
            return {"error": str(e)}

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            result = self._send_to_blender("ping")
            self._send_json({
                "status": "ok",
                "version": "0.8.0",
                "blender": "connected" if result.get("pong") else "disconnected",
                "ai_state": "connected",
                "models_dir": str(Path.home() / "blender-mcp" / "models"),
            })

        elif parsed.path == "/api/providers":
            config = read_opencode_config()
            self._send_json(config if config.get("found") else {"found": False})

        elif parsed.path.startswith("/api/chat/status"):
            from urllib.parse import parse_qs
            params = parse_qs(parsed.query)
            msg_id = params.get("message_id", [None])[0]
            if not msg_id:
                self._send_json({"error": "message_id required"}, 400)
                return
            with _chat_lock:
                status = _chat_statuses.get(msg_id)
            if not status:
                self._send_json({"status": "not_found"})
            else:
                self._send_json(status)

        elif parsed.path == "/api/models":
            scene = self._send_to_blender("get_scene_info")
            objects = scene.get("objects", [])
            self._send_json({
                "count": len(objects),
                "objects": objects,
            })

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        body = self._read_body()

        if parsed.path == "/api/chat":
            message = body.get("message", "")
            if not message:
                self._send_json({"error": "Empty message"}, 400)
                return
            msg_id = str(uuid.uuid4())
            with _chat_lock:
                _chat_statuses[msg_id] = {
                    "status": "queued", "message": message, "response": None, "timestamp": time.time(),
                }
            # Send to Blender chat
            self._send_to_blender("chat_send", {"message": message})
            self._send_json({"status": "queued", "message_id": msg_id})

        elif parsed.path == "/api/set-model":
            model_name = body.get("model", "")
            if not model_name:
                self._send_json({"error": "model required"}, 400)
                return
            result = write_opencode_model(model_name)
            self._send_json(result, 200 if result["success"] else 500)

        elif parsed.path == "/api/fetch-all-models":
            config = read_opencode_config()
            providers = config.get("providers", [])
            results = {}
            for p in providers:
                pid = p["id"]
                cfg = PROVIDER_API_CONFIG.get(pid)
                if not cfg:
                    results[pid] = {"error": "No config"}
                    continue
                result = _fetch_provider_models(pid, cfg)
                results[pid] = result
            self._send_json({"providers": results})

        elif parsed.path == "/api/execute":
            code = body.get("code", "")
            result = self._send_to_blender("execute_code", {"code": code})
            self._send_json(result)

        else:
            self._send_json({"error": "Not found"}, 404)


def _fetch_provider_models(provider_id, cfg):
    """Fetch models from a provider's API."""
    import urllib.request
    url = cfg["url"]
    headers = {"User-Agent": "blender-mcp/0.8"}
    if cfg.get("auth"):
        key = get_api_key(provider_id)
        if not key:
            return {"error": f"No API key for {provider_id}"}
        headers["Authorization"] = f"Bearer {key}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read())
        raw_list = raw.get("data", raw)
        if not isinstance(raw_list, list):
            return {"error": "Unexpected format"}
        models = []
        for m in raw_list:
            mid = m.get("id", "")
            if mid:
                models.append({"id": mid, "name": m.get("name", mid), "provider": provider_id})
        return {"models": models}
    except Exception as e:
        return {"error": str(e)}


def start_http_server(port=HTTP_PORT):
    global _server_instance
    _server_instance = HTTPServer(("0.0.0.0", port), MCPBridgeHandler)
    t = threading.Thread(target=_server_instance.serve_forever, daemon=True)
    t.start()
    print(f"[HTTP Bridge] Server on http://0.0.0.0:{port}")
    return _server_instance


def stop_http_server():
    global _server_instance
    if _server_instance:
        _server_instance.shutdown()
        _server_instance = None


if __name__ == "__main__":
    print("Starting HTTP bridge...")
    start_http_server()
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        stop_http_server()
