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


# ═══════════════════════════════════════════════════════════════
# Export avanzado (game/web/print) + optimización
# ═══════════════════════════════════════════════════════════════


def export_game_collision(object_name: str, engine: str = "unreal") -> dict:
    mod = _addon_module("export_advanced")
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise ValueError(f"Objeto no encontrado: {object_name}")
    mod.generate_game_engine_collision(obj, engine=engine)
    return {"object": object_name, "collision_for": engine}


def export_lods(object_name: str, ratios: list = None) -> dict:
    mod = _addon_module("export_advanced")
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise ValueError(f"Objeto no encontrado: {object_name}")
    mod.generate_lod_levels(obj, lod_ratios=ratios)
    return {"object": object_name, "lods": len(ratios) if ratios else 3}


def export_batch(directory: str, formats: list = None, selection_only: bool = False) -> dict:
    mod = _addon_module("export_advanced")
    mod.export_batch(directory, formats=formats, selection_only=selection_only)
    return {"directory": directory, "formats": formats or ["GLB", "FBX", "OBJ"]}


def export_for_target(target: str, filepath: str, engine: str = "unity", fmt: str = "STL") -> dict:
    """Export por destino: game/web/print/film."""
    mod = _addon_module("export_advanced")
    fn = {
        "game": mod.export_for_game_engine,
        "web": mod.export_for_web,
        "print": mod.export_for_print,
        "film": mod.export_for_film,
    }.get(target.lower())
    if fn is None:
        raise ValueError(f"target desconocido: {target} (game/web/print/film)")
    if target.lower() == "game":
        fn(filepath, engine=engine, selection_only=False)
    elif target.lower() == "print":
        fn(filepath, fmt=fmt, selection_only=False)
    else:
        fn(filepath, selection_only=False)
    return {"exported": filepath, "target": target.lower()}


def perf_optimize_scene() -> dict:
    mod = _addon_module("performance_optimizer")
    return mod.optimize_scene()


def perf_stats() -> dict:
    mod = _addon_module("performance_optimizer")
    return mod.get_performance_stats()


def perf_render_estimate() -> dict:
    mod = _addon_module("performance_optimizer")
    return mod.estimate_render_time()


def perf_auto_lod(object_name: str, distance_threshold: float = 10.0) -> dict:
    mod = _addon_module("performance_optimizer")
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise ValueError(f"Objeto no encontrado: {object_name}")
    mod.auto_lod(obj, distance_threshold=distance_threshold)
    return {"object": object_name, "auto_lod": True}


def perf_batch_optimize(target_faces: int = 10000) -> dict:
    mod = _addon_module("performance_optimizer")
    mod.batch_optimize(objects=None, target_faces=target_faces)
    return {"optimized": "toda la escena", "target_faces": target_faces}


def perf_memory_report() -> dict:
    try:
        mod = _addon_module("memory_optimizer")
        return mod.get_memory_report()
    except RuntimeError:
        return _addon_module("performance_optimizer").memory_usage()


# ═══════════════════════════════════════════════════════════════
# Planner + documentación + versionado
# ═══════════════════════════════════════════════════════════════


def plan_create(name: str, description: str = "") -> dict:
    mod = _addon_module("scene_planner")
    return mod.create_plan(name, description)


def plan_add_step(
    object_type: str,
    position: list,
    parent: str = "",
    anchor: str = "",
    collection: str = "",
    material: str = "",
) -> dict:
    mod = _addon_module("scene_planner")
    return mod.add_object_to_plan(
        object_type,
        tuple(position),
        parent=parent or None,
        anchor=anchor or None,
        collection=collection or None,
        material=material or None,
    )


def plan_execute() -> dict:
    mod = _addon_module("scene_planner")
    return mod.execute_plan()


def plan_get() -> dict:
    mod = _addon_module("scene_planner")
    return mod.get_plan()


def docs_scene() -> dict:
    mod = _addon_module("doc_generator")
    return mod.generate_scene_doc()


def docs_object(object_name: str) -> dict:
    mod = _addon_module("doc_generator")
    path = mod.generate_object_spec(object_name)
    return {"spec": str(path)}


def docs_export_json(filepath: str = "/tmp/opencode/scene_doc.json") -> dict:
    mod = _addon_module("doc_generator")
    mod.export_scene_json(filepath)
    return {"exported": filepath}


def vc_snapshot(label: str = "") -> dict:
    mod = _addon_module("version_control")
    vid = mod.create_snapshot(label or None)
    return {"version": vid}


def vc_restore(version_id: str) -> dict:
    mod = _addon_module("version_control")
    ok = mod.restore_version(version_id)
    return {"restored": bool(ok), "version": version_id}


