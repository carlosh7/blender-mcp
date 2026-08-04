"""
blender-mcp — Sculpt Engine
Motor de sculpting para formas orgánicas.
Inspirado en MB-Lab y herramientas de sculpting de Blender.
"""
try:
    import bpy
    import bmesh
except ImportError:
    bpy = None
    bmesh = None

import math
try:
    from mathutils import Vector
except ImportError:
    Vector = None


# ═══════════════════════════════════════════════════════════════
# SCULPT PRIMITIVES
# ═══════════════════════════════════════════════════════════════

def create_sculpt_base(primitive_type="sphere", subdivisions=4):
    """
    Crear base para sculpting.
    
    Args:
        primitive_type: Tipo de primitiva base
        subdivisions: Niveles de subdivisión
    
    Returns:
        Objeto base para sculpting
    """
    if primitive_type == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=1,
            segments=64,
            ring_count=32,
            location=(0, 0, 0)
        )
    elif primitive_type == "cube":
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        # Subdividir para tener más geometría
        obj = bpy.context.active_object
        mod = obj.modifiers.new("Subdivision", 'SUBSURF')
        mod.levels = subdivisions
        bpy.ops.object.modifier_apply(modifier=mod.name)
    elif primitive_type == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1,
            depth=2,
            vertices=64,
            location=(0, 0, 0)
        )
    
    obj = bpy.context.active_object
    obj.name = "SculptBase"
    
    # Entrar en modo sculpt
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='SCULPT')
    
    print(f"Base de sculpting creada: {primitive_type}")
    return obj


# ═══════════════════════════════════════════════════════════════
# SCULPT TOOLS (Simulados con operaciones de malla)
# ═══════════════════════════════════════════════════════════════

def smooth_region(obj, center, radius, strength=0.5):
    """
    Suavizar región de una malla.
    
    Args:
        obj: Objeto mesh
        center: Centro de la región (Vector)
        radius: Radio de la región
        strength: Fuerza del suavizado (0-1)
    """
    if obj.type != 'MESH':
        return
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Seleccionar vértices en la región
    bm = bmesh.from_edit_mesh(obj.data)
    for v in bm.verts:
        if (v.co - center).length < radius:
            v.select = True
    
    # Suavizar
    bpy.ops.mesh.smooth(iterations=3)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Región suavizada: radio {radius}")


def inflate_region(obj, center, radius, strength=0.2):
    """
    Inflar región de una malla.
    """
    if obj.type != 'MESH':
        return
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    bm = bmesh.from_edit_mesh(obj.data)
    for v in bm.verts:
        if (v.co - center).length < radius:
            v.select = True
    
    # Inflar (mover en dirección normal)
    bpy.ops.mesh.extrude_region_move(TRANSFORM_translate=(0, 0, 0.1))
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Región inflada: radio {radius}")


def create_crease(obj, edge_loop, depth=0.1):
    """
    Crear pliegue (crease) en un borde.
    """
    if obj.type != 'MESH':
        return
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Seleccionar borde
    bm = bmesh.from_edit_mesh(obj.data)
    for edge in bm.edges:
        if edge.index in edge_loop:
            edge.select = True
    
    # Crear pliegue
    bpy.ops.mesh.extrude_region_move(TRANSFORM_translate=(0, 0, -depth))
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Pliegue creado: profundidad {depth}")


def smooth整个人(obj, iterations=5):
    """
    Suavizar toda la malla.
    """
    if obj.type != 'MESH':
        return
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.smooth(iterations=iterations)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Malla suavizada: {iterations} iteraciones")


# ═══════════════════════════════════════════════════════════════
# FACE SCULPTING
# ═══════════════════════════════════════════════════════════════

def create_face_base(head_radius=0.12):
    """
    Crear base para cara (head).
    """
    # Cabeza base (esfera)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=head_radius,
        segments=32,
        ring_count=16,
        location=(0, 0, 0)
    )
    head = bpy.context.active_object
    head.name = "Face_Base"
    
    # Escalar ligeramente para forma ovalada
    head.scale = (1, 1.1, 0.95)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    print(f"Base de cara creada: radio {head_radius}")
    return head


