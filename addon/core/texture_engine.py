"""
blender-mcp — Texture Engine
Motor de texturizado: UV Unwrap, PBR Materials, Procedural Textures.
"""
import bpy
import bmesh
import math
from mathutils import Vector


# ═══════════════════════════════════════════════════════════════
# MATERIALES PBR (50+ presets)
# ═══════════════════════════════════════════════════════════════

PBR_MATERIALS = {
    # Maderas
    "wood_oak": {"color": (0.45, 0.30, 0.15), "roughness": 0.7, "metallic": 0.0},
    "wood_walnut": {"color": (0.30, 0.18, 0.08), "roughness": 0.65, "metallic": 0.0},
    "wood_cherry": {"color": (0.55, 0.25, 0.12), "roughness": 0.6, "metallic": 0.0},
    "wood_pine": {"color": (0.65, 0.50, 0.30), "roughness": 0.75, "metallic": 0.0},
    "wood_maple": {"color": (0.70, 0.55, 0.35), "roughness": 0.6, "metallic": 0.0},
    
    # Metales
    "metal_iron": {"color": (0.35, 0.35, 0.35), "roughness": 0.4, "metallic": 0.9},
    "metal_steel": {"color": (0.60, 0.60, 0.60), "roughness": 0.2, "metallic": 1.0},
    "metal_aluminum": {"color": (0.75, 0.75, 0.75), "roughness": 0.15, "metallic": 0.9},
    "metal_copper": {"color": (0.72, 0.45, 0.20), "roughness": 0.25, "metallic": 0.95},
    "metal_gold": {"color": (0.85, 0.65, 0.10), "roughness": 0.1, "metallic": 1.0},
    "metal_silver": {"color": (0.90, 0.90, 0.90), "roughness": 0.05, "metallic": 1.0},
    "metal_bronze": {"color": (0.80, 0.50, 0.20), "roughness": 0.3, "metallic": 0.85},
    "metal_chrome": {"color": (0.95, 0.95, 0.95), "roughness": 0.02, "metallic": 1.0},
    
    # Piedras
    "stone_granite": {"color": (0.50, 0.48, 0.45), "roughness": 0.8, "metallic": 0.0},
    "stone_marble": {"color": (0.90, 0.88, 0.85), "roughness": 0.15, "metallic": 0.0},
    "stone_slate": {"color": (0.30, 0.30, 0.35), "roughness": 0.7, "metallic": 0.0},
    "stone_sandstone": {"color": (0.75, 0.65, 0.50), "roughness": 0.85, "metallic": 0.0},
    "stone_basalt": {"color": (0.20, 0.20, 0.22), "roughness": 0.6, "metallic": 0.0},
    
    # Plásticos
    "plastic_white": {"color": (0.90, 0.90, 0.90), "roughness": 0.4, "metallic": 0.0},
    "plastic_black": {"color": (0.05, 0.05, 0.05), "roughness": 0.4, "metallic": 0.0},
    "plastic_red": {"color": (0.80, 0.10, 0.10), "roughness": 0.4, "metallic": 0.0},
    "plastic_blue": {"color": (0.10, 0.20, 0.80), "roughness": 0.4, "metallic": 0.0},
    "plastic_green": {"color": (0.10, 0.70, 0.20), "roughness": 0.4, "metallic": 0.0},
    "plastic_yellow": {"color": (0.90, 0.85, 0.10), "roughness": 0.4, "metallic": 0.0},
    "plastic_transparent": {"color": (0.95, 0.95, 0.95), "roughness": 0.1, "metallic": 0.0},
    
    # Telas
    "fabric_cotton": {"color": (0.90, 0.88, 0.85), "roughness": 0.9, "metallic": 0.0},
    "fabric_denim": {"color": (0.20, 0.30, 0.50), "roughness": 0.85, "metallic": 0.0},
    "fabric_silk": {"color": (0.85, 0.80, 0.75), "roughness": 0.3, "metallic": 0.1},
    "fabric_leather": {"color": (0.35, 0.20, 0.10), "roughness": 0.6, "metallic": 0.0},
    "fabric_velvet": {"color": (0.40, 0.10, 0.10), "roughness": 0.95, "metallic": 0.0},
    
    # Vidrio
    "glass_clear": {"color": (0.95, 0.95, 0.95), "roughness": 0.0, "metallic": 0.0},
    "glass_frosted": {"color": (0.85, 0.85, 0.85), "roughness": 0.5, "metallic": 0.0},
    "glass_colored": {"color": (0.30, 0.50, 0.80), "roughness": 0.05, "metallic": 0.0},
    "glass_mirrored": {"color": (0.90, 0.90, 0.90), "roughness": 0.0, "metallic": 1.0},
    
    # Cuero
    "leather_brown": {"color": (0.35, 0.20, 0.10), "roughness": 0.6, "metallic": 0.0},
    "leather_black": {"color": (0.10, 0.08, 0.06), "roughness": 0.55, "metallic": 0.0},
    "leather_red": {"color": (0.50, 0.10, 0.08), "roughness": 0.6, "metallic": 0.0},
    
    # Goma
    "rubber_black": {"color": (0.05, 0.05, 0.05), "roughness": 0.95, "metallic": 0.0},
    "rubber_white": {"color": (0.85, 0.85, 0.85), "roughness": 0.9, "metallic": 0.0},
    "rubber_red": {"color": (0.70, 0.10, 0.10), "roughness": 0.85, "metallic": 0.0},
    
    # Concreto
    "concrete_light": {"color": (0.70, 0.68, 0.65), "roughness": 0.9, "metallic": 0.0},
    "concrete_dark": {"color": (0.35, 0.33, 0.30), "roughness": 0.85, "metallic": 0.0},
    
    # Otros
    "paper_white": {"color": (0.95, 0.93, 0.90), "roughness": 0.8, "metallic": 0.0},
    "paper_cardboard": {"color": (0.60, 0.45, 0.25), "roughness": 0.85, "metallic": 0.0},
    "ceramic_white": {"color": (0.95, 0.95, 0.93), "roughness": 0.15, "metallic": 0.0},
    "ceramic_colored": {"color": (0.20, 0.50, 0.80), "roughness": 0.2, "metallic": 0.0},
    "bamboo": {"color": (0.70, 0.60, 0.35), "roughness": 0.65, "metallic": 0.0},
    "cork": {"color": (0.60, 0.45, 0.25), "roughness": 0.9, "metallic": 0.0},
}


