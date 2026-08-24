#!/usr/bin/env python3
"""
Ejemplo 3: Shader Nodes y Geometry Nodes
Requiere: Blender abierto con addon MCP activo
"""

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
        except TimeoutError:
            continue
    s.close()
    data = json.loads(r.decode().strip())
    return data.get("result", data)


# 1. Material Ladrillo Procedural
print("1. Creando material ladrillo...")
run("""
import bpy

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, -5, 1))
wall = bpy.context.active_object
wall.name = "ParedLadrillo"

mat = bpy.data.materials.new("Ladrillo")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

for n in nodes:
    nodes.remove(n)

output = nodes.new("ShaderNodeOutputMaterial")
output.location = (600, 0)

bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (300, 0)

brick = nodes.new("ShaderNodeTexBrick")
brick.location = (-200, 100)

links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

wall.data.materials.append(mat)
print(f"Material ladrillo: {mat.name}")
""")

# 2. Material Vidrio
print("2. Creando material vidrio...")
run("""
import bpy

bpy.ops.mesh.primitive_ico_sphere_add(radius=1, subdivisions=4, location=(3, -5, 1))
glass = bpy.context.active_object
glass.name = "Vidrio"

mat = bpy.data.materials.new("Vidrio")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.95, 1.0, 1)
bsdf.inputs["Roughness"].default_value = 0.0
bsdf.inputs["IOR"].default_value = 1.45
bsdf.inputs["Alpha"].default_value = 0.3

glass.data.materials.append(mat)
print(f"Material vidrio: {mat.name}")
""")

# 3. Geometry Nodes: Scatter
print("3. Creando scatter con Geometry Nodes...")
run("""
import bpy

bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 5, 0))
scatter = bpy.context.active_object
scatter.name = "ScatterPlane"

mod = scatter.modifiers.new("Scatter", "NODES")
ng = bpy.data.node_groups.new("ScatterGN", "GeometryNodeTree")
mod.node_group = ng

nodes = ng.nodes
links = ng.links

inp = nodes.new("NodeGroupInput")
inp.location = (-400, 0)

out = nodes.new("NodeGroupOutput")
out.location = (400, 0)

dist = nodes.new("GeometryNodeDistributePointsOnFaces")
dist.location = (-100, 0)
dist.inputs["Density"].default_value = 10.0

inst = nodes.new("GeometryNodeInstanceOnPoints")
inst.location = (100, 0)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1)
iso = bpy.context.active_object
iso.hide_viewport = True
iso.name = "InstanceDot"

oi = nodes.new("GeometryNodeObjectInfo")
oi.location = (-100, -200)
oi.inputs["Object"].default_value = iso

links.new(inp.outputs[0], dist.inputs["Mesh"])
links.new(dist.outputs["Points"], inst.inputs["Points"])
links.new(oi.outputs["Geometry"], inst.inputs["Instance"])
links.new(inst.outputs["Instances"], out.inputs[0])

# Material para instancias
mat = bpy.data.materials.new("DotMat")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.8, 0.3, 1)
iso.data.materials.append(mat)

print(f"GeoNodes: {ng.name}")
""")

# 4. Array Modifier
print("4. Creando grid con Array...")
run("""
import bpy

bpy.ops.mesh.primitive_cube_add(size=0.4, location=(8, 0, 0.2))
arr = bpy.context.active_object
arr.name = "GridCubos"

m1 = arr.modifiers.new("X", "ARRAY")
m1.count = 8
m1.relative_offset_displace = (1.8, 0, 0)

m2 = arr.modifiers.new("Y", "ARRAY")
m2.count = 5
m2.relative_offset_displace = (0, 1.8, 0)

mat = bpy.data.materials.new("GridMat")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.6, 0.0, 1)
arr.data.materials.append(mat)

print(f"Grid: 8x5 = 40 cubos")
""")

# 5. Luces y cámara
print("5. Configurando luces y cámara...")
run("""
import bpy

# Luces
bpy.ops.object.light_add(type="AREA", location=(5, -5, 8))
bpy.context.active_object.data.energy = 500
bpy.ops.object.light_add(type="AREA", location=(-5, -3, 6))
bpy.context.active_object.data.energy = 200
bpy.ops.object.light_add(type="AREA", location=(0, 6, 7))
bpy.context.active_object.data.energy = 300

# Cámara
bpy.ops.object.camera_add(location=(12, -10, 8))
cam = bpy.context.active_object
cam.name = "MainCamera"
cam.rotation_euler = (1.1, 0, 0.8)
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

print("Luces y cámara configuradas")
""")

print("\nEscena avanzada creada!")
print("Materiales: Ladrillo, Vidrio")
print("GeoNodes: Scatter con 10 puntos/m²")
print("Modifiers: Grid 8x5 = 40 cubos")
print("Cámara: 1920x1080")
