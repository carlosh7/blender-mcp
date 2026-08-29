"""
blender-mcp-ultra — Spatial Intelligence Tools
Capa semántica sobre el sistema de anclas: posicionamiento por relación con
chequeo de colisión, queries espaciales, dimensiones reales y plano ASCII.

Inspirado en mlolson/blender-orchestrator (MIT) — reimplementado para el
registry de blender-mcp-ultra.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

try:
    import bpy
    from mathutils import Vector
except ImportError:  # fuera de Blender (indexación/tests)
    bpy = None
    Vector = None

from ...core.entities import Tool, ToolCategory, ToolPermission

# ═══════════════════════════════════════════════════════════════
# DB de dimensiones reales (metros) — 60 objetos comunes
# ═══════════════════════════════════════════════════════════════

REAL_DIMENSIONS: dict[str, tuple[float, float, float]] = {
    # (ancho, profundidad, alto)
    "silla": (0.45, 0.45, 0.9),
    "mesa_comedor": (1.6, 0.9, 0.75),
    "mesa_escritorio": (1.4, 0.7, 0.75),
    "mesa_cafe": (1.1, 0.6, 0.45),
    "sofa_2plazas": (1.6, 0.9, 0.85),
    "sofa_3plazas": (2.1, 0.9, 0.85),
    "cama_doble": (1.6, 2.0, 0.5),
    "cama_individual": (0.9, 2.0, 0.5),
    "mesita_noche": (0.45, 0.4, 0.55),
    "armario": (1.2, 0.6, 2.1),
    "estanteria": (0.9, 0.35, 1.8),
    "puerta": (0.9, 0.08, 2.1),
    "ventana": (1.2, 0.1, 1.4),
    "mesada_cocina": (1.8, 0.65, 0.9),
    "nevera": (0.7, 0.7, 1.8),
    "horno": (0.6, 0.6, 0.9),
    "lavadora": (0.6, 0.6, 0.85),
    "tv_55": (1.24, 0.08, 0.72),
    "monitor_27": (0.62, 0.2, 0.4),
    "teclado": (0.44, 0.15, 0.03),
    "raton": (0.07, 0.12, 0.04),
    "lampara_escritorio": (0.2, 0.2, 0.45),
    "lampara_pie": (0.35, 0.35, 1.6),
    "taza": (0.09, 0.12, 0.1),
    "plato": (0.27, 0.27, 0.03),
    "botella_vino": (0.08, 0.08, 0.3),
    "libro": (0.15, 0.03, 0.23),
    "maceta_pequena": (0.15, 0.15, 0.15),
    "maceta_grande": (0.4, 0.4, 0.5),
    "planta_interior": (0.5, 0.5, 1.2),
    "alfombra_sala": (2.0, 1.4, 0.02),
    "cuadro_a4": (0.21, 0.03, 0.3),
    "espejo_pared": (0.6, 0.05, 0.8),
    "toalla": (0.5, 0.1, 0.7),
    "escalera": (0.5, 1.0, 2.2),
    "escritorio_pie": (0.6, 0.6, 1.05),
    "sillon": (0.8, 0.8, 1.0),
    "taburete": (0.35, 0.35, 0.65),
    "aparador": (1.5, 0.45, 0.85),
    "vestidor": (1.8, 0.6, 2.2),
    "ducha": (0.9, 0.9, 2.1),
    "banera": (1.7, 0.75, 0.6),
    "inodoro": (0.37, 0.65, 0.78),
    "lavabo": (0.6, 0.45, 0.85),
    "microondas": (0.5, 0.4, 0.3),
    "cafetera": (0.25, 0.25, 0.35),
    "tostadora": (0.28, 0.18, 0.19),
    "cocina_vitro": (0.6, 0.52, 0.05),
    "coche": (1.8, 4.5, 1.5),
    "bici": (0.6, 1.7, 1.1),
    "arbol_mediano": (3.0, 3.0, 6.0),
    "arbusto": (1.0, 1.0, 1.0),
    "valla_panel": (1.8, 0.05, 1.2),
    "farola": (0.3, 0.3, 4.5),
    "banco_parque": (1.8, 0.6, 0.85),
    "mesa_picnic": (1.8, 1.6, 0.75),
    "pizarra": (1.5, 0.05, 1.0),
    "proyector": (0.3, 0.25, 0.12),
}

# ═══════════════════════════════════════════════════════════════
# helpers
# ═══════════════════════════════════════════════════════════════


def _scene():
    return bpy.context.scene


def _resp(payload):
    if bpy is not None:
        payload["scene"] = _scene().name
    return payload


def _bbox(obj) -> tuple[Vector, Vector]:
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def _mesh_bvh_overlap(a, b) -> bool:
    """Chequeo de solape por bbox (rápido, suficiente para colocación)."""
    amn, amx = _bbox(a)
    bmn, bmx = _bbox(b)
    return not (
        amx.x <= bmn.x
        or amn.x >= bmx.x
        or amx.y <= bmn.y
        or amn.y >= bmx.y
        or amx.z <= bmn.z
        or amn.z >= bmx.z
    )


# ═══════════════════════════════════════════════════════════════
# spatial_place
# ═══════════════════════════════════════════════════════════════


def spatial_place(
    name: str = "",
    relation: str = "on_top",
    target: str = "",
    offset: float = 0.0,
    check_collision: bool = True,
    **_kw,
) -> dict:
    """Coloca un objeto respecto a otro con semántica espacial y chequeo de colisión.

    relation: on_top | beside_x | beside_y | behind | front | on_floor
    Ajusta también la rotación Z al centro del target. Si la colocación produce
    solape con un tercero, lo reporta (no lo bloquea).
    """
    a = bpy.data.objects.get(name)
    if a is None:
        return _resp({"error": f"objeto no encontrado: {name}"})
    if relation != "on_floor":
        b = bpy.data.objects.get(target)
        if b is None:
            return _resp({"error": f"target no encontrado: {target}"})

    # reutilizar snap_to vía import local del módulo hermano
    from ..agent_experience import _world_bbox
    from ..agent_experience import snap_to as _snap  # type: ignore

    if relation == "on_floor":
        bpy.context.view_layer.update()
        mn, _mx = _world_bbox(a)
        a.location += Vector((0, 0, -mn.z))
    else:
        r = _snap(name=name, target=target, relation=relation, gap=offset)
        if "error" in r:
            return _resp(r)

    bpy.context.view_layer.update()
    colisiones = []
    if check_collision:
        for o in _scene().objects:
            if o.type != "MESH" or o.name in (name, target):
                continue
            if _mesh_bvh_overlap(a, o):
                colisiones.append(o.name)
    mn, mx = _bbox(a)
    return _resp(
        {
            "ok": True,
            "relation": relation,
            "target": target,
            "centro": [round(v, 3) for v in ((mn + mx) / 2)],
            "colisiones_con": colisiones,
            "aviso": "solape detectado tras colocar" if colisiones else None,
        }
    )


# ═══════════════════════════════════════════════════════════════
# spatial_query
# ═══════════════════════════════════════════════════════════════


def spatial_query(
    on: str = "",
    near: str = "",
    radius: float = 1.0,
    name_contains: str = "",
    type_filter: str = "MESH",
    **_kw,
) -> dict:
    """Query espacial: ¿qué hay SOBRE un objeto? ¿qué está CERCA de otro?"""
    sc = _scene()
    resultados = []
    if on:
        base = bpy.data.objects.get(on)
        if base is None:
            return _resp({"error": f"objeto no encontrado: {on}"})
        bmn, bmx = _bbox(base)
        for o in sc.objects:
            if o.type != type_filter or o.name == on:
                continue
            mn, mx = _bbox(o)
            # "sobre": solapa en XY con la huella del base Y su base está a la
            # altura de la cara superior (± tolerancia)
            overlap_xy = not (mx.x <= bmn.x or mn.x >= bmx.x or mx.y <= bmn.y or mn.y >= bmx.y)
            apoyado = abs(mn.z - bmx.z) < 0.05
            if overlap_xy and apoyado:
                resultados.append({"name": o.name, "donde": f"sobre {on}", "z": round(mn.z, 3)})
    elif near:
        base = bpy.data.objects.get(near)
        if base is None:
            return _resp({"error": f"objeto no encontrado: {near}"})
        bmn, bmx = _bbox(base)
        bc = (bmn + bmx) / 2
        for o in sc.objects:
            if o.type != type_filter or o.name == near:
                continue
            mn, mx = _bbox(o)
            d = ((mn + mx) / 2 - bc).length
            if d <= radius:
                resultados.append({"name": o.name, "distancia_m": round(d, 3)})
    else:
        for o in sc.objects:
            if o.type != type_filter:
                continue
            if name_contains and name_contains.lower() not in o.name.lower():
                continue
            mn, mx = _bbox(o)
            resultados.append(
                {
                    "name": o.name,
                    "centro": [round(v, 2) for v in ((mn + mx) / 2)],
                    "dims": [round(v, 2) for v in (mx - mn)],
                }
            )
    return _resp({"resultados": resultados, "total": len(resultados)})


# ═══════════════════════════════════════════════════════════════
# spatial_check_move
# ═══════════════════════════════════════════════════════════════


def spatial_check_move(
    name: str = "", direction: str = "+x", distance: float = 1.0, steps: int = 20, **_kw
) -> dict:
    """¿Cuánto puede moverse un objeto en una dirección sin colisionar?

    direction: +x/-x/+y/-y/+z/-z. No mueve el objeto: solo informa.
    """
    obj = bpy.data.objects.get(name)
    if obj is None:
        return _resp({"error": f"objeto no encontrado: {name}"})
    axis = Vector(
        {
            " +x": (1, 0, 0),
            "-x": (-1, 0, 0),
            "+y": (0, 1, 0),
            "-y": (0, -1, 0),
            "+z": (0, 0, 1),
            "-z": (0, 0, -1),
        }.get(direction, (1, 0, 0))
    )
    otros = [o for o in _scene().objects if o.type == "MESH" and o.name != name]
    orig_loc = obj.location.copy()
    seguro = 0.0
    colision_con = None
    try:
        for i in range(1, steps + 1):
            d = distance * i / steps
            obj.location = orig_loc + axis * d
            bpy.context.view_layer.update()
            hit = None
            for o in otros:
                if _mesh_bvh_overlap(obj, o):
                    hit = o.name
                    break
            if hit:
                colision_con = hit
                break
            seguro = d
    finally:
        obj.location = orig_loc
        bpy.context.view_layer.update()
    return _resp(
        {
            "movimiento_seguro_m": round(seguro, 3),
            "solicitado_m": distance,
            "colisiona_con": colision_con,
            "libre_total": colision_con is None,
        }
    )


# ═══════════════════════════════════════════════════════════════
# spatial_dimensions
# ═══════════════════════════════════════════════════════════════


def spatial_dimensions(category: str = "", search: str = "", **_kw) -> dict:
    """Dimensiones reales (ancho×profundo×alto, metros) de objetos comunes."""
    data = REAL_DIMENSIONS
    if search:
        q = search.lower()
        data = {k: v for k, v in data.items() if q in k}
    elif category:
        data = dict(list(data.items())[:0])  # categoría exacta no implementada: usar search
    return _resp(
        {
            "dimensiones_m": {k: list(v) for k, v in data.items()},
            "total": len(data),
            "nota": "formato [ancho, profundidad, alto] en metros",
        }
    )


# ═══════════════════════════════════════════════════════════════
# spatial_floorplan
# ═══════════════════════════════════════════════════════════════


def spatial_floorplan(view: str = "top", cells: int = 40, **_kw) -> dict:
    """Plano ASCII de la escena para que el agente "vea" el espacio.

    view: top | front | right. Rellena una rejilla con la huella de los objetos.
    """
    sc = _scene()
    meshes = [o for o in sc.objects if o.type == "MESH"]
    if not meshes:
        return _resp({"error": "sin meshes en la escena"})
    boxes = []
    for o in meshes:
        mn, mx = _bbox(o)
        boxes.append((o.name, mn, mx))
    if view == "top":
        ax, ay = 0, 1  # X→columnas, Y→filas
    elif view == "front":
        ax, ay = 0, 2
    else:
        ax, ay = 1, 2
    mn_all = Vector(min(b[1][i] for b in boxes) for i in range(3))
    mx_all = Vector(max(b[2][i] for b in boxes) for i in range(3))
    span_x = max(0.01, mx_all[ax] - mn_all[ax])
    span_y = max(0.01, mx_all[ay] - mn_all[ay])
    cols = max(10, min(cells, 120))
    rows = max(6, int(cols * span_y / span_x / 2))  # caracteres ~2:1 alto/ancho
    grid = [["."] * cols for _ in range(rows)]
    simbolos = "O#@%&*=+~ABCDEF"
    leyenda = {}
    for i, (name, bmn, bmx) in enumerate(boxes):
        sym = simbolos[i % len(simbolos)]
        leyenda[sym] = name
        c0 = int((bmn[ax] - mn_all[ax]) / span_x * (cols - 1))
        c1 = max(c0 + 1, int((bmx[ax] - mn_all[ax]) / span_x * (cols - 1)))
        r0 = int((bmn[ay] - mn_all[ay]) / span_y * (rows - 1))
        r1 = max(r0 + 1, int((bmx[ay] - mn_all[ay]) / span_y * (rows - 1)))
        for r in range(r0, min(r1 + 1, rows)):
            for c in range(c0, min(c1 + 1, cols)):
                if grid[r][c] == ".":
                    grid[r][c] = sym
    plano = "\n".join("".join(row) for row in reversed(grid))
    return _resp(
        {
            "view": view,
            "plano": plano,
            "leyenda": leyenda,
            "dimensiones_m": [round(span_x, 2), round(span_y, 2)],
            "eje_horizontal": ["X", "X", "Y"][["top", "front", "right"].index(view)],
            "eje_vertical": ["Y", "Z", "Z"][["top", "front", "right"].index(view)],
        }
    )


# ═══════════════════════════════════════════════════════════════
# spatial_stack
# ═══════════════════════════════════════════════════════════════


def spatial_stack(names: str = "", gap: float = 0.0, **_kw) -> dict:
    """Apila objetos en orden (base primero) centrados sobre el anterior.

    names: lista separada por comas, p.ej. 'Mesa,Tablero,Taza'.
    """
    order = [n.strip() for n in names.split(",") if n.strip()]
    if len(order) < 2:
        return _resp({"error": "pasa al menos 2 nombres separados por coma"})
    faltan = [n for n in order if bpy.data.objects.get(n) is None]
    if faltan:
        return _resp({"error": f"no encontrados: {faltan}"})
    from ..agent_experience import snap_to as _snap  # type: ignore

    pila = []
    for abajo, arriba in zip(order, order[1:]):
        r = _snap(name=arriba, target=abajo, relation="on_top", gap=gap)
        if "error" in r:
            return _resp(r)
        pila.append(f"{arriba} → sobre {abajo}")
    return _resp({"ok": True, "pila": pila})


# ═══════════════════════════════════════════════════════════════
# registro
# ═══════════════════════════════════════════════════════════════

TOOLS = [
    Tool(
        name="spatial.place",
        category=ToolCategory.SCENE_UTILS,
        description="Coloca un objeto respecto a otro con semántica (on_top/beside_x/beside_y/behind/front/on_floor) y chequeo de colisión",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True},
            "relation": {"type": "str", "default": "on_top"},
            "target": {"type": "str", "default": ""},
            "offset": {"type": "float", "default": 0.0},
            "check_collision": {"type": "bool", "default": True},
        },
        examples=["spatial.place(name='Mug', relation='on_top', target='Mesa')"],
    ),
    Tool(
        name="spatial.query",
        category=ToolCategory.SCENE_UTILS,
        description="Query espacial: qué hay SOBRE un objeto (on=), qué está CERCA (near=, radius=) o listar por nombre",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "on": {"type": "str", "default": ""},
            "near": {"type": "str", "default": ""},
            "radius": {"type": "float", "default": 1.0},
            "name_contains": {"type": "str", "default": ""},
            "type_filter": {"type": "str", "default": "MESH"},
        },
        examples=["spatial.query(on='Mesa')", "spatial.query(near='Puerta', radius=1.5)"],
    ),
    Tool(
        name="spatial.check_move",
        category=ToolCategory.SCENE_UTILS,
        description="¿Cuánto puede moverse un objeto en una dirección sin colisionar? No mueve nada",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "name": {"type": "str", "required": True},
            "direction": {"type": "str", "default": "+x"},
            "distance": {"type": "float", "default": 1.0},
        },
        examples=["spatial.check_move(name='Silla', direction='+x', distance=2)"],
    ),
    Tool(
        name="spatial.dimensions",
        category=ToolCategory.SCENE_UTILS,
        description="Dimensiones reales (ancho×profundo×alto m) de 60 objetos comunes para dimensionar escenas creíbles",
        permission=ToolPermission.READ_ONLY,
        parameters={"search": {"type": "str", "default": ""}},
        examples=["spatial.dimensions(search='mesa')"],
    ),
    Tool(
        name="spatial.floorplan",
        category=ToolCategory.SCENE_UTILS,
        description="Plano ASCII de la escena (top/front/right) para que el agente 'vea' la distribución sin render",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "view": {"type": "str", "default": "top"},
            "cells": {"type": "int", "default": 40},
        },
        examples=["spatial.floorplan(view='top', cells=50)"],
    ),
    Tool(
        name="spatial.stack",
        category=ToolCategory.SCENE_UTILS,
        description="Apila objetos en orden (base primero) con centrado y gap",
        permission=ToolPermission.WRITE,
        parameters={
            "names": {
                "type": "str",
                "required": True,
                "description": "nombres separados por coma, base primero",
            },
            "gap": {"type": "float", "default": 0.0},
        },
        examples=["spatial.stack(names='Mesa,Tablero,Taza')"],
    ),
]

HANDLERS = {
    "spatial.place": spatial_place,
    "spatial.query": spatial_query,
    "spatial.check_move": spatial_check_move,
    "spatial.dimensions": spatial_dimensions,
    "spatial.floorplan": spatial_floorplan,
    "spatial.stack": spatial_stack,
}
