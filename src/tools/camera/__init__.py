"""
blender-mcp-ultra — Camera Tools
"""
from typing import Any, Dict, Optional, Tuple
from core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool("camera.create", ToolCategory.CAMERA, "Create a camera", ToolPermission.WRITE,
         {"name": {"type": "str"}, "location": {"type": "tuple", "default": (0, -5, 2)},
          "lens": {"type": "float", "default": 50}}),
    Tool("camera.delete", ToolCategory.CAMERA, "Delete a camera", ToolPermission.DESTRUCTIVE,
         {"name": {"type": "str", "required": True}}),
    Tool("camera.set_active", ToolCategory.CAMERA, "Set active camera", ToolPermission.WRITE,
         {"name": {"type": "str", "required": True}}),
    Tool("camera.update", ToolCategory.CAMERA, "Update camera properties", ToolPermission.WRITE,
         {"name": {"type": "str", "required": True}, "lens": {"type": "float"},
          "dof": {"type": "float"}, "clip_start": {"type": "float"}, "clip_end": {"type": "float"}}),
    Tool("camera.track_to", ToolCategory.CAMERA, "Make camera track to object", ToolPermission.WRITE,
         {"camera_name": {"type": "str", "required": True}, "target_name": {"type": "str", "required": True}}),
    Tool("camera.list", ToolCategory.CAMERA, "List all cameras", ToolPermission.READ_ONLY, {}),
    Tool("camera.setResolution", ToolCategory.CAMERA, "Set render resolution", ToolPermission.WRITE,
         {"width": {"type": "int"}, "height": {"type": "int"}, "percentage": {"type": "float"}}),
    Tool("camera.set_framing", ToolCategory.CAMERA, "Set camera framing (center object)", ToolPermission.WRITE,
         {"camera_name": {"type": "str"}, "object_name": {"type": "str"}}),
]

def create(name: str = None, location: Tuple = (0, -5, 2), lens: float = 50) -> Dict:
    try:
        import bpy
        bpy.ops.object.camera_add(location=location)
        cam = getattr(bpy.context, "active_object", None)
        if cam is None and getattr(bpy.context, "selected_objects", []):
            cam = getattr(bpy.context, "selected_objects", [])[0]
        if cam is None:
            for o in reversed(bpy.data.objects):
                if o.type == 'CAMERA':
                    cam = o
                    break
        if cam is None:
            return {"error": "Failed to create camera"}
        if name: cam.name = name
        cam.data.lens = lens
        bpy.context.scene.camera = cam
        return {"success": True, "name": cam.name, "lens": lens}
    except ImportError: return {"error": "Blender not available"}

def delete(name: str) -> Dict:
    try:
        import bpy
        obj = bpy.data.objects.get(name)
        if not obj or obj.type != 'CAMERA': return {"error": f"Camera not found: {name}"}
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"success": True, "name": name}
    except ImportError: return {"error": "Blender not available"}

def set_active(name: str) -> Dict:
    try:
        import bpy
        cam = bpy.data.objects.get(name)
        if not cam or cam.type != 'CAMERA': return {"error": f"Camera not found: {name}"}
        bpy.context.scene.camera = cam
        return {"success": True, "name": name}
    except ImportError: return {"error": "Blender not available"}

def update(name: str, lens: float = None, dof: float = None, clip_start: float = None, clip_end: float = None) -> Dict:
    try:
        import bpy
        obj = bpy.data.objects.get(name)
        if not obj or obj.type != 'CAMERA': return {"error": f"Camera not found: {name}"}
        cam = obj.data
        updated = []
        if lens is not None: cam.lens = lens; updated.append("lens")
        if dof is not None: cam.dof.aperture_fstop = dof; updated.append("dof")
        if clip_start is not None: cam.clip_start = clip_start; updated.append("clip_start")
        if clip_end is not None: cam.clip_end = clip_end; updated.append("clip_end")
        return {"success": True, "name": name, "updated": updated}
    except ImportError: return {"error": "Blender not available"}

def track_to(camera_name: str, target_name: str) -> Dict:
    try:
        import bpy
        cam = bpy.data.objects.get(camera_name)
        target = bpy.data.objects.get(target_name)
        if not cam: return {"error": f"Camera not found: {camera_name}"}
        if not target: return {"error": f"Target not found: {target_name}"}
        constraint = cam.constraints.new(type='TRACK_TO')
        constraint.target = target
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        return {"success": True, "camera": camera_name, "target": target_name}
    except ImportError: return {"error": "Blender not available"}

def list_cameras() -> Dict:
    try:
        import bpy
        cameras = [{"name": o.name, "lens": o.data.lens, "location": list(o.location)}
                   for o in bpy.context.scene.objects if o.type == 'CAMERA']
        return {"count": len(cameras), "cameras": cameras}
    except ImportError: return {"error": "Blender not available"}

def set_resolution(width: int = 1920, height: int = 1080, percentage: float = 100) -> Dict:
    try:
        import bpy
        s = bpy.context.scene
        s.render.resolution_x = width
        s.render.resolution_y = height
        s.render.resolution_percentage = percentage
        return {"success": True, "width": width, "height": height, "percentage": percentage}
    except ImportError: return {"error": "Blender not available"}

def set_framing(camera_name: str = None, object_name: str = None) -> Dict:
    try:
        import bpy
        cam_obj = bpy.data.objects.get(camera_name) if camera_name else bpy.context.scene.camera
        target = bpy.data.objects.get(object_name) if object_name else None
        if not cam_obj: return {"error": "No active camera"}
        if target:
            bpy.context.scene.camera = cam_obj
            cam_obj.location = target.location + bpy.mathutils.Vector((0, -5, 2))
            bpy.ops.object.constraint_add(type='TRACK_TO')
            bpy.context.object.constraints[-1].target = target
        return {"success": True}
    except ImportError: return {"error": "Blender not available"}

HANDLERS = {
    "camera.create": create, "camera.delete": delete, "camera.set_active": set_active,
    "camera.update": update, "camera.track_to": track_to, "camera.list": list_cameras,
    "camera.setResolution": set_resolution, "camera.set_framing": set_framing,
}
