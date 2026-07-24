#!/usr/bin/env python3
"""
blender-mcp-ultra — Complete Test Suite
Run this script to verify all modules work correctly.
"""
import sys
import os

# Add parent of src to path, so src.core works as package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_security_modules():
    """Test all security modules."""
    print("=" * 60)
    print("TESTING SECURITY MODULES")
    print("=" * 60)
    
    # AST Validator
    print("\n1. AST Validator...")
    from infrastructure.security.ast_validator import ASTValidator, SecurityError
    validator = ASTValidator()
    
    result = validator.validate("x = 1 + 2")
    assert result.is_safe, f"Safe code failed: {result.errors}"
    print("   ✓ Safe code passed")
    
    result = validator.validate("import os")
    assert not result.is_safe, "Dangerous import should be blocked"
    print("   ✓ Blocked import os")
    
    # Sandbox
    print("\n2. Sandbox...")
    from infrastructure.security.sandbox import Sandbox
    sandbox = Sandbox(validate_code=True)
    
    result = sandbox.execute("print('hello')")
    assert result.success, f"Sandbox failed: {result.error}"
    assert 'hello' in result.output
    print("   ✓ Safe execution")
    
    result = sandbox.execute("import os")
    assert not result.success, "Dangerous code should be blocked"
    print("   ✓ Blocked dangerous code")
    
    # URL Validator
    print("\n3. URL Validator...")
    from infrastructure.security.url_validator import URLValidator
    url_validator = URLValidator()
    
    result = url_validator.validate("https://polyhaven.com/textures")
    assert result.is_safe, f"Safe URL failed: {result.errors}"
    print("   ✓ Safe URL")
    
    result = url_validator.validate("file:///etc/passwd")
    assert not result.is_safe, "file:// URL should be blocked"
    print("   ✓ Blocked file:// URL")
    
    # Rate Limiter
    print("\n4. Rate Limiter...")
    from infrastructure.security.rate_limiter import RateLimiter
    limiter = RateLimiter()
    
    assert limiter.check("user1") is True
    print("   ✓ Allows first request")
    
    # Input Validator
    print("\n5. Input Validator...")
    from infrastructure.security.input_validator import InputValidator
    input_validator = InputValidator()
    
    result = input_validator.validate_string("hello world")
    assert result == "hello world"
    print("   ✓ Safe string")
    
    print("\n" + "=" * 60)
    print("✓ ALL SECURITY TESTS PASSED")
    print("=" * 60)


def test_core_entities():
    """Test core entities."""
    print("\n" + "=" * 60)
    print("TESTING CORE ENTITIES")
    print("=" * 60)
    
    from core.entities import Tool, ToolCategory, ToolPermission, Scene, Object, Material
    
    # Tool
    print("\n1. Tool entity...")
    tool = Tool(
        name="test.tool",
        category=ToolCategory.SCENE,
        description="Test tool",
        permission=ToolPermission.READ_ONLY,
    )
    assert tool.name == "test.tool"
    print("   ✓ Tool created")
    
    # Scene
    print("\n2. Scene entity...")
    scene = Scene(name="TestScene", object_count=5)
    assert scene.name == "TestScene"
    assert scene.object_count == 5
    print("   ✓ Scene created")
    
    # Object
    print("\n3. Object entity...")
    obj = Object(name="Cube", type="MESH", location=(1, 2, 3))
    assert obj.name == "Cube"
    assert obj.location == (1, 2, 3)
    print("   ✓ Object created")
    
    # Material
    print("\n4. Material entity...")
    mat = Material(name="Red", color=(1, 0, 0, 1))
    assert mat.name == "Red"
    assert mat.color == (1, 0, 0, 1)
    print("   ✓ Material created")
    
    print("\n" + "=" * 60)
    print("✓ ALL ENTITY TESTS PASSED")
    print("=" * 60)


def test_tool_registry():
    """Test tool registry."""
    print("\n" + "=" * 60)
    print("TESTING TOOL REGISTRY")
    print("=" * 60)
    
    from tools import ToolRegistry
    from core.entities import Tool, ToolCategory, ToolPermission
    
    registry = ToolRegistry()
    
    # Register tool
    print("\n1. Register tool...")
    def test_handler():
        return {"success": True}
    
    tool = Tool(
        name="test.tool",
        category=ToolCategory.SCENE,
        description="Test tool",
        permission=ToolPermission.READ_ONLY,
    )
    
    registry.register_tool(tool, test_handler)
    assert registry.get_tool("test.tool") is not None
    print("   ✓ Tool registered")
    
    # List tools
    print("\n2. List tools...")
    tools = registry.list_tools()
    assert len(tools) == 1
    print("   ✓ Tools listed")
    
    # Execute tool
    print("\n3. Execute tool...")
    result = registry.execute_tool("test.tool", {})
    assert result.success is True
    print("   ✓ Tool executed")
    
    # Stats
    print("\n4. Registry stats...")
    stats = registry.get_stats()
    assert stats['total_tools'] == 1
    print("   ✓ Stats retrieved")
    
    print("\n" + "=" * 60)
    print("✓ ALL REGISTRY TESTS PASSED")
    print("=" * 60)


