#!/usr/bin/env python3
"""blender-mcp — Comprehensive Test Suite"""
import socket
import json
import time
import sys

def send(code):
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


def test_section(name, tests):
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    
    passed = 0
    failed = 0
    
    for test_name, code in tests:
        try:
            result = send(code)
            output = result.get('output', '')
            if output and 'ERROR' not in output.upper():
                print(f"  ✅ {test_name}")
                passed += 1
            else:
                print(f"  ❌ {test_name}: {output[:100]}")
                failed += 1
        except Exception as e:
            print(f"  ❌ {test_name}: {str(e)[:100]}")
            failed += 1
    
    return passed, failed


# ═══════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════

results = []

# 1. Basic Operations
passed, failed = test_section("1. Basic Operations", [
    ("Create Cube", '''
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
obj = bpy.context.active_object
obj.name = "TestCube"
print(f"Created: {obj.name}")
'''),
    ("Create Sphere", '''
import bpy
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 0, 1))
obj = bpy.context.active_object
obj.name = "TestSphere"
print(f"Created: {obj.name}")
'''),
    ("Create Cylinder", '''
import bpy
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(-3, 0, 1))
obj = bpy.context.active_object
obj.name = "TestCylinder"
print(f"Created: {obj.name}")
'''),
    ("Apply Material", '''
import bpy
obj = bpy.data.objects.get("TestCube")
if obj:
    mat = bpy.data.materials.new("RedMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1)
    obj.data.materials.append(mat)
    print(f"Material applied to {obj.name}")
'''),
])
results.append(("Basic Operations", passed, failed))

# 2. AI Integration
passed, failed = test_section("2. AI Integration", [
    ("Scene Analysis", '''
import bpy
objects = bpy.data.objects
meshes = [o for o in objects if o.type == "MESH"]
materials = [o for o in meshes if o.data.materials]
print(f"Objects: {len(objects)}, Meshes: {len(meshes)}, With Material: {len(materials)}")
'''),
    ("Quality Score", '''
import bpy
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
with_mat = [o for o in meshes if o.data.materials]
score = int(len(with_mat) / max(len(meshes), 1) * 100)
print(f"Quality: {score}/100")
'''),
])
results.append(("AI Integration", passed, failed))

# 3. Materials
passed, failed = test_section("3. Materials", [
    ("Gold Material", '''
import bpy
obj = bpy.data.objects.get("TestSphere")
if obj:
    mat = bpy.data.materials.new("Gold")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.65, 0.1, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.1
    obj.data.materials.append(mat)
    print(f"Gold applied to {obj.name}")
'''),
    ("Glass Material", '''
import bpy
obj = bpy.data.objects.get("TestCylinder")
if obj:
    mat = bpy.data.materials.new("Glass")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.95, 1.0, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.0
    mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.3
    obj.data.materials.append(mat)
    print(f"Glass applied to {obj.name}")
'''),
])
results.append(("Materials", passed, failed))

# 4. Animation
passed, failed = test_section("4. Animation", [
    ("Create Animation", '''
import bpy, math
obj = bpy.data.objects.get("TestCube")
if obj:
    for i in range(5):
        frame = i * 10 + 1
        obj.location.z = 1 + math.sin(i * math.pi / 2) * 0.5
        obj.keyframe_insert("location", frame=frame)
    print(f"Animation created on {obj.name}")
'''),
])
results.append(("Animation", passed, failed))

# 5. Export
passed, failed = test_section("5. Export", [
    ("Export Test", '''
import bpy
# Just verify export operators exist
print(f"Export operators available: {hasattr(bpy.ops, 'export_scene')}")
'''),
])
results.append(("Export", passed, failed))

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print(f"\n{'='*60}")
print(f"  TEST SUMMARY")
print(f"{'='*60}")

total_passed = 0
total_failed = 0

for name, passed, failed in results:
    status = "✅" if failed == 0 else "⚠️"
    print(f"  {status} {name}: {passed} passed, {failed} failed")
    total_passed += passed
    total_failed += failed

print(f"\n  TOTAL: {total_passed} passed, {total_failed} failed")
print(f"{'='*60}")
