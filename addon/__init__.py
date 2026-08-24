"""
blender-mcp-ultra — Blender 4.0+ Addon
Socket server on :9876 for MCP protocol communication.
Professional UI panel with modeling, texturing, rigging, animation, characters, perception, export.
Self-contained — no external src/ dependencies.
"""

import json
import os
import socket
import sys
import threading
import time

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import Operator, Panel, PropertyGroup

bl_info = {
    "name": "blender-mcp-ultra",
    "blender": (4, 0, 0),
    "category": "System",
    "version": (2, 0, 0),
    "author": "CarlosH",
    "description": "Professional MCP server for Blender — modeling, texturing, rigging, animation, characters, perception, export",
}

_port = 9876


class AIChatMessage(PropertyGroup):
    """Single chat message."""

    role: StringProperty(default="user")
    content: StringProperty(default="")
    timestamp: StringProperty(default="")


class MCPUltraProperties(bpy.types.PropertyGroup):
    connected: BoolProperty(default=False)
    port: IntProperty(default=9876, name="Port")
    auto_start: BoolProperty(default=True, name="Auto-start Server")
    status: StringProperty(default="Disconnected")

    # Modeling
    primitive_type: bpy.props.EnumProperty(
        name="Primitive",
        items=[
            ("cube", "Cube", ""),
            ("sphere", "Sphere", ""),
            ("cylinder", "Cylinder", ""),
            ("cone", "Cone", ""),
            ("torus", "Torus", ""),
            ("capsule", "Capsule", ""),
            ("pyramid", "Pyramid", ""),
            ("star", "Star", ""),
            ("gear", "Gear", ""),
            ("spring", "Spring", ""),
        ],
        default="cube",
    )

    # Texturing
    material_type: bpy.props.EnumProperty(
        name="Material",
        items=[
            ("wood_oak", "Wood Oak", ""),
            ("wood_walnut", "Wood Walnut", ""),
            ("metal_gold", "Gold", ""),
            ("metal_silver", "Silver", ""),
            ("metal_chrome", "Chrome", ""),
            ("stone_marble", "Marble", ""),
            ("plastic_white", "Plastic White", ""),
            ("glass_clear", "Glass", ""),
            ("fabric_cotton", "Cotton", ""),
            ("leather_brown", "Leather", ""),
        ],
        default="wood_oak",
    )

    # Rigging
    rig_type: bpy.props.EnumProperty(
        name="Rig Type",
        items=[
            ("humanoid", "Humanoid", ""),
            ("quadruped", "Quadruped", ""),
        ],
        default="humanoid",
    )

    # Animation
    animation_type: bpy.props.EnumProperty(
        name="Animation",
        items=[
            ("walk", "Walk Cycle", ""),
            ("run", "Run Cycle", ""),
            ("idle", "Idle", ""),
            ("jump", "Jump", ""),
            ("wave", "Wave", ""),
            ("spin", "Spin", ""),
        ],
        default="walk",
    )

    # Character
    character_type: bpy.props.EnumProperty(
        name="Character",
        items=[
            ("humanoid", "Humanoid", ""),
            ("quadruped", "Quadruped", ""),
            ("avian", "Avian", ""),
            ("reptile", "Reptile", ""),
            ("fantasy", "Fantasy", ""),
        ],
        default="humanoid",
    )

    # Export
    export_format: bpy.props.EnumProperty(
        name="Format",
        items=[
            ("FBX", "FBX (Unity/Unreal)", ""),
            ("GLB", "glTF (Web/AR)", ""),
            ("STL", "STL (3D Print)", ""),
            ("OBJ", "OBJ (Universal)", ""),
            ("USD", "USD (Film)", ""),
        ],
        default="FBX",
    )

    # Quality
    target_quality: IntProperty(default=85, min=0, max=100, name="Target Quality")

    # Text to 3D
    text_description: StringProperty(default="", name="Description")

    # Image to 3D / References
    image_path: StringProperty(
        name="Image Path", description="Path to image file", subtype="FILE_PATH"
    )

    # ═══════════════════════════════════════════════════════════════
    # AI ASSISTANT PROPERTIES
    # ═══════════════════════════════════════════════════════════════

    # Chat
    chat_messages: CollectionProperty(type=AIChatMessage)
    chat_input: StringProperty(default="", name="Message")

    # Mode
    ui_mode: EnumProperty(
        name="Mode",
        items=[
            ("beginner", "Beginner", "Simple interface"),
            ("expert", "Expert", "Full control"),
        ],
        default="beginner",
    )

    # Voice
    voice_enabled: BoolProperty(default=False, name="Voice")

    # Preview
    preview_enabled: BoolProperty(default=True, name="Preview")
    preview_opacity: FloatProperty(default=0.5, min=0.0, max=1.0, name="Opacity")


