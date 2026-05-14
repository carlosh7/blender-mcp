"""
blender-mcp — Blender API Docs MCP tools
"""
import json
from blender_connection import get_blender


def register_tools(mcp):
    @mcp.tool()
    def search_api_docs(query: str = "") -> str:
        """Search Blender's Python API for types, properties, and operators matching a query. Uses built-in introspection (no external docs needed)."""
        b = get_blender()
        r = b.send_command("search_api_docs", {"query": query})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def get_python_api_docs(topic: str) -> str:
        """Get detailed documentation for a specific Blender Python API topic. Examples: 'Object.location', 'Mesh', 'ops.mesh.primitive_cube_add', 'Material'."""
        b = get_blender()
        r = b.send_command("get_python_api_docs", {"topic": topic})
        return json.dumps(r, indent=2)
