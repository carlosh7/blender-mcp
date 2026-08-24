"""
blender-mcp-ultra — Physics Tools
Rigid body, cloth y force fields (la categoría que el catálogo prometía).
"""

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
]

HANDLERS = {
    "physics.rigidbody_add": rigidbody_add,
    "physics.collision_add": collision_add,
    "physics.cloth_add": cloth_add,
    "physics.force_field_add": force_field_add,
    "physics.bake_rigidbody": bake_rigidbody,
}
