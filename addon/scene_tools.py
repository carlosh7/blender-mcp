"""
scene_tools.py — Perintah scene, pencahayaan, kamera, dan render.
Aman di background (data API) kecuali operasi khusus viewport.
"""
import bpy
from mathutils import Vector

from . import compat



LIGHT_TYPES = ("POINT", "SUN", "SPOT", "AREA")
RENDER_ENGINES = ("CYCLES", "EEVEE", "WORKBENCH", "BLENDER_WORKBENCH",
                  "BLENDER_EEVEE_NEXT")


def _get_object(name):
    return bpy.data.objects.get(name)


def create_light(name="Light", light_type="POINT", energy=10.0,
                 color=(1.0, 1.0, 1.0), location=(0.0, 4.0, 0.0),
                 spot_angle=45.0, area_size=1.0, shadow=True):
    """Buat cahaya (point/sun/spot/area). Aman di background."""
    ltype = str(light_type).upper()
    if ltype not in LIGHT_TYPES:
        return {"error": f"Tipe cahaya tidak dikenal: {light_type}. "
                         f"Tersedia: {', '.join(LIGHT_TYPES)}"}
    light = bpy.data.lights.new(name, type=ltype)
    light.energy = float(energy)
    light.color = tuple(float(v) for v in color[:3])
    light.use_shadow = bool(shadow)
    if ltype == "SPOT":
        import math
        light.spot_size = math.radians(float(spot_angle))
    if ltype == "AREA":
        light.size = float(area_size)
        light.size_y = float(area_size)
    obj = bpy.data.objects.new(name, light)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(location)
    return {"status": "success", "object": obj.name, "type": ltype,
            "energy": energy}


def setup_three_point_lighting(target_name="", intensity=1.0):
    """Key + fill + rim mengelilingi bounding box target. Aman di background."""
    target = _get_object(target_name)
    if target is None:
        return {"error": f"Objek target tidak ditemukan: {target_name}"}
    bb = [Vector(v) for v in target.bound_box]
    center = sum(bb, Vector()) / 8.0
    dims = target.dimensions
    radius = max(dims.x, dims.y, dims.z) * 2.0 + 2.0
    height = dims.z + radius * 0.6

    key = create_light("Key_Light", "AREA", 200.0 * intensity,
                       (1.0, 0.95, 0.85),
                       (center.x + radius * 0.5, center.y - radius * 0.5, height),
                       area_size=2.0)
    fill = create_light("Fill_Light", "AREA", 80.0 * intensity,
                        (0.6, 0.8, 1.0),
                        (center.x - radius, center.y + radius * 0.4, height * 0.6),
                        area_size=1.5)
    rim = create_light("Rim_Light", "SUN", 60.0 * intensity,
                       (1.0, 1.0, 1.0),
                       (center.x, center.y + radius, center.z + radius * 0.8))
    return {"status": "success", "target": target.name, "lights": [
        key.get("object"), fill.get("object"), rim.get("object")]}


def create_camera(name="Camera", location=(5.0, -5.0, 4.0),
                  rotation=None, lens=50.0, clip_start=0.1, clip_end=1000.0):
    """Buat kamera. Aman di background."""
    cam = bpy.data.cameras.new(name)
    cam.lens = float(lens)
    cam.clip_start = float(clip_start)
    cam.clip_end = float(clip_end)
    obj = bpy.data.objects.new(name, cam)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(location)
    if rotation is not None:
        obj.rotation_euler = tuple(rotation)
    return {"status": "success", "object": obj.name, "lens": lens}


def set_camera_target(camera_name="", target_name=""):
    """Buat kamera mengarah ke target (constraint TRACK_TO)."""
    cam = _get_object(camera_name)
    target = _get_object(target_name)
    if cam is None:
        return {"error": f"Kamera tidak ditemukan: {camera_name}"}
    if target is None:
        return {"error": f"Target tidak ditemukan: {target_name}"}
    con = cam.constraints.new("TRACK_TO")
    con.target = target
    return {"status": "success", "camera": cam.name, "target": target.name,
            "constraint": con.name}


def set_camera_active(camera_name=""):
    """Jadikan kamera sebagai kamera aktif scene."""
    cam = _get_object(camera_name)
    if cam is None:
        return {"error": f"Kamera tidak ditemukan: {camera_name}"}
    bpy.context.scene.camera = cam
    return {"status": "success", "camera": cam.name}


def set_render_engine(engine="CYCLES"):
    """Set render engine (CYCLES / EEVEE / WORKBENCH)."""
    e = str(engine).upper()
    if e == "WORKBENCH":
        e = "BLENDER_WORKBENCH"
    if e == "EEVEE":
        e = "BLENDER_EEVEE_NEXT" if compat.at_least(compat.BLENDER_4_2) else "BLENDER_EEVEE"
    if e not in RENDER_ENGINES and not e.startswith("BLENDER_"):
        return {"error": f"Engine tidak dikenal: {engine}. Tersedia: CYCLES, EEVEE, WORKBENCH"}
    bpy.context.scene.render.engine = e
    return {"status": "success", "engine": e}


