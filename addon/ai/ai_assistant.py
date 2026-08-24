"""
blender-mcp — AI Assistant
Asistente IA: Text→3D, Image→3D, Auto-rig, Voice Control.
"""

import bpy

# ═══════════════════════════════════════════════════════════════
# TEXT TO 3D
# ═══════════════════════════════════════════════════════════════


def text_to_3d(description, style="realistic"):
    """
    Crear modelo 3D desde descripción textual.

    Args:
        description: Descripción del objeto
        style: Estilo (realistic, cartoon, anime, etc.)

    Returns:
        Objeto creado o None
    """
    # Parsear descripción
    parsed = parse_description(description)

    # Seleccionar estrategia basada en tipo
    obj_type = parsed.get("type", "unknown")

    if obj_type in ["furniture", "chair", "table", "sofa"]:
        return create_furniture(parsed, style)
    elif obj_type in ["vehicle", "car", "bike"]:
        return create_vehicle(parsed, style)
    elif obj_type in ["building", "house", "room"]:
        return create_building(parsed, style)
    elif obj_type in ["animal", "dog", "cat"]:
        return create_animal(parsed, style)
    elif obj_type in ["character", "person", "human"]:
        return create_character_from_text(parsed, style)
    else:
        return create_generic(parsed, style)


def parse_description(description):
    """Parsear descripción textual"""
    # Análisis simple de keywords
    keywords = description.lower().split()

    result = {
        "raw": description,
        "type": "unknown",
        "attributes": {},
    }

    # Detectar tipo
    type_keywords = {
        "chair": "furniture",
        "table": "furniture",
        "sofa": "furniture",
        "bed": "furniture",
        "car": "vehicle",
        "bike": "vehicle",
        "house": "building",
        "room": "building",
        "dog": "animal",
        "cat": "animal",
        "person": "character",
        "human": "character",
    }

    for keyword, obj_type in type_keywords.items():
        if keyword in keywords:
            result["type"] = obj_type
            break

    # Detectar color
    colors = {
        "red": (0.8, 0.1, 0.1),
        "blue": (0.1, 0.1, 0.8),
        "green": (0.1, 0.7, 0.1),
        "yellow": (0.9, 0.9, 0.1),
        "black": (0.05, 0.05, 0.05),
        "white": (0.9, 0.9, 0.9),
    }

    for keyword, color in colors.items():
        if keyword in keywords:
            result["attributes"]["color"] = color
            break

    # Detectar tamaño
    size_keywords = {
        "big": 2.0,
        "large": 2.0,
        "small": 0.5,
        "tiny": 0.3,
    }

    for keyword, size in size_keywords.items():
        if keyword in keywords:
            result["attributes"]["size"] = size
            break

    return result


def create_furniture(parsed, style):
    """Crear mueble desde descripción"""
    from ..core.mesh_engine import create_advanced_primitive

    # Crear base (cubo)
    size = parsed["attributes"].get("size", 1.0)
    obj = create_advanced_primitive("cube", {"size": size})

    # Aplicar color
    color = parsed["attributes"].get("color", (0.5, 0.3, 0.15))
    from ..core.texture_engine import create_custom_material

    mat = create_custom_material("FurnitureMat", color, roughness=0.6)
    obj.data.materials.append(mat)

    print(f"Mueble creado desde descripción: '{parsed['raw']}'")
    return obj


def create_vehicle(parsed, style):
    """Crear vehículo desde descripción"""
    # Crear carrocería básica
    size = parsed["attributes"].get("size", 1.0)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.3))
    body = bpy.context.active_object
    body.name = "VehicleBody"
    body.scale = (size * 1.5, size * 0.6, size * 0.4)
    bpy.ops.object.transform_apply(rotation=False, scale=True)

    color = parsed["attributes"].get("color", (0.8, 0.1, 0.1))
    from ..core.texture_engine import create_custom_material

    mat = create_custom_material("VehicleMat", color, roughness=0.2, metallic=0.8)
    body.data.materials.append(mat)

    # Agregar ruedas
    for x in [-0.6, 0.6]:
        for y in [-0.4, 0.4]:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.15, depth=0.1, location=(x * size, y * size, 0.15)
            )
            wheel = bpy.context.active_object
            wheel.name = "Wheel"
            wheel.rotation_euler = (0, 0, 0)
            wheel.data.materials.append(mat)

    print(f"Vehículo creado: '{parsed['raw']}'")
    return body


