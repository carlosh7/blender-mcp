"""
blender-mcp-ultra — Modifier Tools
Tools for modifier management.
"""
from typing import Any, Dict, List, Optional
from core.entities import Tool, ToolCategory, ToolPermission


# Tool definitions
TOOLS = [
    Tool(
        name="modifier.add",
        category=ToolCategory.MODIFIERS,
        description="Add a modifier to an object",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "type": {"type": "str", "required": True, "description": "Modifier type"},
            "name": {"type": "str", "default": None, "description": "Modifier name"},
        },
        examples=[
            "modifier.add(object_name='Cube', type='SUBSURF')",
            "modifier.add(object_name='Cube', type='BEVEL', name='MyBevel')",
        ],
    ),
    Tool(
        name="modifier.remove",
        category=ToolCategory.MODIFIERS,
        description="Remove a modifier from an object",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "modifier_name": {"type": "str", "required": True, "description": "Modifier name"},
        },
        examples=[
            "modifier.remove(object_name='Cube', modifier_name='MyBevel')",
        ],
    ),
    Tool(
        name="modifier.apply",
        category=ToolCategory.MODIFIERS,
        description="Apply a modifier",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "modifier_name": {"type": "str", "required": True, "description": "Modifier name"},
        },
        examples=[
            "modifier.apply(object_name='Cube', modifier_name='Subsurf')",
        ],
    ),
    Tool(
        name="modifier.list",
        category=ToolCategory.MODIFIERS,
        description="List modifiers on an object",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
        },
        examples=[
            "modifier.list(object_name='Cube')",
        ],
    ),
    Tool(
        name="modifier.update",
        category=ToolCategory.MODIFIERS,
        description="Update modifier properties",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "modifier_name": {"type": "str", "required": True, "description": "Modifier name"},
            "properties": {"type": "dict", "required": True, "description": "Properties to update"},
        },
        examples=[
            "modifier.update(object_name='Cube', modifier_name='Subsurf', properties={'levels': 3})",
        ],
    ),
    Tool(
        name="modifier.types",
        category=ToolCategory.MODIFIERS,
        description="List available modifier types",
        permission=ToolPermission.READ_ONLY,
        parameters={},
        examples=[
            "modifier.types()",
        ],
    ),
]


def add(
    object_name: str,
    type: str,
    name: str = None,
) -> Dict[str, Any]:
    """Add a modifier to an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        # Add modifier
        mod = obj.modifiers.new(name=name or type, type=type)
        
        return {
            'success': True,
            'object': object_name,
            'modifier': mod.name,
            'type': type,
        }
        
    except Exception as e:
        return {'error': str(e)}


def remove(
    object_name: str,
    modifier_name: str,
) -> Dict[str, Any]:
    """Remove a modifier from an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        mod = obj.modifiers.get(modifier_name)
        if not mod:
            return {'error': f'Modifier not found: {modifier_name}'}
        
        obj.modifiers.remove(mod)
        
        return {
            'success': True,
            'object': object_name,
            'modifier': modifier_name,
        }
        
    except Exception as e:
        return {'error': str(e)}


def apply(
    object_name: str,
    modifier_name: str,
) -> Dict[str, Any]:
    """Apply a modifier."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        mod = obj.modifiers.get(modifier_name)
        if not mod:
            return {'error': f'Modifier not found: {modifier_name}'}
        
        # Apply modifier
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        
        return {
            'success': True,
            'object': object_name,
            'modifier': modifier_name,
        }
        
    except Exception as e:
        return {'error': str(e)}


def list_modifiers(object_name: str) -> Dict[str, Any]:
    """List modifiers on an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        modifiers = []
        for mod in obj.modifiers:
            modifiers.append({
                'name': mod.name,
                'type': mod.type,
                'show_viewport': mod.show_viewport,
                'show_render': mod.show_render,
            })
        
        return {
            'object': object_name,
            'count': len(modifiers),
            'modifiers': modifiers,
        }
        
    except Exception as e:
        return {'error': str(e)}


