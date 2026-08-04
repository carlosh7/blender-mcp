"""
blender-mcp-ultra — Animation Tools
Tools for animation management.
"""
from typing import Any, Dict, List, Optional, Tuple
from core.entities import Tool, ToolCategory, ToolPermission


# Tool definitions
TOOLS = [
    Tool(
        name="animation.keyframe_insert",
        category=ToolCategory.ANIMATION,
        description="Insert a keyframe for an object property",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "property": {"type": "str", "required": True, "description": "Property to keyframe"},
            "frame": {"type": "int", "default": None, "description": "Frame number"},
        },
        examples=[
            "animation.keyframe_insert(object_name='Cube', property='location', frame=1)",
        ],
    ),
    Tool(
        name="animation.keyframe_delete",
        category=ToolCategory.ANIMATION,
        description="Delete keyframes for a property",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "property": {"type": "str", "required": True, "description": "Property name"},
        },
        examples=[
            "animation.keyframe_delete(object_name='Cube', property='location')",
        ],
    ),
    Tool(
        name="animation.set_keyframe",
        category=ToolCategory.ANIMATION,
        description="Set a keyframe value at a specific frame",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "property": {"type": "str", "required": True, "description": "Property name"},
            "frame": {"type": "int", "required": True, "description": "Frame number"},
            "value": {"required": True, "description": "Keyframe value"},
        },
        examples=[
            "animation.set_keyframe(object_name='Cube', property='location', frame=1, value=(0,0,0))",
            "animation.set_keyframe(object_name='Cube', property='location', frame=50, value=(5,0,3))",
        ],
    ),
    Tool(
        name="animation.get_fcurves",
        category=ToolCategory.ANIMATION,
        description="Get F-Curves for an object",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
        },
        examples=[
            "animation.get_fcurves(object_name='Cube')",
        ],
    ),
    Tool(
        name="animation.set_interpolation",
        category=ToolCategory.ANIMATION,
        description="Set interpolation mode for F-Curves",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "interpolation": {"type": "str", "required": True, "description": "Interpolation mode"},
        },
        examples=[
            "animation.set_interpolation(object_name='Cube', interpolation='BEZIER')",
        ],
    ),
    Tool(
        name="animation.play",
        category=ToolCategory.ANIMATION,
        description="Play animation",
        permission=ToolPermission.WRITE,
        parameters={
            "start": {"type": "int", "default": None, "description": "Start frame"},
            "end": {"type": "int", "default": None, "description": "End frame"},
        },
        examples=[
            "animation.play()",
            "animation.play(start=1, end=100)",
        ],
    ),
    Tool(
        name="animation.stop",
        category=ToolCategory.ANIMATION,
        description="Stop animation",
        permission=ToolPermission.WRITE,
        parameters={},
        examples=[
            "animation.stop()",
        ],
    ),
    Tool(
        name="animation.clear",
        category=ToolCategory.ANIMATION,
        description="Clear all animation data from an object",
        permission=ToolPermission.DESTRUCTIVE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
        },
        examples=[
            "animation.clear(object_name='Cube')",
        ],
    ),
]


def keyframe_insert(
    object_name: str,
    property: str,
    frame: int = None,
) -> Dict[str, Any]:
    """Insert a keyframe for an object property."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        if frame is None:
            frame = bpy.context.scene.frame_current
        
        # Insert keyframe
        obj.keyframe_insert(data_path=property, frame=frame)
        
        return {
            'success': True,
            'object': object_name,
            'property': property,
            'frame': frame,
        }
        
    except Exception as e:
        return {'error': str(e)}


def keyframe_delete(
    object_name: str,
    property: str,
) -> Dict[str, Any]:
    """Delete keyframes for a property."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        obj.keyframe_delete(data_path=property)
        
        return {
            'success': True,
            'object': object_name,
            'property': property,
        }
        
    except Exception as e:
        return {'error': str(e)}


