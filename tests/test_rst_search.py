"""
blender-mcp — RST Documentation Search Tests
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_DATA_API = Path(__file__).resolve().parents[1] / "data" / "api"
_requires_docs = pytest.mark.skipif(
    not _DATA_API.exists(), reason="data/api no presente (ejecuta scripts/fetch_docs_data.py)"
)


class TestRSTSearch:
    @_requires_docs
    def test_search_api_docs_found(self):
        from blender_mcp.rst_search import search_api_docs

        r = search_api_docs("primitive_cube_add")
        assert r["total"] >= 1
        assert any("cube" in f["snippet"].lower() for f in r["results"])

    @_requires_docs
    def test_search_api_docs_not_found(self):
        from blender_mcp.rst_search import search_api_docs

        r = search_api_docs("zzzzzzzzz99")
        assert r["total"] == 0

    @_requires_docs
    def test_search_manual_docs(self):
        from blender_mcp.rst_search import search_manual_docs

        r = search_manual_docs("modifier")
        assert r["total"] >= 1

    @_requires_docs
    def test_get_python_api_docs(self):
        from blender_mcp.rst_search import get_python_api_docs

        r = get_python_api_docs("bpy.ops.mesh")
        assert "content" in r
        assert len(r["content"]) > 100

    @_requires_docs
    def test_snippet_extraction(self):
        from blender_mcp.rst_search import _extract_snippet

        text = "Blender is a 3D creation suite" * 10
        snippet = _extract_snippet(text, "3D")
        assert "3D" in snippet
        assert len(snippet) <= 125
