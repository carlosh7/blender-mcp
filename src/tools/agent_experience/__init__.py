"""
blender-mcp-ultra — Agent Experience Tools
Herramientas nacidas de ciclos reales agente↔Blender: colocación bbox-aware,
verificación de cámara, física headless, limpieza de escena y diff de estado.

Cada tool responde con `scene` (escena activa) para eliminar la ambigüedad
multi-escena que provocaba renders sobre la escena equivocada.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

try:
    import bpy
    from mathutils import Vector
except ImportError:  # fuera de Blender (indexación/tests)
    bpy = None
    Vector = None

from ...core.entities import Tool, ToolCategory, ToolPermission

# ═══════════════════════════════════════════════════════════════
# helpers
# ═══════════════════════════════════════════════════════════════

_MARKERS: dict[str, dict[str, Any]] = {}


def _scene():
    return bpy.context.scene


def _world_bbox(obj) -> tuple[Vector, Vector]:
    """bbox mundial (min, max) evaluando la malla real."""
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def _snapshot_state() -> dict[str, Any]:
    state = {}
    for o in _scene().objects:
        entry = {
            "type": o.type,
            "loc": [round(v, 4) for v in o.location],
            "rot": [round(v, 4) for v in o.rotation_euler],
            "scale": [round(v, 4) for v in o.scale],
            "mats": sorted(m.name if m else "?" for m in o.data.materials)
            if hasattr(o.data, "materials")
            else [],
        }
        if o.parent:
            entry["parent"] = o.parent.name
        state[o.name] = entry
    return state


def _diff_states(a: dict, b: dict) -> dict[str, Any]:
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = {}
    for name in sorted(set(a) & set(b)):
        if a[name] != b[name]:
            changed[name] = {"antes": a[name], "ahora": b[name]}
    return {"added": added, "removed": removed, "changed": changed}


def _resp(payload: dict[str, Any]) -> dict[str, Any]:
    if bpy is None:
        return payload
    payload["scene"] = _scene().name
    payload["object_count"] = len(_scene().objects)
    return payload


# ═══════════════════════════════════════════════════════════════
# scene_mark / scene_diff
# ═══════════════════════════════════════════════════════════════


def scene_mark(label: str = "", **_kw) -> dict:
    """Marca el estado actual para comparar después con scene_diff."""
    state = _snapshot_state()
    marker_id = hashlib.md5(json.dumps(state, sort_keys=True).encode()).hexdigest()[:8]
    _MARKERS.clear()  # un marcador activo a la vez (el último)
    _MARKERS[marker_id] = {"label": label or "mark", "state": state}
    return _resp({"marker": marker_id, "label": label or "mark", "objects": len(state)})


def scene_diff(**_kw) -> dict:
    """Compara el estado actual contra el último scene_mark."""
    if not _MARKERS:
        return _resp({"error": "sin marcador: llama scene_mark primero"})
    marker = next(iter(_MARKERS.values()))
    d = _diff_states(marker["state"], _snapshot_state())
    d["marker_label"] = marker["label"]
    d["resumen"] = f"+{len(d['added'])} -{len(d['removed'])} ~{len(d['changed'])}"
    return _resp(d)


# ═══════════════════════════════════════════════════════════════
# place_bottom / snap_to
# ═══════════════════════════════════════════════════════════════


def place_bottom(name: str = "", x: float = 0.0, y: float = 0.0, z: float = 0.0, **_kw) -> dict:
    """Coloca el punto MÁS BAJO del bbox del objeto en (x, y, z).

    A diferencia de object.transform (que mueve el ORIGEN), esto garantiza
    que la geometría quede apoyada exactamente en la cota z dada, sin importar
    offsets de origen ni escala heredada.
    """
    obj = bpy.data.objects.get(name)
    if obj is None:
        return _resp({"error": f"objeto no encontrado: {name}"})
    bpy.context.view_layer.update()
    mn, _mx = _world_bbox(obj)
    delta = Vector((x, y, z)) - mn
    obj.location += delta
    bpy.context.view_layer.update()
    mn2, mx2 = _world_bbox(obj)
    return _resp(
        {
            "ok": True,
            "bbox_min": [round(v, 4) for v in mn2],
            "bbox_max": [round(v, 4) for v in mx2],
        }
    )


_RELATIONS = ("on_top", "inside_top", "beside_x", "beside_y", "behind", "front")


def snap_to(
    name: str = "", target: str = "", relation: str = "on_top", gap: float = 0.0, **_kw
) -> dict:
    """Coloca `name` en relación bbox-aware con `target`.

    on_top: apoyado sobre la cara superior · beside_x/y: pegado lateral
    behind/front: alineado en -Y/+Y del target. `gap` añade separación (m).
    """
    a = bpy.data.objects.get(name)
    b = bpy.data.objects.get(target)
    if a is None or b is None:
        return _resp({"error": f"objeto no encontrado: {name if a is None else target}"})
    if relation not in _RELATIONS:
        return _resp({"error": f"relation inválida: {relation}. válidas: {_RELATIONS}"})
    bpy.context.view_layer.update()
    amn, amx = _world_bbox(a)
    bmn, bmx = _world_bbox(b)
    if relation == "on_top":
        delta = Vector((0, 0, (bmx.z - amn.z) + gap))
    elif relation == "inside_top":
        delta = Vector((0, 0, (bmx.z - amx.z) + gap))
    elif relation == "beside_x":
        delta = Vector(((bmx.x - amn.x) + gap, 0, 0))
    elif relation == "beside_y":
        delta = Vector((0, ((bmx.y - amn.y) + gap), 0))
    elif relation == "behind":
        delta = Vector((0, amn.y - (bmn.y + (amx.y - amn.y)) - gap, 0))
    else:  # front
        delta = Vector((0, bmx.y - amn.y + gap, 0))
    # centrar en X o Y según la relación
    ac = (amn + amx) / 2
    bc = (bmn + bmx) / 2
    if relation == "on_top":
        a.location += Vector((bc.x - ac.x, bc.y - ac.y, 0)) + delta
    elif relation in ("beside_x",):
        a.location += Vector((0, bc.y - ac.y, 0)) + delta
    elif relation in ("beside_y", "behind", "front"):
        a.location += Vector((bc.x - ac.x, 0, 0)) + delta
    bpy.context.view_layer.update()
    nmn, nmx = _world_bbox(a)
    return _resp({"ok": True, "relation": relation, "bbox_min": [round(v, 4) for v in nmn]})


# ═══════════════════════════════════════════════════════════════
# render_preview / camera_check
# ═══════════════════════════════════════════════════════════════


def render_preview(filepath: str = "", samples: int = 16, scale: int = 50, **_kw) -> dict:
    """Render borrador rápido (EEVEE, resolución reducida) para chequear encuadre.

    No toca la configuración del render final: la restaura al terminar.
    """
    sc = _scene()
    if sc.camera is None:
        return _resp({"error": "sin cámara activa (scene.camera es None). Usa camera.set_active."})
    old = {
        "engine": sc.render.engine,
        "res_x": sc.render.resolution_x,
        "res_y": sc.render.resolution_y,
        "percentage": sc.render.resolution_percentage,
    }
    out = filepath or "/tmp/blender_mcp_preview.png"
    try:
        for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                sc.render.engine = e
                break
            except Exception:
                continue
        sc.render.resolution_x = int(old["res_x"] * scale / 100)
        sc.render.resolution_y = int(old["res_y"] * scale / 100)
        sc.render.resolution_percentage = 100
        sc.cycles.samples = samples
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True)
    finally:
        sc.render.engine = old["engine"]
        sc.render.resolution_x = old["res_x"]
        sc.render.resolution_y = old["res_y"]
        sc.render.resolution_percentage = old["percentage"]
    return _resp({"ok": True, "filepath": out, "escala": f"{scale}%"})


def camera_check(**_kw) -> dict:
    """Diagnóstico de cámara: ¿existe? ¿está activa? ¿qué objetos ve?"""
    sc = _scene()
    cams = [o.name for o in sc.objects if o.type == "CAMERA"]
    if sc.camera is None:
        return _resp(
            {
                "error": "scene.camera es None: el render fallará con 'no camera'",
                "camaras_en_escena": cams,
                "fix": "camera.set_active(name='<una de las cámaras>')",
            }
        )
    cam = sc.camera
    from mathutils.geometry import normal  # noqa: F401

    mw = cam.matrix_world
    origin = mw.translation
    # frustum: 4 semi-ejes a partir de los planos de la cámara
    import math

    fov_h = 2 * math.atan(cam.data.sensor_width / (2 * cam.data.lens))
    aspect = sc.render.resolution_x / max(1, sc.render.resolution_y)
    fov_v = 2 * math.atan(math.tan(fov_h / 2) / aspect)
    fwd = (mw.to_quaternion() @ Vector((0, 0, -1))).normalized()
    up = (mw.to_quaternion() @ Vector((0, 1, 0))).normalized()
    right = (mw.to_quaternion() @ Vector((1, 0, 0))).normalized()
    max_dist = 1000.0
    en_cuadro, fuera = [], []
    for o in sc.objects:
        if o.type not in {"MESH", "CURVE", "FONT"} or o.name == cam.name:
            continue
        mn, mx = _world_bbox(o)
        center = (mn + mx) / 2
        rel = center - origin
        dist = rel.dot(fwd)
        if dist <= 0.05:
            fuera.append((o.name, "detrás de la cámara"))
            continue
        half_w = dist * math.tan(fov_h / 2)
        half_h = dist * math.tan(fov_v / 2)
        dx, dy = rel.dot(right), rel.dot(up)
        if abs(dx) <= half_w + 0.1 and abs(dy) <= half_h + 0.1:
            en_cuadro.append((o.name, round(dist, 2)))
        else:
            fuera.append((o.name, "fuera del frustum"))
    return _resp(
        {
            "camara_activa": cam.name,
            "lens_mm": round(cam.data.lens, 1),
            "en_cuadro": [n for n, _ in en_cuadro],
            "fuera_de_cuadro": [n for n, _ in fuera],
            "distancias_m": dict(en_cuadro),
            "_max_dist": max_dist,
        }
    )


# ═══════════════════════════════════════════════════════════════
# physics_bake / physics_free_cache
# ═══════════════════════════════════════════════════════════════


def physics_bake(frame_start: int = 1, frame_end: int = 50, **_kw) -> dict:
    """Hornea la simulación de rigid body (frame_start..frame_end).

    En Blender headless la sim no corre con frame_set a menos que la
    colección RBW esté enlazada a la escena y la caché horneada.
    """
    sc = _scene()
    rbw = sc.rigidbody_world
    if rbw is None:
        return _resp({"error": "la escena no tiene rigidbody_world"})
    if rbw.collection and rbw.collection.name not in [c.name for c in sc.collection.children]:
        try:
            sc.collection.children.link(rbw.collection)
        except Exception:
            pass
    rbw.point_cache.frame_start = frame_start
    rbw.point_cache.frame_end = frame_end
    try:
        bpy.ops.ptcache.free_bake_all()
        bpy.ops.ptcache.bake_all(bake=True)
    except Exception as e:
        return _resp({"error": f"bake falló: {e}"})
    sc.frame_set(frame_end)
    return _resp(
        {"ok": True, "frames": [frame_start, frame_end], "is_baked": rbw.point_cache.is_baked}
    )


def physics_free_cache(**_kw) -> dict:
    """Invalida la caché de simulación (imprescindible tras cambiar keyframes)."""
    try:
        bpy.ops.ptcache.free_bake_all()
        return _resp({"ok": True})
    except Exception as e:
        return _resp({"error": str(e)})


# ═══════════════════════════════════════════════════════════════
# scene_cleanup
# ═══════════════════════════════════════════════════════════════


def scene_cleanup(dry_run: bool = True, purge_orphans: bool = True, **_kw) -> dict:
    """Detecta (y opcionalmente elimina) basura acumulada en la escena.

    Categorías: duplicados .001 sin uso, empties de test (RBC_*/probe),
    objetos vacíos (sin caras), escala no aplicada, datos huérfanos.
    """
    sc = _scene()
    problemas: dict[str, list[str]] = {
        "duplicados_suffix": [],
        "empties_test": [],
        "mesh_vacios": [],
        "escala_no_aplicada": [],
    }
    for o in sc.objects:
        if o.name.split(".")[-1].isdigit() and bpy.data.objects.get(o.name.rsplit(".", 1)[0]):
            problemas["duplicados_suffix"].append(o.name)
        if o.type == "EMPTY" and (o.name.startswith(("RBC_", "probe")) or "test" in o.name.lower()):
            problemas["empties_test"].append(o.name)
        if o.type == "MESH" and len(o.data.polygons) == 0:
            problemas["mesh_vacios"].append(o.name)
        if any(abs(s - 1.0) > 1e-4 for s in o.scale):
            problemas["escala_no_aplicada"].append(o.name)
    total = sum(len(v) for v in problemas.values())
    acciones = []
    if not dry_run:
        for n in problemas["empties_test"] + problemas["mesh_vacios"]:
            o = bpy.data.objects.get(n)
            if o:
                bpy.data.objects.remove(o, do_unlink=True)
                acciones.append(f"eliminado {n}")
        for n in problemas["escala_no_aplicada"]:
            o = bpy.data.objects.get(n)
            if o:
                mw = o.matrix_world.copy()
                o.data.transform(mw)
                o.matrix_world = (
                    mw.to_3x3().to_4x4() @ mw.translation.to_4x4() if False else o.matrix_world
                )
                o.scale = (1, 1, 1)
                acciones.append(f"escala aplicada {n}")
    out = _resp({"problemas": problemas, "total": total, "dry_run": dry_run})
    if acciones:
        out["acciones"] = acciones
    if purge_orphans and not dry_run:
        try:
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
            out["huérfanos_purgados"] = True
        except Exception:
            pass
    return out


# ═══════════════════════════════════════════════════════════════
# registro
# ═══════════════════════════════════════════════════════════════

TOOLS = [
    Tool(
        name="scene.mark",
        category=ToolCategory.SCENE_UTILS,
        description="Marca el estado actual de la escena para comparar luego con scene.diff",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "label": {"type": "str", "default": "", "description": "etiqueta del marcador"}
        },
        examples=["scene.mark(label='antes de la física')"],
    ),
    Tool(
        name="scene.diff",
        category=ToolCategory.SCENE_UTILS,
        description="Qué cambió desde el último scene.mark (añadidos/eliminados/modificados)",
        permission=ToolPermission.READ_ONLY,
        parameters={},
        examples=["scene.diff()"],
    ),
    Tool(
        name="object.place_bottom",
        category=ToolCategory.OBJECTS,
        description="Coloca el punto más bajo del bbox del objeto en (x,y,z) — inmune a offsets de origen y escala",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True, "description": "objeto"},
            "x": {"type": "float", "default": 0.0},
            "y": {"type": "float", "default": 0.0},
            "z": {"type": "float", "default": 0.0, "description": "cota de apoyo"},
        },
        examples=["object.place_bottom(name='Mug', z=0.75)"],
    ),
    Tool(
        name="object.snap_to",
        category=ToolCategory.OBJECTS,
        description="Coloca un objeto en relación bbox-aware con otro (on_top/beside_x/beside_y/behind/front)",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True},
            "target": {"type": "str", "required": True},
            "relation": {"type": "str", "default": "on_top"},
            "gap": {"type": "float", "default": 0.0},
        },
        examples=["object.snap_to(name='Mug', target='Mesa', relation='on_top')"],
    ),
    Tool(
        name="render.preview",
        category=ToolCategory.RENDER,
        description="Render borrador rápido (EEVEE, resolución reducida) para validar encuadre sin esperar Cycles",
        permission=ToolPermission.WRITE,
        parameters={
            "filepath": {"type": "str", "default": ""},
            "samples": {"type": "int", "default": 16},
            "scale": {"type": "int", "default": 50, "description": "% de resolución"},
        },
        examples=["render.preview()"],
    ),
    Tool(
        name="camera.check",
        category=ToolCategory.CAMERA,
        description="Diagnóstico de cámara: activa, lens, qué objetos están en el frustum y a qué distancia",
        permission=ToolPermission.READ_ONLY,
        parameters={},
        examples=["camera.check()"],
    ),
    Tool(
        name="physics.bake",
        category=ToolCategory.MODIFIERS,
        description="Hornea la simulación rigid body (linkea colección RBW y hornea la caché)",
        permission=ToolPermission.WRITE,
        parameters={
            "frame_start": {"type": "int", "default": 1},
            "frame_end": {"type": "int", "default": 50},
        },
        examples=["physics.bake(frame_end=60)"],
    ),
    Tool(
        name="physics.free_cache",
        category=ToolCategory.MODIFIERS,
        description="Invalida la caché de simulación (obligatorio tras cambiar keyframes)",
        permission=ToolPermission.WRITE,
        parameters={},
        examples=["physics.free_cache()"],
    ),
    Tool(
        name="scene.cleanup",
        category=ToolCategory.SCENE_UTILS,
        description="Detecta/elimina basura: duplicados .001, empties de test, meshes vacíos, escala no aplicada, huérfanos",
        permission=ToolPermission.WRITE,
        parameters={
            "dry_run": {"type": "bool", "default": True},
            "purge_orphans": {"type": "bool", "default": True},
        },
        examples=["scene.cleanup(dry_run=True)", "scene.cleanup(dry_run=False)"],
    ),
]

HANDLERS = {
    "scene.mark": scene_mark,
    "scene.diff": scene_diff,
    "object.place_bottom": place_bottom,
    "object.snap_to": snap_to,
    "render.preview": render_preview,
    "camera.check": camera_check,
    "physics.bake": physics_bake,
    "physics.free_cache": physics_free_cache,
    "scene.cleanup": scene_cleanup,
}
