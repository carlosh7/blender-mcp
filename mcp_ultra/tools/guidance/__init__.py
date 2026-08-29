"""
blender-mcp-ultra — Guidance (guías de workflow para agentes)
Sirve las guías de técnica y workflow del producto como tools MCP: el agente
las descubre y pide bajo demanda (coste de contexto ~0 hasta entonces), en
vez de requerir que el usuario instale archivos de skills aparte.

Mismo patrón que rst_search: contenido empaquetado en el wheel, servido
por el MCP.
"""

from __future__ import annotations

from pathlib import Path

from ...core.entities import Tool, ToolCategory, ToolPermission

_DATA_DIR = Path(__file__).parent / "guides"


def _available_topics() -> list[tuple[str, str, str]]:
    """(topic, título, resumen = primera línea descriptiva)."""
    out = []
    for md in sorted(_DATA_DIR.glob("*.md")):
        lines = [ln.strip() for ln in md.read_text(encoding="utf-8").splitlines() if ln.strip()]
        title = lines[0].lstrip("# ").strip() if lines else md.stem
        summary = next((ln for ln in lines[1:] if not ln.startswith("#")), "")
        out.append((md.stem, title, summary))
    return out


def _normalize_topic(topic: str) -> str:
    return topic.strip().lower().replace("_", "-").replace(" ", "-")


def list_guidance() -> dict:
    """Lista de guías disponibles con su resumen."""
    topics = _available_topics()
    return {
        "topics": [
            {"topic": t, "title": title, "summary": summary} for t, title, summary in topics
        ],
        "count": len(topics),
        "hint": "Usa guidance.get(topic) para leer la guía completa antes de empezar un workflow complejo.",
    }


def get_guidance(topic: str = "") -> dict:
    """Devuelve la guía completa de un tema (acepta 'scene-setup', 'scene_setup', 'Scene Setup')."""
    wanted = _normalize_topic(topic)
    if not wanted:
        available = [t for t, _, _ in _available_topics()]
        return {"error": "topic requerido", "available": available}
    md = _DATA_DIR / f"{wanted}.md"
    if not md.exists():
        available = [t for t, _, _ in _available_topics()]
        return {
            "error": f"guía no encontrada: {topic}",
            "available": available,
            "hint": "Usa guidance.list para ver los temas disponibles.",
        }
    content = md.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    title = lines[0].lstrip("# ").strip() if lines else wanted
    return {"topic": wanted, "title": title, "content": content, "chars": len(content)}


def _all_topics_str() -> str:
    return ", ".join(t for t, _, _ in _available_topics())


TOOLS = [
    Tool(
        name="guidance.list",
        category=ToolCategory.GUIDANCE,
        description="Lista las guías de workflow y técnica disponibles (animación, iluminación, "
        "render, pipeline de producción...). Léelas antes de empezar workflows complejos.",
        permission=ToolPermission.READ_ONLY,
        parameters={},
        examples=["guidance.list()"],
    ),
    Tool(
        name="guidance.get",
        category=ToolCategory.GUIDANCE,
        description="Devuelve la guía completa de un tema. Temas: " + _all_topics_str(),
        permission=ToolPermission.READ_ONLY,
        parameters={
            "topic": {
                "type": "str",
                "required": True,
                "description": "ej: 'lighting', 'scene-setup'",
            },
        },
        examples=["guidance.get(topic='lighting')", "guidance.get(topic='scene-setup')"],
    ),
]

HANDLERS = {
    "guidance.list": list_guidance,
    "guidance.get": get_guidance,
}
