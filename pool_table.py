#!/usr/bin/env python3
"""blender-mcp — Mesa de Billar (Test del sistema completo)"""
import socket, json, time, math

def send(code):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect(('localhost', 9876))
    s.send(json.dumps({'command':'execute_code','params':{'code':code}}).encode()+b'\n')
    r=b''; dl=time.time()+25
    while time.time()<dl:
        try:
            c=s.recv(65536)
            if c: r+=c
            if b'\n' in r: break
        except: continue
    s.close()
    data = json.loads(r.decode().strip())
    return data.get('result',{})

def phase(name):
    print(f"\n{'='*60}\n{name}\n{'='*60}")

# =============================================
# LIMPIAR ESCENA
# =============================================
phase("LIMPIAR ESCENA")
print(send('''
import bpy
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
for m in bpy.data.materials: bpy.data.materials.remove(m)
for mesh in bpy.data.meshes: bpy.data.meshes.remove(m)
print("Escena limpia")
''').get('output',''))

# =============================================
# CREAR COLECCIONES
# =============================================
phase("CREAR COLECCIONES")
print(send('''
import bpy

# Crear colecciones
cols = ["PoolTable", "Balls", "Accessories", "Room"]
for name in cols:
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)

# Mover default collection
for obj in bpy.context.scene.collection.objects:
    for col in obj.users_collection:
        col.objects.unlink(obj)
    bpy.data.collections["PoolTable"].objects.link(obj)

print(f"Colecciones creadas: {cols}")
''').get('output',''))

# =============================================
# MATERIALES
# =============================================
phase("CREAR MATERIALES")
print(send('''
import bpy

materials = {
    "Wood_Dark": {"color": (0.25, 0.15, 0.08), "roughness": 0.6, "metallic": 0.0},
    "Wood_Light": {"color": (0.45, 0.3, 0.15), "roughness": 0.5, "metallic": 0.0},
    "Felt_Green": {"color": (0.05, 0.35, 0.1), "roughness": 0.9, "metallic": 0.0},
    "Rubber_Black": {"color": (0.02, 0.02, 0.02), "roughness": 0.95, "metallic": 0.0},
    "Metal_Chrome": {"color": (0.9, 0.9, 0.9), "roughness": 0.1, "metallic": 1.0},
    "Ball_White": {"color": (0.95, 0.95, 0.9), "roughness": 0.15, "metallic": 0.0},
    "Ball_Red": {"color": (0.8, 0.05, 0.05), "roughness": 0.15, "metallic": 0.0},
    "Ball_Blue": {"color": (0.05, 0.15, 0.8), "roughness": 0.15, "metallic": 0.0},
    "Ball_Yellow": {"color": (0.9, 0.8, 0.1), "roughness": 0.15, "metallic": 0.0},
    "Ball_Green": {"color": (0.05, 0.6, 0.1), "roughness": 0.15, "metallic": 0.0},
    "Ball_Purple": {"color": (0.5, 0.05, 0.5), "roughness": 0.15, "metallic": 0.0},
    "Ball_Orange": {"color": (0.9, 0.4, 0.05), "roughness": 0.15, "metallic": 0.0},
    "Ball_Maroon": {"color": (0.4, 0.05, 0.05), "roughness": 0.15, "metallic": 0.0},
    "Cue_Wood": {"color": (0.6, 0.4, 0.2), "roughness": 0.4, "metallic": 0.0},
}

for name, props in materials.items():
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*props["color"], 1)
    bsdf.inputs["Roughness"].default_value = props["roughness"]
    bsdf.inputs["Metallic"].default_value = props["metallic"]

print(f"Materiales creados: {len(materials)}")
''').get('output',''))

# =============================================
# DIMENSIONES ESTÁNDAR MESA DE BILLAR
# =============================================
# Estándar torneo: 9 pies (2.74m x 1.37m)
# Altura: 0.80m
# Bolsillos: 6 (4 esquinas + 2 laterales)
# =============================================