def create_pbr_material(name, material_type, params=None):
    """
    Crear material PBR desde catálogo.
    
    Args:
        name: Nombre del material
        material_type: Tipo de material (del catálogo)
        params: Parámetros adicionales (opcional)
    
    Returns:
        Material creado
    """
    if material_type not in PBR_MATERIALS:
        raise ValueError(f"Material no encontrado: {material_type}")
    
    preset = PBR_MATERIALS[material_type]
    
    # Crear material
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    
    # Aplicar propiedades base
    bsdf.inputs["Base Color"].default_value = (*preset["color"], 1.0)
    bsdf.inputs["Roughness"].default_value = preset["roughness"]
    bsdf.inputs["Metallic"].default_value = preset["metallic"]
    
    # Aplicar parámetros adicionales
    if params:
        for key, value in params.items():
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = value
    
    return mat


def create_custom_material(name, color, roughness=0.5, metallic=0.0, 
                          emission=None, alpha=None):
    """
    Crear material personalizado.
    
    Args:
        name: Nombre del material
        color: Tupla RGBA (0-1)
        roughness: Rugosidad (0-1)
        metallic: Metalicidad (0-1)
        emission: Tupla RGBA para emisión (opcional)
        alpha: Transparencia (opcional)
    
    Returns:
        Material creado
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    
    bsdf.inputs["Base Color"].default_value = (*color, 1.0) if len(color) == 3 else color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    
    if emission:
        em = mat.node_tree.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*emission, 1.0) if len(emission) == 3 else emission
        em.inputs["Strength"].default_value = 3.0
        output = mat.node_tree.nodes["Material Output"]
        mat.node_tree.links.new(em.outputs["Emission"], output.inputs["Surface"])
    
    if alpha is not None:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else None
    
    return mat


# ═══════════════════════════════════════════════════════════════
# TEXTURAS PROCEDURALES
# ═══════════════════════════════════════════════════════════════

PROCEDURAL_TEXTURES = {
    "checker": {"description": "Tablero de ajedrez"},
    "brick": {"description": "Ladrillo"},
    "wood_grain": {"description": "Veta de madera"},
    "marble": {"description": "Vetas de mármol"},
    "noise": {"description": "Ruido Perlin"},
    "voronoi": {"description": "Patrón Voronoi"},
    "wave": {"description": "Ondas"},
    "gradient": {"description": "Degradado"},
}


def create_procedural_texture(name, texture_type, params=None):
    """
    Crear textura procedural.
    
    Args:
        name: Nombre de la textura
        texture_type: Tipo de textura
        params: Parámetros adicionales
    
    Returns:
        Nodo de textura creado
    """
    if texture_type not in PROCEDURAL_TEXTURES:
        raise ValueError(f"Textura no encontrada: {texture_type}")
    
    # Crear material base si no existe
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Limpiar nodos existentes
    for n in nodes:
        nodes.remove(n)
    
    # Output
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    # BSDF
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    
    # Textura procedural
    tex_node = nodes.new(f"ShaderNodeTex{texture_type.capitalize()}")
    tex_node.location = (0, 0)
    
    # Conectar
    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    return mat


# ═══════════════════════════════════════════════════════════════
# UV UNWRAP
# ═══════════════════════════════════════════════════════════════

def smart_uv_unwrap(obj):
    """
    Aplicar UV unwrap inteligente.
    
    Args:
        obj: Objeto a desenrollar
    
    Returns:
        True si fue exitoso
    """
    if obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return True


def auto_uv_unwrap(obj, method='smart'):
    """
    UV unwrap automático con método seleccionado.
    
    Args:
        obj: Objeto a desenrollar
        method: 'smart', 'cube', 'cylinder', 'sphere'
    """
    if obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    if method == 'smart':
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    elif method == 'cube':
        bpy.ops.uv.cube_project(cube_size=1)
    elif method == 'cylinder':
        bpy.ops.uv.cylinder_project()
    elif method == 'sphere':
        bpy.ops.uv.sphere_project()
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return True


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def apply_material(obj, material_name_or_type, is_preset=True):
    """
    Aplicar material a un objeto.
    
    Args:
        obj: Objeto
        material_name_or_type: Nombre del material o tipo del catálogo
        is_preset: Si es un preset del catálogo
    """
    if is_preset:
        mat = create_pbr_material(f"Mat_{material_name_or_type}", material_name_or_type)
    else:
        mat = bpy.data.materials.get(material_name_or_type)
        if not mat:
            mat = bpy.data.materials.new(material_name_or_type)
    
    obj.data.materials.append(mat)
    return mat


def list_materials(category=None):
    """Listar materiales disponibles"""
    if category:
        # Filtrar por categoría (basado en prefijo)
        return {k: v for k, v in PBR_MATERIALS.items() if k.startswith(category)}
    return PBR_MATERIALS


def get_material_info(mat_name):
    """Obtener información de un material"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        return None
    
    if mat.use_nodes:
        bsdf = None
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf = node
                break
        
        if bsdf:
            return {
                "name": mat.name,
                "color": bsdf.inputs["Base Color"].default_value[:3],
                "roughness": bsdf.inputs["Roughness"].default_value,
                "metallic": bsdf.inputs["Metallic"].default_value,
            }
    
    return {"name": mat.name}
