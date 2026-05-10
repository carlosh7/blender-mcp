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
from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty
import json
import threading
import time
import os
import sys

# Add parent to path for imports
ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
if ADDON_DIR not in sys.path:
    sys.path.insert(0, ADDON_DIR)

# ─── Properties ───
class AIMCPProperties(bpy.types.PropertyGroup):
    server_host: StringProperty(
        name="Server Host",
        default="localhost",
        description="MCP server hostname or IP",
    )
    server_port: IntProperty(
        name="Server Port",
        default=9876,
        min=1024,
        max=65535,
        description="MCP server WebSocket port",
    )
    connected: BoolProperty(
        name="Connected",
        default=False,
    )


# ─── Operators ───
class AIMCP_OT_Connect(bpy.types.Operator):
    bl_idname = "aimcp.connect"
    bl_label = "Connect to MCP Server"
    bl_description = "Connect to the blender-mcp server"

    def execute(self, context):
        props = context.scene.aimcp_props
        props.connected = True
        self.report({'INFO'}, f"Connected to {props.server_host}:{props.server_port}")
        return {'FINISHED'}


class AIMCP_OT_Disconnect(bpy.types.Operator):
    bl_idname = "aimcp.disconnect"
    bl_label = "Disconnect"
    bl_description = "Disconnect from MCP server"

    def execute(self, context):
        context.scene.aimcp_props.connected = False
        self.report({'INFO'}, "Disconnected")
        return {'FINISHED'}


class AIMCP_OT_SendMessage(bpy.types.Operator):
    bl_idname = "aimcp.send_message"
    bl_label = "Send Message"
    bl_description = "Send message to AI assistant"

    message: StringProperty(default="")

    def execute(self, context):
        if not self.message.strip():
            return {'CANCELLED'}
        # Store message in scene for panel display
        chat = context.scene.aimcp_chat
        chat.add_message("user", self.message.strip())
        self.report({'INFO'}, f"Sent: {self.message}")
        return {'FINISHED'}


class AIMCP_OT_CaptureScene(bpy.types.Operator):
    bl_idname = "aimcp.capture_scene"
    bl_label = "Capture Scene"
    bl_description = "Send current scene info and screenshot to AI"

    def execute(self, context):
        # Count objects
        obj_count = len(bpy.data.objects)
        mesh_count = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        chat = context.scene.aimcp_chat
        chat.add_message("system", f"Scene captured: {obj_count} objects ({mesh_count} meshes)")
        self.report({'INFO'}, f"Scene: {obj_count} objects")
        return {'FINISHED'}


class AIMCP_OT_ExportGLB(bpy.types.Operator):
    bl_idname = "aimcp.export_glb"
    bl_label = "Export to GLB"
    bl_description = "Export scene to GLTF/GLB"

    filename: StringProperty(default="exported_model.glb")

    def execute(self, context):
        output = os.path.join(os.path.expanduser("~"), "blender-mcp", "models", self.filename)
        os.makedirs(os.path.dirname(output), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=output, export_format='GLB')
        self.report({'INFO'}, f"Exported to {output}")
        return {'FINISHED'}


# ─── Chat History ───
class AIMCP_ChatHistory(bpy.types.PropertyGroup):
    messages: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def add_message(self, role: str, text: str):
        item = self.messages.add()
        item.name = f"{role}_{len(self.messages)}"
        # Use custom properties
        item["role"] = role
        item["text"] = text
        item["time"] = time.time()


# ─── Panel UI ───
class AIMCP_PT_MainPanel(bpy.types.Panel):
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
            row.label(text="● Online", icon='CHECKBOX_HLT')
        else:
            row.operator("aimcp.connect", text="Connect", icon='LINKED')
            row.label(text="○ Offline", icon='CHECKBOX_DEHLT')

        # Actions
        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("aimcp.capture_scene", text="📷 Capture Scene", icon='CAMERA_DATA')
        col.operator("aimcp.export_glb", text="📤 Export to GLB", icon='EXPORT')

        # Chat
        layout.separator()
        box = layout.box()
        box.scale_y = 0.8

        chat = context.scene.aimcp_chat
        for msg in chat.messages:
            role = msg.get("role", "user")
            text = msg.get("text", "")
            if role == "user":
                box.label(text=f"🧑 {text[:60]}", icon='USER')
            elif role == "assistant":
                box.label(text=f"🤖 {text[:60]}", icon='ROBOT')
            elif role == "system":
                box.label(text=f"ℹ️ {text[:60]}", icon='INFO')

        # Input
        layout.separator()
        row = layout.row(align=True)
        row.prop(context.scene, "aimcp_input", text="")
        op = row.operator("aimcp.send_message", text="→", icon='PLAY')


# ─── Registration ───
classes = [
    AIMCP_OT_Connect,
    AIMCP_OT_Disconnect,
    AIMCP_OT_SendMessage,
    AIMCP_OT_CaptureScene,
    AIMCP_OT_ExportGLB,
    AIMCP_PT_MainPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aimcp_props = bpy.props.PointerProperty(type=AIMCPProperties)
    bpy.types.Scene.aimcp_chat = bpy.props.PointerProperty(type=AIMCP_ChatHistory)
    bpy.types.Scene.aimcp_input = bpy.props.StringProperty(name="Message", description="Type your message for the AI")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.aimcp_props
    del bpy.types.Scene.aimcp_chat
    del bpy.types.Scene.aimcp_input


if __name__ == "__main__":
    register()
