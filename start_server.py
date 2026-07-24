#!/usr/bin/env python3
"""Start Blender MCP server."""
# Monkey-patch bpy.context for Blender 5.2 background mode
# Many operators check bpy.context.active_object which doesn't
# exist in background mode. We add it using the view_layer.
import bpy

# Try to access active_object - it doesn't exist in background mode
if not hasattr(bpy.types.Context, 'active_object'):
    # Add it as a property that delegates to view_layer
    def _get_active_obj(self):
        try:
            return self.view_layer.objects.active
        except:
            return None
    try:
        from bpy.types import Context as BpyContext
        BpyContext.active_object = property(_get_active_obj)
        print("[MCP] Patched bpy.context.active_object for background mode")
    except Exception as e:
        print(f"[MCP] Could not patch active_object: {e}")
import sys
import os
import time

sys.path.insert(0, '/home/carlosh/blender-mcp/src')

from infrastructure.network import SocketServer
from tools import ToolRegistry
from tools.scene import TOOLS as t1, HANDLERS as h1
from tools.objects import TOOLS as t2, HANDLERS as h2
from tools.materials import TOOLS as t3, HANDLERS as h3
from tools.lights import TOOLS as t4, HANDLERS as h4
from tools.modifiers import TOOLS as t5, HANDLERS as h5
from tools.animation import TOOLS as t6, HANDLERS as h6
from tools.camera import TOOLS as t7, HANDLERS as h7
from tools.render import TOOLS as t8, HANDLERS as h8
from tools.io import TOOLS as t9, HANDLERS as h9
from tools.uv_texture import TOOLS as t10, HANDLERS as h10
from tools.rigging import TOOLS as t11, HANDLERS as h11
from tools.batch import TOOLS as t12, HANDLERS as h12
from tools.scene_utils import TOOLS as t13, HANDLERS as h13
from tools.printing import TOOLS as t14, HANDLERS as h14
from tools.shader_nodes import TOOLS as t15, HANDLERS as h15
from tools.geometry_nodes import TOOLS as t16, HANDLERS as h16

registry = ToolRegistry()
for tools, handlers in [(t1,h1),(t2,h2),(t3,h3),(t4,h4),(t5,h5),(t6,h6),(t7,h7),(t8,h8),(t9,h9),(t10,h10),(t11,h11),(t12,h12),(t13,h13),(t14,h14),(t15,h15),(t16,h16)]:
    for tool in tools:
        if tool.name in handlers:
            registry.register_tool(tool, handlers[tool.name])

server = SocketServer(port=9876)

def h_execute_code(code=''):
    import io
    from contextlib import redirect_stdout
    try:
        bpy.ops.ed.undo_push(message='MCP')
    except:
        pass
    buf = io.StringIO()
    with redirect_stdout(buf):
        exec(compile(code, '<mcp>', 'exec'), {'bpy': bpy, 'C': bpy.context, 'D': bpy.data})
    return {'output': buf.getvalue()}

def h_scene_info():
    s = bpy.context.scene
    return {
        'name': s.name,
        'object_count': len(s.objects),
        'objects': [{'name': o.name, 'type': o.type, 'location': [o.location.x, o.location.y, o.location.z]} for o in s.objects]
    }

def h_tool(tool_name='', params=None):
    return registry.execute_tool(tool_name, params or {}).to_dict()

def h_ping():
    return {'pong': True, 'version': '1.0.0', 'tools': len(registry.list_tools())}

def h_list_tools():
    return {'tools': [t.to_dict() for t in registry.list_tools()]}

server.register_handler('execute_code', h_execute_code)
server.register_handler('get_scene_info', h_scene_info)
server.register_handler('tool', h_tool)
server.register_handler('ping', h_ping)
server.register_handler('list_tools', h_list_tools)

if server.start():
    print(f'SERVER_READY port=9876 tools={len(registry.list_tools())}')
    while True:
        time.sleep(1)
else:
    print('SERVER_FAILED')
