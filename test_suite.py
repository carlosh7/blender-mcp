#!/usr/bin/env python3
"""blender-mcp — Complete Test Suite"""
import sys
import os
import time

sys.path.insert(0, '/home/carlosh/blender-mcp/addon')


def run_in_blender(code):
    """Execute code in Blender via socket"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(25)
    s.connect(('localhost', 9876))
    s.send(json.dumps({'command': 'execute_code', 'params': {'code': code}}).encode() + b'\n')
    r = b''
    dl = time.time() + 20
    while time.time() < dl:
        try:
            c = s.recv(65536)
            if c:
                r += c
                if b'\n' in r:
                    break
        except:
            continue
    s.close()
    if r:
        return json.loads(r.decode().strip()).get('result', {})
    return {}


import json


# ═══════════════════════════════════════════════════════════════
# TEST CATEGORIES
# ═══════════════════════════════════════════════════════════════

results = {"passed": 0, "failed": 0, "errors": []}


def test(name, test_func):
    """Run a test and track results"""
    try:
        result = test_func()
        if result:
            results["passed"] += 1
            print(f"  PASS: {name}")
        else:
            results["failed"] += 1
            results["errors"].append(name)
            print(f"  FAIL: {name}")
    except Exception as e:
        results["failed"] += 1
        results["errors"].append(f"{name}: {str(e)[:50]}")
        print(f"  ERROR: {name}: {str(e)[:50]}")


# ═══════════════════════════════════════════════════════════════
# AI TESTS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("AI INTEGRATION TESTS")
print("="*60)

from ai.ai_integration import query_llm, parse_description_with_ai, test_connection

test("Ollama Connection", lambda: test_connection())

test("LLM: 2+2", lambda: "4" in query_llm("What is 2+2? (one word)"))

test("Parse: chair", lambda: parse_description_with_ai("Una silla roja").get("type") == "furniture")

test("Parse: car", lambda: parse_description_with_ai("Un coche azul").get("type") == "vehicle")

test("Parse: house", lambda: parse_description_with_ai("Una casa").get("type") == "building")


# ═══════════════════════════════════════════════════════════════
# VOICE CONTROL TESTS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("VOICE CONTROL TESTS")
print("="*60)

from ai.voice_control import parse_voice_command

test("Voice: create", lambda: parse_voice_command("Crear cubo").get("action") == "create")

test("Voice: delete", lambda: parse_voice_command("Eliminar esfera").get("action") == "delete")

test("Voice: analyze", lambda: parse_voice_command("Analizar escena").get("action") == "analyze")

test("Voice: export", lambda: parse_voice_command("Exportar modelo").get("action") == "export")


# ═══════════════════════════════════════════════════════════════
# REFERENCE COMPARE TESTS
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("REFERENCE COMPARE TESTS")
print("="*60)

from perception.reference_compare import ReferenceComparator

def test_reference():
    comp = ReferenceComparator()
    comp.add_reference("chair", "", "furniture", "red")
    results = comp.compare_with_scene()
    return len(results) == 1

test("Reference Comparator", test_reference)


# ═══════════════════════════════════════════════════════════════
# BLENDER TESTS (require running Blender)
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("BLENDER TESTS")
print("="*60)

def test_blender_ping():
    r = run_in_blender('print("ping")')
    return r.get('output', '') == 'ping'

test("Blender Ping", test_blender_ping)


def test_blender_create():
    r = run_in_blender('''
import bpy
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
print(bpy.context.active_object.name)
''')
    return "TestCube" in r.get('output', '') or "Cube" in r.get('output', '')

test("Blender Create Cube", test_blender_create)


def test_blender_material():
    r = run_in_blender('''
import bpy
obj = bpy.context.active_object
if obj:
    mat = bpy.data.materials.new("TestMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1,0,0,1)
    obj.data.materials.append(mat)
    print("material_applied")
''')
    return "material_applied" in r.get('output', '')

test("Blender Apply Material", test_blender_material)


def test_blender_scene_info():
    r = run_in_blender('''
import bpy
print(f"objects:{len(bpy.data.objects)}")
''')
    return "objects:" in r.get('output', '')

test("Blender Scene Info", test_blender_scene_info)


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print(f"  Passed: {results['passed']}")
print(f"  Failed: {results['failed']}")
if results['errors']:
    print(f"  Errors: {results['errors']}")
print(f"  Rate: {results['passed']/(results['passed']+results['failed'])*100:.1f}%")
print("="*60)
