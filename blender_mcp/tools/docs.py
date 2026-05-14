"""
blender-mcp — Blender API Docs MCP tools
"""
import json
import os
from ...blender_connection import get_blender
from mcp.types import ToolAnnotations

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool(**RO())
    def search_api_docs(query: str = "") -> str:
        """Search Blender's Python API documentation (bundled RST files) for a query."""
        if os.path.exists(os.path.join(_DATA_DIR, "api")):
            from blender_mcp.rst_search import search_api_docs as _search
            r = _search(query)
        else:
            b = get_blender()
            r = b.send_command("search_api_docs", {"query": query})
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def search_manual_docs(query: str = "") -> str:
        """Search Blender's user manual (bundled RST files) for a query."""
        if os.path.exists(os.path.join(_DATA_DIR, "manual")):
            from blender_mcp.rst_search import search_manual_docs as _search
            r = _search(query)
        else:
            b = get_blender()
            r = b.send_command("search_manual_docs", {"query": query})
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_python_api_docs(topic: str) -> str:
        """Get detailed documentation for a Blender Python API topic from bundled RST docs. Examples: 'bpy.types.Object', 'bpy.ops.mesh.primitive_cube_add'."""
        if os.path.exists(os.path.join(_DATA_DIR, "api")):
            from blender_mcp.rst_search import get_python_api_docs as _get
            r = _get(topic)
        else:
            b = get_blender()
            r = b.send_command("get_python_api_docs", {"topic": topic})
        return json.dumps(r, indent=2)
