"""
blender-mcp-ultra — Core Entities
Domain objects for the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ToolCategory(Enum):
    """Tool categories."""

    SCENE = "scene"
    OBJECTS = "objects"
    MATERIALS = "materials"
    SHADER_NODES = "shader_nodes"
    LIGHTS = "lights"
    MODIFIERS = "modifiers"
    ANIMATION = "animation"
    GEOMETRY_NODES = "geometry_nodes"
    CAMERA = "camera"
    RENDER = "render"
    IO = "io"
    UV_TEXTURE = "uv_texture"
    RIGGING = "rigging"
    BATCH = "batch"
    SCENE_UTILS = "scene_utils"
    PRINTING = "printing"


class ToolPermission(Enum):
    """Tool permission levels."""

    READ_ONLY = "read_only"
    WRITE = "write"
    DESTRUCTIVE = "destructive"


@dataclass
class Tool:
    """Tool definition."""

    name: str
    category: ToolCategory
    description: str
    permission: ToolPermission
    parameters: dict[str, Any] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "permission": self.permission.value,
            "parameters": self.parameters,
            "examples": self.examples,
            "version": self.version,
        }


@dataclass
class ToolResult:
    """Result of tool execution."""

    success: bool
    data: Any = None
    error: str | None = None
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
        }


@dataclass
class Scene:
    """Scene information."""

    name: str
    object_count: int
    objects: list["Object"] = field(default_factory=list)
    materials: list["Material"] = field(default_factory=list)
    camera_count: int = 0
    light_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "object_count": self.object_count,
            "objects": [o.to_dict() for o in self.objects],
            "materials": [m.to_dict() for m in self.materials],
            "camera_count": self.camera_count,
            "light_count": self.light_count,
        }


@dataclass
class Object:
    """Blender object."""

    name: str
    type: str
    location: tuple = (0.0, 0.0, 0.0)
    rotation: tuple = (0.0, 0.0, 0.0)
    scale: tuple = (1.0, 1.0, 1.0)
    dimensions: tuple = (0.0, 0.0, 0.0)
    material_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "location": list(self.location),
            "rotation": list(self.rotation),
            "scale": list(self.scale),
            "dimensions": list(self.dimensions),
            "material_name": self.material_name,
        }


@dataclass
class Material:
    """Blender material."""

    name: str
    color: tuple = (0.8, 0.8, 0.8, 1.0)
    metallic: float = 0.0
    roughness: float = 0.5
    nodes_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "color": list(self.color),
            "metallic": self.metallic,
            "roughness": self.roughness,
            "nodes_count": self.nodes_count,
        }


@dataclass
class Config:
    """Application configuration."""

    version: str = "1.0.0"
    blender_version_min: str = "4.0.0"
    blender_version_max: str = "6.0.0"
    python_version_min: str = "3.10"
    python_version_max: str = "3.12"

    # Security settings
    ast_validation: bool = True
    sandbox_mode: bool = True
    rate_limit_per_minute: int = 60
    timeout_seconds: int = 30

    # Feature flags
    enable_lazy_loading: bool = True
    enable_cache: bool = True
    enable_telemetry: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "blender_version_min": self.blender_version_min,
            "blender_version_max": self.blender_version_max,
            "python_version_min": self.python_version_min,
            "python_version_max": self.python_version_max,
            "ast_validation": self.ast_validation,
            "sandbox_mode": self.sandbox_mode,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "timeout_seconds": self.timeout_seconds,
            "enable_lazy_loading": self.enable_lazy_loading,
            "enable_cache": self.enable_cache,
            "enable_telemetry": self.enable_telemetry,
        }
