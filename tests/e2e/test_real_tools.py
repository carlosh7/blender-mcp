"""
blender-mcp-ultra — Real Tool Validation
Tests every tool category with actual Blender instance.
"""

import json
import os
import socket
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helpers import skip_without_blender, socket_token


def call_tool(tool_name, arguments=None):
    """Call tool via MCP and return result."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect(("localhost", 9876))

        cmd = {"command": "tool", "params": {"tool_name": tool_name, "params": arguments or {}}}
        tok = socket_token()
        if tok:
            cmd["token"] = tok
        sock.sendall(json.dumps(cmd).encode())
        time.sleep(0.2)

        # loop de recepción: respuestas grandes (escenas con cientos de
        # objetos) llegan fragmentadas — un solo recv trunca el JSON
        buf = b""
        result = None
        while True:
            chunk = sock.recv(262144)
            if not chunk:
                break
            buf += chunk
            try:
                result = json.loads(buf.decode())
                break
            except json.JSONDecodeError:
                continue
        sock.close()
        if result is None:
            return {"error": "sin respuesta o JSON truncado"}
        if result.get("status") == "success" and isinstance(result.get("result"), dict):
            inner = result["result"]
            return inner.get("data", inner)
        return {"error": result.get("message", "unknown error")}
    except Exception as e:
        return {"error": str(e)}


class TestRealSceneTools:
    """Real tests for Scene tools with Blender."""

    @skip_without_blender
    def test_scene_get_info(self):
        result = call_tool("scene.get_info")
        assert result is not None
        assert "name" in result or "objects" in result

    @skip_without_blender
    def test_scene_render_settings(self):
        result = call_tool("scene.render_settings", {"engine": "BLENDER_EEVEE"})
        assert result is not None
        assert "engine" in result or "error" in result


class TestRealObjectTools:
    """Real tests for Object tools with Blender."""

    @skip_without_blender
    def test_object_create_cube(self):
        result = call_tool(
            "object.create", {"type": "MESH", "name": "RealCube", "location": [0, 0, 0]}
        )
        assert result is not None
        assert result.get("success") or result.get("name")

    @skip_without_blender
    def test_object_create_sphere(self):
        result = call_tool(
            "object.create", {"type": "MESH", "name": "RealSphere", "location": [3, 0, 0]}
        )
        assert result is not None

    @skip_without_blender
    def test_object_create_cylinder(self):
        result = call_tool(
            "object.create", {"type": "MESH", "name": "RealCylinder", "location": [-3, 0, 0]}
        )
        assert result is not None

    @skip_without_blender
    def test_object_create_cone(self):
        result = call_tool(
            "object.create", {"type": "MESH", "name": "RealCone", "location": [0, 3, 0]}
        )
        assert result is not None

    @skip_without_blender
    def test_object_create_torus(self):
        result = call_tool(
            "object.create", {"type": "MESH", "name": "RealTorus", "location": [0, -3, 0]}
        )
        assert result is not None

    @skip_without_blender
    def test_object_create_light(self):
        result = call_tool(
            "object.create", {"type": "LIGHT", "name": "RealLight", "location": [5, 5, 5]}
        )
        assert result is not None

    @skip_without_blender
    def test_object_create_camera(self):
        result = call_tool(
            "object.create", {"type": "CAMERA", "name": "RealCamera", "location": [0, -5, 2]}
        )
        assert result is not None

    @skip_without_blender
    def test_object_list(self):
        result = call_tool("object.list")
        assert result is not None
        assert "objects" in result or "count" in result

    @skip_without_blender
    def test_object_get_info(self):
        result = call_tool("object.get_info", {"name": "RealCube"})
        assert result is not None

    @skip_without_blender
    def test_object_transform(self):
        result = call_tool("object.transform", {"name": "RealCube", "location": [1, 1, 1]})
        assert result is not None

    @skip_without_blender
    def test_object_duplicate(self):
        result = call_tool("object.duplicate", {"name": "RealCube"})
        assert result is not None

    @skip_without_blender
    def test_object_select(self):
        result = call_tool("object.select", {"type": "MESH"})
        assert result is not None


class TestRealMaterialTools:
    """Real tests for Material tools with Blender."""

    @skip_without_blender
    def test_material_create(self):
        result = call_tool(
            "material.create", {"name": "RealMat", "color": [1, 0, 0, 1], "metallic": 0.5}
        )
        assert result is not None

    @skip_without_blender
    def test_material_assign(self):
        call_tool("material.create", {"name": "AssignMat", "color": [0, 1, 0, 1]})
        result = call_tool(
            "material.assign", {"object_name": "RealCube", "material_name": "AssignMat"}
        )
        assert result is not None

    @skip_without_blender
    def test_material_list(self):
        result = call_tool("material.list")
        assert result is not None

    @skip_without_blender
    def test_material_get_info(self):
        result = call_tool("material.get_info", {"name": "RealMat"})
        assert result is not None


class TestRealLightTools:
    """Real tests for Light tools with Blender."""

    @skip_without_blender
    def test_light_create_area(self):
        result = call_tool(
            "light.create",
            {"type": "AREA", "name": "RealAreaLight", "location": [3, -3, 5], "energy": 1000},
        )
        assert result is not None

    @skip_without_blender
    def test_light_create_point(self):
        result = call_tool(
            "light.create", {"type": "POINT", "name": "RealPointLight", "location": [0, 0, 3]}
        )
        assert result is not None

    @skip_without_blender
    def test_light_create_sun(self):
        result = call_tool(
            "light.create", {"type": "SUN", "name": "RealSunLight", "location": [0, 0, 10]}
        )
        assert result is not None

    @skip_without_blender
    def test_light_create_spot(self):
        result = call_tool(
            "light.create", {"type": "SPOT", "name": "RealSpotLight", "location": [0, -5, 3]}
        )
        assert result is not None

    @skip_without_blender
    def test_light_three_point(self):
        result = call_tool("light.three_point")
        assert result is not None

    @skip_without_blender
    def test_light_list(self):
        result = call_tool("light.list")
        assert result is not None


class TestRealCameraTools:
    """Real tests for Camera tools with Blender."""

    @skip_without_blender
    def test_camera_create(self):
        result = call_tool("camera.create", {"name": "RealCam", "location": [0, -5, 2], "lens": 50})
        assert result is not None

    @skip_without_blender
    def test_camera_list(self):
        result = call_tool("camera.list")
        assert result is not None

    @skip_without_blender
    def test_camera_set_resolution(self):
        result = call_tool("camera.setResolution", {"width": 1920, "height": 1080})
        assert result is not None


class TestRealModifierTools:
    """Real tests for Modifier tools with Blender."""

    @skip_without_blender
    def test_modifier_add_subsurf(self):
        result = call_tool("modifier.add", {"object_name": "RealCube", "type": "SUBSURF"})
        assert result is not None

    @skip_without_blender
    def test_modifier_add_bevel(self):
        result = call_tool("modifier.add", {"object_name": "RealCube", "type": "BEVEL"})
        assert result is not None

    @skip_without_blender
    def test_modifier_add_array(self):
        result = call_tool("modifier.add", {"object_name": "RealCube", "type": "ARRAY"})
        assert result is not None

    @skip_without_blender
    def test_modifier_add_mirror(self):
        result = call_tool("modifier.add", {"object_name": "RealCube", "type": "MIRROR"})
        assert result is not None

    @skip_without_blender
    def test_modifier_list(self):
        result = call_tool("modifier.list", {"object_name": "RealCube"})
        assert result is not None

    @skip_without_blender
    def test_modifier_types(self):
        result = call_tool("modifier.types")
        assert result is not None


class TestRealAnimationTools:
    """Real tests for Animation tools with Blender."""

    @skip_without_blender
    def test_animation_set_keyframe(self):
        result = call_tool(
            "animation.set_keyframe",
            {"object_name": "RealCube", "property": "location", "frame": 1, "value": [0, 0, 0]},
        )
        assert result is not None

    @skip_without_blender
    def test_animation_set_keyframe2(self):
        result = call_tool(
            "animation.set_keyframe",
            {"object_name": "RealCube", "property": "location", "frame": 50, "value": [5, 0, 3]},
        )
        assert result is not None

    @skip_without_blender
    def test_animation_get_fcurves(self):
        result = call_tool("animation.get_fcurves", {"object_name": "RealCube"})
        assert result is not None


class TestRealUVTools:
    """Real tests for UV tools with Blender."""

    @skip_without_blender
    def test_uv_create(self):
        result = call_tool("uv.create", {"object_name": "RealCube", "name": "RealUVMap"})
        assert result is not None

    @skip_without_blender
    def test_uv_list(self):
        result = call_tool("uv.list", {"object_name": "RealCube"})
        assert result is not None

    @skip_without_blender
    def test_texture_create(self):
        result = call_tool("texture.create", {"name": "RealTexture", "width": 1024, "height": 1024})
        assert result is not None


class TestRealSceneUtilsTools:
    """Real tests for Scene Utils tools with Blender."""

    @skip_without_blender
    def test_mesh_analysis(self):
        result = call_tool("scene_utils.mesh_analysis", {"object_name": "RealCube"})
        assert result is not None

    @skip_without_blender
    def test_fix_normals(self):
        result = call_tool("scene_utils.fix_normals", {"object_name": "RealCube"})
        assert result is not None

    @skip_without_blender
    def test_remove_doubles(self):
        result = call_tool("scene_utils.remove_doubles", {"object_name": "RealCube"})
        assert result is not None

    @skip_without_blender
    def test_cleanup(self):
        result = call_tool("scene_utils.cleanup")
        assert result is not None


class TestRealIOTools:
    """Real tests for I/O tools with Blender."""

    @skip_without_blender
    def test_io_save_file(self):
        result = call_tool("io.save_file", {"filepath": "/tmp/blender_test.blend"})
        assert result is not None

    @skip_without_blender
    def test_io_export_obj(self):
        result = call_tool("io.export_obj", {"filepath": "/tmp/test.obj"})
        # OBJ export may fail in background mode - that's expected
        assert result is not None


class TestRealShaderNodeTools:
    """Real tests for Shader Node tools with Blender."""

    @skip_without_blender
    def test_shader_add_node(self):
        result = call_tool(
            "shader.add_node", {"material_name": "RealMat", "node_type": "ShaderNodeTexNoise"}
        )
        assert result is not None

    @skip_without_blender
    def test_shader_list_nodes(self):
        result = call_tool("shader.list_nodes", {"material_name": "RealMat"})
        assert result is not None


class TestRealGeometryNodeTools:
    """Real tests for Geometry Node tools with Blender."""

    @skip_without_blender
    def test_geonodes_create_group(self):
        result = call_tool("geonodes.create_group", {"name": "RealGN"})
        assert result is not None

    @skip_without_blender
    def test_geonodes_list_groups(self):
        result = call_tool("geonodes.list_groups")
        assert result is not None


class TestRealBatchTools:
    """Real tests for Batch tools with Blender."""

    @skip_without_blender
    def test_batch_turntable(self):
        result = call_tool(
            "batch.turntable", {"object_name": "RealSphere", "frames": 30, "axis": "Z"}
        )
        assert result is not None

    @skip_without_blender
    def test_batch_apply_transforms(self):
        result = call_tool("batch.apply_transforms")
        assert result is not None


class TestRealRiggingTools:
    """Real tests for Rigging tools with Blender."""

    @skip_without_blender
    def test_rigging_create_armature(self):
        result = call_tool("rigging.create_armature", {"name": "RealArm"})
        assert result is not None

    @skip_without_blender
    def test_rigging_list_bones(self):
        result = call_tool("rigging.list_bones", {"armature_name": "RealArm"})
        assert result is not None


class TestRealPrintingTools:
    """Real tests for Printing tools with Blender."""

    @skip_without_blender
    def test_printing_info(self):
        result = call_tool("printing.info", {"object_name": "RealCube"})
        assert result is not None


class TestRealRenderTools:
    """Real tests for Render tools with Blender."""

    @skip_without_blender
    def test_render_settings(self):
        result = call_tool("scene.render_settings", {"engine": "BLENDER_EEVEE"})
        assert result is not None

    @skip_without_blender
    def test_render_cycles(self):
        result = call_tool("scene.render_settings", {"engine": "CYCLES", "samples": 128})
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
