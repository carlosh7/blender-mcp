"""
blender-mcp — Expert Knowledge & Standards
Provee al agente dimensiones estándar y reglas funcionales.
Ahora lee del AKB (Axiom Knowledge Base) en vez de datos hardcodeados.
"""
import json
import os
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)

_AKB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "addon", "data", "akb")


def _get_specs(query):
    """Busca en AKB por nombre."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        from addon.akb import get_specs
        return get_specs(query)
    except:
        return []


def register_tools(mcp):
    @mcp.tool(**RO())
    def get_standard_dimensions(category: str) -> str:
        """Returns real-world standard dimensions and functional rules for a given category.
        Consulta la base de conocimiento AKB para obtener dimensiones reales de objetos.
        Categorías disponibles: truss, led, moving head, line array, table, chair, door, etc.
        """
        results = _get_specs(category)
        if not results:
            return json.dumps({
                "error": f"Category '{category}' not found",
                "available": ["truss", "led", "moving head", "line array", "table", "chair", "door", "human"]
            })
        return json.dumps(results, indent=2)

    @mcp.tool(**RO())
    def validate_human_scale(object_type: str, dimensions: list) -> str:
        """Validates if the provided dimensions for an object type are within reasonable human-scale bounds."""
        results = _get_specs(object_type)
        if not results:
            return "No standard found for this object."
        
        bp = results[0]
        std = bp.get("geometry", {}).get("dimensions", [1, 1, 1])
        warnings = []
        for i, axis in enumerate(["X", "Y", "Z"]):
            if dimensions[i] > std[i] * 1.5:
                warnings.append(f"{axis}: {dimensions[i]}m exceeds standard {std[i]}m")
            elif dimensions[i] < std[i] * 0.3:
                warnings.append(f"{axis}: {dimensions[i]}m is too small (standard {std[i]}m)")
        
        return json.dumps({
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "std_dimensions": std
        })
