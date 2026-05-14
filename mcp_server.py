#!/usr/bin/env python3
import json, os, sys, time, logging, threading, tempfile
from pathlib import Path

# Usamos imports relativos para cumplir con las políticas de Blender 4.2
from .blender_mcp.platform import get_log_dir, SYSTEM as SYS
from .blender_connection import get_blender, BlenderConnection
from . import config

_log_dir = get_log_dir()
_log_file = str(_log_dir / "server.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(_log_file)]
)
logger = logging.getLogger("blender-mcp")
logger.info(f"Log file: {_log_file}")

# ─── FastMCP Server ───
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
mcp = FastMCP("blender-mcp", log_level="INFO")

def RO():
    return dict(annotations=ToolAnnotations(readOnlyHint=True))
def RW():
    return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
def ADD():
    return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False))

_proxy_active = False  # Track if external MCP client handles chat

# ─── Register modular tools (blender_mcp/tools/) ───
from .blender_mcp.tools import (
    polyhaven, sketchfab, hyper3d, hunyuan, ambientcg,
    shader_nodes, animation, geometry_nodes, render,
    io, uv_texture, batch, rigging, scene_utils, printing,
    analysis, docs, viewport, ui, connection, expert, av_tools, assembly,
)
for mod in [polyhaven, sketchfab, hyper3d, hunyuan, ambientcg,
             shader_nodes, animation, geometry_nodes, render,
             io, uv_texture, batch, rigging, scene_utils, printing,
             analysis, docs, viewport, ui, connection, expert, av_tools, assembly]:
    mod.register_tools(mcp)

@mcp.tool(**RO())
def get_scene_info() -> str:
    """Get information about the current Blender scene (objects, counts, names)."""
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)

@mcp.tool(**RW())
def execute_blender_code(code: str) -> str:
    """Ejecuta código Python arbitrario en Blender. Usa bpy, C (bpy.context), D (bpy.data), ops (bpy.ops)."""
    b = get_blender()
    result = b.send_command("execute_code", {"code": code})
    return f"Salida:\n{result.get('output', '')}"

@mcp.tool(**RO())
def get_viewport_screenshot() -> str:
    """Captura una imagen del viewport 3D de Blender. Retorna la ruta del archivo."""
    b = get_blender()
    result = b.send_command("get_viewport_screenshot")
    if "error" in result:
        return f"Error al capturar: {result['error']}"
    return f"Captura Axiom guardada en: {result['filepath']} ({result['width']}x{result['height']})"

@mcp.tool(**RO())
def search_assets(provider: str = "polyhaven", query: str = "", asset_type: str = "textures") -> str:
    """Busca assets externos (Polyhaven o Sketchfab). 
    Tipos para Polyhaven: textures, hdris, models."""
    b = get_blender()
    result = b.send_command("search_assets", {"provider": provider, "query": query, "asset_type": asset_type})
    return json.dumps(result, indent=2)

@mcp.tool(**RW())
def generate_3d_model(prompt: str) -> str:
    """Inicia la generación de un modelo 3D por IA usando Rodin/Hyper3D a partir de un texto."""
    b = get_blender()
    result = b.send_command("generate_3d", {"prompt": prompt})
    return json.dumps(result, indent=2)

@mcp.tool(**RO())
def get_scene_visual() -> str:
    """Get a top-down ASCII visualization of the scene for spatial reasoning."""
    from .blender_mcp.spatial import get_spatial_summary
    b = get_blender()
    scene_info = b.send_command("get_scene_info")
    return get_spatial_summary(scene_info)

@mcp.tool(**ADD())
def chat_send(message: str) -> str:
    """Send a message to the Blender chat (from external tools). User messages go here."""
    global _proxy_active
    _proxy_active = True
    b = get_blender()
    result = b.send_command("chat_send", {"message": message})
    return json.dumps(result)

@mcp.tool(**RW())
def export_to_planner(name: str) -> str:
    """Export the current Blender scene as a .glb model to the 3D Planner directory."""
    from .config import PLANNER_MODELS_DIR
    b = get_blender()
    filename = f"{name}.glb" if not name.endswith(".glb") else name
    path = str(PLANNER_MODELS_DIR / filename)
    result = b.send_command("export_glb", {"filepath": path})
    return json.dumps(result, indent=2)

@mcp.tool(**RO())
def read_chat() -> str:
    """Read pending chat messages from the Blender user. Returns messages waiting for AI response."""
    b = get_blender()
    result = b.send_command("read_chat")
    return json.dumps(result, indent=2)

@mcp.tool(**RW())
def respond_chat(message_id: str, response: str) -> str:
    """Respond to a pending chat message from Blender. The user will see this in the chat panel."""
    global _proxy_active
    _proxy_active = True
    b = get_blender()
    result = b.send_command("respond_chat", {"message_id": message_id, "response": response})
    return json.dumps(result)

@mcp.tool(**RW())
def clear_history() -> str:
    """Clear the AI agent's conversation history/memory."""
    global _chat_history
    _chat_history = []
    b = get_blender()
    b.send_command("clear_chat")
    return "History cleared."

