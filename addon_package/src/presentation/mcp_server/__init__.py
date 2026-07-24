"""
blender-mcp-ultra — MCP Server
FastMCP-based server for Blender control.
"""
import json
import os
import sys
import logging
from typing import Any, Dict, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.entities import Tool, ToolCategory, ToolPermission
from tools import ToolRegistry
from tools.scene import TOOLS as scene_tools, HANDLERS as scene_handlers
from tools.objects import TOOLS as object_tools, HANDLERS as object_handlers
from tools.materials import TOOLS as material_tools, HANDLERS as material_handlers
from tools.lights import TOOLS as light_tools, HANDLERS as light_handlers
from tools.modifiers import TOOLS as modifier_tools, HANDLERS as modifier_handlers
from tools.animation import TOOLS as animation_tools, HANDLERS as animation_handlers
from tools.camera import TOOLS as camera_tools, HANDLERS as camera_handlers
from tools.render import TOOLS as render_tools, HANDLERS as render_handlers
from tools.io import TOOLS as io_tools, HANDLERS as io_handlers
from tools.uv_texture import TOOLS as uv_tools, HANDLERS as uv_handlers
from tools.rigging import TOOLS as rigging_tools, HANDLERS as rigging_handlers
from tools.batch import TOOLS as batch_tools, HANDLERS as batch_handlers
from tools.scene_utils import TOOLS as utils_tools, HANDLERS as utils_handlers
from tools.printing import TOOLS as printing_tools, HANDLERS as printing_handlers
from tools.shader_nodes import TOOLS as shader_tools, HANDLERS as shader_handlers
from tools.geometry_nodes import TOOLS as geonodes_tools, HANDLERS as geonodes_handlers


logger = logging.getLogger("blender-mcp-ultra")


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
    
    # Register each tool as an MCP tool
    for tool in registry.list_tools():
        _register_mcp_tool(mcp, registry, tool)
    
    return mcp


def _register_mcp_tool(mcp, registry, tool: Tool):
    """Register a single tool in the MCP server."""
    
    # Build parameter annotations
    annotations = {}
    for param_name, param_info in tool.parameters.items():
        annotations[param_name] = {
            "type": param_info.get("type", "str"),
            "description": param_info.get("description", ""),
            "required": param_info.get("required", False),
        }
    
    # Create handler function
    def make_handler(tool_name):
        def handler(**kwargs):
            result = registry.execute_tool(tool_name, kwargs)
            return json.dumps(result.to_dict())
        handler.__name__ = tool_name.replace(".", "_")
        handler.__doc__ = tool.description
        return handler
    
    # Register with MCP
    @mcp.tool()
    def tool_handler(**kwargs):
        """Tool handler."""
        pass
    
    # Replace with proper handler
    tool_handler.__name__ = tool.name.replace(".", "_")
    tool_handler.__doc__ = tool.description
    tool_handler.__wrapped__ = make_handler(tool.name)


def main():
    """Main entry point for MCP server."""
    logging.basicConfig(level=logging.INFO)
    
    server = create_mcp_server()
    if server:
        logger.info("Starting blender-mcp-ultra MCP server")
        server.run()
    else:
        logger.error("Failed to create MCP server")


if __name__ == "__main__":
    main()
