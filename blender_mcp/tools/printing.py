"""
blender-mcp — 3D Printing MCP tools
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def check_manifold(object_name: str = "") -> str:
        """Check if a mesh is manifold (watertight) for 3D printing. Reports non-manifold edges."""
        b = get_blender()
        r = b.send_command("check_manifold", {"object_name": object_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def set_dimensions_mm(object_name: str = "", width_mm: float = 0, depth_mm: float = 0, height_mm: float = 0) -> str:
        """Set object dimensions in millimeters for 3D printing."""
        b = get_blender()
        r = b.send_command("set_dimensions_mm", {"object_name": object_name, "width_mm": width_mm, "depth_mm": depth_mm, "height_mm": height_mm})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def export_stl_mm(filepath: str, object_name: str = "") -> str:
        """Export model as STL with millimeter scale for 3D printing."""
        b = get_blender()
        r = b.send_command("export_stl_mm", {"filepath": filepath, "object_name": object_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def arrange_bed_layout(object_names: list = None, bed_width_mm: float = 200, bed_height_mm: float = 200) -> str:
        """Arrange objects on a print bed for optimal layout."""
        b = get_blender()
        r = b.send_command("bed_layout", {"object_names": object_names, "bed_size_x_mm": bed_width_mm, "bed_size_y_mm": bed_height_mm})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def add_wall_thickness(object_name: str = "", thickness_mm: float = 2.0) -> str:
        """Add wall thickness (Solidify modifier) for 3D printing prep."""
        b = get_blender()
        r = b.send_command("add_wall_thickness", {"object_name": object_name, "thickness_mm": thickness_mm})
        return json.dumps(r, indent=2)
