#!/usr/bin/env python3
"""blender-mcp — Pool Table V2 (step by step)"""
import socket
import json
import time

def send(code, label=""):
    """Send code to Blender and wait for response."""
    if label:
        print(f"  [{label}]...", end=" ", flush=True)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(45)
    s.connect(('localhost', 9876))
    s.send(json.dumps({'command': 'execute_code', 'params': {'code': code}}).encode() + b'\n')
    
    r = b''
    deadline = time.time() + 40
    while time.time() < deadline:
        try:
            c = s.recv(65536)
            if c:
                r += c
                if b'\n' in r:
                    break
        except:
            continue
    s.close()
    
    data = json.loads(r.decode().strip())
    result = data.get('result', {})
    output = result.get('output', str(result))
    
    if label:
        # Extract just the last line
        lines = output.strip().split('\n')
        print(lines[-1] if lines else "OK")
    
    return result

print("=" * 60)
print("POOL TABLE V2 - Step by Step")
print("=" * 60)

# Step 1: Clean
print("\n1. Cleaning scene...")
send('''
import bpy
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
for m in bpy.data.materials: bpy.data.materials.remove(m)
for c in bpy.data.collections: bpy.data.collections.remove(c)
print("Scene cleaned")
''', "clean")

# Step 2: Materials
print("\n2. Creating materials...")
send('''
import bpy

def mat(name, color, rough=0.15, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes=True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal

mat("Wood_Dark", (0.25, 0.15, 0.08), 0.6)
mat("Wood_Light", (0.5, 0.35, 0.2), 0.5)
mat("Felt_Green", (0.05, 0.35, 0.1), 0.9)
mat("Rubber_Black", (0.02, 0.02, 0.02), 0.95)
mat("Floor_Wood", (0.45, 0.3, 0.18), 0.5)
mat("Wall_Cream", (0.85, 0.82, 0.75), 0.5)

ball_colors = [
    (0.95, 0.95, 0.9), (0.9, 0.8, 0.1), (0.05, 0.15, 0.8), (0.8, 0.05, 0.05),
    (0.5, 0.05, 0.5), (0.9, 0.4, 0.05), (0.05, 0.6, 0.1), (0.4, 0.05, 0.05),
    (0.02, 0.02, 0.02), (0.9, 0.8, 0.1), (0.05, 0.15, 0.8), (0.8, 0.05, 0.05),
    (0.5, 0.05, 0.5), (0.9, 0.4, 0.05), (0.05, 0.6, 0.1), (0.4, 0.05, 0.05),
]
for i, c in enumerate(ball_colors):
    mat(f"Ball_{i}", c, 0.15)

print(f"Created {len(ball_colors) + 6} materials")
''', "materials")

# Step 3: Room
print("\n3. Creating room...")
send('''
import bpy, math

# Floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.data.materials.append(bpy.data.materials["Floor_Wood"])

# Back wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 5, 1.5))
wall = bpy.context.active_object
wall.rotation_euler = (math.pi/2, 0, 0)
wall.data.materials.append(bpy.data.materials["Wall_Cream"])

# Left wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(-5, 0, 1.5))
wall2 = bpy.context.active_object
wall2.rotation_euler = (0, math.pi/2, 0)
wall2.data.materials.append(bpy.data.materials["Wall_Cream"])

print("Room: floor + 2 walls")
''', "room")

# Step 4: Table structure
print("\n4. Creating table structure...")
send('''
import bpy

mat = bpy.data.materials["Wood_Dark"]

# Legs (4)
for i, (x, y) in enumerate([(-1.27, -0.58), (1.27, -0.58), (-1.27, 0.58), (1.27, 0.58)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.75, location=(x, y, 0.375))
    bpy.context.active_object.data.materials.append(mat)

# Beams (5)
for n, l, s in [("F", (0, -0.55, 0.38), (1.22, 0.04, 0.04)),
                ("B", (0, 0.55, 0.38), (1.22, 0.04, 0.04)),
                ("L", (-1.20, 0, 0.38), (0.04, 0.56, 0.04)),
                ("R", (1.20, 0, 0.38), (0.04, 0.56, 0.04)),
                ("C", (0, 0, 0.38), (1.22, 0.03, 0.03))]:
    bpy.ops.mesh.primitive_cube_add(location=l)
    o = bpy.context.active_object
    o.scale = s
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    o.data.materials.append(mat)

print("Table: 4 legs + 5 beams")
''', "structure")

