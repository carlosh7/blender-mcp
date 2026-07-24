"""
blender-mcp-ultra — Object Tools
Tools for object management.
"""
from typing import Any, Dict, List, Optional, Tuple
from core.entities import Tool, ToolCategory, ToolPermission


# Tool definitions
TOOLS = [
    Tool(
        name="object.create",
        category=ToolCategory.OBJECTS,
        description="Create a new object",
        permission=ToolPermission.WRITE,
        parameters={
            "type": {"type": "str", "required": True, "description": "Object type (MESH, CURVE, LIGHT, CAMERA)"},
            "name": {"type": "str", "default": None, "description": "Object name"},
            "location": {"type": "tuple", "default": (0, 0, 0), "description": "Object location"},
        },
        examples=[
            "object.create(type='MESH', name='Cube')",
            "object.create(type='LIGHT', name='Sun', location=(0, 0, 5))",
        ],
    ),
    Tool(
        name="object.delete",
        category=ToolCategory.OBJECTS,
        description="Delete an object",
        permission=ToolPermission.DESTRUCTIVE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Object name"},
        },
        examples=[
            "object.delete(name='Cube')",
        ],
    ),
    Tool(
        name="object.select",
        category=ToolCategory.OBJECTS,
        description="Select objects",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "name": {"type": "str", "default": None, "description": "Object name"},
            "type": {"type": "str", "default": None, "description": "Object type"},
            "all": {"type": "bool", "default": False, "description": "Select all objects"},
        },
        examples=[
            "object.select(name='Cube')",
            "object.select(type='MESH')",
            "object.select(all=True)",
        ],
    ),
    Tool(
        name="object.transform",
        category=ToolCategory.OBJECTS,
        description="Transform an object (move, rotate, scale)",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Object name"},
            "location": {"type": "tuple", "default": None, "description": "New location"},
            "rotation": {"type": "tuple", "default": None, "description": "New rotation (Euler)"},
            "scale": {"type": "tuple", "default": None, "description": "New scale"},
        },
        examples=[
            "object.transform(name='Cube', location=(1, 2, 3))",
            "object.transform(name='Cube', rotation=(0, 0, 1.57))",
            "object.transform(name='Cube', scale=(2, 2, 2))",
        ],
    ),
    Tool(
        name="object.duplicate",
        category=ToolCategory.OBJECTS,
        description="Duplicate an object",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Object name"},
            "new_name": {"type": "str", "default": None, "description": "New object name"},
            "linked": {"type": "bool", "default": False, "description": "Create linked duplicate"},
        },
        examples=[
            "object.duplicate(name='Cube')",
            "object.duplicate(name='Cube', new_name='Cube.001', linked=True)",
        ],
    ),
    Tool(
        name="object.join",
        category=ToolCategory.OBJECTS,
        description="Join multiple objects",
        permission=ToolPermission.WRITE,
        parameters={
            "names": {"type": "list", "required": True, "description": "List of object names"},
        },
        examples=[
            "object.join(names=['Cube', 'Cube.001', 'Cube.002'])",
        ],
    ),
    Tool(
        name="object.get_info",
        category=ToolCategory.OBJECTS,
        description="Get information about an object",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "name": {"type": "str", "required": True, "description": "Object name"},
        },
        examples=[
            "object.get_info(name='Cube')",
        ],
    ),
    Tool(
        name="object.list",
        category=ToolCategory.OBJECTS,
        description="List all objects in the scene",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "type": {"type": "str", "default": None, "description": "Filter by type"},
        },
        examples=[
            "object.list()",
            "object.list(type='MESH')",
        ],
    ),
]


