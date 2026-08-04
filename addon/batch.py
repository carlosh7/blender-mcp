"""
batch.py — Operasi batch antar objek. Aman di background (data API).
"""
import bpy
from mathutils import Vector


def batch_rename(prefix="", search=None, replace=None, start_index=1):
    """Ganti nama objek: prefix + indeks, atau search/replace pada nama."""
    renamed = 0
    changes = []
    for i, obj in enumerate(bpy.context.scene.objects):
        new_name = None
        if search is not None and replace is not None:
            if search in obj.name:
                new_name = obj.name.replace(search, replace)
        elif prefix:
            new_name = f"{prefix}{i + int(start_index)}"
        if new_name and new_name != obj.name:
            changes.append({"from": obj.name, "to": new_name})
            obj.name = new_name
            renamed += 1
    return {"status": "success", "renamed": renamed, "changes": changes}


def batch_delete_by_type(object_type="EMPTY"):
    """Hapus semua objek dengan tipe tertentu."""
    t = str(object_type).upper()
    deleted = []
    for obj in list(bpy.context.scene.objects):
        if obj.type == t:
            deleted.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    return {"status": "success", "type": t, "deleted": deleted,
            "count": len(deleted)}


def apply_transforms_all(types=("MESH",)):
    """Bakar transform visual ke data mesh untuk semua objek yang cocok."""
    from .modeling import apply_transform
    applied = []
    for obj in bpy.context.scene.objects:
        if obj.type in types:
            r = apply_transform(obj.name)
            if "error" not in r:
                applied.append(obj.name)
    return {"status": "success", "applied": applied, "count": len(applied)}


def batch_duplicate(object_name="", count=2, offset=(1.0, 0.0, 0.0)):
    """Duplikat objek sebanyak N kali dengan offset linear."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    created = []
    for i in range(1, int(count) + 1):
        dup = obj.copy()
        dup.name = f"{obj.name}_dup{i}"
        dup.location = Vector(obj.location) + Vector(offset) * i
        bpy.context.scene.collection.objects.link(dup)
        created.append(dup.name)
    return {"status": "success", "object": obj.name, "created": created}


def select_all(action="SELECT"):
    """Pilih/batal pilih semua objek."""
    action = str(action).upper()
    for obj in bpy.context.scene.objects:
        obj.select_set(action == "SELECT")
    return {"status": "success", "action": action,
            "count": len(bpy.context.scene.objects)}


def batch_set_scale(scale=(1.0, 1.0, 1.0), types=("MESH", "CURVE")):
    """Atur skala semua objek dengan tipe tertentu."""
    s = Vector(scale)
    count = 0
    for obj in bpy.context.scene.objects:
        if obj.type in types:
            obj.scale = Vector(s)
            count += 1
    return {"status": "success", "scale": list(s), "affected": count}


def batch_set_location(offset=(0.0, 0.0, 0.0)):
    """Geser semua objek dengan vektor."""
    v = Vector(offset)
    count = 0
    for obj in bpy.context.scene.objects:
        obj.location = obj.location + v
        count += 1
    return {"status": "success", "offset": list(v), "affected": count}