def create_building(parsed, style):
    """Crear edificio desde descripción"""
    size = parsed["attributes"].get("size", 1.0)

    # Crear estructura básica
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, size))
    building = bpy.context.active_object
    building.name = "Building"
    building.scale = (size, size, size)
    bpy.ops.object.transform_apply(rotation=False, scale=True)

    from ..core.texture_engine import create_pbr_material

    mat = create_pbr_material("BuildingMat", "concrete_light")
    building.data.materials.append(mat)

    print(f"Edificio creado: '{parsed['raw']}'")
    return building


def create_animal(parsed, style):
    """Crear animal desde descripción"""
    from ..organic.character_gen import create_character

    animal_type = parsed.get("type", "quadruped")
    parts = create_character(animal_type, parsed.get("attributes", {}))

    if parts:
        print(f"Animal creado: '{parsed['raw']}'")
        return list(parts.values())[0] if parts else None
    return None


def create_character_from_text(parsed, style):
    """Crear personaje desde descripción"""
    from ..organic.character_gen import create_character

    parts = create_character("humanoid", parsed.get("attributes", {}))

    if parts:
        print(f"Personaje creado: '{parsed['raw']}'")
        return list(parts.values())[0] if parts else None
    return None


def create_generic(parsed, style):
    """Crear objeto genérico"""
    from ..core.mesh_engine import create_advanced_primitive

    size = parsed["attributes"].get("size", 1.0)
    obj = create_advanced_primitive("cube", {"size": size})

    print(f"Objeto genérico creado: '{parsed['raw']}'")
    return obj


# ═══════════════════════════════════════════════════════════════
# IMAGE TO 3D (placeholder - requiere API externa)
# ═══════════════════════════════════════════════════════════════


def image_to_3d(image_path, style="realistic"):
    """
    Crear modelo 3D desde imagen.

    NOTA: Requiere integración con API externa (Meshy, Tripo, etc.)
    """
    print(f"Image → 3D: {image_path}")
    print("NOTA: Requiere integración con API de AI 3D")

    # Placeholder - crear objeto genérico
    from ..core.mesh_engine import create_advanced_primitive

    return create_advanced_primitive("cube", {"size": 1})


# ═══════════════════════════════════════════════════════════════
# AUTO-RIG
# ═══════════════════════════════════════════════════════════════


def auto_rig(mesh_obj, rig_type="humanoid"):
    """
    Auto-rig un objeto mesh.
    """
    from ..core.rig_engine import automatic_weights, create_humanoid_rig, create_quadruped_rig

    if rig_type == "humanoid":
        arm_obj = create_humanoid_rig("AutoRig", mesh_obj.location)
    elif rig_type == "quadruped":
        arm_obj = create_quadruped_rig("AutoRig", mesh_obj.location)
    else:
        print(f"Tipo de rig no soportado: {rig_type}")
        return None

    # Asignar pesos automáticos
    automatic_weights(mesh_obj, arm_obj)

    print(f"Auto-rig completado: {mesh_obj.name} → {arm_obj.name}")
    return arm_obj


# ═══════════════════════════════════════════════════════════════
# VOICE CONTROL (placeholder)
# ═══════════════════════════════════════════════════════════════


def voice_control(audio_path):
    """
    Procesar comando de voz.

    NOTA: Requiere integración con STT (Whisper, etc.)
    """
    print(f"Voice control: {audio_path}")
    print("NOTA: Requiere integración con STT (Whisper, etc.)")

    # Placeholder
    return {"action": "unknown", "confidence": 0}


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def list_ai_features():
    """Listar features de IA disponibles"""
    return {
        "text_to_3d": "Crear modelo desde descripción",
        "image_to_3d": "Crear modelo desde imagen (requiere API)",
        "auto_rig": "Rigging automático",
        "voice_control": "Control por voz (requiere STT)",
    }