def set_render_resolution(width=1920, height=1080, percentage=100):
    scene = bpy.context.scene
    scene.render.resolution_x = int(width)
    scene.render.resolution_y = int(height)
    scene.render.resolution_percentage = int(percentage)
    return {"status": "success", "width": int(width), "height": int(height),
            "percentage": int(percentage)}


def set_render_samples(samples=64):
    """Set samples for the active engine (Cycles / EEVEE)."""
    return compat.set_render_samples(bpy.context.scene, samples)


def set_cycles_device(device="CPU"):
    """Set Cycles compute device (CPU / GPU / OPTIX / CUDA / HIP / METAL)."""
    scene = bpy.context.scene
    d = compat.cycles_device(device)
    try:
        scene.cycles.device = d
        return {"status": "success", "device": d}
    except Exception as e:
        return {"error": f"Gagal mengganti device: {e}"}


def render_frame(filepath=""):
    """Render frame saat ini ke file (write_still)."""
    scene = bpy.context.scene
    if filepath:
        import os as _os
        scene.render.filepath = _os.path.abspath(str(filepath))
    try:
        r = bpy.ops.render.render(write_still=True)
        if isinstance(r, dict) and r.get("error"):
            return r
        return {"status": "success",
                "filepath": scene.render.filepath}
    except Exception as e:
        return {"error": f"Render gagal: {e}"}


def render_viewport_to_path(filepath=""):
    """Render to an explicit path (alias of render_frame with filepath)."""
    if not filepath:
        return {"error": "filepath wajib diisi."}
    return render_frame(filepath)


def scene_summary():
    scene = bpy.context.scene
    counts = {}
    for obj in scene.objects:
        counts[obj.type] = counts.get(obj.type, 0) + 1
    active = bpy.context.view_layer.objects.active
    return {
        "name": scene.name,
        "object_count": len(scene.objects),
        "types": counts,
        "frame_range": [scene.frame_start, scene.frame_end],
        "frame_current": scene.frame_current,
        "render_engine": scene.render.engine,
        "active_object": active.name if active else None,
        "materials": len(bpy.data.materials),
        "cameras": len([o for o in scene.objects if o.type == "CAMERA"]),
        "lights": len([o for o in scene.objects if o.type == "LIGHT"]),
    }


def cleanup_scene(purge_unused=True):
    """Hapus datablock yatim; normalkan nama objek. Aman di background."""
    if purge_unused:
        try:
            bpy.ops.outliner.orphans_purge(
                do_local_ids=True, do_linked_ids=True, do_recursive=True)
        except Exception:
            # data-API fallback (background mode)
            for reg in (bpy.data.meshes, bpy.data.materials, bpy.data.actions,
                        bpy.data.armatures, bpy.data.cameras, bpy.data.lights,
                        bpy.data.curves, bpy.data.images, bpy.data.node_groups):
                for item in list(reg):
                    if getattr(item, "users", 1) == 0:
                        try:
                            reg.remove(item)
                        except Exception:
                            pass
    renamed = 0
    for obj in bpy.context.scene.objects:
        if "." in obj.name and not obj.name.endswith((".001", ".002", ".003")):
            obj.name = obj.name.split(".")[0]
            renamed += 1
    return {"status": "success", "purged": bool(purge_unused), "renamed": renamed}


def purge_orphans():
    """Hapus datablock yang tidak dipakai (data API)."""
    removed = 0
    for reg in (bpy.data.meshes, bpy.data.materials, bpy.data.actions,
                bpy.data.armatures, bpy.data.cameras, bpy.data.lights,
                bpy.data.curves, bpy.data.images, bpy.data.node_groups):
        for item in list(reg):
            if getattr(item, "users", 1) == 0:
                try:
                    reg.remove(item)
                    removed += 1
                except Exception:
                    pass
    return {"status": "success", "removed": removed}


def select_by_type(object_type="MESH"):
    """Pilih semua objek sesuai tipe; mengembalikan jumlah. Aman di background."""
    t = str(object_type).upper()
    count = 0
    for obj in bpy.context.scene.objects:
        if obj.type == t:
            obj.select_set(True)
            count += 1
    return {"status": "success", "type": t, "selected": count}


def hide_object(object_name="", hide=True):
    """Sembunyikan/tampilkan objek di viewport. Aman di background."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    obj.hide_set(bool(hide))
    return {"status": "success", "object": obj.name, "hidden": bool(hide)}


def unhide_all():
    count = 0
    for obj in bpy.context.scene.objects:
        if obj.hide_get():
            obj.hide_set(False)
            count += 1
    return {"status": "success", "unhidden": count}


def set_scene_name(name="Scene"):
    bpy.context.scene.name = name
    return {"status": "success", "scene": bpy.context.scene.name}


def jump_to_view3d_object_by_name(name=""):
    """Frame the 3D viewport on an object. Requires a Blender UI."""
    obj = bpy.data.objects.get(name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {name}"}
    r = compat.run_ui_operator("object.select_all", action="DESELECT")
    if "error" in r:
        return r
    compat.select_and_activate(obj)
    r = compat.run_ui_operator("view3d.view_selected", use_all_regions=True)
    if "error" in r:
        return r
    return {"status": "success", "framed": obj.name}