def create(type: str, name: str = None, location: Tuple[float, float, float] = (0, 0, 0)) -> Dict[str, Any]:
    """Create a new object."""
    try:
        import bpy
        
        # Map type string to Blender type
        type_map = {
            'MESH': 'MESH',
            'CURVE': 'CURVE',
            'SURFACE': 'SURFACE',
            'META': 'META',
            'FONT': 'FONT',
            'ARMATURE': 'ARMATURE',
            'LATTICE': 'LATTICE',
            'EMPTY': 'EMPTY',
            'LIGHT': 'LIGHT',
            'LIGHT_PROBE': 'LIGHT_PROBE',
            'CAMERA': 'CAMERA',
            'SPEAKER': 'SPEAKER',
        }
        
        blender_type = type_map.get(type.upper())
        if not blender_type:
            return {'error': f'Invalid object type: {type}'}
        
        # Create object
        bpy.ops.object.add(type=blender_type, location=location)
        obj = bpy.context.active_object
        
        if name:
            obj.name = name
        
        return {
            'success': True,
            'name': obj.name,
            'type': obj.type,
            'location': list(obj.location),
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


def delete(name: str) -> Dict[str, Any]:
    """Delete an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(name)
        if not obj:
            return {'error': f'Object not found: {name}'}
        
        bpy.data.objects.remove(obj, do_unlink=True)
        
        return {'success': True, 'name': name}
        
    except ImportError:
        return {'error': 'Blender not available'}


def select(
    name: str = None,
    type: str = None,
    all: bool = False,
) -> Dict[str, Any]:
    """Select objects."""
    try:
        import bpy
        
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        
        selected = []
        
        if name:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                selected.append(name)
        elif type:
            for obj in bpy.data.objects:
                if obj.type == type.upper():
                    obj.select_set(True)
                    selected.append(obj.name)
        elif all:
            bpy.ops.object.select_all(action='SELECT')
            selected = [obj.name for obj in bpy.context.selected_objects]
        
        return {'success': True, 'selected': selected}
        
    except ImportError:
        return {'error': 'Blender not available'}


def transform(
    name: str,
    location: Tuple[float, float, float] = None,
    rotation: Tuple[float, float, float] = None,
    scale: Tuple[float, float, float] = None,
) -> Dict[str, Any]:
    """Transform an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(name)
        if not obj:
            return {'error': f'Object not found: {name}'}
        
        if location is not None:
            obj.location = location
        if rotation is not None:
            obj.rotation_euler = rotation
        if scale is not None:
            obj.scale = scale
        
        return {
            'success': True,
            'name': name,
            'location': list(obj.location),
            'rotation': list(obj.rotation_euler),
            'scale': list(obj.scale),
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


def duplicate(
    name: str,
    new_name: str = None,
    linked: bool = False,
) -> Dict[str, Any]:
    """Duplicate an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(name)
        if not obj:
            return {'error': f'Object not found: {name}'}
        
        # Select the object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Duplicate
        bpy.ops.object.duplicate(linked=linked)
        
        new_obj = bpy.context.active_object
        if new_name:
            new_obj.name = new_name
        
        return {
            'success': True,
            'original': name,
            'new_name': new_obj.name,
            'linked': linked,
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


def join(names: List[str]) -> Dict[str, Any]:
    """Join multiple objects."""
    try:
        import bpy
        
        # Select objects to join
        bpy.ops.object.select_all(action='DESELECT')
        
        objects = []
        for name in names:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
                objects.append(name)
        
        if len(objects) < 2:
            return {'error': 'Need at least 2 objects to join'}
        
        # Join
        bpy.context.view_layer.objects.active = bpy.data.objects[objects[0]]
        bpy.ops.object.join()
        
        return {
            'success': True,
            'joined': objects,
            'result': bpy.context.active_object.name,
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


def get_info(name: str) -> Dict[str, Any]:
    """Get information about an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(name)
        if not obj:
            return {'error': f'Object not found: {name}'}
        
        return {
            'name': obj.name,
            'type': obj.type,
            'location': list(obj.location),
            'rotation': list(obj.rotation_euler),
            'scale': list(obj.scale),
            'dimensions': list(obj.dimensions),
            'parent': obj.parent.name if obj.parent else None,
            'material': obj.data.materials[0].name if obj.data and obj.data.materials else None,
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


def list(type: str = None) -> Dict[str, Any]:
    """List all objects in the scene."""
    try:
        import bpy
        
        objects = []
        for obj in bpy.context.scene.objects:
            if type and obj.type != type.upper():
                continue
            objects.append({
                'name': obj.name,
                'type': obj.type,
                'location': list(obj.location),
            })
        
        return {
            'count': len(objects),
            'objects': objects,
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


# Handler mapping
HANDLERS = {
    'object.create': create,
    'object.delete': delete,
    'object.select': select,
    'object.transform': transform,
    'object.duplicate': duplicate,
    'object.join': join,
    'object.get_info': get_info,
    'object.list': list,
}
