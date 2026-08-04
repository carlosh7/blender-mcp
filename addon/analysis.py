"""
analysis.py — Perintah analisis scene/objek/datablock.
Aman di background (data API); analisis mesh memakai bmesh.
"""
import bpy
import bmesh
from mathutils import Vector


def get_objects_summary():
    """Ringkasan per objek: nama, tipe, transform, topologi."""
    scene = bpy.context.scene
    objects = []
    for obj in scene.objects:
        entry = {
            "name": obj.name,
            "type": obj.type,
            "location": [round(v, 4) for v in obj.location],
            "dimensions": [round(v, 4) for v in obj.dimensions],
            "parent": obj.parent.name if obj.parent else None,
        }
        if obj.type == "MESH" and obj.data:
            entry["topology"] = {
                "vertices": len(obj.data.vertices),
                "faces": len(obj.data.polygons),
            }
        objects.append(entry)
    return {"object_count": len(objects), "objects": objects}


def get_object_detail_summary(name=""):
    """Ringkasan mendalam satu objek."""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {name}"}
    summary = {
        "name": obj.name,
        "type": obj.type,
        "location": [round(v, 4) for v in obj.location],
        "rotation": [round(v, 4) for v in obj.rotation_euler],
        "scale": [round(v, 4) for v in obj.scale],
        "dimensions_mm": [round(v * 1000, 2) for v in obj.dimensions],
        "parent": obj.parent.name if obj.parent else None,
        "children": [c.name for c in obj.children],
        "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers],
        "constraints": [{"name": c.name, "type": c.type} for c in obj.constraints],
        "vertex_groups": [vg.name for vg in obj.vertex_groups],
    }
    if obj.type == "MESH" and obj.data:
        mesh = obj.data
        summary["topology"] = {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
        }
        summary["materials"] = [m.name for m in mesh.materials]
        summary["uv_maps"] = [u.name for u in mesh.uv_layers]
        summary["vertex_color_layers"] = [c.name for c in mesh.vertex_colors]
    if obj.type == "ARMATURE":
        summary["bones"] = len(obj.data.bones)
    if obj.type == "CAMERA":
        summary["lens"] = obj.data.lens
    if obj.type == "LIGHT":
        summary["light_type"] = obj.data.type
        summary["energy"] = obj.data.energy
    return summary


def get_blendfile_summary_datablocks():
    """Inventaris datablock file blend saat ini."""
    data = bpy.data
    counts = {}
    for attr in ("objects", "meshes", "materials", "armatures", "actions",
                 "cameras", "lights", "curves", "images", "node_groups",
                 "texts", "fonts"):
        try:
            col = getattr(data, attr, None)
            counts[attr] = len(col) if col is not None else 0
        except Exception:
            counts[attr] = 0
    total = sum(counts.values())
    return {"total_datablocks": total, "counts": counts,
            "scene": bpy.context.scene.name,
            "objects_in_scene": len(bpy.context.scene.objects)}


def mesh_analysis(object_name=""):
    """Analisis kualitas topologi: ngon, tris, non-manifold, lepas."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH" or obj.data is None:
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    mesh = obj.data

    tris = quads = ngons = 0
    for p in mesh.polygons:
        n = p.loop_total
        if n == 3:
            tris += 1
        elif n == 4:
            quads += 1
        else:
            ngons += 1

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    boundary = non_manifold = manifold = 0
    for e in bm.edges:
        n = len(e.link_faces)
        if n == 1:
            boundary += 1
        elif n == 2:
            manifold += 1
        else:
            non_manifold += 1
    loose_verts = sum(1 for v in bm.verts if not v.link_edges)
    loose_edges = sum(1 for e in bm.edges if not e.link_faces)
    bm.free()

    total_faces = tris + quads + ngons
    return {
        "object": obj.name,
        "topology": {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": total_faces,
            "tris": tris,
            "quads": quads,
            "ngons": ngons,
            "ngon_percent": round(100.0 * ngons / total_faces, 2) if total_faces else 0.0,
        },
        "edge_health": {
            "manifold": manifold,
            "boundary": boundary,
            "non_manifold": non_manifold,
        },
        "loose": {"vertices": loose_verts, "edges": loose_edges},
        "verdict": "CLEAN" if (ngons == 0 and non_manifold == 0
                               and loose_verts == 0) else "REVIEW",
    }


def analyze_performance():
    """Laporan anggaran poligon untuk scene."""
    report = []
    total_polys = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.data:
            poly_count = len(obj.data.polygons)
            total_polys += poly_count
            if poly_count > 50000:
                report.append(f"KRITIS: {obj.name} — {poly_count} poligon")
            elif poly_count > 10000:
                report.append(f"TINGGI: {obj.name} — {poly_count} poligon")
    return {"total_polygons": total_polys, "object_count": len(report),
            "report": report or ["Scene sudah optimal."]}
