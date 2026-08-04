#!/usr/bin/env python3
"""blender-mcp — Objetos Cotidianos de la Vida Real"""
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


# CLEAN
print(run('''
import bpy
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
for m in bpy.data.materials: bpy.data.materials.remove(m)
for mesh in bpy.data.meshes: bpy.data.meshes.remove(m)
s = bpy.context.scene; s.frame_start=1; s.frame_end=1
print("Clean")
''').get('output',''))

# =============================================
# SILLA DE MADERA
# =============================================
phase("SILLA DE MADERA")
print(run('''
import bpy

wood = bpy.data.materials.new("Wood")
wood.use_nodes = True
bsdf = wood.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.4, 0.25, 0.12, 1)
bsdf.inputs["Roughness"].default_value = 0.7
bsdf.inputs["Metallic"].default_value = 0.0

seat = bpy.data.materials.new("Seat")
seat.use_nodes = True
seat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.55, 0.35, 0.18, 1)
seat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6

# Asiento
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.45))
silla = bpy.context.active_object; silla.name = "Silla_Asiento"
silla.scale = (0.5, 0.5, 0.05)
bpy.ops.object.transform_apply(rotation=False, scale=True)
silla.data.materials.append(seat)

# Patas (4)
positions = [(0.2, 0.2), (0.2, -0.2), (-0.2, 0.2), (-0.2, -0.2)]
for i, (x, y) in enumerate(positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.45, location=(x, y, 0.225))
    pata = bpy.context.active_object; pata.name = f"Silla_Pata_{i}"
    pata.data.materials.append(wood)

# Respaldo (3 barras verticales)
for i in range(3):
    x = (i - 1) * 0.15
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.5, location=(x, -0.22, 0.7))
    barra = bpy.context.active_object; barra.name = f"Silla_Respaldo_{i}"
    barra.data.materials.append(wood)

# Barra superior del respaldo
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.4, location=(0, -0.22, 0.95))
barra_top = bpy.context.active_object; barra_top.name = "Silla_Respaldo_Top"
barra_top.rotation_euler = (0, math.pi/2, 0)
barra_top.data.materials.append(wood)

print("Silla creada: asiento + 4 patas + respaldo")
''').get('output',''))


# =============================================
# MESA CON CAJONES
# =============================================
phase("MESA CON CAJONES")
print(run('''
import bpy

# Material madera oscura
dark_wood = bpy.data.materials.new("DarkWood")
dark_wood.use_nodes = True
bsdf = dark_wood.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.3, 0.18, 0.08, 1)
bsdf.inputs["Roughness"].default_value = 0.65

# Material cajon
drawer_mat = bpy.data.materials.new("Drawer")
drawer_mat.use_nodes = True
drawer_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.22, 0.1, 1)
drawer_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5

# Material tirador (bronce)
bronze = bpy.data.materials.new("Bronze")
bronze.use_nodes = True
bronze.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.55, 0.2, 1)
bronze.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.9
bronze.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.3

# Tabla superior
bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 0, 0.75))
tabla = bpy.context.active_object; tabla.name = "Mesa_Top"
tabla.scale = (1.2, 0.6, 0.04)
bpy.ops.object.transform_apply(rotation=False, scale=True)
tabla.data.materials.append(dark_wood)

# 4 patas
for x in [2.55, 3.45]:
    for y in [-0.5, 0.5]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.37))
        pata = bpy.context.active_object; pata.name = f"Mesa_Pata"
        pata.scale = (0.05, 0.05, 0.74)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        pata.data.materials.append(dark_wood)

# Cajones (2)
for i, y_pos in enumerate([-0.15, 0.15]):
    # Cajon
    bpy.ops.mesh.primitive_cube_add(size=1, location=(3, y_pos, 0.6))
    cajon = bpy.context.active_object; cajon.name = f"Mesa_Cajon_{i}"
    cajon.scale = (0.35, 0.18, 0.1)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    cajon.data.materials.append(drawer_mat)
    
    # Tirador
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.12, location=(3, y_pos - 0.09, 0.6))
    tirador = bpy.context.active_object; tirador.name = f"Mesa_Tirador_{i}"
    tirador.rotation_euler = (0, math.pi/2, 0)
    tirador.data.materials.append(bronze)

# Repisa inferior
bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 0, 0.2))
repisa = bpy.context.active_object; repisa.name = "Mesa_Repisa"
repisa.scale = (1.0, 0.5, 0.03)
bpy.ops.object.transform_apply(rotation=False, scale=True)
repisa.data.materials.append(dark_wood)

print("Mesa creada: tabla + 4 patas + 2 cajones + repisa")
''').get('output',''))


