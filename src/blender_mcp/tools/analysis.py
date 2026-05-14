"""
blender-mcp — Analysis MCP tools
"""
import json
from blender_connection import get_blender


def register_tools(mcp):
    @mcp.tool()
    def get_screenshot_as_base64(max_size: int = 800) -> str:
        """Capture a screenshot of the 3D viewport and return as base64 PNG. Use this for visual validation."""
        b = get_blender()
        r = b.send_command("get_screenshot_as_base64", {"max_size": max_size})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def get_objects_summary() -> str:
        """Get a summary table of ALL objects in the scene: name, type, location, dimensions, visibility."""
        b = get_blender()
        r = b.send_command("get_objects_summary")
        return json.dumps(r, indent=2)

    @mcp.tool()
    def get_object_detail_summary(name: str) -> str:
        """Get comprehensive detail for a single object: transforms, modifiers, materials, mesh data, children/parent."""
        b = get_blender()
        r = b.send_command("get_object_detail_summary", {"name": name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def get_blendfile_summary_datablocks() -> str:
        """Get a count summary of ALL data-block types in the blend file (meshes, materials, scenes, etc.)."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_datablocks")
        return json.dumps(r, indent=2)
