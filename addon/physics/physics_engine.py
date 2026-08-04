"""
blender-mcp — Physics Engine
Simulación física: Rigid Body, Soft Body, Fluid, Particles.
"""
import bpy


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
    
    bpy.ops.rigidbody.object_add(type='ACTIVE')
    
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
    
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    
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
    
    bpy.ops.object.modifier_add(type='SOFT_BODY')
    
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
    
    bpy.ops.object.modifier_add(type='FLUID')
    mod = obj.modifiers.get("Fluid")
    
    if mod:
        mod.fluid_type = 'DOMAIN'
        mod.domain_settings.resolution = resolution
        print(f"Dominio de fluido: {obj.name} (resolución: {resolution})")
    
    return mod


def add_fluid_flow(obj, flow_type='LIQUID'):
    """
    Agregar flujo de fluido.
    """
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.modifier_add(type='FLUID')
    mod = obj.modifiers.get("Fluid")
    
    if mod:
        mod.fluid_type = 'FLOW'
        mod.flow_type = flow_type
        print(f"Flujo de fluido: {obj.name} ({flow_type})")
    
    return mod


# ═══════════════════════════════════════════════════════════════
# PARTICLE SYSTEM
# ═══════════════════════════════════════════════════════════════

def add_particle_system(obj, particle_type='HAIR', count=1000):
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
        
        if particle_type == 'HAIR':
            ps.settings.type = 'HAIR'
            ps.settings.hair_length = 0.1
        else:
            ps.settings.type = 'EMITTER'
            ps.settings.frame_start = 1
            ps.settings.frame_end = 100
        
        print(f"Sistema de partículas: {obj.name} ({particle_type}, {count})")
    
    return ps


def add_hair_system(obj, length=0.1, count=1000):
    """Agregar sistema de pelo"""
    return add_particle_system(obj, 'HAIR', count)


def add_emitter_system(obj, count=1000, frame_start=1, frame_end=100):
    """Agregar sistema de emisor (lluvia, chispas, etc.)"""
    return add_particle_system(obj, 'EMITTER', count)


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
        "fluid_domain": "Dominio de fluido (agua)",
        "fluid_flow": "Flujo de fluido (chorro)",
        "hair": "Sistema de pelo",
        "emitter": "Sistema de emisor (lluvia, chispas)",
    }
