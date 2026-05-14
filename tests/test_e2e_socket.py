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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from blender_connection import get_blender, BlenderConnection


@pytest.mark.e2e
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
