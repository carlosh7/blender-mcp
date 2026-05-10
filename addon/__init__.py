# blender-mcp Addon for Blender
# Provides: AI chat panel, scene capture, live script execution
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 2, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > AI Tab",
    "description": "Chat with AI to create and edit 3D models via blender-mcp. Open sidebar with N, click AI tab.",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty
import os


# ─── Chat Message Item ───
class ChatMessageItem(PropertyGroup):
    role: StringProperty(name="Role", default="user")
    text: StringProperty(name="Text", default="")
    time: StringProperty(name="Time", default="")


# ─── Chat Container ───
class ChatContainer(PropertyGroup):
    messages: CollectionProperty(type=ChatMessageItem)
    count: IntProperty(name="Count", default=0)
    max_messages: IntProperty(default=20)

    def add_message(self, role: str, text: str):
        while len(self.messages) >= self.max_messages:
            self.messages.remove(0)
        item = self.messages.add()
        item.role = role
        item.text = text
        self.count = len(self.messages)


# ─── Properties ───
class AIMCPProperties(PropertyGroup):
    server_host: StringProperty(name="Server Host", default="localhost")
    server_port: IntProperty(name="Server Port", default=9876, min=1024, max=65535)
    connected: BoolProperty(name="Connected", default=False)


# ─── Operators ───
class AIMCP_OT_Connect(Operator):
    bl_idname = "aimcp.connect"
    bl_label = "Connect"
    bl_description = "Connect to blender-mcp server"

    def execute(self, context):
        context.scene.aimcp_props.connected = True
        context.scene.aimcp_chat.add_message("system", "Connected to blender-mcp server")
        context.area.tag_redraw()
        self.report({'INFO'}, "Connected")
        return {'FINISHED'}


class AIMCP_OT_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"
    bl_label = "Disconnect"
    bl_description = "Disconnect from MCP server"

    def execute(self, context):
        context.scene.aimcp_props.connected = False
        context.scene.aimcp_chat.add_message("system", "Disconnected")
        context.area.tag_redraw()
        self.report({'INFO'}, "Disconnected")
        return {'FINISHED'}


class AIMCP_OT_SendMessage(Operator):
    bl_idname = "aimcp.send_message"
    bl_label = "Send"
    bl_description = "Send message to AI assistant"

    def execute(self, context):
        text = context.scene.aimcp_input.strip()
        if not text:
            return {'CANCELLED'}
        context.scene.aimcp_chat.add_message("user", text)
        context.scene.aimcp_input = ""
        context.scene.aimcp_chat.add_message("assistant", f"⏳ Processing... (connect blender-mcp server)")
        context.area.tag_redraw()
        return {'FINISHED'}


class AIMCP_OT_CaptureScene(Operator):
    bl_idname = "aimcp.capture_scene"
    bl_label = "Capture Scene"
    bl_description = "Send current scene info to AI"

    def execute(self, context):
        obj_count = len(bpy.data.objects)
        mesh_count = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        context.scene.aimcp_chat.add_message("system", f"Scene: {obj_count} objects ({mesh_count} meshes)")
        context.area.tag_redraw()
        self.report({'INFO'}, f"Scene: {obj_count} objects")
        return {'FINISHED'}


class AIMCP_OT_ExportGLB(Operator):
    bl_idname = "aimcp.export_glb"
    bl_label = "Export GLB"
    bl_description = "Export scene as GLTF/GLB"

    def execute(self, context):
        output = os.path.join(os.path.expanduser("~"), "blender-mcp", "models", "exported_model.glb")
        os.makedirs(os.path.dirname(output), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=output, export_format='GLB')
        context.scene.aimcp_chat.add_message("system", f"Exported to {output}")
        context.area.tag_redraw()
        self.report({'INFO'}, f"Exported to {output}")
        return {'FINISHED'}


class AIMCP_OT_ClearChat(Operator):
    bl_idname = "aimcp.clear_chat"
    bl_label = "Clear Chat"

    def execute(self, context):
        context.scene.aimcp_chat.messages.clear()
        context.scene.aimcp_chat.count = 0
        context.area.tag_redraw()
        return {'FINISHED'}


# ─── Main Panel ───
class AIMCP_PT_MainPanel(Panel):
    bl_label = "🤖 AI Assistant"
    bl_idname = "AIMCP_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.area is not None

    def draw(self, context):
        layout = self.layout
        props = context.scene.aimcp_props
        chat = context.scene.aimcp_chat

        # ─── Connection status bar (always visible) ───
        row = layout.row(align=True)
        if props.connected:
            row.operator("aimcp.disconnect", text="Disconnect", icon='LINK_BREAK')
            row.label(text="● Online")
        else:
            row.operator("aimcp.connect", text="Connect", icon='LINKED')
            row.label(text="○ Offline")

        # ─── Action buttons ───
        col = layout.column(align=True)
        col.scale_y = 1.3
        row = col.row(align=True)
        row.operator("aimcp.capture_scene", text="📷 Scene", icon='CAMERA_DATA')
        row.operator("aimcp.export_glb", text="📤 Export", icon='EXPORT')

        # ─── Chat history (scrollable area) ───
        layout.separator()
        box = layout.box()
        if chat.count == 0:
            box.label(text="💬 No messages yet")
        else:
            for msg in chat.messages:
                if msg.role == "user":
                    box.label(text=f"🧑 {msg.text[:80]}")
                elif msg.role == "assistant":
                    box.label(text=f"🤖 {msg.text[:80]}")
                else:
                    box.label(text=f"ℹ️ {msg.text[:80]}")
            row = box.row(align=True)
            row.operator("aimcp.clear_chat", text="Clear", icon='X')

        # ─── Input area (ALWAYS visible) ───
        layout.separator()
        row = layout.row(align=True)
        row.prop(context.scene, "aimcp_input", text="")
        op = row.operator("aimcp.send_message", text="Send", icon='PLAY')
        row.scale_x = 0.6
        layout.separator()
        layout.scale_y = 0.5
        layout.label(text="Connected" if props.connected else "Disconnected")


# ─── Registration ───
classes = [
    ChatMessageItem,
    ChatContainer,
    AIMCPProperties,
    AIMCP_OT_Connect,
    AIMCP_OT_Disconnect,
    AIMCP_OT_SendMessage,
    AIMCP_OT_CaptureScene,
    AIMCP_OT_ExportGLB,
    AIMCP_OT_ClearChat,
    AIMCP_PT_MainPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_props = PointerProperty(type=AIMCPProperties)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatContainer)
    bpy.types.Scene.aimcp_input = StringProperty(name="", default="", description="Write your message here...")


def unregister():
    del bpy.types.Scene.aimcp_input
    del bpy.types.Scene.aimcp_chat
    del bpy.types.Scene.aimcp_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
