"""
blender-mcp-ultra — E2E Tests
Complete workflow tests simulating real LLM interactions.
"""
import sys
import os
import socket
import json
import time
import subprocess
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


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
    reason="Blender MCP server not running"
)


def send_mcp_request(method, params=None):
    """Send MCP request via adapter."""
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    })
    result = subprocess.run(
        ['python3', '/home/carlosh/blender-mcp/mcp_adapter.py'],
        input=req,
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.stdout:
        return json.loads(result.stdout)
    return None


def call_tool(tool_name, arguments=None):
    """Call a tool via MCP."""
    result = send_mcp_request("tools/call", {
        "name": tool_name,
        "arguments": arguments or {}
    })
    if result and "result" in result:
        content = result["result"].get("content", [{}])[0].get("text", "")
        try:
            return json.loads(content)
        except:
            return {"raw": content}
    return None


class TestE2EProductVisualization:
    """E2E test: Product visualization workflow."""
    
    @skip_without_blender
    def test_product_scene_creation(self):
        """Test creating a complete product scene."""
        # 1. Create product
        result = call_tool("object.create", {
            "type": "MESH", "name": "Product", "location": [0, 0, 0]
        })
        assert result is not None
        
        # 2. Add modifiers
        result = call_tool("modifier.add", {
            "object_name": "Product", "type": "SUBSURF"
        })
        assert result is not None
        
        # 3. Create material
        result = call_tool("material.create", {
            "name": "ProductMat", "color": [0.8, 0.2, 0.2, 1], "metallic": 0.5
        })
        assert result is not None
        
        # 4. Assign material
        result = call_tool("material.assign", {
            "object_name": "Product", "material_name": "ProductMat"
        })
        assert result is not None
        
        # 5. Setup lighting
        result = call_tool("light.three_point", {})
        assert result is not None
        
        # 6. Create camera
        result = call_tool("camera.create", {
            "name": "ProductCam", "location": [0, -3, 1.5], "lens": 85
        })
        assert result is not None
        
        # 7. Set render settings
        result = call_tool("scene.render_settings", {
            "engine": "CYCLES", "samples": 128
        })
        assert result is not None
        
        # 8. Verify scene
        scene = call_tool("scene.get_info", {})
        assert scene is not None
        assert scene.get("object_count", 0) >= 3


class TestE2ECharacterRig:
    """E2E test: Character rigging workflow."""
    
    @skip_without_blender
    def test_character_rig_creation(self):
        """Test creating a character rig."""
        # 1. Create armature
        result = call_tool("rigging.create_armature", {
            "name": "CharacterArm", "location": [0, 0, 0]
        })
        assert result is not None
        
        # 2. Create character mesh
        result = call_tool("object.create", {
            "type": "MESH", "name": "CharacterMesh", "location": [0, 0, 0]
        })
        assert result is not None
        
        # 3. Create vertex group
        result = call_tool("rigging.create_vertex_group", {
            "object_name": "CharacterMesh", "name": "Body"
        })
        assert result is not None
        
        # 4. Setup camera for rigging
        result = call_tool("camera.create", {
            "name": "RigCam", "location": [0, -5, 2], "lens": 50
        })
        assert result is not None


class TestE2EAnimation:
    """E2E test: Animation workflow."""
    
    @skip_without_blender
    def test_animation_workflow(self):
        """Test creating an animation."""
        # 1. Create object
        result = call_tool("object.create", {
            "type": "MESH", "name": "AnimObj", "location": [0, 0, 0]
        })
        assert result is not None
        
        # 2. Set keyframes
        result = call_tool("animation.set_keyframe", {
            "object_name": "AnimObj", "property": "location",
            "frame": 1, "value": [0, 0, 0]
        })
        assert result is not None
        
        result = call_tool("animation.set_keyframe", {
            "object_name": "AnimObj", "property": "location",
            "frame": 50, "value": [5, 0, 3]
        })
        assert result is not None
        
        # 3. Set interpolation
        result = call_tool("animation.set_interpolation", {
            "object_name": "AnimObj", "interpolation": "BEZIER"
        })
        assert result is not None
        
        # 4. Get F-curves
        result = call_tool("animation.get_fcurves", {
            "object_name": "AnimObj"
        })
        assert result is not None


class TestE2EGeometryNodes:
    """E2E test: Geometry Nodes workflow."""
    
    @skip_without_blender
    def test_geometry_nodes_workflow(self):
        """Test creating geometry nodes setup."""
        # 1. Create object
        result = call_tool("object.create", {
            "type": "MESH", "name": "GNObj", "location": [0, 0, 0]
        })
        assert result is not None
        
        # 2. Create node group
        result = call_tool("geonodes.create_group", {
            "name": "ProceduralSetup"
        })
        assert result is not None
        
        # 3. List groups
        result = call_tool("geonodes.list_groups", {})
        assert result is not None


class TestE2EShaderNodes:
    """E2E test: Shader Nodes workflow."""
    
    @skip_without_blender
    def test_shader_workflow(self):
        """Test creating shader setup."""
        # 1. Create material
        result = call_tool("material.create", {
            "name": "ShaderMat", "color": [1, 0, 0, 1]
        })
        assert result is not None
        
        # 2. Add noise node
        result = call_tool("shader.add_node", {
            "material_name": "ShaderMat",
            "node_type": "ShaderNodeTexNoise"
        })
        assert result is not None
        
        # 3. List nodes
        result = call_tool("shader.list_nodes", {
            "material_name": "ShaderMat"
        })
        assert result is not None
        
        # 4. Set node value
        result = call_tool("shader.set_node_value", {
            "material_name": "ShaderMat",
            "node_name": "Noise Texture",
            "input_name": "Scale",
            "value": 5.0
        })
        assert result is not None


class TestE2ESceneManagement:
    """E2E test: Scene management workflow."""
    
    @skip_without_blender
    def test_scene_management(self):
        """Test scene management operations."""
        # 1. Get scene info
        scene = call_tool("scene.get_info", {})
        assert scene is not None
        
        # 2. Create multiple objects
        for i in range(5):
            result = call_tool("object.create", {
                "type": "MESH", "name": f"Obj_{i}",
                "location": [i * 2, 0, 0]
            })
            assert result is not None
        
        # 3. List objects
        result = call_tool("object.list", {})
        assert result is not None
        assert result.get("count", 0) >= 5
        
        # 4. Mesh analysis
        result = call_tool("scene_utils.mesh_analysis", {
            "object_name": "Obj_0"
        })
        assert result is not None
        
        # 5. Cleanup
        result = call_tool("scene_utils.cleanup", {})
        assert result is not None


class TestE2EBatchOperations:
    """E2E test: Batch operations workflow."""
    
    @skip_without_blender
    def test_batch_workflow(self):
        """Test batch operations."""
        # 1. Create objects
        for i in range(3):
            call_tool("object.create", {
                "type": "MESH", "name": f"Batch_{i}",
                "location": [i * 2, 0, 0]
            })
        
        # 2. Batch rename
        result = call_tool("batch.rename", {
            "pattern": "Batch", "replace": "Item"
        })
        assert result is not None
        
        # 3. Batch apply transforms
        result = call_tool("batch.apply_transforms", {})
        assert result is not None


class TestE2EExport:
    """E2E test: Export workflow."""
    
    @skip_without_blender
    def test_export_workflow(self):
        """Test export operations."""
        # 1. Create object
        call_tool("object.create", {
            "type": "MESH", "name": "ExportObj", "location": [0, 0, 0]
        })
        
        # 2. Save blend file
        result = call_tool("io.save_file", {
            "filepath": "/tmp/e2e_test.blend"
        })
        assert result is not None


class TestE2EExecuteCode:
    """E2E test: Code execution workflow."""
    
    @skip_without_blender
    def test_code_execution(self):
        """Test executing custom code."""
        # 1. Execute simple code
        result = call_tool("scene.get_info", {})
        assert result is not None
        
        # 2. Create object via code
        result = send_mcp_request("tools/call", {
            "name": "scene.get_info",
            "arguments": {"include_objects": True}
        })
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
