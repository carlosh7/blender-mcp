"""
blender-mcp — Viewport Navigation Handler
"""
import bpy
from . import BaseHandler


class ViewportHandler(BaseHandler):
    """Viewport navigation: focus on objects, snap to view."""

    namespace = "viewport"

    @staticmethod
    def cmd_jump_to_view3d_object_by_name(name=""):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = bpy.context.temp_override(area=area, region=area.regions[0])
                with override:
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                return {"focused": name}
        return {"error": "No 3D viewport area found", "focused": name}
