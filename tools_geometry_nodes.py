"""
blender-mcp — Geometry Nodes MCP tools
"""
import json
from blender_connection import get_blender


def register_tools(mcp):
    @mcp.tool()
    def add_geometry_nodes_modifier(object_name: str = "") -> str:
        """Add a Geometry Nodes modifier to an object with a new node group."""
        b = get_blender()
        r = b.send_command("add_geometry_nodes_modifier", {"object_name": object_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def add_gn_node(object_name: str = "", node_type: str = "GeometryNodeDistributePointsOnFaces", location_x: float = 0, location_y: float = 0) -> str:
        """Add a node to a Geometry Nodes group. Types: GeometryNodeDistributePointsOnFaces, GeometryNodeInstanceOnPoints, etc."""
        b = get_blender()
        r = b.send_command("add_gn_node", {"object_name": object_name, "node_type": node_type, "location": (location_x, location_y)})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def connect_gn_nodes(object_name: str = "", from_node: str = "", to_node: str = "", from_socket: str = "", to_socket: str = "") -> str:
        """Connect two Geometry Nodes nodes."""
        b = get_blender()
        r = b.send_command("connect_gn_nodes", {"object_name": object_name, "from_node": from_node, "from_socket": from_socket, "to_node": to_node, "to_socket": to_socket})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def setup_gn_scatter(object_name: str = "", density: float = 10.0, seed: int = 0) -> str:
        """Quick scatter setup: distribute points + instance on points."""
        b = get_blender()
        r = b.send_command("setup_scatter", {"object_name": object_name, "scatter_density": density, "seed": seed})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def list_gn_modifiers(object_name: str = "") -> str:
        """List Geometry Nodes modifiers and their node trees."""
        b = get_blender()
        r = b.send_command("list_gn_modifiers", {"object_name": object_name})
        return json.dumps(r, indent=2)
