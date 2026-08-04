"""
uv_texture.py — Perintah pemetaan UV. Proyeksi manual via bmesh agar bekerja
juga di mode background (tanpa operator edit-mode).
"""
import math

import bpy
import bmesh
from mathutils import Vector

METHODS = ("SMART", "PLANAR", "CUBE", "SPHERE", "CYLINDER")


def add_uv_map(object_name="", name="UVMap"):
    """Add a new UV layer to a mesh (data API, background-safe)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH" or obj.data is None:
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    layer = obj.data.uv_layers.new(name=name)
    return {"status": "success", "object": obj.name, "uv_layer": layer.name}


def _project(uv, p, method, center, radius):
    co = p.co
    if method == "PLANAR":
        uv.x = (co.x - center.x) / (radius * 2.0) + 0.5
        uv.y = (co.y - center.y) / (radius * 2.0) + 0.5
    elif method == "SPHERE":
        d = (co - center)
        r = d.length or 1e-6
        d = d / r
        uv.x = 0.5 + math.atan2(d.x, d.z) / (2.0 * math.pi)
        uv.y = 0.5 - math.acos(max(-1.0, min(1.0, d.y))) / math.pi
    elif method == "CYLINDER":
        d = (co - center)
        uv.x = 0.5 + math.atan2(d.x, d.z) / (2.0 * math.pi)
        uv.y = (d.y / (radius * 2.0)) + 0.5
    else:  # CUBE / SMART: dominant normal axis
        n = Vector((abs(p.normal.x), abs(p.normal.y), abs(p.normal.z)))
        if n.x >= n.y and n.x >= n.z:
            uv.x = (co.y - center.y) / (radius * 2.0) + 0.5
            uv.y = (co.z - center.z) / (radius * 2.0) + 0.5
        elif n.y >= n.z:
            uv.x = (co.x - center.x) / (radius * 2.0) + 0.5
            uv.y = (co.z - center.z) / (radius * 2.0) + 0.5
        else:
            uv.x = (co.x - center.x) / (radius * 2.0) + 0.5
            uv.y = (co.y - center.y) / (radius * 2.0) + 0.5


def unwrap_object(object_name="", method="SMART", name="UVMap"):
    """Unwrap a mesh with a manual projection (background-safe)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH" or obj.data is None:
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    method = str(method).upper()
    if method not in METHODS:
        return {"error": f"Metode tidak dikenal: {method}. Tersedia: {', '.join(METHODS)}"}

    mesh = obj.data
    layer = mesh.uv_layers.get(name) or mesh.uv_layers.new(name=name)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv_layer = bm.loops.layers.uv.new(name)

    verts = [Vector(v.co) for v in mesh.vertices]
    center = sum(verts, Vector()) / max(1, len(verts)) if verts else Vector()
    radius = max((Vector(v) - center).length for v in verts) or 1.0

    for face in bm.faces:
        for loop in face.loops:
            p = loop.vert
            uv = loop[uv_layer]
            _project(uv.uv, p, method, center, radius)

    bm.to_mesh(mesh)
    bm.free()
    return {"status": "success", "object": obj.name, "method": method,
            "uv_layer": layer.name, "faces": len(mesh.polygons)}


def list_uv_maps(object_name=""):
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    maps = [uv.name for uv in obj.data.uv_layers]
    return {"object": obj.name, "count": len(maps), "uv_maps": maps}


def remove_uv_map(object_name="", name=""):
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    layer = obj.data.uv_layers.get(name)
    if layer is None:
        return {"error": f"UV map tidak ditemukan: {name}"}
    obj.data.uv_layers.remove(layer)
    return {"status": "success", "removed": name}


def texel_density(object_name="", density=10.0):
    """Set a target texel density by scaling UVs (rough; background-safe)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    # simple uniform scale toward target density relative to mesh size
    dims = obj.dimensions
    area = max(dims.x * dims.y, dims.x * dims.z, dims.y * dims.z, 1e-6)
    scale = float(density) / math.sqrt(area)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if not bm.loops.layers.uv:
        bm.loops.layers.uv.new("UVMap")
    uv_layer = bm.loops.layers.uv[0]
    for face in bm.faces:
        for loop in face.loops:
            loop[uv_layer].uv.x *= scale
            loop[uv_layer].uv.y *= scale
    bm.to_mesh(obj.data)
    bm.free()
    return {"status": "success", "object": obj.name, "density": density}
