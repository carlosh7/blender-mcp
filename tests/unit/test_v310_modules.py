"""Tests offline (sin bpy) para los módulos v3.1.0."""

import importlib
import json
from pathlib import Path

import pytest

bpy = pytest.importorskip("bpy", reason="requiere bpy") if False else None

# ─── tools_search (puro, sin bpy) ───


def test_tools_search_importa_sin_bpy():
    from mcp_ultra.tools import context_search

    importlib.reload(context_search)
    assert hasattr(context_search, "tools_search")


def test_tools_search_por_query():
    from mcp_ultra.tools.context_search import tools_search

    r = tools_search(query="bevel")
    assert "resultados" in r
    assert any("bevel" in x["name"].lower() for x in r["resultados"])


def test_tools_search_por_categoria():
    from mcp_ultra.tools.context_search import tools_search

    r = tools_search(category="render", limit=30)
    assert r["total"] > 0
    assert all(x["category"] == "render" for x in r["resultados"])


def test_tools_search_sin_resultados():
    from mcp_ultra.tools.context_search import tools_search

    r = tools_search(query="zzzznada")
    assert r["total"] == 0


def test_tools_index_completo():
    idx = Path(__file__).parents[2] / "mcp_ultra/tools/context_search/data/tools_index.json"
    data = json.loads(idx.read_text())
    assert len(data) >= 230
    nombres = {e["name"] for e in data}
    assert "tools.search" in nombres
    assert "spatial.place" in nombres
    assert "inspect.view" in nombres
    assert "object.place_bottom" in nombres


# ─── spatial_dimensions (puro, sin bpy) ───


def test_dimensions_db():
    from mcp_ultra.tools.spatial_intel import REAL_DIMENSIONS

    assert len(REAL_DIMENSIONS) >= 55
    for k, (w, d, h) in REAL_DIMENSIONS.items():
        assert 0 < w < 10 and 0 < d < 10 and 0 < h < 10, k


def test_dimensions_search():
    from mcp_ultra.tools.spatial_intel import spatial_dimensions

    r = spatial_dimensions(search="mesa")
    assert r["total"] >= 3


# ─── imports sin bpy de todos los módulos nuevos ───


@pytest.mark.parametrize(
    "mod",
    [
        "mcp_ultra.tools.agent_experience",
        "mcp_ultra.tools.spatial_intel",
        "mcp_ultra.tools.inspect",
        "mcp_ultra.tools.scene_explain",
        "mcp_ultra.tools.presets",
    ],
)
def test_modulos_importan_sin_bpy(mod):
    import sys

    # simular ausencia de bpy
    saved = {k: sys.modules.pop(k, None) for k in ("bpy", "mathutils")}
    sys.modules["bpy"] = None  # forzar ImportError en `import bpy`
    sys.modules["mathutils"] = None
    try:
        m = importlib.import_module(mod)
        assert hasattr(m, "TOOLS") and hasattr(m, "HANDLERS")
        assert len(m.TOOLS) > 0
        assert set(m.HANDLERS) == {t.name for t in m.TOOLS}
    finally:
        for k, v in saved.items():
            if v is not None:
                sys.modules[k] = v
            else:
                sys.modules.pop(k, None)
