"""
blender-mcp — Batch Processing Handler
Multi-camera render, turntable, batch operations.
"""
import bpy
import math
import os
from . import BaseHandler


class BatchHandler(BaseHandler):
    """Batch operations: multi-camera render, turntable, batch rename."""

    namespace = "batch"

    @staticmethod
    def cmd_turntable_render(object_name="", output_dir="", frames=36, resolution=(1920, 1080)):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        os.makedirs(output_dir, exist_ok=True)
        scene = bpy.context.scene
        old_res = (scene.render.resolution_x, scene.render.resolution_y)
        scene.render.resolution_x, scene.render.resolution_y = resolution
        old_end = scene.frame_end
        scene.frame_end = frames
        # Point camera at object
        cam = scene.camera
        if cam:
            constraint = cam.constraints.new(type='TRACK_TO')
            constraint.target = obj
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
        # Animate object rotation
        for f in range(1, frames + 1):
            scene.frame_set(f)
            obj.rotation_euler.z = math.radians(360 * (f - 1) / frames)
            obj.keyframe_insert(data_path="rotation_euler", index=2)
        # Render
        scene.render.filepath = os.path.join(output_dir, "turntable_####")
        bpy.ops.render.render(animation=True)
        scene.render.resolution_x, scene.render.resolution_y = old_res
        scene.frame_end = old_end
        # Cleanup constraint
        if cam:
            cam.constraints.clear()
        return {"output_dir": output_dir, "frames": frames}

    @staticmethod
    def cmd_batch_rename(prefix="", search="", replace="", object_type="ALL"):
        count = 0
        for obj in bpy.data.objects:
            if object_type != "ALL" and obj.type != object_type:
                continue
            if search and search in obj.name:
                obj.name = obj.name.replace(search, replace)
                count += 1
            elif prefix:
                obj.name = f"{prefix}_{obj.name}"
                count += 1
        return {"renamed": count, "prefix": prefix or f"'{search}'→'{replace}'"}

    @staticmethod
    def cmd_batch_delete_by_type(object_type="MESH"):
        count = 0
        for obj in list(bpy.data.objects):
            if obj.type == object_type:
                bpy.data.objects.remove(obj, do_unlink=True)
                count += 1
        return {"deleted": count, "type": object_type}

    @staticmethod
    def cmd_apply_transforms_all():
        count = 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                count += 1
        return {"applied": count}
