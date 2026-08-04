"""
modeling.py — Perintah scene/modeling (aman di background, data-API dulu).

Membuat geometri dengan bpy.data/bmesh, bukan operator, agar
jalur kode yang sama bekerja di `blender -b` maupun sesi GUI. Fitur khusus operator
(monkey Suzanne, workflow edit-mode) berubah menjadi pesan jelas.
"""
import math

import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix

from . import compat

PRIMITIVES = ("CUBE", "PLANE", "SPHERE", "UVSPHERE", "ICOSPHERE", "CYLINDER",
              "CONE", "TORUS", "MONKEY", "GRID", "CIRCLE", "EMPTY")

_MODIFIER_TYPES = (
    "SUBSURF", "BEVEL", "BOOLEAN", "ARRAY", "MIRROR", "SOLIDIFY", "SCREW",
    "WIREFRAME", "DECIMATE", "TRIANGULATE", "LATTICE", "SHRINKWRAP",
    "DISPLACE", "SIMPLE_DEFORM", "SKIN", "REMESH", "NODES", "WELD",
    "DATA_TRANSFER", "CAST", "CURVE", "WAVE", "MESH_SEQUENCE_CACHE",
    "MULTIRES", "MASK", "NORMAL_EDIT",
)


def _link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _new_object(name, data):
    return bpy.data.objects.new(name, data)


def _uv_sphere_mesh(name, radius=1.0, rings=24, sectors=32):
    rings = int(rings)
    sectors = int(sectors)
    radius = float(radius)
    if radius <= 0 or rings < 2 or sectors < 3:
        raise ValueError("Sphere memerlukan radius > 0, rings >= 2, dan sectors >= 3.")
    mesh = bpy.data.meshes.new(name)
    verts = [(0.0, radius, 0.0), (0.0, -radius, 0.0)]
    for ring in range(1, rings):
        phi = math.pi * ring / rings
        y = radius * math.cos(phi)
        ring_radius = radius * math.sin(phi)
        for sector in range(sectors):
            theta = 2.0 * math.pi * sector / sectors
            verts.append((ring_radius * math.cos(theta), y, ring_radius * math.sin(theta)))

    faces = []
    first_ring = 2
    for sector in range(sectors):
        nxt = (sector + 1) % sectors
        faces.append((0, first_ring + sector, first_ring + nxt))
    for ring in range(rings - 2):
        current = first_ring + ring * sectors
        following = current + sectors
        for sector in range(sectors):
            nxt = (sector + 1) % sectors
            faces.append((current + sector, following + sector,
                          following + nxt, current + nxt))
    last_ring = first_ring + (rings - 2) * sectors
    for sector in range(sectors):
        nxt = (sector + 1) % sectors
        faces.append((1, last_ring + nxt, last_ring + sector))

    mesh.from_pydata(verts, [], faces)
    if hasattr(mesh, "validate"):
        mesh.validate()
    mesh.update()
    return mesh


def _cylinder_mesh(name, radius=1.0, depth=2.0, vertices=32, cap=True):
    radius = float(radius)
    depth = float(depth)
    vertices = int(vertices)
    if radius <= 0 or depth <= 0 or vertices < 3:
        raise ValueError("Cylinder memerlukan radius/depth > 0 dan vertices >= 3.")
    mesh = bpy.data.meshes.new(name)
    verts = []
    for i in range(vertices):
        theta = 2.0 * math.pi * i / vertices
        x, y = radius * math.cos(theta), radius * math.sin(theta)
        verts.extend(((x, y, -depth / 2.0), (x, y, depth / 2.0)))
    faces = []
    if cap:
        faces.append(tuple(range((vertices - 1) * 2, -1, -2)))
        faces.append(tuple(range(1, vertices * 2, 2)))
    for i in range(vertices):
        nxt = (i + 1) % vertices
        bottom, bottom_next = 2 * i, 2 * nxt
        top, top_next = bottom + 1, bottom_next + 1
        faces.append((bottom, bottom_next, top_next, top))
    mesh.from_pydata(verts, [], faces)
    if hasattr(mesh, "validate"):
        mesh.validate()
    mesh.update()
    return mesh


