#!/usr/bin/env python3
"""
Ejemplo 1: Crear escena básica con objetos y materiales
Requiere: Blender abierto con addon MCP activo en puerto 9876
"""

import json
import socket
import time


def run(code):
    """Ejecutar código en Blender via socket."""
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


# 1. Limpiar escena
print("1. Limpiando escena...")
run("""
import bpy
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
for m in bpy.data.materials:
    bpy.data.materials.remove(m)
print("Escena limpia")
""")

# 2. Crear cubo rojo
print("2. Creando cubo rojo...")
run("""
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(-3, 0, 1))
cube = bpy.context.active_object
cube.name = "CuboRojo"
mat = bpy.data.materials.new("Rojo")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.05, 0.05, 1)
bsdf.inputs["Metallic"].default_value = 0.3
bsdf.inputs["Roughness"].default_value = 0.4
cube.data.materials.append(mat)
print(f"Cubo: {cube.name}")
""")

# 3. Crear esfera azul
print("3. Creando esfera azul...")
run("""
import bpy
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.active_object
sphere.name = "EsferaAzul"
mat = bpy.data.materials.new("Azul")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.05, 0.15, 0.8, 1)
bsdf.inputs["Metallic"].default_value = 0.9
bsdf.inputs["Roughness"].default_value = 0.1
sphere.data.materials.append(mat)
print(f"Esfera: {sphere.name}")
""")

# 4. Crear cilindro verde
print("4. Creando cilindro verde...")
run("""
import bpy
bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=3, location=(3, 0, 1.5))
cyl = bpy.context.active_object
cyl.name = "CilindroVerde"
mat = bpy.data.materials.new("Verde")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.7, 0.2, 1)
cyl.data.materials.append(mat)
print(f"Cilindro: {cyl.name}")
""")

# 5. Crear suelo
print("5. Creando suelo...")
run("""
import bpy
bpy.ops.mesh.primitive_plane_add(size=20)
plane = bpy.context.active_object
plane.name = "Suelo"
mat = bpy.data.materials.new("SueloMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1)
plane.data.materials.append(mat)
print("Suelo creado")
""")

# 6. Agregar luces
print("6. Agregando luces 3-point...")
run("""
import bpy

# Key Light
bpy.ops.object.light_add(type="AREA", location=(5, -5, 8))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 500
key.data.size = 4

# Fill Light
bpy.ops.object.light_add(type="AREA", location=(-5, -3, 6))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 200

# Rim Light
bpy.ops.object.light_add(type="AREA", location=(0, 6, 7))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 300

print("3-Point Lighting creada")
""")

# 7. Resumen
print("\n=== RESUMEN ===")
result = run("""
import bpy
scene = bpy.context.scene
types = {}
for o in scene.objects:
    types[o.type] = types.get(o.type, 0) + 1
print(f"Objetos: {len(scene.objects)}")
for t, c in sorted(types.items()):
    print(f"  {t}: {c}")
print(f"Materiales: {len(bpy.data.materials)}")
""")

print(result.get("output", result))
print("\nEscena creada! Abre Blender para ver los resultados.")
