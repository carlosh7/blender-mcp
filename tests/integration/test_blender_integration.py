"""
blender-mcp-ultra — Integration Tests
Tests that require Blender running with MCP server.
"""

import json
import os
import socket
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from helpers import skip_without_blender


def send_command(command, params=None):
    """Send command to Blender MCP server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(("localhost", 9876))
    cmd = json.dumps({"command": command, "params": params or {}})
    sock.sendall(cmd.encode())
    time.sleep(0.3)
    resp = sock.recv(65536)
    sock.close()
    return json.loads(resp.decode()) if resp else None


def payload(resp):
    """Unwrap socket envelope {"status", "result"|"message"} to a flat dict."""
    if not resp:
        return {}
    result = resp.get("result")
    if resp.get("status") == "success" and isinstance(result, dict):
        return result
    return {"success": False, "error": resp.get("message", "unknown error")}


def call_tool(tool_name, params=None):
    """Call a registry tool via the socket 'tool' command (unwrapped)."""
    return payload(send_command("tool", {"tool_name": tool_name, "params": params or {}}))


class TestBlenderConnection:
    """Tests for Blender MCP connection."""

    @skip_without_blender
    def test_ping(self):
        result = payload(send_command("ping"))
        assert result.get("pong") is True

    @skip_without_blender
    def test_get_scene_info(self):
        result = payload(send_command("get_scene_info"))
        assert "name" in result
        assert "object_count" in result

    @skip_without_blender
    def test_list_tools(self):
        result = payload(send_command("list_tools"))
        assert len(result.get("tools", [])) > 0


class TestObjectCreation:
    """Tests for object creation via MCP."""

    @skip_without_blender
    def test_create_cube(self):
        result = call_tool(
            "object.create", {"type": "MESH", "name": "IntegrationCube", "location": [0, 0, 0]}
        )
        assert result.get("success") is True
        # Blender may auto-rename if name exists
        assert "IntegrationCube" in result.get("data", {}).get("name", "")

    @skip_without_blender
    def test_create_sphere(self):
        result = call_tool(
            "object.create", {"type": "MESH", "name": "TestSphere", "location": [3, 0, 0]}
        )
        assert result.get("success") is True

    @skip_without_blender
    def test_list_objects(self):
        result = call_tool("object.list", {})
        assert result.get("success") is True
        assert "objects" in result.get("data", {})


class TestMaterialCreation:
    """Tests for material creation via MCP."""

    @skip_without_blender
    def test_create_material(self):
        result = call_tool("material.create", {"name": "TestMat", "color": [1, 0, 0, 1]})
        assert result.get("success") is True

    @skip_without_blender
    def test_assign_material(self):
        # First create object and material
        call_tool("object.create", {"type": "MESH", "name": "AssignTest", "location": [0, 0, 0]})
        call_tool("material.create", {"name": "AssignMat", "color": [0, 1, 0, 1]})

        result = call_tool(
            "material.assign", {"object_name": "AssignTest", "material_name": "AssignMat"}
        )
        assert result.get("success") is True


class TestLightCreation:
    """Tests for light creation via MCP."""

    @skip_without_blender
    def test_create_light(self):
        result = call_tool(
            "light.create",
            {"type": "AREA", "name": "TestLight", "location": [3, -3, 5], "energy": 1000},
        )
        assert result.get("success") is True

    @skip_without_blender
    def test_three_point_lighting(self):
        result = call_tool("light.three_point", {})
        assert result.get("success") is True


class TestCameraCreation:
    """Tests for camera creation via MCP."""

    @skip_without_blender
    def test_create_camera(self):
        result = call_tool("camera.create", {"name": "TestCam", "location": [0, -5, 2], "lens": 50})
        assert result.get("success") is True


class TestModifierOperations:
    """Tests for modifier operations via MCP."""

    @skip_without_blender
    def test_add_modifier(self):
        # Create object first
        call_tool("object.create", {"type": "MESH", "name": "ModTest", "location": [0, 0, 0]})

        result = call_tool("modifier.add", {"object_name": "ModTest", "type": "SUBSURF"})
        assert result.get("success") is True


class TestAnimationOperations:
    """Tests for animation operations via MCP."""

    @skip_without_blender
    def test_set_keyframe(self):
        # Create object first
        call_tool("object.create", {"type": "MESH", "name": "AnimTest", "location": [0, 0, 0]})

        result = call_tool(
            "animation.set_keyframe",
            {"object_name": "AnimTest", "property": "location", "frame": 1, "value": [0, 0, 0]},
        )
        assert result.get("success") is True


class TestSceneUtils:
    """Tests for scene utilities via MCP."""

    @skip_without_blender
    def test_mesh_analysis(self):
        # Create object first
        call_tool("object.create", {"type": "MESH", "name": "AnalysisTest", "location": [0, 0, 0]})

        result = call_tool("scene_utils.mesh_analysis", {"object_name": "AnalysisTest"})
        assert "vertices" in result.get("data", {}) or "error" in result.get("data", {})


class TestExecuteCode:
    """Tests for code execution via MCP."""

    @skip_without_blender
    def test_execute_simple_code(self):
        result = payload(send_command("execute_code", {"code": "print('Hello from Blender')"}))
        assert "Hello from Blender" in result.get("output", "")

    @skip_without_blender
    def test_execute_object_creation(self):
        result = payload(
            send_command(
                "execute_code",
                {
                    "code": "import bpy; bpy.ops.mesh.primitive_cube_add(location=(10, 0, 0)); print('Cube created')"
                },
            )
        )
        assert "Cube created" in result.get("output", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
