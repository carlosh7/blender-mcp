"""
blender-mcp — Export Operator
"""
import bpy
import os
from bpy.types import Operator


class OP_Export(Operator):
    bl_idname = "aimcp.export"
    bl_label = "Export"

    def execute(self, ctx):
        out = os.path.expanduser("~/blender-mcp/models/scene.glb")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
        ctx.scene.aimcp_chat.add("system", "Exported")
        if ctx.area:
            ctx.area.tag_redraw()
        return {'FINISHED'}


EXPORT_OPERATORS = [OP_Export]


def register_export_operators():
    from bpy.utils import register_class
    for cls in EXPORT_OPERATORS:
        try: register_class(cls)
        except: pass


def unregister_export_operators():
    from bpy.utils import unregister_class
    for cls in reversed(EXPORT_OPERATORS):
        unregister_class(cls)
