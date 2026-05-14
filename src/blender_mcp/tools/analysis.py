"""
blender-mcp — Analysis MCP tools
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


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

    @mcp.tool(**RO())
    def get_blendfile_summary_datablocks() -> str:
        """Get a count summary of ALL data-block types in the blend file (meshes, materials, scenes, etc.)."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_datablocks")
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_missing_files() -> str:
        """Report all missing external file references (textures, images, sounds, etc.) in the blend file."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_missing_files")
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_of_linked_libraries() -> str:
        """Get the tree of direct and indirect linked libraries in the blend file."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_of_linked_libraries")
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_path_info() -> str:
        """Get blend file path, save status, age, file size, and backup versions."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_path_info")
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_usage_guess() -> str:
        """Score likelihood (0-100) of each use-case for the current blend file (Animation, Modeling, Rendering, etc.)."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_usage_guess")
        return json.dumps(r, indent=2)
