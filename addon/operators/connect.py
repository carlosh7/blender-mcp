"""
blender-mcp — Connection Operators
"""
import bpy
import os
import json
import threading
import urllib.request
from bpy.types import Operator
from bpy.props import StringProperty
from .. import _axsock as bsock


class OP_Check(Operator):
    bl_idname = "aimcp.check"
    bl_label = "Check Connection"

    def execute(self, ctx):
        ctx.scene.aimcp_status = "Checking..."
        if ctx.area:
            ctx.area.tag_redraw()
        connected = bsock._socket_server is not None and bsock._socket_server.running
        ctx.scene.aimcp_connected = connected
        ctx.scene.aimcp_status = "Connected" if connected else "Socket not running"
        if ctx.area:
            ctx.area.tag_redraw()
        return {'FINISHED'}


class OP_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"
    bl_label = "Disconnect"

    def execute(self, ctx):
        bsock.stop_socket_server()
        ctx.scene.aimcp_connected = False
        ctx.scene.aimcp_status = ""
        if ctx.area:
            ctx.area.tag_redraw()
        return {'FINISHED'}


CONNECT_OPERATORS = [OP_Check, OP_Disconnect]


def register_connect_operators():
    from bpy.utils import register_class
    for cls in CONNECT_OPERATORS:
        register_class(cls)


def unregister_connect_operators():
    from bpy.utils import unregister_class
    for cls in reversed(CONNECT_OPERATORS):
        unregister_class(cls)
