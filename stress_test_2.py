#!/usr/bin/env python3
"""blender-mcp — STRESS TEST 2: Rigging + Array + Batch"""

import json
import socket
import time


def run(code):
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
    data = json.loads(r.decode().strip())
    return data.get("result", data)


def phase(name):
    print(f"\n{'=' * 60}\n{name}\n{'=' * 60}")


# FASE 1: RIGGING
phase("FASE 1: RIGGING - Armature + Bones")
print(
    run("""
import bpy
from mathutils import Vector
arm_data = bpy.data.armatures.new("RigData")
arm_obj = bpy.data.objects.new("Character", arm_data)
bpy.context.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
arm = arm_obj.data
root = arm.edit_bones[0]; root.name = "Root"
root.head = Vector((0,0,0)); root.tail = Vector((0,0,0.3))
sp = arm.edit_bones.new("Spine"); sp.head = Vector((0,0,0.3)); sp.tail = Vector((0,0,0.8)); sp.parent = root
hd = arm.edit_bones.new("Head"); hd.head = Vector((0,0,0.8)); hd.tail = Vector((0,0,1.1)); hd.parent = sp
ua = arm.edit_bones.new("UpperArm_L"); ua.head = Vector((0,0,0.75)); ua.tail = Vector((0.4,0,0.7)); ua.parent = sp
la = arm.edit_bones.new("LowerArm_L"); la.head = Vector((0.4,0,0.7)); la.tail = Vector((0.7,0,0.6)); la.parent = ua
ua2 = arm.edit_bones.new("UpperArm_R"); ua2.head = Vector((0,0,0.75)); ua2.tail = Vector((-0.4,0,0.7)); ua2.parent = sp
la2 = arm.edit_bones.new("LowerArm_R"); la2.head = Vector((-0.4,0,0.7)); la2.tail = Vector((-0.7,0,0.6)); la2.parent = ua2
ul = arm.edit_bones.new("UpperLeg_L"); ul.head = Vector((0.15,0,0)); ul.tail = Vector((0.15,0,-0.5)); ul.parent = root
ll = arm.edit_bones.new("LowerLeg_L"); ll.head = Vector((0.15,0,-0.5)); ll.tail = Vector((0.15,0,-1.0)); ll.parent = ul
ur = arm.edit_bones.new("UpperLeg_R"); ur.head = Vector((-0.15,0,0)); ur.tail = Vector((-0.15,0,-0.5)); ur.parent = root
lr = arm.edit_bones.new("LowerLeg_R"); lr.head = Vector((-0.15,0,-0.5)); lr.tail = Vector((-0.15,0,-1.0)); lr.parent = ur
bpy.ops.object.mode_set(mode="OBJECT")
print(f"Armature: {arm_obj.name} ({len(arm.bones)} bones)")
for b in arm.bones:
    print(f"  - {b.name}")
""").get("output", "")
)

# FASE 2: ANIMATE RIG
phase("FASE 2: ANIMATE RIG (pose mode)")
print(
    run("""
import bpy, math
arm = bpy.data.objects.get("Character")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
for bone_name in ["UpperArm_L", "UpperArm_R", "Head"]:
    b = arm.pose.bones.get(bone_name)
    if b:
        b.rotation_mode = "XYZ"
        b.rotation_euler = (0,0,0); b.keyframe_insert("rotation_euler", frame=1)
        b.rotation_euler = (0,0,math.radians(45)); b.keyframe_insert("rotation_euler", frame=30)
        b.rotation_euler = (0,0,math.radians(-30)); b.keyframe_insert("rotation_euler", frame=60)
        b.rotation_euler = (0,0,0); b.keyframe_insert("rotation_euler", frame=90)
bpy.ops.object.mode_set(mode="OBJECT")
print("Animated: UpperArm_L, UpperArm_R, Head")
""").get("output", "")
)

# FASE 3: ARRAY MODIFIERS
phase("FASE 3: ARRAY MODIFIERS (3D Grid)")
print(
    run("""
import bpy
bpy.ops.mesh.primitive_cube_add(size=0.3, location=(10,0,0.15))
grid = bpy.context.active_object; grid.name = "Array3D"
m1 = grid.modifiers.new("X","ARRAY"); m1.count = 10; m1.relative_offset_displace = (1.5,0,0)
m2 = grid.modifiers.new("Y","ARRAY"); m2.count = 10; m2.relative_offset_displace = (0,1.5,0)
m3 = grid.modifiers.new("Z","ARRAY"); m3.count = 5; m3.relative_offset_displace = (0,0,1.5)
mat = bpy.data.materials.new("ArrayMat"); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2,0.6,1,1)
mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.6
grid.data.materials.append(mat)
print(f"Array3D: 10x10x5 = 500 cubes")
""").get("output", "")
)

