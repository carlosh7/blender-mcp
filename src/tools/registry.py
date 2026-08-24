"""
blender-mcp-ultra — Tool Registry (Versioned)
Central registry for all tools with version support.
Each tool is registered as tool_name@version for client negotiation.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolInfo:
    """Information about a registered tool."""

    name: str
    version: str
    description: str
    category: str
    handler: str  # Module path to handler function
    params: list[str] = field(default_factory=list)
    required_params: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


class ToolRegistry:
    """
    Central registry for all MCP tools.

    Tools are registered as name@version for client negotiation.
    Example: "create_object@v1", "apply_material@v1"
    """

    def __init__(self):
        self._tools: dict[str, ToolInfo] = {}
        self._version = "1.0.0"

    @property
    def version(self) -> str:
        """Get registry version."""
        return self._version

    def register(self, tool: ToolInfo) -> None:
        """
        Register a tool.

        Args:
            tool: ToolInfo with name, version, description, etc.
        """
        key = f"{tool.name}@{tool.version}"
        self._tools[key] = tool

    def unregister(self, name: str, version: str) -> bool:
        """
        Unregister a tool.

        Args:
            name: Tool name
            version: Tool version

        Returns:
            True if unregistered, False if not found
        """
        key = f"{name}@{version}"
        if key in self._tools:
            del self._tools[key]
            return True
        return False

    def get(self, name: str, version: str = None) -> ToolInfo | None:
        """
        Get a tool by name and version.

        Args:
            name: Tool name
            version: Tool version (optional, returns latest if not specified)

        Returns:
            ToolInfo or None
        """
        if version:
            key = f"{name}@{version}"
            return self._tools.get(key)

        # Find latest version
        tools = [t for t in self._tools.values() if t.name == name]
        if not tools:
            return None
        return sorted(tools, key=lambda t: t.version, reverse=True)[0]

    def list_tools(self, category: str = None) -> list[dict[str, Any]]:
        """
        List all registered tools.

        Args:
            category: Filter by category (optional)

        Returns:
            List of tool info dicts
        """
        tools = self._tools.values()
        if category:
            tools = [t for t in tools if t.category == category]

        return [
            {
                "name": t.name,
                "version": t.version,
                "description": t.description,
                "category": t.category,
                "params": t.params,
                "required_params": t.required_params,
            }
            for t in tools
        ]

    def get_handler(self, name: str, version: str = None) -> str | None:
        """
        Get handler module path for a tool.

        Args:
            name: Tool name
            version: Tool version

        Returns:
            Handler module path or None
        """
        tool = self.get(name, version)
        return tool.handler if tool else None

    def negotiate_version(self, client_version: str, tool_name: str) -> str | None:
        """
        Negotiate tool version with client.

        Args:
            client_version: Client's requested version
            tool_name: Tool name

        Returns:
            Negotiated version or None if incompatible
        """
        tools = [t for t in self._tools.values() if t.name == tool_name]
        if not tools:
            return None

        # Simple semver matching
        # In production, use proper semver library
        for tool in tools:
            if tool.version.startswith(client_version.split(".")[0]):
                return tool.version

        return None


# ═══════════════════════════════════════════════════════════════
# DEFAULT REGISTRY
# ═══════════════════════════════════════════════════════════════

_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """Get singleton tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
        _register_default_tools(_registry)
    return _registry


