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
        # Quick health check
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


class BLENDERMCP_OT_SetHyper3DFreeTrial(Operator):
    bl_idname = "blendermcp.set_hyper3d_free_trial"
    bl_label = "Set Free Trial API Key"

    def execute(self, context):
        context.scene.blendermcp_hyper3d_api_key = "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"
        context.scene.blendermcp_hyper3d_mode = 'MAIN_SITE'
        self.report({'INFO'}, "Hyper3D Free Trial key set")
        return {'FINISHED'}


SETUP_OPERATORS = [
    BLENDERMCP_OT_InstallDeps,
    BLENDERMCP_OT_CopyConfig,
    BLENDERMCP_OT_OpenLogs,
    BLENDERMCP_OT_HealthCheck,
    BLENDERMCP_OT_SetHyper3DFreeTrial,
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