# FASE 4: SUBDIVISION + SMOOTH
phase("FASE 4: SUBDIVISION SURFACES")
print(
    run("""
import bpy
# Monkey with subdivision
bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, -10, 2))
monkey = bpy.context.active_object; monkey.name = "Suzanne"
mod = monkey.modifiers.new("Subsurf", "SUBSURF")
mod.levels = 2; mod.render_levels = 3
mat = bpy.data.materials.new("MonkeyMat"); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8,0.4,0.1,1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.3
monkey.data.materials.append(mat)
# Sphere with smooth
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1.5, location=(0,-10,5))
smooth = bpy.context.active_object; smooth.name = "SmoothSphere"
smooth.modifiers.new("Subsurf2", "SUBSURF").levels = 1
mat2 = bpy.data.materials.new("SmoothMat"); mat2.use_nodes = True
mat2.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1,0.9,0.4,1)
mat2.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.8
mat2.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.1
smooth.data.materials.append(mat2)
print("Suzanne (subsurf 2) + SmoothSphere (64 seg)")
""").get("output", "")
)

# FASE 5: MULTIPLE CURVES
phase("FASE 5: CURVES + BEZIER")
print(
    run("""
import bpy, math
# Create bezier circle
bpy.ops.curve.primitive_bezier_circle_add(radius=4, location=(0,12,1))
curve_obj = bpy.context.active_object; curve_obj.name = "BezierCircle"
curve = curve_obj.data; curve.bevel_depth = 0.1; curve.bevel_resolution = 12
mat = bpy.data.materials.new("CurveMat"); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1,0.3,0.6,1)
mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.5
curve_obj.data.materials.append(mat)
# Create spiral with Array + Curve modifier
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1, location=(4,12,0))
spiral = bpy.context.active_object; spiral.name = "SpiralTube"
spiral.modifiers.new("SpiralArray","ARRAY").count = 50
spiral.modifiers["SpiralArray"].use_relative_offset = False
spiral.modifiers["SpiralArray"].use_constant_offset = True
spiral.modifiers["SpiralArray"].constant_offset_displace = (0, 0, 0.15)
mat2 = bpy.data.materials.new("SpiralMat"); mat2.use_nodes = True
mat2.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5,0.1,0.9,1)
spiral.data.materials.append(mat2)
print(f"BezierCircle (bevel 0.1) + SpiralTube (50 segments)")
""").get("output", "")
)

# FASE 6: BOOLEAN OPERATIONS
phase("FASE 6: BOOLEAN OPERATIONS")
print(
    run("""
import bpy
# Base cube
bpy.ops.mesh.primitive_cube_add(size=3, location=(-10, 0, 1.5))
base = bpy.context.active_object; base.name = "BooleanBase"
# Sphere to subtract
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(-10, 0, 1.5))
cutter = bpy.context.active_object; cutter.name = "BooleanCutter"
# Add boolean modifier
mod = base.modifiers.new("Cut", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = cutter
cutter.hide_viewport = True
# Cylinder to intersect
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=3, location=(-8, 0, 1.5))
intersect = bpy.context.active_object; intersect.name = "BooleanIntersect"
# Apply intersection with another sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(-8, 0, 1.5))
cutter2 = bpy.context.active_object; cutter2.name = "BoolCut2"
mod2 = intersect.modifiers.new("Intersect", "BOOLEAN")
mod2.operation = "INTERSECT"
mod2.object = cutter2
cutter2.hide_viewport = True
mat = bpy.data.materials.new("BoolMat"); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.7,0.2,0.2,1)
base.data.materials.append(mat)
intersect.data.materials.append(mat)
print("Boolean: DIFFERENCE + INTERSECT")
""").get("output", "")
)

# RESUMEN
phase("RESUMEN STRESS TEST 2")
print(
    run("""
import bpy
s = bpy.context.scene
types = {}
for o in s.objects: types[o.type] = types.get(o.type,0)+1
print(f"Total objects: {len(s.objects)}")
for t,c in sorted(types.items()): print(f"  {t}: {c}")
print(f"Materials: {len(bpy.data.materials)}")
print(f"Meshes: {len(bpy.data.meshes)}")
print(f"Armatures: {len(bpy.data.armatures)}")
print(f"Curves: {len(bpy.data.curves)}")
print(f"Frames: {s.frame_start}-{s.frame_end} @ {s.render.fps}fps")
""").get("output", "")
)

print("\n" + "=" * 60)
print("STRESS TEST 2 COMPLETADO")
print("=" * 60)