def update(
    object_name: str,
    modifier_name: str,
    properties: Dict[str, Any],
) -> Dict[str, Any]:
    """Update modifier properties."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        mod = obj.modifiers.get(modifier_name)
        if not mod:
            return {'error': f'Modifier not found: {modifier_name}'}
        
        updated = []
        for prop, value in properties.items():
            if hasattr(mod, prop):
                setattr(mod, prop, value)
                updated.append(prop)
        
        return {
            'success': True,
            'object': object_name,
            'modifier': modifier_name,
            'updated': updated,
        }
        
    except Exception as e:
        return {'error': str(e)}


def types() -> Dict[str, Any]:
    """List available modifier types."""
    try:
        import bpy
        
        # Get all modifier types
        modifier_types = [
            ('ARRAY', 'Array', 'Generate'),
            ('BEVEL', 'Bevel', 'Generate'),
            ('BOOLEAN', 'Boolean', 'Generate'),
            ('BUILD', 'Build', 'Generate'),
            ('DECIMATE', 'Decimate', 'Generate'),
            ('EDGE_SPLIT', 'Edge Split', 'Generate'),
            ('MASK', 'Mask', 'Generate'),
            ('MIRROR', 'Mirror', 'Generate'),
            ('MULTIRES', 'Multiresolution', 'Generate'),
            ('REMESH', 'Remesh', 'Generate'),
            ('SCREW', 'Screw', 'Generate'),
            ('SKIN', 'Skin', 'Generate'),
            ('SOLIDIFY', 'Solidify', 'Generate'),
            ('SUBSURF', 'Subdivision Surface', 'Generate'),
            ('TRIANGULATE', 'Triangulate', 'Generate'),
            ('WELD', 'Weld', 'Generate'),
            ('WIREFRAME', 'Wireframe', 'Generate'),
            ('ARMATURE', 'Armature', 'Deform'),
            ('CAST', 'Cast', 'Deform'),
            ('CURVE', 'Curve', 'Deform'),
            ('DISPLACE', 'Displace', 'Deform'),
            ('HOOK', 'Hook', 'Deform'),
            ('LATTICE', 'Lattice', 'Deform'),
            ('MESH_DEFORM', 'Mesh Deform', 'Deform'),
            ('SHRINKWRAP', 'Shrinkwrap', 'Deform'),
            ('SIMPLE_DEFORM', 'Simple Deform', 'Deform'),
            ('SMOOTH', 'Smooth', 'Deform'),
            ('CORRECTIVE_SMOOTH', 'Corrective Smooth', 'Deform'),
            ('LAPLACIAN_SMOOTH', 'Laplacian Smooth', 'Deform'),
            ('SURFACE_DEFORM', 'Surface Deform', 'Deform'),
            ('WARP', 'Warp', 'Deform'),
            ('WAVE', 'Wave', 'Deform'),
            ('CLOTH', 'Cloth', 'Physics'),
            ('COLLISION', 'Collision', 'Physics'),
            ('DYNAMIC_PAINT', 'Dynamic Paint', 'Physics'),
            ('EXPLODE', 'Explode', 'Physics'),
            ('FLUID', 'Fluid', 'Physics'),
            ('OCEAN', 'Ocean', 'Physics'),
            ('PARTICLE_SYSTEM', 'Particle System', 'Physics'),
            ('SOFT_BODY', 'Soft Body', 'Physics'),
        ]
        
        return {
            'count': len(modifier_types),
            'types': [
                {'id': t[0], 'name': t[1], 'category': t[2]}
                for t in modifier_types
            ],
        }
        
    except ImportError:
        return {'error': 'Blender not available'}


# Handler mapping
HANDLERS = {
    'modifier.add': add,
    'modifier.remove': remove,
    'modifier.apply': apply,
    'modifier.list': list_modifiers,
    'modifier.update': update,
    'modifier.types': types,
}