def vc_list() -> dict:
    mod = _addon_module("version_control")
    return {"versions": mod.list_snapshots()}


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
    Tool(
        "export.game_collision",
        ToolCategory.IO,
        "Malla de colisión para game engine (unreal/unity/godot)",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "engine": {"type": "str"}},
    ),
    Tool(
        "export.lods",
        ToolCategory.IO,
        "Generar niveles de LOD para un objeto",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "ratios": {"type": "list"}},
    ),
    Tool(
        "export.batch",
        ToolCategory.IO,
        "Export batch de la escena/selección a varios formatos",
        ToolPermission.WRITE,
        {
            "directory": {"type": "str", "required": True},
            "formats": {"type": "list"},
            "selection_only": {"type": "bool"},
        },
    ),
    Tool(
        "export.for_target",
        ToolCategory.IO,
        "Export por destino: game/web/print/film",
        ToolPermission.WRITE,
        {
            "target": {"type": "str", "required": True},
            "filepath": {"type": "str", "required": True},
            "engine": {"type": "str"},
            "fmt": {"type": "str"},
        },
    ),
    Tool(
        "perf.optimize_scene",
        ToolCategory.SCENE_UTILS,
        "Optimización automática de la escena",
        ToolPermission.WRITE,
        {},
    ),
    Tool(
        "perf.stats",
        ToolCategory.SCENE_UTILS,
        "Estadísticas de rendimiento",
        ToolPermission.READ_ONLY,
        {},
    ),
    Tool(
        "perf.render_estimate",
        ToolCategory.RENDER,
        "Estimación de tiempo de render",
        ToolPermission.READ_ONLY,
        {},
    ),
    Tool(
        "perf.auto_lod",
        ToolCategory.OBJECTS,
        "LOD automático por distancia",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "distance_threshold": {"type": "float"},
        },
    ),
    Tool(
        "perf.batch_optimize",
        ToolCategory.SCENE_UTILS,
        "Optimizar toda la escena a un presupuesto de caras",
        ToolPermission.WRITE,
        {"target_faces": {"type": "int"}},
    ),
    Tool(
        "perf.memory_report",
        ToolCategory.SCENE_UTILS,
        "Informe de uso de memoria",
        ToolPermission.READ_ONLY,
        {},
    ),
    Tool(
        "plan.create",
        ToolCategory.SCENE_UTILS,
        "Crear plan de construcción de escena",
        ToolPermission.WRITE,
        {"name": {"type": "str", "required": True}, "description": {"type": "str"}},
    ),
    Tool(
        "plan.add_step",
        ToolCategory.SCENE_UTILS,
        "Añadir paso al plan (tipo, posición, parent/anchor/material)",
        ToolPermission.WRITE,
        {
            "object_type": {"type": "str", "required": True},
            "position": {"type": "list", "required": True},
            "parent": {"type": "str"},
            "anchor": {"type": "str"},
            "collection": {"type": "str"},
            "material": {"type": "str"},
        },
    ),
    Tool(
        "plan.execute",
        ToolCategory.SCENE_UTILS,
        "Ejecutar el plan en orden calculado",
        ToolPermission.WRITE,
        {},
    ),
    Tool(
        "plan.get",
        ToolCategory.SCENE_UTILS,
        "Ver el plan actual",
        ToolPermission.READ_ONLY,
        {},
    ),
    Tool(
        "docs.scene",
        ToolCategory.SCENE_UTILS,
        "Documentación completa de la escena",
        ToolPermission.READ_ONLY,
        {},
    ),
    Tool(
        "docs.object",
        ToolCategory.SCENE_UTILS,
        "Spec de documentación de un objeto",
        ToolPermission.READ_ONLY,
        {"object_name": {"type": "str", "required": True}},
    ),
    Tool(
        "docs.export_json",
        ToolCategory.SCENE_UTILS,
        "Exportar documentación de escena a JSON",
        ToolPermission.WRITE,
        {"filepath": {"type": "str"}},
    ),
    Tool(
        "vc.snapshot",
        ToolCategory.SCENE_UTILS,
        "Snapshot versionado (historial persistente)",
        ToolPermission.WRITE,
        {"label": {"type": "str"}},
    ),
    Tool(
        "vc.restore",
        ToolCategory.SCENE_UTILS,
        "Restaurar versión del historial",
        ToolPermission.WRITE,
        {"version_id": {"type": "str", "required": True}},
    ),
    Tool(
        "vc.list",
        ToolCategory.SCENE_UTILS,
        "Listar versiones guardadas",
        ToolPermission.READ_ONLY,
        {},
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
    "export.game_collision": export_game_collision,
    "export.lods": export_lods,
    "export.batch": export_batch,
    "export.for_target": export_for_target,
    "perf.optimize_scene": perf_optimize_scene,
    "perf.stats": perf_stats,
    "perf.render_estimate": perf_render_estimate,
    "perf.auto_lod": perf_auto_lod,
    "perf.batch_optimize": perf_batch_optimize,
    "perf.memory_report": perf_memory_report,
    "plan.create": plan_create,
    "plan.add_step": plan_add_step,
    "plan.execute": plan_execute,
    "plan.get": plan_get,
    "docs.scene": docs_scene,
    "docs.object": docs_object,
    "docs.export_json": docs_export_json,
    "vc.snapshot": vc_snapshot,
    "vc.restore": vc_restore,
    "vc.list": vc_list,
}