@mcp.tool(**RO())
def poll_response(message_id: str) -> str:
    """Check if a response is ready for a chat message. Returns {status: 'done'/'pending', response: '...'}"""
    b = get_blender()
    result = b.send_command("poll_response", {"message_id": message_id})
    return json.dumps(result)

# ─── Resources MCP ───
@mcp.resource("blender://scene/info")
def resource_scene_info() -> str:
    """Current Blender scene overview: name, object count, materials count."""
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)

@mcp.resource("blender://scene/objects")
def resource_scene_objects() -> str:
    """List all objects in the current Blender scene with types and locations."""
    b = get_blender()
    info = b.send_command("get_scene_info")
    return json.dumps(info.get("objects", []), indent=2)

@mcp.resource("blender://scene/materials")
def resource_scene_materials() -> str:
    """List all materials in the current Blender scene."""
    b = get_blender()
    result = b.send_command("list_materials")
    return json.dumps(result, indent=2)

# ─── Image Response MCP ───
from mcp.server.fastmcp import Image as MCPImage

@mcp.tool(**RO())
def get_viewport_screenshot_image() -> object:
    """Capture a screenshot of the Blender 3D viewport and return as an image."""
    import tempfile
    b = get_blender()
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    result = b.send_command("get_viewport_screenshot", {"filepath": tmp, "max_size": 800})
    if "error" in result:
        return {"error": result["error"]}
    try:
        with open(tmp, "rb") as f:
            img_data = f.read()
        return MCPImage(data=img_data, format="png")
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.unlink(tmp)
        except:
            pass

# ─── Agent Host Logic ───
MEMORY_PATH = str(get_log_dir().parent / "server_memory.json")

def save_memory(history):
    try:
        os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
        with open(MEMORY_PATH, 'w') as f:
            json.dump(history, f, indent=2)
    except: pass

def load_memory():
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, 'r') as f:
                return json.load(f)
        except: pass
    return []

_processed_ids = set()
_chat_history = load_memory()
_last_ping = 0
_auto_connection = None

def _get_auto_connection():
    global _auto_connection
    if _auto_connection is None:
        from .blender_connection import SOCKET_HOST, SOCKET_PORT
        _auto_connection = BlenderConnection(host=SOCKET_HOST, port=SOCKET_PORT)
    if not _auto_connection.sock:
        _auto_connection.connect()
    return _auto_connection

def _agent_send(cmd_type, params=None):
    b = _get_auto_connection()
    return b.send_command(cmd_type, params or {})

def _auto_process():
    global _chat_history, _last_ping, _proxy_active, _auto_connection
    from .blender_mcp.tool_cache import invalidate as cache_invalidate
    while True:
        try:
            b = _get_auto_connection()
            if not b:
                time.sleep(2)
                continue

            try:
                res = b.send_command("get_clear_signal")
                if res and res.get("clear"):
                    _chat_history.clear()
                    cache_invalidate()
                    if os.path.exists(MEMORY_PATH): os.remove(MEMORY_PATH)
                now = time.time()
                if now - _last_ping > 2:
                    b.send_command("ping")
                    _last_ping = now
            except: pass

            try:
                result = b.send_command("read_chat")
                messages = result.get("messages", [])
            except:
                time.sleep(1)
                continue

            if not messages:
                time.sleep(0.5)
                continue

            for msg in messages:
                mid = msg.get("id")
                if not mid or mid in _processed_ids: continue
                _processed_ids.add(mid)

                text = msg.get("message", "")
                if _proxy_active: continue

                def status_cb(t):
                    try: b.send_command("respond_status", {"message_id": mid, "response": t})
                    except: pass

                def check_stop_cb():
                    try: return b.send_command("is_stopped").get("stopped", False)
                    except: return False

                try:
                    from . import agent_host
                    import importlib
                    importlib.reload(agent_host)

                    _chat_history = agent_host.process_message(
                        text, _agent_send, history=_chat_history,
                        status_callback=status_cb, check_stop_callback=check_stop_cb,
                    )
                    save_memory(_chat_history)
                except Exception as e:
                    logger.error(f"Agent error: {e}")
                finally:
                    try: b.send_command("respond_chat", {"message_id": mid, "response": ""})
                    except: pass

            if len(_processed_ids) > 1000: _processed_ids.clear()

        except Exception as e:
            logger.error(f"Auto-process error: {e}")
        time.sleep(0.5)

def main():
    logger.info("Starting blender-mcp MCP server...")
    from .blender_connection import SOCKET_HOST, SOCKET_PORT
    
    t = threading.Thread(target=_auto_process, daemon=True)
    t.start()
    
    try:
        import uvicorn
        from starlette.responses import HTMLResponse
        sse_app = mcp.sse_app()
        uvicorn.run(sse_app, host="127.0.0.1", port=9879, log_level="warning")
    except Exception as e:
        logger.warning(f"SSE server error: {e}")

if __name__ == "__main__":
    main()
