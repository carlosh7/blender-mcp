#!/usr/bin/env python3
"""blender-mcp — STRESS TEST 3: Escena Completa + Render"""
import socket, json, time, math


def run(code):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect(('localhost', 9876))
    s.send(json.dumps({'command': 'execute_code', 'params': {'code': code}}).encode() + b'\n')
    r = b''
    dl = time.time() + 25
    while time.time() < dl:
        try:
            c = s.recv(65536)
            if c:
                r += c
                if b'\n' in r: break
        except: continue
    s.close()
    data = json.loads(r.decode().strip())
    return data.get('result', data)


def phase(name):
    print(f"\n{'='*60}\n{name}\n{'='*60}")


# FASE 1: CLEAN
phase("FASE 1: CLEAN")
print(run('''
import bpy
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
for m in bpy.data.materials: bpy.data.materials.remove(m)
for mesh in bpy.data.meshes: bpy.data.meshes.remove(m)
for curve in bpy.data.curves: bpy.data.curves.remove(curve)
s = bpy.context.scene; s.frame_start=1; s.frame_end=120; s.render.fps=24
s.render.engine = "BLENDER_EEVEE_NEXT"
print("Clean: 120 frames, EEVEE_NEXT")
''').get('output',''))

# FASE 2: MATERIALS LIBRARY
phase("FASE 2: MATERIALS LIBRARY (20 materiales)")
print(run('''
import bpy
materials_config = [
    ("Red_Metal", (0.8,0.05,0.05,1), 0.9, 0.1),
    ("Blue_Glass", (0.1,0.2,0.8,1), 0.0, 0.0),
    ("Green_Glow", (0.1,0.8,0.2,1), 0.0, 0.5),
    ("Gold", (1.0,0.8,0.0,1), 1.0, 0.15),
    ("Silver", (0.9,0.9,0.9,1), 1.0, 0.05),
    ("Copper", (0.7,0.4,0.2,1), 0.8, 0.25),
    ("Plastic_Red", (0.9,0.1,0.1,1), 0.0, 0.4),
    ("Plastic_Blue", (0.1,0.1,0.9,1), 0.0, 0.4),
    ("Plastic_Green", (0.1,0.7,0.1,1), 0.0, 0.4),
    ("Wood", (0.4,0.25,0.1,1), 0.0, 0.7),
    ("Marble", (0.85,0.83,0.8,1), 0.0, 0.15),
    ("Rubber", (0.1,0.1,0.1,1), 0.0, 0.9),
    ("Neon_Pink", (1.0,0.2,0.6,1), 0.0, 0.1),
    ("Neon_Cyan", (0.0,1.0,1.0,1), 0.0, 0.1),
    ("Neon_Yellow", (1.0,1.0,0.0,1), 0.0, 0.1),
    ("Carbon_Fiber", (0.15,0.15,0.15,1), 0.3, 0.2),
    ("Chrome_Blue", (0.4,0.6,1.0,1), 1.0, 0.02),
    ("Chrome_Red", (1.0,0.3,0.3,1), 1.0, 0.02),
    ("Obsidian", (0.02,0.02,0.03,1), 0.1, 0.05),
    ("Pearl", (0.9,0.85,0.8,1), 0.2, 0.1),
]
for name, color, metal, rough in materials_config:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
print(f"Created {len(materials_config)} materials")
''').get('output',''))

