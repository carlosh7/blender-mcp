"""
blender-mcp — Handler Tests
Tests for Blender addon handler modules.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestHandlerImports:
    """Test that all handler modules import correctly."""

    def test_scene_handler(self):
        pytest.importorskip("bpy")
        from handlers.scene import SceneHandler
        cmds = SceneHandler.get_commands()
        assert "ping" in cmds
        assert "get_scene_info" in cmds
        assert "execute_code" in cmds
        assert "get_object_info" in cmds

    def test_objects_handler(self):
        pytest.importorskip("bpy")
        from handlers.objects import ObjectsHandler
        cmds = ObjectsHandler.get_commands()
        assert "create_object" in cmds
        assert "delete_object" in cmds
        assert "transform_object" in cmds

    def test_materials_handler(self):
        pytest.importorskip("bpy")
        from handlers.materials import MaterialsHandler
        cmds = MaterialsHandler.get_commands()
        assert "create_material" in cmds
        assert "assign_material" in cmds
        assert "list_materials" in cmds

    def test_modifiers_handler(self):
        pytest.importorskip("bpy")
        from handlers.modifiers import ModifiersHandler
        cmds = ModifiersHandler.get_commands()
        assert "add_modifier" in cmds
        assert "remove_modifier" in cmds
        assert "list_modifiers" in cmds
        assert "apply_modifier" in cmds

    def test_lights_handler(self):
        pytest.importorskip("bpy")
        from handlers.lights import LightsHandler
        cmds = LightsHandler.get_commands()
        assert "create_light" in cmds
        assert "setup_three_point_lighting" in cmds

    def test_camera_handler(self):
        pytest.importorskip("bpy")
        from handlers.camera import CameraHandler
        cmds = CameraHandler.get_commands()
        assert "create_camera" in cmds
        assert "set_camera_target" in cmds

    def test_shader_nodes_handler(self):
        pytest.importorskip("bpy")
        from handlers.shader_nodes import ShaderNodesHandler
        cmds = ShaderNodesHandler.get_commands()
        assert "add_shader_node" in cmds
        assert "connect_nodes" in cmds
        assert "list_shader_nodes" in cmds

    def test_animation_handler(self):
        pytest.importorskip("bpy")
        from handlers.animation import AnimationHandler
        cmds = AnimationHandler.get_commands()
        assert "insert_keyframe" in cmds
        assert "animate_location" in cmds

    def test_io_handler(self):
        pytest.importorskip("bpy")
        from handlers.io import IOHandler
        cmds = IOHandler.get_commands()
        assert "export_scene" in cmds
        assert "import_model" in cmds
        assert "list_export_formats" in cmds

    def test_printing_handler(self):
        pytest.importorskip("bpy")
        from handlers.printing import PrintingHandler
        cmds = PrintingHandler.get_commands()
        assert "check_manifold" in cmds
        assert "set_dimensions_mm" in cmds
        assert "bed_layout" in cmds

    def test_rigging_handler(self):
        pytest.importorskip("bpy")
        from handlers.rigging import RiggingHandler
        cmds = RiggingHandler.get_commands()
        assert "create_armature" in cmds
        assert "add_bone" in cmds
        assert "auto_rig_weight" in cmds

    def test_scene_utils_handler(self):
        pytest.importorskip("bpy")
        from handlers.scene_utils import SceneUtilsHandler
        cmds = SceneUtilsHandler.get_commands()
        assert "purge_orphans" in cmds
        assert "scene_summary" in cmds
        assert "mesh_analysis" in cmds

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_properties_module(self):
        import properties
        assert hasattr(properties, "register_properties")
        assert hasattr(properties, "unregister_properties")

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_preferences_module(self):
        import preferences
        assert hasattr(preferences, "register_preferences")
        assert hasattr(preferences, "unregister_preferences")


class TestAssetsHandler:
    """Test asset handler imports."""

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_polyhaven_handler(self):
        import handlers.polyhaven as ph
        assert hasattr(ph, "cmd_search_polyhaven")
        assert hasattr(ph, "cmd_get_polyhaven_status")
        assert hasattr(ph, "cmd_download_polyhaven_hdri")
        assert hasattr(ph, "cmd_download_polyhaven_texture")
        assert hasattr(ph, "cmd_download_polyhaven_model")

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_sketchfab_handler(self):
        import handlers.sketchfab as sk
        assert hasattr(sk, "cmd_search_sketchfab")
        assert hasattr(sk, "cmd_get_sketchfab_status")
        assert hasattr(sk, "cmd_get_sketchfab_preview")
        assert hasattr(sk, "cmd_download_sketchfab_model")

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_ambientcg_handler(self):
        import handlers.ambientcg as ac
        assert hasattr(ac, "cmd_search_ambientcg")
        assert hasattr(ac, "cmd_download_ambientcg_material")

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_analysis_handler(self):
        from handlers.analysis import AnalysisHandler
        cmds = AnalysisHandler.get_commands()
        assert "get_objects_summary" in cmds
        assert "get_object_detail_summary" in cmds
        assert "get_blendfile_summary_datablocks" in cmds
        assert "get_screenshot_as_base64" in cmds

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_docs_handler(self):
        from handlers.docs import DocsHandler
        cmds = DocsHandler.get_commands()
        assert "search_api_docs" in cmds
        assert "get_python_api_docs" in cmds

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_viewport_handler(self):
        from handlers.viewport import ViewportHandler
        cmds = ViewportHandler.get_commands()
        assert "jump_to_view3d_object_by_name" in cmds
        assert "jump_to_tab_by_name" in cmds
        assert "jump_to_tab_by_space_type" in cmds

    @pytest.mark.skip(reason="Requires Blender Python API (bpy)")
    def test_weak_sandbox(self):
        import sys
        from weak_sandbox import WeakSandboxForLLM
        with WeakSandboxForLLM():
            try:
                sys.exit(0)
                assert False, "Should have raised"
            except RuntimeError:
                pass
