"""
blender-mcp — UV & Texture MCP tools
"""
import json
from blender_connection import get_blender


def register_tools(mcp):
    @mcp.tool()
    def unwrap_object(object_name: str = "", method: str = "smart") -> str:
        """UV unwrap a mesh object. Methods: smart, unwrap, conformal, cube, cylinder, sphere, project."""
        b = get_blender()
        r = b.send_command("unwrap_object", {"object_name": object_name, "method": method})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def add_uv_map(object_name: str = "", name: str = "") -> str:
        """Add a new UV map to a mesh object."""
        b = get_blender()
        r = b.send_command("add_uv_map", {"object_name": object_name, "name": name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def bake_textures(object_name: str = "", bake_type: str = "DIFFUSE", resolution: int = 1024) -> str:
        """Bake textures onto a mesh. Types: DIFFUSE, NORMAL, COMBINED, AO, ROUGHNESS, EMIT."""
        b = get_blender()
        r = b.send_command("bake_textures", {"object_name": object_name, "bake_type": bake_type, "resolution": resolution})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def list_uv_maps(object_name: str = "") -> str:
        """List UV maps on an object."""
        b = get_blender()
        r = b.send_command("list_uv_maps", {"object_name": object_name})
        return json.dumps(r, indent=2)