# FASE 3: OBJECT ZOO (every primitive type)
phase("FASE 3: OBJECT ZOO (every primitive)")
print(run('''
import bpy
prims = [
    ("Cube", "primitive_cube_add", {"size":1.5}, (-8,0,1)),
    ("Sphere", "primitive_uv_sphere_add", {"radius":0.8}, (-6,0,1)),
    ("IcoSphere", "primitive_ico_sphere_add", {"radius":0.8, "subdivisions":3}, (-4,0,1)),
    ("Cylinder", "primitive_cylinder_add", {"radius":0.5, "depth":2}, (-2,0,1)),
    ("Cone", "primitive_cone_add", {"radius1":0.7, "radius2":0, "depth":1.5}, (0,0,1)),
    ("Torus", "primitive_torus_add", {"major_radius":0.6, "minor_radius":0.2}, (2,0,1)),
    ("Plane", "primitive_plane_add", {"size":1.5}, (4,0,0.5)),
    ("Monkey", "primitive_monkey_add", {"size":1.2}, (6,0,1.5)),
    ("Circle", "primitive_circle_add", {"radius":0.7}, (8,0,0.5)),
]
for name, prim, kwargs, loc in prims:
    getattr(bpy.ops.mesh, prim)(**kwargs, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    mat_idx = hash(name) % 20
    mat = bpy.data.materials[mat_idx]
    obj.data.materials.append(mat)
    print(f"  {name} -> {mat.name}")
print(f"Created {len(prims)} primitives")
''').get('output',''))

# FASE 4: PARTICLE-LIKE SCATTER (multiple GeoNodes)
phase("FASE 4: MULTIPLE SCATTER SYSTEMS")
print(run('''
import bpy
# Scatter 1: grass-like
bpy.ops.mesh.primitive_plane_add(size=8, location=(-8,8,0))
g1 = bpy.context.active_object; g1.name = "GrassScatter"
mod1 = g1.modifiers.new("Grass","NODES")
ng1 = bpy.data.node_groups.new("GrassGN","GeometryNodeTree")
mod1.node_group = ng1
n1 = ng1.nodes; l1 = ng1.links
inp1 = n1.new("NodeGroupInput"); inp1.location=(-400,0)
out1 = n1.new("NodeGroupOutput"); out1.location=(400,0)
dist1 = n1.new("GeometryNodeDistributePointsOnFaces"); dist1.location=(-100,0)
dist1.inputs["Density"].default_value = 50.0
inst1 = n1.new("GeometryNodeInstanceOnPoints"); inst1.location=(100,0)
bpy.ops.mesh.primitive_cone_add(radius1=0.02, radius2=0, depth=0.3)
iso1 = bpy.context.active_object; iso1.hide_viewport=True; iso1.name = "Blade"
oi1 = n1.new("GeometryNodeObjectInfo"); oi1.location=(-100,-200)
oi1.inputs["Object"].default_value = iso1
l1.new(inp1.outputs[0], dist1.inputs["Mesh"])
l1.new(dist1.outputs["Points"], inst1.inputs["Points"])
l1.new(oi1.outputs["Geometry"], inst1.inputs["Instance"])
l1.new(inst1.outputs["Instances"], out1.inputs[0])
mat_g = bpy.data.materials.new("Grass"); mat_g.use_nodes = True
mat_g.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.2,0.6,0.1,1)
iso1.data.materials.append(mat_g)

# Scatter 2: rocks
bpy.ops.mesh.primitive_plane_add(size=6, location=(8,8,0))
g2 = bpy.context.active_object; g2.name = "RockScatter"
mod2 = g2.modifiers.new("Rocks","NODES")
ng2 = bpy.data.node_groups.new("RockGN","GeometryNodeTree")
mod2.node_group = ng2
n2 = ng2.nodes; l2 = ng2.links
inp2 = n2.new("NodeGroupInput"); inp2.location=(-400,0)
out2 = n2.new("NodeGroupOutput"); out2.location=(400,0)
dist2 = n2.new("GeometryNodeDistributePointsOnFaces"); dist2.location=(-100,0)
dist2.inputs["Density"].default_value = 20.0
inst2 = n2.new("GeometryNodeInstanceOnPoints"); inst2.location=(100,0)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, subdivisions=1)
iso2 = bpy.context.active_object; iso2.hide_viewport=True; iso2.name = "Rock"
oi2 = n2.new("GeometryNodeObjectInfo"); oi2.location=(-100,-200)
oi2.inputs["Object"].default_value = iso2
l2.new(inp2.outputs[0], dist2.inputs["Mesh"])
l2.new(dist2.outputs["Points"], inst2.inputs["Points"])
l2.new(oi2.outputs["Geometry"], inst2.inputs["Instance"])
l2.new(inst2.outputs["Instances"], out2.inputs[0])
mat_r = bpy.data.materials.new("Rock"); mat_r.use_nodes = True
mat_r.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.4,0.35,0.3,1)
iso2.data.materials.append(mat_r)
print("2 scatter systems: Grass (50 pts/m2) + Rocks (20 pts/m2)")
''').get('output',''))

