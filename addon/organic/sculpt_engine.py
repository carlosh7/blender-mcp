"""
blender-mcp — Sculpt Engine
Motor de sculpting para formas orgánicas.
Inspirado en MB-Lab y herramientas de sculpting de Blender.
"""
import bpy
import bmesh
import math
from mathutils import Vector


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
    bpy.ops.mesh.extrude_region_move(TRANSFORM Translate)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Región inflada: radio {radius}")


def create crease(obj, edge_loop, depth=0.1):
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
    bpy.ops.mesh.extrude_region_move(TRANSFORM Translate)
    
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
