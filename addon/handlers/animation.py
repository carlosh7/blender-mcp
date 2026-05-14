"""
blender-mcp — Animation Handler
Keyframes, F-curves, actions, NLA, motion.
"""
import bpy
import math
from . import BaseHandler


class AnimationHandler(BaseHandler):
    """Create and manage keyframe animation, actions, and NLA."""

    namespace = "animation"

    @staticmethod
    def cmd_insert_keyframe(object_name="", frame=1, property="location", value=None):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        bpy.context.scene.frame_set(frame)
        if value is not None and hasattr(obj, property):
            setattr(obj, property, value)
        obj.keyframe_insert(data_path=property)
        return {"object": object_name, "property": property, "frame": frame}

    @staticmethod
    def cmd_animate_location(object_name="", start_frame=1, end_frame=60, start_loc=(0, 0, 0), end_loc=(5, 0, 0)):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        bpy.context.scene.frame_set(start_frame)
        obj.location = start_loc
        obj.keyframe_insert(data_path="location")
        bpy.context.scene.frame_set(end_frame)
        obj.location = end_loc
        obj.keyframe_insert(data_path="location")
        return {"object": object_name, "frames": [start_frame, end_frame]}

    @staticmethod
    def cmd_animate_rotation(object_name="", start_frame=1, end_frame=60, start_rot=(0, 0, 0), end_rot=(0, 0, math.radians(360))):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        bpy.context.scene.frame_set(start_frame)
        obj.rotation_euler = start_rot
        obj.keyframe_insert(data_path="rotation_euler")
        bpy.context.scene.frame_set(end_frame)
        obj.rotation_euler = end_rot
        obj.keyframe_insert(data_path="rotation_euler")
        return {"object": object_name, "frames": [start_frame, end_frame]}

    @staticmethod
    def cmd_animate_scale(object_name="", start_frame=1, end_frame=60, start_scale=(1, 1, 1), end_scale=(2, 2, 2)):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        bpy.context.scene.frame_set(start_frame)
        obj.scale = start_scale
        obj.keyframe_insert(data_path="scale")
        bpy.context.scene.frame_set(end_frame)
        obj.scale = end_scale
        obj.keyframe_insert(data_path="scale")
        return {"object": object_name, "frames": [start_frame, end_frame]}

    @staticmethod
    def cmd_set_keyframe_interpolation(object_name="", interpolation="BEZIER"):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = interpolation
        return {"object": object_name, "interpolation": interpolation}

    @staticmethod
    def cmd_create_action(object_name="", action_name=""):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        if not action_name:
            action_name = f"{obj.name}_action"
        action = bpy.data.actions.new(action_name)
        if obj.animation_data:
            obj.animation_data.action = action
        else:
            obj.animation_data_create().action = action
        return {"object": object_name, "action": action_name}

    @staticmethod
    def cmd_set_render_range(start=1, end=250):
        bpy.context.scene.frame_start = start
        bpy.context.scene.frame_end = end
        return {"frame_start": start, "frame_end": end}
