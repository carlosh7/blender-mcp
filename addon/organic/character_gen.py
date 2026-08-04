"""
blender-mcp — Character Generator
Generador de personajes: humanoid, quadruped, avian, reptile, fantasy.
"""
import bpy
import math
from mathutils import Vector


# ═══════════════════════════════════════════════════════════════
# PLANTILLAS DE PERSONAJES
# ═══════════════════════════════════════════════════════════════

CHARACTER_TEMPLATES = {
    "humanoid": {
        "description": "Personaje humanoide",
        "body_parts": ["head", "torso", "arms", "legs", "hands", "feet"],
        "default_height": 1.8,
        "default_proportions": {
            "head_ratio": 0.12,      # 12% de la altura
            "torso_ratio": 0.30,     # 30% de la altura
            "leg_ratio": 0.45,       # 45% de la altura
            "arm_ratio": 0.40,       # 40% de la altura
        },
    },
    "quadruped": {
        "description": "Animal cuadrúpedo (perro, gato, etc.)",
        "body_parts": ["head", "body", "front_legs", "back_legs", "tail"],
        "default_height": 0.5,
        "default_proportions": {
            "head_ratio": 0.15,
            "body_ratio": 0.50,
            "leg_ratio": 0.35,
        },
    },
    "avian": {
        "description": "Ave",
        "body_parts": ["head", "body", "wings", "legs", "beak"],
        "default_height": 0.3,
        "default_proportions": {
            "head_ratio": 0.10,
            "body_ratio": 0.50,
            "wing_ratio": 0.60,
        },
    },
    "reptile": {
        "description": "Reptil (lagarto, serpiente)",
        "body_parts": ["head", "body", "legs", "tail"],
        "default_height": 0.2,
        "default_proportions": {
            "head_ratio": 0.10,
            "body_ratio": 0.40,
            "tail_ratio": 0.50,
        },
    },
    "fantasy": {
        "description": "Criatura fantástica (dragón, fénix, etc.)",
        "body_parts": ["head", "body", "wings", "legs", "tail"],
        "default_height": 2.0,
        "default_proportions": {
            "head_ratio": 0.15,
            "body_ratio": 0.45,
            "wing_ratio": 0.80,
            "tail_ratio": 0.60,
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# GENERADOR DE PERSONAJES
# ═══════════════════════════════════════════════════════════════

def create_character(character_type, params=None):
    """
    Crear personaje basado en plantilla.
    
    Args:
        character_type: Tipo de personaje (humanoid, quadruped, etc.)
        params: Parámetros personalizados
    
    Returns:
        Diccionario con objetos creados
    """
    if character_type not in CHARACTER_TEMPLATES:
        raise ValueError(f"Tipo no soportado: {character_type}")
    
    template = CHARACTER_TEMPLATES[character_type]
    
    if params is None:
        params = {}
    
    # Obtener parámetros
    height = params.get("height", template["default_height"])
    proportions = template["default_proportions"]
    
    # Crear cuerpo
    if character_type == "humanoid":
        return _create_humanoid(height, proportions, params)
    elif character_type == "quadruped":
        return _create_quadruped(height, proportions, params)
    elif character_type == "avian":
        return _create_avian(height, proportions, params)
    elif character_type == "reptile":
        return _create_reptile(height, proportions, params)
    elif character_type == "fantasy":
        return _create_fantasy(height, proportions, params)
    
    return {}


def _create_humanoid(height, proportions, params):
    """Crear personaje humanoid REALISTA con ropa, pelo, cara"""
    color = params.get("color", (0.8, 0.6, 0.5))
    cloth_color = params.get("cloth_color", (0.2, 0.2, 0.5))
    hair_color = params.get("hair_color", (0.2, 0.15, 0.1))
    
    # Materiales
    skin_mat = bpy.data.materials.new("Skin")
    skin_mat.use_nodes = True
    skin_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    skin_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.7
    
    cloth_mat = bpy.data.materials.new("Cloth")
    cloth_mat.use_nodes = True
    cloth_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*cloth_color, 1)
    cloth_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    
    hair_mat = bpy.data.materials.new("Hair")
    hair_mat.use_nodes = True
    hair_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*hair_color, 1)
    hair_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    
    eye_mat = bpy.data.materials.new("Eye")
    eye_mat.use_nodes = True
    eye_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
    eye_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.0
    
    parts = {}
    
    # === CUERPO ===
    # Torso (con forma más realista)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height * 0.55))
    torso = bpy.context.active_object
    torso.name = "Torso"
    torso.scale = (0.18, 0.12, height * 0.25)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    torso.data.materials.append(cloth_mat)
    parts["torso"] = torso
    
    # Cadera
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height * 0.35))
    hips = bpy.context.active_object
    hips.name = "Hips"
    hips.scale = (0.20, 0.13, height * 0.10)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    hips.data.materials.append(cloth_mat)
    parts["hips"] = hips
    
    # Cabeza (más realista)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=height * 0.08, location=(0, 0, height * 0.88))
    head = bpy.context.active_object
    head.name = "Head"
    head.scale = (1, 1.1, 1)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    head.data.materials.append(skin_mat)
    parts["head"] = head
    
    # Cuello
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.08, location=(0, 0, height * 0.78))
    neck = bpy.context.active_object
    neck.name = "Neck"
    neck.data.materials.append(skin_mat)
    parts["neck"] = neck
    
    # === CARA ===
    # Ojos
    for side in ["L", "R"]:
        x = 0.03 if side == "L" else -0.03
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=(x, -0.06, height * 0.90))
        eye = bpy.context.active_object
        eye.name = f"Eye_{side}"
        eye.data.materials.append(eye_mat)
        parts[f"eye_{side}"] = eye
    
    # Nariz
    bpy.ops.mesh.primitive_cone_add(radius1=0.015, radius2=0, depth=0.03, vertices=8, location=(0, -0.07, height * 0.87))
    nose = bpy.context.active_object
    nose.name = "Nose"
    nose.rotation_euler = (math.radians(90), 0, 0)
    nose.data.materials.append(skin_mat)
    parts["nose"] = nose
    
    # Boca
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.07, height * 0.84))
    mouth = bpy.context.active_object
    mouth.name = "Mouth"
    mouth.scale = (0.025, 0.005, 0.005)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    mouth.data.materials.append(skin_mat)
    parts["mouth"] = mouth
    
    # === PELO ===
    bpy.ops.mesh.primitive_uv_sphere_add(radius=height * 0.085, location=(0, 0.01, height * 0.92))
    hair = bpy.context.active_object
    hair.name = "Hair"
    hair.scale = (1.05, 1.15, 1.1)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    hair.data.materials.append(hair_mat)
    parts["hair"] = hair
    
    # === BRAZOS ===
    for side in ["L", "R"]:
        x = 0.22 if side == "L" else -0.22
        
        # Hombro
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(x, 0, height * 0.72))
        shoulder = bpy.context.active_object
        shoulder.name = f"Shoulder_{side}"
        shoulder.data.materials.append(skin_mat)
        parts[f"shoulder_{side}"] = shoulder
        
        # Brazo superior
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.25, location=(x, 0, height * 0.60))
        upper = bpy.context.active_object
        upper.name = f"UpperArm_{side}"
        upper.data.materials.append(skin_mat)
        parts[f"upper_arm_{side}"] = upper
        
        # Codo
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(x, 0, height * 0.48))
        elbow = bpy.context.active_object
        elbow.name = f"Elbow_{side}"
        elbow.data.materials.append(skin_mat)
        parts[f"elbow_{side}"] = elbow
        
        # Brazo inferior
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.22, location=(x, 0, height * 0.36))
        lower = bpy.context.active_object
        lower.name = f"LowerArm_{side}"
        lower.data.materials.append(skin_mat)
        parts[f"lower_arm_{side}"] = lower
        
        # Mano
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(x, 0, height * 0.24))
        hand = bpy.context.active_object
        hand.name = f"Hand_{side}"
        hand.scale = (0.8, 1.2, 0.6)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        hand.data.materials.append(skin_mat)
        parts[f"hand_{side}"] = hand
        
        # Dedos (5 por mano)
        for finger in range(5):
            angle = (finger - 2) * 0.15
            fx = x + math.cos(angle) * 0.02
            fy = -0.02
            fz = height * 0.22
            bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.03, location=(fx, fy, fz))
            finger_obj = bpy.context.active_object
            finger_obj.name = f"Finger_{side}_{finger}"
            finger_obj.data.materials.append(skin_mat)
            parts[f"finger_{side}_{finger}"] = finger_obj
    
    # === PIERNAS ===
    for side in ["L", "R"]:
        x = 0.08 if side == "L" else -0.08
        
        # Muslo
        bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.35, location=(x, 0, height * 0.22))
        thigh = bpy.context.active_object
        thigh.name = f"Thigh_{side}"
        thigh.data.materials.append(cloth_mat)
        parts[f"thigh_{side}"] = thigh
        
        # Rodilla
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(x, 0, height * 0.05))
        knee = bpy.context.active_object
        knee.name = f"Knee_{side}"
        knee.data.materials.append(skin_mat)
        parts[f"knee_{side}"] = knee
        
        # Pantorrilla
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.30, location=(x, 0, -0.10))
        calf = bpy.context.active_object
        calf.name = f"Calf_{side}"
        calf.data.materials.append(skin_mat)
        parts[f"calf_{side}"] = calf
        
        # Pie
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.03, -0.25))
        foot = bpy.context.active_object
        foot.name = f"Foot_{side}"
        foot.scale = (0.04, 0.07, 0.02)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        foot.data.materials.append(cloth_mat)
        parts[f"foot_{side}"] = foot
        
        # Dedos del pie (5)
        for toe in range(5):
            angle = (toe - 2) * 0.1
            tx = x + math.cos(angle) * 0.01
            ty = 0.05
            tz = -0.26
            bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=0.02, location=(tx, ty, tz))
            toe_obj = bpy.context.active_object
            toe_obj.name = f"Toe_{side}_{toe}"
            toe_obj.data.materials.append(skin_mat)
            parts[f"toe_{side}_{toe}"] = toe_obj
    
    # === OREJAS ===
    for side in ["L", "R"]:
        x = 0.08 if side == "L" else -0.08
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=(x, 0.02, height * 0.92))
        ear = bpy.context.active_object
        ear.name = f"Ear_{side}"
        ear.scale = (0.6, 1.2, 0.8)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        ear.data.materials.append(skin_mat)
        parts[f"ear_{side}"] = ear
    
    print(f"Personaje REALISTA creado: {len(parts)} partes, altura {height}m")
    print(f"  - Cuerpo: torso, cadera, cuello")
    print(f"  - Cara: ojos, nariz, boca, orejas")
    print(f"  - Pelo: esfera estilizada")
    print(f"  - Brazos: hombro, brazo, codo, antebrazo, mano, 5 dedos")
    print(f"  - Piernas: muslo, rodilla, pantorrilla, pie, 5 dedos")
    return parts


