"""
blender-mcp-ultra — Tool Registry
Manages registration and execution of tools.
"""

import importlib
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.entities import Tool, ToolCategory, ToolPermission, ToolResult
from ..core.interfaces import IBlenderAPI, IToolRegistry
from ..infrastructure.cache import get_tool_cache
from ..infrastructure.logging import get_logger
from ..infrastructure.security import InputValidationError, validate_string


def _remediation_hint(tool_name: str, exc: Exception) -> str:
    """Sugerencia de remediación según el tipo de fallo — errores que enseñan."""
    msg = str(exc)
    low = msg.lower()
    if isinstance(exc, TypeError) and "unexpected keyword" in low:
        kw = msg.split("'")[-2] if msg.count("'") >= 2 else "?"
        return (
            f"El parámetro '{kw}' no existe en este tool. "
            "Consulta su definición en list_tools (campo parameters)."
        )
    if isinstance(exc, KeyError):
        return f"Falta el parámetro obligatorio '{exc}'. Revisa 'required' en list_tools."
    if "no encontrado" in low or "not found" in low or "not found:" in low:
        return (
            "El objeto/recurso no existe (¿nombre exacto?). "
            "Usa scene.query(name_contains=...) para listar nombres reales."
        )
    if "nonetype" in low:
        return (
            "Algo interno es None: puede que el objeto tenga un slot de material "
            "vacío o falte cámara activa. Verifica con mesh.get_topology o "
            "scene.get_info antes de reintentar."
        )
    if "fuera de rango" in low or "out of range" in low or "index" in low:
        return (
            "Índice inválido: la topología cambió. Vuelve a llamar a "
            "mesh.get_topology para re-obtener índices frescos."
        )
    if "permission" in low or "destructive" in low:
        return "Este tool requiere permiso elevado; pásalo en el contexto del agente."
    return ""


class ToolRegistry(IToolRegistry):
    """
    Registry for managing tools.

    Features:
    - Lazy loading of tool modules
    - Permission-based execution
    - Automatic validation
    - Execution logging
    - Tool result caching
    """

    def __init__(self, blender_api: IBlenderAPI | None = None, use_cache: bool = True):
        """
        Initialize tool registry.

        Args:
            blender_api: Blender API instance
            use_cache: Whether to cache tool results
        """
        self.blender_api = blender_api
        self._tools: dict[str, Tool] = {}
        self._handlers: dict[str, Callable] = {}
        self._loaded_categories: set = set()
        self._logger = get_logger()
        self._cache = get_tool_cache() if use_cache else None

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

    def get_tool(self, tool_name: str) -> Tool | None:
        """Get tool by name."""
        return self._tools.get(tool_name)

    def get_tools_by_category(self, category: str) -> list[Tool]:
        """Get tools by category."""
        return [tool for tool in self._tools.values() if tool.category.value == category]

    def execute_tool(self, tool_name: str, params: dict[str, Any]) -> ToolResult:
        """Execute a tool."""
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(success=False, error=f"Tool not found: {tool_name}")

        handler = self._handlers.get(tool_name)
        if not handler:
            return ToolResult(success=False, error=f"Handler not found for tool: {tool_name}")

        # Check cache first
        if self._cache:
            cached_result = self._cache.get_result(tool_name, params)
            if cached_result is not None:
                return cached_result

        start_time = time.time()

        try:
            # Validate inputs
            self._validate_params(tool, params)

            # Execute handler
            result = handler(**params)

            execution_time = time.time() - start_time

            # Log execution
            self._logger.log_tool_execution(
                tool_name=tool_name, params=params, success=True, execution_time=execution_time
            )

            tool_result = ToolResult(
                success=True,
                data=result,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat(),
            )

            # Cache result
            if self._cache:
                self._cache.set_result(tool_name, params, tool_result)

            return tool_result

        except Exception as e:
            execution_time = time.time() - start_time

            # Log error
            self._logger.log_tool_execution(
                tool_name=tool_name,
                params=params,
                success=False,
                execution_time=execution_time,
                error=str(e),
            )

            return ToolResult(
                success=False,
                error=str(e),
                hint=_remediation_hint(tool_name, e),
                execution_time=execution_time,
                timestamp=datetime.now().isoformat(),
            )

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def _validate_params(self, tool: Tool, params: dict[str, Any]) -> None:
        """Valida strings (inyección/path traversal): error → ToolResult con hint."""
        for key, value in params.items():
            if isinstance(value, str):
                try:
                    validate_string(value, field_name=key)
                except InputValidationError as e:
                    raise ValueError(f"parámetro '{key}' rechazado por validación: {e}") from e

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
            tools = getattr(module, "TOOLS", [])
            handlers = getattr(module, "HANDLERS", {})

            for tool in tools:
                if tool.name in handlers:
                    self.register_tool(tool, handlers[tool.name])

            self._loaded_categories.add(category)
            return len(tools)

        except ImportError:
            return 0

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        categories = {}
        for tool in self._tools.values():
            cat = tool.category.value
            categories[cat] = categories.get(cat, 0) + 1

        stats = {
            "total_tools": len(self._tools),
            "loaded_categories": len(self._loaded_categories),
            "tools_by_category": categories,
        }

        if self._cache:
            stats["cache"] = self._cache.stats()

        return stats


# Singleton instance
_registry = None


def get_registry(blender_api: IBlenderAPI | None = None) -> ToolRegistry:
    """Get singleton registry instance."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry(blender_api)
    return _registry
