"""
blender-mcp — Capture Operator
"""
import bpy
from bpy.types import Operator


class OP_Capture(Operator):
    bl_idname = "aimcp.capture"
    bl_label = "Capture"

    def execute(self, ctx):
        n = len(bpy.data.objects)
        m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects, {m} meshes")
        if ctx.area:
            ctx.area.tag_redraw()
        return {'FINISHED'}


CAPTURE_OPERATORS = [OP_Capture]


def register_capture_operators():
    from bpy.utils import register_class
    for cls in CAPTURE_OPERATORS:
        try: register_class(cls)
        except: pass


def unregister_capture_operators():
    from bpy.utils import unregister_class
    for cls in reversed(CAPTURE_OPERATORS):
        unregister_class(cls)