def _register_default_tools(registry: ToolRegistry) -> None:
    """Register default tools."""

    # ═══ SCENE TOOLS ═══
    registry.register(
        ToolInfo(
            name="get_scene_info",
            version="1.0.0",
            description="Get information about the current scene",
            category="scene",
            handler="src.tools.scene.info.get_scene_info",
            params=["include_objects", "include_materials"],
        )
    )

    registry.register(
        ToolInfo(
            name="create_collection",
            version="1.0.0",
            description="Create a new collection",
            category="scene",
            handler="src.tools.scene.collection.create_collection",
            params=["name", "parent"],
            required_params=["name"],
        )
    )

    # ═══ OBJECT TOOLS ═══
    registry.register(
        ToolInfo(
            name="create_object",
            version="1.0.0",
            description="Create a standard object with rules",
            category="objects",
            handler="src.tools.objects.creation.create_object",
            params=["object_type", "position", "collection", "material"],
            required_params=["object_type"],
        )
    )

    registry.register(
        ToolInfo(
            name="validate_object",
            version="1.0.0",
            description="Validate an object",
            category="objects",
            handler="src.tools.objects.validation.validate_object",
            params=["name", "expected_location", "expected_type"],
            required_params=["name"],
        )
    )

    # ═══ MATERIAL TOOLS ═══
    registry.register(
        ToolInfo(
            name="apply_material",
            version="1.0.0",
            description="Apply PBR material to object",
            category="materials",
            handler="src.tools.materials.pbr.apply_material",
            params=["obj_name", "material_type", "params"],
            required_params=["obj_name", "material_type"],
        )
    )

    registry.register(
        ToolInfo(
            name="create_pbr_material",
            version="1.0.0",
            description="Create a PBR material",
            category="materials",
            handler="src.tools.materials.pbr.create_pbr_material",
            params=["name", "material_type", "params"],
            required_params=["name", "material_type"],
        )
    )

    # ═══ MESH TOOLS ═══
    registry.register(
        ToolInfo(
            name="create_primitive",
            version="1.0.0",
            description="Create an advanced primitive",
            category="mesh",
            handler="src.tools.mesh.primitives.create_primitive",
            params=["primitive_type", "params"],
            required_params=["primitive_type"],
        )
    )

    registry.register(
        ToolInfo(
            name="apply_boolean",
            version="1.0.0",
            description="Apply boolean operation",
            category="mesh",
            handler="src.tools.mesh.boolean.apply_boolean",
            params=["obj_name", "target_name", "operation"],
            required_params=["obj_name", "target_name", "operation"],
        )
    )

    # ═══ RIGGING TOOLS ═══
    registry.register(
        ToolInfo(
            name="create_armature",
            version="1.0.0",
            description="Create an armature from template",
            category="rigging",
            handler="src.tools.rigging.armature.create_armature",
            params=["rig_type", "params"],
            required_params=["rig_type"],
        )
    )

    # ═══ ANIMATION TOOLS ═══
    registry.register(
        ToolInfo(
            name="create_animation",
            version="1.0.0",
            description="Create animation on object",
            category="animation",
            handler="src.tools.animation.create.create_animation",
            params=["obj_name", "anim_type", "params"],
            required_params=["obj_name", "anim_type"],
        )
    )

    # ═══ EXPORT TOOLS ═══
    registry.register(
        ToolInfo(
            name="export_scene",
            version="1.0.0",
            description="Export scene to file",
            category="io",
            handler="src.tools.io.export.export_scene",
            params=["filepath", "format", "params"],
            required_params=["filepath", "format"],
        )
    )

    # ═══ GEOMETRY NODES TOOLS ═══
    registry.register(
        ToolInfo(
            name="apply_geometry_nodes",
            version="1.0.0",
            description="Apply geometry nodes modifier",
            category="geometry_nodes",
            handler="src.tools.geometry_nodes.apply.apply_geometry_nodes",
            params=["obj_name", "node_group", "params"],
            required_params=["obj_name", "node_group"],
        )
    )


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def list_tools(category: str = None) -> list[dict[str, Any]]:
    """List all tools (convenience function)."""
    return get_registry().list_tools(category)


def get_tool_info(name: str, version: str = None) -> ToolInfo | None:
    """Get tool info (convenience function)."""
    return get_registry().get(name, version)


def get_tool_handler(name: str, version: str = None) -> str | None:
    """Get tool handler path (convenience function)."""
    return get_registry().get_handler(name, version)
