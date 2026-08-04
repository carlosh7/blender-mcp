"""
blender-mcp-ultra — Blender 4.0+ Addon
Socket server on :9876 for MCP protocol communication.
Self-contained — no external src/ dependencies.
"""
import bpy
import sys
import os
import json
import socket
import threading
import time
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Operator, Panel

bl_info = {
    "name": "blender-mcp-ultra",
    "blender": (4, 0, 0),
    "category": "System",
    "version": (1, 0, 0),
    "author": "CarlosH",
    "description": "MCP server for Blender — socket on :9876",
}

_port = 9876


class MCPUltraProperties(bpy.types.PropertyGroup):
    connected: BoolProperty(default=False)
    port: IntProperty(default=9876, name="Port")
    auto_start: BoolProperty(default=True, name="Auto-start Server")
    status: StringProperty(default="Disconnected")


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
            self.report({'INFO'}, f"MCP Server started on :{_port}")
        except Exception as e:
            context.scene.mcp_ultra.status = f"Error: {e}"
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


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
            self.report({'INFO'}, "MCP Server stopped")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class MCPUltraPanel(Panel):
    bl_label = "MCP Ultra"
    bl_idname = "MCPUltra_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.mcp_ultra

        layout.label(text=f"Status: {props.status}")
        layout.label(text=f"Port: {props.port}")

        row = layout.row(align=True)
        row.operator("mcp_ultra.start_server", text="Start Server", icon='PLAY')
        row.operator("mcp_ultra.stop_server", text="Stop Server", icon='PAUSE')


classes = (
    MCPUltraProperties,
    MCPUltraStartServer,
    MCPUltraStopServer,
    MCPUltraPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mcp_ultra = bpy.props.PointerProperty(type=MCPUltraProperties)

    try:
        from . import _axsock
        _axsock.start_socket_server()
    except Exception as e:
        print(f"[blender-mcp-ultra] Auto-start error: {e}")


def unregister():
    try:
        from . import _axsock
        _axsock.stop_socket_server()
    except:
        pass
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mcp_ultra
