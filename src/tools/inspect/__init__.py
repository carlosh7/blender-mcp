"""
blender-mcp-ultra — Inspection Views ("eyes" sin VLM)
Renders de inspección determinísticos y baratos: silueta, wireframe,
UV-checker, normales y turntable. El agente VERIFICA sin depender de un
proveedor de visión.

Inspirado en OhaoTech/niua-blender-mcp — reimplementado para blender-mcp-ultra.
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict

try:
    import bpy
except ImportError:  # fuera de Blender (indexación/tests)
    bpy = None

from ...core.entities import Tool, ToolCategory, ToolPermission

_OUT_DIR = "/tmp/blender_mcp_inspect"


def _scene():
    return bpy.context.scene


def _resp(payload):
    if bpy is not None:
        payload["scene"] = _scene().name
    return payload


def _frame_object(cam, obj, padding: float = 1.6):
    """Coloca la cámara a distancia fija mirando el objeto (bbox-aware)."""
    import mathutils

    pts = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    mn = mathutils.Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = mathutils.Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (mn + mx) / 2
    radius = max(0.05, (mx - mn).length / 2)
    dist = radius * padding * (cam.data.lens / 35.0)
    direction = mathutils.Vector((1.0, -1.0, 0.6)).normalized()
    cam.location = center + direction * dist
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _setup_world_flat(strength: float = 1.0, color=(1, 1, 1)):
    sc = _scene()
    old = sc.world
    w = bpy.data.worlds.new("InspectWorld")
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (*color, 1.0)
    bg.inputs[1].default_value = strength
    sc.world = w
    return old


def inspect_view(
    name: str = "", mode: str = "silhouette", filepath: str = "", samples: int = 16, **_kw
) -> dict:
    """Render de inspección de un objeto: silhouette | wireframe | uv_checker | normals.

    - silhouette: objeto blanco plano sobre fondo negro (leer la FORMA)
    - wireframe: malla visible (leer la DENSIDAD/topología)
    - uv_checker: tablero de ajedrez UV (leer el DESPLIEGUE)
    - normals: normales en color (leer la ORIENTACIÓN de caras)
    """
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        return _resp({"error": f"mesh no encontrado: {name}"})
    sc = _scene()
    if sc.camera is None:
        cam_data = bpy.data.cameras.new("InspectCam")
        cam = bpy.data.objects.new("InspectCam", cam_data)
        sc.collection.objects.link(cam)
        sc.camera = cam
    else:
        cam = sc.camera
    _frame_object(cam, obj)

    old_world = sc.world
    old_hide = [o.name for o in sc.objects if o.hide_render]
    # aislar: ocultar todo menos el objeto
    for o in sc.objects:
        if o != obj and o.type in {"MESH", "CURVE", "FONT"}:
            o.hide_render = True

    old_mat = obj.data.materials[:] if obj.data.materials else []
    m = bpy.data.materials.new("InspectTmp")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")

    if mode == "silhouette":
        _setup_world_flat(0.02, (0, 0, 0))
        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
        bsdf.inputs["Roughness"].default_value = 1.0
        bsdf.inputs["Metallic"].default_value = 0.0
    elif mode == "wireframe":
        _setup_world_flat(1.0, (0.05, 0.05, 0.05))
        wire = nt.nodes.new("ShaderNodeWireframe")
        wire.inputs["Thickness"].default_value = 1.2
        emit = nt.nodes.new("ShaderNodeEmission")
        emit.inputs["Color"].default_value = (0.2, 0.9, 1.0, 1)
        nt.links.new(wire.outputs["Fac"], emit.inputs["Strength"])
        nt.links.new(emit.outputs["Emission"], nt.nodes["Material Output"].inputs["Surface"])
    elif mode == "uv_checker":
        _setup_world_flat(1.0)
        checker = nt.nodes.new("ShaderNodeTexChecker")
        checker.inputs["Scale"].default_value = 12.0
        checker.inputs["Color1"].default_value = (0.85, 0.85, 0.85, 1)
        checker.inputs["Color2"].default_value = (0.15, 0.3, 0.7, 1)
        uv = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(uv.outputs["UV"], checker.inputs["Vector"])
        nt.links.new(checker.outputs["Color"], bsdf.inputs["Base Color"])
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")
    elif mode == "normals":
        _setup_world_flat(0.8)
        geom = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(geom.outputs["Normal"], sep.inputs["Color"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(sep.outputs["Red"], mix.inputs[6])
        nt.links.new(sep.outputs["Green"], mix.inputs[7])
        mix.blend_type = "MIX"
        nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    else:
        return _resp(
            {"error": f"mode inválido: {mode}. válidos: silhouette/wireframe/uv_checker/normals"}
        )

    obj.data.materials.clear()
    obj.data.materials.append(m)

    out = filepath or os.path.join(_OUT_DIR, f"{name}_{mode}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    old_engine = sc.render.engine
    old_res = (sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage)
    try:
        for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                sc.render.engine = e
                break
            except Exception:
                continue
        sc.render.resolution_x = 800
        sc.render.resolution_y = 600
        sc.render.resolution_percentage = 100
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True)
    finally:
        sc.render.engine = old_engine
        sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = old_res
        obj.data.materials.clear()
        for mm in old_mat:
            obj.data.materials.append(mm)
        sc.world = old_world
        for o in sc.objects:
            if o.name in old_hide:
                o.hide_render = True
            elif o.type in {"MESH", "CURVE", "FONT"}:
                o.hide_render = False
    return _resp({"ok": True, "mode": mode, "filepath": out})


def inspect_turntable(name: str = "", frames: int = 6, filepath_pattern: str = "", **_kw) -> dict:
    """Órbita automática alrededor del objeto: N renders desde ángulos equidistantes."""
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        return _resp({"error": f"mesh no encontrado: {name}"})
    sc = _scene()
    cam = sc.camera or bpy.data.objects.new("InspectCam", bpy.data.cameras.new("InspectCam"))
    if sc.camera is None:
        sc.collection.objects.link(cam)
        sc.camera = cam
    import mathutils

    pts = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    center = (
        (min(p.x for p in pts) + max(p.x for p in pts)) / 2,
        (min(p.y for p in pts) + max(p.y for p in pts)) / 2,
        (min(p.z for p in pts) + max(p.z for p in pts)) / 2,
    )
    center = mathutils.Vector(center)
    radius = max(0.05, max((p - center).length for p in pts))
    dist = radius * 2.4
    out_dir = _OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    pattern = filepath_pattern or os.path.join(out_dir, f"{name}_turn_{{i}}.png")
    shots = []
    old_cam_loc, old_cam_rot = cam.location.copy(), cam.rotation_euler.copy()
    old_world = sc.world
    _setup_world_flat(1.0, (0.85, 0.85, 0.9))
    old_engine = sc.render.engine
    old_res = (sc.render.resolution_x, sc.render.resolution_y)
    try:
        for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                sc.render.engine = e
                break
            except Exception:
                continue
        sc.render.resolution_x, sc.render.resolution_y = 640, 480
        for i in range(max(2, min(frames, 24))):
            ang = 2 * math.pi * i / max(2, frames)
            cam.location = center + mathutils.Vector(
                (math.cos(ang) * dist, math.sin(ang) * dist, dist * 0.35)
            )
            d = (center - cam.location).normalized()
            cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
            out = pattern.format(i=i)
            sc.render.filepath = out
            bpy.ops.render.render(write_still=True)
            shots.append(out)
    finally:
        cam.location, cam.rotation_euler = old_cam_loc, old_cam_rot
        sc.world = old_world
        sc.render.engine = old_engine
        sc.render.resolution_x, sc.render.resolution_y = old_res
    return _resp({"ok": True, "renders": shots, "total": len(shots)})


def inspect_topology(name: str = "", **_kw) -> dict:
    """Salud de la topología: ngons, triángulos, poles, UV, densidad, escala."""
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        return _resp({"error": f"mesh no encontrado: {name}"})
    me = obj.data
    tris = ngons = quads = 0
    poles5 = poles3 = 0
    for p in me.polygons:
        n = p.loop_total
        if n == 3:
            tris += 1
        elif n == 4:
            quads += 1
        elif n > 4:
            ngons += 1
    for v in me.vertices:
        c = 0
        for e in me.edges:
            if v.index in e.vertices:
                c += 1
        if c > 5:
            poles5 += 1
        elif c < 4 and c > 0:
            poles3 += 1
    area = sum(p.area for p in me.polygons)
    densidad = len(me.polygons) / area if area > 0 else 0
    uv_ok = bool(me.uv_layers)
    escala_ok = all(abs(s - 1.0) < 1e-4 for s in obj.scale)
    score = 100
    score -= min(30, ngons * 2)
    score -= min(20, poles5)
    score -= 0 if uv_ok else 25
    score -= 0 if escala_ok else 15
    return _resp(
        {
            "vertices": len(me.vertices),
            "caras": {"tris": tris, "quads": quads, "ngons": ngons},
            "poles_5+": poles5,
            "uv": uv_ok,
            "escala_aplicada": escala_ok,
            "densidad_caras_m2": round(densidad, 1),
            "area_total_m2": round(area, 3),
            "score_topologia": max(0, score),
            "avisos": [
                a
                for a, bad in [
                    (f"{ngons} ngons (preferir quads)", ngons > 0),
                    ("sin UV map", not uv_ok),
                    ("escala no aplicada", not escala_ok),
                    (f"{poles5} poles de 5+", poles5 > len(me.vertices) * 0.05),
                ]
                if bad
            ],
        }
    )


TOOLS = [
    Tool(
        name="inspect.view",
        category=ToolCategory.RENDER,
        description="Render de inspección determinístico: silhouette (forma), wireframe (densidad), uv_checker (despliegue) o normals (orientación). No requiere VLM",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True},
            "mode": {"type": "str", "default": "silhouette"},
            "filepath": {"type": "str", "default": ""},
        },
        examples=[
            "inspect.view(name='Mug', mode='silhouette')",
            "inspect.view(name='Mug', mode='uv_checker')",
        ],
    ),
    Tool(
        name="inspect.turntable",
        category=ToolCategory.RENDER,
        description="Órbita automática: N renders equidistantes alrededor del objeto",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True},
            "frames": {"type": "int", "default": 6},
        },
        examples=["inspect.turntable(name='Mug', frames=8)"],
    ),
    Tool(
        name="inspect.topology",
        category=ToolCategory.SCENE_UTILS,
        description="Salud de topología: tris/quads/ngons, poles, UV, escala, densidad y score 0-100",
        permission=ToolPermission.READ_ONLY,
        parameters={"name": {"type": "str", "required": True}},
        examples=["inspect.topology(name='Mug')"],
    ),
]

HANDLERS = {
    "inspect.view": inspect_view,
    "inspect.turntable": inspect_turntable,
    "inspect.topology": inspect_topology,
}
