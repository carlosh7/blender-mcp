"""
blender-mcp-ultra — Tests for Tool Registry (Versioned)
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestToolRegistry:
    """Tests for versioned tool registry."""
    
    def test_import(self):
        """Registry should be importable."""
        from tools.registry import ToolRegistry
        assert ToolRegistry is not None
    
    def test_create_registry(self):
        """Should create empty registry."""
        from tools.registry import ToolRegistry
        r = ToolRegistry()
        assert r is not None
        assert r.version == "1.0.0"
    
    def test_register_tool(self):
        """Should register a tool."""
        from tools.registry import ToolRegistry, ToolInfo
        r = ToolRegistry()
        
        tool = ToolInfo(
            name="test_tool",
            version="1.0.0",
            description="Test tool",
            category="test",
            handler="test.handler",
        )
        r.register(tool)
        
        assert r.get("test_tool", "1.0.0") is not None
    
    def test_get_tool(self):
        """Should get registered tool."""
        from tools.registry import ToolRegistry, ToolInfo
        r = ToolRegistry()
        
        tool = ToolInfo(
            name="my_tool",
            version="2.0.0",
            description="My tool",
            category="test",
            handler="my.handler",
        )
        r.register(tool)
        
        result = r.get("my_tool", "2.0.0")
        assert result is not None
        assert result.name == "my_tool"
        assert result.version == "2.0.0"
    
    def test_get_latest_version(self):
        """Should get latest version when version not specified."""
        from tools.registry import ToolRegistry, ToolInfo
        r = ToolRegistry()
        
        r.register(ToolInfo(name="tool", version="1.0.0", description="", category="", handler=""))
        r.register(ToolInfo(name="tool", version="2.0.0", description="", category="", handler=""))
        r.register(ToolInfo(name="tool", version="1.5.0", description="", category="", handler=""))
        
        result = r.get("tool")
        assert result.version == "2.0.0"
    
    def test_unregister_tool(self):
        """Should unregister a tool."""
        from tools.registry import ToolRegistry, ToolInfo
        r = ToolRegistry()
        
        tool = ToolInfo(name="temp", version="1.0.0", description="", category="", handler="")
        r.register(tool)
        assert r.get("temp", "1.0.0") is not None
        
        r.unregister("temp", "1.0.0")
        assert r.get("temp", "1.0.0") is None
    
    def test_list_tools(self):
        """Should list all tools."""
        from tools.registry import ToolRegistry, ToolInfo
        r = ToolRegistry()
        
        r.register(ToolInfo(name="tool1", version="1.0.0", description="", category="cat1", handler=""))
        r.register(ToolInfo(name="tool2", version="1.0.0", description="", category="cat2", handler=""))
        
        tools = r.list_tools()
        assert len(tools) == 2
    
    def test_list_tools_by_category(self):
        """Should filter tools by category."""
        from tools.registry import ToolRegistry, ToolInfo
        r = ToolRegistry()
        
        r.register(ToolInfo(name="tool1", version="1.0.0", description="", category="cat1", handler=""))
        r.register(ToolInfo(name="tool2", version="1.0.0", description="", category="cat1", handler=""))
        r.register(ToolInfo(name="tool3", version="1.0.0", description="", category="cat2", handler=""))
        
        tools = r.list_tools(category="cat1")
        assert len(tools) == 2
    
    def test_get_handler(self):
        """Should get handler path."""
        from tools.registry import ToolRegistry, ToolInfo
        r = ToolRegistry()
        
        r.register(ToolInfo(
            name="my_tool",
            version="1.0.0",
            description="",
            category="",
            handler="src.tools.mypackage.myhandler",
        ))
        
        handler = r.get_handler("my_tool", "1.0.0")
        assert handler == "src.tools.mypackage.myhandler"
    
    def test_default_tools_registered(self):
        """Default tools should be registered."""
        from tools.registry import get_registry
        r = get_registry()
        
        tools = r.list_tools()
        assert len(tools) >= 10  # At least 10 default tools
    
    def test_singleton(self):
        """get_registry should return singleton."""
        from tools.registry import get_registry
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2