# =============================================
# LAPARA DE ESCRITORIO
# =============================================
phase("LAMPARA DE ESCRITORIO")
print(run('''
import bpy, math

# Material metal negro
black_metal = bpy.data.materials.new("BlackMetal")
black_metal.use_nodes = True
bsdf = black_metal.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)
bsdf.inputs["Metallic"].default_value = 0.8
bsdf.inputs["Roughness"].default_value = 0.3

# Material pantalla (blanco cálido)
shade_mat = bpy.data.materials.new("LampShade")
shade_mat.use_nodes = True
shade_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.95, 0.9, 0.8, 1)
shade_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8

# Base circular
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.03, location=(6, 0, 0.015))
base = bpy.context.active_object; base.name = "Lamp_Base"
base.data.materials.append(black_metal)

# Vara vertical
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.5, location=(6, 0, 0.28))
vara = bpy.context.active_object; vara.name = "Lamp_Vara"
vara.data.materials.append(black_metal)

# Brazo angular (45 grados)
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.35, location=(6.12, 0, 0.55))
brazo = bpy.context.active_object; brazo.name = "Lamp_Brazo"
brazo.rotation_euler = (0, 0, math.pi/6)
brazo.data.materials.append(black_metal)

# Pantalla (cono invertido)
bpy.ops.mesh.primitive_cone_add(radius1=0.12, radius2=0.06, depth=0.12, location=(6.25, 0, 0.62))
pantalla = bpy.context.active_object; pantalla.name = "Lamp_Pantalla"
pantalla.data.materials.append(shade_mat)

# Bulbo (esfera pequeña)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(6.25, 0, 0.57))
bulbo = bpy.context.active_object; bulbo.name = "Lamp_Bulb"
mat_bulb = bpy.data.materials.new("Bulb")
mat_bulb.use_nodes = True
em = mat_bulb.node_tree.nodes.new("ShaderNodeEmission")
em.inputs["Color"].default_value = (1, 0.9, 0.7, 1)
em.inputs["Strength"].default_value = 3
mat_bulb.node_tree.links.new(em.outputs["Emission"], mat_bulb.node_tree.nodes["Material Output"].inputs["Surface"])
bulbo.data.materials.append(mat_bulb)

# Luz puntual
bpy.ops.object.light_add(type="POINT", location=(6.25, 0, 0.55))
luz = bpy.context.active_object; luz.name = "Lamp_Light"
luz.data.energy = 100
luz.data.color = (1, 0.9, 0.7)

print("Lampara creada: base + vara + brazo + pantalla + bulbo + luz")
''').get('output',''))


# =============================================
# TAZA DE CAFE
# =============================================
phase("TAZA DE CAFE")
print(run('''
import bpy, math

# Material ceramica blanca
ceramic = bpy.data.materials.new("Ceramic")
ceramic.use_nodes = True
bsdf = ceramic.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.93, 1)
bsdf.inputs["Roughness"].default_value = 0.15
bsdf.inputs["Metallic"].default_value = 0.0

# Material cafe
coffee_mat = bpy.data.materials.new("Coffee")
coffee_mat.use_nodes = True
coffee_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.15, 0.08, 0.02, 1)
coffee_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.1
coffee_mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.0

# Cuerpo de la taza (cilindro hueco simulado con toroide + disco)
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.2, location=(0, -3, 0.1))
taza = bpy.context.active_object; taza.name = "Taza_Body"
taza.data.materials.append(ceramic)

# Disco interior (cafe)
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.005, location=(0, -3, 0.18))
cafe = bpy.context.active_object; cafe.name = "Taza_Coffee"
cafe.data.materials.append(coffee_mat)

# Asa (toroide cortado)
bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.015, location=(0.15, -3, 0.12))
asa = bpy.context.active_object; asa.name = "Taza_Handle"
asa.rotation_euler = (0, math.pi/2, 0)
asa.data.materials.append(ceramic)

# Plato base
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.015, location=(0, -3, 0.007))
plato = bpy.context.active_object; plato.name = "Taza_Plate"
plato.data.materials.append(ceramic)

# Cucharita
bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.15, location=(0.15, -3.15, 0.1))
cuch = bpy.context.active_object; cuch.name = "Cuchara"
cuch.rotation_euler = (0, 0, math.pi/4)
mat_sp = bpy.data.materials.new("Silverware")
mat_sp.use_nodes = True
mat_sp.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.85, 0.85, 1)
mat_sp.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
mat_sp.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.1
cuch.data.materials.append(mat_sp)

# Copa de la cuchara
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(0.2, -3.2, 0.17))
copa = bpy.context.active_object; copa.name = "Cuchara_Copa"
copa.scale = (1, 0.6, 0.4)
bpy.ops.object.transform_apply(rotation=False, scale=True)
copa.data.materials.append(mat_sp)

print("Taza creada: taza + cafe + asa + plato + cucharita")
''').get('output',''))