def _cone_mesh(name, radius=1.0, depth=2.0, vertices=32, cap=True):
    radius = float(radius)
    depth = float(depth)
    vertices = int(vertices)
    if radius <= 0 or depth <= 0 or vertices < 3:
        raise ValueError("Cone memerlukan radius/depth > 0 dan vertices >= 3.")
    mesh = bpy.data.meshes.new(name)
    verts = [(0.0, 0.0, depth / 2.0)]
    for i in range(vertices):
        theta = 2.0 * math.pi * i / vertices
        verts.append((radius * math.cos(theta), radius * math.sin(theta), -depth / 2.0))
    faces = []
    if cap:
        faces.append(tuple(range(vertices, 0, -1)))
    for i in range(vertices):
        nxt = (i + 1) % vertices
        faces.append((0, 1 + i, 1 + nxt))
    mesh.from_pydata(verts, [], faces)
    if hasattr(mesh, "validate"):
        mesh.validate()
    mesh.update()
    return mesh


def _torus_mesh(name, major=1.0, minor=0.25, major_segments=48, minor_segments=16):
    major = float(major)
    minor = float(minor)
    major_segments = int(major_segments)
    minor_segments = int(minor_segments)
    if major <= 0 or minor <= 0 or major_segments < 3 or minor_segments < 3:
        raise ValueError("Torus memerlukan radius > 0 dan segmen >= 3.")
    mesh = bpy.data.meshes.new(name)
    verts = []
    for i in range(major_segments):
        theta = 2.0 * math.pi * i / major_segments
        for j in range(minor_segments):
            phi = 2.0 * math.pi * j / minor_segments
            x = (major + minor * math.cos(phi)) * math.cos(theta)
            y = (major + minor * math.cos(phi)) * math.sin(theta)
            z = minor * math.sin(phi)
            verts.append((x, y, z))
    faces = []
    for i in range(major_segments):
        for j in range(minor_segments):
            a = i * minor_segments + j
            b = ((i + 1) % major_segments) * minor_segments + j
            c = ((i + 1) % major_segments) * minor_segments + (j + 1) % minor_segments
            d = i * minor_segments + (j + 1) % minor_segments
            faces.append((a, b, c, d))
    mesh.from_pydata(verts, [], faces)
    if hasattr(mesh, "validate"):
        mesh.validate()
    mesh.update()
    return mesh


def _grid_mesh(name, x_subdivisions=10, y_subdivisions=10, size=2.0):
    x_subdivisions = int(x_subdivisions)
    y_subdivisions = int(y_subdivisions)
    size = float(size)
    if x_subdivisions < 1 or y_subdivisions < 1 or size <= 0:
        raise ValueError("Grid memerlukan subdivision >= 1 dan size > 0.")
    mesh = bpy.data.meshes.new(name)
    verts = []
    for i in range(y_subdivisions + 1):
        for j in range(x_subdivisions + 1):
            verts.append((
                (j / x_subdivisions - 0.5) * size,
                (i / y_subdivisions - 0.5) * size,
                0.0,
            ))
    faces = []
    w = x_subdivisions + 1
    for i in range(y_subdivisions):
        for j in range(x_subdivisions):
            a = i * w + j
            faces.append((a, a + 1, a + w + 1, a + w))
    mesh.from_pydata(verts, [], faces)
    if hasattr(mesh, "validate"):
        mesh.validate()
    mesh.update()
    return mesh


