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
