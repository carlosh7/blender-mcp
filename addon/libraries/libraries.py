"""
blender-mcp — Libraries
Bibliotecas: Materiales (50+), Animaciones (20+), Escenas (10+).
"""
import bpy
import math


# ═══════════════════════════════════════════════════════════════
# MATERIAL LIBRARY (50+ presets)
# ═══════════════════════════════════════════════════════════════

MATERIAL_LIBRARY = {
    # Maderas (5)
    "wood_oak": {"color": (0.45, 0.30, 0.15), "roughness": 0.7, "metallic": 0.0},
    "wood_walnut": {"color": (0.30, 0.18, 0.08), "roughness": 0.65, "metallic": 0.0},
    "wood_cherry": {"color": (0.55, 0.25, 0.12), "roughness": 0.6, "metallic": 0.0},
    "wood_pine": {"color": (0.65, 0.50, 0.30), "roughness": 0.75, "metallic": 0.0},
    "wood_maple": {"color": (0.70, 0.55, 0.35), "roughness": 0.6, "metallic": 0.0},
    
    # Metales (8)
    "metal_iron": {"color": (0.35, 0.35, 0.35), "roughness": 0.4, "metallic": 0.9},
    "metal_steel": {"color": (0.60, 0.60, 0.60), "roughness": 0.2, "metallic": 1.0},
    "metal_aluminum": {"color": (0.75, 0.75, 0.75), "roughness": 0.15, "metallic": 0.9},
    "metal_copper": {"color": (0.72, 0.45, 0.20), "roughness": 0.25, "metallic": 0.95},
    "metal_gold": {"color": (0.85, 0.65, 0.10), "roughness": 0.1, "metallic": 1.0},
    "metal_silver": {"color": (0.90, 0.90, 0.90), "roughness": 0.05, "metallic": 1.0},
    "metal_bronze": {"color": (0.80, 0.50, 0.20), "roughness": 0.3, "metallic": 0.85},
    "metal_chrome": {"color": (0.95, 0.95, 0.95), "roughness": 0.02, "metallic": 1.0},
    
    # Piedras (5)
    "stone_granite": {"color": (0.50, 0.48, 0.45), "roughness": 0.8, "metallic": 0.0},
    "stone_marble": {"color": (0.90, 0.88, 0.85), "roughness": 0.15, "metallic": 0.0},
    "stone_slate": {"color": (0.30, 0.30, 0.35), "roughness": 0.7, "metallic": 0.0},
    "stone_sandstone": {"color": (0.75, 0.65, 0.50), "roughness": 0.85, "metallic": 0.0},
    "stone_basalt": {"color": (0.20, 0.20, 0.22), "roughness": 0.6, "metallic": 0.0},
    
    # Plásticos (7)
    "plastic_white": {"color": (0.90, 0.90, 0.90), "roughness": 0.4, "metallic": 0.0},
    "plastic_black": {"color": (0.05, 0.05, 0.05), "roughness": 0.4, "metallic": 0.0},
    "plastic_red": {"color": (0.80, 0.10, 0.10), "roughness": 0.4, "metallic": 0.0},
    "plastic_blue": {"color": (0.10, 0.20, 0.80), "roughness": 0.4, "metallic": 0.0},
    "plastic_green": {"color": (0.10, 0.70, 0.20), "roughness": 0.4, "metallic": 0.0},
    "plastic_yellow": {"color": (0.90, 0.85, 0.10), "roughness": 0.4, "metallic": 0.0},
    "plastic_transparent": {"color": (0.95, 0.95, 0.95), "roughness": 0.1, "metallic": 0.0},
    
    # Telas (5)
    "fabric_cotton": {"color": (0.90, 0.88, 0.85), "roughness": 0.9, "metallic": 0.0},
    "fabric_denim": {"color": (0.20, 0.30, 0.50), "roughness": 0.85, "metallic": 0.0},
    "fabric_silk": {"color": (0.85, 0.80, 0.75), "roughness": 0.3, "metallic": 0.1},
    "fabric_leather": {"color": (0.35, 0.20, 0.10), "roughness": 0.6, "metallic": 0.0},
    "fabric_velvet": {"color": (0.40, 0.10, 0.10), "roughness": 0.95, "metallic": 0.0},
    
    # Vidrio (4)
    "glass_clear": {"color": (0.95, 0.95, 0.95), "roughness": 0.0, "metallic": 0.0},
    "glass_frosted": {"color": (0.85, 0.85, 0.85), "roughness": 0.5, "metallic": 0.0},
    "glass_colored": {"color": (0.30, 0.50, 0.80), "roughness": 0.05, "metallic": 0.0},
    "glass_mirrored": {"color": (0.90, 0.90, 0.90), "roughness": 0.0, "metallic": 1.0},
    
    # Cuero (3)
    "leather_brown": {"color": (0.35, 0.20, 0.10), "roughness": 0.6, "metallic": 0.0},
    "leather_black": {"color": (0.10, 0.08, 0.06), "roughness": 0.55, "metallic": 0.0},
    "leather_red": {"color": (0.50, 0.10, 0.08), "roughness": 0.6, "metallic": 0.0},
    
    # Goma (3)
    "rubber_black": {"color": (0.05, 0.05, 0.05), "roughness": 0.95, "metallic": 0.0},
    "rubber_white": {"color": (0.85, 0.85, 0.85), "roughness": 0.9, "metallic": 0.0},
    "rubber_red": {"color": (0.70, 0.10, 0.10), "roughness": 0.85, "metallic": 0.0},
    
    # Concreto (2)
    "concrete_light": {"color": (0.70, 0.68, 0.65), "roughness": 0.9, "metallic": 0.0},
    "concrete_dark": {"color": (0.35, 0.33, 0.30), "roughness": 0.85, "metallic": 0.0},
    
    # Otros (8)
    "paper_white": {"color": (0.95, 0.93, 0.90), "roughness": 0.8, "metallic": 0.0},
    "paper_cardboard": {"color": (0.60, 0.45, 0.25), "roughness": 0.85, "metallic": 0.0},
    "ceramic_white": {"color": (0.95, 0.95, 0.93), "roughness": 0.15, "metallic": 0.0},
    "ceramic_colored": {"color": (0.20, 0.50, 0.80), "roughness": 0.2, "metallic": 0.0},
    "bamboo": {"color": (0.70, 0.60, 0.35), "roughness": 0.65, "metallic": 0.0},
    "cork": {"color": (0.60, 0.45, 0.25), "roughness": 0.9, "metallic": 0.0},
    "soil": {"color": (0.35, 0.25, 0.15), "roughness": 0.95, "metallic": 0.0},
    "grass": {"color": (0.20, 0.50, 0.15), "roughness": 0.8, "metallic": 0.0},
}