def set_keyframe(
    object_name: str,
    property: str,
    frame: int,
    value: Any,
) -> Dict[str, Any]:
    """Set a keyframe value at a specific frame."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        # Set value
        if isinstance(value, (list, tuple)):
            setattr(obj, property, value)
        else:
            setattr(obj, property, value)
        
        # Insert keyframe
        obj.keyframe_insert(data_path=property, frame=frame)
        
        return {
            'success': True,
            'object': object_name,
            'property': property,
            'frame': frame,
            'value': value,
        }
        
    except Exception as e:
        return {'error': str(e)}


def get_fcurves(object_name: str) -> Dict[str, Any]:
    """Get F-Curves for an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        if not obj.animation_data or not obj.animation_data.action:
            return {'object': object_name, 'fcurves': []}
        
        action = obj.animation_data.action
        fcurves = []
        if hasattr(action, 'fcurves'):
            for fc in action.fcurves:
                keyframes = []
                if hasattr(fc, 'keyframe_points'):
                    keyframes = [{'frame': kp.co[0], 'value': kp.co[1]} for kp in fc.keyframe_points]
                fcurves.append({
                    'data_path': fc.data_path,
                    'array_index': fc.array_index,
                    'keyframe_count': len(keyframes),
                    'keyframes': keyframes[:5],  # First 5 keyframes
                })
        
        return {
            'object': object_name,
            'count': len(fcurves),
            'fcurves': fcurves,
        }
        
    except Exception as e:
        return {'error': str(e)}


def set_interpolation(
    object_name: str,
    interpolation: str,
) -> Dict[str, Any]:
    """Set interpolation mode for F-Curves."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        if not obj.animation_data or not obj.animation_data.action:
            return {'error': f'No animation data for {object_name}'}
        
        # Valid interpolation modes
        valid_modes = ['CONSTANT', 'LINEAR', 'BEZIER', 'SINE', 'QUAD', 'CUBIC', 'QUART', 'QUINT', 'EXPO', 'CIRC', 'BACK', 'BOUNCE', 'ELASTIC']
        interpolation = interpolation.upper()
        
        if interpolation not in valid_modes:
            return {'error': f'Invalid interpolation mode: {interpolation}'}
        
        updated = 0
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = interpolation
                updated += 1
        
        return {
            'success': True,
            'object': object_name,
            'interpolation': interpolation,
            'keyframes_updated': updated,
        }
        
    except Exception as e:
        return {'error': str(e)}


def play(
    start: int = None,
    end: int = None,
) -> Dict[str, Any]:
    """Play animation."""
    try:
        import bpy
        if getattr(bpy.app, "background", False):
            return {"error": "Pemutaran animasi memerlukan antarmuka Blender."}
        
        scene = bpy.context.scene
        
        if start is not None:
            scene.frame_start = start
        if end is not None:
            scene.frame_end = end
        
        bpy.ops.screen.animation_play()
        
        return {
            'success': True,
            'start': scene.frame_start,
            'end': scene.frame_end,
        }
        
    except Exception as e:
        return {'error': str(e)}


def stop() -> Dict[str, Any]:
    """Stop animation."""
    try:
        import bpy
        if getattr(bpy.app, "background", False):
            return {"error": "Penghentian playback memerlukan antarmuka Blender."}
        
        bpy.ops.screen.animation_cancel(restore_frame=False)
        
        return {'success': True}
        
    except Exception as e:
        return {'error': str(e)}


def clear(object_name: str) -> Dict[str, Any]:
    """Clear all animation data from an object."""
    try:
        import bpy
        
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {'error': f'Object not found: {object_name}'}
        
        if obj.animation_data:
            obj.animation_data_clear()
        
        return {
            'success': True,
            'object': object_name,
        }
        
    except Exception as e:
        return {'error': str(e)}


# Handler mapping
HANDLERS = {
    'animation.keyframe_insert': keyframe_insert,
    'animation.keyframe_delete': keyframe_delete,
    'animation.set_keyframe': set_keyframe,
    'animation.get_fcurves': get_fcurves,
    'animation.set_interpolation': set_interpolation,
    'animation.play': play,
    'animation.stop': stop,
    'animation.clear': clear,
}