phase("CREAR BASE (PIES + ESTRUCTURA)")
print(send('''
import bpy

# === PIES DE LA MESA (4) ===
leg_positions = [
    (-1.27, -0.58, 0),   # Front-Left
    (1.27, -0.58, 0),    # Front-Right
    (-1.27, 0.58, 0),    # Back-Left
    (1.27, 0.58, 0),     # Back-Right
]

for i, (x, y, z) in enumerate(leg_positions):
    # Pata principal (cilindro)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.06,
        depth=0.75,
        location=(x, y, 0.375)
    )
    leg = bpy.context.active_object
    leg.name = f"Leg_{i+1}"
    mat = bpy.data.materials["Wood_Dark"]
    leg.data.materials.append(mat)
    
    # Mover a colección
    for col in leg.users_collection:
        col.objects.unlink(leg)
    bpy.data.collections["PoolTable"].objects.link(leg)

    # Pie (cilindro achatado)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.09,
        depth=0.03,
        location=(x, y, 0.015)
    )
    foot = bpy.context.active_object
    foot.name = f"Foot_{i+1}"
    foot.data.materials.append(mat)
    for col in foot.users_collection:
        col.objects.unlink(foot)
    bpy.data.collections["PoolTable"].objects.link(foot)

print("4 patas + 4 pies creados")
''').get('output',''))

phase("CREAR ESTRUCTURA INFERIOR")
print(send('''
import bpy

mat = bpy.data.materials["Wood_Dark"]

# Viga frontal
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.58, 0.35))
front = bpy.context.active_object
front.name = "Beam_Front"
front.scale = (1.33, 0.05, 0.05)
bpy.ops.object.transform_apply(rotation=False, scale=True)
front.data.materials.append(mat)
for col in front.users_collection:
    col.objects.unlink(front)
bpy.data.collections["PoolTable"].objects.link(front)

# Viga trasera
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.58, 0.35))
back = bpy.context.active_object
back.name = "Beam_Back"
back.scale = (1.33, 0.05, 0.05)
bpy.ops.object.transform_apply(rotation=False, scale=True)
back.data.materials.append(mat)
for col in back.users_collection:
    col.objects.unlink(back)
bpy.data.collections["PoolTable"].objects.link(back)

# Viga lateral izquierda
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.27, 0, 0.35))
left = bpy.context.active_object
left.name = "Beam_Left"
left.scale = (0.05, 0.63, 0.05)
bpy.ops.object.transform_apply(rotation=False, scale=True)
left.data.materials.append(mat)
for col in left.users_collection:
    col.objects.unlink(left)
bpy.data.collections["PoolTable"].objects.link(left)

# Viga lateral derecha
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.27, 0, 0.35))
right = bpy.context.active_object
right.name = "Beam_Right"
right.scale = (0.05, 0.63, 0.05)
bpy.ops.object.transform_apply(rotation=False, scale=True)
right.data.materials.append(mat)
for col in right.users_collection:
    col.objects.unlink(right)
bpy.data.collections["PoolTable"].objects.link(right)

print("Estructura inferior: 4 vigas")
''').get('output',''))

phase("CREAR SUPERFICIE DE JUEGO (FELT)")
print(send('''
import bpy

mat = bpy.data.materials["Felt_Green"]

# Tablero de juego (plano verde)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.78))
felt = bpy.context.active_object
felt.name = "Felt_Surface"
felt.scale = (2.74, 1.37, 1)
bpy.ops.object.transform_apply(rotation=False, scale=True)
felt.data.materials.append(mat)
for col in felt.users_collection:
    col.objects.unlink(felt)
bpy.data.collections["PoolTable"].objects.link(felt)

# Marco exterior (madera oscura)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.80))
frame = bpy.context.active_object
frame.name = "Outer_Frame"
frame.scale = (1.45, 0.74, 0.03)
bpy.ops.object.transform_apply(rotation=False, scale=True)
frame_mat = bpy.data.materials["Wood_Dark"]
frame.data.materials.append(frame_mat)
for col in frame.users_collection:
    col.objects.unlink(frame)
bpy.data.collections["PoolTable"].objects.link(frame)

print("Superficie: felt verde + marco exterior")
''').get('output',''))

phase("CREAR BOLSILLOS")
print(send('''
import bpy, math

mat = bpy.data.materials["Rubber_Black"]

# 6 bolsillos: 4 esquinas + 2 laterales
pocket_positions = [
    (-1.27, -0.58, 0.79),   # Front-Left corner
    (1.27, -0.58, 0.79),    # Front-Right corner
    (-1.27, 0.58, 0.79),    # Back-Left corner
    (1.27, 0.58, 0.79),     # Back-Right corner
    (0, -0.58, 0.79),       # Front-Center
    (0, 0.58, 0.79),        # Back-Center
]

pocket_sizes = [0.07, 0.07, 0.07, 0.07, 0.06, 0.06]  # Radio

for i, (x, y, z) in enumerate(pocket_sizes):
    pos = pocket_positions[i]
    
    # Boca del bolsillo (cilindro negro)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=pocket_sizes[i],
        depth=0.02,
        location=(pos[0], pos[1], pos[2])
    )
    pocket = bpy.context.active_object
    pocket.name = f"Pocket_{i+1}"
    pocket.data.materials.append(mat)
    for col in pocket.users_collection:
        col.objects.unlink(pocket)
    bpy.data.collections["PoolTable"].objects.link(pocket)

print("6 bolsillos creados (4 esquinas + 2 laterales)")
''').get('output',''))

