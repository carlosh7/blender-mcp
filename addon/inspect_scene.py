"""
inspect_scene.py — Consultas de lectura sobre la escena.

`get_scene_info` devuelve una lista plana truncada a 20 objetos: sin jerarquía,
sin dimensiones y sin materiales. Un agente que ensambla necesita saber qué
cuelga de qué y cuánto mengukur cada pieza antes de decidir dónde poner la
siguiente. Todo lo de aquí es de solo lectura.
"""
import bpy
from mathutils import Vector


def _dims(obj):
    d = obj.dimensions
    return [round(d.x, 4), round(d.y, 4), round(d.z, 4)]


def _loc(obj):
    return [round(v, 4) for v in obj.location]


def _bounds(obj):
    bpy.context.view_layer.update()  # matrix_world se recalcula en el depsgraph
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    hi = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    return lo, hi


def scene_graph(include_data=True):
    """Jerarquía completa padre→hijo, con dimensiones y materiales.

    Devuelve los objetos raíz anidando sus descendientes, que es como el agente
    razona sobre un ensamblaje.
    """
    scene = bpy.context.scene

    def node(obj):
        entry = {
            "name": obj.name,
            "type": obj.type,
            "location": _loc(obj),
            "children": [node(c) for c in obj.children if c.name in scene.objects],
        }
        if include_data:
            entry["dimensions"] = _dims(obj)
            entry["visible"] = bool(obj.visible_get()) if obj.name in scene.objects else False
            mats = [m.name for m in getattr(obj.data, "materials", []) or [] if m]
            if mats:
                entry["materials"] = mats
            if obj.type == "MESH" and obj.data:
                entry["polygons"] = len(obj.data.polygons)
            mods = [m.type for m in obj.modifiers]
            if mods:
                entry["modifiers"] = mods
        return entry

    roots = [o for o in scene.objects if o.parent is None]
    total_polys = sum(len(o.data.polygons) for o in scene.objects
                      if o.type == "MESH" and o.data)
    return {
        "scene": scene.name,
        "object_count": len(scene.objects),
        "total_polygons": total_polys,
        "frame_range": [scene.frame_start, scene.frame_end],
        "roots": [node(o) for o in roots],
    }


def measure(name_a, name_b=None):
    """Mide un objeto, o la relación entre dos.

    Con un objeto: dimensiones, volumen del bbox, centro y extremos.
    Con dos: distancia entre centros, hueco real entre superficies (negativo si
    se solapan) y si sus bounding boxes se intersectan.
    """
    obj_a = bpy.data.objects.get(name_a)
    if obj_a is None:
        return {"error": f"Objek tidak ditemukan: {name_a}"}

    lo_a, hi_a = _bounds(obj_a)
    size_a = hi_a - lo_a
    info_a = {
        "name": obj_a.name,
        "dimensions": _dims(obj_a),
        "bbox_min": [round(v, 4) for v in lo_a],
        "bbox_max": [round(v, 4) for v in hi_a],
        "center": [round(v, 4) for v in (lo_a + hi_a) / 2],
        "bbox_volume": round(size_a.x * size_a.y * size_a.z, 6),
    }

    if name_b is None:
        return info_a

    obj_b = bpy.data.objects.get(name_b)
    if obj_b is None:
        return {"error": f"Objek tidak ditemukan: {name_b}"}

    lo_b, hi_b = _bounds(obj_b)
    center_a = (lo_a + hi_a) / 2
    center_b = (lo_b + hi_b) / 2

    # Hueco por eje: negativo cuando los volúmenes se solapan en ese eje.
    gaps = []
    for i in range(3):
        gaps.append(max(lo_a[i] - hi_b[i], lo_b[i] - hi_a[i]))

    return {
        "a": info_a,
        "b": {
            "name": obj_b.name,
            "dimensions": _dims(obj_b),
            "center": [round(v, 4) for v in center_b],
        },
        "center_distance": round((center_a - center_b).length, 4),
        "gap_per_axis": [round(g, 4) for g in gaps],
        "gap": round(max(gaps), 4),
        "overlapping": all(g < 0 for g in gaps),
    }


def find_objects(name_contains="", type=None, min_polygons=None, has_material=None):
    """Busca objetos por nombre, tipo, complejidad o material.

    Evita traerse la escena entera para localizar una pieza.
    """
    needle = (name_contains or "").lower()
    results = []
    for obj in bpy.context.scene.objects:
        if needle and needle not in obj.name.lower():
            continue
        if type and obj.type != type.upper():
            continue

        polys = len(obj.data.polygons) if obj.type == "MESH" and obj.data else 0
        if min_polygons is not None and polys < min_polygons:
            continue

        mats = [m.name for m in getattr(obj.data, "materials", []) or [] if m]
        if has_material and has_material not in mats:
            continue

        results.append({
            "name": obj.name,
            "type": obj.type,
            "location": _loc(obj),
            "dimensions": _dims(obj),
            "polygons": polys,
            "materials": mats,
            "parent": obj.parent.name if obj.parent else None,
        })

    return {"total": len(results), "objects": results}