def add_nose(parent, position=(0, -0.08, 0), size=0.03):
    """
    Agregar nariz a la cara.
    """
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=size,
        location=position
    )
    nose = bpy.context.active_object
    nose.name = "Face_Nose"
    nose.scale = (0.8, 1.2, 0.6)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    print(f"Nariz creada")
    return nose


def add_eyes(parent, spacing=0.04, size=0.015):
    """
    Agregar ojos a la cara.
    """
    eyes = []
    
    for side in ["L", "R"]:
        x_sign = 1 if side == "L" else -1
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=size,
            location=(x_sign * spacing, -0.06, 0.02)
        )
        eye = bpy.context.active_object
        eye.name = f"Face_Eye_{side}"
        
        # Material para ojos
        mat = bpy.data.materials.new(f"EyeMat_{side}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
        mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.0
        eye.data.materials.append(mat)
        
        eyes.append(eye)
    
    print(f"Ojos creados: {len(eyes)}")
    return eyes


def add_mouth(parent, width=0.03, position=(0, -0.07, -0.03)):
    """
    Agregar boca a la cara.
    """
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=position
    )
    mouth = bpy.context.active_object
    mouth.name = "Face_Mouth"
    mouth.scale = (width, 0.005, 0.008)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.new("MouthMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.6, 0.2, 0.2, 1)
    mouth.data.materials.append(mat)
    
    print(f"Boca creada")
    return mouth


# ═══════════════════════════════════════════════════════════════
# BODY SCULPTING
# ═══════════════════════════════════════════════════════════════

def create_torso(height=0.5, width=0.25, depth=0.15):
    """
    Crear torso simplificado.
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    torso = bpy.context.active_object
    torso.name = "Body_Torso"
    torso.scale = (width, depth, height)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    print(f"Torso creado: {width}x{depth}x{height}m")
    return torso


def create_limbs(side="L", limb_type="arm"):
    """
    Crear extremidades (brazos/piernas).
    """
    limbs = []
    
    x_sign = 1 if side == "L" else -1
    
    if limb_type == "arm":
        # Hombro
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.03,
            location=(x_sign * 0.15, 0, 0.4)
        )
        shoulder = bpy.context.active_object
        shoulder.name = f"Body_Shoulder_{side}"
        limbs.append(shoulder)
        
        # Brazo superior
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.025,
            depth=0.25,
            location=(x_sign * 0.2, 0, 0.3)
        )
        upper = bpy.context.active_object
        upper.name = f"Body_UpperArm_{side}"
        limbs.append(upper)
        
        # Brazo inferior
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.02,
            depth=0.22,
            location=(x_sign * 0.25, 0, 0.15)
        )
        lower = bpy.context.active_object
        lower.name = f"Body_LowerArm_{side}"
        limbs.append(lower)
    
    elif limb_type == "leg":
        # Muslo
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04,
            depth=0.3,
            location=(x_sign * 0.08, 0, -0.2)
        )
        upper = bpy.context.active_object
        upper.name = f"Body_UpperLeg_{side}"
        limbs.append(upper)
        
        # Pantorrilla
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.03,
            depth=0.28,
            location=(x_sign * 0.08, 0, -0.5)
        )
        lower = bpy.context.active_object
        lower.name = f"Body_LowerLeg_{side}"
        limbs.append(lower)
        
        # Pie
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_sign * 0.08, 0.03, -0.65)
        )
        foot = bpy.context.active_object
        foot.name = f"Body_Foot_{side}"
        foot.scale = (0.04, 0.06, 0.02)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        limbs.append(foot)
    
    print(f"Extremidades creadas: {limb_type}_{side} ({len(limbs)} piezas)")
    return limbs


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_sculpt_primitives():
    """Listar primitivas disponibles para sculpting"""
    return {
        "sphere": "Esfera (cabezas, bolas)",
        "cube": "Cubo (objetos rectangulares)",
        "cylinder": "Cilindro (brazos, piernas)",
    }


# ═══════════════════════════════════════════════════════════════
# SCULPT MODE TOOLS
# ═══════════════════════════════════════════════════════════════

def enter_sculpt_mode(obj):
    """Entrar en modo sculpt"""
    if bpy is None or obj is None:
        return False
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='SCULPT')
    print(f"Sculpt mode: {obj.name}")
    return True


def exit_sculpt_mode():
    """Salir de modo sculpt"""
    if bpy is None:
        return False
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Exited sculpt mode")
    return True


def set_sculpt_brush(brush_name, strength=0.5, radius=0.1):
    """Configurar pincel de sculpting"""
    if bpy is None:
        return False
    brush = bpy.data.brushes.get(brush_name)
    if brush:
        bpy.context.tool_settings.sculpt.brush = brush
        bpy.context.tool_settings.sculpt.strength = strength
        bpy.context.tool_settings.sculpt.size = radius
        print(f"Brush set: {brush_name}, strength={strength}")
        return True
    return False


def smooth_mesh_local(obj, factor=0.5):
    """Suavizar malla en ubicación específica"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.smooth(factor=factor)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Mesh smoothed: factor={factor}")
    return True


