"""
blender-mcp-ultra — Core Interfaces
Abstract interfaces (ports) for the application.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..entities import Tool, ToolResult, Scene, Object, Material


class IBlenderAPI(ABC):
    """Interface for Blender API operations."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to Blender instance."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from Blender."""
        pass
    
    @abstractmethod
    def execute_code(self, code: str) -> ToolResult:
        """Execute Python code in Blender."""
        pass
    
    @abstractmethod
    def get_scene_info(self) -> Scene:
        """Get current scene information."""
        pass
    
    @abstractmethod
    def get_object(self, name: str) -> Optional[Object]:
        """Get object by name."""
        pass
    
    @abstractmethod
    def create_object(self, obj_type: str, name: str, **kwargs) -> ToolResult:
        """Create a new object."""
        pass
    
    @abstractmethod
    def delete_object(self, name: str) -> ToolResult:
        """Delete an object."""
        pass
    
    @abstractmethod
    def create_material(self, name: str, **kwargs) -> ToolResult:
        """Create a new material."""
        pass
    
    @abstractmethod
    def apply_material(self, object_name: str, material_name: str) -> ToolResult:
        """Apply material to object."""
        pass
    
    @abstractmethod
    def search_api_docs(self, query: str) -> Dict[str, Any]:
        """Search Blender API documentation."""
        pass
    
    @abstractmethod
    def get_viewport_screenshot(self) -> ToolResult:
        """Capture viewport screenshot."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to Blender."""
        pass
    
    @abstractmethod
    def get_blender_version(self) -> str:
        """Get Blender version."""
        pass


class ILLMProvider(ABC):
    """Interface for LLM providers."""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate API key."""
        pass
    
    @abstractmethod
    def get_models(self) -> List[str]:
        """Get available models."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name."""
        pass


class IToolRegistry(ABC):
    """Interface for tool registry."""
    
    @abstractmethod
    def register_tool(self, tool: Tool, handler: callable) -> None:
        """Register a tool."""
        pass
    
    @abstractmethod
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool."""
        pass
    
    @abstractmethod
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get tool by name."""
        pass
    
    @abstractmethod
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get tools by category."""
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a tool."""
        pass
    
    @abstractmethod
    def list_tools(self) -> List[Tool]:
        """List all registered tools."""
        pass


class ICache(ABC):
    """Interface for cache storage."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache."""
        pass
    
    @abstractmethod
    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass


class IStorage(ABC):
    """Interface for persistent storage."""
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """Load data from storage."""
        pass
    
    @abstractmethod
    def save(self, key: str, value: Any) -> bool:
        """Save data to storage."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data from storage."""
        pass
    
    @abstractmethod
    def list_keys(self) -> List[str]:
        """List all keys in storage."""
        pass


class ISecurityValidator(ABC):
    """Interface for security validation."""
    
    @abstractmethod
    def validate_code(self, code: str) -> bool:
        """Validate code for security."""
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Validate URL for security."""
        pass
    
    @abstractmethod
    def validate_input(self, input_value: str, field_name: str) -> str:
        """Validate and sanitize input."""
        pass
    
    @abstractmethod
    def check_rate_limit(self, key: str) -> bool:
        """Check rate limit."""
        pass
