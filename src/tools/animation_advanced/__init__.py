"""
blender-mcp-ultra — Advanced Animation Tools
Fcurves, drivers, constraints y shape keys para animación real.
"""

from typing import Any, Dict, List

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


def _action_fcurves(obj):
    """fcurves de la acción: legacy (<4.4) o ranuradas (4.4+/5.x)."""
    ad = getattr(obj, "animation_data", None)
    action = ad.action if ad else None
    if action is None:
        return None
    try:
        return action.fcurves  # legacy
    except AttributeError:
        pass
    slot = getattr(ad, "action_slot", None)
    for layer in action.layers:
        for strip in layer.strips:
            if hasattr(strip, "channelbag"):
                bag = strip.channelbag(slot) if slot else None
                if bag is not None and hasattr(bag, "fcurves"):
                    return bag.fcurves
    return None


def fcurve_info(object_name: str, data_path: str = "") -> dict:
    """Listar fcurves de la acción del objeto (canales y keyframes)."""
    obj = _get_obj(object_name)
    ad = getattr(obj, "animation_data", None)
    action = ad.action if ad else None
    fcurves = _action_fcurves(obj)
    if action is None or fcurves is None:
        return {"object": object_name, "fcurves": [], "note": "sin acción de animación"}
    out = []
    for fc in fcurves:
        if data_path and fc.data_path != data_path:
            continue
        out.append(
            {
                "data_path": fc.data_path,
                "index": fc.array_index,
                "keys": [
                    {"frame": round(kp.co.x, 3), "value": round(kp.co.y, 4)}
                    for kp in fc.keyframe_points
                ],
            }
        )
    return {"object": object_name, "action": action.name, "fcurves": out}


def fcurve_set_key(
    object_name: str,
    data_path: str,
    index: int,
    frame: float,
    value: float,
    interpolation: str = "BEZIER",
) -> dict:
    """Insertar/reemplazar un keyframe en un canal concreto (data_path + índice)."""
    obj = _get_obj(object_name)
    obj.keyframe_insert(data_path=data_path, index=index, frame=frame)
    fcurves = _action_fcurves(obj)
    fc = None
    if fcurves is not None:
        for candidate in fcurves:
            if candidate.data_path == data_path and candidate.array_index == index:
                fc = candidate
                break
    if fc is None:
        raise ValueError(f"No se creó el fcurve para {data_path}[{index}]")
    for kp in fc.keyframe_points:
        if abs(kp.co.x - frame) < 1e-4:
            kp.co.y = float(value)
            kp.interpolation = interpolation
    fc.update()
    return {
        "object": object_name,
        "channel": f"{data_path}[{index}]",
        "frame": frame,
        "value": value,
    }


def driver_add(
    object_name: str,
    data_path: str,
    index: int,
    expression: str,
    driver_vars: dict[str, str] = None,
) -> dict:
    """Añadir driver con expresión; driver_vars: {nombre_var: "obj@path"}."""
    obj = _get_obj(object_name)
    if obj.animation_data is None:
        obj.animation_data_create()
    fc = obj.driver_add(data_path, index)
    d = fc.driver
    d.type = "SCRIPTED"
    d.expression = expression
    for var_name, ref in (driver_vars or {}).items():
        var = d.variables.new()
        var.name = var_name
        target_obj, _, target_path = ref.partition("@")
        var.targets[0].id = bpy.data.objects.get(target_obj)
        var.targets[0].data_path = target_path or "location"
    return {"object": object_name, "channel": f"{data_path}[{index}]", "expression": expression}


def constraint_add(
    object_name: str, type: str, target: str = "", props: dict[str, Any] = None
) -> dict:
    """Añadir constraint al objeto (Copy_Location, Track_To, Child_Of, ...)."""
    obj = _get_obj(object_name)
    con = obj.constraints.new(type=type.upper())
    if target:
        t = bpy.data.objects.get(target)
        if t is None:
            raise ValueError(f"Objeto target no encontrado: {target}")
        con.target = t
    for k, v in (props or {}).items():
        if hasattr(con, k):
            setattr(con, k, v)
    return {"object": object_name, "constraint": con.name, "type": con.type}


def shape_key_add(object_name: str, name: str, from_mix: bool = False) -> dict:
    """Añadir shape key (crea la base 'Basis' si no existe)."""
    obj = _get_obj(object_name)
    if obj.type != "MESH":
        raise ValueError("shape keys solo en MESH")
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis")
    key = obj.shape_key_add(name=name, from_mix=from_mix)
    return {
        "object": object_name,
        "shape_key": key.name,
        "index": len(obj.data.shape_keys.key_blocks) - 1,
    }


def shape_key_set(
    object_name: str, name: str, value: float = None, move_verts: dict[str, list[float]] = None
) -> dict:
    """Ajustar valor (0-1) y/o desplazar vértices relativos de una shape key."""
    obj = _get_obj(object_name)
    keys = obj.data.shape_keys.key_blocks if obj.data.shape_keys else []
    key = next((k for k in keys if k.name == name), None)
    if key is None:
        raise ValueError(f"Shape key no encontrada: {name}")
    if value is not None:
        key.value = float(value)
    if move_verts:
        for idx_str, delta in move_verts.items():
            v = key.data[int(idx_str)]
            v.co = (v.co[0] + delta[0], v.co[1] + delta[1], v.co[2] + delta[2])
    return {"object": object_name, "shape_key": name, "value": key.value}


TOOLS = [
    Tool(
        "animation.fcurve_info",
        ToolCategory.ANIMATION,
        "Listar fcurves y keyframes de la acción del objeto",
        ToolPermission.READ_ONLY,
        {"object_name": {"type": "str", "required": True}, "data_path": {"type": "str"}},
    ),
    Tool(
        "animation.fcurve_set_key",
        ToolCategory.ANIMATION,
        "Keyframe en canal concreto (data_path + índice de array)",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "data_path": {"type": "str", "required": True},
            "index": {"type": "int", "required": True},
            "frame": {"type": "float", "required": True},
            "value": {"type": "float", "required": True},
            "interpolation": {"type": "str"},
        },
    ),
    Tool(
        "animation.driver_add",
        ToolCategory.ANIMATION,
        "Driver con expresión y variables {nombre: 'objeto@data_path'}",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "data_path": {"type": "str", "required": True},
            "index": {"type": "int", "required": True},
            "expression": {"type": "str", "required": True},
            "driver_vars": {"type": "dict"},
        },
    ),
    Tool(
        "animation.constraint_add",
        ToolCategory.ANIMATION,
        "Añadir constraint (Copy_Location, Track_To, Child_Of, ...) con props",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "type": {"type": "str", "required": True},
            "target": {"type": "str"},
            "props": {"type": "dict", "description": "Atributos extra del constraint"},
        },
    ),
    Tool(
        "animation.shape_key_add",
        ToolCategory.ANIMATION,
        "Añadir shape key (crea Basis si falta)",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "name": {"type": "str", "required": True},
            "from_mix": {"type": "bool"},
        },
    ),
    Tool(
        "animation.shape_key_set",
        ToolCategory.ANIMATION,
        "Valor y/o desplazamiento de vértices de una shape key",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "name": {"type": "str", "required": True},
            "value": {"type": "float"},
            "move_verts": {"type": "dict"},
        },
    ),
]

HANDLERS = {
    "animation.fcurve_info": fcurve_info,
    "animation.fcurve_set_key": fcurve_set_key,
    "animation.driver_add": driver_add,
    "animation.constraint_add": constraint_add,
    "animation.shape_key_add": shape_key_add,
    "animation.shape_key_set": shape_key_set,
}
