"""
blender-mcp-ultra — MCP Server (capa src/, 118+ tools)
FastMCP-based server exposing the full ToolRegistry as real MCP tools.

Los handlers se ejecutan in-process: requieren bpy (Blender) o degradan a
{'error': 'Blender not available'}. Para control remoto vía socket usar el
servidor minimalista de la raíz (mcp_server.py).
"""

import inspect
import json
import logging
import sys
from pathlib import Path
from typing import Any

from ...core.entities import Tool
from ...tools import ToolRegistry
from ...tools.animation import HANDLERS as animation_handlers
from ...tools.animation import TOOLS as animation_tools
from ...tools.batch import HANDLERS as batch_handlers
from ...tools.batch import TOOLS as batch_tools
from ...tools.camera import HANDLERS as camera_handlers
from ...tools.camera import TOOLS as camera_tools
from ...tools.geometry_nodes import HANDLERS as geonodes_handlers
from ...tools.geometry_nodes import TOOLS as geonodes_tools
from ...tools.io import HANDLERS as io_handlers
from ...tools.io import TOOLS as io_tools
from ...tools.lights import HANDLERS as light_handlers
from ...tools.lights import TOOLS as light_tools
from ...tools.materials import HANDLERS as material_handlers
from ...tools.materials import TOOLS as material_tools
from ...tools.modifiers import HANDLERS as modifier_handlers
from ...tools.modifiers import TOOLS as modifier_tools
from ...tools.objects import HANDLERS as object_handlers
from ...tools.objects import TOOLS as object_tools
from ...tools.printing import HANDLERS as printing_handlers
from ...tools.printing import TOOLS as printing_tools
from ...tools.render import HANDLERS as render_handlers
from ...tools.render import TOOLS as render_tools
from ...tools.rigging import HANDLERS as rigging_handlers
from ...tools.rigging import TOOLS as rigging_tools
from ...tools.scene import HANDLERS as scene_handlers
from ...tools.scene import TOOLS as scene_tools
from ...tools.scene_utils import HANDLERS as utils_handlers
from ...tools.scene_utils import TOOLS as utils_tools
from ...tools.shader_nodes import HANDLERS as shader_handlers
from ...tools.shader_nodes import TOOLS as shader_tools
from ...tools.uv_texture import HANDLERS as uv_handlers
from ...tools.uv_texture import TOOLS as uv_tools

logger = logging.getLogger("blender-mcp-ultra")

_PY_TYPES = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "any": Any,
}


def register_all_tools(registry: ToolRegistry):
    """Register all tools in the registry."""
    all_tools = [
        (scene_tools, scene_handlers),
        (object_tools, object_handlers),
        (material_tools, material_handlers),
        (light_tools, light_handlers),
        (modifier_tools, modifier_handlers),
        (animation_tools, animation_handlers),
        (camera_tools, camera_handlers),
        (render_tools, render_handlers),
        (io_tools, io_handlers),
        (uv_tools, uv_handlers),
        (rigging_tools, rigging_handlers),
        (batch_tools, batch_handlers),
        (utils_tools, utils_handlers),
        (printing_tools, printing_handlers),
        (shader_tools, shader_handlers),
        (geonodes_tools, geonodes_handlers),
    ]

    total = 0
    for tools, handlers in all_tools:
        for tool in tools:
            if tool.name in handlers:
                registry.register_tool(tool, handlers[tool.name])
                total += 1

    logger.info(f"Registered {total} tools")
    return total


def _build_signature(tool: Tool) -> inspect.Signature:
    """Construye una Signature real a partir de tool.parameters (para el schema MCP)."""
    params = []
    for name, info in tool.parameters.items():
        py_type = _PY_TYPES.get(str(info.get("type", "str")).lower(), str)
        if info.get("required", False):
            params.append(
                inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=py_type)
            )
        else:
            params.append(
                inspect.Parameter(
                    name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=py_type,
                    default=info.get("default"),
                )
            )
    return inspect.Signature(params)


def _register_mcp_tool(mcp, registry: ToolRegistry, tool: Tool):
    """Registra un tool real: closure que ejecuta registry.execute_tool."""

    def handler(**kwargs):
        result = registry.execute_tool(tool.name, kwargs)
        return json.dumps(result.to_dict())

    handler.__name__ = tool.name.replace(".", "_")
    handler.__doc__ = tool.description or tool.name
    handler.__signature__ = _build_signature(tool)

    mcp.tool(name=handler.__name__, description=tool.description or tool.name)(handler)


def create_mcp_server():
    """Create FastMCP server with all tools."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        logger.warning("MCP library not available, using simple server")
        return None

    mcp = FastMCP("blender-mcp-ultra", log_level="INFO")
    registry = ToolRegistry()
    register_all_tools(registry)

    for tool in registry.list_tools():
        _register_mcp_tool(mcp, registry, tool)

    return mcp


def main():
    """Entry-point unificado `blender-mcp-server`.

    - Con bpy (dentro de Blender): 118 tools in-process por stdio.
    - Sin bpy (cliente remoto): delega en mcp_server.py (modo socket, 6 tools).
    """
    logging.basicConfig(level=logging.INFO)

    try:
        import bpy  # noqa: F401

        has_bpy = True
    except ImportError:
        has_bpy = False

    if has_bpy:
        logger.info("bpy disponible: modo in-Blender (118 tools, stdio)")
        server = create_mcp_server()
        if server:
            server.run()
        else:
            logger.error("Failed to create MCP server")
        return

    # Modo socket: reutilizar el servidor canónico de la raíz del repo
    root_server = Path(__file__).resolve().parents[3] / "mcp_server.py"
    if root_server.exists():
        logger.info("sin bpy: modo socket vía %s", root_server)
        import runpy

        sys.argv = [str(root_server)] + [a for a in sys.argv[1:]]
        runpy.run_path(str(root_server), run_name="__main__")
    else:
        logger.error(
            "bpy no disponible y mcp_server.py no encontrado en %s. "
            "Instala el paquete en el repo o usa: python mcp_server.py",
            root_server,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
