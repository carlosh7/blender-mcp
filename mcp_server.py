#!/usr/bin/env python3
"""
blender-mcp — MCP Server that connects to Blender's socket server (port 9876).
Replaces server.py + http_bridge.py.
Connect: opencode mcp uses this via opencode.json → uvx blender-mcp (or python mcp_server.py)
"""
import json, socket, os, sys, time, logging, threading
from pathlib import Path
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("blender-mcp")

SOCKET_HOST = os.getenv("BLENDER_HOST", "localhost")
SOCKET_PORT = int(os.getenv("BLENDER_PORT", "9876"))
ROOT = Path(__file__).parent.resolve()

# ─── Blender Socket Connection ───
_connection = None
_connection_lock = threading.Lock()

class BlenderConnection:
    def __init__(self, host=SOCKET_HOST, port=SOCKET_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        if self.sock:
            return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10.0)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Blender: {e}")
            self.sock = None
            return False

    def disconnect(self):
        if self.sock:
            try: self.sock.close()
            except: pass
            self.sock = None

    def send_command(self, cmd_type, params=None):
        with _connection_lock:
            if not self.sock and not self.connect():
                raise ConnectionError("Not connected to Blender")
            cmd = {"type": cmd_type, "params": params or {}}
            try:
                self.sock.sendall(json.dumps(cmd).encode('utf-8'))
                self.sock.settimeout(180.0)
                buffer = b''
                while True:
                    chunk = self.sock.recv(65536)
                    if not chunk:
                        break
                    buffer += chunk
                    try:
                        resp = json.loads(buffer.decode('utf-8'))
                        if resp.get("status") == "error":
                            raise Exception(resp.get("message", "Blender error"))
                        return resp.get("result", {})
                    except json.JSONDecodeError:
                        continue
                raise Exception("No response from Blender")
            except (ConnectionError, BrokenPipeError) as e:
                self.sock = None
                raise Exception(f"Connection lost: {e}")
            except socket.timeout:
                self.sock = None
                raise Exception("Blender timeout")

def get_blender():
    global _connection
    if _connection is None:
        _connection = BlenderConnection()
    if not _connection.sock:
        _connection.connect()
    return _connection


# ─── FastMCP Server ───
mcp = FastMCP("blender-mcp", log_level="INFO")

@mcp.tool()
def get_scene_info() -> str:
    """Get information about the current Blender scene (objects, counts, names)."""
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)

@mcp.tool()
def execute_blender_code(code: str) -> str:
    """Execute arbitrary Python code in Blender. Use bpy, C (bpy.context), D (bpy.data), ops (bpy.ops).
    Create objects step by step in small chunks. Always check the result before proceeding."""
    b = get_blender()
    result = b.send_command("execute_code", {"code": code})
    return f"Output:\n{result.get('output', '')}"

@mcp.tool()
def chat_send(message: str) -> str:
    """Send a message to the Blender chat (from external tools). User messages go here."""
    b = get_blender()
    result = b.send_command("chat_send", {"message": message})
    return json.dumps(result)

@mcp.tool()
def read_chat() -> str:
    """Read pending chat messages from the Blender user. Returns messages waiting for AI response."""
    b = get_blender()
    result = b.send_command("read_chat")
    return json.dumps(result, indent=2)

@mcp.tool()
def respond_chat(message_id: str, response: str) -> str:
    """Respond to a pending chat message from Blender. The user will see this in the chat panel."""
    b = get_blender()
    result = b.send_command("respond_chat", {"message_id": message_id, "response": response})
    return json.dumps(result)

@mcp.tool()
def poll_response(message_id: str) -> str:
    """Check if a response is ready for a chat message. Returns {status: 'done'/'pending', response: '...'}"""
    b = get_blender()
    result = b.send_command("poll_response", {"message_id": message_id})
    return json.dumps(result)


# ─── Agent Host: processes all Blender chat messages via LLM ───
_processed_ids = set()
_last_ping = 0

def _agent_send(cmd_type, params=None):
    """Helper: send command to Blender and return result."""
    b = get_blender()
    return b.send_command(cmd_type, params or {})


def _auto_process():
    """Background thread: keeps ping alive, forwards chat messages to agent_host."""
    global _last_ping
    while True:
        try:
            b = get_blender()
            # Send ping every 5s so addon knows MCP is alive
            now = time.time()
            if now - _last_ping > 5:
                try:
                    b.send_command("ping")
                    _last_ping = now
                except:
                    pass
            # Check for new messages
            result = b.send_command("read_chat")
            messages = result.get("messages", [])
            for msg in messages:
                mid = msg["id"]
                if mid in _processed_ids:
                    continue
                _processed_ids.add(mid)
                text = msg.get("message", "")
                logger.info(f"New chat message: {text[:80]}")
                # Acknowledge immediately so spinner stops
                try:
                    b.send_command("respond_chat", {
                        "message_id": mid,
                        "response": "Processing..."
                    })
                except:
                    pass
                # Process via agent_host (LLM)
                try:
                    import agent_host
                    response = agent_host.process_message(text, _agent_send)
                except Exception as e:
                    response = f"Error processing: {str(e)[:100]}"
                    logger.error(f"Agent error: {e}")
                # Send final response
                try:
                    b.send_command("respond_chat", {
                        "message_id": mid,
                        "response": response
                    })
                except Exception as e:
                    logger.error(f"Failed to send response: {e}")
            if len(_processed_ids) > 500:
                _processed_ids.clear()
        except Exception:
            pass
        time.sleep(2)


def main():
    logger.info("Starting blender-mcp MCP server...")
    logger.info(f"Blender socket: {SOCKET_HOST}:{SOCKET_PORT}")
    # Start auto-processor
    t = threading.Thread(target=_auto_process, daemon=True)
    t.start()
    logger.info("Auto-processor thread started")
    # Use SSE transport for persistence
    import uvicorn
    starlette_app = mcp.sse_app()
    logger.info(f"SSE endpoint ready, starting HTTP on port 9879")
    uvicorn.run(starlette_app, host="127.0.0.1", port=9879, log_level="info")

if __name__ == "__main__":
    main()
