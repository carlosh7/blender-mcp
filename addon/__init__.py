# blender-mcp Addon for Blender — v0.2.4
# Minimal but functional: chat panel, scene capture, export GLB
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 2, 5),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > AI",
    "description": "Chat panel to interact with AI via blender-mcp server",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty
import os

# ─── Chat Message (single item in collection) ───
class ChatMsg(PropertyGroup):
    role: StringProperty()
    text: StringProperty()

# ─── Chat Data (scene storage) ───
class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg)
    count: IntProperty(default=0)

    def add(self, role, text):
        m = self.msgs.add()
        m.role = role
        m.text = text
        self.count = len(self.msgs)

# ─── App State ───
class AppState(PropertyGroup):
    connected: BoolProperty(default=False)

# ─── Connect ───
class OP_Connect(Operator):
    bl_idname = "aimcp.connect"
    bl_label = "Connect"
    def execute(self, ctx):
        ctx.scene.aimcp_connected = True
        ctx.scene.aimcp_chat.add("system", "Connected ✅")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"
    bl_label = "Disconnect"
    def execute(self, ctx):
        ctx.scene.aimcp_connected = False
        ctx.scene.aimcp_chat.add("system", "Disconnected")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Send(Operator):
    bl_idname = "aimcp.send"
    bl_label = "Send"
    def execute(self, ctx):
        txt = ctx.scene.aimcp_input.strip()
        if not txt: return {'CANCELLED'}
        ctx.scene.aimcp_chat.add("user", txt)
        ctx.scene.aimcp_input = ""
        ctx.scene.aimcp_chat.add("assistant", "🤖 Processing...")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Capture(Operator):
    bl_idname = "aimcp.capture"
    bl_label = "Capture Scene"
    def execute(self, ctx):
        n = len(bpy.data.objects)
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Export(Operator):
    bl_idname = "aimcp.export_glb"
    bl_label = "Export GLB"
    def execute(self, ctx):
        out = os.path.expanduser("~/blender-mcp/models/scene.glb")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
        ctx.scene.aimcp_chat.add("system", f"Exported ✅")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Clear(Operator):
    bl_idname = "aimcp.clear"
    bl_label = "Clear"
    def execute(self, ctx):
        ctx.scene.aimcp_chat.msgs.clear()
        ctx.scene.aimcp_chat.count = 0
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

# ─── Panel ───
class PN_Main(Panel):
    bl_label = "🤖 AI Assistant"
    bl_idname = "PN_Main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI'

    def draw(self, ctx):
        L = self.layout

        # Status bar
        r = L.row(align=True)
        if ctx.scene.aimcp_connected:
            r.operator("aimcp.disconnect", text="Disconnect")
            r.label(text="● Online")
        else:
            r.operator("aimcp.connect", text="Connect")
            r.label(text="○ Offline")

        # Actions
        c = L.column(align=True)
        c.scale_y = 1.3
        r2 = c.row(align=True)
        r2.operator("aimcp.capture", text="📷 Scene")
        r2.operator("aimcp.export_glb", text="📤 Export")

        # Chat
        L.separator()
        b = L.box()
        chat = ctx.scene.aimcp_chat
        if chat.count == 0:
            b.label(text="💬 No messages")
        else:
            for m in chat.msgs:
                icon = "🧑" if m.role == "user" else "🤖" if m.role == "assistant" else "ℹ️"
                b.label(text=f"{icon} {m.text[:80]}")
            b.operator("aimcp.clear", text="Clear", icon='X')

        # Input
        L.separator()
        r3 = L.row(align=True)
        r3.prop(ctx.scene, "aimcp_input", text="")
        r3.operator("aimcp.send", text="Send", icon='PLAY')

# ─── Register ───
classes = [ChatMsg, ChatData, AppState, OP_Connect, OP_Disconnect, OP_Send, OP_Capture, OP_Export, OP_Clear, PN_Main]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatData)
    bpy.types.Scene.aimcp_input = StringProperty(description="Write your message...")
    bpy.types.Scene.aimcp_connected = BoolProperty(default=False)

def unregister():
    del bpy.types.Scene.aimcp_connected
    del bpy.types.Scene.aimcp_input
    del bpy.types.Scene.aimcp_chat
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
