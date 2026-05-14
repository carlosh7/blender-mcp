"""
blender-mcp — Embedded MCP Server + HTTP API (inside Blender)
FastMCP server (SSE :45677) + Mini REST API (:9877)
"""
import bpy
import json
import threading
import logging
import functools
from typing import Any

logger = logging.getLogger("blender-mcp-embedded")
_server_instance = None
_http_instance = None
_timer_queue = []


def _run_in_main_thread(func, *args, **kwargs):
    """Queue a function call to run on Blender's main thread via timer."""
    result_container = {}
    event = threading.Event()

    def wrapper():
        try:
            result_container["result"] = func(*args, **kwargs)
        except Exception as e:
            result_container["error"] = str(e)
        event.set()
        return None

    bpy.app.timers.register(wrapper, first_interval=0.01)
    event.wait(timeout=30)
    if "error" in result_container:
        raise Exception(result_container["error"])
    return result_container.get("result")


def _discover_tools():
    """Discover all cmd_* functions from handler modules and wrap them for FastMCP."""
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("blender-mcp-embedded", log_level="WARNING")

    handler_modules = [
        "scene", "objects", "materials", "modifiers", "lights", "camera",
        "shader_nodes", "animation", "geometry_nodes", "render",
        "io", "uv_texture", "batch", "rigging", "scene_utils", "printing",
        "polyhaven", "sketchfab", "hyper3d", "hunyuan", "ambientcg",
    ]

    for mod_name in handler_modules:
        try:
            mod = __import__(f"addon.handlers.{mod_name}", fromlist=[mod_name])
        except ImportError:
            continue

        # Collect functions
        cmd_funcs = {}
        for attr_name in dir(mod):
            if attr_name.startswith("cmd_") and callable(getattr(mod, attr_name)):
                cmd_name = attr_name[4:]
                cmd_funcs[cmd_name] = getattr(mod, attr_name)

        # Also check class-based handlers
        for attr_name in dir(mod):
            if attr_name.endswith("Handler"):
                handler_cls = getattr(mod, attr_name)
                for method_name in dir(handler_cls):
                    if method_name.startswith("cmd_") and callable(getattr(handler_cls, method_name)):
                        cmd_name = method_name[4:]
                        func = getattr(handler_cls, method_name)
                        if cmd_name not in cmd_funcs:
                            cmd_funcs[cmd_name] = staticmethod(func)

        # Register each as a tool
        for cmd_name, func in cmd_funcs.items():
            # Wrap to run in Blender's main thread
            @functools.wraps(func)
            def make_tool(f=func):
                def tool_fn(**kwargs) -> str:
                    try:
                        result = _run_in_main_thread(lambda: f(**kwargs))
                        return json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                    except Exception as e:
                        return json.dumps({"error": str(e)})
                tool_fn.__name__ = f"mcp_{cmd_name}"
                tool_fn.__doc__ = f"Execute {cmd_name} in Blender"
                return tool_fn

            tool_fn = make_tool(func)
            mcp.tool(name=f"blender_{cmd_name}")(tool_fn)

    return mcp


def start_embedded_server():
    """Start embedded MCP server (SSE :45677) + HTTP API (:9877)."""
    global _server_instance, _http_instance
    if _server_instance:
        return _server_instance

    # Start FastMCP SSE server
    mcp = _discover_tools()

    def run_mcp():
        try:
            import uvicorn
            uvicorn.run(mcp.sse_app(), host="localhost", port=45677, log_level="warning")
        except Exception as e:
            print(f"[EMBEDDED MCP] Server error: {e}")

    thread = threading.Thread(target=run_mcp, daemon=True)
    thread.start()
    _server_instance = {"mcp": mcp, "thread": thread}
    print(f"[EMBEDDED MCP] SSE on http://localhost:45677/sse")

    # Start HTTP REST API for Antigravity
    try:
        from .mini_http import start as start_http
        start_http()
        _http_instance = True
    except Exception as e:
        print(f"[EMBEDDED MCP] HTTP API error: {e}")

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
    print("[EMBEDDED MCP] Server stopped")
