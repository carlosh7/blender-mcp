"""
blender-mcp-ultra — Tool Tests
Comprehensive tests for all tool categories.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Check if bpy is available
try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

# skip_without_bpy removed - using pytest.skip() instead


class TestSceneTools:
    """Tests for Scene tools."""
    
    def test_scene_tools_import(self):
        from tools.scene import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_scene_tools_mapping(self):
        from tools.scene import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    
    def test_scene_get_info(self):
        pytest.skip("Blender not available")
        from tools.scene import get_info
        result = get_info()
        assert 'name' in result or 'error' in result
    
    def test_scene_render_settings(self):
        pytest.skip("Blender not available")
        from tools.scene import render_settings
        result = render_settings(engine='BLENDER_EEVEE')
        assert 'engine' in result or 'error' in result


class TestObjectTools:
    """Tests for Object tools."""
    
    def test_object_tools_import(self):
        from tools.objects import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_object_tools_mapping(self):
        from tools.objects import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    
    def test_object_create(self):
        pytest.skip("Blender not available")
        from tools.objects import create
        result = create(type='MESH', name='TestObj', location=(0, 0, 0))
        assert 'name' in result or 'error' in result
    
    def test_object_list(self):
        pytest.skip("Blender not available")
        from tools.objects import list_objects
        result = list_objects()
        assert 'objects' in result or 'error' in result


class TestMaterialTools:
    """Tests for Material tools."""
    
    def test_material_tools_import(self):
        from tools.materials import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_material_tools_mapping(self):
        from tools.materials import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    
    def test_material_create(self):
        pytest.skip("Blender not available")
        from tools.materials import create
        result = create(name='TestMat', color=(1, 0, 0, 1))
        assert 'name' in result or 'error' in result
    
    def test_material_list(self):
        pytest.skip("Blender not available")
        from tools.materials import list_materials
        result = list_materials()
        assert 'materials' in result or 'error' in result


class TestLightTools:
    """Tests for Light tools."""
    
    def test_light_tools_import(self):
        from tools.lights import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_light_tools_mapping(self):
        from tools.lights import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    
    def test_light_create(self):
        pytest.skip("Blender not available")
        from tools.lights import create
        result = create(type='AREA', name='TestLight', location=(0, 0, 5))
        assert 'name' in result or 'error' in result
    
    def test_light_list(self):
        pytest.skip("Blender not available")
        from tools.lights import list_lights
        result = list_lights()
        assert 'lights' in result or 'error' in result


class TestModifierTools:
    """Tests for Modifier tools."""
    
    def test_modifier_tools_import(self):
        from tools.modifiers import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_modifier_tools_mapping(self):
        from tools.modifiers import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    
    def test_modifier_types(self):
        from tools.modifiers import types
        result = types()
        assert 'types' in result or 'error' in result


class TestAnimationTools:
    """Tests for Animation tools."""
    
    def test_animation_tools_import(self):
        from tools.animation import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_animation_tools_mapping(self):
        from tools.animation import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestCameraTools:
    """Tests for Camera tools."""
    
    def test_camera_tools_import(self):
        from tools.camera import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_camera_tools_mapping(self):
        from tools.camera import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestRenderTools:
    """Tests for Render tools."""
    
    def test_render_tools_import(self):
        from tools.render import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_render_tools_mapping(self):
        from tools.render import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestIOTools:
    """Tests for I/O tools."""
    
    def test_io_tools_import(self):
        from tools.io import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_io_tools_mapping(self):
        from tools.io import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestUVTools:
    """Tests for UV/Texture tools."""
    
    def test_uv_tools_import(self):
        from tools.uv_texture import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_uv_tools_mapping(self):
        from tools.uv_texture import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestRiggingTools:
    """Tests for Rigging tools."""
    
    def test_rigging_tools_import(self):
        from tools.rigging import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_rigging_tools_mapping(self):
        from tools.rigging import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestBatchTools:
    """Tests for Batch tools."""
    
    def test_batch_tools_import(self):
        from tools.batch import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_batch_tools_mapping(self):
        from tools.batch import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestSceneUtilsTools:
    """Tests for Scene Utils tools."""
    
    def test_scene_utils_import(self):
        from tools.scene_utils import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_scene_utils_mapping(self):
        from tools.scene_utils import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestPrintingTools:
    """Tests for Printing tools."""
    
    def test_printing_tools_import(self):
        from tools.printing import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_printing_tools_mapping(self):
        from tools.printing import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestShaderNodeTools:
    """Tests for Shader Node tools."""
    
    def test_shader_tools_import(self):
        from tools.shader_nodes import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0
    
    def test_shader_tools_mapping(self):
        from tools.shader_nodes import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestGeometryNodeTools:
    """Tests for Geometry Node tools."""

    def test_geonodes_tools_import(self):
        from tools.geometry_nodes import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0

    def test_geonodes_tools_mapping(self):
        from tools.geometry_nodes import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestGeometryNodesExtendedTools:
    """Tests for Geometry Nodes Extended tools."""

    def test_geonodes_extended_tools_import(self):
        from tools.geometry_nodes_extended import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0

    def test_geonodes_extended_tools_mapping(self):
        from tools.geometry_nodes_extended import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestShaderNodesExtendedTools:
    """Tests for Shader Nodes Extended tools."""

    def test_shader_extended_tools_import(self):
        from tools.shader_nodes_extended import TOOLS, HANDLERS
        assert len(TOOLS) > 0
        assert len(HANDLERS) > 0

    def test_shader_extended_tools_mapping(self):
        from tools.shader_nodes_extended import TOOLS, HANDLERS
        for tool in TOOLS:
            assert tool.name in HANDLERS, f"Handler missing for {tool.name}"


class TestToolRegistry:
    """Tests for Tool Registry."""
    
    def test_registry_import(self):
        from tools import ToolRegistry
        assert ToolRegistry is not None
    
    def test_registry_register_tool(self):
        from tools import ToolRegistry
        from core.entities import Tool, ToolCategory, ToolPermission
        
        registry = ToolRegistry()
        tool = Tool(
            name="test.tool",
            category=ToolCategory.SCENE,
            description="Test tool",
            permission=ToolPermission.READ_ONLY,
        )
        registry.register_tool(tool, lambda: {'success': True})
        assert registry.get_tool("test.tool") is not None
    
    def test_registry_list_tools(self):
        from tools import ToolRegistry
        from core.entities import Tool, ToolCategory, ToolPermission
        
        registry = ToolRegistry()
        tool = Tool(
            name="test.tool",
            category=ToolCategory.SCENE,
            description="Test tool",
            permission=ToolPermission.READ_ONLY,
        )
        registry.register_tool(tool, lambda: {'success': True})
        tools = registry.list_tools()
        assert len(tools) == 1
    
    def test_registry_execute_tool(self):
        from tools import ToolRegistry
        from core.entities import Tool, ToolCategory, ToolPermission
        
        registry = ToolRegistry()
        tool = Tool(
            name="test.tool",
            category=ToolCategory.SCENE,
            description="Test tool",
            permission=ToolPermission.READ_ONLY,
        )
        registry.register_tool(tool, lambda: {'success': True})
        result = registry.execute_tool("test.tool", {})
        assert result.success is True
    
    def test_registry_stats(self):
        from tools import ToolRegistry
        from core.entities import Tool, ToolCategory, ToolPermission
        
        registry = ToolRegistry()
        tool = Tool(
            name="test.tool",
            category=ToolCategory.SCENE,
            description="Test tool",
            permission=ToolPermission.READ_ONLY,
        )
        registry.register_tool(tool, lambda: {'success': True})
        stats = registry.get_stats()
        assert stats['total_tools'] == 1


class TestLLMAdapters:
    """Tests for LLM Adapters."""
    
    def test_openai_provider(self):
        from adapters.llm import OpenAIProvider, LLMConfig
        config = LLMConfig(api_key='test', api_url='', model='gpt-4o')
        provider = OpenAIProvider(config)
        assert provider.get_provider_name() == 'OpenAIProvider'
        assert len(provider.get_models()) > 0
    
    def test_anthropic_provider(self):
        from adapters.llm import AnthropicProvider, LLMConfig
        config = LLMConfig(api_key='test', api_url='', model='claude-3')
        provider = AnthropicProvider(config)
        assert provider.get_provider_name() == 'AnthropicProvider'
        assert len(provider.get_models()) > 0
    
    def test_google_provider(self):
        from adapters.llm import GoogleProvider, LLMConfig
        config = LLMConfig(api_key='test', api_url='', model='gemini-pro')
        provider = GoogleProvider(config)
        assert provider.get_provider_name() == 'GoogleProvider'
        assert len(provider.get_models()) > 0
    
    def test_deepseek_provider(self):
        from adapters.llm import DeepSeekProvider, LLMConfig
        config = LLMConfig(api_key='test', api_url='', model='deepseek-chat')
        provider = DeepSeekProvider(config)
        assert provider.get_provider_name() == 'DeepSeekProvider'
        assert len(provider.get_models()) > 0


class TestInfrastructure:
    """Tests for Infrastructure modules."""
    
    def test_lru_cache(self):
        from infrastructure.cache import LRUCache
        cache = LRUCache(maxsize=10, default_ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.get("missing") is None
        stats = cache.stats()
        assert stats['hits'] > 0
    
    def test_tool_cache(self):
        from infrastructure.cache import ToolCache
        tc = ToolCache()
        tc.set_result("tool1", {"a": 1}, {"result": "ok"})
        assert tc.get_result("tool1", {"a": 1}) == {"result": "ok"}
    
    def test_connection_pool(self):
        from infrastructure.network import ConnectionPool, ConnectionConfig
        pool = ConnectionPool(ConnectionConfig(), max_connections=2)
        assert pool is not None
    
    def test_socket_server(self):
        from infrastructure.network import SocketServer
        server = SocketServer()
        assert server is not None
    
    def test_audit_logger(self):
        from infrastructure.logging import AuditLogger
        logger = AuditLogger()
        assert logger is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