phase("CREAR BANDAS (RAILS)")
print(send('''
import bpy

mat = bpy.data.materials["Wood_Light"]

# Bandas interiores (zonas de rebote)
# Front band
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.52, 0.81))
front_rail = bpy.context.active_object
front_rail.name = "Rail_Front"
front_rail.scale = (1.15, 0.04, 0.02)
bpy.ops.object.transform_apply(rotation=False, scale=True)
front_rail.data.materials.append(mat)
for col in front_rail.users_collection:
    col.objects.unlink(front_rail)
bpy.data.collections["PoolTable"].objects.link(front_rail)

# Back band
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.52, 0.81))
back_rail = bpy.context.active_object
back_rail.name = "Rail_Back"
back_rail.scale = (1.15, 0.04, 0.02)
bpy.ops.object.transform_apply(rotation=False, scale=True)
back_rail.data.materials.append(mat)
for col in back_rail.users_collection:
    col.objects.unlink(back_rail)
bpy.data.collections["PoolTable"].objects.link(back_rail)

# Left band (upper half)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.21, 0.26, 0.81))
left_rail_u = bpy.context.active_object
left_rail_u.name = "Rail_Left_Upper"
left_rail_u.scale = (0.04, 0.28, 0.02)
bpy.ops.object.transform_apply(rotation=False, scale=True)
left_rail_u.data.materials.append(mat)
for col in left_rail_u.users_collection:
    col.objects.unlink(left_rail_u)
bpy.data.collections["PoolTable"].objects.link(left_rail_u)

# Left band (lower half)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.21, -0.26, 0.81))
left_rail_l = bpy.context.active_object
left_rail_l.name = "Rail_Left_Lower"
left_rail_l.scale = (0.04, 0.28, 0.02)
bpy.ops.object.transform_apply(rotation=False, scale=True)
left_rail_l.data.materials.append(mat)
for col in left_rail_l.users_collection:
    col.objects.unlink(left_rail_l)
bpy.data.collections["PoolTable"].objects.link(left_rail_l)

# Right band (upper half)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.21, 0.26, 0.81))
right_rail_u = bpy.context.active_object
right_rail_u.name = "Rail_Right_Upper"
right_rail_u.scale = (0.04, 0.28, 0.02)
bpy.ops.object.transform_apply(rotation=False, scale=True)
right_rail_u.data.materials.append(mat)
for col in right_rail_u.users_collection:
    col.objects.unlink(right_rail_u)
bpy.data.collections["PoolTable"].objects.link(right_rail_u)

# Right band (lower half)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.21, -0.26, 0.81))
right_rail_l = bpy.context.active_object
right_rail_l.name = "Rail_Right_Lower"
right_rail_l.scale = (0.04, 0.28, 0.02)
bpy.ops.object.transform_apply(rotation=False, scale=True)
right_rail_l.data.materials.append(mat)
for col in right_rail_l.users_collection:
    col.objects.unlink(right_rail_l)
bpy.data.collections["PoolTable"].objects.link(right_rail_l)

print("6 bandas creadas (front, back, 2 left, 2 right)")
''').get('output',''))

