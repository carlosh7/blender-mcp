"""
blender-mcp — AKB (Axiom Knowledge Base) MCP tools
"""
import json
import os
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)

_AKB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "addon", "data", "akb")

def _akb_available():
    return os.path.exists(os.path.join(_AKB_DIR, "_index.json"))

def register_tools(mcp):
    @mcp.tool(**RO())
    def get_object_specs(query: str) -> str:
        """Search the Axiom Knowledge Base for real-world object specifications (dimensions, weight, anchors).
        Consulta la base de conocimiento para obtener dimensiones reales de objetos.
        Categorías disponibles: av (truss, LED, moving heads), furniture, vehicles, structural.
        Siempre consulta ANTES de crear un objeto para usar dimensiones reales."""
        if _akb_available():
            from addon.akb import get_specs
            results = get_specs(query)
            return json.dumps({"query": query, "total": len(results), "results": results}, indent=2)
        b = get_blender()
        r = b.send_command("get_specs", {"query": query})
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def akb_list_categories() -> str:
        """List all available categories in the Axiom Knowledge Base with object counts."""
        if _akb_available():
            from addon.akb import list_categories
            r = list_categories()
            return json.dumps({"categories": r}, indent=2)
        b = get_blender()
        r = b.send_command("list_categories")
        return json.dumps(r, indent=2)
