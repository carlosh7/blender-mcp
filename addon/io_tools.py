"""
io_tools.py — Perintah import/export. Operator export bekerja di mode background;
seleksi disiapkan via data API terlebih dahulu.
"""
import os

import bpy

# Setiap format punya DAFTAR kandidat operator, diurutkan dari yang paling
# modern. Blender 4.4 sudah menghapus operator lama (`export_mesh.stl`,
# `export_scene.obj`) dan menggantinya dengan `wm.stl_export` / `wm.obj_export`,
# sedangkan 4.2 masih punya keduanya. Memilih kandidat pertama yang benar-benar
# ada membuat kode ini jalan di 4.2 maupun 4.4+ tanpa perubahan.
EXPORT_FORMATS = {
    "glb": [("export_scene.gltf", {"export_format": "GLB"})],
    "gltf": [("export_scene.gltf", {"export_format": "GLTF_SEPARATE"})],
    "fbx": [("export_scene.fbx", {})],
    "obj": [("wm.obj_export", {}), ("export_scene.obj", {})],
    "stl": [("wm.stl_export", {}), ("export_mesh.stl", {})],
    "ply": [("wm.ply_export", {}), ("export_mesh.ply", {})],
    "usd": [("wm.usd_export", {})],
    "usdz": [("wm.usd_export", {"export_format": "USDZ"})],
    "dae": [("wm.collada_export", {})],
    "x3d": [("export_scene.x3d", {})],
}

IMPORT_FORMATS = {
    "glb": ["import_scene.gltf"],
    "gltf": ["import_scene.gltf"],
    "fbx": ["import_scene.fbx"],
    "obj": ["wm.obj_import", "import_scene.obj"],
    "stl": ["wm.stl_import", "import_mesh.stl"],
    "ply": ["wm.ply_import", "import_mesh.ply"],
    "usd": ["wm.usd_import"],
    "usdz": ["wm.usd_import"],
    "dae": ["wm.collada_import"],
}

# Nama argumen "hanya objek terpilih" berbeda tiap operator.
SELECTION_ARGS = ("use_selection", "export_selected_objects",
                  "selected_objects_only")


def list_export_formats():
    return {"count": len(EXPORT_FORMATS),
            "formats": sorted(EXPORT_FORMATS.keys())}


def _resolve_op(op_path):
    """Kembalikan operator bila ada di build Blender ini, atau None."""
    target = bpy.ops
    for part in op_path.split("."):
        target = getattr(target, part, None)
        if target is None:
            return None
    return target


def _pick(candidates):
    """Pilih kandidat operator pertama yang tersedia.

    `candidates` boleh berupa list nama (import) atau list (nama, kwargs)
    (export).
    """
    for entry in candidates:
        op_path, extra = entry if isinstance(entry, tuple) else (entry, {})
        op = _resolve_op(op_path)
        if op is not None:
            return op, op_path, dict(extra)
    return None, None, {}


def export_scene(filepath="", format="glb"):
    """Export seluruh scene ke format file."""
    if not filepath:
        return {"error": "filepath wajib diisi."}
    fmt = str(format).lower()
    if fmt not in EXPORT_FORMATS:
        return {"error": f"Format tidak didukung: {format}. "
                         f"Tersedia: {', '.join(sorted(EXPORT_FORMATS))}"}
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    op, op_path, extra = _pick(EXPORT_FORMATS[fmt])
    if op is None:
        return {"error": f"Operator export '{fmt}' tidak tersedia di Blender "
                         f"{bpy.app.version_string}. Aktifkan add-on formatnya."}
    try:
        for obj in bpy.context.scene.objects:
            obj.select_set(True)
        op(filepath=filepath, **extra)
        size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        return {"status": "success", "filepath": filepath, "format": fmt,
                "operator": op_path, "size": size}
    except Exception as e:
        return {"error": f"Export {fmt} gagal: {e}"}


def _selection_kwarg(op):
    """Cari nama argumen 'hanya yang terpilih' yang dipahami operator ini.

    Tiap operator menamainya berbeda: `use_selection` (gltf/fbx/obj lama),
    `export_selected_objects` (wm.obj_export), `selected_objects_only` (usd).
    Nama yang sah dibaca dari rna operator, jadi tidak perlu ditebak per format.
    """
    try:
        props = op.get_rna_type().properties.keys()
    except Exception:
        return None
    for name in SELECTION_ARGS:
        if name in props:
            return name
    return None


def export_selected(filepath="", format="glb"):
    """Export hanya objek yang dipilih."""
    if not filepath:
        return {"error": "filepath wajib diisi."}
    fmt = str(format).lower()
    if fmt not in EXPORT_FORMATS:
        return {"error": f"Format tidak didukung: {format}"}
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    op, op_path, extra = _pick(EXPORT_FORMATS[fmt])
    if op is None:
        return {"error": f"Operator export '{fmt}' tidak tersedia di Blender "
                         f"{bpy.app.version_string}."}
    key = _selection_kwarg(op)
    if key:
        extra[key] = True
    try:
        op(filepath=filepath, **extra)
        size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        return {"status": "success", "filepath": filepath, "format": fmt,
                "operator": op_path, "selection_arg": key, "size": size}
    except Exception as e:
        return {"error": f"Export {fmt} gagal: {e}"}


def import_file(filepath="", format=""):
    """Import file ke dalam scene."""
    if not filepath or not os.path.exists(filepath):
        return {"error": f"File tidak ditemukan: {filepath}"}
    fmt = str(format).lower() or os.path.splitext(filepath)[1].lstrip(".").lower()
    candidates = IMPORT_FORMATS.get(fmt)
    if candidates is None:
        return {"error": f"Format tidak didukung: {fmt}"}

    op, op_path, _ = _pick(candidates)
    if op is None:
        return {"error": f"Operator import '{fmt}' tidak tersedia di Blender "
                         f"{bpy.app.version_string}."}
    try:
        op(filepath=filepath)
        return {"status": "success", "filepath": filepath, "format": fmt,
                "operator": op_path}
    except Exception as e:
        return {"error": f"Import {fmt} gagal: {e}"}