def test_scene_tools():
    """Test scene tools (without Blender)."""
    print("\n" + "=" * 60)
    print("TESTING SCENE TOOLS")
    print("=" * 60)
    
    from tools.scene import TOOLS, HANDLERS
    
    # Check tools defined
    print("\n1. Tools defined...")
    assert len(TOOLS) > 0
    print(f"   ✓ {len(TOOLS)} tools defined")
    
    # Check handlers
    print("\n2. Handlers defined...")
    assert len(HANDLERS) > 0
    print(f"   ✓ {len(HANDLERS)} handlers defined")
    
    # Check tool-handler mapping
    print("\n3. Tool-handler mapping...")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    
    print("\n" + "=" * 60)
    print("✓ ALL SCENE TOOLS TESTS PASSED")
    print("=" * 60)


def test_object_tools():
    """Test object tools (without Blender)."""
    print("\n" + "=" * 60)
    print("TESTING OBJECT TOOLS")
    print("=" * 60)
    
    from tools.objects import TOOLS, HANDLERS
    
    # Check tools defined
    print("\n1. Tools defined...")
    assert len(TOOLS) > 0
    print(f"   ✓ {len(TOOLS)} tools defined")
    
    # Check handlers
    print("\n2. Handlers defined...")
    assert len(HANDLERS) > 0
    print(f"   ✓ {len(HANDLERS)} handlers defined")
    
    # Check tool-handler mapping
    print("\n3. Tool-handler mapping...")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    
    print("\n" + "=" * 60)
    print("✓ ALL OBJECT TOOLS TESTS PASSED")
    print("=" * 60)


def test_material_tools():
    """Test material tools (without Blender)."""
    print("\n" + "=" * 60)
    print("TESTING MATERIAL TOOLS")
    print("=" * 60)
    
    from tools.materials import TOOLS, HANDLERS
    
    # Check tools defined
    print("\n1. Tools defined...")
    assert len(TOOLS) > 0
    print(f"   ✓ {len(TOOLS)} tools defined")
    
    # Check handlers
    print("\n2. Handlers defined...")
    assert len(HANDLERS) > 0
    print(f"   ✓ {len(HANDLERS)} handlers defined")
    
    # Check tool-handler mapping
    print("\n3. Tool-handler mapping...")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    
    print("\n" + "=" * 60)
    print("✓ ALL MATERIAL TOOLS TESTS PASSED")
    print("=" * 60)


def test_light_tools():
    """Test light tools (without Blender)."""
    print("\n" + "=" * 60)
    print("TESTING LIGHT TOOLS")
    print("=" * 60)
    
    from tools.lights import TOOLS, HANDLERS
    
    # Check tools defined
    print("\n1. Tools defined...")
    assert len(TOOLS) > 0
    print(f"   ✓ {len(TOOLS)} tools defined")
    
    # Check handlers
    print("\n2. Handlers defined...")
    assert len(HANDLERS) > 0
    print(f"   ✓ {len(HANDLERS)} handlers defined")
    
    # Check tool-handler mapping
    print("\n3. Tool-handler mapping...")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    
    print("\n" + "=" * 60)
    print("✓ ALL LIGHT TOOLS TESTS PASSED")
    print("=" * 60)


def test_modifier_tools():
    """Test modifier tools (without Blender)."""
    print("\n" + "=" * 60)
    print("TESTING MODIFIER TOOLS")
    print("=" * 60)
    
    from tools.modifiers import TOOLS, HANDLERS
    
    # Check tools defined
    print("\n1. Tools defined...")
    assert len(TOOLS) > 0
    print(f"   ✓ {len(TOOLS)} tools defined")
    
    # Check handlers
    print("\n2. Handlers defined...")
    assert len(HANDLERS) > 0
    print(f"   ✓ {len(HANDLERS)} handlers defined")
    
    # Check tool-handler mapping
    print("\n3. Tool-handler mapping...")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    
    print("\n" + "=" * 60)
    print("✓ ALL MODIFIER TOOLS TESTS PASSED")
    print("=" * 60)


