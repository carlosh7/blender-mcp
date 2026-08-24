"""
blender-mcp — Physics Engine
Simulación física: Rigid Body, Soft Body, Fluid, Particles, Cloth.
"""

try:
    import bpy
except ImportError:
    bpy = None


# ═══════════════════════════════════════════════════════════════
# RIGID BODY
# ═══════════════════════════════════════════════════════════════


def add_rigid_body(obj, mass=1.0, friction=0.5, restitution=0.3):
    """
    Agregar rigid body a un objeto.

    Args:
        obj: Objeto
        mass: Masa en kg
        friction: Fricción (0-1)
        restitution: Rebote (0-1)
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.rigidbody.object_add(type="ACTIVE")

    rb = obj.rigid_body
    rb.mass = mass
    rb.friction = friction
    rb.restitution = restitution

    print(f"Rigid body agregado: {obj.name} ({mass}kg)")
    return rb


def add_rigid_body_passive(obj, friction=0.5):
    """
    Agregar rigid body pasivo (suelo, paredes).
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.rigidbody.object_add(type="PASSIVE")

    rb = obj.rigid_body
    rb.friction = friction

    print(f"Rigid body pasivo: {obj.name}")
    return rb


# ═══════════════════════════════════════════════════════════════
# SOFT BODY
# ═══════════════════════════════════════════════════════════════


def add_soft_body(obj, mass=1.0, friction=0.5, speed=1.0):
    """
    Agregar soft body a un objeto.

    Args:
        obj: Objeto
        mass: Masa
        friction: Fricción
        speed: Velocidad de simulación
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.modifier_add(type="SOFT_BODY")

    mod = obj.modifiers.get("Softbody")
    if mod:
        mod.point_cache.frame_start = 1
        mod.point_cache.frame_end = 250

        sb = mod.settings
        sb.mass = mass
        sb.friction = friction
        sb.speed = speed

        print(f"Soft body agregado: {obj.name}")

    return mod


# ═══════════════════════════════════════════════════════════════
# FLUID SIMULATION
# ═══════════════════════════════════════════════════════════════


def add_fluid_domain(obj, resolution=64):
    """
    Agregar dominio de fluido.
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.modifier_add(type="FLUID")
    mod = obj.modifiers.get("Fluid")

    if mod:
        mod.fluid_type = "DOMAIN"
        mod.domain_settings.resolution = resolution
        print(f"Dominio de fluido: {obj.name} (resolución: {resolution})")

    return mod


def add_fluid_flow(obj, flow_type="LIQUID"):
    """
    Agregar flujo de fluido.
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.modifier_add(type="FLUID")
    mod = obj.modifiers.get("Fluid")

    if mod:
        mod.fluid_type = "FLOW"
        mod.flow_type = flow_type
        print(f"Flujo de fluido: {obj.name} ({flow_type})")

    return mod


# ═══════════════════════════════════════════════════════════════
# PARTICLE SYSTEM
# ═══════════════════════════════════════════════════════════════


def add_particle_system(obj, particle_type="HAIR", count=1000):
    """
    Agregar sistema de partículas.

    Args:
        obj: Objeto
        particle_type: 'HAIR' o 'EMITTER'
        count: Número de partículas
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.particle_system_add()

    ps = obj.particle_systems.active
    if ps:
        ps.settings.count = count

        if particle_type == "HAIR":
            ps.settings.type = "HAIR"
            ps.settings.hair_length = 0.1
        else:
            ps.settings.type = "EMITTER"
            ps.settings.frame_start = 1
            ps.settings.frame_end = 100

        print(f"Sistema de partículas: {obj.name} ({particle_type}, {count})")

    return ps


def add_hair_system(obj, length=0.1, count=1000):
    """Agregar sistema de pelo"""
    return add_particle_system(obj, "HAIR", count)


