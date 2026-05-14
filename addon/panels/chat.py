"""
blender-mcp — Chat Panel (refactored from addon/__init__.py)
3D View Sidebar — Axiom tab chat interface.
"""
import bpy
import json
import os
import time
import webbrowser
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty, PointerProperty
from bpy.types import Panel, UIList, PropertyGroup, Operator

from .. import blender_socket as bsock
from ..handlers import scene as scene_handler


class ChatMsg(PropertyGroup):
    role: StringProperty()
    text: StringProperty()
    is_new: BoolProperty(default=False)


class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg)
    count: IntProperty(default=0)

    def add(self, r, t, is_update=False, scene=None):
        was_at_bottom = False
        if scene:
            was_at_bottom = (scene.aimcp_chat_index >= len(self.msgs) - 1)
        if is_update:
            while len(self.msgs) > 0 and self.msgs[-1].role == r and not self.msgs[-1].is_new:
                self.msgs.remove(len(self.msgs) - 1)
            if len(self.msgs) > 0 and self.msgs[-1].role == r and self.msgs[-1].is_new:
                self.msgs.remove(len(self.msgs) - 1)
        lines = self._wrap(t)
        for i, l in enumerate(lines):
            m = self.msgs.add()
            m.role = r
            m.text = l
            m.is_new = (i == 0)
        self.count = len(self.msgs)
        if scene and (was_at_bottom or r == 'user' or (not is_update and r == 'assistant')):
            scene.aimcp_chat_index = self.count - 1

    @staticmethod
    def _wrap(text, max_chars=45):
        lines = []
        for p in text.split("\n"):
            if not p:
                lines.append("")
                continue
            words = p.split()
            curr, curr_len = [], 0
            for w in words:
                if curr_len + len(w) > max_chars:
                    lines.append(" ".join(curr))
                    curr = [w]
                    curr_len = len(w) + 1
                else:
                    curr.append(w)
                    curr_len += len(w) + 1
            if curr:
                lines.append(" ".join(curr))
        return lines

    def clear_all(self):
        for s in bpy.data.scenes:
            while s.aimcp_chat.msgs:
                s.aimcp_chat.msgs.remove(0)
            s.aimcp_chat.count = 0


class MCP_UL_Chat(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if not item:
            return
        row = layout.row(align=True)
        if item.is_new:
            tag = "Usted" if item.role == "user" else "IA" if item.role == "assistant" else "Sys"
            row.label(text=f"[{tag}] {item.text}")
        else:
            row.label(text=f"      {item.text}")


class BLENDERMCP_OT_OpenWeb(Operator):
    bl_idname = "blendermcp.open_web"
    bl_label = "Open Web UI"
    bl_description = "Open blender-mcp web status page in browser"

    def execute(self, context):
        webbrowser.open("http://127.0.0.1:9877/")
        return {'FINISHED'}


class PN_PT_Chat(Panel):
    bl_label = "AXIOM Chat"
    bl_idname = "PN_PT_Chat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Axiom'

    def draw(self, ctx):
        L = self.layout
        c = ctx.scene
        # Row 1: Status with connection indicator
        conn = c.aimcp_connection_status or "Listo"
        icon = 'CHECKBOX_HLT' if "✅" in conn else 'ERROR' if "🔴" in conn else 'SORTTIME' if "🟡" in conn else 'CHECKBOX_DEHLT'
        row = L.row(align=True)
        if c.aimcp_waiting:
            row.operator("aimcp.stop_agent", text="STOP", icon='CANCEL')
            row.label(text="Working...", icon='SORTTIME')
        else:
            row.label(text=conn[:28], icon=icon)
        row.operator("blendermcp.start_embedded", text="", icon='SYSTEM')
        row.operator("blendermcp.open_web", text="", icon='URL')
        row = L.row(align=True)
        row.operator("aimcp.capture", text="Vision", icon='CAMERA_DATA')
        row.operator("aimcp.export", text="Export", icon='EXPORT')
        row.operator("blendermcp.open_web", text="Web", icon='URL')
        L.separator()
        col = L.column(align=True)
        num = len(c.aimcp_chat.msgs)
        col.template_list("MCP_UL_Chat", "", c.aimcp_chat, "msgs", c, "aimcp_chat_index", rows=min(max(num, 2), 11))
        L.separator()
        L.prop(c, "aimcp_input", text="")
        row = L.row(align=True)
        row.scale_y = 1.2
        row.operator("aimcp.send", text="Send", icon='PLAY')
        row.operator("aimcp.clear_chat", text="Clear", icon='X')