# =============================================
# RELOJ DE PARED
# =============================================
phase("RELOJ DE PARED")
print(run('''
import bpy, math

# Material carcasa
case_mat = bpy.data.materials.new("ClockCase")
case_mat.use_nodes = True
bsdf = case_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
bsdf.inputs["Roughness"].default_value = 0.2
bsdf.inputs["Metallic"].default_value = 0.5

# Material esfera blanca
face_mat = bpy.data.materials.new("ClockFace")
face_mat.use_nodes = True
face_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.95, 0.95, 0.9, 1)
face_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.3

# Material marcadores
marker_mat = bpy.data.materials.new("ClockMarker")
marker_mat.use_nodes = True
marker_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)

# Material dorado (manecillas)
gold_mat = bpy.data.materials.new("ClockGold")
gold_mat.use_nodes = True
gold_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.65, 0.1, 1)
gold_mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
gold_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.15

# Carcasa (cilindro)
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.05, location=(-5, -6, 1.5))
cuerpo = bpy.context.active_object; cuerpo.name = "Reloj_Case"
cuerpo.data.materials.append(case_mat)

# Esfera blanca
bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.01, location=(-5, -5.97, 1.5))
esfera = bpy.context.active_object; esfera.name = "Reloj_Face"
esfera.data.materials.append(face_mat)

# 12 marcadores de hora
for i in range(12):
    angle = (i / 12) * math.pi * 2 - math.pi/2
    x = -5 + math.cos(angle) * 0.25
    y = -5.97 + math.sin(angle) * 0.25
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 1.5))
    marcador = bpy.context.active_object; marcador.name = f"Reloj_Mark_{i}"
    marcador.scale = (0.015, 0.005, 0.02)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    # Rotar para que apunte al centro
    marcador.rotation_euler = (0, 0, angle + math.pi/2)
    marcador.data.materials.append(marker_mat)

# Manecilla horas
bpy.ops.mesh.primitive_cube_add(size=1, location=(-5, -5.85, 1.52))
hora = bpy.context.active_object; hora.name = "Reloj_HourHand"
hora.scale = (0.008, 0.15, 0.005)
bpy.ops.object.transform_apply(rotation=False, scale=True)
hora.rotation_euler = (0, 0, math.pi/4)
hora.data.materials.append(gold_mat)

# Manecilla minutos
bpy.ops.mesh.primitive_cube_add(size=1, location=(-5, -5.82, 1.53))
minuto = bpy.context.active_object; minuto.name = "Reloj_MinuteHand"
minuto.scale = (0.005, 0.22, 0.004)
bpy.ops.object.transform_apply(rotation=False, scale=True)
minuto.rotation_euler = (0, 0, -math.pi/3)
minuto.data.materials.append(gold_mat)

# Centro (punto dorado)
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.01, location=(-5, -5.97, 1.54))
centro = bpy.context.active_object; centro.name = "Reloj_Center"
centro.data.materials.append(gold_mat)

print("Reloj creado: carcasa + esfera + 12 marcadores + manecillas")
''').get('output',''))


# =============================================
# MACETA CON PLANTA
# =============================================
phase("MACETA CON PLANTA")
print(run('''
import bpy, math

# Material terracota
terracota = bpy.data.materials.new("Terracota")
terracota.use_nodes = True
bsdf = terracota.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.7, 0.35, 0.15, 1)
bsdf.inputs["Roughness"].default_value = 0.8

# Material tierra
dirt = bpy.data.materials.new("Dirt")
dirt.use_nodes = True
dirt.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.12, 0.05, 1)
dirt.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95

# Material hoja
leaf = bpy.data.materials.new("Leaf")
leaf.use_nodes = True
leaf.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.5, 0.15, 1)
leaf.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.4

# Maceta (cono)
bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0.1, depth=0.25, location=(-3, -6, 0.125))
maceta = bpy.context.active_object; maceta.name = "Maceta_Body"
maceta.data.materials.append(terracota)

# Borde
bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.015, location=(-3, -6, 0.25))
borde = bpy.context.active_object; borde.name = "Maceta_Rim"
borde.data.materials.append(terracota)

# Tierra
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.02, location=(-3, -6, 0.24))
tierra = bpy.context.active_object; tierra.name = "Maceta_Dirt"
tierra.data.materials.append(dirt)

# Tallo
bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.2, location=(-3, -6, 0.35))
tallo = bpy.context.active_object; tallo.name = "Plant_Stem"
tallo.data.materials.append(leaf)

# Hojas (5 elipsoides)
for i in range(5):
    angle = (i / 5) * math.pi * 2
    x = -3 + math.cos(angle) * 0.08
    y = -6 + math.sin(angle) * 0.08
    z = 0.42 + i * 0.03
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(x, y, z))
    hoja = bpy.context.active_object; hoja.name = f"Plant_Leaf_{i}"
    hoja.scale = (1.5, 0.8, 0.3)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    hoja.rotation_euler = (angle, 0, 0)
    hoja.data.materials.append(leaf)

# Flor (esfera amarilla)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(-3, -6, 0.55))
flor = bpy.context.active_object; flor.name = "Plant_Flower"
flor.scale = (1.2, 1.2, 0.8)
bpy.ops.object.transform_apply(rotation=False, scale=True)
mat_flower = bpy.data.materials.new("Flower")
mat_flower.use_nodes = True
mat_flower.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 0.8, 0.1, 1)
flor.data.materials.append(mat_flower)

print("Maceta creada: maceta + tierra + tallo + 5 hojas + flor")
''').get('output',''))


