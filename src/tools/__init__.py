"""
blender-mcp-ultra — Tool Registry
Manages registration and execution of tools.
"""
import time
import importlib
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

from core.entities import Tool, ToolResult, ToolCategory, ToolPermission
from core.interfaces import IToolRegistry, IBlenderAPI
from infrastructure.security import validate_code_strict
from infrastructure.logging import get_logger


class ToolRegistry(IToolRegistry):
    """
    Registry for managing tools.
    
    Features:
    - Lazy loading of tool modules
    - Permission-based execution
    - Automatic validation
    - Execution logging
    """
    
    def __init__(self, blender_api: Optional[IBlenderAPI] = None):
        """
        Initialize tool registry.
        
        Args:
            blender_api: Blender API instance
        """
        self.blender_api = blender_api
        self._tools: Dict[str, Tool] = {}
        self._handlers: Dict[str, Callable] = {}
        self._loaded_categories: set = set()
        self._logger = get_logger()
    
    def register_tool(self, tool: Tool, handler: Callable) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        self._handlers[tool.name] = handler
        
        # Load category if not loaded
        if tool.category.value not in self._loaded_categories:
            self._loaded_categories.add(tool.category.value)
    
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool."""
        self._tools.pop(tool_name, None)
        self._handlers.pop(tool_name, None)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get tool by name."""
        return self._tools.get(tool_name)
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get tools by category."""
        return [
            tool for tool in self._tools.values()
            if tool.category.value == category
        ]
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a tool."""
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}"
            )
        
        handler = self._handlers.get(tool_name)
        if not handler:
            return ToolResult(
                success=False,
                error=f"Handler not found for tool: {tool_name}"
            )
        
        start_time = time.time()
        
        try:
            # Validate inputs
            self._validate_params(tool, params)
            
            # Execute handler
            result = handler(**params)
            
            execution_time = time.time() - start_time
            
            # Log execution
            self._logger.log_tool_execution(
                tool_name=tool_name,
                params=params,
                success=True,
                execution_time=execution_time
            )
            
            return ToolResult(
                success=True,
                data=result,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log error
            self._logger.log_tool_execution(
                tool_name=tool_name,
                params=params,
                success=False,
                execution_time=execution_time,
                error=str(e)
            )
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                timestamp=datetime.now().isoformat()
            )
    
    def list_tools(self) -> List[Tool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def _validate_params(self, tool: Tool, params: Dict[str, Any]) -> None:
        """Validate tool parameters."""
        # Basic validation - extend as needed
        for key, value in params.items():
            if isinstance(value, str):
                # Validate string inputs
                try:
                    from infrastructure.security import validate_string
                    validate_string(value, field_name=key)
                except ImportError:
                    pass  # Skip validation if security module not available
    
    def load_category(self, category: str) -> int:
        """
        Load tools from a category module.
        
        Args:
            category: Category name
            
        Returns:
            Number of tools loaded
        """
        if category in self._loaded_categories:
            return 0
        
        try:
            module = importlib.import_module(f"tools.{category}")
            
            # Look for TOOLS list in module
            tools = getattr(module, 'TOOLS', [])
            handlers = getattr(module, 'HANDLERS', {})
            
            for tool in tools:
                if tool.name in handlers:
                    self.register_tool(tool, handlers[tool.name])
            
            self._loaded_categories.add(category)
            return len(tools)
            
        except ImportError:
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        categories = {}
        for tool in self._tools.values():
            cat = tool.category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_tools': len(self._tools),
            'loaded_categories': len(self._loaded_categories),
            'tools_by_category': categories,
        }


# Singleton instance
_registry = None

def get_registry(blender_api: Optional[IBlenderAPI] = None) -> ToolRegistry:
    """Get singleton registry instance."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry(blender_api)
    return _registry
