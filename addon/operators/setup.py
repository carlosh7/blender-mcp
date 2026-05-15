"""
blender-mcp — Setup Operators (cross-platform)
"""
import bpy
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from bpy.types import Operator

from ..platform_utils import get_log_dir


class BLENDERMCP_OT_InstallDeps(Operator):
    bl_idname = "blendermcp.install_deps"
    bl_label = "Check/Install Dependencies"

    def execute(self, context):
        self.report({'INFO'}, "Checking dependencies...")
        root = os.path.dirname(os.path.dirname(__file__))
        req_file = os.path.join(root, "requirements.txt")
        if not os.path.exists(req_file):
            self.report({'INFO'}, "No requirements.txt, checking pip packages...")
            self.report({'INFO'}, "Dependencies are auto-installed on activation")
            return {'FINISHED'}
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-r", req_file, "--quiet"]
            if sys.prefix == sys.base_prefix:
                cmd.append("--break-system-packages")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.report({'INFO'}, "Dependencies installed")
            else:
                self.report({'WARNING'}, f"Deps check: {result.stderr[:100]}")
        except Exception as e:
            self.report({'ERROR'}, f"Error: {e}")
        return {'FINISHED'}


class BLENDERMCP_OT_CopyConfig(Operator):
    bl_idname = "blendermcp.copy_config"
    bl_label = "Copy MCP Client Config"

    def execute(self, context):
        config = {
            "mcpServers": {
                "blender": {
                    "command": "uvx",
                    "args": ["blender-mcp"],
                }
            }
        }
        # Try to copy to clipboard
        text = json.dumps(config, indent=2)
        context.window_manager.clipboard = text
        self.report({'INFO'}, "Config copied to clipboard for Claude Desktop / Cursor")
        return {'FINISHED'}


class BLENDERMCP_OT_OpenLogs(Operator):
    bl_idname = "blendermcp.open_logs"
    bl_label = "Open Logs"

    def execute(self, context):
        log_path = str(get_log_dir())
        main_log = str(get_log_dir() / "blender_mcp.log")
        try:
            if sys.platform == "win32":
                os.startfile(log_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", log_path])
            else:
                subprocess.Popen(["xdg-open", log_path])
            self.report({'INFO'}, f"Opened logs at {log_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Could not open logs: {e}")
        return {'FINISHED'}


class BLENDERMCP_OT_HealthCheck(Operator):
    bl_idname = "blendermcp.health_check"
    bl_label = "Health Check"

    def execute(self, context):
        import socket
        host = "localhost"
        port = 9876
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect((host, port))
            self.report({'INFO'}, f"Socket OK on {host}:{port}")
            s.close()
        except:
            self.report({'WARNING'}, f"Socket NOT responding on {host}:{port}")
        return {'FINISHED'}


class BLENDERMCP_OT_StartMCP(Operator):
    bl_idname = "blendermcp.start_mcp"
    bl_label = "Start MCP Server"

    def execute(self, context):
        import threading
        def _run():
            try:
                import sys, os
                ext_root = os.path.dirname(os.path.abspath(__file__))
                ext_root = os.path.dirname(ext_root)
                if ext_root not in sys.path:
                    sys.path.insert(0, ext_root)
                import uvicorn
                from mcp.server.fastmcp import FastMCP
                from mcp.types import ToolAnnotations
                from blender_connection import get_blender
                _mcp = FastMCP("blender-mcp", log_level="INFO")
                @_mcp.tool(**dict(annotations=ToolAnnotations(readOnlyHint=True)))
                def get_scene_info() -> str:
                    import json
                    return json.dumps(get_blender().send_command("get_scene_info"), indent=2)
                @_mcp.tool(**dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True)))
                def execute_blender_code(code: str) -> str:
                    r = get_blender().send_command("execute_code", {"code": code})
                    return f"Salida:\n{r.get('output', '')}"
                uvicorn.run(_mcp.sse_app(), host="127.0.0.1", port=9879, log_level="warning")
            except Exception as e:
                print(f"[blender-mcp] MCP start: {e}")
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        self.report({'INFO'}, "MCP server starting on :9879")
        return {'FINISHED'}


SETUP_OPERATORS = [
    BLENDERMCP_OT_InstallDeps,
    BLENDERMCP_OT_CopyConfig,
    BLENDERMCP_OT_OpenLogs,
    BLENDERMCP_OT_HealthCheck,
    BLENDERMCP_OT_StartMCP,
]


def register_setup_operators():
    from bpy.utils import register_class
    for cls in SETUP_OPERATORS:
        try: register_class(cls)
        except: pass


def unregister_setup_operators():
    from bpy.utils import unregister_class
    for cls in reversed(SETUP_OPERATORS):
        unregister_class(cls)
