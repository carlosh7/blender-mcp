"""
blender-mcp-ultra — Light Tools
Tools for light management.
"""
from typing import Any, Dict, List, Optional, Tuple
from core.entities import Tool, ToolCategory, ToolPermission


# Tool definitions
TOOLS = [
    Tool(
        name="light.create",
        category=ToolCategory.LIGHTS,
        description="Create a new light",
        permission=ToolPermission.WRITE,
        parameters={
            "type": {"type": "str", "required": True, "description": "Light type (POINT, SUN, SPOT, AREA)"},
            "name": {"type": "str", "default": None, "description": "Light name"},
            "location": {"type": "tuple", "default": (0, 0, 5), "description": "Light location"},
            "energy": {"type": "float", "default": 1000.0, "description": "Light energy"},
            "color": {"type": "tuple", "default": (1, 1, 1), "description": "Light color (RGB)"},
        },
        examples=[
            "light.create(type='POINT', name='KeyLight', location=(3, -3, 5))",
            "light.create(type='SUN', energy=5, color=(1, 0.95, 0.9))",
        ],
    ),
    Tool(
        name="light.delete",
        category=ToolCategory.LIGHTS,
        description="Delete a light",
        permission=ToolPermission.DESTRUCTIVE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Light name"},
        },
        examples=[
            "light.delete(name='KeyLight')",
        ],
    ),
    Tool(
        name="light.three_point",
        category=ToolCategory.LIGHTS,
        description="Setup three-point lighting",
        permission=ToolPermission.WRITE,
        parameters={
            "key_energy": {"type": "float", "default": 1000, "description": "Key light energy"},
            "fill_energy": {"type": "float", "default": 500, "description": "Fill light energy"},
            "rim_energy": {"type": "float", "default": 800, "description": "Rim light energy"},
            "distance": {"type": "float", "default": 5, "description": "Distance from center"},
        },
        examples=[
            "light.three_point()",
            "light.three_point(key_energy=2000, distance=10)",
        ],
    ),
    Tool(
        name="light.update",
        category=ToolCategory.LIGHTS,
        description="Update light properties",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Light name"},
            "energy": {"type": "float", "default": None, "description": "New energy"},
            "color": {"type": "tuple", "default": None, "description": "New color (RGB)"},
            "size": {"type": "float", "default": None, "description": "New size"},
        },
        examples=[
            "light.update(name='KeyLight', energy=2000, color=(1, 0.9, 0.8))",
        ],
    ),
    Tool(
        name="light.list",
        category=ToolCategory.LIGHTS,
        description="List all lights in the scene",
        permission=ToolPermission.READ_ONLY,
        parameters={},
        examples=[
            "light.list()",
        ],
    ),
]


def create(
    type: str,
    name: str = None,
    location: Tuple[float, float, float] = (0, 0, 5),
    energy: float = 1000.0,
    color: Tuple[float, float, float] = (1, 1, 1),
) -> Dict[str, Any]:
    """Create a new light."""
    try:
        import bpy
        
        # Map type string to Blender type
        type_map = {
            'POINT': 'POINT',
            'SUN': 'SUN',
            'SPOT': 'SPOT',
            'AREA': 'AREA',
        }
        
        blender_type = type_map.get(type.upper())
        if not blender_type:
            return {'error': f'Invalid light type: {type}'}
        
        # Create light
        bpy.ops.object.light_add(type=blender_type, location=location)
        light_obj = getattr(bpy.context, "active_object", None)
        if light_obj is None and getattr(bpy.context, "selected_objects", []):
            light_obj = getattr(bpy.context, "selected_objects", [])[0]
        if light_obj is None:
            for o in reversed(bpy.data.objects):
                if o.type == 'LIGHT':
                    light_obj = o
                    break
        if light_obj is None:
            return {'error': 'Failed to create light'}
        
        if name:
            light_obj.name = name
        
        # Set light properties
        light = light_obj.data
        light.energy = energy
        light.color = color[:3]
        
        return {
            'success': True,
            'name': light_obj.name,
            'type': blender_type,
            'energy': energy,
            'color': [c for c in color[:3]],
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


def delete(name: str) -> Dict[str, Any]:
    """Delete a light."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(name)
        if not obj or obj.type != 'LIGHT':
            return {'error': f'Light not found: {name}'}
        
        bpy.data.objects.remove(obj, do_unlink=True)
        
        return {'success': True, 'name': name}
        
    except ImportError:
        return {'error': 'Blender not available'}


def three_point(
    key_energy: float = 1000,
    fill_energy: float = 500,
    rim_energy: float = 800,
    distance: float = 5,
) -> Dict[str, Any]:
    """Setup three-point lighting."""
    try:
        import bpy
        
        # Clear existing lights
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT':
                obj.select_set(True)
        bpy.ops.object.delete()
        
        # Create key light
        bpy.ops.object.light_add(type='AREA', location=(distance, -distance, distance))
        key = getattr(bpy.context, "active_object", None)
        if key:
            key.name = 'KeyLight'
            key.data.energy = key_energy
            key.data.size = 2
        
        # Create fill light
        bpy.ops.object.light_add(type='AREA', location=(-distance, -distance, distance/2))
        fill = getattr(bpy.context, "active_object", None)
        if fill:
            fill.name = 'FillLight'
            fill.data.energy = fill_energy
            fill.data.size = 3
            fill.data.color = (0.9, 0.95, 1.0)
        
        # Create rim light
        bpy.ops.object.light_add(type='AREA', location=(0, distance, distance))
        rim = getattr(bpy.context, "active_object", None)
        if rim:
            rim.name = 'RimLight'
            rim.data.energy = rim_energy
            rim.data.size = 1.5
        
        return {
            'success': True,
            'key': {'name': 'KeyLight', 'energy': key_energy},
            'fill': {'name': 'FillLight', 'energy': fill_energy},
            'rim': {'name': 'RimLight', 'energy': rim_energy},
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


def update(
    name: str,
    energy: float = None,
    color: Tuple[float, float, float] = None,
    size: float = None,
) -> Dict[str, Any]:
    """Update light properties."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(name)
        if not obj or obj.type != 'LIGHT':
            return {'error': f'Light not found: {name}'}
        
        light = obj.data
        updated = []
        
        if energy is not None:
            light.energy = energy
            updated.append('energy')
        
        if color is not None:
            light.color = color[:3]
            updated.append('color')
        
        if size is not None:
            light.size = size
            updated.append('size')
        
        return {
            'success': True,
            'name': name,
            'updated': updated,
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


def list_lights() -> Dict[str, Any]:
    """List all lights in the scene."""
    try:
        import bpy
        
        lights = []
        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT':
                lights.append({
                    'name': obj.name,
                    'type': obj.data.type,
                    'energy': obj.data.energy,
                    'color': [c for c in obj.data.color],
                    'location': [obj.location.x, obj.location.y, obj.location.z],
                })
        
        return {
            'count': len(lights),
            'lights': lights,
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


# Handler mapping
HANDLERS = {
    'light.create': create,
    'light.delete': delete,
    'light.three_point': three_point,
    'light.update': update,
    'light.list': list_lights,
}