def _create_quadruped(height, proportions, params):
    """Crear animal cuadrúpedo"""
    color = params.get("color", (0.5, 0.35, 0.2))  # Pelo marrón
    
    # Material pelo
    fur_mat = bpy.data.materials.new("Fur")
    fur_mat.use_nodes = True
    fur_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    fur_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    
    parts = {}
    
    # Cuerpo
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height * 0.5))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (0.3, 0.6, 0.25)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    body.data.materials.append(fur_mat)
    parts["body"] = body
    
    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0.5, height * 0.5))
    head = bpy.context.active_object
    head.name = "Head"
    head.scale = (1, 1.2, 0.9)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    head.data.materials.append(fur_mat)
    parts["head"] = head
    
    # Patas (4)
    leg_positions = [
        (0.15, 0.35, 0.15),   # Front-Left
        (-0.15, 0.35, 0.15),  # Front-Right
        (0.15, -0.35, 0.15),  # Back-Left
        (-0.15, -0.35, 0.15), # Back-Right
    ]
    
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.3, location=pos)
        leg = bpy.context.active_object
        leg.name = f"Leg_{i}"
        leg.data.materials.append(fur_mat)
        parts[f"leg_{i}"] = leg
    
    # Cola
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.2, location=(0, -0.6, height * 0.55))
    tail = bpy.context.active_object
    tail.name = "Tail"
    tail.rotation_euler = (math.radians(30), 0, 0)
    tail.data.materials.append(fur_mat)
    parts["tail"] = tail
    
    print(f"Animal cuadrúpedo creado: {len(parts)} partes")
    return parts


