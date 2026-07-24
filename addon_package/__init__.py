"""
blender-mcp-ultra — Blender 5.2 Addon
Main registration file for Blender extension system.
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

# Add src to path
_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(os.path.dirname(_dir), 'src')
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

bl_info = {
    "name": "blender-mcp-ultra",
    "blender": (4, 0, 0),
    "category": "System",
    "version": (1, 0, 0),
    "author": "CarlosH",
    "description": "The most complete MCP server for Blender — 118+ tools",
}

# Global state
_socket_server = None
_mcp_process = None
_connected = False
_port = 9876


class MCPUltraProperties(bpy.types.PropertyGroup):
    """Properties for the MCP Ultra addon."""
    connected: BoolProperty(default=False)
    port: IntProperty(default=9876, name="Port")
    auto_start: BoolProperty(default=True, name="Auto-start Server")
    status: StringProperty(default="Disconnected")


class MCPUltraStartServer(Operator):
    """Start the MCP Ultra socket server."""
    bl_idname = "mcp_ultra.start_server"
    bl_label = "Start MCP Server"
    bl_description = "Start the TCP socket server for MCP connection"

    def execute(self, context):
        global _socket_server
        try:
            from infrastructure.network import SocketServer
            from tools import ToolRegistry
            from tools.scene import TOOLS as scene_tools, HANDLERS as scene_handlers
            from tools.objects import TOOLS as obj_tools, HANDLERS as obj_handlers
            from tools.materials import TOOLS as mat_tools, HANDLERS as mat_handlers
            from tools.lights import TOOLS as light_tools, HANDLERS as light_handlers
            from tools.modifiers import TOOLS as mod_tools, HANDLERS as mod_handlers
            from tools.animation import TOOLS as anim_tools, HANDLERS as anim_handlers

            registry = ToolRegistry()

            # Register tools
            for tools, handlers in [(scene_tools, scene_handlers), (obj_tools, obj_handlers),
                                     (mat_tools, mat_handlers), (light_tools, light_handlers),
                                     (mod_tools, mod_handlers), (anim_tools, anim_handlers)]:
                for tool in tools:
                    if tool.name in handlers:
                        registry.register_tool(tool, handlers[tool.name])

            # Create server with handlers
            port = context.scene.mcp_ultra.port
            server = SocketServer(port=port)

            # Register command handlers
            def handle_execute_code(code=""):
                try:
                    import io
                    from contextlib import redirect_stdout
                    bpy.ops.ed.undo_push(message="MCP Ultra")
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        compiled = compile(code, "<mcp_code>", "exec")
                        exec(compiled, {"bpy": bpy, "C": bpy.context, "D": bpy.data})
                    return {"output": buf.getvalue()}
                except Exception as e:
                    return {"error": str(e)}

            def handle_get_scene_info():
                scene = bpy.context.scene
                objects = []
                for obj in scene.objects:
                    objects.append({
                        "name": obj.name,
                        "type": obj.type,
                        "location": list(obj.location),
                    })
                return {"name": scene.name, "object_count": len(scene.objects), "objects": objects}

            def handle_tool(tool_name="", params=None):
                result = registry.execute_tool(tool_name, params or {})
                return result.to_dict()

            def handle_ping():
                return {"pong": True, "version": "1.0.0", "tools": len(registry.list_tools())}

            server.register_handler("execute_code", handle_execute_code)
            server.register_handler("get_scene_info", handle_get_scene_info)
            server.register_handler("tool", handle_tool)
            server.register_handler("ping", handle_ping)

            if server.start():
                _socket_server = server
                context.scene.mcp_ultra.connected = True
                context.scene.mcp_ultra.status = f"Running on port {port}"
                self.report({'INFO'}, f"MCP Server started on port {port}")
            else:
                self.report({'ERROR'}, "Failed to start MCP server")
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")

        return {'FINISHED'}


class MCPUltraStopServer(Operator):
    """Stop the MCP Ultra socket server."""
    bl_idname = "mcp_ultra.stop_server"
    bl_label = "Stop MCP Server"
    bl_description = "Stop the TCP socket server"

    def execute(self, context):
        global _socket_server
        if _socket_server:
            _socket_server.stop()
            _socket_server = None
        context.scene.mcp_ultra.connected = False
        context.scene.mcp_ultra.status = "Disconnected"
        self.report({'INFO'}, "MCP Server stopped")
        return {'FINISHED'}


class MCPUltraTestConnection(Operator):
    """Test the MCP connection."""
    bl_idname = "mcp_ultra.test_connection"
    bl_label = "Test Connection"
    bl_description = "Test connection to MCP server"

    def execute(self, context):
        port = context.scene.mcp_ultra.port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("localhost", port))
            cmd = json.dumps({"command": "ping", "params": {}})
            sock.sendall(cmd.encode())
            resp = sock.recv(4096)
            data = json.loads(resp.decode())
            sock.close()
            if data.get("pong"):
                tools = data.get("tools", 0)
                self.report({'INFO'}, f"Connected! {tools} tools available")
            else:
                self.report({'WARNING'}, "Server responded but no pong")
        except Exception as e:
            self.report({'ERROR'}, f"Connection failed: {str(e)}")
        return {'FINISHED'}


class MCPUltraPanel(Panel):
    """Main panel for blender-mcp-ultra."""
    bl_label = "MCP Ultra"
    bl_idname = "MCPUltra_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MCP Ultra"

    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_ultra

        # Status
        row = layout.row()
        if props.connected:
            row.label(text=f"Status: {props.status}", icon='CHECKMARK')
        else:
            row.label(text="Status: Disconnected", icon='X')

        # Port
        layout.prop(props, "port")

        # Buttons
        row = layout.row(align=True)
        if not props.connected:
            row.operator("mcp_ultra.start_server", icon='PLAY')
        else:
            row.operator("mcp_ultra.stop_server", icon='PAUSE')

        row.operator("mcp_ultra.test_connection", icon='VIEWZOOM')

        # Info
        if props.connected:
            box = layout.box()
            box.label(text="Server Running", icon='INFO')
            box.label(text=f"Port: {props.port}")
            box.label(text="Connect with MCP client")


# Registration
classes = (
    MCPUltraProperties,
    MCPUltraStartServer,
    MCPUltraStopServer,
    MCPUltraTestConnection,
    MCPUltraPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mcp_ultra = bpy.props.PointerProperty(type=MCPUltraProperties)
    print("[blender-mcp-ultra] Registered")


def unregister():
    global _socket_server
    if _socket_server:
        _socket_server.stop()
        _socket_server = None
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mcp_ultra
    print("[blender-mcp-ultra] Unregistered")


if __name__ == "__main__":
    register()
