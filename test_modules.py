#!/usr/bin/env python3
"""blender-mcp — Module Tests"""
import sys
import os

sys.path.insert(0, '/home/carlosh/blender-mcp/addon')

results = {"passed": 0, "failed": 0}


def test(name, func):
    try:
        if func():
            results["passed"] += 1
            print(f"  PASS: {name}")
        else:
            results["failed"] += 1
            print(f"  FAIL: {name}")
    except Exception as e:
        results["failed"] += 1
        print(f"  ERROR: {name}: {str(e)[:50]}")


# Test imports
print("="*50)
print("MODULE IMPORT TESTS")
print("="*50)

def test_import_mesh():
    from core.mesh_engine import create_advanced_primitive
    return True

def test_import_texture():
    from core.texture_engine import create_pbr_material
    return True

def test_import_rig():
    from core.rig_engine import create_humanoid_rig
    return True

def test_import_animation():
    from core.animation_engine import create_walk_cycle
    return True

def test_import_physics():
    from physics.physics_engine import add_rigid_body, add_cloth, add_fluid_domain
    return True

def test_import_character():
    from organic.character_gen import create_character
    return True

def test_import_sculpt():
    from organic.sculpt_engine import create_sculpt_base, sculpt_face
    return True

def test_import_ai():
    from ai.ai_integration import text_to_3d, query_llm
    return True

def test_import_voice():
    from ai.voice_control import parse_voice_command, execute_voice_command
    return True

def test_import_perception():
    from perception.perception_system import analyze_scene
    return True

def test_import_reference():
    from perception.reference_system import ReferenceManager
    return True

def test_import_compare():
    from perception.reference_compare import ReferenceComparator
    return True

def test_import_quality():
    from perception.quality_refinement import refine_quality
    return True

def test_import_libraries():
    from libraries.libraries import get_material_from_library
    return True

def test_import_export():
    from export.export_engine import smart_export
    return True

test("Mesh Engine", test_import_mesh)
test("Texture Engine", test_import_texture)
test("Rig Engine", test_import_rig)
test("Animation Engine", test_import_animation)
test("Physics Engine", test_import_physics)
test("Character Gen", test_import_character)
test("Sculpt Engine", test_import_sculpt)
test("AI Integration", test_import_ai)
test("Voice Control", test_import_voice)
test("Perception", test_import_perception)
test("Reference System", test_import_reference)
test("Reference Compare", test_import_compare)
test("Quality Refinement", test_import_quality)
test("Libraries", test_import_libraries)
test("Export Engine", test_import_export)

# Test functionality
print("\n" + "="*50)
print("FUNCTIONALITY TESTS")
print("="*50)

def test_ai_connection():
    from ai.ai_integration import test_connection
    return test_connection()

def test_voice_parse():
    from ai.voice_control import parse_voice_command
    result = parse_voice_command("Crear cubo rojo")
    return result.get("action") == "create"

def test_reference_compare():
    from perception.reference_compare import ReferenceComparator
    comp = ReferenceComparator()
    comp.add_reference("test", "", "furniture", "red")
    results = comp.compare_with_scene()
    return len(results) == 1

def test_material_library():
    from libraries.libraries import list_material_library
    mats = list_material_library()
    return len(mats) > 20

def test_animation_presets():
    from core.animation_engine import list_animation_presets
    presets = list_animation_presets()
    return len(presets) > 10

def test_physics_presets():
    from physics.physics_engine import list_physics_types
    types = list_physics_types()
    return len(types) > 5

test("AI Connection", test_ai_connection)
test("Voice Parse", test_voice_parse)
test("Reference Compare", test_reference_compare)
test("Material Library", test_material_library)
test("Animation Presets", test_animation_presets)
test("Physics Presets", test_physics_presets)

# Summary
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
total = results["passed"] + results["failed"]
print(f"  Total: {total}")
print(f"  Passed: {results['passed']}")
print(f"  Failed: {results['failed']}")
print(f"  Rate: {results['passed']/max(total,1)*100:.1f}%")
