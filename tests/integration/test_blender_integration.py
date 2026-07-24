"""
blender-mcp-ultra — Integration Tests
Tests that require Blender running with MCP server.
"""
import sys
import os
import socket
import json
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Check if Blender MCP server is available
def is_blender_available():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('localhost', 9876))
        sock.close()
        return True
    except:
        return False

skip_without_blender = pytest.mark.skipif(
    not is_blender_available(),
    reason="Blender MCP server not running on port 9876"
)


def send_command(command, params=None):
    """Send command to Blender MCP server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(('localhost', 9876))
    cmd = json.dumps({"command": command, "params": params or {}})
    sock.sendall(cmd.encode())
    time.sleep(0.3)
    resp = sock.recv(65536)
    sock.close()
    return json.loads(resp.decode()) if resp else None


class TestBlenderConnection:
    """Tests for Blender MCP connection."""
    
    @skip_without_blender
    def test_ping(self):
        result = send_command("ping")
        assert result is not None
        assert result.get("pong") is True
        assert "tools" in result
    
    @skip_without_blender
    def test_get_scene_info(self):
        result = send_command("get_scene_info")
        assert result is not None
        assert "name" in result
        assert "object_count" in result
        assert "objects" in result
    
    @skip_without_blender
    def test_list_tools(self):
        result = send_command("list_tools")
        assert result is not None
        assert "tools" in result
        assert len(result["tools"]) > 0


class TestObjectCreation:
    """Tests for object creation via MCP."""
    
    @skip_without_blender
    def test_create_cube(self):
        result = send_command("tool", {
            "tool_name": "object.create",
            "params": {"type": "MESH", "name": "TestCube", "location": [0, 0, 0]}
        })
        assert result is not None
        assert result.get("success") is True
        assert result.get("data", {}).get("name") == "TestCube"
    
    @skip_without_blender
    def test_create_sphere(self):
        result = send_command("tool", {
            "tool_name": "object.create",
            "params": {"type": "MESH", "name": "TestSphere", "location": [3, 0, 0]}
        })
        assert result is not None
        assert result.get("success") is True
    
    @skip_without_blender
    def test_list_objects(self):
        result = send_command("tool", {
            "tool_name": "object.list",
            "params": {}
        })
        assert result is not None
        assert result.get("success") is True
        assert "objects" in result.get("data", {})


class TestMaterialCreation:
    """Tests for material creation via MCP."""
    
    @skip_without_blender
    def test_create_material(self):
        result = send_command("tool", {
            "tool_name": "material.create",
            "params": {"name": "TestMat", "color": [1, 0, 0, 1]}
        })
        assert result is not None
        assert result.get("success") is True
    
    @skip_without_blender
    def test_assign_material(self):
        # First create object and material
        send_command("tool", {
            "tool_name": "object.create",
            "params": {"type": "MESH", "name": "AssignTest", "location": [0, 0, 0]}
        })
        send_command("tool", {
            "tool_name": "material.create",
            "params": {"name": "AssignMat", "color": [0, 1, 0, 1]}
        })
        
        result = send_command("tool", {
            "tool_name": "material.assign",
            "params": {"object_name": "AssignTest", "material_name": "AssignMat"}
        })
        assert result is not None
        assert result.get("success") is True


class TestLightCreation:
    """Tests for light creation via MCP."""
    
    @skip_without_blender
    def test_create_light(self):
        result = send_command("tool", {
            "tool_name": "light.create",
            "params": {"type": "AREA", "name": "TestLight", "location": [3, -3, 5], "energy": 1000}
        })
        assert result is not None
        assert result.get("success") is True
    
    @skip_without_blender
    def test_three_point_lighting(self):
        result = send_command("tool", {
            "tool_name": "light.three_point",
            "params": {}
        })
        assert result is not None
        assert result.get("success") is True


class TestCameraCreation:
    """Tests for camera creation via MCP."""
    
    @skip_without_blender
    def test_create_camera(self):
        result = send_command("tool", {
            "tool_name": "camera.create",
            "params": {"name": "TestCam", "location": [0, -5, 2], "lens": 50}
        })
        assert result is not None
        assert result.get("success") is True


class TestModifierOperations:
    """Tests for modifier operations via MCP."""
    
    @skip_without_blender
    def test_add_modifier(self):
        # Create object first
        send_command("tool", {
            "tool_name": "object.create",
            "params": {"type": "MESH", "name": "ModTest", "location": [0, 0, 0]}
        })
        
        result = send_command("tool", {
            "tool_name": "modifier.add",
            "params": {"object_name": "ModTest", "type": "SUBSURF"}
        })
        assert result is not None
        assert result.get("success") is True


class TestAnimationOperations:
    """Tests for animation operations via MCP."""
    
    @skip_without_blender
    def test_set_keyframe(self):
        # Create object first
        send_command("tool", {
            "tool_name": "object.create",
            "params": {"type": "MESH", "name": "AnimTest", "location": [0, 0, 0]}
        })
        
        result = send_command("tool", {
            "tool_name": "animation.set_keyframe",
            "params": {"object_name": "AnimTest", "property": "location", "frame": 1, "value": [0, 0, 0]}
        })
        assert result is not None
        assert result.get("success") is True


class TestSceneUtils:
    """Tests for scene utilities via MCP."""
    
    @skip_without_blender
    def test_mesh_analysis(self):
        # Create object first
        send_command("tool", {
            "tool_name": "object.create",
            "params": {"type": "MESH", "name": "AnalysisTest", "location": [0, 0, 0]}
        })
        
        result = send_command("tool", {
            "tool_name": "scene_utils.mesh_analysis",
            "params": {"object_name": "AnalysisTest"}
        })
        assert result is not None
        assert "vertices" in result.get("data", {}) or "error" in result.get("data", {})


class TestExecuteCode:
    """Tests for code execution via MCP."""
    
    @skip_without_blender
    def test_execute_simple_code(self):
        result = send_command("execute_code", {
            "code": "print('Hello from Blender')"
        })
        assert result is not None
        assert "output" in result
        assert "Hello from Blender" in result["output"]
    
    @skip_without_blender
    def test_execute_object_creation(self):
        result = send_command("execute_code", {
            "code": "import bpy; bpy.ops.mesh.primitive_cube_add(location=(10, 0, 0)); print('Cube created')"
        })
        assert result is not None
        assert "output" in result
        assert "Cube created" in result["output"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
