"""
HTTP Bridge for blender-mcp.
Provides REST endpoints for the Blender addon to communicate with the MCP server.
Runs on port 9877 by default.
Endpoints:
  GET  /api/health          → { status: "ok" }
  GET  /api/models          → list of available 3D model types
  GET  /api/providers       → detect connected providers from opencode config
  POST /api/fetch-all-models → fetch live models from all connected providers
  POST /api/set-model       → set model in opencode config
  POST /api/chat            → process a chat message
  POST /api/generate        → generate a 3D model
"""
import json
import os
import sys
import time
import uuid
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
MODELS_DIR = ROOT / "models"
os.makedirs(MODELS_DIR, exist_ok=True)

HTTP_PORT = 9877
server_instance = None

sys.path.insert(0, str(ROOT))
from config import read_opencode_config, write_opencode_model, PROVIDER_API_CONFIG, get_api_key

# Shared session with MCP server (must be running in same process)
try:
    from server import session as server_session
except ImportError:
    server_session = None

# Model cache: {provider_id: {"data": [...], "cached_at": timestamp}}
_model_cache = {}
CACHE_TTL = 300  # 5 minutes

# Chat status store: {message_id: {"status": "processing"/"done"/"error", "response": "...", "message": "...", "timestamp": ...}}
_chat_statuses = {}
_chat_lock = threading.Lock()

# Object detection for auto-processing
_OBJECT_KEYWORDS = {
    "chair": "chair-folding", "silla": "chair-folding", "asiento": "chair-folding",
    "table": "table-round-150", "mesa": "table-round-150",
    "mesa redonda": "table-round-150", "mesa rectangular": "table-rect",
    "stage": "stage-custom", "escenario": "stage-custom", "tarima": "platform-2x2",
    "platform": "platform-2x2",
    "speaker": "speaker", "altavoz": "speaker", "bocina": "speaker",
    "screen": "led-flat", "pantalla": "led-flat", "monitor": "led-flat",
    "truss": "truss-straight",
    "barrier": "barrier", "valla": "barrier", "barrera": "barrier",
}

_COLOR_KEYWORDS = {
    "rojo": "#ff0000", "azul": "#0000ff", "verde": "#00ff00",
    "negro": "#000000", "blanco": "#ffffff", "gris": "#888888",
    "amarillo": "#ffff00", "dorado": "#ffd700", "plateado": "#c0c0c0",
    "madera": "#8B4513", "roble": "#8B4513", "oscuro": "#333333",
    "popo": "#7B3F00", "caca": "#7B3F00", "marron": "#7B3F00", "marrón": "#7B3F00",
}


