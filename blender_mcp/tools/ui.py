"""
blender-mcp — UI Layout MCP tool
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)

def register_tools(mcp):
    @mcp.tool(**RO())
    def get_ui_layout() -> str:
        """Get the complete Blender UI layout: editor types, positions, shading, view matrices, node editor state."""
        b = get_blender()
        r = b.send_command("get_ui_layout")
        return json.dumps(r, indent=2)
