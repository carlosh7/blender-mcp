#!/usr/bin/env python3
"""
blender-mcp — MCP Server that connects to Blender's socket server (port 9876).
Replaces server.py + http_bridge.py.
Connect: opencode mcp uses this via opencode.json → uvx blender-mcp (or python mcp_server.py)
"""
import json, socket, os, sys, time, logging, threading
import textwrap
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


# ─── Auto-processor: detects object keywords and generates models ───
_processed_ids = set()
_OBJECT_KEYWORDS = {
    "silla": "chair-folding", "chair": "chair-folding", "asiento": "chair-folding",
    "mesa": "table-round-150", "table": "table-round-150",
    "escenario": "stage-custom", "stage": "stage-custom", "tarima": "platform-2x2",
    "platform": "platform-2x2",
    "altavoz": "speaker", "speaker": "speaker", "bocina": "speaker",
    "pantalla": "led-flat", "screen": "led-flat", "monitor": "led-flat",
    "truss": "truss-straight",
    "valla": "barrier", "barrera": "barrier", "barrier": "barrier",
}
_COLOR_KEYWORDS = {
    "rojo": "#ff0000", "azul": "#0000ff", "verde": "#00ff00",
    "negro": "#000000", "blanco": "#ffffff", "gris": "#888888",
    "amarillo": "#ffff00", "dorado": "#ffd700", "plateado": "#c0c0c0",
    "madera": "#8B4513", "roble": "#8B4513", "oscuro": "#333333",
}


def _build_chair_script(color, scale):
    c = color or "#3b404a"
    r, g, b = int(c[1:3], 16) / 255, int(c[3:5], 16) / 255, int(c[5:7], 16) / 255
    return textwrap.dedent(f"""\
import bpy, math
S = {scale}
def make_mat(name, r, g, b, rough=0.5, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (r, g, b, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    return mat
metal = make_mat('metal', {r}, {g}, {b}, 0.3, 0.8)
plastic = make_mat('plastic', {r*0.8}, {g*0.8}, {b*0.8}, 0.6, 0.0)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.44*S))
bpy.context.active_object.scale = (0.2*S, 0.2*S, 0.02*S)
bpy.context.active_object.data.materials.append(plastic)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.68*S))
bpy.context.active_object.scale = (0.2*S, 0.15*S, 0.02*S)
bpy.context.active_object.data.materials.append(plastic)
for x, z in [(-0.085*S, -0.085*S), (0.085*S, -0.085*S), (-0.085*S, 0.085*S), (0.085*S, 0.085*S)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.01*S, depth=0.44*S, location=(x, 0, 0.22*S))
    bpy.context.active_object.data.materials.append(metal)
""")


_last_ping = 0

def _auto_process():
    """Background thread: polls Blender chat, auto-generates 3D objects from keywords."""
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
            result = b.send_command("read_chat")
            messages = result.get("messages", [])
            for msg in messages:
                mid = msg["id"]
                if mid in _processed_ids:
                    continue
                _processed_ids.add(mid)
                text = msg.get("message", "").lower()
                # Detect object keyword
                matched_type = None
                matched_word = None
                for word, mtype in _OBJECT_KEYWORDS.items():
                    if word in text:
                        matched_type = mtype
                        matched_word = word
                        break
                if matched_type:
                    # Detect color
                    color = None
                    for cname, chex in _COLOR_KEYWORDS.items():
                        if cname in text:
                            color = chex
                            break
                    # Generate script and execute
                    try:
                        if matched_type == "chair-folding":
                            code = _build_chair_script(color, 1.0)
                        else:
                            code = f"""
import bpy
S = 1.0
# {matched_type} - basic placeholder
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5*S))
bpy.context.active_object.scale = (0.5*S, 0.5*S, 0.5*S)
"""
                        b.send_command("execute_code", {"code": code})
                        response = f"Created {matched_word}!" + (f" ({color})" if color else "")
                    except Exception as e:
                        response = f"Error creating {matched_word}: {str(e)[:80]}"
                else:
                    response = None  # Leave for AI
                if response:
                    b.send_command("respond_chat", {"message_id": mid, "response": response})
            # Keep set bounded
            if len(_processed_ids) > 500:
                _processed_ids.clear()
        except Exception:
            pass  # Blender not connected yet
        time.sleep(2)


@mcp.prompt()
def blender_workflow() -> str:
    """Workflow for creating 3D content in Blender"""
    return """When working with Blender via this MCP server:

1. Check the chat periodically with `read_chat` for user messages.
2. For creating objects, use `execute_blender_code` with small Python scripts using bpy.
3. Respond to chat messages with `respond_chat` to confirm what was done.
4. Create objects step by step. Verify each step before proceeding.
5. Common objects: chair (silla), table (mesa), stage (escenario), speaker (altavoz), screen (pantalla).
"""


def main():
    logger.info("Starting blender-mcp MCP server...")
    logger.info(f"Blender socket: {SOCKET_HOST}:{SOCKET_PORT}")
    # Start auto-processor
    t = threading.Thread(target=_auto_process, daemon=True)
    t.start()
    logger.info("Auto-processor thread started")
    mcp.run()

if __name__ == "__main__":
    main()