def inflate_mesh_local(obj, factor=0.2):
    """Inflar malla"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.inflate(factor=factor)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Mesh inflated: factor={factor}")
    return True


def pinch_mesh_local(obj, factor=0.5):
    """Pellizcar malla"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.pinch(factor=factor)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Mesh pinched: factor={factor}")
    return True


def grab_mesh_local(obj, offset=(0, 0, 0.1)):
    """Agarrar y mover malla"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.grab(offset=offset)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Mesh grabbed: offset={offset}")
    return True


def smooth整个人(obj, iterations=5):
    """Suavizar toda la malla"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.smooth(iterations=iterations)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Mesh smoothed: {iterations} iterations")
    return True


def flatten_mesh_local(obj, factor=0.5):
    """Aplanar malla"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flatten(factor=factor)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Mesh flattened: factor={factor}")
    return True


def randomize_mesh_local(obj, factor=0.1):
    """Randomizar vértices"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.randomize(factor=factor)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Mesh randomized: factor={factor}")
    return True


# ═══════════════════════════════════════════════════════════════
# ADVANCED SCULPT TOOLS
# ═══════════════════════════════════════════════════════════════

def symmetrize_mesh(obj, direction='NEGATIVE_X'):
    """
    Simetrizar malla.
    
    Args:
        obj: Objeto mesh
        direction: 'POSITIVE_X', 'NEGATIVE_X', etc.
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.symmetrize(direction=direction)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Mesh symmetrized: {direction}")
    return True


def remesh_mesh(obj, mode='VOXEL', voxel_size=0.1):
    """
    Remesh malla.
    
    Args:
        obj: Objeto mesh
        mode: 'VOXEL', 'SMOOTH', 'BLOCKS'
        voxel_size: Tamaño del voxel
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    mod = obj.modifiers.new("Remesh", 'REMESH')
    if mode == 'VOXEL':
        mod.mode = 'VOXEL'
        mod.voxel_size = voxel_size
    elif mode == 'SMOOTH':
        mod.mode = 'SMOOTH'
        mod.octree_depth = 4
    elif mode == 'BLOCKS':
        mod.mode = 'BLOCKS'
    
    print(f"Remesh applied: {mode}")
    return True