phase("CREAR BALAS (16 BOLAS)")
print(send('''
import bpy, math

ball_colors = [
    ("Ball_White", "Cue_Ball"),      # Bola blanca (taco)
    ("Ball_Yellow", "Ball_1"),        # 1 - Amarilla
    ("Ball_Blue", "Ball_2"),          # 2 - Azul
    ("Ball_Red", "Ball_3"),           # 3 - Roja
    ("Ball_Purple", "Ball_4"),        # 4 - Púrpura
    ("Ball_Orange", "Ball_5"),        # 5 - Naranja
    ("Ball_Green", "Ball_6"),         # 6 - Verde
    ("Ball_Maroon", "Ball_7"),        # 7 - Granate
    ("Ball_Black", "Ball_8"),         # 8 - Negra (8-ball)
    ("Ball_Yellow", "Ball_9"),        # 9 - Amarilla rayada
    ("Ball_Blue", "Ball_10"),         # 10 - Azul rayada
    ("Ball_Red", "Ball_11"),          # 11 - Roja rayada
    ("Ball_Purple", "Ball_12"),       # 12 - Púrpura rayada
    ("Ball_Orange", "Ball_13"),       # 13 - Naranja rayada
    ("Ball_Green", "Ball_14"),        # 14 - Verde rayada
    ("Ball_Maroon", "Ball_15"),       # 15 - Granate rayada
]

# Asegurar que Ball_Black existe
if "Ball_Black" not in bpy.data.materials:
    m = bpy.data.materials.new("Ball_Black")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.15

# Posicionar bola blanca (taco)
cue_x, cue_y = -0.8, 0
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, location=(cue_x, cue_y, 0.806))
cue = bpy.context.active_object
cue.name = "Cue_Ball"
cue.data.materials.append(bpy.data.materials["Ball_White"])
for col in cue.users_collection:
    col.objects.unlink(cue)
bpy.data.collections["Balls"].objects.link(cue)

# Triángulo de bolas (5 filas)
start_x = 0.8
start_y = 0
spacing = 0.055  # Diámetro + espacio
ball_idx = 1

for row in range(5):
    for col in range(row + 1):
        x = start_x + row * spacing * 0.866  # cos(30°)
        y = start_y + (col - row/2) * spacing
        
        mat_name, ball_name = ball_colors[ball_idx]
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, location=(x, y, 0.806))
        ball = bpy.context.active_object
        ball.name = ball_name
        
        # Material (rayada para 9-15)
        if ball_idx >= 9:
            # Crear material rayada
            mat = bpy.data.materials.new(f"{ball_name}_Mat")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            # Color base
            base_mat = bpy.data.materials[mat_name]
            base_color = base_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value
            bsdf.inputs["Base Color"].default_value = base_color
            bsdf.inputs["Roughness"].default_value = 0.15
            ball.data.materials.append(mat)
        else:
            ball.data.materials.append(bpy.data.materials[mat_name])
        
        # Mover a colección
        for col_obj in ball.users_collection:
            col_obj.objects.unlink(ball)
        bpy.data.collections["Balls"].objects.link(ball)
        
        ball_idx += 1

print("16 bolas creadas (1 cue + 15 object balls)")
''').get('output',''))

phase("CREAR TACO (CUE STICK)")
print(send('''
import bpy, math

mat = bpy.data.materials["Cue_Wood"]

# Taco principal (cilindro largo)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.006,
    depth=1.45,
    location=(-1.6, 0, 0.82)
)
cue = bpy.context.active_object
cue.name = "Cue_Stick"
cue.rotation_euler = (0, 0, math.pi/2)
cue.data.materials.append(mat)
for col in cue.users_collection:
    col.objects.unlink(cue)
bpy.data.collections["Accessories"].objects.link(cue)

# Punta del taco (cilindro más fino)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.004,
    depth=0.05,
    location=(-0.87, 0, 0.82)
)
tip = bpy.context.active_object
tip.name = "Cue_Tip"
tip.rotation_euler = (0, 0, math.pi/2)
tip_mat = bpy.data.materials.new("Cue_Tip_Mat")
tip_mat.use_nodes = True
tip_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.85, 0.7, 1)
tip.data.materials.append(tip_mat)
for col in tip.users_collection:
    col.objects.unlink(tip)
bpy.data.collections["Accessories"].objects.link(tip)

# Taco de descanso (bridge)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.0, 0, 0.79))
rest = bpy.context.active_object
rest.name = "Cue_Rest"
rest.scale = (0.08, 0.04, 0.01)
bpy.ops.object.transform_apply(rotation=False, scale=True)
rest_mat = bpy.data.materials.new("Rest_Mat")
rest_mat.use_nodes = True
rest_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.15, 0.1, 0.05, 1)
rest.data.materials.append(rest_mat)
for col in rest.users_collection:
    col.objects.unlink(rest)
bpy.data.collections["Accessories"].objects.link(rest)

print("Taco: stick + tip + rest")
''').get('output',''))

