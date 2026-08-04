"""
blender-mcp — Test Helpers
Shared utilities for test modules.
"""
import socket
import pytest


def is_blender_available():
    """Check if Blender MCP server is running on port 9876."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("localhost", 9876))
        sock.close()
        return True
    except Exception:
        return False


_skip_blender_cache = None


def skip_without_blender(func=None, *, reason="Blender MCP server not running on port 9876"):
    """Decorator/marker to skip test when Blender is not available."""
    global _skip_blender_cache
    if _skip_blender_cache is None:
        _skip_blender_cache = not is_blender_available()

    marker = pytest.mark.skipif(_skip_blender_cache, reason=reason)
    if func is not None:
        return marker(func)
    return marker
