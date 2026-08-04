"""
test_command_surface.py — Offline validation of the Blender command surface.

Runs every command from validate_tools.COMMANDS through the real
addon/_axsock.BlenderSocketServer._execute dispatcher against a fake bpy
(bpy_stub). Proves: dispatch wiring, parameter handling, registry coverage,
return shapes, and absence of NameError/AttributeError across the surface —
without needing a Blender binary.

Complements validate_tools.py, which runs the same list against `blender -b`.
"""
import os
import sys

import pytest

# Install the bpy/bmesh/mathutils stub BEFORE importing any addon module.
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import bpy_stub  # noqa: E402
bpy_stub.install()

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from validate_tools import COMMANDS  # noqa: E402
from addon._axsock import BlenderSocketServer  # noqa: E402


@pytest.fixture(scope="module")
def srv():
    return BlenderSocketServer()


@pytest.fixture(scope="module")
def results(srv):
    out = {}
    for cmd_type, params, category in COMMANDS:
        try:
            r = srv._execute({"command": cmd_type, "args": params})
            out[cmd_type] = r
        except Exception as e:  # pragma: no cover - defensive
            out[cmd_type] = {"status": "error", "message": f"EXC {type(e).__name__}: {e}"}
    return out


def test_every_documented_command_succeeds(results):
    from validate_tools import is_ui_required
    failures = {c: r for c, r in results.items()
                if r.get("status") != "success"
                and not is_ui_required(r.get("message", ""))}
    assert not failures, f"{len(failures)} commands failed: {failures}"


def test_unknown_command_returns_error(srv):
    r = srv._execute({"command": "definitely_not_a_command", "args": {}})
    assert r["status"] == "error"

    assert "Perintah tidak dikenal" in r["message"]
def test_create_object_creates_mesh(srv):
    r = srv._execute({"command": "create_object",
                      "args": {"type": "SPHERE", "name": "surface_sphere",
                               "radius": 0.5, "segments": 16, "vertices": 8}})
    assert r["status"] == "success"
    obj = r["result"]
    assert obj["object"] == "surface_sphere"
    assert obj["type"] == "SPHERE"
    import bpy
    mesh = bpy.data.objects["surface_sphere"].data
    assert len(mesh.vertices) > 8
    assert len(mesh.polygons) > 0


def test_create_object_rejects_bad_type(srv):
    r = srv._execute({"command": "create_object",
                      "args": {"type": "NOPE", "name": "x"}})
    assert r["status"] == "error"
    assert "Tipe tidak dikenal" in r["message"]


def test_material_pipeline(srv):
    r = srv._execute({"command": "create_material",
                      "args": {"name": "surface_mat", "color": [1, 0, 0, 1],
                               "roughness": 0.25, "metallic": 0.9}})
    assert r["status"] == "success"
    import bpy
    mat = bpy.data.materials["surface_mat"]
    assert mat.use_nodes
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    assert bsdf.inputs["Roughness"].default_value == 0.25
    assert bsdf.inputs["Metallic"].default_value == 0.9
    assert list(bsdf.inputs["Base Color"].default_value) == [1.0, 0.0, 0.0, 1.0]

    r = srv._execute({"command": "assign_material",
                      "args": {"object_name": "surface_sphere",
                               "material_name": "surface_mat"}})
    assert r["status"] == "success"
    assert bpy.data.objects["surface_sphere"].data.materials[0].name == "surface_mat"


def test_shader_node_graph(srv):
    r = srv._execute({"command": "add_shader_node",
                      "args": {"material_name": "surface_mat",
                               "node_type": "emission"}})
    assert r["status"] == "success"
    node_name = r["result"]["node"]
    r = srv._execute({"command": "set_node_value",
                      "args": {"material_name": "surface_mat",
                               "node_name": node_name,
                               "input_name": "Strength", "value": 3.0}})
    assert r["status"] == "success"
    r = srv._execute({"command": "connect_shader_nodes",
                      "args": {"material_name": "surface_mat",
                               "from_node": node_name, "from_output": "Emission",
                               "to_node": "Principled BSDF",
                               "to_input": "Emission Strength"}})
    assert r["status"] == "success"


