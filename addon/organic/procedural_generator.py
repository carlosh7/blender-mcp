"""
blender-mcp — Procedural Generator
Generador procedural de objetos complejos.
"""
try:
    import bpy
except ImportError:
    bpy = None

import math


# ═══════════════════════════════════════════════════════════════
# PROCEDURAL OBJECTS
# ═══════════════════════════════════════════════════════════════

def procedural_tree(trunk_height=2.0, crown_radius=1.5, branches=8):
    """
    Generar árbol proceduralmente.
    
    Args:
        trunk_height: Altura del tronco
        crown_radius: Radio de la copa
        branches: Número de ramas
    
    Returns:
        dict con objetos creados
    """
    if bpy is None:
        return None
    
    parts = {}
    
    # Tronco
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=trunk_height, location=(0, 0, trunk_height/2))
    trunk = bpy.context.active_object
    trunk.name = "Tree_Trunk"
    trunk.data.materials.append(bpy.data.materials.get("Wood") or create_wood_material())
    parts["trunk"] = trunk
    
    # Copa (esfera)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=crown_radius, location=(0, 0, trunk_height + crown_radius*0.7))
    crown = bpy.context.active_object
    crown.name = "Tree_Crown"
    crown.scale = (1, 1, 0.8)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    crown.data.materials.append(bpy.data.materials.get("Leaf") or create_leaf_material())
    parts["crown"] = crown
    
    print(f"Árbol procedural: {trunk_height}m alto, {branches} ramas")
    return parts


def procedural_house(rooms=4, floors=1, width=10, depth=8):
    """
    Generar casa proceduralmente.
    
    Args:
        rooms: Número de habitaciones
        floors: Número de pisos
        width: Ancho total
        depth: Profundidad total
    
    Returns:
        dict con objetos creados
    """
    if bpy is None:
        return None
    
    parts = {}
    
    # Estructura base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
    structure = bpy.context.active_object
    structure.name = "House_Structure"
    structure.scale = (width, depth, 3)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    structure.data.materials.append(bpy.data.materials.get("Wall") or create_wall_material())
    parts["structure"] = structure
    
    # Techo
    bpy.ops.mesh.primitive_cone_add(radius1=width*0.7, radius2=0, depth=2, vertices=4, location=(0, 0, 4))
    roof = bpy.context.active_object
    roof.name = "House_Roof"
    roof.rotation_euler = (0, 0, math.radians(45))
    roof.data.materials.append(bpy.data.materials.get("Roof") or create_roof_material())
    parts["roof"] = roof
    
    # Ventanas
    for i in range(rooms):
        x = (i - rooms/2 + 0.5) * (width / rooms)
        bpy.ops.mesh.primitive_cube_add(size=0.8, location=(x, depth/2 + 0.01, 1.5))
        window = bpy.context.active_object
        window.name = f"Window_{i}"
        window.scale = (1, 0.02, 0.8)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        window.data.materials.append(bpy.data.materials.get("Glass") or create_glass_material())
        parts[f"window_{i}"] = window
    
    print(f"Casa procedural: {rooms} habitaciones, {floors} pisos")
    return parts


def procedural_vehicle(body_type="sedan", length=4.5, width=1.8):
    """
    Generar vehículo proceduralmente.
    
    Args:
        body_type: Tipo de carrocería (sedan, suv, truck)
        length: Largo
        width: Ancho
    
    Returns:
        dict con objetos creados
    """
    if bpy is None:
        return None
    
    parts = {}
    
    # Carrocería
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.4))
    body = bpy.context.active_object
    body.name = "Vehicle_Body"
    body.scale = (length, width, 0.4)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    body.data.materials.append(bpy.data.materials.get("Paint") or create_paint_material())
    parts["body"] = body
    
    # Ruedas (4)
    for x in [-length*0.35, length*0.35]:
        for y in [-width*0.4, width*0.4]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, location=(x, y, 0.15))
            wheel = bpy.context.active_object
            wheel.name = "Wheel"
            wheel.rotation_euler = (0, math.pi/2, 0)
            wheel.data.materials.append(bpy.data.materials.get("Rubber") or create_rubber_material())
            parts[f"wheel_{x}_{y}"] = wheel
    
    print(f"Vehículo procedural: {body_type}, {length}m x {width}m")
    return parts


