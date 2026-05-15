#!/usr/bin/env python3
import json, os, sys, time, logging, threading, tempfile
from pathlib import Path

# Usamos imports relativos para cumplir con las políticas de Blender 4.2
from blender_mcp.platform import get_log_dir, SYSTEM as SYS
from blender_connection import get_blender, BlenderConnection
import config

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

_proxy_active = False

# ─── Register modular tools (blender_mcp/tools/) ───
from blender_mcp.tools import (
    polyhaven, sketchfab, hyper3d, hunyuan, ambientcg,
    shader_nodes, animation, geometry_nodes, render,
    io, uv_texture, batch, rigging, scene_utils, printing,
    analysis, docs, viewport, ui, connection, expert, av_tools, assembly,
)
_mods = [polyhaven, sketchfab, hyper3d, hunyuan, ambientcg,
         shader_nodes, animation, geometry_nodes, render,
         io, uv_texture, batch, rigging, scene_utils, printing,
         analysis, docs, viewport, ui, connection, expert, av_tools, assembly]

for mod in _mods:
    mod.register_tools(mcp)

@mcp.tool(**RO())
def get_scene_info() -> str:
    """Get information about the current Blender scene."""
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)

@mcp.tool(**RW())
def execute_blender_code(code: str) -> str:
    """Ejecuta código Python arbitrario en Blender."""
    b = get_blender()
    result = b.send_command("execute_code", {"code": code})
    return f"Salida:\n{result.get('output', '')}"

@mcp.tool(**RO())
def get_viewport_screenshot() -> str:
    """Captura una imagen del viewport 3D de Blender."""
    b = get_blender()
    result = b.send_command("get_viewport_screenshot")
    if "error" in result: return f"Error: {result['error']}"
    return f"Captura Axiom guardada en: {result['filepath']}"

# ─── Resources ───
@mcp.resource("blender://scene/info")
def resource_scene_info() -> str:
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)

# ─── Agent Host Logic ───
MEMORY_PATH = str(get_log_dir().parent / "server_memory.json")
def save_memory(h):
    try:
        with open(MEMORY_PATH, 'w') as f: json.dump(h, f, indent=2)
    except: pass
def load_memory():
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, 'r') as f: return json.load(f)
        except: pass
    return []

_processed_ids = set()
_chat_history = load_memory()
_last_ping = 0
_auto_connection = None

def _get_auto_connection():
    global _auto_connection
    if _auto_connection is None:
        from blender_connection import SOCKET_HOST, SOCKET_PORT
        _auto_connection = BlenderConnection(host=SOCKET_HOST, port=SOCKET_PORT)
    if not _auto_connection.sock: _auto_connection.connect()
    return _auto_connection

def _auto_process():
    global _chat_history, _last_ping, _proxy_active
    while True:
        try:
            b = _get_auto_connection()
            if not b:
                time.sleep(1)
                continue
            
            try:
                res = b.send_command("get_clear_signal")
                if res and res.get("clear"):
                    _chat_history.clear()
                    if os.path.exists(MEMORY_PATH): os.remove(MEMORY_PATH)
                now = time.time()
                if now - _last_ping > 2:
                    b.send_command("ping")
                    _last_ping = now
            except: pass

            try:
                result = b.send_command("read_chat")
                messages = result.get("messages", [])
                for msg in messages:
                    mid = msg.get("id")
                    if mid not in _processed_ids:
                        _processed_ids.add(mid)
                        import agent_host
                        _chat_history = agent_host.process_message(msg.get("message"), b.send_command, history=_chat_history)
                        save_memory(_chat_history)
                        b.send_command("respond_chat", {"message_id": mid, "response": ""})
            except: pass
        except Exception as e: logger.error(f"Auto-process: {e}")
        time.sleep(0.5)

# ─── Web UI & Server ───
def main():
    logger.info("Iniciando Axiom MCP Server...")
    from blender_connection import SOCKET_HOST, SOCKET_PORT
    
    threading.Thread(target=_auto_process, daemon=True).start()
    
    try:
        import uvicorn
        from starlette.responses import HTMLResponse
        from starlette.middleware.cors import CORSMiddleware
        
        def _make_html():
            tools_count = len(mcp._tool_manager.list_tools())
            return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>AXIOM Diagnostic</title>
<style>
body{{font-family:sans-serif;background:#0d0d0d;color:#00f2ff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}}
.card{{background:#1a1a1a;padding:2rem;border-radius:12px;border:1px solid #00f2ff;box-shadow:0 0 20px #00f2ff44;width:400px}}
h1{{font-size:1.5rem;margin-bottom:0.5rem}}
.status{{margin:1rem 0;padding:0.5rem;background:#000;border-radius:4px;font-family:monospace}}
.dot{{height:10px;width:10px;background:#00f2ff;border-radius:50%;display:inline-block;margin-right:8px;box-shadow:0 0 8px #00f2ff}}
a{{color:#fff;text-decoration:none;border-bottom:1px solid #00f2ff}}
</style></head>
<body><div class="card">
<h1>AXIOM ENGINE ●</h1>
<div class="status"><span class="dot"></span> v0.8.83 Stable</div>
<div class="status"><span class="dot"></span> {tools_count} Tools Loaded</div>
<div class="status"><span class="dot"></span> Socket: {SOCKET_HOST}:{SOCKET_PORT}</div>
<div class="status"><span class="dot"></span> <a href="/sse">SSE Stream Active</a></div>
<div style="margin-top:1rem;font-size:0.8rem;color:#666">© 2026 Axiom Precision Engine</div>
</div></body></html>"""

        sse_app = mcp.sse_app()
        async def app(scope, receive, send):
            if scope["type"] == "http" and scope["path"] == "/":
                html = _make_html()
                await send({ "type": "http.response.start", "status": 200, "headers": [[b"content-type", b"text/html"]] })
                await send({ "type": "http.response.body", "body": html.encode() })
            elif scope["type"] == "http" and scope["path"] == "/health":
                body = json.dumps({"status":"ok","socket":f"{SOCKET_HOST}:{SOCKET_PORT}"})
                await send({ "type": "http.response.start", "status": 200, "headers": [[b"content-type", b"application/json"]] })
                await send({ "type": "http.response.body", "body": body.encode() })
            else:
                await sse_app(scope, receive, send)

        uvicorn.run(app, host="127.0.0.1", port=9879, log_level="warning")
    except Exception as e: logger.warning(f"SSE Error: {e}")

if __name__ == "__main__":
    main()
