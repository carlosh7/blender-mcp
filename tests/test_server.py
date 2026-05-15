"""
blender-mcp — Core Import Tests
Tests that the simplified system imports correctly.
Does NOT require Blender (except for addon tests).
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCoreImports:
    def test_blender_connection_import(self):
        from blender_connection import BlenderConnection, get_blender
        assert BlenderConnection is not None

    def test_rst_search_import(self):
        from blender_mcp.rst_search import search_api_docs, get_python_api_docs
        assert callable(search_api_docs)
        assert callable(get_python_api_docs)

    def test_rst_search_works(self):
        from blender_mcp.rst_search import search_api_docs
        result = search_api_docs("cylinder")
        assert "results" in result
        assert "query" in result
