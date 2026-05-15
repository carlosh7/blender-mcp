"""
blender-mcp — Scene Utils MCP tools
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def purge_orphans() -> str:
        """Remove all unused data blocks (orphaned materials, meshes, textures, etc.)."""
        b = get_blender()
        r = b.send_command("purge_orphans")
        return json.dumps(r, indent=2)

    @mcp.tool()
    def cleanup_scene() -> str:
        """Full scene cleanup: purge orphans, remove empty collections, normalize."""
        b = get_blender()
        r = b.send_command("cleanup_scene")
        return json.dumps(r, indent=2)

    @mcp.tool()
    def mesh_analysis(object_name: str = "") -> str:
        """Analyze mesh topology: vertex/edge/polygon counts, dimensions, location."""
        b = get_blender()
        r = b.send_command("mesh_analysis", {"object_name": object_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def scene_summary() -> str:
        """Get full scene summary: object counts by type, materials, collections."""
        b = get_blender()
        r = b.send_command("scene_summary")
        return json.dumps(r, indent=2)

    @mcp.tool()
    def hide_object(object_name: str, hide: bool = True) -> str:
        """Hide or unhide an object in viewport and render."""
        b = get_blender()
        r = b.send_command("hide_object", {"object_name": object_name, "hide": hide})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def join_objects(target_name: str, source_names: list = None) -> str:
        """Join multiple objects into a single mesh object."""
        b = get_blender()
        r = b.send_command("join_objects", {"target_name": target_name, "source_names": source_names or []})
        return json.dumps(r, indent=2)
