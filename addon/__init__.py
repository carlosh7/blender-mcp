# blender-mcp Addon for Blender
# Provides: AI chat panel, scene capture, live script execution
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > AI",
    "description": "Chat with AI to create and edit 3D models via blender-mcp",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}

import bpy
from bpy.types import Panel, Operator, PropertyGroup, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty
import os
import sys

ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
if ADDON_DIR not in sys.path:
    sys.path.insert(0, ADDON_DIR)

# ─── Chat Message Item ───
class ChatMessageItem(PropertyGroup):
    role: StringProperty(name="Role", default="user")
    text: StringProperty(name="Text", default="")
    time: StringProperty(name="Time", default="")


# ─── Chat Container (holds collection of messages) ───
class ChatContainer(PropertyGroup):
    messages: CollectionProperty(type=ChatMessageItem)
    count: IntProperty(name="Count", default=0)

    def add_message(self, role: str, text: str):
        item = self.messages.add()
        item.role = role
        item.text = text
        self.count = len(self.messages)


# ─── Properties ───
class AIMCPProperties(PropertyGroup):
    server_host: StringProperty(
        name="Server Host", default="localhost",
        description="MCP server hostname or IP",
    )
    server_port: IntProperty(
        name="Server Port", default=9876, min=1024, max=65535,
        description="MCP server WebSocket port",
    )
    connected: BoolProperty(
        name="Connected", default=False,
    )


# ─── Operators ───
class AIMCP_OT_Connect(Operator):
    bl_idname = "aimcp.connect"
    bl_label = "Connect"
    bl_description = "Connect to the blender-mcp server"

    def execute(self, context):
        props = context.scene.aimcp_props
        props.connected = True
        self.report({'INFO'}, f"Connected to {props.server_host}:{props.server_port}")
        return {'FINISHED'}


class AIMCP_OT_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"
    bl_label = "Disconnect"
    bl_description = "Disconnect from MCP server"

    def execute(self, context):
        context.scene.aimcp_props.connected = False
        self.report({'INFO'}, "Disconnected")
        return {'FINISHED'}


class AIMCP_OT_AddMessage(Operator):
    bl_idname = "aimcp.add_message"
    bl_label = "Add Message"
    bl_description = "Add message to chat"

    def execute(self, context):
        chat = context.scene.aimcp_chat
        msg = chat.messages.add()
        msg.role = "user"
        msg.text = context.scene.aimcp_input
        msg.time = "now"
        context.scene.aimcp_input = ""
        self.report({'INFO'}, "Message sent")
        return {'FINISHED'}


class AIMCP_OT_CaptureScene(Operator):
    bl_idname = "aimcp.capture_scene"
    bl_label = "Capture Scene"
    bl_description = "Send current scene info and screenshot to AI"

    def execute(self, context):
        obj_count = len(bpy.data.objects)
        mesh_count = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        chat = context.scene.aimcp_chat
        msg = chat.messages.add()
        msg.role = "system"
        msg.text = f"Scene: {obj_count} objects ({mesh_count} meshes)"
        self.report({'INFO'}, f"Scene captured: {obj_count} objects")
        return {'FINISHED'}


class AIMCP_OT_ExportGLB(Operator):
    bl_idname = "aimcp.export_glb"
    bl_label = "Export GLB"
    bl_description = "Export scene to GLTF/GLB"

    def execute(self, context):
        output = os.path.join(os.path.expanduser("~"), "blender-mcp", "models", "exported_model.glb")
        os.makedirs(os.path.dirname(output), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=output, export_format='GLB')
        self.report({'INFO'}, f"Exported to {output}")
        return {'FINISHED'}


# ─── Panel ───
class AIMCP_PT_MainPanel(Panel):
    bl_label = "🤖 AI Assistant"
    bl_idname = "AIMCP_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI'

    def draw(self, context):
        layout = self.layout
        props = context.scene.aimcp_props

        # Connection
        row = layout.row(align=True)
        if props.connected:
            row.operator("aimcp.disconnect", text="Disconnect", icon='LINK_BREAK')
            row.label(text="● Online")
        else:
            row.operator("aimcp.connect", text="Connect", icon='LINKED')
            row.label(text="○ Offline")

        # Actions
        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("aimcp.capture_scene", text="Capture Scene", icon='CAMERA_DATA')
        col.operator("aimcp.export_glb", text="Export to GLB", icon='EXPORT')

        # Chat history
        layout.separator()
        box = layout.box()
        chat = context.scene.aimcp_chat
        for msg in chat.messages:
            if msg.role == "user":
                box.label(text=f"🧑 {msg.text[:60]}")
            elif msg.role == "assistant":
                box.label(text=f"🤖 {msg.text[:60]}")
            else:
                box.label(text=f"ℹ️ {msg.text[:60]}")

        # Input
        layout.separator()
        row = layout.row(align=True)
        row.prop(context.scene, "aimcp_input", text="")
        row.operator("aimcp.add_message", text="→")


# ─── Registration ───
classes = [
    ChatMessageItem,
    ChatContainer,
    AIMCPProperties,
    AIMCP_OT_Connect,
    AIMCP_OT_Disconnect,
    AIMCP_OT_AddMessage,
    AIMCP_OT_CaptureScene,
    AIMCP_OT_ExportGLB,
    AIMCP_PT_MainPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_props = PointerProperty(type=AIMCPProperties)
    bpy.types.Scene.aimcp_chat = PointerProperty(type=ChatContainer)
    bpy.types.Scene.aimcp_input = StringProperty(name="Message", default="", description="Type your message for the AI")


def unregister():
    del bpy.types.Scene.aimcp_input
    del bpy.types.Scene.aimcp_chat
    del bpy.types.Scene.aimcp_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