def _fetch_provider_models(provider_id: str, cfg: dict) -> dict:
    """Fetch models from a provider's API. Returns {"models": [...], "error": None} or {"error": "..."}."""
    url = cfg["url"]
    headers = {"User-Agent": "blender-mcp/0.9.0", "Accept": "application/json"}

    if cfg.get("auth"):
        api_key = get_api_key(provider_id)
        if not api_key:
            return {"error": f"No API key found for {provider_id}"}
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read())
    except Exception as e:
        return {"error": f"Failed to fetch from {provider_id}: {str(e)[:100]}"}

    # Normalize different API response formats
    models_raw = raw.get("data", raw)
    if not isinstance(models_raw, list):
        return {"error": f"Unexpected response format from {provider_id}"}

    models = []
    seen = set()
    for m in models_raw:
        mid = m.get("id", "")
        if not mid or mid in seen:
            continue
        seen.add(mid)
        models.append({
            "id": mid,
            "name": m.get("name") or mid.split("/")[-1].replace("-", " ").title(),
            "provider": provider_id,
        })

    return {"models": models, "error": None}


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
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            self._send_json({
                "status": "ok",
                "version": "0.9.0",
                "models_dir": str(MODELS_DIR),
                "models_count": len(list(MODELS_DIR.glob("*.glb"))),
            })

        elif parsed.path == "/api/models":
            try:
                from server import AVAILABLE_MODELS
                self._send_json({
                    "models": [
                        {"id": k, "name": k.replace("-", " ").title(), "category": v["category"],
                         "width": v["width"], "depth": v["depth"], "height": v["height"]}
                        for k, v in sorted(AVAILABLE_MODELS.items())
                    ],
                    "count": len(AVAILABLE_MODELS),
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif parsed.path == "/api/chat/status":
            from urllib.parse import parse_qs
            params = parse_qs(parsed.query)
            msg_id = params.get("message_id", [None])[0]
            if not msg_id:
                self._send_json({"error": "message_id required"}, 400)
                return
            with _chat_lock:
                status = _chat_statuses.get(msg_id)
            if not status:
                self._send_json({"status": "not_found", "message_id": msg_id})
            else:
                self._send_json({
                    "status": status["status"],
                    "message_id": msg_id,
                    "response": status.get("response", ""),
                })

        elif parsed.path == "/api/providers":
            config = read_opencode_config()
            providers = config.get("providers", [])
            # Add model counts from cache if available
            for p in providers:
                pid = p["id"]
                cached = _model_cache.get(pid)
                if cached and cached["data"]:
                    p["model_count"] = len(cached["data"])
                else:
                    p["model_count"] = 0

            self._send_json({
                "found": config["found"],
                "config_file": config.get("config_file"),
                "current_model": config.get("model", ""),
                "current_provider": config.get("current_provider", "opencode"),
                "providers": providers,
            })

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/fetch-all-models":
            body = self._read_body()
            force_refresh = body.get("force", False)
            now = time.time()

            config = read_opencode_config()
            providers = config.get("providers", [])
            results = {}

            for p in providers:
                pid = p["id"]
                cfg = PROVIDER_API_CONFIG.get(pid)
                if not cfg:
                    results[pid] = {"error": "No API config for this provider"}
                    continue

                # Check cache
                cached = _model_cache.get(pid)
                if cached and not force_refresh and (now - cached["cached_at"]) < CACHE_TTL:
                    results[pid] = {"models": cached["data"], "cached": True}
                    continue

                # Fetch live
                result = _fetch_provider_models(pid, cfg)
                if result["models"]:
                    _model_cache[pid] = {"data": result["models"], "cached_at": now}
                    results[pid] = {"models": result["models"], "cached": False}
                else:
                    # Keep stale cache if fetch fails
                    if cached:
                        results[pid] = {"models": cached["data"], "cached": True, "fetch_error": result["error"]}
                    else:
                        results[pid] = {"models": [], "error": result["error"]}

            self._send_json({"providers": results})

        elif parsed.path == "/api/set-model":
            body = self._read_body()
            model_name = body.get("model", "")
            if not model_name:
                self._send_json({"error": "model field required"}, 400)
                return
            result = write_opencode_model(model_name)
            self._send_json(result, 200 if result["success"] else 500)

        elif parsed.path == "/api/chat":
            body = self._read_body()
            message = body.get("message", "")
            if not message:
                self._send_json({"error": "Empty message"}, 400)
                return

            msg_id = str(uuid.uuid4())
            with _chat_lock:
                _chat_statuses[msg_id] = {
                    "status": "processing",
                    "message": message,
                    "response": None,
                    "timestamp": time.time(),
                }

            # Queue for AI (opencode) to see
            if server_session is not None:
                server_session["chat_queue"].append({
                    "id": msg_id,
                    "message": message,
                    "timestamp": time.time(),
                })

            # Auto-process in background thread (Blender pipeline)
            threading.Thread(target=_auto_process_chat, args=(msg_id, message), daemon=True).start()

            # Respond immediately — Blender will poll for status
            self._send_json({
                "status": "queued",
                "message_id": msg_id,
            })

        elif parsed.path == "/api/generate":
            body = self._read_body()
            model_type = body.get("model_type", "")
            name = body.get("name", model_type)

            if not model_type:
                self._send_json({"error": "model_type required"}, 400)
                return

            try:
                from server import generate_blender_script, run_blender, session
                script, output_path = generate_blender_script(model_type, name=name)
                result = run_blender(script)

                if os.path.exists(output_path):
                    size = os.path.getsize(output_path)
                    final_path = str(output_path)
                    if session.get("check_path"):
                        dst = Path(session["check_path"]) / f"{name}.glb"
                        import shutil
                        shutil.copy2(output_path, dst)
                        final_path = str(dst)

                    self._send_json({
                        "success": True,
                        "file": final_path,
                        "size_bytes": size,
                        "output_preview": result[:300],
                    })
                else:
                    self._send_json({"success": False, "error": "Generation failed"}, 500)
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, 500)

        else:
            self._send_json({"error": "Not found"}, 404)

def _auto_process_chat(msg_id: str, message: str):
    """Wait for AI to respond via MCP. Fallback: auto-detect objects if AI unavailable."""
    msg_lower = message.lower()
    response = None

    # Step 1: wait for AI response (60s)
    with _chat_lock:
        if msg_id in _chat_statuses:
            _chat_statuses[msg_id]["status"] = "waiting_for_ai"

    if server_session is not None:
        deadline = time.time() + 60
        while time.time() < deadline:
            if msg_id in server_session.get("chat_responses", {}):
                response = server_session["chat_responses"].pop(msg_id, None)
                break
            time.sleep(1)

    # Step 2: if AI didn't respond, try auto-detect as fallback
    if not response:
        matched_type = None
        matched_word = None
        for word, mtype in _OBJECT_KEYWORDS.items():
            if word in msg_lower:
                matched_type = mtype
                matched_word = word
                break

        if matched_type and server_session is not None:
            color = None
            for cname, chex in _COLOR_KEYWORDS.items():
                if cname in msg_lower:
                    color = chex
                    break
            try:
                from server import generate_blender_script, run_blender, session as srv_sesh
                script, _ = generate_blender_script(matched_type, name=matched_type, color=color, keep_scene=True)
                # Try addon first
                try:
                    body = json.dumps({"code": script}).encode()
                    req = urllib.request.Request("http://localhost:9878/api/execute",
                        data=body, headers={"Content-Type": "application/json"}, method="POST")
                    addon_resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
                    if addon_resp.get("status") == "ok":
                        response = f"✅ {matched_word} created in scene"
                except:
                    pass
                if not response:
                    # Headless fallback
                    script_h, out_path = generate_blender_script(matched_type, name=matched_type, color=color, keep_scene=False)
                    run_blender(script_h)
                    if os.path.exists(out_path):
                        response = f"✅ {matched_word} generated ({os.path.basename(out_path)})"
                    else:
                        response = f"❌ Failed to generate {matched_word}"
            except Exception as e:
                response = f"❌ Error: {str(e)[:100]}"
        else:
            response = "I didn't get a response from the AI. Try asking when opencode is connected."

    # Store final status
    with _chat_lock:
        if msg_id in _chat_statuses:
            _chat_statuses[msg_id]["status"] = "done"
            if response:
                _chat_statuses[msg_id]["response"] = response
            _chat_statuses[msg_id]["timestamp"] = time.time()

    # Clean old statuses (keep last 50)
    with _chat_lock:
        ids = sorted(_chat_statuses.keys(), key=lambda i: _chat_statuses[i]["timestamp"], reverse=True)
        for old_id in ids[50:]:
            del _chat_statuses[old_id]


def start_http_server(port: int = HTTP_PORT):
    global server_instance
    server_instance = HTTPServer(("0.0.0.0", port), MCPBridgeHandler)
    thread = threading.Thread(target=server_instance.serve_forever, daemon=True)
    thread.start()
    print(f"[HTTP Bridge] Server running on http://0.0.0.0:{port}")
    print(f"[HTTP Bridge] Endpoints: GET /api/health, GET /api/models, GET /api/providers, GET /api/chat/status, POST /api/fetch-all-models, POST /api/set-model, POST /api/chat, POST /api/generate")
    return server_instance


def stop_http_server():
    global server_instance
    if server_instance:
        server_instance.shutdown()
        server_instance = None


if __name__ == "__main__":
    print("Starting HTTP bridge server...")
    start_http_server()
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        stop_http_server()
        print("Stopped.")