def test_animation_pipeline(srv):
    r = srv._execute({"command": "create_object",
                      "args": {"type": "CUBE", "name": "anim_cube"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "animate_location",
                      "args": {"object_name": "anim_cube",
                               "start_frame": 1, "end_frame": 50,
                               "start_loc": [0, 0, 0], "end_loc": [3, 4, 5]}})
    assert r["status"] == "success"
    import bpy
    obj = bpy.data.objects["anim_cube"]
    assert list(obj.location) == [3.0, 4.0, 5.0]
    assert obj.animation_data is not None
    r = srv._execute({"command": "set_keyframe_interpolation",
                      "args": {"object_name": "anim_cube",
                               "interpolation": "LINEAR"}})
    assert r["status"] == "success"


def test_rigging_pipeline(srv):
    r = srv._execute({"command": "create_armature",
                      "args": {"name": "surface_rig", "add_root_bone": False}})
    assert r["status"] == "success"
    r = srv._execute({"command": "add_bone",
                      "args": {"armature_name": "surface_rig",
                               "bone_name": "Leg.L",
                               "head": [0, 0, 0], "tail": [0, 0, 1]}})
    assert r["status"] == "success"
    r = srv._execute({"command": "add_bone",
                      "args": {"armature_name": "surface_rig",
                               "bone_name": "Foot.L",
                               "head": [0, 0, 1], "tail": [0.2, 0, 1],
                               "parent": "Leg.L"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "list_bones",
                      "args": {"armature_name": "surface_rig"}})
    assert r["result"]["count"] == 2
    r = srv._execute({"command": "setup_ik_chain",
                      "args": {"armature_name": "surface_rig",
                               "bone_name": "Leg.L",
                               "target_object": "anim_cube",
                               "chain_count": 2}})
    assert r["status"] == "success"


def test_vertex_groups_and_weights(srv):
    r = srv._execute({"command": "add_vertex_group",
                      "args": {"object_name": "anim_cube",
                               "group_name": "surface_vg"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "assign_vertex_weights",
                      "args": {"object_name": "anim_cube",
                               "group_name": "surface_vg",
                               "vertex_indices": [0, 1, 2], "weight": 0.5}})
    assert r["status"] == "success"
    import bpy
    vg = bpy.data.objects["anim_cube"].vertex_groups.get("surface_vg")
    assert vg.weight(0) == 0.5


def test_manifold_and_dimensions(srv):
    r = srv._execute({"command": "create_object",
                      "args": {"type": "CUBE", "name": "print_cube"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "check_manifold",
                      "args": {"object_name": "print_cube"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "set_dimensions_mm",
                      "args": {"object_name": "print_cube",
                               "width_mm": 50, "height_mm": 20}})
    assert r["status"] == "success"
    import bpy
    d = bpy.data.objects["print_cube"].dimensions
    assert abs(d.x - 0.05) < 1e-6
    assert abs(d.z - 0.02) < 1e-6


def test_bed_layout_positions_on_bed(srv):
    r = srv._execute({"command": "bed_layout",
                      "args": {"object_names": ["print_cube", "anim_cube",
                                                "surface_sphere"],
                               "bed_width_mm": 200, "bed_height_mm": 200,
                               "margin_mm": 5}})
    assert r["status"] == "success"
    import bpy
    for name in ("print_cube", "anim_cube", "surface_sphere"):
        obj = bpy.data.objects[name]
        assert obj.location.z == 0.0
        assert obj.location.x >= 0.005


def test_join_objects_merges_topology(srv):
    r = srv._execute({"command": "create_object",
                      "args": {"type": "CUBE", "name": "join_a"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "create_object",
                      "args": {"type": "CUBE", "name": "join_b"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "join_objects",
                      "args": {"object_names": ["join_a", "join_b"],
                               "new_name": "join_merged"}})
    assert r["status"] == "success"
    import bpy
    merged = bpy.data.objects["join_merged"].data
    assert len(merged.vertices) == 16
    assert len(merged.polygons) == 12


def test_geometry_nodes_scatter(srv):
    r = srv._execute({"command": "create_object",
                      "args": {"type": "PLANE", "name": "gn_ground"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "create_object",
                      "args": {"type": "CUBE", "name": "gn_rock"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "scatter_instances",
                      "args": {"object_name": "gn_ground",
                               "instance_object": "gn_rock",
                               "count": 50}})
    assert r["status"] == "success"
    import bpy
    mods = [m for m in bpy.data.objects["gn_ground"].modifiers if m.type == "NODES"]
    assert len(mods) == 1
    assert mods[0].node_group is not None


def test_uv_unwrap_creates_layer(srv):
    r = srv._execute({"command": "unwrap_object",
                      "args": {"object_name": "surface_sphere",
                               "method": "SMART", "name": "TestUV"}})
    assert r["status"] == "success"
    import bpy
    mesh = bpy.data.objects["surface_sphere"].data
    assert any(u.name == "TestUV" for u in mesh.uv_layers)


def test_every_mcp_tool_command_is_dispatchable(srv):
    """Wiring invariant: every command exposed by mcp_tools must resolve."""
    from mcp_tools import TOOL_META
    import addon.handlers as handlers
    missing = []
    for name, meta in TOOL_META.items():
        cmd = meta["command"]
        if getattr(srv, f"cmd_{cmd}", None) is None and \
                handlers.get_handler(cmd) is None:
            missing.append((name, cmd))
    assert not missing, f"Undispatchable tools: {missing}"


def test_handler_registry_coverage():
    """Every documented command must exist in the handler registry or legacy."""
    import addon.handlers as handlers
    from mcp_tools import TOOL_META
    missing = []
    for _, meta in TOOL_META.items():
        if meta["command"] not in handlers.HANDLERS and \
                meta["command"] not in ("execute_code", "get_viewport_screenshot",
                                        "search_api_docs", "get_python_api_docs",
                                        "ping", "snap_and_parent", "snap_to_anchor",
                                        "apply_symmetry", "fix_normals",
                                        "get_object_anchors", "get_model_blueprint",
                                        "get_spatial_visual", "validate_geometry",
                                        "get_scene_property", "get_scene_info",
                                        "cleanup_scene", "analyze_performance",
                                        "export_glb", "get_scene_info",
                                        "generate_3d", "search_assets"):
            missing.append(meta["command"])
    assert not missing, f"Commands without any backend: {missing}"


def test_v2_new_commands(srv):
    """Command gabungan baru: empty, subdivide, loop cut, armature modifier."""
    r = srv._execute({"command": "create_object",
                      "args": {"type": "CUBE", "name": "v2_cube"}})
    assert r["status"] == "success"
    r = srv._execute({"command": "create_empty",
                      "args": {"name": "v2_empty"}})
    assert r["status"] == "success"
    import bpy
    assert bpy.data.objects["v2_empty"].type == "EMPTY"

    r = srv._execute({"command": "subdivide_mesh",
                      "args": {"object_name": "v2_cube", "cuts": 2}})
    assert r["status"] == "success"
    r = srv._execute({"command": "loop_cut",
                      "args": {"object_name": "v2_cube",
                               "plane_no": [0, 1, 0]}})
    assert r["status"] == "success"

    r = srv._execute({"command": "create_armature",
                      "args": {"name": "v2_rig", "add_root_bone": True}})
    assert r["status"] == "success"
    r = srv._execute({"command": "add_armature_modifier",
                      "args": {"object_name": "v2_cube",
                               "armature_name": "v2_rig"}})
    assert r["status"] == "success"
    mods = [m for m in bpy.data.objects["v2_cube"].modifiers]
    assert any(m.type == "ARMATURE" for m in mods)

    r = srv._execute({"command": "animate_location",
                      "args": {"object_name": "v2_cube",
                               "start_frame": 1, "end_frame": 30,
                               "start_loc": [0, 0, 0], "end_loc": [1, 0, 0]}})
    assert r["status"] == "success"
    r = srv._execute({"command": "clear_keyframes",
                      "args": {"object_name": "v2_cube", "property": "all"}})
    ad = bpy.data.objects["v2_cube"].animation_data
    action = getattr(ad, "action", None) if ad else None
    assert ad is None or action is None or len(action.fcurves) == 0
