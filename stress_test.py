#!/usr/bin/env python3
"""blender-mcp — STRESS TEST: Escena Compleja 60+ objetos"""

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


# FASE 1: CLEAN
phase("FASE 1: CLEAN")
print(
    run("""
import bpy
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
for m in bpy.data.materials: bpy.data.materials.remove(m)
for mesh in bpy.data.meshes: bpy.data.meshes.remove(mesh)
s = bpy.context.scene; s.frame_start=1; s.frame_end=240; s.render.fps=30
print("Clean: 240 frames @ 30fps")
""").get("output", "")
)

# FASE 2: GRID 8x8
phase("FASE 2: GRID 8x8 = 64 CUBOS")
print(
    run("""
import bpy, math
colors = [
    (0.9,0.1,0.1,1),(0.1,0.8,0.1,1),(0.1,0.1,0.9,1),(0.9,0.9,0.1,1),
    (0.9,0.1,0.9,1),(0.1,0.9,0.9,1),(0.9,0.5,0.1,1),(0.5,0.1,0.9,1),
]
mats = []
for i, c in enumerate(colors):
    m = bpy.data.materials.new(f"C{i}")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = c
    m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.3+i*0.08
    mats.append(m)
for x in range(8):
    for y in range(8):
        bpy.ops.mesh.primitive_cube_add(size=0.6, location=(x*1.2-4.5, y*1.2-4.5, 0.3))
        o = bpy.context.active_object; o.name = f"T{x}_{y}"
        o.data.materials.append(mats[(x+y)%8])
        o.scale = (1,1,(0.5+0.5*math.sin(x*0.5)*math.cos(y*0.5))*2)
print("Grid: 64 tiles, 8 colors")
""").get("output", "")
)

# FASE 3: SPHERES
phase("FASE 3: SPECIAL SPHERES")
print(
    run("""
import bpy
# Glass
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(-6,6,1.5))
g = bpy.context.active_object; g.name = "Glass"
m = bpy.data.materials.new("Glass"); m.use_nodes = True
bsdf = m.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value=(0.8,0.95,1,1)
bsdf.inputs["Roughness"].default_value=0.0
bsdf.inputs["IOR"].default_value=1.45
bsdf.inputs["Alpha"].default_value=0.2
g.data.materials.append(m)
# Chrome
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(6,6,1.5))
c = bpy.context.active_object; c.name = "Chrome"
m2 = bpy.data.materials.new("Chrome"); m2.use_nodes = True
m2.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value=1.0
m2.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=0.05
c.data.materials.append(m2)
# Glow
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0,6,1.5))
gl = bpy.context.active_object; gl.name = "Glow"
m3 = bpy.data.materials.new("Emission"); m3.use_nodes = True
em = m3.node_tree.nodes.new("ShaderNodeEmission")
em.inputs["Color"].default_value=(0,1,0.5,1); em.inputs["Strength"].default_value=5
m3.node_tree.links.new(em.outputs["Emission"], m3.node_tree.nodes["Material Output"].inputs["Surface"])
gl.data.materials.append(m3)
print("Glass + Chrome + Glow spheres")
""").get("output", "")
)

# FASE 4: TORUS + PILLARS
phase("FASE 4: TORUS + 12 PILLARS")
print(
    run("""
import bpy, math
bpy.ops.mesh.primitive_torus_add(major_radius=3, minor_radius=0.3, location=(0,-6,1))
t = bpy.context.active_object; t.name = "Torus"
m = bpy.data.materials.new("TorusMat"); m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(1,0.6,0,1)
m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value=0.7
t.data.materials.append(m)
for i in range(12):
    a = (i/12)*math.pi*2
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1, location=(math.cos(a)*3, -6, math.sin(a)*3+1))
    p = bpy.context.active_object; p.name = f"P{i}"
    pm = bpy.data.materials.new(f"P{i}"); pm.use_nodes = True
    h = i/12
    pm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(
        math.sin(h*6.28)*0.5+0.5, math.sin((h+0.33)*6.28)*0.5+0.5, math.sin((h+0.66)*6.28)*0.5+0.5, 1)
    p.data.materials.append(pm)
print("Torus + 12 rainbow pillars")
""").get("output", "")
)