def create_object(type="CUBE", name="", location=(0.0, 0.0, 0.0),
                  size=1.0, radius=1.0, depth=2.0, vertices=32,
                  segments=48, minor_segments=16, scale=(1.0, 1.0, 1.0)):
    """Buat objek mesh/primitive dari nol. Aman di background."""
    t = str(type).upper()
    if t not in PRIMITIVES:
        return {"error": f"Tipe tidak dikenal: {type}. Tersedia: {', '.join(PRIMITIVES)}"}

    name = name or t.title()
    if bpy.data.objects.get(name) is not None:
        return {"error": f"Objek '{name}' sudah ada."}

    if t == "EMPTY":
        obj = _new_object(name, None)
        obj.empty_display_type = "PLAIN_AXES"
        _link(obj)
        obj.location = Vector(location)
        return {"status": "success", "object": obj.name, "type": "EMPTY"}

    if t == "MONKEY":
        # Operator-only primitive; requires a UI context.
        r = compat.run_ui_operator("mesh.primitive_monkey_add", size=radius, location=Vector(location))
        if "error" in r:
            return r
        obj = bpy.context.active_object or bpy.context.view_layer.objects.active
        if obj is None:
            return {"error": "MONKEY memerlukan antarmuka Blender."}
        obj.name = name
        return {"status": "success", "object": obj.name, "type": "MONKEY"}

    if t == "ICOSPHERE":
        r = compat.run_ui_operator("mesh.primitive_ico_sphere_add", radius=radius, location=Vector(location))
        if "error" in r:
            return r
        obj = bpy.context.view_layer.objects.active
        obj.name = name
        return {"status": "success", "object": obj.name, "type": "ICOSPHERE"}

    builders = {
        "CUBE": lambda n: _box_mesh(n, size),
        "PLANE": lambda n: _plane_mesh(n, size),
        "SPHERE": lambda n: _uv_sphere_mesh(n, radius, vertices, segments),
        "UVSPHERE": lambda n: _uv_sphere_mesh(n, radius, vertices, segments),
        "CYLINDER": lambda n: _cylinder_mesh(n, radius, depth, vertices),
        "CONE": lambda n: _cone_mesh(n, radius, depth, vertices),
        "TORUS": lambda n: _torus_mesh(n, radius, size, segments, minor_segments),
        "GRID": lambda n: _grid_mesh(n, vertices, segments, size),
        "CIRCLE": lambda n: _circle_mesh(n, radius, vertices),
    }
    mesh = builders[t](name + "_mesh")
    obj = _new_object(name, mesh)
    _link(obj)
    obj.location = Vector(location)
    obj.scale = Vector(scale)
    return {"status": "success", "object": obj.name, "type": t,
            "vertices": len(mesh.vertices), "faces": len(mesh.polygons)}


