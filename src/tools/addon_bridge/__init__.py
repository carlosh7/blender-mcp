"""
blender-mcp-ultra — Addon Bridge
Expone módulos veteranos del addon (pbr_factory, sculpt_engine, anti_blockout)
como tools del registry. Requiere el repo dentro de Blender (raíz en sys.path).
"""

from typing import Any, Dict, List

from ...core.entities import Tool, ToolCategory, ToolPermission

try:
    import bpy
except ImportError:  # fuera de Blender: solo definiciones
    bpy = None


def _addon_module(name: str):
    try:
        import addon

        return __import__(f"addon.{name}", fromlist=[name])
    except Exception as e:  # pragma: no cover - solo dentro de Blender
        raise RuntimeError(f"addon.{name} no disponible: {e}") from e


# ═══════════════════════════════════════════════════════════════
# PBR factory
# ═══════════════════════════════════════════════════════════════

_PBR_KINDS = {
    "wood": "create_pbr_wood",
    "fabric": "create_pbr_fabric",
    "metal": "create_pbr_metal",
    "leather": "create_pbr_leather",
    "stone": "create_pbr_stone",
    "glass": "create_pbr_glass",
    "ceramic": "create_pbr_ceramic",
    "plastic": "create_pbr_plastic",
    "rubber": "create_pbr_rubber",
}


def pbr_material(kind: str, name: str, color: list[float] = None, **kwargs) -> dict:
    """Material PBR procedural del factory (wood/metal/glass/ceramic/...)."""
    mod = _addon_module("pbr_factory")
    fn = getattr(mod, _PBR_KINDS[kind.lower()], None)
    if fn is None:
        raise ValueError(f"kind desconocido: {kind}. Válidos: {sorted(_PBR_KINDS)}")
    args = [name]
    if color:
        args.append(tuple(color))
    mat = fn(*args, **kwargs)
    return {"material": mat.name if hasattr(mat, "name") else str(mat), "kind": kind.lower()}


# ═══════════════════════════════════════════════════════════════
# Sculpt
# ═══════════════════════════════════════════════════════════════


def sculpt_base(primitive_type: str = "sphere", subdivisions: int = 4) -> dict:
    mod = _addon_module("organic.sculpt_engine")
    obj = mod.create_sculpt_base(primitive_type=primitive_type, subdivisions=subdivisions)
    return {"object": obj.name, "mode": obj.mode}


def sculpt_voxel_remesh(object_name: str, voxel_size: float = 0.02) -> dict:
    mod = _addon_module("organic.sculpt_engine")
    obj = bpy.data.objects.get(object_name)
    ok = mod.voxel_remesh_sculpt(obj, voxel_size=voxel_size)
    return {"object": object_name, "remeshed": bool(ok)}


def sculpt_multires(object_name: str, levels: int = 3) -> dict:
    mod = _addon_module("organic.sculpt_engine")
    obj = bpy.data.objects.get(object_name)
    ok = mod.apply_multiresolution_sculpt(obj, levels=levels)
    return {"object": object_name, "multires": bool(ok)}


def sculpt_smooth(object_name: str, iterations: int = 5) -> dict:
    mod = _addon_module("organic.sculpt_engine")
    obj = bpy.data.objects.get(object_name)
    mod.smooth_entire_mesh(obj, iterations=iterations)
    return {"object": object_name, "smoothed": iterations}


def sculpt_brush(brush_name: str, strength: float = 0.5, radius: float = 0.1) -> dict:
    mod = _addon_module("organic.sculpt_engine")
    mod.set_sculpt_brush(brush_name, strength=strength, radius=radius)
    return {"brush": brush_name, "strength": strength, "radius": radius}


# ═══════════════════════════════════════════════════════════════
# Anti-blockout
# ═══════════════════════════════════════════════════════════════


def blockout_check(object_name: str = "") -> dict:
    mod = _addon_module("anti_blockout")
    if object_name:
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Objeto no encontrado: {object_name}")
        return mod.is_blockout(obj)
    return mod.validate_scene_blockout()


def blockout_fix(object_name: str) -> dict:
    mod = _addon_module("anti_blockout")
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise ValueError(f"Objeto no encontrado: {object_name}")
    return mod.auto_fix_blockout(obj)


# ═══════════════════════════════════════════════════════════════
# Definiciones
# ═══════════════════════════════════════════════════════════════

TOOLS = [
    Tool(
        "material.pbr",
        ToolCategory.MATERIALS,
        "Material PBR procedural: wood/fabric/metal/leather/stone/glass/ceramic/plastic/rubber",
        ToolPermission.WRITE,
        {
            "kind": {"type": "str", "required": True},
            "name": {"type": "str", "required": True},
            "color": {"type": "list", "description": "[r, g, b] 0-1"},
        },
    ),
    Tool(
        "sculpt.base",
        ToolCategory.OBJECTS,
        "Base de escultura (sphere/cube) con densidad preparada",
        ToolPermission.WRITE,
        {"primitive_type": {"type": "str"}, "subdivisions": {"type": "int"}},
    ),
    Tool(
        "sculpt.voxel_remesh",
        ToolCategory.OBJECTS,
        "Voxel remesh para esculpido",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "voxel_size": {"type": "float"}},
    ),
    Tool(
        "sculpt.multires",
        ToolCategory.OBJECTS,
        "Multiresolution subdivide",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "levels": {"type": "int"}},
    ),
    Tool(
        "sculpt.smooth",
        ToolCategory.OBJECTS,
        "Suavizado completo de la malla",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "iterations": {"type": "int"}},
    ),
    Tool(
        "sculpt.brush",
        ToolCategory.OBJECTS,
        "Pincel de esculpido activo (nombre, fuerza, radio)",
        ToolPermission.WRITE,
        {
            "brush_name": {"type": "str", "required": True},
            "strength": {"type": "float"},
            "radius": {"type": "float"},
        },
    ),
    Tool(
        "scene.check_blockout",
        ToolCategory.SCENE_UTILS,
        "Detecta blockout (primitivas sin detalle) en un objeto o toda la escena",
        ToolPermission.READ_ONLY,
        {"object_name": {"type": "str"}},
    ),
    Tool(
        "scene.fix_blockout",
        ToolCategory.SCENE_UTILS,
        "Autocorrección anti-blockout (bisel, suavizado, material)",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}},
    ),
]

HANDLERS = {
    "material.pbr": pbr_material,
    "sculpt.base": sculpt_base,
    "sculpt.voxel_remesh": sculpt_voxel_remesh,
    "sculpt.multires": sculpt_multires,
    "sculpt.smooth": sculpt_smooth,
    "sculpt.brush": sculpt_brush,
    "scene.check_blockout": blockout_check,
    "scene.fix_blockout": blockout_fix,
}
