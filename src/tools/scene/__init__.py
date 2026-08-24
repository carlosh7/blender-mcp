"""
blender-mcp-ultra — Scene Tools
Tools for scene management.
"""

from typing import Any, Dict, List

from ...core.entities import Tool, ToolCategory, ToolPermission

# Tool definitions
TOOLS = [
    Tool(
        name="scene.get_info",
        category=ToolCategory.SCENE,
        description="Get information about the current scene",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "include_objects": {
                "type": "bool",
                "default": True,
                "description": "Include object list",
            },
            "include_materials": {
                "type": "bool",
                "default": False,
                "description": "Include material list",
            },
        },
        examples=[
            "scene.get_info()",
            "scene.get_info(include_objects=True, include_materials=True)",
        ],
    ),
    Tool(
        name="scene.query",
        category=ToolCategory.SCENE,
        description="Buscar objetos por nombre/tipo/distancia (el grep de la escena)",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "name_contains": {"type": "str", "description": "Subcadena del nombre"},
            "name_regex": {"type": "str", "description": "Regex sobre el nombre"},
            "obj_type": {"type": "str", "description": "MESH/LIGHT/CAMERA/..."},
            "near": {"type": "list", "description": "[x,y,z] centro de búsqueda"},
            "max_distance": {"type": "float"},
            "limit": {"type": "int"},
        },
        examples=["scene.query(name_contains='Cube')"],
    ),
    Tool(
        name="scene.create",
        category=ToolCategory.SCENE,
        description="Create a new scene",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Scene name"},
        },
        examples=[
            "scene.create(name='MyScene')",
        ],
    ),
    Tool(
        name="scene.delete",
        category=ToolCategory.SCENE,
        description="Delete a scene",
        permission=ToolPermission.DESTRUCTIVE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Scene name"},
        },
        examples=[
            "scene.delete(name='MyScene')",
        ],
    ),
    Tool(
        name="scene.set_active",
        category=ToolCategory.SCENE,
        description="Set the active scene",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Scene name"},
        },
        examples=[
            "scene.set_active(name='MyScene')",
        ],
    ),
    Tool(
        name="scene.render_settings",
        category=ToolCategory.SCENE,
        description="Get or set render settings",
        permission=ToolPermission.WRITE,
        parameters={
            "engine": {
                "type": "str",
                "default": None,
                "description": "Render engine (CYCLES, EEVEE)",
            },
            "samples": {"type": "int", "default": None, "description": "Render samples"},
            "resolution_x": {"type": "int", "default": None, "description": "Resolution X"},
            "resolution_y": {"type": "int", "default": None, "description": "Resolution Y"},
        },
        examples=[
            "scene.render_settings()",
            "scene.render_settings(engine='CYCLES', samples=128)",
        ],
    ),
]


def query(
    name_contains: str = "",
    name_regex: str = "",
    obj_type: str = "",
    near: list = None,
    max_distance: float = 1.0,
    limit: int = 50,
) -> dict[str, Any]:
    """Buscar objetos por nombre/tipo/distancia — el 'grep' de la escena."""
    import re

    import bpy
    from mathutils import Vector

    results = []
    rx = re.compile(name_regex) if name_regex else None
    origin = Vector(near) if near else None
    for obj in bpy.context.scene.objects:
        if name_contains and name_contains.lower() not in obj.name.lower():
            continue
        if rx and not rx.search(obj.name):
            continue
        if obj_type and obj.type != obj_type.upper():
            continue
        entry: dict[str, Any] = {
            "name": obj.name,
            "type": obj.type,
            "location": [round(c, 4) for c in obj.location],
        }
        if origin is not None:
            entry["distance"] = round((obj.location - origin).length, 4)
            if entry["distance"] > float(max_distance):
                continue
        results.append(entry)
        if len(results) >= int(limit):
            break
    return {"matches": len(results), "objects": results}


def get_info(include_objects: bool = True, include_materials: bool = False) -> dict[str, Any]:
    """Get scene information."""
    try:
        import bpy

        scene = bpy.context.scene

        result = {
            "name": scene.name,
            "object_count": len(scene.objects),
            "camera_count": sum(1 for o in scene.objects if o.type == "CAMERA"),
            "light_count": sum(1 for o in scene.objects if o.type == "LIGHT"),
        }

        if include_objects:
            result["objects"] = [
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": list(obj.location),
                }
                for obj in scene.objects
            ]

        if include_materials:
            result["materials"] = [
                {
                    "name": mat.name,
                    "use_nodes": mat.use_nodes,
                }
                for mat in bpy.data.materials
            ]

        return result

    except ImportError:
        return {"error": "Blender not available"}


def create(name: str) -> dict[str, Any]:
    """Create a new scene."""
    try:
        import bpy

        # Check if scene exists
        if name in bpy.data.scenes:
            return {"error": f"Scene already exists: {name}"}

        # Create new scene
        bpy.data.scenes.new(name)

        return {"success": True, "name": name}

    except ImportError:
        return {"error": "Blender not available"}


def delete(name: str) -> dict[str, Any]:
    """Delete a scene."""
    try:
        import bpy

        # Can't delete the last scene
        if len(bpy.data.scenes) <= 1:
            return {"error": "Cannot delete the last scene"}

        # Check if scene exists
        scene = bpy.data.scenes.get(name)
        if not scene:
            return {"error": f"Scene not found: {name}"}

        # Delete scene
        bpy.data.scenes.remove(scene)

        return {"success": True, "name": name}

    except ImportError:
        return {"error": "Blender not available"}


def set_active(name: str) -> dict[str, Any]:
    """Set the active scene."""
    try:
        import bpy

        # Check if scene exists
        scene = bpy.data.scenes.get(name)
        if not scene:
            return {"error": f"Scene not found: {name}"}

        # Set as active
        bpy.context.window.scene = scene

        return {"success": True, "name": name}

    except ImportError:
        return {"error": "Blender not available"}


def render_settings(
    engine: str = None,
    samples: int = None,
    resolution_x: int = None,
    resolution_y: int = None,
) -> dict[str, Any]:
    """Get or set render settings."""
    try:
        import bpy

        scene = bpy.context.scene

        # Get current settings
        result = {
            "engine": scene.render.engine,
            "samples": scene.cycles.samples if scene.render.engine == "CYCLES" else None,
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
        }

        # Apply new settings
        if engine:
            engine_map = {
                "BLENDER_EEVEE_NEXT": "BLENDER_EEVEE",
                "EEVEE": "BLENDER_EEVEE",
                "EEVEE_NEXT": "BLENDER_EEVEE",
                "CYCLES": "CYCLES",
            }
            scene.render.engine = engine_map.get(engine, engine)
            result["engine"] = scene.render.engine

        if samples is not None and scene.render.engine == "CYCLES":
            scene.cycles.samples = samples
            result["samples"] = samples

        if resolution_x is not None:
            scene.render.resolution_x = resolution_x
            result["resolution_x"] = resolution_x

        if resolution_y is not None:
            scene.render.resolution_y = resolution_y
            result["resolution_y"] = resolution_y

        return result

    except ImportError:
        return {"error": "Blender not available"}


# Handler mapping
HANDLERS = {
    "scene.get_info": get_info,
    "scene.query": query,
    "scene.create": create,
    "scene.delete": delete,
    "scene.set_active": set_active,
    "scene.render_settings": render_settings,
}
