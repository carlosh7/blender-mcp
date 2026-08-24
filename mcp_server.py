#!/usr/bin/env python3
"""
blender-mcp — Simplified MCP Server
Exposes 6 core tools for controlling Blender via MCP protocol.
Compatible with opencode, Claude Desktop, Cursor, etc.

Transport: stdio por defecto (clientes MCP locales); `--sse` para HTTP en :9879.
"""

import json
import logging
import sys
from pathlib import Path

from blender_connection import get_blender
from blender_mcp.platform import get_log_dir

_log_dir = get_log_dir()
_log_file = str(_log_dir / "server.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr), logging.FileHandler(_log_file)],
)
logger = logging.getLogger("blender-mcp")

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP("blender-mcp", log_level="INFO")


def _load_code_guard():
    """Carga addon/code_guard.py (solo stdlib) por ruta; None si no existe."""
    import importlib.util

    guard_path = Path(__file__).resolve().parent / "addon" / "code_guard.py"
    if not guard_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("bmcp_code_guard", guard_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_code_guard = _load_code_guard()


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
    if _code_guard is not None:
        try:
            _code_guard.check_code(code)
        except _code_guard.CodeGuardError as e:
            return f"⛔ Bloqueado por seguridad: {e}"
    b = get_blender()
    result = b.send_command("execute_code", {"code": code})
    out = f"Salida:\n{result.get('output', '')}"
    if "result" in result:
        out += f"\nResultado: {result['result']}"
    return out


@mcp.tool(**RO())
def get_viewport_screenshot() -> str:
    """Captura una imagen del viewport 3D de Blender."""
    b = get_blender()
    result = b.send_command("get_viewport_screenshot")
    if "error" in result:
        return f"Error: {result['error']}"
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
    Formatos de ancla: FRONT_BOTTOM_LEFT, FRONT_BOTTOM_RIGHT, ..., TOP_CENTER,
    BOTTOM_CENTER, CENTROID (ver addon/anchor_system.py:ANCHOR_NAMES)."""
    b = get_blender()
    r = b.send_command(
        "snap_and_parent",
        {
            "obj_move": obj_move,
            "obj_target": obj_target,
            "anchor_move": anchor_move,
            "anchor_target": anchor_target,
        },
    )
    return json.dumps(r, indent=2)


@mcp.resource("blender://scene/info")
def resource_scene_info() -> str:
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)


def main():
    logger.info("Starting MCP Server (6 tools)...")

    try:
        if "--sse" in sys.argv:
            import uvicorn

            app = mcp.sse_app()

            logger.info("Uvicorn starting on :9879")
            uvicorn.run(app, host="127.0.0.1", port=9879, log_level="info")
        else:
            logger.info("Transport: stdio")
            mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"MCP SERVER ERROR: {e}", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