def _box_mesh(name, size=1.0):
    mesh = bpy.data.meshes.new(name)
    s = size / 2.0
    verts = [
        (s, s, s), (s, s, -s), (s, -s, s), (s, -s, -s),
        (-s, s, s), (-s, s, -s), (-s, -s, s), (-s, -s, -s),
    ]
    faces = [
        (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
        (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def _plane_mesh(name, size=1.0):
    mesh = bpy.data.meshes.new(name)
    s = size / 2.0
    mesh.from_pydata([(s, s, 0), (s, -s, 0), (-s, -s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    mesh.update()
    return mesh


def _circle_mesh(name, radius=1.0, vertices=32):
    mesh = bpy.data.meshes.new(name)
    verts = [(0.0, 0.0, 0.0)]
    for i in range(vertices):
        theta = 2.0 * math.pi * i / vertices
        verts.append((radius * math.cos(theta), radius * math.sin(theta), 0.0))
    mesh.from_pydata(verts, [], [tuple(range(1, vertices + 1))])
    mesh.update()
    return mesh


def get_object_info(name=""):
    """Info detail satu objek (transform, topologi, material)."""
    obj = bpy.data.objects.get(name) or bpy.context.view_layer.objects.active
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {name}"}
    info = {
        "name": obj.name,
        "type": obj.type,
        "location": [round(v, 4) for v in obj.location],
        "rotation_euler": [round(v, 4) for v in obj.rotation_euler],
        "scale": [round(v, 4) for v in obj.scale],
        "dimensions": [round(v, 4) for v in obj.dimensions],
        "parent": obj.parent.name if obj.parent else None,
        "children": [c.name for c in obj.children],
        "modifiers": [m.name for m in obj.modifiers],
        "constraints": [c.name for c in obj.constraints],
        "vertex_groups": [vg.name for vg in obj.vertex_groups],
    }
    if obj.type == "MESH" and obj.data:
        mesh = obj.data
        info["topology"] = {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
        }
        info["materials"] = [m.name for m in mesh.materials]
    return info


def delete_object(name=""):
    """Hapus objek (dan datanya bila tidak dipakai)."""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {name}"}
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    # Lepaskan data blok sesuai registrinya bila sudah tidak dipakai
    if data is not None and getattr(data, "users", 1) == 0:
        for reg in (bpy.data.meshes, bpy.data.curves, bpy.data.armatures,
                    bpy.data.cameras, bpy.data.lights):
            try:
                reg.remove(data)
                break
            except Exception:
                continue
    return {"status": "success", "deleted": name}


def create_empty(name="Empty", location=(0.0, 0.0, 0.0),
                 display_type="PLAIN_AXES"):
    """Buat objek Empty (titik referensi / kontrol)."""
    if bpy.data.objects.get(name) is not None:
        return {"error": f"Objek '{name}' sudah ada."}
    obj = _new_object(name, None)
    obj.empty_display_type = str(display_type).upper()
    _link(obj)
    obj.location = Vector(location)
    return {"status": "success", "object": obj.name, "type": "EMPTY"}


def subdivide_mesh(object_name="", cuts=1, smooth=0.0):
    """Subdivide semua edge mesh (bmesh.ops.subdivide_edges)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH" or obj.data is None:
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=int(cuts),
                              smooth=float(smooth))
    bm.to_mesh(obj.data)
    bm.free()
    return {"status": "success", "object": obj.name, "cuts": cuts}


def loop_cut(object_name="", plane_co=(0.0, 0.0, 0.0), plane_no=(0.0, 1.0, 0.0),
             clear_inner=False, clear_outer=False):
    """Potong loop (bmesh.ops.bisect_plane) sepanjang bidang."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH" or obj.data is None:
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.bisect_plane(
        bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        plane_co=Vector(plane_co), plane_no=Vector(plane_no),
        clear_inner=bool(clear_inner), clear_outer=bool(clear_outer))
    bm.to_mesh(obj.data)
    bm.free()
    return {"status": "success", "object": obj.name,
            "plane_no": list(plane_no), "plane_co": list(plane_co)}


def transform_object(name="", location=None, rotation=None, scale=None,
                     relative=False):
    """Pindah/putar/skala objek. absolut atau relatif terhadap kondisi sekarang."""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {name}"}
    if location is not None:
        v = Vector(location)
        obj.location = obj.location + v if relative else v
    if rotation is not None:
        r = Vector(rotation)
        if relative:
            e = obj.rotation_euler
            obj.rotation_euler = (e.x + r.x, e.y + r.y, e.z + r.z)
        else:
            obj.rotation_euler = tuple(r)
    if scale is not None:
        s = Vector(scale)
        obj.scale = obj.scale * s if relative else s
    return {"status": "success", "object": obj.name,
            "location": [round(v, 4) for v in obj.location],
            "scale": [round(v, 4) for v in obj.scale]}


def duplicate_object(name="", new_name=""):
    """Duplikat objek; data dibagi (seperti instance copy Blender)."""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {name}"}
    dup = obj.copy()
    dup.name = new_name or (obj.name + "_copy")
    dup.location = Vector(obj.location)
    _link(dup)
    return {"status": "success", "object": dup.name, "source": obj.name}


def select_object(name=""):
    """Pilih satu objek berdasarkan nama."""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {name}"}
    compat.select_and_activate(obj)
    return {"status": "success", "selected": obj.name}


def add_modifier(object_name="", modifier_type="SUBSURF", **params):
    """Tambah modifier ke objek (data API; aman di background)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    mtype = str(modifier_type).upper()
    if mtype not in _MODIFIER_TYPES:
        return {"error": f"Tipe modifier tidak dikenal: {modifier_type}"}
    try:
        mod = obj.modifiers.new(name=mtype.title(), type=mtype)
    except TypeError as e:
        return {"error": f"Modifier tidak didukung versi ini: {e}"}
    mod.show_viewport = True

    try:
        if mtype == "SUBSURF":
            mod.levels = max(0, min(11, int(params.get("levels", 1))))
            mod.render_levels = max(0, min(11, int(params.get("render_levels", mod.levels))))
        elif mtype == "BEVEL":
            mod.width = max(0.0, float(params.get("width", 0.01)))
            mod.segments = max(1, min(1000, int(params.get("segments", 1))))
        elif mtype == "BOOLEAN":
            operation = str(params.get("operation", "DIFFERENCE")).upper()
            if operation not in {"INTERSECT", "UNION", "DIFFERENCE"}:
                raise ValueError(f"Operasi Boolean tidak valid: {operation}")
            target = bpy.data.objects.get(params.get("target_object", ""))
            if target is None:
                raise ValueError("Objek target Boolean tidak ditemukan.")
            mod.operation = operation
            mod.object = target
        elif mtype == "ARRAY":
            mod.count = max(1, int(params.get("count", 2)))
            mod.relative_offset_displace = Vector(params.get("offset", (1.0, 0.0, 0.0)))
        elif mtype == "MIRROR":
            axes = {str(axis).upper() for axis in params.get("axes", ["X"])}
            if not axes or not axes <= {"X", "Y", "Z"}:
                raise ValueError(f"Sumbu Mirror tidak valid: {sorted(axes)}")
            for i, axis in enumerate(("X", "Y", "Z")):
                mod.use_axis[i] = axis in axes
        elif mtype == "SOLIDIFY":
            mod.thickness = float(params.get("thickness", 0.01))
            mod.offset = max(-1.0, min(1.0, float(params.get("offset", -1.0))))
        elif mtype == "SCREW":
            axis = str(params.get("axis", "Y")).upper()
            if axis not in {"X", "Y", "Z"}:
                raise ValueError(f"Sumbu Screw tidak valid: {axis}")
            mod.angle = math.radians(float(params.get("angle", 360.0)))
            mod.steps = max(1, int(params.get("steps", 16)))
            mod.render_steps = mod.steps
            mod.axis = axis
            mod.object = bpy.data.objects.get(params.get("axis_object", "")) or None
        elif mtype == "WIREFRAME":
            mod.thickness = float(params.get("thickness", 0.01))
        elif mtype == "DECIMATE":
            mod.ratio = max(0.0, min(1.0, float(params.get("ratio", 0.5))))
        elif mtype == "REMESH":
            mod.octree_depth = max(1, min(12, int(params.get("octree_depth", 6))))
        elif mtype == "WELD":
            mod.merge_threshold = max(0.0, float(params.get("merge_threshold", 0.001)))
        elif mtype == "DISPLACE":
            mod.strength = float(params.get("strength", 1.0))
    except (TypeError, ValueError) as exc:
        obj.modifiers.remove(mod)
        return {"error": str(exc)}
    return {"status": "success", "object": obj.name, "modifier": mod.name, "type": mtype}


def list_modifiers(object_name=""):
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    return {"object": obj.name, "modifiers": [
        {"name": m.name, "type": m.type} for m in obj.modifiers]}


def remove_modifier(object_name="", modifier_name=""):
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    mod = obj.modifiers.get(modifier_name)
    if mod is None:
        for m in obj.modifiers:
            if m.name.lower() == modifier_name.lower():
                mod = m
                break
    if mod is None:
        return {"error": f"Modifier tidak ditemukan: {modifier_name}"}
    obj.modifiers.remove(mod)
    return {"status": "success", "removed": modifier_name}


def apply_modifiers(object_name="", modifier_types=None):
    """Bakar semua (atau modifier tertentu) ke data mesh. Aman di background."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    if obj.type != "MESH":
        return {"error": "Hanya mesh yang dapat menerapkan modifiers."}
    if len(obj.modifiers) == 0:
        return {"status": "success", "applied": []}
    dg = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(dg)
    new_mesh = bpy.data.meshes.new_from_object(eval_obj)
    if new_mesh is None:
        return {"error": "Gagal mengevaluasi objek."}
    old_mesh = obj.data
    obj.data = new_mesh
    applied = [m.name for m in list(obj.modifiers)]
    for m in list(obj.modifiers):
        obj.modifiers.remove(m)
    try:
        bpy.data.meshes.remove(old_mesh)
    except Exception:
        pass
    return {"status": "success", "object": obj.name, "applied": applied}


def boolean_operation(object_name="", target_object="", operation="DIFFERENCE"):
    """Boolean modifier (difference/union/intersect) on object_name."""
    return add_modifier(object_name, "BOOLEAN",
                        operation=operation, target_object=target_object)


def join_objects(object_names=None, new_name="Merged"):
    """Gabungkan beberapa objek mesh menjadi satu dengan menggabung data (aman di background)."""
    names = object_names or []
    objs = [bpy.data.objects.get(n) for n in names]
    objs = [o for o in objs if o is not None and o.type == "MESH"]
    if not objs:
        return {"error": "Tidak ada objek mesh valid untuk digabung."}
    target = objs[0]
    combined = bmesh.new()
    combined.from_mesh(target.data)
    # remember material indices of the target first
    mat_offset = len(target.data.materials)
    joined = []
    for src in objs[1:]:
        if src is target:
            continue
        src_mesh = src.data
        # merge materials
        for mat in src_mesh.materials:
            target.data.materials.append(mat)
        # append geometry with index offsets
        base = len(combined.verts)
        vmap = {}
        for v in src_mesh.vertices:
            vmap[v.index] = combined.verts.new(v.co)
        for f in src_mesh.polygons:
            verts = [vmap[i] for i in f.vertices]
            face = combined.faces.new(verts)
            face.material_index = f.material_index + mat_offset
        bpy.data.objects.remove(src, do_unlink=True)
        joined.append(src.name)
    combined.to_mesh(target.data)
    combined.free()
    target.name = new_name
    return {"status": "success", "object": target.name, "joined": joined}


def merge_by_distance(object_name="", distance=0.001):
    """Hapus vertex ganda (bmesh remove_doubles)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=float(distance))
    bm.to_mesh(obj.data)
    bm.free()
    return {"status": "success", "object": obj.name, "distance": distance}


def bevel_mesh(object_name="", width=0.01, segments=1, affect="EDGES"):
    """Bevel edge/vertex via bmesh (aman di background)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    geom = list(bm.edges) if affect.upper() == "EDGES" else list(bm.verts)
    bmesh.ops.bevel(bm, geom=geom, offset=float(width), segments=int(segments),
                    affect=affect.upper())
    bm.to_mesh(obj.data)
    bm.free()
    return {"status": "success", "object": obj.name, "width": width, "segments": segments}


def extrude_face(object_name="", face_index=0, offset=(0.0, 0.0, 1.0)):
    """Extrude region face sepanjang offset (bmesh, aman di background)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    faces = [f for f in bm.faces]
    if face_index >= len(faces):
        bm.free()
        return {"error": f"Indeks face di luar jangkauan: {face_index}"}
    target = faces[face_index]
    res = bmesh.ops.extrude_face_region(bm, geom=[target])
    new_geom = res.get("geom", [])
    bmesh.ops.translate(bm, verts=[g for g in new_geom if isinstance(g, bmesh.types.BMVert)],
                        vec=Vector(offset))
    bm.to_mesh(obj.data)
    bm.free()
    return {"status": "success", "object": obj.name, "face": face_index}


def inset_face(object_name="", face_index=0, thickness=0.1, depth=0.0):
    """Inset sebuah face (bmesh inset_region, aman di background)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    faces = [f for f in bm.faces]
    if face_index >= len(faces):
        bm.free()
        return {"error": f"Indeks face di luar jangkauan: {face_index}"}
    bmesh.ops.inset_region(bm, faces=[faces[face_index]], thickness=float(thickness),
                           depth=float(depth))
    bm.to_mesh(obj.data)
    bm.free()
    return {"status": "success", "object": obj.name, "face": face_index}


def solidify_mesh(object_name="", thickness=0.01, offset=-1.0):
    """Tambah modifier Solidify (memberi ketebalan pada permukaan tipis)."""
    return add_modifier(object_name, "SOLIDIFY", thickness=thickness, offset=offset)


def clean_mesh(object_name="", merge_distance=0.001, delete_loose=True):
    """Hapus vertex ganda + geometri lepas (bmesh, aman di background)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=float(merge_distance))
    if delete_loose:
        loose_verts = [v for v in bm.verts if not v.link_edges]
        loose_edges = [e for e in bm.edges if not e.link_faces]
        if loose_verts:
            bmesh.ops.delete(bm, geom=loose_verts, context="VERTS")
        if loose_edges:
            bmesh.ops.delete(bm, geom=loose_edges, context="EDGES")
    bm.to_mesh(obj.data)
    bm.free()
    return {"status": "success", "object": obj.name, "merged": True, "loose_removed": delete_loose}


def create_text(name="Text", body="Hello", location=(0.0, 0.0, 0.0),
                size=1.0, extrude=0.0, font_name="Bfont"):
    """Buat objek teks 3D (data API, aman di background)."""
    curve = bpy.data.curves.new(name + "_curve", type="FONT")
    curve.body = body
    curve.extrude = float(extrude)
    curve.size = float(size)
    try:
        curve.font = bpy.data.fonts.get(font_name) or curve.font
    except Exception:
        pass
    obj = _new_object(name, curve)
    _link(obj)
    obj.location = Vector(location)
    return {"status": "success", "object": obj.name, "type": "FONT", "body": body}


def create_curve(name="Curve", points=None, bezier=True, closed=False,
                 location=(0.0, 0.0, 0.0), extrude=0.0):
    """Buat kurva bezier/poly dari titik-titik. Aman di background."""
    pts = points or [(0, 0, 0), (1, 0, 0), (2, 1, 0)]
    curve = bpy.data.curves.new(name + "_curve", type="CURVE")
    curve.dimensions = "3D"
    spline = curve.splines.new("BEZIER" if bezier else "POLY")
    spline.use_cyclic_u = bool(closed)
    if bezier:
        spline.bezier_points.add(len(pts) - 1)
        for i, pt in enumerate(pts):
            p = spline.bezier_points[i]
            p.co = Vector(pt)
            p.handle_left_type = "AUTO"
            p.handle_right_type = "AUTO"
    else:
        spline.points.add(len(pts) - 1)
        for i, pt in enumerate(pts):
            v = Vector(pt)
            spline.points[i].co = (v.x, v.y, v.z, 1.0)
    curve.extrude = float(extrude)
    obj = _new_object(name, curve)
    _link(obj)
    obj.location = Vector(location)
    return {"status": "success", "object": obj.name, "type": "CURVE",
            "points": len(pts), "closed": closed}


def create_screw_profile(name="Screw", profile=None, angle=360.0, steps=32,
                         axis="Y", location=(0.0, 0.0, 0.0)):
    """Lathe/screw: profil bezier + modifier SCREW. Aman di background."""
    pts = profile or [(0, 0, 0), (0.2, 0, 0), (0.2, 0.5, 0), (0, 0.5, 0)]
    curve = bpy.data.curves.new(name + "_profile", type="CURVE")
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(pts) - 1)
    for i, pt in enumerate(pts):
        p = spline.bezier_points[i]
        p.co = Vector(pt)
        p.handle_left_type = "VECTOR"
        p.handle_right_type = "VECTOR"
    obj = _new_object(name, curve)
    _link(obj)
    obj.location = Vector(location)
    axis = str(axis).upper()
    if axis not in {"X", "Y", "Z"}:
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.curves.remove(curve)
        return {"error": f"Sumbu Screw tidak valid: {axis}"}
    mod = obj.modifiers.new(name="Screw", type="SCREW")
    mod.angle = math.radians(float(angle))
    mod.steps = max(1, int(steps))
    mod.render_steps = mod.steps
    mod.axis = axis
    return {"status": "success", "object": obj.name, "modifier": "Screw",
            "angle": angle, "steps": steps}


def apply_transform(object_name=""):
    """Bakar transform objek ke data mesh; reset loc/rot/scale."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    if obj.type != "MESH":
        return {"error": "apply_transform hanya berlaku untuk mesh."}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=list(bm.verts))
    bm.to_mesh(obj.data)
    bm.free()
    obj.location = Vector((0, 0, 0))
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = Vector((1.0, 1.0, 1.0))
    return {"status": "success", "object": obj.name}


def model_from_scratch(name="Model", type="CUBE", location=(0.0, 0.0, 0.0),
                       scale=None, subdivisions=0, bevel_width=0.0,
                       smooth=False):
    """Sekali jalan: buat objek, atur transform, lalu pasang modifier dasar.

    Alur "dari nol" untuk modeling: satu panggilan menggantikan rangkaian
    create -> transform -> add_modifier yang biasanya dirakit manual oleh
    agent, sehingga lebih sedikit langkah yang bisa gagal separuh jalan.
    """
    r = create_object(type=type, name=name, location=location)
    if isinstance(r, dict) and "error" in r:
        return r
    obj = bpy.data.objects.get(name) or bpy.context.object
    if obj is None:
        return {"error": "Objek gagal dibuat."}

    langkah = ["create_object"]
    if scale is not None:
        t = transform_object(name=obj.name, scale=scale)
        if isinstance(t, dict) and "error" in t:
            return t
        langkah.append("transform_object")

    if int(subdivisions) > 0:
        m = add_modifier(object_name=obj.name, modifier_type="SUBSURF",
                         levels=int(subdivisions))
        if isinstance(m, dict) and "error" in m:
            return m
        langkah.append("subsurf")

    if float(bevel_width) > 0.0:
        m = add_modifier(object_name=obj.name, modifier_type="BEVEL",
                         width=float(bevel_width))
        if isinstance(m, dict) and "error" in m:
            return m
        langkah.append("bevel")

    if smooth and obj.type == "MESH" and obj.data is not None:
        for poly in obj.data.polygons:
            poly.use_smooth = True
        langkah.append("shade_smooth")

    return {"status": "success", "object": obj.name, "type": type,
            "steps": langkah, "modifiers": [m.type for m in obj.modifiers]}
