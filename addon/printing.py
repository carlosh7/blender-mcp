"""
printing.py — Perintah bantu cetak 3D: cek manifold, dimensi milimeter,
ketebalan dinding, tata letak print-bed. Aman di background (data API).
"""
import bpy
import bmesh
from mathutils import Vector


def check_manifold(object_name=""):
    """Analisis kerapatan air (watertight) via topologi edge/face bmesh."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    mesh = obj.data

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    boundary_edges = 0
    non_manifold_edges = 0
    manifold_edges = 0
    for e in bm.edges:
        faces = e.link_faces
        if len(faces) == 0:
            continue
        if len(faces) == 1:
            boundary_edges += 1
        elif len(faces) == 2:
            manifold_edges += 1
        else:
            non_manifold_edges += 1

    verts = len(bm.verts)
    faces = len(bm.faces)
    edge_count = len(bm.edges)
    # Euler characteristic sanity for closed meshes: V - E + F == 2
    euler = verts - edge_count + faces
    watertight = boundary_edges == 0 and non_manifold_edges == 0
    holes = 0
    # boundary loops approximate holes
    visited = set()

    def walk_boundary(edge):
        loop = []
        stack = [edge]
        while stack:
            e = stack.pop()
            if id(e) in visited:
                continue
            visited.add(id(e))
            loop.append(e)
            for f in e.link_faces:
                for le in f.edges:
                    if le is not e and len(le.link_faces) == 1 and id(le) not in visited:
                        stack.append(le)
        return loop

    for e in bm.edges:
        if len(e.link_faces) == 1 and id(e) not in visited:
            walk_boundary(e)
            holes += 1

    bm.free()
    return {
        "object": obj.name,
        "watertight": bool(watertight),
        "topology": {"vertices": verts, "edges": edge_count, "faces": faces},
        "edges": {
            "manifold": manifold_edges,
            "boundary": boundary_edges,
            "non_manifold": non_manifold_edges,
        },
        "holes": holes,
        "euler_characteristic": euler,
        "verdict": "WATERTIGHT" if watertight else (
            "NON_MANIFOLD" if non_manifold_edges else "OPEN_BOUNDARY"),
    }


def set_dimensions_mm(object_name="", width_mm=None, height_mm=None,
                      depth_mm=None):
    """Skala objek agar dimensinya sesuai mm yang diminta (scene dalam meter)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    scale_factor = 0.001  # mm -> meters
    dims = obj.dimensions
    targets = {
        "x": (width_mm, dims.x),
        "y": (depth_mm, dims.y),
        "z": (height_mm, dims.z),
    }
    s = list(obj.scale)
    applied = {}
    for axis, (target, current) in targets.items():
        if target is None:
            continue
        current_m = current / obj.scale[{"x": 0, "y": 1, "z": 2}[axis]] \
            if obj.scale[{"x": 0, "y": 1, "z": 2}[axis]] else current
        target_m = float(target) * scale_factor
        idx = {"x": 0, "y": 1, "z": 2}[axis]
        s[idx] = target_m / current_m
        applied[axis] = float(target)
    obj.scale = Vector(s)
    return {"status": "success", "object": obj.name, "dimensions_mm": applied,
            "scale": [round(v, 6) for v in obj.scale]}


def add_wall_thickness(object_name="", thickness_mm=2.0):
    """Tambah ketebalan kulit via modifier Solidify (mm -> meter scene)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    mod = obj.modifiers.new(name="Wall_Thickness", type="SOLIDIFY")
    mod.thickness = float(thickness_mm) * 0.001
    mod.offset = -1.0
    return {"status": "success", "object": obj.name, "modifier": mod.name,
            "thickness_mm": thickness_mm}


def bed_layout(object_names=None, bed_width_mm=220.0, bed_height_mm=220.0,
               margin_mm=5.0):
    """Susun objek dalam grid di print bed (Z=0, satuan mm)."""
    names = object_names or []
    objs = [bpy.data.objects.get(n) for n in names]
    objs = [o for o in objs if o is not None]
    if not objs:
        return {"error": "Tidak ada objek yang diminta untuk disusun."}

    margin = float(margin_mm) * 0.001
    bed_w = float(bed_width_mm) * 0.001
    bed_h = float(bed_height_mm) * 0.001

    # sort by footprint to pack tightly (largest first, greedy)
    items = []
    for o in objs:
        d = o.dimensions
        items.append((o, max(d.x, 1e-4), max(d.y, 1e-4)))
    items.sort(key=lambda t: -(t[1] * t[2]))

    placed = []
    cursor_x = margin
    row_h = 0.0
    for obj, w, h in items:
        if cursor_x + w + margin > bed_w:
            cursor_x = margin
            cursor_y = row_h + margin
            row_h = 0.0
        else:
            cursor_y = row_h + margin if placed else margin
        row_h = max(row_h, h)
        # center object on its footprint cell
        obj.location = Vector((cursor_x + w / 2.0, cursor_y + h / 2.0, 0.0))
        placed.append({"name": obj.name, "x": round(cursor_x, 4),
                       "y": round(cursor_y, 4)})
        cursor_x += w + margin

    return {"status": "success", "bed_mm": [bed_width_mm, bed_height_mm],
            "count": len(placed), "placements": placed}


def export_stl_mm(filepath="", object_name=""):
    """Export objek (atau seleksi) ke STL, skala milimeter."""
    if not filepath:
        return {"error": "filepath wajib diisi."}
    import os
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    try:
        for obj in bpy.context.scene.objects:
            obj.select_set(False)
        if object_name:
            obj = bpy.data.objects.get(object_name)
            if obj is None:
                return {"error": f"Objek tidak ditemukan: {object_name}"}
            obj.select_set(True)
        else:
            bpy.ops.object.select_all(action="SELECT")

        # Blender 4.4 menghapus `export_mesh.stl`; `wm.stl_export` adalah
        # penggantinya dan sudah ada sejak 4.2. Argumen skalanya pun berbeda
        # nama, jadi dipilih sesuai operator yang dipakai.
        if hasattr(bpy.ops.wm, "stl_export"):
            bpy.ops.wm.stl_export(filepath=filepath, use_scene_unit=False,
                                  global_scale=1000.0,
                                  export_selected_objects=True)
        elif hasattr(bpy.ops.export_mesh, "stl"):
            bpy.ops.export_mesh.stl(filepath=filepath, use_scene_unit=False,
                                    global_scale=1000.0, use_selection=True)
        else:
            return {"error": "Operator export STL tidak tersedia di Blender "
                             f"{bpy.app.version_string}."}
        size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        return {"status": "success", "filepath": filepath, "size": size}
    except Exception as e:
        return {"error": f"Export STL gagal: {e}"}