class MCPUltraStartServer(Operator):
    bl_idname = "mcp_ultra.start_server"
    bl_label = "Start MCP Server"
    bl_description = "Start the TCP socket server on :9876"

    def execute(self, context):
        global _port
        try:
            from . import _axsock

            _axsock.start_socket_server()
            context.scene.mcp_ultra.connected = True
            context.scene.mcp_ultra.status = "Connected"
            self.report({"INFO"}, f"MCP Server started on :{_port}")
        except Exception as e:
            context.scene.mcp_ultra.status = f"Error: {e}"
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class MCPUltraStopServer(Operator):
    bl_idname = "mcp_ultra.stop_server"
    bl_label = "Stop MCP Server"
    bl_description = "Stop the TCP socket server"

    def execute(self, context):
        try:
            from . import _axsock

            _axsock.stop_socket_server()
            context.scene.mcp_ultra.connected = False
            context.scene.mcp_ultra.status = "Disconnected"
            self.report({"INFO"}, "MCP Server stopped")
        except Exception as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class MCPUltraPanel(Panel):
    bl_label = "MCP Ultra"
    bl_idname = "MCPUltra_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MCP"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.mcp_ultra

        layout.label(text=f"Status: {props.status}")
        layout.label(text=f"Port: {props.port}")

        row = layout.row(align=True)
        row.operator("mcp_ultra.start_server", text="Start Server", icon="PLAY")
        row.operator("mcp_ultra.stop_server", text="Stop Server", icon="PAUSE")


# Import and register UI panel
try:
    from .ui import mcp_panel

    ui_classes = mcp_panel.classes
    ui_register = mcp_panel.register
    ui_unregister = mcp_panel.unregister
except ImportError:
    ui_classes = ()
    ui_register = None
    ui_unregister = None


# Import and register AI Assistant
try:
    from .ui import ai_panel

    ai_classes = ai_panel.classes
    ai_register = ai_panel.register
    ai_unregister = ai_panel.unregister
except ImportError:
    ai_classes = ()
    ai_register = None
    ai_unregister = None


classes = (
    AIChatMessage,
    MCPUltraProperties,
    MCPUltraStartServer,
    MCPUltraStopServer,
    MCPUltraPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mcp_ultra = bpy.props.PointerProperty(type=MCPUltraProperties)

    # Register UI panels
    if ui_register:
        ui_register()

    # Register AI Assistant
    if ai_register:
        ai_register()

    try:
        from . import _axsock

        _axsock.start_socket_server()
        print("[blender-mcp-ultra] Socket server started on :9876")
    except Exception as e:
        print(f"[blender-mcp-ultra] Auto-start error: {e}")


def unregister():
    """Unregister addon classes."""
    try:
        from . import _axsock

        _axsock.stop_socket_server()
    except Exception:
        pass

    # Unregister AI Assistant
    if ai_unregister:
        ai_unregister()

    # Unregister UI panels
    if ui_unregister:
        ui_unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Delete properties
    try:
        del bpy.types.Scene.mcp_ultra
    except Exception:
        pass
