"""
blender-mcp — Camera Handler
"""
import bpy
import math
from mathutils import Vector
from . import BaseHandler


class CameraHandler(BaseHandler):
    """Create and control cameras: lens, DOF, tracking, auto-framing."""

    namespace = "camera"

    @staticmethod
    def cmd_create_camera(name="Camera", location=(5.0, -5.0, 4.0), rotation=(math.radians(60), 0, math.radians(45)), lens=50.0):
        bpy.ops.object.camera_add(location=location, rotation=rotation)
        cam = bpy.context.active_object
        cam.name = name
        cam.data.lens = lens
        bpy.context.scene.camera = cam
        return {"name": cam.name, "location": list(cam.location), "lens": lens}

    @staticmethod
    def cmd_set_camera_target(camera_name="", target_name=""):
        cam = bpy.data.objects.get(camera_name) or bpy.context.scene.camera
        target = bpy.data.objects.get(target_name)
        if not cam or not target:
            return {"error": "Camera or target not found"}
        direction = target.location - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        return {"camera": cam.name, "target": target.name}

    @staticmethod
    def cmd_auto_frame(target_name="", margin=1.5):
        target = bpy.data.objects.get(target_name)
        if not target:
            return {"error": "Target not found"}
        bpy.ops.object.select_all(action='DESELECT')
        target.select_set(True)
        bpy.context.view_layer.objects.active = target
        bpy.ops.view3d.camera_to_view_selected()
        return {"framed": target.name}
