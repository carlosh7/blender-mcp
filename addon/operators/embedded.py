"""
blender-mcp — Embedded Mode Operators
Auto-start on addon activation. User just types and sends.
"""
import bpy
import json
import os
import sys
import time
import threading
import logging
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

logger = logging.getLogger("blender-mcp-embedded")

_embedded_client = None
_embedded_server = None
_auto_started = False


def auto_start():
    """Called from addon/__init__.py register(). Starts server + client."""
    global _embedded_server, _auto_started
    if _auto_started:
        return

    # Start embedded MCP server (tool execution)
    try:
        from ..server import start_embedded_server
        _embedded_server = start_embedded_server()
        logger.info("Embedded MCP server started")
    except Exception as e:
        logger.warning(f"Embedded server: {e}")

    _auto_started = True


def auto_stop():
    """Called from addon/__init__.py unregister()."""
    global _embedded_client, _embedded_server, _auto_started
    if _embedded_client:
        try:
            _embedded_client.stop()
        except:
            pass
        _embedded_client = None
    if _embedded_server:
        try:
            from ..server import stop_embedded_server
            stop_embedded_server()
        except:
            pass
        _embedded_server = None
    _auto_started = False


class BLENDERMCP_OT_StartEmbedded(Operator):
    bl_idname = "blendermcp.start_embedded"
    bl_label = "Start Local AI"
    bl_description = "Connect to local LLM (Ollama/OpenAI) for embedded AI"

    def execute(self, context):
        global _embedded_client, _embedded_server
        scene = context.scene

        # Server should already be running from auto_start()
        if _embedded_server is None:
            from ..server import start_embedded_server
            _embedded_server = start_embedded_server()

        if _embedded_client is None:
            provider = scene.aimcp_provider or "opencode-go"
            api_key = os.environ.get("OPENAI_API_KEY") or ""
            self._start_client(provider, api_key)
            self.report({'INFO'}, f"Local AI ready")

        scene.aimcp_ai_state = "connected"
        return {'FINISHED'}

    def _start_client(self, provider, api_key):
        global _embedded_client
        providers = {
            "anthropic": ("addon.client.claude", "MCPClientClaude"),
            "deepseek": ("addon.client.openai", "MCPClientDeepSeek"),
            "openrouter": ("addon.client.openai", "MCPClientOpenRouter"),
            "google": ("addon.client.openai", "MCPClientGoogle"),
            "ollama": ("addon.client.ollama", "MCPClientOllama"),
        }
        import importlib
        mod_path, cls_name = providers.get(provider, ("addon.client.openai", "MCPClientOpenAI"))
        mod = importlib.import_module(mod_path)
        cls = getattr(mod, cls_name)
        _embedded_client = cls()
        _embedded_client.start()


class BLENDERMCP_OT_StopEmbedded(Operator):
    bl_idname = "blendermcp.stop_embedded"
    bl_label = "Stop Local AI"

    def execute(self, context):
        global _embedded_client
        if _embedded_client:
            _embedded_client.stop()
            _embedded_client = None
        context.scene.aimcp_ai_state = "disconnected"
        self.report({'INFO'}, "Local AI stopped")
        return {'FINISHED'}


EMBEDDED_OPERATORS = [
    BLENDERMCP_OT_StartEmbedded,
    BLENDERMCP_OT_StopEmbedded,
]


def register_embedded_operators():
    from bpy.utils import register_class
    for cls in EMBEDDED_OPERATORS:
        register_class(cls)


def unregister_embedded_operators():
    from bpy.utils import unregister_class
    for cls in reversed(EMBEDDED_OPERATORS):
        unregister_class(cls)
