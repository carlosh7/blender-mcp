#!/usr/bin/env python3
"""
Ejemplo 2: Animación de objetos
Requiere: Blender abierto con addon MCP activo
"""
import socket
import json
import time


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
                if b'\n' in r:
                    break
        except socket.timeout:
            continue
    s.close()
    data = json.loads(r.decode().strip())
    return data.get('result', data)


# Configurar escena de animación
print("Configurando animación...")
run('''
import bpy, math

# Limpiar
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 120
scene.render.fps = 24

# Crear cubo
bpy.ops.mesh.primitive_cube_add(size=1.5, location=(-4, 0, 1))
cube = bpy.context.active_object
cube.name = "CuboAnimado"
mat = bpy.data.materials.new("AnimRojo")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.1, 0.1, 1)
cube.data.materials.append(mat)

# Keyframes: salto lateral
cube.location = (-4, 0, 1)
cube.keyframe_insert("location", frame=1)

cube.location = (0, 0, 4)
cube.keyframe_insert("location", frame=30)

cube.location = (4, 0, 1)
cube.keyframe_insert("location", frame=60)

cube.location = (0, 0, 4)
cube.keyframe_insert("location", frame=90)

cube.location = (-4, 0, 1)
cube.keyframe_insert("location", frame=120)

# Crear esfera
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, -4, 1))
sphere = bpy.context.active_object
sphere.name = "EsferaRotante"
mat2 = bpy.data.materials.new("AnimAzul")
mat2.use_nodes = True
mat2.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.3, 0.9, 1)
mat2.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.8
sphere.data.materials.append(mat2)

# Rotación continua
sphere.rotation_euler = (0, 0, 0)
sphere.keyframe_insert("rotation_euler", frame=1)

sphere.rotation_euler = (0, 0, math.radians(360))
sphere.keyframe_insert("rotation_euler", frame=120)

# Suelo
bpy.ops.mesh.primitive_plane_add(size=20)
plane = bpy.context.active_object
mat3 = bpy.data.materials.new("Suelo")
mat3.use_nodes = True
mat3.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.25, 0.25, 1)
plane.data.materials.append(mat3)

print("Animación creada: 120 frames")
print("  - Cubo: salto lateral (4 puntos)")
print("  - Esfera: rotación 360°")
''')

# Luces
print("Agregando luces...")
run('''
import bpy
bpy.ops.object.light_add(type="AREA", location=(5, -5, 8))
bpy.context.active_object.data.energy = 500
bpy.ops.object.light_add(type="AREA", location=(-5, -3, 6))
bpy.context.active_object.data.energy = 200
bpy.ops.object.light_add(type="AREA", location=(0, 6, 7))
bpy.context.active_object.data.energy = 300
print("Luces creadas")
''')

print("\nAnimación lista!")
print("En Blender: presiona Alt+A o el botón Play para ver la animación")
print("Usa la timeline (Ctrl+Shift+Alt+F) para ver los keyframes")
