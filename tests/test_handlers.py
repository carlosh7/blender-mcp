"""
blender-mcp — Tool Module Tests
Tests for modular tool architecture (src/tools/*).
"""

import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


REQUIRED_CATEGORIES = [
    "scene",
    "objects",
    "materials",
    "modifiers",
    "lights",
    "camera",
    "shader_nodes",
    "animation",
    "io",
    "printing",
    "rigging",
    "scene_utils",
    "geometry_nodes",
    "geometry_nodes_extended",
    "shader_nodes_extended",
    "render",
    "uv_texture",
    "batch",
    "mesh_edit",
    "animation_advanced",
    "physics",
    "curves_text",
    "compositor",
    "addon_bridge",
    "collab",
    "vlm_feedback",
]

EXPECTED_TOOLS_PER_CATEGORY = {
    "scene": ["scene.get_info", "scene.create", "scene.render_settings"],
    "objects": ["object.create", "object.delete", "object.transform", "object.list"],
    "materials": ["material.create", "material.assign", "material.list"],
    "modifiers": ["modifier.add", "modifier.remove", "modifier.list", "modifier.apply"],
    "lights": ["light.create", "light.three_point"],
    "camera": ["camera.create", "camera.set_active"],
    "shader_nodes": ["shader.add_node", "shader.connect_nodes", "shader.list_nodes"],
    "animation": ["animation.keyframe_insert"],
    "io": ["io.export_gltf", "io.import_fbx"],
    "printing": ["printing.check_manifold", "printing.set_dimensions_mm"],
    "rigging": ["rigging.create_armature", "rigging.add_bone"],
    "scene_utils": ["scene_utils.purge_orphans", "scene_utils.mesh_analysis"],
    "geometry_nodes": ["geonodes.create_group", "geonodes.add_node"],
    "geometry_nodes_extended": ["geonodes.mesh_cube", "geonodes.mesh_circle"],
    "shader_nodes_extended": ["shader.brick_texture", "shader.checker_texture"],
    "render": ["render.set_engine"],
    "uv_texture": ["uv.smart_project"],
    "batch": ["batch.rename"],
    "mesh_edit": ["mesh.get_topology", "mesh.extrude_faces", "mesh.bevel_edges"],
    "animation_advanced": [
        "animation.fcurve_info",
        "animation.driver_add",
        "animation.shape_key_add",
    ],
    "physics": ["physics.rigidbody_add", "physics.cloth_add", "physics.force_field_add"],
    "curves_text": ["curve.bezier_add", "text.add", "metaball.add"],
    "compositor": ["compositor.node_add", "compositor.node_set_input"],
    "addon_bridge": ["material.pbr", "sculpt.base", "scene.check_blockout"],
    "collab": ["collab.lock_acquire", "asset.save", "blueprint.save"],
    "vlm_feedback": ["vlm.capture", "vlm.analyze"],
}


class TestToolModuleImports:
    """Test that all tool modules import correctly."""

    @pytest.mark.parametrize("category", REQUIRED_CATEGORIES)
    def test_module_imports(self, category):
        module = importlib.import_module(f"mcp_ultra.tools.{category}")
        assert module is not None

    @pytest.mark.parametrize("category", REQUIRED_CATEGORIES)
    def test_tools_not_empty(self, category):
        module = importlib.import_module(f"mcp_ultra.tools.{category}")
        assert hasattr(module, "TOOLS"), f"tools.{category} missing TOOLS"
        assert len(module.TOOLS) > 0, f"tools.{category}.TOOLS is empty"

    @pytest.mark.parametrize("category", REQUIRED_CATEGORIES)
    def test_handlers_not_empty(self, category):
        module = importlib.import_module(f"mcp_ultra.tools.{category}")
        assert hasattr(module, "HANDLERS"), f"tools.{category} missing HANDLERS"
        assert len(module.HANDLERS) > 0, f"tools.{category}.HANDLERS is empty"

    @pytest.mark.parametrize("category", REQUIRED_CATEGORIES)
    def test_all_tools_have_handlers(self, category):
        module = importlib.import_module(f"mcp_ultra.tools.{category}")
        for tool in module.TOOLS:
            assert tool.name in module.HANDLERS, (
                f"Handler missing for {tool.name} in tools.{category}"
            )


class TestExpectedToolNames:
    """Validate expected tools exist per category."""

    @pytest.mark.parametrize("category,expected", EXPECTED_TOOLS_PER_CATEGORY.items())
    def test_expected_tools_present(self, category, expected):
        module = importlib.import_module(f"mcp_ultra.tools.{category}")
        tool_names = {t.name for t in module.TOOLS}
        for tool_name in expected:
            assert tool_name in tool_names, (
                f"Expected tool {tool_name} not found in tools.{category}"
            )


class TestToolRegistry:
    """Test the central tool registry."""

    def test_registry_import(self):
        from mcp_ultra.tools import ToolRegistry

        assert ToolRegistry is not None

    def test_registry_register_and_execute(self):
        from mcp_ultra.core.entities import Tool, ToolCategory, ToolPermission
        from mcp_ultra.tools import ToolRegistry

        registry = ToolRegistry()
        tool = Tool(
            name="test.tool",
            category=ToolCategory.SCENE,
            description="Test tool",
            permission=ToolPermission.READ_ONLY,
        )
        registry.register_tool(tool, lambda: {"success": True})
        assert registry.get_tool("test.tool") is not None

        result = registry.execute_tool("test.tool", {})
        assert result.success is True

    def test_registry_list_tools(self):
        from mcp_ultra.core.entities import Tool, ToolCategory, ToolPermission
        from mcp_ultra.tools import ToolRegistry

        registry = ToolRegistry()
        tool = Tool(
            name="test.tool",
            category=ToolCategory.SCENE,
            description="Test tool",
            permission=ToolPermission.READ_ONLY,
        )
        registry.register_tool(tool, lambda: {"success": True})
        tools = registry.list_tools()
        assert len(tools) == 1

    def test_registry_stats(self):
        from mcp_ultra.core.entities import Tool, ToolCategory, ToolPermission
        from mcp_ultra.tools import ToolRegistry

        registry = ToolRegistry()
        tool = Tool(
            name="test.tool",
            category=ToolCategory.SCENE,
            description="Test tool",
            permission=ToolPermission.READ_ONLY,
        )
        registry.register_tool(tool, lambda: {"success": True})
        stats = registry.get_stats()
        assert stats["total_tools"] == 1
