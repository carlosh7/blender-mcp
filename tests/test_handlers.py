"""
blender-mcp — Handler Tests
Tests the Blender command surface (addon.handlers registry + legacy cmd_*)
under the headless bpy stub. Mirrors the documented tool categories.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import bpy_stub  # noqa: E402
bpy_stub.install()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from addon.handlers import HANDLERS  # noqa: E402
from addon._axsock import BlenderSocketServer  # noqa: E402


@pytest.fixture(scope="module")
def srv():
    return BlenderSocketServer()


def _cmds(srv):
    """All dispatchable command names (legacy cmd_* + registry)."""
    names = set()
    for cls in type(srv).__mro__:
        for attr in dir(cls):
            if attr.startswith("cmd_"):
                names.add(attr[4:])
    names.update(HANDLERS.keys())
    return names


class TestHandlerImports:
    """Test that all documented command categories are reachable."""

    def test_scene_handler(self, srv):
        cmds = _cmds(srv)
        assert "ping" in cmds
        assert "get_scene_info" in cmds
        assert "execute_code" in cmds
        assert "get_object_info" in cmds

    def test_objects_handler(self, srv):
        cmds = _cmds(srv)
        assert "create_object" in cmds
        assert "delete_object" in cmds
        assert "transform_object" in cmds
        assert "duplicate_object" in cmds

    def test_materials_handler(self, srv):
        cmds = _cmds(srv)
        assert "create_material" in cmds
        assert "assign_material" in cmds
        assert "list_materials" in cmds
        assert "set_color" in cmds

    def test_modifiers_handler(self, srv):
        cmds = _cmds(srv)
        assert "add_modifier" in cmds
        assert "remove_modifier" in cmds
        assert "list_modifiers" in cmds
        assert "apply_modifiers" in cmds

    def test_lights_handler(self, srv):
        cmds = _cmds(srv)
        assert "create_light" in cmds
        assert "setup_three_point_lighting" in cmds

    def test_camera_handler(self, srv):
        cmds = _cmds(srv)
        assert "create_camera" in cmds
        assert "set_camera_target" in cmds

    def test_shader_nodes_handler(self, srv):
        cmds = _cmds(srv)
        assert "add_shader_node" in cmds
        assert "connect_shader_nodes" in cmds
        assert "list_shader_nodes" in cmds

    def test_animation_handler(self, srv):
        cmds = _cmds(srv)
        assert "insert_keyframe" in cmds
        assert "animate_location" in cmds
        assert "create_action" in cmds

    def test_io_handler(self, srv):
        cmds = _cmds(srv)
        assert "export_scene" in cmds
        assert "import_file" in cmds
        assert "list_export_formats" in cmds

    def test_printing_handler(self, srv):
        cmds = _cmds(srv)
        assert "check_manifold" in cmds
        assert "set_dimensions_mm" in cmds
        assert "bed_layout" in cmds

    def test_rigging_handler(self, srv):
        cmds = _cmds(srv)
        assert "create_armature" in cmds
        assert "add_bone" in cmds
        assert "auto_rig_weight" in cmds

    def test_scene_utils_handler(self, srv):
        cmds = _cmds(srv)
        assert "purge_orphans" in cmds
        assert "scene_summary" in cmds
        assert "mesh_analysis" in cmds


class TestSurfaceExecution:
    """A few categories execute end-to-end through the dispatcher."""

    def test_modeling_flow(self, srv):
        r = srv._execute({"command": "create_object",
                          "args": {"type": "CYLINDER", "name": "flow_cyl",
                                   "radius": 0.5, "depth": 1.0}})
        assert r["status"] == "success"
        r = srv._execute({"command": "add_modifier",
                          "args": {"object_name": "flow_cyl",
                                   "modifier_type": "solidify",
                                   "thickness": 0.02}})
        assert r["status"] == "success"
        r = srv._execute({"command": "apply_modifiers",
                          "args": {"object_name": "flow_cyl"}})
        assert r["status"] == "success"

    def test_rigging_flow(self, srv):
        r = srv._execute({"command": "create_armature",
                          "args": {"name": "flow_arm"}})
        assert r["status"] == "success"
        r = srv._execute({"command": "add_bone",
                          "args": {"armature_name": "flow_arm",
                                   "bone_name": "Upper",
                                   "head": [0, 0, 0], "tail": [0, 0, 1]}})
        assert r["status"] == "success"
        r = srv._execute({"command": "reset_pose",
                          "args": {"armature_name": "flow_arm"}})
        assert r["status"] == "success"

    def test_render_settings_flow(self, srv):
        r = srv._execute({"command": "set_render_engine",
                          "args": {"engine": "CYCLES"}})
        assert r["status"] == "success"
        r = srv._execute({"command": "set_render_resolution",
                          "args": {"width": 800, "height": 600}})
        assert r["status"] == "success"
        r = srv._execute({"command": "set_render_samples",
                          "args": {"samples": 128}})
        assert r["status"] == "success"
