"""
blender-mcp — Viewport MCP tools
"""
import json
from ...blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool(**RW())
    def render_viewport_to_path(filepath: str) -> str:
        """Render the current frame to a file and return confirmation."""
        b = get_blender()
        r = b.send_command("render_viewport_to_path", {"filepath": filepath})
        return json.dumps(r, indent=2)

    @mcp.tool(**ADD())
    def render_thumbnail_to_path(output_path: str) -> str:
        """Render a low-quality thumbnail (320px max) for fast preview."""
        b = get_blender()
        r = b.send_command("render_thumbnail_to_path", {"output_path": output_path})
        return json.dumps(r, indent=2)

    @mcp.tool(**ADD())
    def jump_to_view3d_object_by_name(name: str) -> str:
        """Focus the 3D viewport on a specific object (select, make active, frame)."""
        b = get_blender()
        r = b.send_command("jump_to_view3d_object_by_name", {"name": name})
        return json.dumps(r, indent=2)

    @mcp.tool(**ADD())
    def jump_to_tab_by_name(name: str) -> str:
        """Switch to a workspace tab by name (e.g. 'Modeling', 'Shading', 'Layout')."""
        b = get_blender()
        r = b.send_command("jump_to_tab_by_name", {"name": name})
        return json.dumps(r, indent=2)

    @mcp.tool(**ADD())
    def jump_to_tab_by_space_type(space_type: str, allow_edits: bool = False) -> str:
        """Switch to a workspace whose largest area matches the given space type. Optionally create if not found."""
        b = get_blender()
        r = b.send_command("jump_to_tab_by_space_type", {"space_type": space_type, "allow_edits": allow_edits})
        return json.dumps(r, indent=2)
