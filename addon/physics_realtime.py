"""
blender-mcp — Physics Real-time
Configuración de física en tiempo real para preview rápido.
"""
import bpy
from typing import Dict, Optional


# ═══════════════════════════════════════════════════════════════
# PHYSICS PRESETS
# ═══════════════════════════════════════════════════════════════

PHYSICS_PRESETS = {
    "rigid_heavy": {
        "type": "RIGID_BODY",
        "mass": 10.0,
        "friction": 0.5,
        "restitution": 0.1,
    },
    "rigid_light": {
        "type": "RIGID_BODY",
        "mass": 0.5,
        "friction": 0.3,
        "restitution": 0.3,
    },
    "rigid_bouncy": {
        "type": "RIGID_BODY",
        "mass": 1.0,
        "friction": 0.2,
        "restitution": 0.8,
    },
    "cloth_cotton": {
        "type": "CLOTH",
        "quality": 5,
        "mass": 0.3,
        "tension": 15,
        "compression": 15,
        "bending": 5,
    },
    "cloth_silk": {
        "type": "CLOTH",
        "quality": 8,
        "mass": 0.1,
        "tension": 5,
        "compression": 5,
        "bending": 1,
    },
    "cloth_leather": {
        "type": "CLOTH",
        "quality": 5,
        "mass": 0.8,
        "tension": 40,
        "compression": 40,
        "bending": 20,
    },
    "fluid_water": {
        "type": "FLUID",
        "domain_type": "LIQUID",
        "resolution": 64,
        "viscosity": 1.0,
    },
    "fluid_smoke": {
        "type": "FLUID",
        "domain_type": "GAS",
        "resolution": 32,
        "density": 1.0,
    },
    "soft_body_rubber": {
        "type": "SOFT_BODY",
        "mass": 1.0,
        "friction": 0.5,
        "speed": 1.0,
    },
    "soft_body_jelly": {
        "type": "SOFT_BODY",
        "mass": 0.5,
        "friction": 0.2,
        "speed": 2.0,
    },
    "particle_snow": {
        "type": "PARTICLES",
        "count": 1000,
        "lifetime": 100,
        "mass": 0.01,
    },
    "particle_rain": {
        "type": "PARTICLES",
        "count": 5000,
        "lifetime": 50,
        "mass": 0.001,
    },
    "particle_sparks": {
        "type": "PARTICLES",
        "count": 200,
        "lifetime": 30,
        "mass": 0.001,
    },
}


# ═══════════════════════════════════════════════════════════════
# PHYSICS APPLICATION
# ═══════════════════════════════════════════════════════════════

def add_rigid_body(obj: bpy.types.Object, preset: str = "rigid_heavy",
                   active: bool = True) -> bool:
    """
    Agregar rigid body a objeto.
    
    Args:
        obj: Objeto
        preset: Nombre del preset
        active: Si es activo (True) o pasivo (False)
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add rigid body
        bpy.ops.rigidbody.object_add(type='ACTIVE' if active else 'PASSIVE')
        
        # Apply preset
        if preset in PHYSICS_PRESETS:
            config = PHYSICS_PRESETS[preset]
            rb = obj.rigid_body
            rb.mass = config.get("mass", 1.0)
            rb.friction = config.get("friction", 0.5)
            rb.restitution = config.get("restitution", 0.1)
        
        print(f"[physics] Rigid body added: {obj.name}, preset={preset}")
        return True
        
    except Exception as e:
        print(f"[physics] Rigid body failed: {e}")
        return False


def add_cloth(obj: bpy.types.Object, preset: str = "cloth_cotton") -> bool:
    """
    Agregar cloth a objeto.
    
    Args:
        obj: Objeto
        preset: Nombre del preset
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add cloth modifier
        mod = obj.modifiers.new(name="Cloth", type='CLOTH')
        
        # Apply preset
        if preset in PHYSICS_PRESETS:
            config = PHYSICS_PRESETS[preset]
            mod.settings.mass = config.get("mass", 0.3)
            mod.settings.tension_stiffness = config.get("tension", 15)
            mod.settings.compression_stiffness = config.get("compression", 15)
            mod.settings.bending_stiffness = config.get("bending", 5)
        
        print(f"[physics] Cloth added: {obj.name}, preset={preset}")
        return True
        
    except Exception as e:
        print(f"[physics] Cloth failed: {e}")
        return False