def mask_mesh(obj, vertex_group=None):
    """
    Aplicar máscara a malla.
    
    Args:
        obj: Objeto mesh
        vertex_group: Grupo de vértices para máscara (opcional)
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    # Crear vertex group para máscara
    if vertex_group is None:
        vertex_group = obj.vertex_groups.new(name="Mask")
    
    # Seleccionar todos los vértices
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.vertex_group_assign()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Mask applied: {vertex_group.name}")
    return True


def applyBoolean_operation(obj1, obj2, operation='DIFFERENCE'):
    """
    Aplicar operación booleana.
    
    Args:
        obj1: Objeto base
        obj2: Objeto operador
        operation: 'UNION', 'DIFFERENCE', 'INTERSECT'
    """
    if bpy is None or obj1 is None or obj2 is None:
        return False
    
    mod = obj1.modifiers.new("Boolean", 'BOOLEAN')
    mod.operation = operation
    mod.object = obj2
    
    print(f"Boolean: {obj1.name} {operation} {obj2.name}")
    return True


def applyMirror(obj, axis='X'):
    """
    Aplicar mirror.
    
    Args:
        obj: Objeto
        axis: 'X', 'Y', 'Z'
    """
    if bpy is None or obj is None:
        return False
    
    mod = obj.modifiers.new("Mirror", 'MIRROR')
    mod.use_x = axis == 'X'
    mod.use_y = axis == 'Y'
    mod.use_z = axis == 'Z'
    
    print(f"Mirror applied: {axis}")
    return True


def applyArray(obj, count=2, offset=(1, 0, 0)):
    """
    Aplicar array.
    
    Args:
        obj: Objeto
        count: Número de copias
        offset: Desplazamiento
    """
    if bpy is None or obj is None:
        return False
    
    mod = obj.modifiers.new("Array", 'ARRAY')
    mod.count = count
    mod.use_relative_offset = False
    mod.use_constant_offset = True
    mod.constant_offset_displace = offset
    
    print(f"Array applied: {count} copies")
    return True


def applySubdivision(obj, levels=2):
    """
    Aplicar subdivision surface.
    
    Args:
        obj: Objeto
        levels: Niveles de subdivisión
    """
    if bpy is None or obj is None:
        return False
    
    mod = obj.modifiers.new("Subdivision", 'SUBSURF')
    mod.levels = levels
    mod.render_levels = levels
    
    print(f"Subdivision applied: {levels} levels")
    return True


def applyBevel(obj, width=0.05, segments=2):
    """
    Aplicar bevel.
    
    Args:
        obj: Objeto
        width: Ancho del bevel
        segments: Segmentos
    """
    if bpy is None or obj is None:
        return False
    
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(30)
    
    print(f"Bevel applied: width={width}")
    return True


def applyDecimate(obj, ratio=0.5):
    """
    Aplicar decimate.
    
    Args:
        obj: Objeto
        ratio: Ratio de decimación
    """
    if bpy is None or obj is None:
        return False
    
    mod = obj.modifiers.new("Decimate", 'DECIMATE')
    mod.ratio = ratio
    
    print(f"Decimate applied: ratio={ratio}")
    return True


# ═══════════════════════════════════════════════════════════════
# ADVANCED SCULPTING
# ═══════════════════════════════════════════════════════════════

def sculpt_face(head_obj):
    """
    Sculpt una cara completa en una cabeza.
    
    Args:
        head_obj: Objeto cabeza (esfera)
    """
    if bpy is None or head_obj is None:
        return None
    
    # Crear nariz
    nose = add_nose(head_obj)
    
    # Crear ojos
    eyes = add_eyes(head_obj)
    
    # Crear boca
    mouth = add_mouth(head_obj)
    
    # Suavizar toda la cara
    smooth整个人(head_obj, iterations=3)
    
    print(f"Cara sculpted: nariz + ojos + boca")
    return {"nose": nose, "eyes": eyes, "mouth": mouth}


def sculpt_body(torso_obj):
    """
    Sculpt un cuerpo completo.
    
    Args:
        torso_obj: Objeto torso
    """
    if bpy is None or torso_obj is None:
        return None
    
    # Crear extremidades
    left_arm = create_limbs("L", "arm")
    right_arm = create_limbs("R", "arm")
    left_leg = create_limbs("L", "leg")
    right_leg = create_limbs("R", "leg")
    
    # Suavizar torso
    smooth整个人(torso_obj, iterations=3)
    
    print(f"Cuerpo sculpted: torso + 4 extremidades")
    return {
        "torso": torso_obj,
        "left_arm": left_arm,
        "right_arm": right_arm,
        "left_leg": left_leg,
        "right_leg": right_leg,
    }


def extrude_region(obj, face_index, distance=0.1):
    """
    Extruir una cara de la malla.
    
    Args:
        obj: Objeto mesh
        face_index: Índice de la cara a extruir
        distance: Distancia de extrusión
    """
    if bpy is None or obj.type != 'MESH':
        return
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    bm = bmesh.from_edit_mesh(obj.data)
    if face_index < len(bm.faces):
        bm.faces[face_index].select = True
        bmesh.update_edit_mesh(obj.data)
    
    bpy.ops.mesh.extrude_region_move(TRANSFORM_translate=(0, 0, distance))
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Face extruded: index={face_index}, distance={distance}")


def bevel_edge(obj, edge_index, width=0.05, segments=2):
    """
    Aplicar bevel a un borde.
    
    Args:
        obj: Objeto mesh
        edge_index: Índice del borde
        width: Ancho del bevel
        segments: Número de segmentos
    """
    if bpy is None or obj.type != 'MESH':
        return
    
    # Agregar modifier bevel
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(30)
    
    print(f"Bevel applied: width={width}, segments={segments}")


def create_subdivision(obj, levels=2):
    """
    Crear subdivisión surface.
    
    Args:
        obj: Objeto mesh
        levels: Niveles de subdivisión
    """
    if bpy is None or obj.type != 'MESH':
        return
    
    mod = obj.modifiers.new("Subdivision", 'SUBSURF')
    mod.levels = levels
    mod.render_levels = levels
    
    print(f"Subdivision: {levels} levels")


def decimate_mesh(obj, ratio=0.5):
    """
    Decimar malla (reducir polígonos).
    
    Args:
        obj: Objeto mesh
        ratio: Ratio de decimación (0-1)
    """
    if bpy is None or obj.type != 'MESH':
        return
    
    mod = obj.modifiers.new("Decimate", 'DECIMATE')
    mod.ratio = ratio
    
    print(f"Decimate: ratio={ratio}")



def get_sculpt_info(obj):
    """Obtener información de sculpting"""
    if obj.type != 'MESH':
        return {"error": "No es un mesh"}
    
    return {
        "name": obj.name,
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
        "mode": obj.mode if hasattr(obj, 'mode') else 'OBJECT',
    }


# ═══════════════════════════════════════════════════════════════
# SCULPT MODE TOOLS
# ═══════════════════════════════════════════════════════════════

def enter_sculpt_mode(obj):
    """Entrar en modo sculpt"""
    if bpy is None or obj is None:
        return False
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='SCULPT')
    print(f"Sculpt mode: {obj.name}")
    return True


def exit_sculpt_mode():
    """Salir de modo sculpt"""
    if bpy is None:
        return False
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Exited sculpt mode")
    return True


def smooth_mesh(obj, iterations=5):
    """Suavizar malla completa"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.smooth(iterations=iterations)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Mesh smoothed: {iterations} iterations")
    return True


