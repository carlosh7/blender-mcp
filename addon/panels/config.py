"""
blender-mcp — Config Panel
Model selector, status, connection state
"""
import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty, PointerProperty
from bpy.types import Panel, PropertyGroup, UIList


class PN_PT_Config(Panel):
    bl_label = "Axiom Engine Config"
    bl_idname = "PN_PT_Config"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, ctx):
        L = self.layout
        c = ctx.scene
        box = L.box()
        box.label(text="Status", icon='LINKED')
        row = box.row(align=True)
        is_connected = hasattr(ctx.scene, 'aimcp_connected') and ctx.scene.aimcp_connected
        row.label(text="Socket: Online" if is_connected else "Socket: Offline",
                  icon='CHECKBOX_HLT' if is_connected else 'CHECKBOX_DEHLT')
        L.separator()
        box = L.box()
        box.label(text="AI Provider", icon='SETTINGS')
        box.prop(c, "aimcp_provider", text="")
        box.prop(c, "aimcp_model", text="Model")
        row = box.row(align=True)
        row.operator("aimcp.refresh", text="Refresh", icon='FILE_REFRESH')
        row = box.row(align=True)
        row.label(text="Agent Mode:", icon='MODIFIER')
        row.prop(c, "blendermcp_agent_mode", text="")
        status = c.aimcp_status
        if status:
            L.label(text=status, icon='INFO')
