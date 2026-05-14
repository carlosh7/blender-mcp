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
        from tool_cache import get, set, invalidate
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
        import spatial
        assert hasattr(spatial, "generate_ascii_view")
        assert hasattr(spatial, "get_spatial_summary")


class TestToolRegistration:
    """Test that MCP tool modules register correctly."""

    def _make_test_mcp(self):
        from mcp.server.fastmcp import FastMCP
        return FastMCP("test")

    def test_core_tools_register(self):
        """Core tools from mcp_server should register."""
        mcp = self._make_test_mcp()
        import mcp_server
        # Use the mcp instance from the module
        tools = list(mcp_server.mcp._tool_manager.list_tools())
        assert len(tools) > 10, f"Should have at least 10 tools, got {len(tools)}"

    def test_polyhaven_tools_register(self):
        """Poly Haven tools should register."""
        mcp = self._make_test_mcp()
        import tools_polyhaven
        tools_polyhaven.register_tools(mcp)
        tools = list(mcp._tool_manager.list_tools())
        names = [t.name for t in tools]
        assert "search_polyhaven" in names
        assert "download_polyhaven_hdri" in names

    def test_sketchfab_tools_register(self):
        """Sketchfab tools should register."""
        mcp = self._make_test_mcp()
        import tools_sketchfab
        tools_sketchfab.register_tools(mcp)
        tools = list(mcp._tool_manager.list_tools())
        names = [t.name for t in tools]
        assert "search_sketchfab" in names
        assert "download_sketchfab_model" in names

    def test_hyper3d_tools_register(self):
        """Hyper3D tools should register."""
        mcp = self._make_test_mcp()
        import tools_hyper3d
        tools_hyper3d.register_tools(mcp)
        tools = list(mcp._tool_manager.list_tools())
        names = [t.name for t in tools]
        assert "generate_hyper3d_text" in names
        assert "poll_rodin_job" in names

    def test_hunyuan_tools_register(self):
        """Hunyuan3D tools should register."""
        mcp = self._make_test_mcp()
        import tools_hunyuan
        tools_hunyuan.register_tools(mcp)
        tools = list(mcp._tool_manager.list_tools())
        names = [t.name for t in tools]
        assert "generate_hunyuan3d" in names

    def test_ambientcg_tools_register(self):
        """AmbientCG tools should register."""
        mcp = self._make_test_mcp()
        import tools_ambientcg
        tools_ambientcg.register_tools(mcp)
        tools = list(mcp._tool_manager.list_tools())
        names = [t.name for t in tools]
        assert "search_ambientcg" in names

    def test_all_tools_register(self):
        """All tool modules should register without conflicts."""
        mcp = self._make_test_mcp()
        import tools_polyhaven, tools_sketchfab, tools_hyper3d, tools_hunyuan, tools_ambientcg
        import tools_shader_nodes, tools_animation, tools_geometry_nodes, tools_render
        import tools_io, tools_uv_texture, tools_batch, tools_rigging, tools_scene_utils, tools_printing
        for mod in [tools_polyhaven, tools_sketchfab, tools_hyper3d, tools_hunyuan, tools_ambientcg,
                     tools_shader_nodes, tools_animation, tools_geometry_nodes, tools_render,
                     tools_io, tools_uv_texture, tools_batch, tools_rigging, tools_scene_utils, tools_printing]:
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