def _create_avian(height, proportions, params):
    """Crear ave"""
    color = params.get("color", (0.8, 0.7, 0.1))  # Amarillo (pollito)
    
    feather_mat = bpy.data.materials.new("Feather")
    feather_mat.use_nodes = True
    feather_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    feather_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    
    parts = {}
    
    # Cuerpo
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, height * 0.5))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (1, 1.2, 0.9)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    body.data.materials.append(feather_mat)
    parts["body"] = body
    
    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0.15, height * 0.55))
    head = bpy.context.active_object
    head.name = "Head"
    head.data.materials.append(feather_mat)
    parts["head"] = head
    
    # Pico
    bpy.ops.mesh.primitive_cone_add(radius1=0.03, radius2=0, depth=0.08,
                                    location=(0, 0.22, height * 0.55))
    beak = bpy.context.active_object
    beak.name = "Beak"
    beak.rotation_euler = (math.radians(90), 0, 0)
    mat_orange = bpy.data.materials.new("BeakColor")
    mat_orange.use_nodes = True
    mat_orange.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.5, 0.1, 1)
    beak.data.materials.append(mat_orange)
    parts["beak"] = beak
    
    # Alas
    for side in ["L", "R"]:
        x_sign = 1 if side == "L" else -1
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_sign * 0.2, 0, height * 0.5))
        wing = bpy.context.active_object
        wing.name = f"Wing_{side}"
        wing.scale = (0.25, 0.05, 0.15)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        wing.rotation_euler = (0, x_sign * math.radians(20), 0)
        wing.data.materials.append(feather_mat)
        parts[f"wing_{side}"] = wing
    
    # Patas
    for side in ["L", "R"]:
        x_sign = 1 if side == "L" else -1
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.15,
                                           location=(x_sign * 0.05, 0, height * 0.35))
        leg = bpy.context.active_object
        leg.name = f"Leg_{side}"
        mat_leg = bpy.data.materials.new("LegColor")
        mat_leg.use_nodes = True
        mat_leg.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.6, 0.2, 1)
        leg.data.materials.append(mat_leg)
        parts[f"leg_{side}"] = leg
    
    print(f"Ave creada: {len(parts)} partes")
    return parts


