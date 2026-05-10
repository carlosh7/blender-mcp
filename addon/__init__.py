# blender-mcp — AI Assistant for Blender v0.3.3
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 3, 3),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > AI",
    "description": "Chat with AI to create 3D models via blender-mcp",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}
import bpy, os
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty

# ─── Chat types ───
class ChatMsg(PropertyGroup):
    role: StringProperty(name="Role")
    text: StringProperty(name="Text")

class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg)
    count: IntProperty(name="Count", default=0)
    def add(self, role, text):
        m = self.msgs.add(); m.role = role; m.text = text
        self.count = len(self.msgs)
    def clear_all(self):
        while self.msgs: self.msgs.remove(0)
        self.count = 0

# ─── Operators ───
class OP_Connect(Operator):
    bl_idname = "aimcp.connect"; bl_label = "Connect"
    bl_description = "Connect to blender-mcp server"
    def execute(self, ctx):
        ctx.scene.aimcp_connected = True
        ctx.scene.aimcp_chat.add("system", "Connected OK")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"; bl_label = "Disconnect"
    def execute(self, ctx):
        ctx.scene.aimcp_connected = False
        ctx.scene.aimcp_chat.add("system", "Disconnected")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Send(Operator):
    bl_idname = "aimcp.send"; bl_label = "Send"
    def execute(self, ctx):
        txt = ctx.scene.aimcp_input.strip()
        if not txt: return {'CANCELLED'}
        ctx.scene.aimcp_chat.add("user", txt)
        ctx.scene.aimcp_input = ""
        ctx.scene.aimcp_chat.add("assistant", "OK - connect blender-mcp for live response")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Capture(Operator):
    bl_idname = "aimcp.capture"; bl_label = "Capture Scene"
    def execute(self, ctx):
        n = len(bpy.data.objects)
        m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects, {m} meshes")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Export(Operator):
    bl_idname = "aimcp.export_glb"; bl_label = "Export GLB"
    def execute(self, ctx):
        out = os.path.expanduser("~/blender-mcp/models/scene.glb")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
        ctx.scene.aimcp_chat.add("system", "Exported OK")
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Clear(Operator):
    bl_idname = "aimcp.clear"; bl_label = "Clear"
    def execute(self, ctx):
        ctx.scene.aimcp_chat.clear_all()
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

# ─── Panel ───
class PN_PT_Main(Panel):
    bl_label = "MCP AI Assistant"
    bl_idname = "PN_PT_Main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI'

    def draw(self, ctx):
        L = self.layout
        c = ctx.scene

        # Status
        box = L.box()
        row = box.row(align=True)
        if getattr(c, "aimcp_connected", False):
            row.operator("aimcp.disconnect", text="Disconnect", icon='X')
            row.label(text="Online", icon='CHECKBOX_HLT')
        else:
            row.operator("aimcp.connect", text="Connect", icon='ADD')
            row.label(text="Offline", icon='CHECKBOX_DEHLT')

        # Actions
        row = L.row(align=True)
        row.operator("aimcp.capture", text="Capture", icon='CAMERA_DATA')
        row.operator("aimcp.export_glb", text="Export", icon='EXPORT')

        # Chat
        L.separator()
        col = L.column(align=True)
        chat = getattr(c, "aimcp_chat", None)
        if chat and chat.count > 0:
            for m in chat.msgs:
                tag = "U:" if m.role == "user" else "A:" if m.role == "assistant" else "S:"
                col.label(text=f"{tag} {m.text[:80]}")
            col.operator("aimcp.clear", text="Clear", icon='X')
        else:
            col.label(text="No messages")

        # Input
        L.separator()
        row = L.row(align=True)
        row.scale_y = 2.0
        row.prop(c, "aimcp_input", text="")
        row = L.row(align=True)
        row.scale_y = 1.5
        row.operator("aimcp.send", text="Send", icon='PLAY')

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
    bpy.types.Scene.aimcp_input = StringProperty(name="Message", description="Type here")
    bpy.types.Scene.aimcp_connected = BoolProperty(name="Connected", default=False)

def unregister():
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    for attr in ["aimcp_connected", "aimcp_input", "aimcp_chat"]:
        if hasattr(bpy.types.Scene, attr):
            try: delattr(bpy.types.Scene, attr)
            except: pass

if __name__ == "__main__":
    register()
