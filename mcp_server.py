#!/usr/bin/env python3
"""
blender-mcp — Simplified MCP Server
Exposes 6 core tools for controlling Blender via MCP protocol.
Compatible with opencode, Claude Desktop, Cursor, etc.
"""
import json, os, sys, time, logging, threading
from pathlib import Path

from blender_mcp.platform import get_log_dir
from blender_connection import get_blender

_log_dir = get_log_dir()
_log_file = str(_log_dir / "server.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(_log_file)]
)
logger = logging.getLogger("blender-mcp")

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
mcp = FastMCP("blender-mcp", log_level="INFO")

def RO():
    return dict(annotations=ToolAnnotations(readOnlyHint=True))
def RW():
    return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))


@mcp.tool(**RO())
def get_scene_info() -> str:
    """Get information about the current Blender scene (objects, counts, names)."""
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)

@mcp.tool(**RW())
def execute_blender_code(code: str) -> str:
    """Ejecuta código Python en Blender. Usa search_api_docs primero para encontrar la API correcta."""
    b = get_blender()
    result = b.send_command("execute_code", {"code": code})
    return f"Salida:\n{result.get('output', '')}"

@mcp.tool(**RO())
def get_viewport_screenshot() -> str:
    """Captura una imagen del viewport 3D de Blender."""
    b = get_blender()
    result = b.send_command("get_viewport_screenshot")
    if "error" in result: return f"Error: {result['error']}"
    return f"Captura guardada en: {result['filepath']}"

@mcp.tool(**RO())
def search_api_docs(query: str) -> str:
    """Busca en la documentación de Blender API. Siempre consulta esto ANTES de ejecutar código."""
    b = get_blender()
    result = b.send_command("search_api_docs", {"query": query})
    return json.dumps(result, indent=2)

@mcp.tool(**RO())
def get_python_api_docs(topic: str) -> str:
    """Obtiene documentación detallada de un tema específico de Blender API. Ej: 'bpy.ops.mesh.primitive_cylinder_add'."""
    b = get_blender()
    result = b.send_command("get_python_api_docs", {"topic": topic})
    return json.dumps(result, indent=2)

@mcp.tool(**RW())
def snap_and_parent(obj_move: str, obj_target: str, anchor_move: str, anchor_target: str) -> str:
    """Snap determinista y vinculación jerárquica automática (Parenting).
    Une dos objetos haciendo coincidir sus anclas (27-pt system).
    Formatos de ancla: A_MIN_MIN_MIN, A_CENTER_CENTER_CENTER, A_MAX_MAX_MAX."""
    b = get_blender()
    r = b.send_command("snap_and_parent", {
        "obj_move": obj_move, "obj_target": obj_target,
        "anchor_move": anchor_move, "anchor_target": anchor_target
    })
    return json.dumps(r, indent=2)


@mcp.resource("blender://scene/info")
def resource_scene_info() -> str:
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)


def main():
    logger.info("Starting MCP Server (6 tools)...")
    from blender_connection import SOCKET_HOST, SOCKET_PORT

    try:
        import uvicorn
        from starlette.responses import HTMLResponse
        from starlette.middleware.cors import CORSMiddleware

        tools_count = len(mcp._tool_manager.list_tools())

        sse_app = mcp.sse_app()
        async def app(scope, receive, send):
            if scope["type"] == "http" and scope["path"] == "/":
                html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>blender-mcp</title>
<style>
body{{font-family:sans-serif;background:#0d0d0d;color:#00f2ff;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}}
.card{{background:#1a1a1a;padding:2rem;border-radius:12px;border:1px solid #00f2ff;width:400px}}
h1{{font-size:1.5rem;margin-bottom:0.5rem}}
.status{{margin:1rem 0;padding:0.5rem;background:#000;border-radius:4px;font-family:monospace}}
.dot{{height:10px;width:10px;background:#00f2ff;border-radius:50%;display:inline-block;margin-right:8px}}
</style></head>
<body><div class="card">
<h1>blender-mcp</h1>
<div class="status"><span class="dot"></span> {tools_count} Tools Loaded</div>
<div class="status"><span class="dot"></span> Socket: {SOCKET_HOST}:{SOCKET_PORT}</div>
<div class="status"><span class="dot"></span> <a href="/sse">SSE Stream</a></div>
</div></body></html>"""
                await send({ "type": "http.response.start", "status": 200, "headers": [[b"content-type", b"text/html"]] })
                await send({ "type": "http.response.body", "body": html.encode() })
            elif scope["type"] == "http" and scope["path"] == "/health":
                body = json.dumps({"status":"ok", "socket":f"{SOCKET_HOST}:{SOCKET_PORT}", "tools": tools_count})
                await send({ "type": "http.response.start", "status": 200, "headers": [[b"content-type", b"application/json"]] })
                await send({ "type": "http.response.body", "body": body.encode() })
            else:
                await sse_app(scope, receive, send)

        uvicorn.run(app, host="127.0.0.1", port=9879, log_level="warning")
    except Exception as e:
        logger.warning(f"Server error: {e}")

if __name__ == "__main__":
    main()
