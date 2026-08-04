"""
blender-mcp — E2E Socket Connection Tests
Tests Blender socket connection and command execution.
Requires Blender running with the addon active.
"""
import os
import sys
import json
import time
import pytest


def _blender_up():
    import socket as _socket
    s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect(("localhost", 9876))
        return True
    except OSError:
        return False
    finally:
        s.close()

needs_blender = pytest.mark.skipif(not _blender_up(),
                                   reason="Blender socket (localhost:9876) not reachable")


@pytest.mark.e2e
@needs_blender
class TestSocketConnection:
    def test_connect(self):
        """Test basic socket connection to Blender."""
        conn = BlenderConnection(host="localhost", port=9876)
        assert conn.connect(), "Should connect to Blender socket"
        conn.disconnect()

    def test_ping(self):
        """Test ping/pong with Blender."""
        b = get_blender()
        result = b.send_command("ping")
        assert result.get("pong") == True, "Should receive pong"

    def test_get_scene_info(self):
        """Test get_scene_info command."""
        b = get_blender()
        result = b.send_command("get_scene_info")
        assert "name" in result, "Scene info should contain name"
        assert "objects" in result, "Scene info should contain objects list"
        assert "object_count" in result, "Scene info should contain object_count"

    def test_execute_code(self):
        """Test executing Python code in Blender."""
        b = get_blender()
        result = b.send_command("execute_code", {"code": "print('hello from test')"})
        assert "output" in result, "Should return output"