def flatten_mesh(obj, strength=0.5):
    """Aplanar malla"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flatten(factor=strength)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Mesh flattened: strength={strength}")
    return True


def randomize_mesh(obj, factor=0.1):
    """Randomizar vértices de la malla"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.randomize(factor=factor)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Mesh randomized: factor={factor}")
    return True


def spin_mesh(obj, steps=12, angle=360):
    """Rotar malla (spin)"""
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.spin(steps=steps, angle=math.radians(angle))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Mesh spun: {steps} steps, {angle} degrees")
    return True


# ═══════════════════════════════════════════════════════════════
# SCULPT PRESETS
# ═══════════════════════════════════════════════════════════════

SCULPT_PRESETS = {
    "smooth": {"description": "Suavizar", "strength": 0.5},
    "flatten": {"description": "Aplanar", "strength": 0.5},
    "inflate": {"description": "Inflar", "strength": 0.3},
    "deflate": {"description": "Desinflar", "strength": 0.3},
    "grab": {"description": "Agarrar", "strength": 0.8},
    "pinch": {"description": "Pellizcar", "strength": 0.5},
    "crease": {"description": "Pliegue", "strength": 0.6},
    "scrape": {"description": "Raspar", "strength": 0.4},
    "fill": {"description": "Rellenar", "strength": 0.5},
    "draw": {"description": "Dibujar", "strength": 0.5},
}


