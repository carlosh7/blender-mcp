#!/usr/bin/env python3
"""
blender-mcp — MCP Server that connects to Blender's socket server (port 9876).
Replaces server.py + http_bridge.py.
Connect: opencode mcp uses this via opencode.json → uvx blender-mcp (or python mcp_server.py)
"""
import json, os, sys, time, logging, threading, tempfile
from pathlib import Path
ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from blender_mcp.platform import get_log_dir, SYSTEM as SYS

_log_dir = get_log_dir()
_log_file = str(_log_dir / "server.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(_log_file)]
)
logger = logging.getLogger("blender-mcp")
logger.info(f"Log file: {_log_file}")

ROOT = Path(__file__).parent.resolve()

from blender_connection import get_blender, BlenderConnection


# ─── FastMCP Server ───
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
mcp = FastMCP("blender-mcp", log_level="INFO")

def RO(doc=""):
    return dict(annotations=ToolAnnotations(readOnlyHint=True), description=doc)
def RW(doc=""):
    return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), description=doc)
def ADD(doc=""):
    return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), description=doc)

_proxy_active = False  # Track if external MCP client handles chat (starts as False)

# ─── Register modular tools (src/blender_mcp/tools/) ───
from blender_mcp.tools import (
    polyhaven, sketchfab, hyper3d, hunyuan, ambientcg,
    shader_nodes, animation, geometry_nodes, render,
    io, uv_texture, batch, rigging, scene_utils, printing,
    analysis, docs, viewport, ui,
)
for mod in [polyhaven, sketchfab, hyper3d, hunyuan, ambientcg,
             shader_nodes, animation, geometry_nodes, render,
             io, uv_texture, batch, rigging, scene_utils, printing,
             analysis, docs, viewport, ui]:
    mod.register_tools(mcp)

@mcp.tool(**RO("Get information about the current Blender scene (objects, counts, names)."))
def get_scene_info() -> str:
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)

@mcp.tool(**RW("Ejecuta código Python arbitrario en Blender. Usa bpy, C (bpy.context), D (bpy.data), ops (bpy.ops)."))
def execute_blender_code(code: str) -> str:
    b = get_blender()
    result = b.send_command("execute_code", {"code": code})
    return f"Salida:\n{result.get('output', '')}"

@mcp.tool(**RO("Captura una imagen del viewport 3D de Blender. Retorna la ruta del archivo."))
def get_viewport_screenshot() -> str:
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
    from blender_mcp.spatial import get_spatial_summary
    b = get_blender()
    scene_info = b.send_command("get_scene_info")
    return get_spatial_summary(scene_info)

@mcp.tool(**ADD())
def chat_send(message: str) -> str:
    """Send a message to the Blender chat (from external tools). User messages go here."""
    global _proxy_active
    _proxy_active = True  # External client detected (Fase 4)
    b = get_blender()
    result = b.send_command("chat_send", {"message": message})
    return json.dumps(result)

@mcp.tool(**RW())
def export_to_planner(name: str) -> str:
    """Export the current Blender scene as a .glb model to the 3D Planner directory."""
    from config import PLANNER_MODELS_DIR
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
    _proxy_active = True  # External client responded (Fase 4)
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


# ─── Resources MCP (Fase 5) ───
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

