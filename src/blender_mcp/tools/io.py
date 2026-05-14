"""
blender-mcp — Import/Export MCP tools
"""
import json
from blender_connection import get_blender


def register_tools(mcp):
    @mcp.tool()
    def export_scene(filepath: str, format: str = "glb") -> str:
        """Export the current scene to a 3D file. Formats: glb, gltf, fbx, obj, stl, ply, usd, dae, abc, x3d."""
        b = get_blender()
        r = b.send_command("export_scene", {"filepath": filepath, "format": format})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def export_selected(filepath: str, format: str = "glb") -> str:
        """Export selected objects to a 3D file."""
        b = get_blender()
        r = b.send_command("export_selected", {"filepath": filepath, "format": format})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def import_model(filepath: str, format: str = "") -> str:
        """Import a 3D model file. Auto-detects format from extension if not specified.
        Supports: glb, gltf, fbx, obj, stl, ply, usd, dae, svg, x3d."""
        b = get_blender()
        r = b.send_command("import_model", {"filepath": filepath, "format": format})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def list_export_formats() -> str:
        """List all supported export formats."""
        b = get_blender()
        r = b.send_command("list_export_formats")
        return json.dumps(r, indent=2)
