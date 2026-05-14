"""
blender-mcp — Viewport MCP tools
"""
import json
from blender_connection import get_blender


def register_tools(mcp):
    @mcp.tool()
    def render_viewport_to_path(filepath: str) -> str:
        """Render the current frame to a file and return confirmation."""
        b = get_blender()
        r = b.send_command("render_viewport_to_path", {"filepath": filepath})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def jump_to_view3d_object_by_name(name: str) -> str:
        """Focus the 3D viewport on a specific object (select, make active, frame)."""
        b = get_blender()
        r = b.send_command("jump_to_view3d_object_by_name", {"name": name})
        return json.dumps(r, indent=2)
