"""
blender-mcp — Embedded Mode Operators
Auto-start on addon activation. Auto-detects Ollama if available.
"""
import bpy
import json
import os
import sys
import time
import threading
import logging
import urllib.request
from bpy.types import Operator

logger = logging.getLogger("blender-mcp-embedded")

_embedded_client = None
_embedded_server = None
_auto_started = False


def _check_ollama():
    """Check if Ollama is running locally."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/version", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read())
            return data.get("version", "")
    except Exception:
        return None


def auto_start():
    """Called from addon/__init__.py register(). Auto-detects Ollama."""
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

    # Auto-detect Ollama
    ollama_ver = _check_ollama()
    if ollama_ver:
        logger.info(f"Ollama detected (v{ollama_ver}), auto-starting local AI")
        _auto_start_client("ollama", "")
        _auto_started = True
        return

    _auto_started = True


def _auto_start_client(provider, api_key):
    global _embedded_client
    try:
        if provider == "ollama":
            from ..client.ollama import MCPClientOllama
            _embedded_client = MCPClientOllama()
        elif provider == "anthropic":
            from ..client.claude import MCPClientClaude
            _embedded_client = MCPClientClaude()
        elif provider == "deepseek":
            from ..client.openai import MCPClientDeepSeek
            _embedded_client = MCPClientDeepSeek()
        elif provider == "openrouter":
            from ..client.openai import MCPClientOpenRouter
            _embedded_client = MCPClientOpenRouter()
        elif provider == "google":
            from ..client.openai import MCPClientGoogle
            _embedded_client = MCPClientGoogle()
        else:
            from ..client.openai import MCPClientOpenAI
            _embedded_client = MCPClientOpenAI()
        _embedded_client.start()
        logger.info(f"Embedded client started: {provider}")
    except Exception as e:
        logger.warning(f"Could not start embedded client: {e}")


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
        global _embedded_client
        scene = context.scene

        provider = scene.aimcp_provider or "opencode-go"
        env_map = {"opencode-go": "OPENAI_API_KEY", "openai": "OPENAI_API_KEY",
                   "deepseek": "DEEPSEEK_API_KEY", "openrouter": "OPENROUTER_API_KEY",
                   "anthropic": "ANTHROPIC_API_KEY", "google": "GOOGLE_API_KEY"}
        api_key = os.environ.get(env_map.get(provider, ""), "")

        _auto_start_client(provider, api_key)
        if _embedded_client:
            scene.aimcp_ai_state = "connected"
            self.report({'INFO'}, f"Local AI ready ({provider})")
        else:
            scene.aimcp_ai_state = "no_mcp"
            self.report({'WARNING'}, "Could not start AI. Check API key or Ollama.")
        return {'FINISHED'}


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
        try: register_class(cls)
        except: pass


def unregister_embedded_operators():
    from bpy.utils import unregister_class
    for cls in reversed(EMBEDDED_OPERATORS):
        unregister_class(cls)
