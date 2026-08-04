#!/usr/bin/env python3
"""
validate_tools.py — Valida todas las herramientas MCP en Blender.
Ejecuta cada comando vía socket y reporta éxito/fracaso.
"""
import json
import sys
import os

BLENDER = "/usr/bin/blender"
ADDON_DIR = os.path.expanduser("~/.config/blender/4.0/scripts/addons/axiom_engine")
PASS = "✅"
FAIL = "❌"
SKIP = "⏭️"

SCRIPT = f"""
import sys, os, json
sys.path.insert(0, "{ADDON_DIR}")

from _axsock import BlenderSocketServer
srv = BlenderSocketServer()
if not srv.running:
    srv.start()

# ─── all commands to test ───
commands = [
    # Core scene
    ("ping", {{}}, "basic"),
    ("get_scene_info", {{}}, "basic"),
    ("get_object_info", {{"name": "Cube"}}, "basic"),
    ("execute_code", {{"code": "print('ok')"}}, "basic"),

    # Objects
    ("create_object", {{"type": "SPHERE", "name": "test_sphere"}}, "objects"),
    ("create_object", {{"type": "CUBE", "name": "test_cube"}}, "objects"),
    ("create_object", {{"type": "CYLINDER", "name": "test_cyl"}}, "objects"),
    ("create_object", {{"type": "CONE", "name": "test_cone"}}, "objects"),
    ("create_object", {{"type": "TORUS", "name": "test_torus"}}, "objects"),
    ("create_object", {{"type": "PLANE", "name": "test_plane"}}, "objects"),
    ("transform_object", {{"name": "test_sphere", "location": [2,0,0]}}, "objects"),
    ("duplicate_object", {{"name": "test_sphere", "new_name": "sphere_copy"}}, "objects"),
    ("delete_object", {{"name": "sphere_copy"}}, "objects"),
    ("select_object", {{"name": "test_cube"}}, "objects"),

    # Materials
    ("create_material", {{"name": "mat_rojo", "color": [1,0,0,1]}}, "materials"),
    ("create_material", {{"name": "mat_azul", "color": [0,0,1,1], "roughness": 0.5, "metallic": 0.8}}, "materials"),
    ("assign_material", {{"object_name": "test_cube", "material_name": "mat_rojo"}}, "materials"),
    ("list_materials", {{}}, "materials"),

    # Lights
    ("create_light", {{"name": "test_luz", "light_type": "point", "energy": 200, "location": [0,0,5]}}, "lights"),
    ("setup_three_point_lighting", {{"target_name": "test_cube"}}, "lights"),

    # Camera
    ("create_camera", {{"name": "test_cam", "location": [5,-5,4], "lens": 50}}, "camera"),
    ("set_camera_target", {{"camera_name": "test_cam", "target_name": "test_cube"}}, "camera"),

    # Modifiers
    ("add_modifier", {{"object_name": "test_cube", "modifier_type": "subsurf"}}, "modifiers"),
    ("list_modifiers", {{"object_name": "test_cube"}}, "modifiers"),
    ("remove_modifier", {{"object_name": "test_cube", "modifier_name": "Subsurf"}}, "modifiers"),
    ("add_modifier", {{"object_name": "test_cyl", "modifier_type": "bevel"}}, "modifiers"),
    ("add_modifier", {{"object_name": "test_cone", "modifier_type": "mirror"}}, "modifiers"),

    # Animation
    ("insert_keyframe", {{"object_name": "test_sphere", "frame": 1, "property": "location"}}, "animation"),
    ("animate_location", {{"object_name": "test_sphere", "start_frame": 1, "end_frame": 30, "start_loc": [0,0,0], "end_loc": [5,0,0]}}, "animation"),
    ("set_render_range", {{"start": 1, "end": 30}}, "animation"),

    # UV
    ("create_object", {{"type": "CUBE", "name": "test_uv"}}, "uv"),
    ("unwrap_object", {{"object_name": "test_uv", "method": "smart"}}, "uv"),
    ("add_uv_map", {{"object_name": "test_uv"}}, "uv"),

    # Scene utils
    ("scene_summary", {{}}, "scene_utils"),
    ("mesh_analysis", {{"object_name": "test_cube"}}, "scene_utils"),
    ("hide_object", {{"object_name": "test_cube", "hide": True}}, "scene_utils"),
    ("hide_object", {{"object_name": "test_cube", "hide": False}}, "scene_utils"),

    # Batch
    ("batch_rename", {{"prefix": "renamed_"}}, "batch"),

    # IO
    ("list_export_formats", {{}}, "io"),

    # Shader Nodes
    ("add_shader_node", {{"material_name": "mat_rojo", "node_type": "bsdf_principled"}}, "shader"),
    ("list_shader_nodes", {{"material_name": "mat_rojo"}}, "shader"),
    ("set_node_value", {{"material_name": "mat_rojo", "node_name": "Principled BSDF", "input_name": "Roughness", "value": 0.5}}, "shader"),

    # Geometry Nodes
    ("add_geometry_nodes_modifier", {{"object_name": "test_cube"}}, "geometry"),
    ("list_gn_modifiers", {{"object_name": "test_cube"}}, "geometry"),

    # Rigging
    ("create_armature", {{"name": "test_armature"}}, "rigging"),
    ("add_bone", {{"armature_name": "test_armature", "bone_name": "test_bone", "head": [0,0,0], "tail": [0,0,1]}}, "rigging"),
    ("add_vertex_group", {{"object_name": "test_cube", "group_name": "test_vg"}}, "rigging"),
    ("add_constraint", {{"object_name": "test_cube", "constraint_type": "COPY_LOCATION", "target_name": "test_sphere"}}, "rigging"),

    # 3D Printing
    ("check_manifold", {{"object_name": "test_cube"}}, "printing"),
    ("set_dimensions_mm", {{"object_name": "test_cube", "width_mm": 100, "height_mm": 50}}, "printing"),
    ("add_wall_thickness", {{"object_name": "test_cube", "thickness_mm": 2}}, "printing"),

    # Animation extra
    ("create_action", {{"object_name": "test_sphere", "action_name": "test_action"}}, "animation"),
    ("set_keyframe_interpolation", {{"object_name": "test_sphere", "interpolation": "LINEAR"}}, "animation"),

    # Render
    ("set_render_resolution", {{"width": 640, "height": 480}}, "render"),
    ("set_render_engine", {{"engine": "WORKBENCH"}}, "render"),
    ("set_cycles_device", {{"device": "CPU"}}, "render"),

    # IO
    ("export_scene", {{"filepath": "/tmp/test_export.glb", "format": "glb"}}, "io"),
    ("export_selected", {{"filepath": "/tmp/test_selected.glb", "format": "glb"}}, "io"),

    # Batch
    ("batch_delete_by_type", {{"object_type": "LIGHT"}}, "batch"),
    ("apply_transforms_all", {{}}, "batch"),

    # Scene extra
    ("select_by_type", {{"object_type": "MESH"}}, "scene_utils"),
    ("apply_transform", {{"object_name": "test_cube"}}, "scene_utils"),

    # Material extra
    ("set_color", {{"object_name": "test_cube", "color": [0,1,0,1]}}, "materials"),

    # Analysis (Phase 1)
    ("get_objects_summary", {{}}, "analysis"),
    ("get_object_detail_summary", {{"name": "test_cube"}}, "analysis"),
    ("get_blendfile_summary_datablocks", {{}}, "analysis"),

    # Docs (Phase 4)
    ("search_api_docs", {{"query": "object"}}, "docs"),
    ("get_python_api_docs", {{"topic": "Object.location"}}, "docs"),

    # Viewport (Phase 5)
    ("jump_to_view3d_object_by_name", {{"name": "test_cube"}}, "viewport"),

    # Render (Phase 5)
    ("render_viewport_to_path", {{"filepath": "/tmp/test_render.png"}}, "render"),

    # Cleanup
    ("purge_orphans", {{}}, "scene_utils"),
]

results = {{"pass": 0, "fail": 0, "total": len(commands), "details": []}}

for cmd_type, params, category in commands:
    try:
        r = srv._execute({{"command": cmd_type, "args": params}})
        if r.get("status") == "success":
            results["pass"] += 1
            results["details"].append({{"cmd": cmd_type, "status": "PASS", "category": category}})
        else:
            results["fail"] += 1
            err = r.get("message", r.get("result", "unknown"))
            results["details"].append({{"cmd": cmd_type, "status": f"FAIL: {{err}}", "category": category}})
    except Exception as e:
        results["fail"] += 1
        results["details"].append({{"cmd": cmd_type, "status": f"ERROR: {{str(e)}}", "category": category}})

print("---RESULTS---")
print(json.dumps(results))
print("---END---")
"""