# FASE 5: ANIMATION
phase("FASE 5: ANIMATION (240 frames)")
print(
    run("""
import bpy, math
t = bpy.data.objects.get("Torus")
if t:
    for f in range(1, 241, 10):
        p = f/240
        t.rotation_euler = (p*math.pi*4, p*math.pi*2, 0)
        t.location.z = 1+math.sin(p*math.pi*6)*0.5
        t.keyframe_insert("rotation_euler", frame=f)
        t.keyframe_insert("location", frame=f)
print("Torus: rotation + oscillation")
gl = bpy.data.objects.get("Glow")
if gl:
    em = [n for n in gl.data.materials[0].node_tree.nodes if n.type=="EMISSION"][0]
    for f in range(1, 241, 15):
        p = f/240
        em.inputs["Strength"].default_value = 2+8*math.sin(p*math.pi*8)
        em.keyframe_insert("inputs[2].default_value", frame=f)
print("Glow: emission pulse")
""").get("output", "")
)

# FASE 6: LIGHTS + CAMERA
phase("FASE 6: LIGHTS + CAMERA")
print(
    run("""
import bpy
bpy.ops.object.light_add(type="AREA", location=(8,-8,10))
bpy.context.active_object.data.energy = 800; bpy.context.active_object.data.size = 6
bpy.ops.object.light_add(type="AREA", location=(-8,-5,8))
bpy.context.active_object.data.energy = 300
bpy.ops.object.light_add(type="AREA", location=(0,8,9))
bpy.context.active_object.data.energy = 400
bpy.ops.object.light_add(type="SUN", location=(0,0,15))
bpy.context.active_object.data.energy = 2
bpy.ops.object.camera_add(location=(15,-12,10))
cam = bpy.context.active_object; cam.name = "MainCam"
cam.rotation_euler = (1.0, 0, 0.7)
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
print("4 lights + camera 1920x1080")
""").get("output", "")
)

# FASE 7: GROUND + SCATTER
phase("FASE 7: GROUND + SCATTER")
print(
    run("""
import bpy
bpy.ops.mesh.primitive_plane_add(size=30, location=(0,2,0))
g = bpy.context.active_object; g.name = "Ground"
m = bpy.data.materials.new("GroundMat"); m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.15,0.15,0.15,1)
g.data.materials.append(m)
bpy.ops.mesh.primitive_plane_add(size=12, location=(0,10,0))
sp = bpy.context.active_object; sp.name = "ScatterPlane"
mod = sp.modifiers.new("Scatter","NODES")
ng = bpy.data.node_groups.new("ScatterGN","GeometryNodeTree")
mod.node_group = ng
nodes = ng.nodes; links = ng.links
inp = nodes.new("NodeGroupInput"); inp.location=(-400,0)
out = nodes.new("NodeGroupOutput"); out.location=(400,0)
dist = nodes.new("GeometryNodeDistributePointsOnFaces"); dist.location=(-100,0)
dist.inputs["Density"].default_value = 15.0
inst = nodes.new("GeometryNodeInstanceOnPoints"); inst.location=(100,0)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1)
iso = bpy.context.active_object; iso.hide_viewport=True; iso.name = "Dot"
oi = nodes.new("GeometryNodeObjectInfo"); oi.location=(-100,-200)
oi.inputs["Object"].default_value = iso
links.new(inp.outputs[0], dist.inputs["Mesh"])
links.new(dist.outputs["Points"], inst.inputs["Points"])
links.new(oi.outputs["Geometry"], inst.inputs["Instance"])
links.new(inst.outputs["Instances"], out.inputs[0])
print("Ground 30x30 + Scatter 15 pts/m2")
""").get("output", "")
)

# RESUMEN
phase("RESUMEN FINAL")
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
print(f"Node Groups: {len(bpy.data.node_groups)}")
print(f"Frames: {s.frame_start}-{s.frame_end} @ {s.render.fps}fps")
""").get("output", "")
)

print("\n" + "=" * 60)
print("STRESS TEST COMPLETADO")
print("=" * 60)