@mcp.resource("blender://scene/active-object")
def resource_active_object() -> str:
    """Information about the currently active/selected object."""
    import bpy
    try:
        obj = bpy.context.active_object
        if not obj:
            return json.dumps({"error": "No active object"})
        return json.dumps({
            "name": obj.name,
            "type": obj.type,
            "location": [round(float(obj.location.x), 2), round(float(obj.location.y), 2), round(float(obj.location.z), 2)],
            "dimensions": [round(d, 3) for d in obj.dimensions],
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ─── Prompts MCP (Fase 5) ───
@mcp.prompt()
def asset_creation_strategy() -> str:
    """Preferred strategy for creating 3D assets in Blender. Guides the LLM on integration priorities."""
    return """When creating 3D content in Blender, follow this priority strategy:

1. First check scene state with get_scene_info() and blender://scene/info
2. Check available integrations:
   - Poly Haven: Use get_polyhaven_status(). Best for HDRI environments, PBR textures, 3D models.
   - Sketchfab: Use get_sketchfab_status(). Best for realistic models, wider variety than Poly Haven.
   - Hyper3D Rodin: Use get_hyper3d_status(). Best for generating single items from text.
   - AmbientCG: Free PBR materials, no API key needed.
3. For custom geometry use execute_blender_code() with bpy step by step
4. Always validate with get_viewport_screenshot() after each phase

Recommended priority: Sketchfab > Poly Haven > Hyper3D Rodin > Manual scripting
For environment lighting: Poly Haven HDRIs first
For materials/textures: AmbientCG or Poly Haven textures first"""


@mcp.prompt()
def scene_analysis_strategy() -> str:
    """Strategy for analyzing and debugging Blender scenes. Inspired by blender.org MCP."""
    return """When analyzing a Blender scene, follow this systematic approach:

1. SCENE OVERVIEW: Use blender://scene/info to get counts and names
2. PERFORMANCE ANALYSIS: Check for high-poly objects with low screen impact:
   - Use mesh_analysis() on suspicious objects
   - Look for objects with Subsurf modifiers that could be simplified
   - Check for objects with high vertex counts that are small in viewport
3. DATA-BLOCK AUDIT:
   - Check for orphaned data blocks with purge_orphans()
   - Find materials not assigned to any object
   - Look for naming inconsistencies
4. GEOMETRY VALIDATION:
   - Use check_manifold() for 3D printing readiness
   - Use validate_geometry() (Axiom engine) for collision detection
5. SPATIAL REASONING:
   - Use get_scene_visual() for top-down ASCII view
   - Verify objects are not clipping into each other

Always report findings in a structured format with object names, counts, and specific recommendations."""


@mcp.prompt()
def geometry_nodes_documentation() -> str:
    """Document and explain Geometry Nodes setups. Creates inline documentation frames."""
    return """When documenting a Geometry Nodes setup:

1. Use list_gn_modifiers() to identify all GN modifiers in the scene
2. For each modifier, use add_gn_node() to add frame nodes for organization:
   - Create labeled frame nodes around logical sections
   - Use distinct colors: green for input, blue for process, orange for output
3. Document the data flow:
   - What geometry enters the system
   - What transformations are applied at each stage
   - How instances are distributed and transformed
   - What the final output contains
4. Create a text data-block with analysis if the setup is complex
5. Suggest optimizations:
   - Unlabeled nodes that should be renamed
   - Repeated patterns that could be simplified
   - Missing seed inputs for randomization

Keep documentation in simple English so a beginner can understand the flow."""


# ─── Image Response MCP (Fase 5) ───
from mcp.server.fastmcp import Image as MCPImage

@mcp.tool(**RO())
def get_viewport_screenshot_image() -> object:
    """Capture a screenshot of the Blender 3D viewport and return as an image.
    Use this for visual validation directly visible to the LLM (not just a file path)."""
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


# ─── Agent Host: processes all Blender chat messages via LLM ───
# ─── Persistencia de Memoria ───
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
    """Dedicated connection for auto-process thread (no conflict with SSE tools)."""
    global _auto_connection
    if _auto_connection is None:
        from blender_connection import SOCKET_HOST, SOCKET_PORT
        _auto_connection = BlenderConnection(host=SOCKET_HOST, port=SOCKET_PORT)
    if not _auto_connection.sock:
        _auto_connection.connect()
    return _auto_connection

def _agent_send(cmd_type, params=None):
    """Helper: send command to Blender and return result (uses dedicated connection)."""
    b = _get_auto_connection()
    return b.send_command(cmd_type, params or {})


def _auto_process():
    """Background thread: keeps ping alive, detects proxy mode, forwards to agent_host if needed."""
    global _chat_history, _last_ping, _proxy_active, _auto_connection
    from blender_mcp.tool_cache import invalidate as cache_invalidate
    while True:
        try:
            b = _get_auto_connection()
            if not b:
                time.sleep(2)
                continue

            # ── 1. Ping + Señales ──
            try:
                res = b.send_command("get_clear_signal")
                if res and res.get("clear"):
                    _chat_history.clear()
                    cache_invalidate()
                    if os.path.exists(MEMORY_PATH): os.remove(MEMORY_PATH)
                    logger.info("Memory cleared by user.")
                now = time.time()
                if now - _last_ping > 2:
                    b.send_command("ping")
                    _last_ping = now
            except:
                pass

            # ── 2. Leer Mensajes ──
            try:
                result = b.send_command("read_chat")
                messages = result.get("messages", [])
            except:
                time.sleep(1)
                continue

            if not messages:
                time.sleep(0.5)
                continue
            else:
                logger.info(f"Auto-process found {len(messages)} pending messages")

            # ── 3. Detectar Proxy Mode ──
            proxy_handling = _proxy_active
            # Check agent mode from Blender scene
            try:
                mode_result = b.send_command("get_scene_property", {"prop": "blendermcp_agent_mode"})
                agent_mode = mode_result.get("value", "AUTO")
                if agent_mode == "PROXY":
                    proxy_handling = True
                elif agent_mode == "AUTONOMOUS":
                    proxy_handling = False
            except:
                pass

            for msg in messages:
                mid = msg.get("id")
                if not mid or mid in _processed_ids:
                    continue
                _processed_ids.add(mid)

                # Check if external client already responded to this msg
                try:
                    poll = b.send_command("poll_response", {"message_id": mid})
                    if poll.get("status") == "done":
                        _proxy_active = True
                        proxy_handling = True
                        logger.info(f"Proxy handled message {mid[:8]} — skipping agent")
                        continue
                except:
                    pass

                text = msg.get("message", "")
                logger.info(f"New message: {text[:60]}...  proxy={proxy_handling}")

                if proxy_handling:
                    continue

                # ── 4. Procesar con Agente Autónomo ──
                _last_status_sent = ""

                def status_cb(t):
                    nonlocal _last_status_sent
                    if not t or t == _last_status_sent:
                        return
                    _last_status_sent = t
                    try:
                        b.send_command("respond_status", {"message_id": mid, "response": t})
                    except:
                        pass

                def check_stop_cb():
                    try:
                        return b.send_command("is_stopped").get("stopped", False)
                    except:
                        return False

                try:
                    import agent_host
                    import importlib
                    importlib.reload(agent_host)

                    if len(_chat_history) > 12:
                        _chat_history = [_chat_history[0]] + _chat_history[-11:]
                        logger.info("History trimmed to 12.")

                    _chat_history = agent_host.process_message(
                        text,
                        _agent_send,
                        history=_chat_history,
                        status_callback=status_cb,
                        check_stop_callback=check_stop_cb,
                    )
                    save_memory(_chat_history)

                except Exception as e:
                    logger.error(f"Agent error: {e}")
                    try:
                        status_cb(f"⚠️ Error: {str(e)[:60]}")
                    except:
                        pass
                finally:
                    # Remove processed message from queue to avoid infinite loop
                    try:
                        b.send_command("respond_chat", {"message_id": mid, "response": ""})
                    except:
                        pass

            if len(_processed_ids) > 1000:
                _processed_ids.clear()

        except Exception as e:
            logger.error(f"Auto-process error: {e}")

        time.sleep(0.5)


def main():
    logger.info("Starting blender-mcp MCP server...")
    from blender_connection import SOCKET_HOST, SOCKET_PORT
    logger.info(f"Blender socket: {SOCKET_HOST}:{SOCKET_PORT}")

    # Start auto-processor in a robust daemon thread
    def run_auto_process():
        while True:
            try:
                _auto_process()
            except Exception as e:
                logger.error(f"Auto-process crashed: {e}, restarting in 3s...")
                time.sleep(3)

    t = threading.Thread(target=run_auto_process, daemon=True)
    t.start()
    logger.info("Auto-processor thread started")

    # Start SSE + status page
    def run_sse():
        try:
            import uvicorn
            from starlette.responses import HTMLResponse
            from starlette.middleware.cors import CORSMiddleware

            # Build status page HTML
            def _make_html():
                tools_count = len(mcp._tool_manager.list_tools())
                from blender_connection import SOCKET_HOST, SOCKET_PORT
                return f"""<!DOCTYPE html>
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
a{{color:#64b5f6;text-decoration:none}} .f{{margin-top:1.5em;padding-top:1em;border-top:1px solid #2a2a4a;font-size:.8em;color:#666}}
</style></head>
<body><div class="card">
<h1>blender-mcp ●</h1><div class="v">v0.8.64</div>
<div class="s"><span class="g"></span> {tools_count} tools</div>
<div class="s"><span class="g"></span> Socket: {SOCKET_HOST}:{SOCKET_PORT}</div>
<div class="s"><span class="g"></span> <a href="/sse">SSE endpoint</a></div>
<div class="s"><span class="g"></span> <a href="/health">Health</a></div>
<div class="f">Clients: Claude · Cursor · opencode · Antigravity · LM Studio</div>
</div></body></html>"""

            sse_app = mcp.sse_app()
            sse_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

            # Mount SSE app + status page with a simple wrapper
            async def app(scope, receive, send):
                if scope["type"] == "http" and scope["path"] == "/":
                    html = _make_html()
                    await send({"type": "http.response.start", "status": 200, "headers": [
                        [b"content-type", b"text/html; charset=utf-8"],
                        [b"access-control-allow-origin", b"*"],
                    ]})
                    await send({"type": "http.response.body", "body": html.encode()})
                elif scope["type"] == "http" and scope["path"] == "/health":
                    await send({"type": "http.response.start", "status": 200, "headers": [
                        [b"content-type", b"application/json"],
                        [b"access-control-allow-origin", b"*"],
                    ]})
                    import json; from blender_connection import SOCKET_HOST, SOCKET_PORT
                    body = json.dumps({"status":"ok","version":"0.8.0","tools":len(mcp._tool_manager.list_tools()),"socket":f"{SOCKET_HOST}:{SOCKET_PORT}"})
                    await send({"type": "http.response.body", "body": body.encode()})
                else:
                    await sse_app(scope, receive, send)

            logger.info(f"Web UI at http://127.0.0.1:9879")
            uvicorn.run(app, host="127.0.0.1", port=9879, log_level="warning")
        except Exception as e:
            logger.warning(f"SSE server not available (port 9879): {e}")
            logger.warning("Chat agent still running via auto-processor")

    sse_thread = threading.Thread(target=run_sse, daemon=True)
    sse_thread.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(10)
            if not t.is_alive():
                logger.warning("Auto-process died, restarting...")
                t = threading.Thread(target=run_auto_process, daemon=True)
                t.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    main()
