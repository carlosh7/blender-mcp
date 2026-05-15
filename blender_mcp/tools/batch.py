"""
blender-mcp — Batch Processing MCP tools
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def turntable_render(object_name: str = "", output_dir: str = "", frames: int = 36) -> str:
        """Render a turntable animation around an object."""
        b = get_blender()
        r = b.send_command("turntable_render", {"object_name": object_name, "output_dir": output_dir, "frames": frames})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def batch_rename(prefix: str = "", search: str = "", replace: str = "", object_type: str = "ALL") -> str:
        """Batch rename objects. Use prefix to prepend, or search+replace to substitute."""
        b = get_blender()
        r = b.send_command("batch_rename", {"prefix": prefix, "search": search, "replace": replace, "object_type": object_type})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def batch_delete_by_type(object_type: str = "MESH") -> str:
        """Delete all objects of a specific type."""
        b = get_blender()
        r = b.send_command("batch_delete_by_type", {"object_type": object_type})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def apply_transforms_all() -> str:
        """Apply location, rotation, and scale transforms on all mesh objects."""
        b = get_blender()
        r = b.send_command("apply_transforms_all")
        return json.dumps(r, indent=2)
