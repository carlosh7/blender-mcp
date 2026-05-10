# blender-mcp — AI Assistant for Blender v0.4.0
# Full chat UI with scroll, bigger input, better layout
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 4, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > AI",
    "description": "Chat with AI to create 3D models via blender-mcp",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}
import bpy, os
from bpy.types import Panel, Operator, PropertyGroup, UIList
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

# ─── Scrollable Chat List ───
class MCP_UL_Chat(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        tag = "You" if item.role == "user" else "AI" if item.role == "assistant" else "Sys"
        col = layout.column()
        col.scale_y = 1.5
        col.label(text=f"[{tag}]")
        for line in item.text.split("\n"):
            col.label(text=f"  {line[:120]}")

# ─── Operators ───
class OP_Connect(Operator):
    bl_idname = "aimcp.connect"; bl_label = "Connect"
    bl_description = "Connect to blender-mcp server"
    def execute(self, ctx):
        ctx.scene.aimcp_connected = True
        ctx.scene.aimcp_chat.add("system", "Connected to blender-mcp server")
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
    bl_description = "Send message to AI"
    def execute(self, ctx):
        txt = ctx.scene.aimcp_input.strip()
        if not txt: return {'CANCELLED'}
        ctx.scene.aimcp_chat.add("user", txt)
        ctx.scene.aimcp_input = ""
        ctx.scene.aimcp_chat.add("assistant", "Message received. Connect blender-mcp server for live AI responses.")
        # Auto-scroll: set active to last item
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Capture(Operator):
    bl_idname = "aimcp.capture"; bl_label = "Capture Scene"
    def execute(self, ctx):
        n = len(bpy.data.objects)
        m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects, {m} meshes")
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Export(Operator):
    bl_idname = "aimcp.export_glb"; bl_label = "Export GLB"
    def execute(self, ctx):
        out = os.path.expanduser("~/blender-mcp/models/scene.glb")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
        ctx.scene.aimcp_chat.add("system", f"Exported to ~/blender-mcp/models/")
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
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
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, ctx):
        L = self.layout
        c = ctx.scene

        # Status + actions (compact row)
        row = L.row(align=True)
        if getattr(c, "aimcp_connected", False):
            row.operator("aimcp.disconnect", text="Disconnect", icon='X')
            row.label(text="Online", icon='CHECKBOX_HLT')
        else:
            row.operator("aimcp.connect", text="Connect", icon='ADD')
            row.label(text="Offline", icon='CHECKBOX_DEHLT')
        row.separator()
        row.operator("aimcp.capture", text="", icon='CAMERA_DATA')
        row.operator("aimcp.export_glb", text="", icon='EXPORT')

        # ─── Scrollable Chat ───
        L.separator()
        chat = getattr(c, "aimcp_chat", None)
        if chat and chat.count > 0:
            # Chat list takes available vertical space
            row = L.row()
            row.template_list("MCP_UL_Chat", "", chat, "msgs", c, "aimcp_chat_index", rows=max(5, chat.count))
        else:
            L.label(text="No messages. Type below and press Send.")

        # ─── Input area (always visible, big) ───
        L.separator()
        row = L.row(align=True)
        row.scale_y = 3.0
        row.prop(c, "aimcp_input", text="")
        row = L.row(align=True)
        row.scale_y = 1.5
        row.operator("aimcp.send", text="Send to AI", icon='PLAY')
        row.operator("aimcp.clear", text="Clear", icon='X')

# ─── Register ───
classes = [
    ChatMsg, ChatData, MCP_UL_Chat,
    OP_Connect, OP_Disconnect, OP_Send,
    OP_Capture, OP_Export, OP_Clear,
    PN_PT_Main,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatData)
    bpy.types.Scene.aimcp_input = StringProperty(name="", description="Describe what to create...")
    bpy.types.Scene.aimcp_connected = BoolProperty(name="", default=False)
    bpy.types.Scene.aimcp_chat_index = IntProperty(name="", default=0)

def unregister():
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    for attr in ["aimcp_chat_index", "aimcp_connected", "aimcp_input", "aimcp_chat"]:
        if hasattr(bpy.types.Scene, attr):
            try: delattr(bpy.types.Scene, attr)
            except: pass

if __name__ == "__main__":
    register()