def add_emitter_system(obj, count=1000, frame_start=1, frame_end=100):
    """Agregar sistema de emisor (lluvia, chispas, etc.)"""
    return add_particle_system(obj, "EMITTER", count)


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def simulate_physics(frames=250):
    """
    Ejecutar simulación de física.
    """
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Simulación configurada: {frames} frames")


def list_physics_types():
    """Listar tipos de física disponibles"""
    return {
        "rigid_body": "Cuerpo rígido (caída, colisiones)",
        "rigid_body_passive": "Cuerpo rígido pasivo (suelo)",
        "soft_body": "Cuerpo blando (goma, gelatina)",
        "cloth": "Simulación de tela (ropa, banderas)",
        "fluid_domain": "Dominio de fluido (agua)",
        "fluid_flow": "Flujo de fluido (chorro)",
        "hair": "Sistema de pelo",
        "emitter": "Sistema de emisor (lluvia, chispas)",
    }


# ═══════════════════════════════════════════════════════════════
# CLOTH SIMULATION
# ═══════════════════════════════════════════════════════════════


def add_cloth(obj, mass=0.3, tension=15, compression=15, bending=5):
    """
    Agregar simulación de tela a un objeto.

    Args:
        obj: Objeto (idealmente un plano)
        mass: Masa de la tela
        tension: Tensión (resistencia a estiramiento)
        compression: Compresión
        bending: Resistencia a doblar
    """
    if bpy is None:
        return None

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.modifier_add(type="CLOTH")

    mod = obj.modifiers.get("Cloth")
    if mod:
        mod.settings.mass = mass
        mod.settings.tension_stiffness = tension
        mod.settings.compression_stiffness = compression
        mod.settings.bending_stiffness = bending

        # Configurar colisión
        mod.collision_settings.use_collision = True
        mod.collision_settings.distance_min = 0.01

        print(f"Cloth simulation: {obj.name} (mass={mass}, tension={tension})")

    return mod


def add_cloth_preset(obj, preset="cotton"):
    """
    Agregar cloth con preset predefinido.

    Presets: cotton, silk, leather, rubber, metal
    """
    presets = {
        "cotton": {"mass": 0.3, "tension": 15, "compression": 15, "bending": 5},
        "silk": {"mass": 0.1, "tension": 5, "compression": 5, "bending": 1},
        "leather": {"mass": 0.5, "tension": 25, "compression": 25, "bending": 10},
        "rubber": {"mass": 0.4, "tension": 10, "compression": 10, "bending": 2},
        "metal": {"mass": 1.0, "tension": 50, "compression": 50, "bending": 20},
    }

    if preset not in presets:
        print(f"Preset no encontrado: {preset}")
        return None

    params = presets[preset]
    return add_cloth(obj, **params)


# ═══════════════════════════════════════════════════════════════
# DYNAMIC PAINT
# ═══════════════════════════════════════════════════════════════


def add_dynamic_paint(obj, surface_type="PAINT"):
    """
    Agregar Dynamic Paint a un objeto.

    Args:
        obj: Objeto
        surface_type: 'PAINT', 'WAVE', 'WEIGHT'
    """
    if bpy is None:
        return None

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.modifier_add(type="DYNAMIC_PAINT")

    mod = obj.modifiers.get("Dynamic Paint")
    if mod:
        mod.ui_type = "SURFACE"
        mod.surface_settings.surface_type = surface_type

        print(f"Dynamic Paint: {obj.name} ({surface_type})")

    return mod


# ═══════════════════════════════════════════════════════════════
# FORCE FIELDS
# ═══════════════════════════════════════════════════════════════


def add_force_field(obj, field_type="WIND", strength=1.0):
    """
    Agregar campo de fuerza.

    Args:
        obj: Objeto
        field_type: 'WIND', 'VORTEX', 'MAGNET', 'HARMONIC', 'FORCE'
        strength: Fuerza del campo
    """
    if bpy is None:
        return None

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.effector_add(type=field_type)

    effector = obj.field
    if effector:
        effector.strength = strength
        print(f"Force field: {obj.name} ({field_type}, strength={strength})")

    return effector