def test_animation_tools():
    """Test animation tools (without Blender)."""
    print("\n" + "=" * 60)
    print("TESTING ANIMATION TOOLS")
    print("=" * 60)
    
    from tools.animation import TOOLS, HANDLERS
    
    # Check tools defined
    print("\n1. Tools defined...")
    assert len(TOOLS) > 0
    print(f"   ✓ {len(TOOLS)} tools defined")
    
    # Check handlers
    print("\n2. Handlers defined...")
    assert len(HANDLERS) > 0
    print(f"   ✓ {len(HANDLERS)} handlers defined")
    
    # Check tool-handler mapping
    print("\n3. Tool-handler mapping...")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    
    print("\n" + "=" * 60)
    print("✓ ALL ANIMATION TOOLS TESTS PASSED")
    print("=" * 60)


def test_llm_adapters():
    """Test LLM adapters."""
    print("\n" + "=" * 60)
    print("TESTING LLM ADAPTERS")
    print("=" * 60)
    
    from adapters.llm import OpenAIProvider, AnthropicProvider, GoogleProvider, DeepSeekProvider, LLMConfig
    
    # Create configs
    print("\n1. Create provider configs...")
    configs = {
        'openai': LLMConfig(api_key='test', api_url='', model='gpt-4o'),
        'anthropic': LLMConfig(api_key='test', api_url='', model='claude-3'),
        'google': LLMConfig(api_key='test', api_url='', model='gemini-pro'),
        'deepseek': LLMConfig(api_key='test', api_url='', model='deepseek-chat'),
    }
    print("   ✓ Configs created")
    
    # Create providers
    print("\n2. Create providers...")
    providers = {
        'openai': OpenAIProvider(configs['openai']),
        'anthropic': AnthropicProvider(configs['anthropic']),
        'google': GoogleProvider(configs['google']),
        'deepseek': DeepSeekProvider(configs['deepseek']),
    }
    print("   ✓ Providers created")
    
    # Get provider names
    print("\n3. Get provider names...")
    for name, provider in providers.items():
        assert provider.get_provider_name() is not None
    print("   ✓ All providers have names")
    
    # Get models
    print("\n4. Get available models...")
    for name, provider in providers.items():
        models = provider.get_models()
        assert len(models) > 0
    print("   ✓ All providers have models")
    
    print("\n" + "=" * 60)
    print("✓ ALL LLM ADAPTER TESTS PASSED")
    print("=" * 60)


def test_camera_tools():
    """Test camera tools."""
    print("\n" + "=" * 60)
    print("TESTING CAMERA TOOLS")
    print("=" * 60)
    from tools.camera import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ CAMERA TOOLS PASSED")
    print("=" * 60)


def test_render_tools():
    """Test render tools."""
    print("\n" + "=" * 60)
    print("TESTING RENDER TOOLS")
    print("=" * 60)
    from tools.render import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ RENDER TOOLS PASSED")
    print("=" * 60)


def test_io_tools():
    """Test I/O tools."""
    print("\n" + "=" * 60)
    print("TESTING I/O TOOLS")
    print("=" * 60)
    from tools.io import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ I/O TOOLS PASSED")
    print("=" * 60)


def test_uv_texture_tools():
    """Test UV/Texture tools."""
    print("\n" + "=" * 60)
    print("TESTING UV/TEXTURE TOOLS")
    print("=" * 60)
    from tools.uv_texture import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ UV/TEXTURE TOOLS PASSED")
    print("=" * 60)


def test_rigging_tools():
    """Test rigging tools."""
    print("\n" + "=" * 60)
    print("TESTING RIGGING TOOLS")
    print("=" * 60)
    from tools.rigging import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ RIGGING TOOLS PASSED")
    print("=" * 60)


def test_batch_tools():
    """Test batch tools."""
    print("\n" + "=" * 60)
    print("TESTING BATCH TOOLS")
    print("=" * 60)
    from tools.batch import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ BATCH TOOLS PASSED")
    print("=" * 60)


def test_scene_utils_tools():
    """Test scene utils tools."""
    print("\n" + "=" * 60)
    print("TESTING SCENE UTILS TOOLS")
    print("=" * 60)
    from tools.scene_utils import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ SCENE UTILS TOOLS PASSED")
    print("=" * 60)


def test_printing_tools():
    """Test printing tools."""
    print("\n" + "=" * 60)
    print("TESTING PRINTING TOOLS")
    print("=" * 60)
    from tools.printing import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ PRINTING TOOLS PASSED")
    print("=" * 60)