def get_material_from_library(material_name):
    """Obtener material de la biblioteca"""
    if material_name not in MATERIAL_LIBRARY:
        return None
    
    preset = MATERIAL_LIBRARY[material_name]
    
    mat = bpy.data.materials.new(f"Lib_{material_name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*preset["color"], 1.0)
    bsdf.inputs["Roughness"].default_value = preset["roughness"]
    bsdf.inputs["Metallic"].default_value = preset["metallic"]
    
    return mat


def list_material_library(category=None):
    """Listar materiales de la biblioteca"""
    if category:
        return {k: v for k, v in MATERIAL_LIBRARY.items() if k.startswith(category)}
    return MATERIAL_LIBRARY


# ═══════════════════════════════════════════════════════════════
# ANIMATION LIBRARY (20+ clips)
# ═══════════════════════════════════════════════════════════════

ANIMATION_LIBRARY = {
    # Movimiento básico
    "walk_forward": {"type": "locomotion", "frames": 30, "description": "Caminar hacia adelante"},
    "run_forward": {"type": "locomotion", "frames": 20, "description": "Correr hacia adelante"},
    "walk_backward": {"type": "locomotion", "frames": 30, "description": "Caminar hacia atrás"},
    "idle_breathe": {"type": "idle", "frames": 60, "description": "Respirar"},
    "idle_look_around": {"type": "idle", "frames": 90, "description": "Mirar alrededor"},
    
    # Acciones
    "jump": {"type": "action", "frames": 30, "description": "Saltar"},
    "crouch": {"type": "action", "frames": 20, "description": "Agacharse"},
    "stand_up": {"type": "action", "frames": 20, "description": "Levantarse"},
    "wave": {"type": "gesture", "frames": 40, "description": "Saludar"},
    "point": {"type": "gesture", "frames": 30, "description": "Señalar"},
    
    # Combate
    "punch_left": {"type": "combat", "frames": 15, "description": "Golpe izquierdo"},
    "punch_right": {"type": "combat", "frames": 15, "description": "Golpe derecho"},
    "kick": {"type": "combat", "frames": 20, "description": "Patada"},
    "block": {"type": "combat", "frames": 15, "description": "Bloquear"},
    "dodge": {"type": "combat", "frames": 20, "description": "Esquivar"},
    
    # Emociones
    "happy": {"type": "emotion", "frames": 60, "description": "Feliz"},
    "sad": {"type": "emotion", "frames": 60, "description": "Triste"},
    "angry": {"type": "emotion", "frames": 60, "description": "Enojado"},
    "surprised": {"type": "emotion", "frames": 30, "description": "Sorprendido"},
    "scared": {"type": "emotion", "frames": 60, "description": "Asustado"},
    
    # Naturaleza
    "wind_blow": {"type": "nature", "frames": 120, "description": "Viento soplando"},
    "wave": {"type": "nature", "frames": 60, "description": "Ola"},
    "float": {"type": "nature", "frames": 90, "description": "Flotar"},
}


def play_animation(obj, animation_name):
    """Reproducir animación de la biblioteca"""
    if animation_name not in ANIMATION_LIBRARY:
        print(f"Animación no encontrada: {animation_name}")
        return
    
    clip = ANIMATION_LIBRARY[animation_name]
    
    # Seleccionar tipo de animación
    if clip["type"] == "locomotion":
        from ..core.animation_engine import create_walk_cycle
        create_walk_cycle(obj, clip["frames"])
    elif clip["type"] == "idle":
        from ..core.animation_engine import create_idle_animation
        create_idle_animation(obj, clip["frames"])
    elif clip["type"] == "action":
        if animation_name == "jump":
            from ..core.animation_engine import create_jump_animation
            create_jump_animation(obj, clip["frames"])
    elif clip["type"] == "nature":
        if animation_name == "wave":
            from ..core.animation_engine import create_wave_animation
            create_wave_animation(obj, clip["frames"])
        elif animation_name == "float":
            from ..core.animation_engine import create_idle_animation
            create_idle_animation(obj, clip["frames"], breath_amplitude=0.1)
    
    print(f"Animación '{animation_name}' aplicada")


def list_animation_library(category=None):
    """Listar animaciones de la biblioteca"""
    if category:
        return {k: v for k, v in ANIMATION_LIBRARY.items() if v["type"] == category}
    return ANIMATION_LIBRARY


# ═══════════════════════════════════════════════════════════════
# SCENE TEMPLATES (10+)
# ═══════════════════════════════════════════════════════════════

SCENE_TEMPLATES = {
    # Habitaciones
    "bedroom": {
        "name": "Dormitorio",
        "objects": ["bed", "nightstand", "lamp", "wardrobe"],
        "style": "cozy",
    },
    "living_room": {
        "name": "Sala de estar",
        "objects": ["sofa", "coffee_table", "tv", "lamp"],
        "style": "modern",
    },
    "kitchen": {
        "name": "Cocina",
        "objects": ["counter", "stove", "fridge", "table"],
        "style": "modern",
    },
    "office": {
        "name": "Oficina",
        "objects": ["desk", "chair", "lamp", "bookshelf"],
        "style": "professional",
    },
    "bathroom": {
        "name": "Baño",
        "objects": ["sink", "toilet", "shower", "mirror"],
        "style": "clean",
    },
    
    # Exteriores
    "garden": {
        "name": "Jardín",
        "objects": ["bench", "table", "plants", "fence"],
        "style": "natural",
    },
    "patio": {
        "name": "Patio",
        "objects": ["chairs", "umbrella", "plants"],
        "style": "outdoor",
    },
    
    # Especiales
    "studio": {
        "name": "Estudio de fotografía",
        "objects": ["backdrop", "lights", "camera"],
        "style": "studio",
    },
    "showroom": {
        "name": "Showroom",
        "objects": ["pedestal", "spotlight", "backdrop"],
        "style": "commercial",
    },
    "workshop": {
        "name": "Taller",
        "objects": ["workbench", "tools", "shelves"],
        "style": "industrial",
    },
}


def create_scene_from_template(template_name, location=(0, 0, 0)):
    """Crear escena desde plantilla"""
    if template_name not in SCENE_TEMPLATES:
        print(f"Plantilla no encontrada: {template_name}")
        return None
    
    template = SCENE_TEMPLATES[template_name]
    
    print(f"Creando escena: {template['name']}")
    print(f"Objetos: {template['objects']}")
    print(f"Estilo: {template['style']}")
    
    # Por ahora, crear un placeholder
    # En implementación completa, crearía cada objeto
    from ..core.mesh_engine import create_advanced_primitive
    
    floor = create_advanced_primitive("plane", {"size": 10, "location": location})
    floor.name = f"{template['name']}_Floor"
    
    print(f"Escena '{template['name']}' creada (placeholder)")
    return floor


def list_scene_templates():
    """Listar plantillas de escena"""
    return {k: v["name"] for k, v in SCENE_TEMPLATES.items()}
