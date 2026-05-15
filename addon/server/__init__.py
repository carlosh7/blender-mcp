"""
blender-mcp — Embedded Server (simplified)
HTTP API (:9877) for basic health checks.
MCP tool execution now goes through _axsock.py socket.
"""
import bpy
import threading
import logging

logger = logging.getLogger("blender-mcp-embedded")
_server_instance = None
_http_instance = None


def _build_server():
    return None


def start_embedded_server():
    global _server_instance, _http_instance
    if _server_instance:
        return _server_instance
    _server_instance = True
    try:
        from .mini_http import start as start_http
        start_http()
        _http_instance = True
    except Exception as e:
        print(f"[EMBEDDED] HTTP API error: {e}")
    return _server_instance


def stop_embedded_server():
    global _server_instance, _http_instance
    _server_instance = None
    if _http_instance:
        try:
            from .mini_http import stop as stop_http
            stop_http()
        except:
            pass
        _http_instance = None