def test_shader_node_tools():
    """Test shader node tools."""
    print("\n" + "=" * 60)
    print("TESTING SHADER NODE TOOLS")
    print("=" * 60)
    from tools.shader_nodes import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ SHADER NODE TOOLS PASSED")
    print("=" * 60)


def test_geonode_tools():
    """Test geometry node tools."""
    print("\n" + "=" * 60)
    print("TESTING GEOMETRY NODE TOOLS")
    print("=" * 60)
    from tools.geometry_nodes import TOOLS, HANDLERS
    print(f"\n   ✓ {len(TOOLS)} tools defined, {len(HANDLERS)} handlers")
    for tool in TOOLS:
        assert tool.name in HANDLERS, f"Handler missing for {tool.name}"
    print("   ✓ All tools have handlers")
    print("\n" + "=" * 60)
    print("✓ GEOMETRY NODE TOOLS PASSED")
    print("=" * 60)


def test_infrastructure():
    """Test infrastructure modules."""
    print("\n" + "=" * 60)
    print("TESTING INFRASTRUCTURE")
    print("=" * 60)

    print("\n1. LRU Cache...")
    from infrastructure.cache import LRUCache
    cache = LRUCache(maxsize=10, default_ttl=60)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    assert cache.get("missing") is None
    stats = cache.stats()
    assert stats['hits'] > 0
    print("   ✓ LRU Cache works")

    print("\n2. Tool Cache...")
    from infrastructure.cache import ToolCache
    tc = ToolCache()
    tc.set_result("tool1", {"a": 1}, {"result": "ok"})
    assert tc.get_result("tool1", {"a": 1}) == {"result": "ok"}
    print("   ✓ Tool Cache works")

    print("\n3. Connection Pool...")
    from infrastructure.network import ConnectionPool, ConnectionConfig
    pool = ConnectionPool(ConnectionConfig(), max_connections=2)
    print("   ✓ Connection Pool created")

    print("\n4. Socket Server...")
    from infrastructure.network import SocketServer
    server = SocketServer()
    print("   ✓ Socket Server created")

    print("\n" + "=" * 60)
    print("✓ ALL INFRASTRUCTURE TESTS PASSED")
    print("=" * 60)


def test_total_tools():
    """Count total tools."""
    print("\n" + "=" * 60)
    print("TOOL COUNT SUMMARY")
    print("=" * 60)
    from tools.scene import TOOLS as t1
    from tools.objects import TOOLS as t2
    from tools.materials import TOOLS as t3
    from tools.lights import TOOLS as t4
    from tools.modifiers import TOOLS as t5
    from tools.animation import TOOLS as t6
    from tools.camera import TOOLS as t7
    from tools.render import TOOLS as t8
    from tools.io import TOOLS as t9
    from tools.uv_texture import TOOLS as t10
    from tools.rigging import TOOLS as t11
    from tools.batch import TOOLS as t12
    from tools.scene_utils import TOOLS as t13
    from tools.printing import TOOLS as t14
    from tools.shader_nodes import TOOLS as t15
    from tools.geometry_nodes import TOOLS as t16

    categories = [
        ("Scene", t1), ("Objects", t2), ("Materials", t3), ("Lights", t4),
        ("Modifiers", t5), ("Animation", t6), ("Camera", t7), ("Render", t8),
        ("I/O", t9), ("UV/Texture", t10), ("Rigging", t11), ("Batch", t12),
        ("Scene Utils", t13), ("Printing", t14), ("Shader Nodes", t15), ("Geometry Nodes", t16),
    ]
    total = 0
    for name, tools in categories:
        print(f"   {name:15s}: {len(tools):3d} tools")
        total += len(tools)
    print(f"   {'─'*25}")
    print(f"   {'TOTAL':15s}: {total:3d} tools")
    print("=" * 60)


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("blender-mcp-ultra — COMPLETE TEST SUITE")
    print("=" * 60 + "\n")
    
    tests = [
        test_security_modules,
        test_core_entities,
        test_tool_registry,
        test_scene_tools,
        test_object_tools,
        test_material_tools,
        test_light_tools,
        test_modifier_tools,
        test_animation_tools,
        test_camera_tools,
        test_render_tools,
        test_io_tools,
        test_uv_texture_tools,
        test_rigging_tools,
        test_batch_tools,
        test_scene_utils_tools,
        test_printing_tools,
        test_shader_node_tools,
        test_geonode_tools,
        test_infrastructure,
        test_llm_adapters,
        test_total_tools,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ TEST FAILED: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {failed} TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
