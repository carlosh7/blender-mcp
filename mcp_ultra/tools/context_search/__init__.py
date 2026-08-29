"""
blender-mcp-ultra — Context Economy
tools_search: búsqueda sobre el registry para que los agentes encuentren la
tool correcta sin cargar 223 definiciones en contexto.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from ...core.entities import Tool, ToolCategory, ToolPermission


def _load_registry_entries() -> list[dict[str, Any]]:
    """Lee el índice de tools desde el JSON del paquete (sin tocar bpy)."""
    import os
    from pathlib import Path

    idx = Path(__file__).parent / "index" / "tools_index.json"
    if idx.exists():
        try:
            return json.loads(idx.read_text())
        except Exception:
            pass
    return []


def tools_search(
    query: str = "", category: str = "", permission: str = "", limit: int = 15, **_kw
) -> dict:
    """Busca tools del registry por texto (nombre+descripción), categoría o permiso.

    Devuelve name, category, description y parameters requeridos. Úsalo en vez
    de recorrer list_tools completo: ahorra mucho contexto.
    """
    entries = _load_registry_entries()
    if not entries:
        return {
            "error": "índice de tools no disponible en este entorno",
            "hint": "disponible via list_tools",
        }
    q = (query or "").lower().strip()
    terms = [t for t in q.replace(".", " ").replace("_", " ").split() if len(t) > 2]
    scored = []
    for e in entries:
        if category and e.get("category", "").lower() != category.lower():
            continue
        if permission and e.get("permission", "").lower() != permission.lower():
            continue
        name = e.get("name", "").lower()
        desc = (e.get("description") or "").lower()
        score = 0
        if q and q in name:
            score += 10
        if q and q in desc:
            score += 5
        for t in terms:
            if t in name:
                score += 4
            if t in desc:
                score += 2
        if q and score == 0:
            continue
        required = {
            k: v.get("description", "")
            for k, v in (e.get("parameters") or {}).items()
            if v.get("required")
        }
        scored.append(
            (
                score,
                {
                    "name": e.get("name"),
                    "category": e.get("category"),
                    "description": e.get("description"),
                    "required_params": required,
                },
            )
        )
    scored.sort(key=lambda x: -x[0])
    results = [s[1] for s in scored[: max(1, min(limit, 50))]]
    return {"resultados": results, "total": len(results), "query": query or "(todas)"}


TOOLS = [
    Tool(
        name="tools.search",
        category=ToolCategory.SCENE_UTILS,
        description="Busca tools del registry por texto/categoría sin cargar las 223 definiciones. Ahorra contexto: úsalo antes de adivinar nombres",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "query": {
                "type": "str",
                "default": "",
                "description": "texto libre (p.ej. 'bevel', 'render cycles', 'colocar')",
            },
            "category": {
                "type": "str",
                "default": "",
                "description": "filtra por categoría (objects, materials, render...)",
            },
            "limit": {"type": "int", "default": 15},
        },
        examples=["tools.search(query='bevel')", "tools.search(category='render')"],
    ),
]

HANDLERS = {
    "tools.search": tools_search,
}