# Step 5: Felt + Frame + Pockets
print("\n5. Creating felt, frame, pockets...")
send('''
import bpy

# Felt (CORRECT: 2.54m x 1.22m)
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0.76))
felt = bpy.context.active_object
felt.name = "Felt"
felt.scale = (2.54, 1.22, 1)
bpy.ops.object.transform_apply(rotation=False, scale=True)
felt.data.materials.append(bpy.data.materials["Felt_Green"])

# Frame
mat = bpy.data.materials["Wood_Dark"]
for n, l, s in [("F", (0, -0.68, 0.80), (1.42, 0.06, 0.04)),
                ("B", (0, 0.68, 0.80), (1.42, 0.06, 0.04)),
                ("L", (-1.37, 0, 0.80), (0.06, 0.66, 0.04)),
                ("R", (1.37, 0, 0.80), (0.06, 0.66, 0.04))]:
    bpy.ops.mesh.primitive_cube_add(location=l)
    o = bpy.context.active_object
    o.scale = s
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    o.data.materials.append(mat)

# Pockets
rmat = bpy.data.materials["Rubber_Black"]
for i, (x, y, r) in enumerate([(-1.22, -0.56, 0.065), (1.22, -0.56, 0.065),
                                (-1.22, 0.56, 0.065), (1.22, 0.56, 0.065),
                                (0, -0.61, 0.055), (0, 0.61, 0.055)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=0.02, location=(x, y, 0.78))
    bpy.context.active_object.data.materials.append(rmat)

# Rails
lmat = bpy.data.materials["Wood_Light"]
for l, s in [((-0.61, -0.57, 0.79), (0.58, 0.03, 0.015)),
             ((0.61, -0.57, 0.79), (0.58, 0.03, 0.015)),
             ((-0.61, 0.57, 0.79), (0.58, 0.03, 0.015)),
             ((0.61, 0.57, 0.79), (0.58, 0.03, 0.015)),
             ((-1.23, 0.28, 0.79), (0.03, 0.24, 0.015)),
             ((-1.23, -0.28, 0.79), (0.03, 0.24, 0.015)),
             ((1.23, 0.28, 0.79), (0.03, 0.24, 0.015)),
             ((1.23, -0.28, 0.79), (0.03, 0.24, 0.015))]:
    bpy.ops.mesh.primitive_cube_add(location=l)
    o = bpy.context.active_object
    o.scale = s
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    o.data.materials.append(lmat)

print("Felt + frame + 6 pockets + 8 rails")
''', "surface")

# Step 6: Balls
print("\n6. Creating balls...")
send('''
import bpy

ball_z = 0.786
ball_r = 0.026

# Cue ball
bpy.ops.mesh.primitive_uv_sphere_add(radius=ball_r, location=(-0.7, 0, ball_z))
bpy.context.active_object.data.materials.append(bpy.data.materials["Ball_0"])

# Rack (triangle)
idx = 0
for row in range(5):
    for col in range(row + 1):
        x = 0.75 + row * 0.054 * 0.866
        y = (col - row / 2) * 0.054
        bpy.ops.mesh.primitive_uv_sphere_add(radius=ball_r, location=(x, y, ball_z))
        bpy.context.active_object.data.materials.append(bpy.data.materials[f"Ball_{idx + 1}"])
        idx += 1

print("16 balls (1 cue + 15 rack)")
''', "balls")

# Step 7: Cue stick + lights + camera
print("\n7. Creating cue, lights, camera...")
send('''
import bpy, math

# Cue stick
bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=1.4, location=(-1.5, 0, 0.82))
stick = bpy.context.active_object
stick.rotation_euler = (0, 0, math.pi / 2)
stick.data.materials.append(bpy.data.materials["Wood_Light"])

# Lights
bpy.ops.object.light_add(type="AREA", location=(0, 0, 1.6))
bpy.context.active_object.data.energy = 500
bpy.context.active_object.data.size = 1.2

bpy.ops.object.light_add(type="AREA", location=(3, -2, 2.5))
bpy.context.active_object.data.energy = 150

bpy.ops.object.light_add(type="AREA", location=(-3, 2, 2.5))
bpy.context.active_object.data.energy = 150

# Camera
bpy.ops.object.camera_add(location=(3, -3.5, 2.2))
cam = bpy.context.active_object
cam.rotation_euler = (1.05, 0, 0.6)
bpy.context.scene.camera = cam

s = bpy.context.scene
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.engine = "BLENDER_EEVEE_NEXT"
s.eevee.taa_render_samples = 64

print("Cue + 3 lights + camera")
''', "accessories")

# Step 8: Save
print("\n8. Saving...")
send('''
import bpy
bpy.ops.wm.save_as_mainfile(filepath="/tmp/pool_table_v2.blend")
print("Saved: /tmp/pool_table_v2.blend")
''', "save")

# Summary
print("\n" + "=" * 60)
print("POOL TABLE V2 COMPLETE!")
print("=" * 60)