# Run in Blender
import subprocess
result = subprocess.run(
    [BLENDER, "-b", "--python-expr", SCRIPT],
    capture_output=True, text=True, timeout=60
)

output = result.stdout
if "---RESULTS---" in output:
    data = output.split("---RESULTS---")[1].split("---END---")[0].strip()
    r = json.loads(data)

    print(f"\n{'='*50}")
    print(f"  VALIDACIÖN DE TOOLS")
    print(f"{'='*50}")
    print(f"  Total: {r['total']} | {PASS} {r['pass']} | {FAIL} {r['fail']}")
    print(f"{'='*50}")

    # Group by category
    cats = {}
    for d in r["details"]:
        cat = d["category"]
        if cat not in cats:
            cats[cat] = {"pass": 0, "fail": 0, "total": 0}
        cats[cat]["total"] += 1
        if d["status"] == "PASS":
            cats[cat]["pass"] += 1
        else:
            cats[cat]["fail"] += 1

    for cat, stats in sorted(cats.items()):
        icon = PASS if stats["fail"] == 0 else FAIL
        print(f"  {icon} {cat}: {stats['pass']}/{stats['total']}")

    print()
    if r["fail"] > 0:
        print(f"  {FAIL} FALLOS:")
        for d in r["details"]:
            if d["status"] != "PASS":
                print(f"    - {d['cmd']}: {d['status']}")
    else:
        print(f"  {PASS} TODAS LAS TOOLS FUNCIONAN")
    print(f"{'='*50}")
else:
    print(f"ERROR: No se encontraron resultados")
    print(output[:1000])
