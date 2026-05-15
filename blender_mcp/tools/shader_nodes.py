"""
blender-mcp — Shader Nodes MCP tools
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def add_shader_node(material_name: str, node_type: str = "bsdf_principled", location_x: float = 0, location_y: float = 0) -> str:
        """Add a shader node to a material. Node types: bsdf_principled, bsdf_diffuse, emission, mix_shader, rgb, tex_image, tex_noise, etc."""
        b = get_blender()
        r = b.send_command("add_shader_node", {"material_name": material_name, "node_type": node_type, "location": (location_x, location_y)})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def connect_shader_nodes(material_name: str, from_node: str, to_node: str, from_socket: str = "", to_socket: str = "") -> str:
        """Connect two shader nodes in a material."""
        b = get_blender()
        r = b.send_command("connect_nodes", {"material_name": material_name, "from_node": from_node, "from_socket": from_socket, "to_node": to_node, "to_socket": to_socket})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def set_shader_node_value(material_name: str, node_name: str, input_name: str, value: float) -> str:
        """Set a shader node input value (e.g., roughness, metallic)."""
        b = get_blender()
        r = b.send_command("set_node_value", {"material_name": material_name, "node_name": node_name, "input_name": input_name, "value": value})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def list_shader_nodes(material_name: str) -> str:
        """List all nodes in a material's node tree."""
        b = get_blender()
        r = b.send_command("list_shader_nodes", {"material_name": material_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def remove_shader_node(material_name: str, node_name: str) -> str:
        """Remove a shader node from a material."""
        b = get_blender()
        r = b.send_command("remove_shader_node", {"material_name": material_name, "node_name": node_name})
        return json.dumps(r, indent=2)
