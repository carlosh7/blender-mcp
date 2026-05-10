"""
HTTP Bridge for blender-mcp.
Provides REST endpoints for the Blender addon to communicate with the MCP server.
Runs on port 9877 by default.
Endpoints:
  GET  /api/health       → { status: "ok" }
  GET  /api/models       → list of available model types
  POST /api/chat         → process a chat message
  POST /api/generate     → generate a 3D model
"""
import json
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
MODELS_DIR = ROOT / "models"
os.makedirs(MODELS_DIR, exist_ok=True)

HTTP_PORT = 9877
server_instance = None


class MCPBridgeHandler(BaseHTTPRequestHandler):
    """HTTP handler that bridges Blender addon requests to the MCP system."""

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
                "models_dir": str(MODELS_DIR),
                "models_count": len(list(MODELS_DIR.glob("*.glb"))),
                "suggested_models": [
                    "claude-sonnet-4-5", "claude-haiku-4-5",
                    "gpt-4o", "gpt-4o-mini",
                    "deepseek-chat", "deepseek-reasoner",
                    "mistral-large", "llama-3.3-70b",
                    "gemini-2.0-flash",
                ],
                "openrouter": "https://openrouter.ai/models — 300+ models available",
            })

        elif parsed.path == "/api/models":
            # Return available model types from the server module
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

        elif parsed.path == "/api/opencode-config":
            """Read opencode config to find configured model."""
            config_paths = [
                Path.home() / ".config" / "opencode" / "opencode.json",
                Path.home() / ".config" / "opencode" / "opencode.jsonc",
                Path.cwd() / "opencode.json",
            ]
            model = None
            provider = None
            for p in config_paths:
                if p.exists():
                    try:
                        data = json.loads(p.read_text())
                        model = data.get("model", model)
                        if "provider" in data:
                            provider = list(data["provider"].keys())[0] if isinstance(data["provider"], dict) else provider
                    except: pass
            self._send_json({
                "model": model or "unknown",
                "provider": provider or "opencode",
                "config_files_found": [str(p) for p in config_paths if p.exists()],
            })

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/chat":
            body = self._read_body()
            message = body.get("message", "")
            model = body.get("model", "default")

            if not message:
                self._send_json({"error": "Empty message"}, 400)
                return

            # Process via template matching (simple approach without MCP client)
            response = self._process_chat(message, model)
            self._send_json(response)

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
                    # Copy to check path if configured
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

    def _process_chat(self, message: str, model: str = "default") -> dict:
        """Process a chat message using template matching."""
        msg_lower = message.lower()

        # Check for model generation requests
        if any(w in msg_lower for w in ["chair", "silla", "asiento", "seat"]):
            return {
                "response": "I'll create a chair for you. Use the Generate button or type more details (color, size).",
                "action": "generate",
            }
        if any(w in msg_lower for w in ["table", "mesa"]):
            return {
                "response": "I can create a table. Specify round or rectangular and I'll generate it.",
                "action": "generate",
            }
        if any(w in msg_lower for w in ["stage", "escenario", "tarima", "platform"]):
            return {
                "response": "I'll create a stage/platform. Specify dimensions if you want something custom.",
                "action": "generate",
            }
        if any(w in msg_lower for w in ["help", "ayuda", "?"]):
            return {
                "response": "Available commands: 'create a chair', 'make a table', 'build a stage', 'capture the scene', 'export to glb'.",
                "action": "none",
            }

        return {
            "response": "Message received! Describe what 3D model you want: chair, table, stage, etc.",
            "action": "none",
        }


def start_http_server(port: int = HTTP_PORT):
    """Start the HTTP bridge server in a background thread."""
    global server_instance
    server_instance = HTTPServer(("0.0.0.0", port), MCPBridgeHandler)
    thread = threading.Thread(target=server_instance.serve_forever, daemon=True)
    thread.start()
    print(f"[HTTP Bridge] Server running on http://0.0.0.0:{port}")
    print(f"[HTTP Bridge] Endpoints: GET /api/health, GET /api/models, POST /api/chat, POST /api/generate")
    return server_instance


def stop_http_server():
    """Stop the HTTP bridge server."""
    global server_instance
    if server_instance:
        server_instance.shutdown()
        server_instance = None


if __name__ == "__main__":
    print("Starting HTTP bridge server...")
    start_http_server()
    try:
        threading.Event().wait()  # Keep alive
    except KeyboardInterrupt:
        stop_http_server()
        print("Stopped.")