# =============================================
# LIBRO APILADO
# =============================================
phase("LIBROS APILADOS")
print(run('''
import bpy

colors = [
    (0.7, 0.1, 0.1, 1),   # Rojo
    (0.1, 0.2, 0.7, 1),   # Azul
    (0.1, 0.5, 0.2, 1),   # Verde
    (0.8, 0.5, 0.1, 1),   # Naranja
    (0.5, 0.1, 0.5, 1),   # Morado
]

for i, color in enumerate(colors):
    h = 0.04
    z = 0.02 + i * (h + 0.002)
    
    # Tapa
    bpy.ops.mesh.primitive_cube_add(size=1, location=(6, -6, z))
    libro = bpy.context.active_object; libro.name = f"Book_{i}"
    libro.scale = (0.15, 0.2, h/2)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    mat = bpy.data.materials.new(f"BookMat_{i}")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    libro.data.materials.append(mat)
    
    # Paginas (blanco)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(6, -6, z + 0.001))
    pag = bpy.context.active_object; pag.name = f"Book_Pages_{i}"
    pag.scale = (0.13, 0.18, (h-0.01)/2)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    mat_p = bpy.data.materials.new("Pages")
    mat_p.use_nodes = True
    mat_p.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.95, 0.93, 0.88, 1)
    pag.data.materials.append(mat_p)

print("5 libros apilados con colores diferentes")
''').get('output',''))


# =============================================
# LUZ + CAMARA + SUELO
# =============================================
phase("LUZ + CAMARA + SUELO")
print(run('''
import bpy

# Suelo
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, -2, 0))
suelo = bpy.context.active_object; suelo.name = "Floor"
mat_floor = bpy.data.materials.new("FloorMat")
mat_floor.use_nodes = True
mat_floor.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.6, 0.55, 0.5, 1)
mat_floor.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.4
suelo.data.materials.append(mat_floor)

# Pared
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, -8, 2.5))
pared = bpy.context.active_object; pared.name = "Wall"
pared.rotation_euler = (math.pi/2, 0, 0)
mat_wall = bpy.data.materials.new("WallMat")
mat_wall.use_nodes = True
mat_wall.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.83, 0.8, 1)
pared.data.materials.append(mat_wall)

# Luces
bpy.ops.object.light_add(type="AREA", location=(4, 0, 5))
bpy.context.active_object.data.energy = 800; bpy.context.active_object.data.size = 5
bpy.context.active_object.name = "KeyLight"
bpy.ops.object.light_add(type="AREA", location=(-4, -2, 4))
bpy.context.active_object.data.energy = 300
bpy.ops.object.light_add(type="AREA", location=(0, 4, 4))
bpy.context.active_object.data.energy = 400

# Camara
bpy.ops.object.camera_add(location=(8, 6, 4))
cam = bpy.context.active_object; cam.name = "Camera"
cam.rotation_euler = (1.1, 0, 0.6)
bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
bpy.context.scene.eevee.taa_render_samples = 64

print("Escena: suelo + pared + 3 luces + camara 1920x1080")
''').get('output',''))


# RESUMEN
phase("RESUMEN")
print(run('''
import bpy
s = bpy.context.scene
types = {}
for o in s.objects: types[o.type] = types.get(o.type,0)+1
print(f"Total: {len(s.objects)} objetos")
for t,c in sorted(types.items()): print(f"  {t}: {c}")
print(f"Materiales: {len(bpy.data.materials)}")
print(f"Meshes: {len(bpy.data.meshes)}")
''').get('output',''))

# GUARDAR
print(run('''
import bpy
bpy.ops.wm.save_as_mainfile(filepath="/tmp/daily_objects.blend")
print("Guardado: /tmp/daily_objects.blend")
''').get('output',''))

print("\n" + "="*60)
print("OBJETOS COTIDIANOS COMPLETADOS!")
print("="*60)