def _create_reptile(height, proportions, params):
    """Crear reptil (lagarto simplificado)"""
    color = params.get("color", (0.3, 0.5, 0.2))  # Verde
    
    scale_mat = bpy.data.materials.new("Scales")
    scale_mat.use_nodes = True
    scale_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    scale_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    
    parts = {}
    
    # Cuerpo (cilindro alargado)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.4, location=(0, 0, height * 0.3))
    body = bpy.context.active_object
    body.name = "Body"
    body.rotation_euler = (math.radians(90), 0, 0)
    body.data.materials.append(scale_mat)
    parts["body"] = body
    
    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0, 0.25, height * 0.3))
    head = bpy.context.active_object
    head.name = "Head"
    head.scale = (1, 1.3, 0.8)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    head.data.materials.append(scale_mat)
    parts["head"] = head
    
    # Cola (cilindro fino)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.5, location=(0, -0.3, height * 0.3))
    tail = bpy.context.active_object
    tail.name = "Tail"
    tail.rotation_euler = (math.radians(90), 0, 0)
    tail.data.materials.append(scale_mat)
    parts["tail"] = tail
    
    # Patas (4)
    leg_positions = [
        (0.1, 0.1, height * 0.15),
        (-0.1, 0.1, height * 0.15),
        (0.1, -0.1, height * 0.15),
        (-0.1, -0.1, height * 0.15),
    ]
    
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.1, location=pos)
        leg = bpy.context.active_object
        leg.name = f"Leg_{i}"
        leg.data.materials.append(scale_mat)
        parts[f"leg_{i}"] = leg
    
    print(f"Reptil creado: {len(parts)} partes")
    return parts


def _create_fantasy(height, proportions, params):
    """Crear criatura fantástica (dragón simplificado)"""
    color = params.get("color", (0.6, 0.1, 0.1))  # Rojo fuego
    
    scale_mat = bpy.data.materials.new("DragonScale")
    scale_mat.use_nodes = True
    scale_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    scale_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.4
    scale_mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.3
    
    parts = {}
    
    # Cuerpo
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, height * 0.4))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (1, 1.5, 0.8)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    body.data.materials.append(scale_mat)
    parts["body"] = body
    
    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0.4, height * 0.5))
    head = bpy.context.active_object
    head.name = "Head"
    head.data.materials.append(scale_mat)
    parts["head"] = head
    
    # Cuernos
    for side in ["L", "R"]:
        x_sign = 1 if side == "L" else -1
        bpy.ops.mesh.primitive_cone_add(radius1=0.02, radius2=0, depth=0.1,
                                        location=(x_sign * 0.08, 0.35, height * 0.6))
        horn = bpy.context.active_object
        horn.name = f"Horn_{side}"
        horn.rotation_euler = (math.radians(30), 0, x_sign * math.radians(20))
        mat_horn = bpy.data.materials.new("HornColor")
        mat_horn.use_nodes = True
        mat_horn.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.2, 1)
        horn.data.materials.append(mat_horn)
        parts[f"horn_{side}"] = horn
    
    # Alas
    for side in ["L", "R"]:
        x_sign = 1 if side == "L" else -1
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_sign * 0.4, 0, height * 0.5))
        wing = bpy.context.active_object
        wing.name = f"Wing_{side}"
        wing.scale = (0.5, 0.02, 0.3)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        wing.data.materials.append(scale_mat)
        parts[f"wing_{side}"] = wing
    
    # Cola
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.6, location=(0, -0.5, height * 0.35))
    tail = bpy.context.active_object
    tail.name = "Tail"
    tail.rotation_euler = (math.radians(45), 0, 0)
    tail.data.materials.append(scale_mat)
    parts["tail"] = tail
    
    print(f"Criatura fantástica creada: {len(parts)} partes")
    return parts


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_character_types():
    """Listar tipos de personajes disponibles"""
    return {k: v["description"] for k, v in CHARACTER_TEMPLATES.items()}


def get_character_info(parts):
    """Obtener información del personaje creado"""
    info = {
        "total_parts": len(parts),
        "parts": list(parts.keys()),
    }
    return info