def apply_sculpt_preset(obj, preset_name):
    """
    Aplicar preset de sculpting.
    
    Args:
        obj: Objeto
        preset_name: Nombre del preset
    """
    if bpy is None or obj is None:
        return False
    
    if preset_name not in SCULPT_PRESETS:
        print(f"Preset no encontrado: {preset_name}")
        return False
    
    preset = SCULPT_PRESETS[preset_name]
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Aplicar operación según preset
    if preset_name == "smooth":
        bpy.ops.mesh.smooth(factor=preset["strength"])
    elif preset_name == "flatten":
        bpy.ops.mesh.flatten(factor=preset["strength"])
    elif preset_name == "inflate":
        bpy.ops.mesh.inflate(factor=preset["strength"])
    elif preset_name == "pinch":
        bpy.ops.mesh.pinch(factor=preset["strength"])
    elif preset_name == "grab":
        bpy.ops.mesh.grab(offset=(0, 0, 0.1))
    elif preset_name == "randomize":
        bpy.ops.mesh.randomize(factor=preset["strength"])
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Sculpt preset applied: {preset_name}")
    return True


# ═══════════════════════════════════════════════════════════════
# SYMMETRIZE
# ═══════════════════════════════════════════════════════════════

def symmetrize_mesh(obj, direction='NEGATIVE_X'):
    """
    Simetrizar malla.
    
    Args:
        obj: Objeto
        direction: 'POSITIVE_X', 'NEGATIVE_X', etc.
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.symmetrize(direction=direction)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Mesh symmetrized: {direction}")
    return True


# ═══════════════════════════════════════════════════════════════
# REMESH
# ═══════════════════════════════════════════════════════════════

def remesh_mesh(obj, mode='VOXEL', voxel_size=0.1):
    """
    Remesh malla.
    
    Args:
        obj: Objeto
        mode: 'VOXEL', 'SMOOTH', 'BLOCKS'
        voxel_size: Tamaño del voxel
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    mod = obj.modifiers.new("Remesh", 'REMESH')
    
    if mode == 'VOXEL':
        mod.mode = 'VOXEL'
        mod.voxel_size = voxel_size
    elif mode == 'SMOOTH':
        mod.mode = 'SMOOTH'
        mod.octree_depth = 4
    elif mode == 'BLOCKS':
        mod.mode = 'BLOCKS'
    
    print(f"Remesh applied: {mode}")
    return True


# ═══════════════════════════════════════════════════════════════
# DECIMATE
# ═══════════════════════════════════════════════════════════════

def decimate_mesh(obj, ratio=0.5):
    """
    Decimar malla (reducir polígonos).
    
    Args:
        obj: Objeto
        ratio: Ratio de decimación (0-1)
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    mod = obj.modifiers.new("Decimate", 'DECIMATE')
    mod.ratio = ratio
    
    print(f"Decimate applied: ratio={ratio}")
    return True


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_sculpt_presets():
    """Listar presets de sculpting"""
    return {k: v["description"] for k, v in SCULPT_PRESETS.items()}


def get_sculpt_info(obj):
    """Obtener información de sculpting"""
    if obj is None or obj.type != 'MESH':
        return {"error": "No es un mesh"}
    
    return {
        "name": obj.name,
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
        "has_smooth": any(p.use_smooth for p in obj.data.polygons),
        "modifiers": [m.type for m in obj.modifiers],
    }
