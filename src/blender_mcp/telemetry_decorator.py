"""
blender-mcp — Telemetry Decorator
Wrap MCP tools with automatic telemetry recording.
Usage:
    @telemetry_tool("get_scene_info")
    @mcp.tool()
    def get_scene_info(): ...
"""
import time
import functools
from .telemetry import record_tool


def telemetry_tool(tool_name: str = None):
    """Decorator that records telemetry for MCP tool calls."""
    def decorator(func):
        name = tool_name or func.__name__
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                record_tool(name, success=True, duration_ms=duration)
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                record_tool(name, success=False, duration_ms=duration, error=str(e))
                raise
        return wrapper
    return decorator
