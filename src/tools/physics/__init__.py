"""blender-mcp-ultra — Physics Tools
Rigid body, cloth y force fields (la categoría que el catálogo prometía).
"""
from __future__ import annotations

from typing import Dict

try:
    import bpy
except ImportError:  # fuera de Blender
    bpy = None

from ...core.entities import Tool, ToolCategory, ToolPermission


def _get_obj(object_name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise ValueError(f"Objeto no encontrado: {object_name}")
    return obj


def _ensure_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def rigidbody_add(
    object_name: str,
    body_type: str = "ACTIVE",
    mass: float = 1.0,
    friction: float = 0.5,
    restitution: float = 0.0,
) -> dict:
    """Convertir objeto en rigid body (ACTIVE = cae, PASSIVE = obstáculo)."""
    obj = _get_obj(object_name)
    col = _ensure_collection("RigidBodyWorld")
    if obj.name not in col.objects:
        col.objects.link(obj)
    if bpy.context.scene.rigidbody_world is None:
        bpy.ops.rigidbody.world_add()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.rigidbody.object_add()
    rb = obj.rigid_body
    rb.type = body_type.upper()
    rb.mass = float(mass)
    rb.friction = float(friction)
    rb.restitution = float(restitution)
    return {"object": object_name, "type": rb.type, "mass": rb.mass}


def collision_add(object_name: str, bounce: float = 0.4) -> dict:
    """Añadir colisión (para soft body/partículas)."""
    obj = _get_obj(object_name)
    mod = obj.modifiers.get("Collision")
    if mod is None:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_add(type="COLLISION")
        mod = obj.modifiers.get("Collision")
    col = obj.collision
    # 4.x: bounciness · 5.x: el rebote vive en damping_factor (inverso)
    if hasattr(col, "bounciness"):
        col.bounciness = float(bounce)
    else:
        col.damping_factor = max(0.0, min(1.0, 1.0 - float(bounce)))
    return {"object": object_name, "collision": True, "bounce": bounce}


def cloth_add(object_name: str, quality: int = 10, mass: float = 0.4) -> dict:
    """Añadir simulación de tela al objeto."""
    obj = _get_obj(object_name)
    if obj.type != "MESH":
        raise ValueError("cloth requiere MESH")
    mod = obj.modifiers.new("Cloth", "CLOTH")
    mod.settings.quality = int(quality)
    mod.settings.mass = float(mass)
    return {"object": object_name, "modifier": mod.name}


def force_field_add(
    kind: str = "WIND", location=None, strength: float = 10.0, name: str = ""
) -> dict:
    """Crear force field (WIND, FORCE, TURBULENCE, VORTEX, MAGNET...)."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.effector_add(
        type=kind.upper(),
        location=location or (0.0, 0.0, 0.0),
    )
    field_obj = bpy.context.active_object
    if name:
        field_obj.name = name
    field_obj.field.strength = float(strength)
    return {
        "object": field_obj.name,
        "field_type": kind.upper(),
        "strength": field_obj.field.strength,
    }


def bake_rigidbody(frames: int = 50) -> dict:
    """Cocinar la simulación rigid body hasta `frames` (bloquea unos segundos)."""
    scene = bpy.context.scene
    rb = scene.rigidbody_world
    if rb is None:
        raise ValueError("No hay rigid body world en la escena")
    rb.point_cache.frame_end = min(int(frames), scene.frame_end)
    bpy.ops.ptcache.bake_all(bake=True)
    return {"baked": True, "frame_end": rb.point_cache.frame_end}


# ── Envolturas sobre addon/physics_realtime + physics_advanced ──


def _realtime():
    try:
        import addon.physics_realtime as rt

        return rt
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"addon.physics_realtime no disponible: {e}") from e


_PARTICLE_PRESETS = {
    "particle_snow": {"count": 2000, "lifetime": 100},
    "particle_rain": {"count": 4000, "lifetime": 50},
    "particle_sparks": {"count": 800, "lifetime": 30},
    "particle_default": {"count": 1000, "lifetime": 100},
}


def particles_add(object_name: str, preset: str = "particle_snow") -> dict:
    """Sistema de partículas por preset (compatible 4.x/5.x sin particle_mass)."""
    obj = _get_obj(object_name)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.particle_system_add()
    ps = obj.particle_systems.active
    cfg = _PARTICLE_PRESETS.get(preset, _PARTICLE_PRESETS["particle_default"])
    ps.settings.count = int(cfg["count"])
    ps.settings.lifetime = int(cfg["lifetime"])
    return {"object": object_name, "particles": True, "preset": preset, "count": cfg["count"]}


def soft_body_add(object_name: str, preset: str = "soft_body_rubber") -> dict:
    obj = _get_obj(object_name)
    mod = obj.modifiers.new("Softbody", "SOFT_BODY")
    mod.settings.use_goal = False
    try:
        mod.settings.friction = 0.5
    except Exception:
        pass
    return {"object": object_name, "soft_body": True, "preset": preset}


def physics_preset(object_name: str, preset_name: str) -> dict:
    """Preset físico completo del addon sobre un objeto."""
    obj = _get_obj(object_name)
    ok = _realtime().apply_physics_preset(obj, preset_name)
    return {"object": object_name, "preset": preset_name, "applied": bool(ok)}


def rigidbody_constraint(
    object_a: str, object_b: str, constraint_type: str = "HINGE", location: list = None
) -> dict:
    """Constraint entre dos rigid bodies (HINGE, SLIDER, FIXED...)."""
    adv = __import__("addon.physics_advanced", fromlist=["x"])
    a = _get_obj(object_a)
    b = _get_obj(object_b)
    adv.rigid_body_constraint(
        a, b, constraint_type=constraint_type, location=tuple(location or (0, 0, 0))
    )
    return {"constraint": constraint_type, "a": object_a, "b": object_b}


def bake_cache(frame_start: int = 1, frame_end: int = 250) -> dict:
    """Cocinar TODAS las cachés de física (bloquea unos segundos)."""
    adv = __import__("addon.physics_advanced", fromlist=["x"])
    adv.bake_physics_cache(frame_start=int(frame_start), frame_end=int(frame_end))
    return {"baked": True, "frame_start": frame_start, "frame_end": frame_end}


TOOLS = [
    Tool(
        "physics.rigidbody_add",
        ToolCategory.OBJECTS,
        "Rigid body (ACTIVE cae / PASSIVE obstáculo) con masa y fricción",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "body_type": {"type": "str"},
            "mass": {"type": "float"},
            "friction": {"type": "float"},
            "restitution": {"type": "float"},
        },
    ),
    Tool(
        "physics.collision_add",
        ToolCategory.OBJECTS,
        "Modifier de colisión con rebote",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "bounce": {"type": "float"}},
    ),
    Tool(
        "physics.cloth_add",
        ToolCategory.OBJECTS,
        "Simulación de tela",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "quality": {"type": "int"},
            "mass": {"type": "float"},
        },
    ),
    Tool(
        "physics.force_field_add",
        ToolCategory.OBJECTS,
        "Force field (WIND, FORCE, TURBULENCE, VORTEX...)",
        ToolPermission.WRITE,
        {
            "kind": {"type": "str"},
            "location": {"type": "list"},
            "strength": {"type": "float"},
            "name": {"type": "str"},
        },
    ),
    Tool(
        "physics.bake_rigidbody",
        ToolCategory.OBJECTS,
        "Cocinar rigid body world hasta N frames",
        ToolPermission.WRITE,
        {"frames": {"type": "int"}},
    ),
    Tool(
        "physics.particles_add",
        ToolCategory.OBJECTS,
        "Sistema de partículas por preset (snow/rain/sparks...)",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "preset": {"type": "str"}},
    ),
    Tool(
        "physics.soft_body_add",
        ToolCategory.OBJECTS,
        "Soft body por preset",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "preset": {"type": "str"}},
    ),
    Tool(
        "physics.preset",
        ToolCategory.OBJECTS,
        "Preset físico completo del addon sobre un objeto",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "preset_name": {"type": "str", "required": True},
        },
    ),
    Tool(
        "physics.rigidbody_constraint",
        ToolCategory.OBJECTS,
        "Constraint entre dos rigid bodies (HINGE/SLIDER/FIXED...)",
        ToolPermission.WRITE,
        {
            "object_a": {"type": "str", "required": True},
            "object_b": {"type": "str", "required": True},
            "constraint_type": {"type": "str"},
            "location": {"type": "list"},
        },
    ),
    Tool(
        "physics.bake_cache",
        ToolCategory.OBJECTS,
        "Cocinar todas las cachés de física",
        ToolPermission.WRITE,
        {"frame_start": {"type": "int"}, "frame_end": {"type": "int"}},
    ),
]

HANDLERS = {
    "physics.rigidbody_add": rigidbody_add,
    "physics.collision_add": collision_add,
    "physics.cloth_add": cloth_add,
    "physics.force_field_add": force_field_add,
    "physics.bake_rigidbody": bake_rigidbody,
    "physics.particles_add": particles_add,
    "physics.soft_body_add": soft_body_add,
    "physics.preset": physics_preset,
    "physics.rigidbody_constraint": rigidbody_constraint,
    "physics.bake_cache": bake_cache,
}