phase("CREAR SALA (SUELO + PARED)")
print(send('''
import bpy, math

# Suelo de madera
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
mat_floor = bpy.data.materials.new("Floor_Wood")
mat_floor.use_nodes = True
mat_floor.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.35, 0.2, 1)
mat_floor.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5
floor.data.materials.append(mat_floor)
for col in floor.users_collection:
    col.objects.unlink(floor)
bpy.data.collections["Room"].objects.link(floor)

# Pared trasera
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 4, 1.5))
wall = bpy.context.active_object
wall.name = "Wall_Back"
wall.rotation_euler = (math.pi/2, 0, 0)
mat_wall = bpy.data.materials.new("Wall_Paint")
mat_wall.use_nodes = True
mat_wall.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.82, 0.75, 1)
wall.data.materials.append(mat_wall)
for col in wall.users_collection:
    col.objects.unlink(wall)
bpy.data.collections["Room"].objects.link(wall)

# Pared lateral
bpy.ops.mesh.primitive_plane_add(size=8, location=(-4, 0, 1.5))
wall_l = bpy.context.active_object
wall_l.name = "Wall_Left"
wall_l.rotation_euler = (0, math.pi/2, 0)
wall_l.data.materials.append(mat_wall)
for col in wall_l.users_collection:
    col.objects.unlink(wall_l)
bpy.data.collections["Room"].objects.link(wall_l)

print("Sala: suelo + 2 paredes")
''').get('output',''))

phase("ILUMINACIÓN")
print(send('''
import bpy

# Luz principal sobre la mesa (lámpara de billar)
bpy.ops.object.light_add(type="AREA", location=(0, 0, 1.8))
main_light = bpy.context.active_object
main_light.name = "Pool_Lamp"
main_light.data.energy = 600
main_light.data.size = 1.5
main_light.data.color = (1, 0.95, 0.85)

# Luces de ambiente
bpy.ops.object.light_add(type="AREA", location=(3, 0, 2.5))
ambient1 = bpy.context.active_object
ambient1.name = "Ambient_1"
ambient1.data.energy = 200
ambient1.data.size = 2

bpy.ops.object.light_add(type="AREA", location=(-3, 0, 2.5))
ambient2 = bpy.context.active_object
ambient2.name = "Ambient_2"
ambient2.data.energy = 200
ambient2.data.size = 2

print("Iluminación: 1 principal + 2 ambientales")
''').get('output',''))

phase("CÁMARA")
print(send('''
import bpy

bpy.ops.object.camera_add(location=(3.5, -3, 2.5))
cam = bpy.context.active_object
cam.name = "Main_Camera"
cam.rotation_euler = (1.1, 0, 0.65)
bpy.context.scene.camera = cam

# Configurar render
s = bpy.context.scene
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.engine = "BLENDER_EEVEE_NEXT"
s.eevee.taa_render_samples = 64

print("Cámara: 1920x1080, EEVEE_NEXT")
''').get('output',''))

phase("RESUMEN FINAL")
print(send('''
import bpy

# Contar por colección
print("\\n📦 ESTRUCTURA DE COLECCIONES:")
for col in bpy.data.collections:
    objs = [f"{o.name} ({o.type})" for o in col.objects]
    print(f"\\n  📁 {col.name} ({len(objs)} objetos):")
    for obj_name in objs[:5]:  # Primeros 5
        print(f"     • {obj_name}")
    if len(objs) > 5:
        print(f"     ... y {len(objs)-5} más")

# Estadísticas
print(f"\\n📊 ESTADÍSTICAS:")
print(f"  Total objetos: {len(bpy.data.objects)}")
print(f"  Materiales: {len(bpy.data.materials)}")
print(f"  Colecciones: {len(bpy.data.collections)}")
print(f"  Meshes: {len(bpy.data.meshes)}")

# Dimensiones de la mesa
print(f"\\n📐 DIMENSIONES MESA BILLAR:")
print(f"  Largo: 2.74m (9 pies)")
print(f"  Ancho: 1.37m (4.5 pies)")
print(f"  Altura: 0.80m")
print(f"  Superficie juego: 2.54m x 1.22m")
print(f"  Bolsillos: 6 (Ø 13-14cm)")
print(f"  Balas: 16 (Ø 5.25cm)")
''').get('output',''))

phase("GUARDAR")
print(send('''
import bpy
filepath = "/tmp/pool_table.blend"
bpy.ops.wm.save_as_mainfile(filepath=filepath)
print(f"Guardado: {filepath}")
''').get('output',''))

print("\n" + "="*60)
print("MESA DE BILLAR COMPLETADA!")
print("="*60)
