"""
blender-mcp — Physics Advanced Engine
Motor de física avanzada: Cloth, Fluid, Particles, Rigid Body avanzado.
"""
try:
    import bpy
except ImportError:
    bpy = None

import math


# ═══════════════════════════════════════════════════════════════
# CLOTH SIMULATION
# ═══════════════════════════════════════════════════════════════

def cloth_simulation(obj, preset="cotton"):
    """
    Configurar simulación de tela.
    
    Args:
        obj: Objeto (idealmente un plano)
        preset: 'cotton', 'silk', 'leather', 'rubber'
    """
    if bpy is None or obj is None:
        return False
    
    presets = {
        "cotton": {"mass": 0.3, "tension": 15, "compression": 15, "bending": 5},
        "silk": {"mass": 0.1, "tension": 5, "compression": 5, "bending": 1},
        "leather": {"mass": 0.5, "tension": 25, "compression": 25, "bending": 10},
        "rubber": {"mass": 0.4, "tension": 10, "compression": 10, "bending": 2},
    }
    
    if preset not in presets:
        print(f"Preset no encontrado: {preset}")
        return False
    
    params = presets[preset]
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.modifier_add(type='CLOTH')
    mod = obj.modifiers.get("Cloth")
    
    if mod:
        mod.settings.mass = params["mass"]
        mod.settings.tension_stiffness = params["tension"]
        mod.settings.compression_stiffness = params["compression"]
        mod.settings.bending_stiffness = params["bending"]
        mod.collision_settings.use_collision = True
        
        print(f"Cloth simulation: {preset}")
        return True
    
    return False


# ═══════════════════════════════════════════════════════════════
# FLUID SIMULATION
# ═══════════════════════════════════════════════════════════════

def fluid_simulation(obj, fluid_type="LIQUID", resolution=64):
    """
    Configurar simulación de fluido.
    
    Args:
        obj: Objeto
        fluid_type: 'LIQUID', 'GAS'
        resolution: Resolución de la simulación
    """
    if bpy is None or obj is None:
        return False
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.modifier_add(type='FLUID')
    mod = obj.modifiers.get("Fluid")
    
    if mod:
        mod.fluid_type = 'DOMAIN'
        mod.domain_settings.resolution = resolution
        
        if fluid_type == "LIQUID":
            mod.domain_settings.domain_type = 'LIQUID'
        else:
            mod.domain_settings.domain_type = 'GAS'
        
        print(f"Fluid simulation: {fluid_type}, resolution={resolution}")
        return True
    
    return False


# ═══════════════════════════════════════════════════════════════
# PARTICLE SYSTEM
# ═══════════════════════════════════════════════════════════════

def particle_system(obj, particle_type="HAIR", count=1000):
    """
    Configurar sistema de partículas.
    
    Args:
        obj: Objeto
        particle_type: 'HAIR', 'EMITTER'
        count: Número de partículas
    """
    if bpy is None or obj is None:
        return False
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.particle_system_add()
    ps = obj.particle_systems.active
    
    if ps:
        ps.settings.count = count
        
        if particle_type == "HAIR":
            ps.settings.type = 'HAIR'
            ps.settings.hair_length = 0.1
        else:
            ps.settings.type = 'EMITTER'
            ps.settings.frame_start = 1
            ps.settings.frame_end = 100
        
        print(f"Particle system: {particle_type}, {count} particles")
        return True
    
    return False


# ═══════════════════════════════════════════════════════════════
# RIGID BODY ADVANCED
# ═══════════════════════════════════════════════════════════════

def rigid_body_advanced(obj, mass=1.0, friction=0.5, restitution=0.3, 
                       linear_damping=0.04, angular_damping=0.1):
    """
    Configurar rigid body con parámetros avanzados.
    
    Args:
        obj: Objeto
        mass: Masa en kg
        friction: Fricción (0-1)
        restitution: Rebote (0-1)
        linear_damping: Amortiguación lineal
        angular_damping: Amortiguación angular
    """
    if bpy is None or obj is None:
        return False
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.rigidbody.object_add(type='ACTIVE')
    
    rb = obj.rigid_body
    rb.mass = mass
    rb.friction = friction
    rb.restitution = restitution
    rb.linear_damping = linear_damping
    rb.angular_damping = angular_damping
    
    print(f"Rigid body avanzado: {obj.name} ({mass}kg)")
    return True


# ═══════════════════════════════════════════════════════════════
# SOFT BODY ADVANCED
# ═══════════════════════════════════════════════════════════════

def soft_body_advanced(obj, mass=0.5, friction=0.5, speed=1.0,
                       pull=0.5, push=0.5, gravity=1.0):
    """
    Configurar soft body con parámetros avanzados.
    """
    if bpy is None or obj is None:
        return False
    
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
        sb.pull = pull
        sb.push = push
        sb.gravity = gravity
        
        print(f"Soft body avanzado: {obj.name}")
        return True
    
    return False


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_physics_presets():
    """Listar presets de física disponibles"""
    return {
        "cloth_cotton": "Tela de algodón",
        "cloth_silk": "Seda",
        "cloth_leather": "Cuero",
        "cloth_rubber": "Goma",
        "fluid_liquid": "Líquido",
        "fluid_gas": "Gas",
        "particle_hair": "Pelo",
        "particle_emitter": "Emisor",
    }
