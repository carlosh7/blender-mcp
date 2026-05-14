"""
blender-mcp — MCP Server Unit Tests
Tests the MCP server tool registration and configuration.
Does NOT require Blender.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestServerImports:
    """Test that all modules import correctly without Blender."""

    def test_blender_connection_import(self):
        """blender_connection should import without Blender."""
        from blender_connection import BlenderConnection, get_blender
        assert BlenderConnection is not None

    def test_tool_cache_import(self):
        """tool_cache should import without Blender."""
        from blender_mcp.tool_cache import get, set, invalidate
        # Test basic cache operations
        set("test_key", {"data": 123})
        cached = get("test_key")
        assert cached == {"data": 123}
        invalidate("test_key")
        assert get("test_key") is None

    def test_config_import(self):
        """config should import without Blender."""
        import config
        assert hasattr(config, "find_blender")
        assert hasattr(config, "get_system_info")

    def test_spatial_import(self):
        """spatial module should import."""
        from blender_mcp.spatial import generate_ascii_view, get_spatial_summary
        assert generate_ascii_view is not None


class TestToolRegistration:
    """Test that MCP tool modules register correctly."""

    def _make_test_mcp(self):
        from mcp.server.fastmcp import FastMCP
        return FastMCP("test")

    def _import_tools(self, sys_path):
        """Helper: add src to path and import from blender_mcp.tools"""
        import importlib
        sys.path.insert(0, sys_path)
        mod_names = [
            "blender_mcp.tools.polyhaven", "blender_mcp.tools.sketchfab",
            "blender_mcp.tools.hyper3d", "blender_mcp.tools.hunyuan",
            "blender_mcp.tools.ambientcg", "blender_mcp.tools.shader_nodes",
            "blender_mcp.tools.animation", "blender_mcp.tools.geometry_nodes",
            "blender_mcp.tools.render", "blender_mcp.tools.io",
            "blender_mcp.tools.uv_texture", "blender_mcp.tools.batch",
            "blender_mcp.tools.rigging", "blender_mcp.tools.scene_utils",
            "blender_mcp.tools.printing",
        ]
        return [importlib.import_module(m) for m in mod_names]

    def test_core_tools_register(self):
        """Core tools from mcp_server should register."""
        mcp = self._make_test_mcp()
        import mcp_server
        tools = list(mcp_server.mcp._tool_manager.list_tools())
        assert len(tools) > 10

    def test_polyhaven_tools_register(self):
        """Poly Haven tools should register."""
        mcp = self._make_test_mcp()
        from blender_mcp.tools import polyhaven
        polyhaven.register_tools(mcp)
        names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "search_polyhaven" in names

    def test_sketchfab_tools_register(self):
        """Sketchfab tools should register."""
        mcp = self._make_test_mcp()
        from blender_mcp.tools import sketchfab
        sketchfab.register_tools(mcp)
        names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "search_sketchfab" in names

    def test_hyper3d_tools_register(self):
        """Hyper3D tools should register."""
        mcp = self._make_test_mcp()
        from blender_mcp.tools import hyper3d
        hyper3d.register_tools(mcp)
        names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "generate_hyper3d_text" in names

    def test_hunyuan_tools_register(self):
        """Hunyuan3D tools should register."""
        mcp = self._make_test_mcp()
        from blender_mcp.tools import hunyuan
        hunyuan.register_tools(mcp)
        names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "generate_hunyuan3d" in names

    def test_ambientcg_tools_register(self):
        """AmbientCG tools should register."""
        mcp = self._make_test_mcp()
        from blender_mcp.tools import ambientcg
        ambientcg.register_tools(mcp)
        names = [t.name for t in mcp._tool_manager.list_tools()]
        assert "search_ambientcg" in names

    def test_all_tools_register(self):
        """All tool modules should register without conflicts."""
        mcp = self._make_test_mcp()
        modules = self._import_tools(os.path.join(os.path.dirname(__file__), "..", "src"))
        for mod in modules:
            mod.register_tools(mcp)
        tools = list(mcp._tool_manager.list_tools())
        assert len(tools) >= 60, f"Should register 60+ tools, got {len(tools)}"


class TestTelemetry:
    """Test telemetry module."""

    def test_telemetry_import(self):
        """Telemetry module should import."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from blender_mcp.telemetry import record, record_tool, record_startup
        assert record is not None
        assert record_tool is not None

    def test_telemetry_decorator_import(self):
        """Telemetry decorator should import."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from blender_mcp.telemetry_decorator import telemetry_tool
        assert telemetry_tool is not None


class TestDoctor:
    """Test doctor/health check module."""

    def test_doctor_import(self):
        """Doctor module should import."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
        from blender_mcp.doctor import run_doctor
        assert run_doctor is not None
