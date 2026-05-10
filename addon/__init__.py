# blender-mcp Addon for Blender — v0.3.0
# Panel con indicador de actividad, input más grande, progreso simulado
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 3, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > AI",
    "description": "Chat with AI to create and edit 3D models",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}

import bpy, os, time, threading
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, PointerProperty, CollectionProperty

# ─── Chat Message ───
class ChatMsg(PropertyGroup):
    role: StringProperty()
    text: StringProperty()

# ─── Chat Data ───
class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg)
    count: IntProperty(default=0)
    def add(self, role, text):
        m = self.msgs.add(); m.role = role; m.text = text
        self.count = len(self.msgs)
    def clear_all(self):
        self.msgs.clear(); self.count = 0

# ─── ───
# ─── ───

# ─── Operators ───
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
        ctx.scene.aimcp_processing = False
        ctx.scene.aimcp_chat.add("system", "Disconnected")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Send(Operator):
    bl_idname = "aimcp.send"
    bl_label = "Send"
    bl_description = "Send message to AI"

    _timer = None
    _step = 0

    def execute(self, ctx):
        txt = ctx.scene.aimcp_input.strip()
        if not txt: return {'CANCELLED'}

        ctx.scene.aimcp_chat.add("user", txt)
        ctx.scene.aimcp_input = ""
        ctx.scene.aimcp_processing = True
        ctx.scene.aimcp_progress = 0.0
        ctx.scene.aimcp_status = "Processing..."

        if ctx.area: ctx.area.tag_redraw()

        # Simulate async processing via timer
        self._step = 0
        self._timer = ctx.window_manager.event_timer_add(0.3, window=ctx.window)
        ctx.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, ctx, event):
        if event.type != 'TIMER': return {'PASS_THROUGH'}

        self._step += 1
        if self._step <= 5:
            ctx.scene.aimcp_progress = self._step * 20
            dots = "." * (self._step % 4)
            ctx.scene.aimcp_status = f"Processing{dots}"
            if ctx.area: ctx.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Done
        ctx.scene.aimcp_processing = False
        ctx.scene.aimcp_progress = 100
        ctx.scene.aimcp_chat.add("assistant", "✅ I'll create the model. (Connect blender-mcp server for live generation)")
        if ctx.area: ctx.area.tag_redraw()

        ctx.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}

class OP_Capture(Operator):
    bl_idname = "aimcp.capture"
    bl_label = "Capture Scene"
    def execute(self, ctx):
        n = len(bpy.data.objects)
        m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects ({m} meshes)")
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
        ctx.scene.aimcp_chat.add("system", f"Exported to ~/blender-mcp/models/ ✅")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Clear(Operator):
    bl_idname = "aimcp.clear"
    bl_label = "Clear"
    def execute(self, ctx):
        ctx.scene.aimcp_chat.clear_all()
        ctx.scene.aimcp_processing = False
        ctx.scene.aimcp_progress = 0
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
        c = ctx.scene

        # ── Connection status ──
        r = L.row(align=True)
        if c.aimcp_connected:
            r.operator("aimcp.disconnect", text="Disconnect", icon='LINK_BREAK')
            r.label(text="● Online")
        else:
            r.operator("aimcp.connect", text="Connect", icon='LINKED')
            r.label(text="○ Offline")

        # ── Actions ──
        col = L.column(align=True)
        col.scale_y = 1.3
        r2 = col.row(align=True)
        r2.operator("aimcp.capture", text="📷 Scene", icon='CAMERA_DATA')
        r2.operator("aimcp.export_glb", text="📤 Export", icon='EXPORT')

        # ── Activity indicator (when processing) ──
        if c.aimcp_processing:
            L.separator()
            box = L.box()
            row = box.row()
            row.label(text=c.aimcp_status, icon='INFO')
            # Progress bar
            row = box.row(align=True)
            row.prop(c, "aimcp_progress", slider=True, text=f"{int(c.aimcp_progress)}%")
            row.enabled = False

        # ── Chat ──
        L.separator()
        b = L.box()
        chat = c.aimcp_chat
        if chat.count == 0:
            b.label(text="💬 No messages")
        else:
            for m in chat.msgs:
                icon = "🧑" if m.role == "user" else "🤖" if m.role == "assistant" else "ℹ️"
                b.label(text=f"{icon} {m.text[:100]}")
            b.operator("aimcp.clear", text="Clear", icon='X')

        # ── Input (bigger) ──
        L.separator()
        r3 = L.row(align=True)
        r3.scale_y = 2.0
        r3.prop(c, "aimcp_input", text="")
        r4 = L.row(align=True)
        r4.scale_y = 1.5
        r4.operator("aimcp.send", text="🚀 Send to AI", icon='PLAY')

# ─── Register ───
classes = [
    ChatMsg, ChatData,
    OP_Connect, OP_Disconnect, OP_Send,
    OP_Capture, OP_Export, OP_Clear,
    PN_Main,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatData)
    bpy.types.Scene.aimcp_input = StringProperty(description="Describe what you want to create...")
    bpy.types.Scene.aimcp_connected = BoolProperty(default=False)
    bpy.types.Scene.aimcp_processing = BoolProperty(default=False)
    bpy.types.Scene.aimcp_progress = FloatProperty(default=0.0, min=0, max=100, subtype='PERCENTAGE')
    bpy.types.Scene.aimcp_status = StringProperty(default="")

def unregister():
    for p in ["aimcp_status", "aimcp_progress", "aimcp_processing", "aimcp_connected", "aimcp_input", "aimcp_chat"]:
        if hasattr(bpy.types.Scene, p):
            delattr(bpy.types.Scene, p)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