def procedural_robot(height=2.0, arms=2, legs=2):
    """
    Generar robot proceduralmente.
    
    Args:
        height: Altura total
        arms: Número de brazos
        legs: Número de piernas
    
    Returns:
        dict con objetos creados
    """
    if bpy is None:
        return None
    
    parts = {}
    
    # Cuerpo (cilindro metálico)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.8, location=(0, 0, height*0.5))
    body = bpy.context.active_object
    body.name = "Robot_Body"
    body.data.materials.append(bpy.data.materials.get("Metal") or create_metal_material())
    parts["body"] = body
    
    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0, height*0.9))
    head = bpy.context.active_object
    head.name = "Robot_Head"
    head.data.materials.append(bpy.data.materials.get("Metal") or create_metal_material())
    parts["head"] = head
    
    # Ojos (lucen)
    for side in ["L", "R"]:
        x = 0.08 if side == "L" else -0.08
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(x, -0.15, height*0.92))
        eye = bpy.context.active_object
        eye.name = f"Robot_Eye_{side}"
        eye.data.materials.append(bpy.data.materials.get("Emission") or create_emission_material())
        parts[f"eye_{side}"] = eye
    
    # Brazos
    for i in range(arms):
        angle = (i / arms) * math.pi * 2
        x = math.cos(angle) * 0.4
        y = math.sin(angle) * 0.4
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.5, location=(x, y, height*0.6))
        arm = bpy.context.active_object
        arm.name = f"Robot_Arm_{i}"
        arm.data.materials.append(bpy.data.materials.get("Metal") or create_metal_material())
        parts[f"arm_{i}"] = arm
    
    print(f"Robot procedural: {height}m alto, {arms} brazos, {legs} piernas")
    return parts


# ═══════════════════════════════════════════════════════════════
# HELPER MATERIALS
# ═══════════════════════════════════════════════════════════════

def create_wood_material():
    """Crear material madera"""
    mat = bpy.data.materials.new("Wood_Proc")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.45, 0.30, 0.15, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.7
    return mat


def create_leaf_material():
    """Crear material hoja"""
    mat = bpy.data.materials.new("Leaf_Proc")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.5, 0.15, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    return mat


def create_wall_material():
    """Crear material pared"""
    mat = bpy.data.materials.new("Wall_Proc")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.82, 0.78, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5
    return mat


def create_roof_material():
    """Crear material techo"""
    mat = bpy.data.materials.new("Roof_Proc")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.2, 0.1, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    return mat


def create_glass_material():
    """Crear material vidrio"""
    mat = bpy.data.materials.new("Glass_Proc")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.9, 1.0, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.0
    mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.3
    return mat


def create_paint_material():
    """Crear material pintura"""
    mat = bpy.data.materials.new("Paint_Proc")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.8
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.2
    return mat


def create_rubber_material():
    """Crear material goma"""
    mat = bpy.data.materials.new("Rubber_Proc")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
    return mat


def create_metal_material():
    """Crear material metal"""
    mat = bpy.data.materials.new("Metal_Proc")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.1
    return mat


def create_emission_material():
    """Crear material emisión"""
    mat = bpy.data.materials.new("Emission_Proc")
    mat.use_nodes = True
    emission = mat.node_tree.nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (1, 0.5, 0, 1)
    emission.inputs["Strength"].default_value = 5.0
    output = mat.node_tree.nodes["Material Output"]
    mat.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return mat


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_procedural_types():
    """Listar tipos de objetos procedurales"""
    return {
        "tree": "Árbol procedural",
        "house": "Casa procedural",
        "vehicle": "Vehículo procedural",
        "robot": "Robot procedural",
    }