# FASE 5: ANIMATION
phase("FASE 5: COMPLEX ANIMATION")
print(run('''
import bpy, math
# Animate every primitive
for i, name in enumerate(["Cube","Sphere","IcoSphere","Cylinder","Cone","Torus","Plane","Monkey","Circle"]):
    obj = bpy.data.objects.get(name)
    if obj:
        for f in range(1, 121, 5):
            t = f/120
            obj.location.y = math.sin(t*math.pi*4 + i*0.7)*2
            obj.rotation_euler.z = t*math.pi*2
            obj.keyframe_insert("location", frame=f)
            obj.keyframe_insert("rotation_euler", frame=f)
print("Animated 9 primitives: sine wave + rotation")
''').get('output',''))

# FASE 6: LIGHTS
phase("FASE 6: LIGHTING RIG")
print(run('''
import bpy
bpy.ops.object.light_add(type="AREA", location=(10,-10,12))
bpy.context.active_object.data.energy = 1000; bpy.context.active_object.data.size = 8
bpy.context.active_object.name = "KeyMain"
bpy.ops.object.light_add(type="AREA", location=(-10,-8,10))
bpy.context.active_object.data.energy = 400; bpy.context.active_object.data.size = 6
bpy.context.active_object.name = "FillMain"
bpy.ops.object.light_add(type="AREA", location=(0,10,10))
bpy.context.active_object.data.energy = 500
bpy.context.active_object.name = "RimMain"
bpy.ops.object.light_add(type="SUN", location=(5,5,20))
bpy.context.active_object.data.energy = 3
bpy.ops.object.light_add(type="POINT", location=(0,0,8))
bpy.context.active_object.data.energy = 200; bpy.context.active_object.data.color = (1,0.8,0.6)
bpy.context.active_object.name = "WarmFill"
print("5 lights: Key + Fill + Rim + Sun + WarmFill")
''').get('output',''))

# FASE 7: CAMERA
phase("FASE 7: CAMERA + RENDER SETTINGS")
print(run('''
import bpy
bpy.ops.object.camera_add(location=(18,-15,12))
cam = bpy.context.active_object; cam.name = "FinalCam"
cam.rotation_euler = (1.05, 0, 0.65)
bpy.context.scene.camera = cam
s = bpy.context.scene
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.resolution_percentage = 100
s.render.engine = "BLENDER_EEVEE_NEXT"
s.eevee.taa_render_samples = 64
print(f"Camera: 1920x1080, EEVEE_NEXT, 64 samples")
''').get('output',''))

# FASE 8: SAVE
phase("FASE 8: SAVE")
print(run('''
import bpy
bpy.ops.wm.save_as_mainfile(filepath="/tmp/stress_test_scene.blend")
print("Saved: /tmp/stress_test_scene.blend")
''').get('output',''))

# RESUMEN FINAL
phase("RESUMEN FINAL")
print(run('''
import bpy
s = bpy.context.scene
types = {}
for o in s.objects: types[o.type] = types.get(o.type,0)+1
total = len(s.objects)
print(f"TOTAL OBJECTS: {total}")
for t,c in sorted(types.items()): print(f"  {t}: {c}")
print(f"Materials: {len(bpy.data.materials)}")
print(f"Meshes: {len(bpy.data.meshes)}")
print(f"Node Groups: {len(bpy.data.node_groups)}")
print(f"Frames: {s.frame_start}-{s.frame_end} @ {s.render.fps}fps")
print(f"Render: {s.render.engine} {s.render.resolution_x}x{s.render.resolution_y}")
''').get('output',''))

print("\n" + "="*60)
print("STRESS TEST 3 COMPLETADO - ESCENA LISTA PARA RENDER")
print("="*60)
