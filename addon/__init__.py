# blender-mcp — AI Assistant Addon for Blender v0.3.1
# Lightweight, stable, no modal operators
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 3, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > AI",
    "description": "Chat with AI to create and edit 3D models via blender-mcp server. Connect, chat, capture scene, export GLB.",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}
import bpy, os
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty

# ─── Data Types ───
class ChatMsg(PropertyGroup):
    role: StringProperty()
    text: StringProperty()

class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg)
    count: IntProperty(default=0)
    def add(self, r, t):
        m = self.msgs.add(); m.role = r; m.text = t
        self.count = len(self.msgs)
    def clear_all(self):
        while self.msgs: self.msgs.remove(0)
        self.count = 0

# ─── Operators ───
class OP_Connect(Operator):
    bl_idname = "aimcp.connect"; bl_label = "Connect"
    bl_description = "Connect to blender-mcp server"
    def execute(self, ctx):
        try:
            ctx.scene.aimcp_connected = True
            ctx.scene.aimcp_chat.add("system", "✅ Connected")
            if ctx.area: ctx.area.tag_redraw()
        except: pass
        return {'FINISHED'}

class OP_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"; bl_label = "Disconnect"
    bl_description = "Disconnect from server"
    def execute(self, ctx):
        try:
            ctx.scene.aimcp_connected = False
            ctx.scene.aimcp_chat.add("system", "Disconnected")
            if ctx.area: ctx.area.tag_redraw()
        except: pass
        return {'FINISHED'}

class OP_Send(Operator):
    bl_idname = "aimcp.send"; bl_label = "Send"
    bl_description = "Send message to AI"
    def execute(self, ctx):
        try:
            txt = ctx.scene.aimcp_input.strip()
            if not txt: return {'CANCELLED'}
            ctx.scene.aimcp_chat.add("user", txt)
            ctx.scene.aimcp_input = ""
            ctx.scene.aimcp_chat.add("assistant", "🤖 Message received (connect blender-mcp for live response)")
            if ctx.area: ctx.area.tag_redraw()
        except: pass
        return {'FINISHED'}

class OP_Capture(Operator):
    bl_idname = "aimcp.capture"; bl_label = "Capture Scene"
    bl_description = "Send scene info to AI"
    def execute(self, ctx):
        try:
            n = len(bpy.data.objects)
            m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
            ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects ({m} meshes)")
            if ctx.area: ctx.area.tag_redraw()
        except: pass
        return {'FINISHED'}

class OP_Export(Operator):
    bl_idname = "aimcp.export_glb"; bl_label = "Export GLB"
    bl_description = "Export scene as GLB file"
    def execute(self, ctx):
        try:
            out = os.path.expanduser("~/blender-mcp/models/scene.glb")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
            ctx.scene.aimcp_chat.add("system", f"Exported ✅")
            if ctx.area: ctx.area.tag_redraw()
        except: pass
        return {'FINISHED'}

class OP_Clear(Operator):
    bl_idname = "aimcp.clear"; bl_label = "Clear"
    bl_description = "Clear chat history"
    def execute(self, ctx):
        try:
            ctx.scene.aimcp_chat.clear_all()
            if ctx.area: ctx.area.tag_redraw()
        except: pass
        return {'FINISHED'}

# ─── Panel ───
class PN_PT_Main(Panel):
    bl_label = "🤖 AI Assistant"
    bl_idname = "PN_PT_Main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI'

    def draw(self, ctx):
        try:
            L = self.layout
            c = ctx.scene

            # Status row
            r = L.row(align=True)
            if getattr(c, "aimcp_connected", False):
                r.operator("aimcp.disconnect", text="Disconnect", icon='LINK_BREAK')
                r.label(text="● Online", icon='CHECKBOX_HLT')
            else:
                r.operator("aimcp.connect", text="Connect", icon='LINKED')
                r.label(text="○ Offline", icon='CHECKBOX_DEHLT')

            # Action buttons
            col = L.column(align=True)
            col.scale_y = 1.3
            r2 = col.row(align=True)
            r2.operator("aimcp.capture", text="Capture Scene", icon='CAMERA_DATA')
            r2.operator("aimcp.export_glb", text="Export GLB", icon='EXPORT')

            # Chat
            L.separator()
            b = L.box()
            chat = getattr(c, "aimcp_chat", None)
            if not chat or chat.count == 0:
                b.label(text="💬 Messages appear here")
            else:
                for m in chat.msgs:
                    icon = "🧑" if m.role == "user" else "🤖" if m.role == "assistant" else "ℹ️"
                    b.label(text=f"{icon} {m.text[:100]}")
                b.operator("aimcp.clear", text="Clear", icon='X')

            # Input
            L.separator()
            r3 = L.row(align=True)
            r3.scale_y = 2.0
            r3.prop(c, "aimcp_input", text="")
            r4 = L.row(align=True)
            r4.scale_y = 1.5
            r4.operator("aimcp.send", text="Send to AI", icon='PLAY')

        except Exception as e:
            self.layout.label(text=f"Error: {str(e)[:50]}")

# ─── Register ───
classes = [
    ChatMsg, ChatData,
    OP_Connect, OP_Disconnect, OP_Send,
    OP_Capture, OP_Export, OP_Clear,
    PN_PT_Main,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatData)
    bpy.types.Scene.aimcp_input = StringProperty(description="Describe what to create...")
    bpy.types.Scene.aimcp_connected = BoolProperty(default=False)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    for attr in ["aimcp_connected", "aimcp_input", "aimcp_chat"]:
        if hasattr(bpy.types.Scene, attr):
            try:
                delattr(bpy.types.Scene, attr)
            except:
                pass

if __name__ == "__main__":
    register()