# ═══════════════════════════════════════════════════════════════
# FLUID SIMULATION PRESETS
# ═══════════════════════════════════════════════════════════════

FLUID_PRESETS = {
    "water": {"resolution": 64, "viscosity": 1.0, "diffusion": 0.0},
    "honey": {"resolution": 48, "viscosity": 10.0, "diffusion": 0.0},
    "oil": {"resolution": 48, "viscosity": 5.0, "diffusion": 0.0},
    "milk": {"resolution": 64, "viscosity": 2.0, "diffusion": 0.1},
    "lava": {"resolution": 32, "viscosity": 100.0, "diffusion": 0.0},
}


def add_fluid_preset(obj, preset="water"):
    """
    Agregar fluido con preset predefinido.

    Presets: water, honey, oil, milk, lava
    """
    if bpy is None:
        return None

    if preset not in FLUID_PRESETS:
        print(f"Preset no encontrado: {preset}")
        return None

    params = FLUID_PRESETS[preset]
    return add_fluid_domain(obj, resolution=params["resolution"])


# ═══════════════════════════════════════════════════════════════
# COLLISION PRESETS
# ═══════════════════════════════════════════════════════════════

COLLISION_PRESETS = {
    "ice": {"friction": 0.01, "stickiness": 0.0},
    "rubber": {"friction": 0.8, "stickiness": 0.5},
    "wood": {"friction": 0.5, "stickiness": 0.1},
    "metal": {"friction": 0.3, "stickiness": 0.0},
    "fabric": {"friction": 0.6, "stickiness": 0.3},
}


def add_collision_preset(obj, preset="wood"):
    """
    Agregar colisión con preset predefinido.
    """
    if bpy is None:
        return None

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bpy.ops.object.modifier_add(type="COLLISION")

    mod = obj.modifiers.get("Collision")
    if mod and preset in COLLISION_PRESETS:
        params = COLLISION_PRESETS[preset]
        mod.settings.friction_factor = params["friction"]
        mod.settings.stickiness = params["stickiness"]
        print(f"Collision preset: {obj.name} ({preset})")

    return mod


# ═══════════════════════════════════════════════════════════════
# RIGID BODY PRESETS
# ═══════════════════════════════════════════════════════════════

RIGID_PRESETS = {
    "light": {"mass": 0.1, "friction": 0.3, "restitution": 0.4},
    "medium": {"mass": 1.0, "friction": 0.5, "restitution": 0.3},
    "heavy": {"mass": 5.0, "friction": 0.7, "restitution": 0.2},
    "bouncy": {"mass": 0.5, "friction": 0.2, "restitution": 0.8},
    "metal": {"mass": 3.0, "friction": 0.4, "restitution": 0.1},
}


def add_rigid_body_preset(obj, preset="medium"):
    """
    Agregar rigid body con preset predefinido.
    """
    if bpy is None:
        return None

    if preset not in RIGID_PRESETS:
        print(f"Preset no encontrado: {preset}")
        return None

    params = RIGID_PRESETS[preset]
    return add_rigid_body(obj, **params)


# ═══════════════════════════════════════════════════════════════
# SOFT BODY PRESETS
# ═══════════════════════════════════════════════════════════════

SOFT_PRESETS = {
    "rubber": {"mass": 0.3, "friction": 0.5, "speed": 1.0},
    "gelatin": {"mass": 0.2, "friction": 0.3, "speed": 0.8},
    "jelly": {"mass": 0.4, "friction": 0.4, "speed": 0.9},
    "foam": {"mass": 0.1, "friction": 0.2, "speed": 0.6},
}


def add_soft_body_preset(obj, preset="rubber"):
    """
    Agregar soft body con preset predefinido.
    """
    if bpy is None:
        return None

    if preset not in SOFT_PRESETS:
        print(f"Preset no encontrado: {preset}")
        return None

    params = SOFT_PRESETS[preset]
    return add_soft_body(obj, **params)