def add_soft_body(obj: bpy.types.Object, preset: str = "soft_body_rubber") -> bool:
    """
    Agregar soft body a objeto.
    
    Args:
        obj: Objeto
        preset: Nombre del preset
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add soft body modifier
        mod = obj.modifiers.new(name="SoftBody", type='SOFT_BODY')
        
        # Apply preset
        if preset in PHYSICS_PRESETS:
            config = PHYSICS_PRESETS[preset]
            mod.mass = config.get("mass", 1.0)
            mod.friction = config.get("friction", 0.5)
            mod.speed = config.get("speed", 1.0)
        
        print(f"[physics] Soft body added: {obj.name}, preset={preset}")
        return True
        
    except Exception as e:
        print(f"[physics] Soft body failed: {e}")
        return False


def add_particles(obj: bpy.types.Object, preset: str = "particle_snow") -> bool:
    """
    Agregar sistema de partículas.
    
    Args:
        obj: Objeto
        preset: Nombre del preset
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add particle system
        bpy.ops.object.particle_system_add()
        
        # Configure
        ps = obj.particle_systems.active
        ps.settings.count = PHYSICS_PRESETS.get(preset, {}).get("count", 1000)
        ps.settings.lifetime = PHYSICS_PRESETS.get(preset, {}).get("lifetime", 100)
        ps.settings.particle_mass = PHYSICS_PRESETS.get(preset, {}).get("mass", 0.01)
        
        print(f"[physics] Particles added: {obj.name}, preset={preset}")
        return True
        
    except Exception as e:
        print(f"[physics] Particles failed: {e}")
        return False


def add_force_field(obj: bpy.types.Object, field_type: str = 'FORCE',
                   strength: float = 1.0) -> bool:
    """
    Agregar force field.
    
    Args:
        obj: Objeto
        field_type: Tipo de campo (FORCE, WIND, VORTEX, etc.)
        strength: Fuerza
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add force field
        bpy.ops.object.effector_add(type=field_type)
        
        # Configure
        field = obj.field
        field.strength = strength
        
        print(f"[physics] Force field added: {obj.name}, type={field_type}")
        return True
        
    except Exception as e:
        print(f"[physics] Force field failed: {e}")
        return False


def add_collision(obj: bpy.types.Object, damping: float = 0.5) -> bool:
    """
    Agregar colisión a objeto.
    
    Args:
        obj: Objeto
        damping: Amortiguación
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add collision modifier
        mod = obj.modifiers.new(name="Collision", type='COLLISION')
        mod.settings.damping_factor = damping
        
        print(f"[physics] Collision added: {obj.name}")
        return True
        
    except Exception as e:
        print(f"[physics] Collision failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# REAL-TIME PREVIEW
# ═══════════════════════════════════════════════════════════════

def setup_realtime_preview() -> bool:
    """
    Configurar escena para preview en tiempo real.
    
    Returns:
        True si éxito
    """
    try:
        # Set viewport shading
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        space.shading.show_shadows = False
        
        # Reduce particle count for preview
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for ps in obj.particle_systems:
                    ps.settings.display_percentage = 10
        
        # Set low quality for physics
        if bpy.context.scene.rigidbody_world:
            bpy.context.scene.rigidbody_world.substeps_per_frame = 1
            bpy.context.scene.rigidbody_world.solver_iterations = 10
        
        print("[physics] Real-time preview setup complete")
        return True
        
    except Exception as e:
        print(f"[physics] Preview setup failed: {e}")
        return False


def apply_physics_preset(obj: bpy.types.Object, preset_name: str) -> bool:
    """
    Aplicar preset de física completo.
    
    Args:
        obj: Objeto
        preset_name: Nombre del preset
    
    Returns:
        True si éxito
    """
    if preset_name not in PHYSICS_PRESETS:
        print(f"[physics] Unknown preset: {preset_name}")
        return False
    
    preset = PHYSICS_PRESETS[preset_name]
    physics_type = preset["type"]
    
    if physics_type == "RIGID_BODY":
        return add_rigid_body(obj, preset_name)
    elif physics_type == "CLOTH":
        return add_cloth(obj, preset_name)
    elif physics_type == "SOFT_BODY":
        return add_soft_body(obj, preset_name)
    elif physics_type == "PARTICLES":
        return add_particles(obj, preset_name)
    elif physics_type == "FLUID":
        # Fluid setup is more complex
        print(f"[physics] Fluid preset '{preset_name}' requires manual configuration")
        return False
    
    return False
