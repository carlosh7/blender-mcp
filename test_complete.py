#!/usr/bin/env python3
"""blender-mcp — COMPLETE TEST SUITE"""

import json
import socket
import sys
import time


def send(code):
    """Execute code in Blender via socket"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect(("localhost", 9876))
    s.send(json.dumps({"command": "execute_code", "params": {"code": code}}).encode() + b"\n")
    r = b""
    dl = time.time() + 25
    while time.time() < dl:
        try:
            c = s.recv(65536)
            if c:
                r += c
                if b"\n" in r:
                    break
        except Exception:
            continue
    s.close()
    if r:
        return json.loads(r.decode().strip()).get("result", {})
    return {}


results = {"passed": 0, "failed": 0, "errors": []}


def test(name, func):
    """Run a test and track results"""
    try:
        result = func()
        if result:
            results["passed"] += 1
            print(f"  ✅ {name}")
        else:
            results["failed"] += 1
            results["errors"].append(name)
            print(f"  ❌ {name}")
    except Exception as e:
        results["failed"] += 1
        results["errors"].append(f"{name}: {str(e)[:50]}")
        print(f"  ❌ {name}: {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════
# TEST 1: BASIC OPERATIONS
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 1: BASIC OPERATIONS")
print("=" * 60)

test(
    "Create Cube",
    lambda: (
        send("""
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,1))
print(bpy.context.active_object.name)
""").get("output", "")
        != ""
    ),
)

test(
    "Create Sphere",
    lambda: (
        send("""
import bpy
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3,0,1))
print(bpy.context.active_object.name)
""").get("output", "")
        != ""
    ),
)

test(
    "Create Cylinder",
    lambda: (
        send("""
import bpy
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(-3,0,1))
print(bpy.context.active_object.name)
""").get("output", "")
        != ""
    ),
)

test(
    "Apply Material",
    lambda: (
        send("""
import bpy
obj = bpy.context.active_object
if obj:
    mat = bpy.data.materials.new("TestMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1,0,0,1)
    obj.data.materials.append(mat)
    print("material_applied")
""").get("output", "")
        != ""
    ),
)


# ═══════════════════════════════════════════════════════════════
# TEST 2: AI INTEGRATION
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 2: AI INTEGRATION")
print("=" * 60)

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "addon"))

from ai.ai_integration import parse_description_with_ai, query_llm, test_connection

test("Ollama Connection", lambda: test_connection())

test("LLM: 2+2", lambda: "4" in query_llm("What is 2+2? (one word)"))

test("Parse: chair", lambda: parse_description_with_ai("Una silla roja").get("type") == "furniture")

test("Parse: car", lambda: parse_description_with_ai("Un coche azul").get("type") == "vehicle")


# ═══════════════════════════════════════════════════════════════
# TEST 3: VOICE CONTROL
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 3: VOICE CONTROL")
print("=" * 60)

from ai.voice_control import parse_voice_command

test("Voice: create", lambda: parse_voice_command("Crear cubo").get("action") == "create")

test("Voice: delete", lambda: parse_voice_command("Eliminar esfera").get("action") == "delete")

test("Voice: analyze", lambda: parse_voice_command("Analizar escena").get("action") == "analyze")


# ═══════════════════════════════════════════════════════════════
# TEST 4: REFERENCE SYSTEM
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 4: REFERENCE SYSTEM")
print("=" * 60)

from perception.reference_system import REFERENCE_TEMPLATES, ReferenceManager

test("Templates", lambda: len(REFERENCE_TEMPLATES) == 6)

test("ReferenceManager", lambda: ReferenceManager() is not None)


# ═══════════════════════════════════════════════════════════════
# TEST 5: REFERENCE COMPARE
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 5: REFERENCE COMPARE")
print("=" * 60)

from perception.reference_compare import ReferenceComparator

test("Comparator", lambda: ReferenceComparator() is not None)


# ═══════════════════════════════════════════════════════════════
# TEST 6: MATERIAL LIBRARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 6: MATERIAL LIBRARY")
print("=" * 60)

from libraries.libraries import list_material_library

test("50 materials", lambda: len(list_material_library()) >= 50)


# ═══════════════════════════════════════════════════════════════
# TEST 7: BUILDING GENERATOR
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 7: BUILDING GENERATOR")
print("=" * 60)

from libraries.building_generator import list_building_types

test("5 building types", lambda: len(list_building_types()) == 5)


# ═══════════════════════════════════════════════════════════════
# TEST 8: EXPORT ENGINE
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 8: EXPORT ENGINE")
print("=" * 60)

from export.export_engine import list_export_formats

test("6 export formats", lambda: len(list_export_formats()) == 6)


# ═══════════════════════════════════════════════════════════════
# TEST 9: PHYSICS ENGINE
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 9: PHYSICS ENGINE")
print("=" * 60)

from physics.physics_engine import list_physics_types

test("8 physics types", lambda: len(list_physics_types()) == 8)


# ═══════════════════════════════════════════════════════════════
# TEST 10: PROCEDURAL GENERATOR
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 10: PROCEDURAL GENERATOR")
print("=" * 60)

from organic.procedural_generator import list_procedural_types

test("10 procedural types", lambda: len(list_procedural_types()) == 10)


# ═══════════════════════════════════════════════════════════════
# TEST 11: ANIMATION ENGINE
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 11: ANIMATION ENGINE")
print("=" * 60)

from core.animation_engine import list_animation_presets

test("20 animation presets", lambda: len(list_animation_presets()) == 20)


# ═══════════════════════════════════════════════════════════════
# TEST 12: BLENDER INTEGRATION
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST 12: BLENDER INTEGRATION")
print("=" * 60)

test("Ping Blender", lambda: send('print("ping")').get("output", "") == "ping")

test("Scene Info", lambda: send("import bpy; print(len(bpy.data.objects))").get("output", "") != "")


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)

total = results["passed"] + results["failed"]
print(f"  Total: {total}")
print(f"  Passed: {results['passed']}")
print(f"  Failed: {results['failed']}")
if results["errors"]:
    print(f"  Errors: {results['errors']}")
print(f"  Rate: {results['passed'] / max(total, 1) * 100:.1f}%")
print("=" * 60)
