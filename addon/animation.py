"""
animation.py — Perintah animasi: keyframe, action, interpolasi,
timeline, shape key, fisika rigid body. Aman di background (data API).
"""
import math

import bpy
from mathutils import Vector

INTERPOLATIONS = ("CONSTANT", "LINEAR", "BEZIER")


def _get_object(name):
    return bpy.data.objects.get(name)


ANIMATABLE_PROPERTIES = {
    "location": "vector",
    "rotation_euler": "vector",
    "rotation_quaternion": "quaternion",
    "scale": "vector",
    "hide_viewport": "scalar",
    "color": "color",
}


def _frame_range(start_frame, end_frame):
    start, end = int(start_frame), int(end_frame)
    if start == end:
        raise ValueError("start_frame harus berbeda dari end_frame.")
    if start > end:
        start, end = end, start
    return start, end


def _interpolation(value):
    result = str(value).upper()
    if result not in INTERPOLATIONS:
        raise ValueError(f"Interpolasi tidak valid: {value}")
    return result


def insert_keyframe(object_name="", frame=1, property="location"):
    """Sisipkan keyframe untuk properti pada sebuah frame. Aman di background."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    if property not in ANIMATABLE_PROPERTIES:
        return {"error": f"Properti tidak didukung: {property}"}
    try:
        frame = int(frame)
        obj.keyframe_insert(data_path=property, frame=frame)
        return {"status": "success", "object": obj.name, "property": property,
                "frame": frame}
    except Exception as exc:
        return {"error": f"keyframe_insert gagal: {exc}"}


def animate_location(object_name="", start_frame=1, end_frame=30,
                     start_loc=(0.0, 0.0, 0.0), end_loc=(5.0, 0.0, 0.0),
                     interpolation="BEZIER"):
    """Animasi objek bergerak dari start_loc ke end_loc."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    try:
        start, end = _frame_range(start_frame, end_frame)
        interpolation = _interpolation(interpolation)
        start_value, end_value = Vector(start_loc), Vector(end_loc)
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    obj.location = start_value
    obj.keyframe_insert(data_path="location", frame=start)
    obj.location = end_value
    obj.keyframe_insert(data_path="location", frame=end)
    _set_fcurve_interpolation(obj, "location", interpolation)
    return {"status": "success", "object": obj.name,
            "from": list(start_value), "to": list(end_value),
            "frames": [start, end]}


def animate_rotation(object_name="", start_frame=1, end_frame=30,
                     revolutions=1.0, axis="Z", start_rotation=(0.0, 0.0, 0.0),
                     interpolation="BEZIER"):
    """Putar objek `revolutions` kali mengelilingi `axis` antar frame."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    try:
        start, end = _frame_range(start_frame, end_frame)
        interpolation = _interpolation(interpolation)
        axis = str(axis).upper()
        if axis not in {"X", "Y", "Z"}:
            raise ValueError(f"Sumbu rotasi tidak valid: {axis}")
        start_value = Vector(start_rotation)
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = tuple(start_value)
    obj.keyframe_insert(data_path="rotation_euler", frame=start)
    index = {"X": 0, "Y": 1, "Z": 2}[axis]
    end_value = list(start_value)
    end_value[index] += 2.0 * math.pi * float(revolutions)
    obj.rotation_euler = tuple(end_value)
    obj.keyframe_insert(data_path="rotation_euler", frame=end)
    _set_fcurve_interpolation(obj, "rotation_euler", interpolation)
    return {"status": "success", "object": obj.name, "revolutions": revolutions,
            "axis": axis, "frames": [start, end]}


def animate_scale(object_name="", start_frame=1, end_frame=30,
                  start_scale=(1.0, 1.0, 1.0), end_scale=(2.0, 2.0, 2.0),
                  interpolation="BEZIER"):
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    try:
        start, end = _frame_range(start_frame, end_frame)
        interpolation = _interpolation(interpolation)
        start_value, end_value = Vector(start_scale), Vector(end_scale)
        if any(value <= 0 for value in (*start_value, *end_value)):
            raise ValueError("Nilai scale harus positif.")
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    obj.scale = start_value
    obj.keyframe_insert(data_path="scale", frame=start)
    obj.scale = end_value
    obj.keyframe_insert(data_path="scale", frame=end)
    _set_fcurve_interpolation(obj, "scale", interpolation)
    return {"status": "success", "object": obj.name,
            "from": list(start_value), "to": list(end_value),
            "frames": [start, end]}


def _set_fcurve_interpolation(obj, data_path, interpolation):
    """Terapkan mode interpolasi ke seluruh keyframe pada data_path tertentu.

    Interpolasi adalah properti KEYFRAME, bukan properti FCurve: menulis
    `fcurve.interpolation` melempar AttributeError dan menggagalkan seluruh
    proses animasi.
    """
    interp = _interpolation(interpolation)
    ad = getattr(obj, "animation_data", None)
    action = getattr(ad, "action", None) if ad else None
    if action is None:
        return 0
    diubah = 0
    for fc in action.fcurves:
        if data_path and fc.data_path != data_path:
            continue
        for kp in fc.keyframe_points:
            kp.interpolation = interp
            diubah += 1
        fc.update()
    return diubah


def set_render_range(start=1, end=250):
    """Atur rentang frame untuk animasi dan render."""
    scene = bpy.context.scene
    try:
        start, end = _frame_range(start, end)
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    scene.frame_start = start
    scene.frame_end = end
    return {"status": "success", "start": start, "end": end}


def set_frame(frame=1):
    """Pindahkan timeline ke frame tertentu."""
    frame = int(frame)
    bpy.context.scene.frame_set(frame)
    return {"status": "success", "frame": frame}


def create_action(object_name="", action_name=""):
    """Buat (atau tetapkan) datablock Action ke objek."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    name = action_name or f"{obj.name}Action"
    if bpy.data.actions.get(name) is not None:
        return {"error": f"Action '{name}' sudah ada."}
    action = bpy.data.actions.new(name)
    ad = obj.animation_data_create()
    ad.action = action
    return {"status": "success", "object": obj.name, "action": action.name}


def list_actions():
    actions = [{"name": a.name, "users": getattr(a, "users", 0)}
               for a in bpy.data.actions]
    return {"count": len(actions), "actions": actions}


def set_keyframe_interpolation(object_name="", interpolation="LINEAR"):
    """Atur interpolasi semua fcurve di action objek."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    interp = str(interpolation).upper()
    if interp not in INTERPOLATIONS:
        return {"error": f"Interpolasi tidak valid: {interpolation}. "
                         f"Tersedia: {', '.join(INTERPOLATIONS)}"}
    ad = getattr(obj, "animation_data", None)
    action = getattr(ad, "action", None) if ad else None
    if action is None:
        return {"error": f"{obj.name} belum punya Action."}
    # Interpolasi hanya ada di keyframe, bukan di FCurve-nya.
    count = 0
    total_key = 0
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = interp
            total_key += 1
        fc.update()
        count += 1
    return {"status": "success", "object": obj.name, "interpolation": interp,
            "fcurves": count, "keyframes": total_key}


def add_shape_key(object_name="", name="Key", value=0.0, frame=1, keyframe=False):
    """Tambah shape key dan opsional keyframe nilainya."""
    obj = _get_object(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    kb = obj.shape_key_add(name=name)
    if kb is None:
        return {"error": "shape_key_add gagal (mesh tanpa geometry?)."}
    if not 0.0 <= float(value) <= 1.0:
        return {"error": "Nilai shape key harus berada pada rentang 0..1."}
    kb.value = float(value)
    if keyframe:
        try:
            kb.keyframe_insert("value", frame=int(frame))
        except Exception as exc:
            return {"error": f"Gagal memberi keyframe shape key: {exc}"}
    return {"status": "success", "object": obj.name, "key": kb.name,
            "value": kb.value}


def list_shape_keys(object_name=""):
    obj = _get_object(object_name)
    if obj is None or obj.type != "MESH" or obj.data is None:
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    sk = obj.data.shape_keys
    if sk is None:
        return {"object": obj.name, "keys": []}
    keys = [{"name": kb.name, "value": round(getattr(kb, "value", 0.0), 4)}
            for kb in sk.key_blocks]
    return {"object": obj.name, "count": len(keys), "keys": keys}


def add_rigid_body(object_name="", body_type="ACTIVE", mass=1.0, friction=0.5,
                   bounciness=0.0, shape="CONVEX_HULL", animate=False):
    """Jadikan objek sebagai rigid body (simulasi fisika).

    `bpy.ops.rigidbody.*` terbukti berjalan di mode background, jadi tidak ada
    lagi penolakan dini di sini. Rigid body world dibuat otomatis bila scene
    belum punya, karena `object_add` butuh world tersebut.
    """
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    if obj.type != "MESH":
        return {"error": f"Rigid body hanya untuk objek mesh, bukan {obj.type}."}
    body_type = str(body_type).upper()
    shape = str(shape).upper()
    if body_type not in {"ACTIVE", "PASSIVE"}:
        return {"error": f"Tipe rigid body tidak valid: {body_type}"}
    if shape not in {"BOX", "SPHERE", "CAPSULE", "CYLINDER", "CONE",
                     "CONVEX_HULL", "MESH", "COMPOUND"}:
        return {"error": f"Bentuk collision tidak valid: {shape}"}
    try:
        mass = float(mass)
        friction = float(friction)
        bounciness = float(bounciness)
        if mass <= 0 or not 0.0 <= friction <= 1.0 or not 0.0 <= bounciness <= 1.0:
            raise ValueError("mass harus > 0; friction/bounciness harus 0..1.")
        if obj.name not in bpy.context.view_layer.objects:
            bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.rigidbody.object_add(type=body_type)
        rb = obj.rigid_body
        rb.mass = mass
        rb.friction = friction
        rb.restitution = bounciness
        rb.collision_shape = shape
        rb.kinematic = bool(animate)
        return {"status": "success", "object": obj.name,
                "body_type": body_type, "mass": mass}
    except Exception as exc:
        return {"error": f"Rigid body gagal: {exc}"}


def set_gravity(gravity=(0.0, 0.0, -9.81)):
    """Atur gravitasi scene untuk simulasi fisika."""
    scene = bpy.context.scene
    scene.gravity = Vector(gravity)
    return {"status": "success", "gravity": list(gravity)}


def keyframe_animation(object_name="", property="location", frames=None,
                       values=None, interpolation="BEZIER"):
    """Sisipkan keyframe di beberapa frame sekaligus beserta nilainya."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    frames = frames or [1, 30]
    values = values or [[0.0, 0.0, 0.0], [5.0, 0.0, 0.0]]
    if property not in ANIMATABLE_PROPERTIES:
        return {"error": f"Properti tidak didukung: {property}"}
    if len(frames) != len(values) or not frames:
        return {"error": "frames dan values harus sama panjang dan tidak kosong."}
    try:
        interpolation = _interpolation(interpolation)
        numeric_frames = [int(frame) for frame in frames]
        for frame, value in zip(numeric_frames, values):
            kind = ANIMATABLE_PROPERTIES[property]
            converted = Vector(value) if kind == "vector" else value
            setattr(obj, property, converted)
            obj.keyframe_insert(data_path=property, frame=frame)
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    _set_fcurve_interpolation(obj, property, interpolation)
    return {"status": "success", "object": obj.name, "property": property,
            "keys": len(numeric_frames)}


def clear_keyframes(object_name="", property="location"):
    """Hapus semua keyframe properti dari action objek."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    ad = getattr(obj, "animation_data", None)
    action = getattr(ad, "action", None) if ad else None
    if action is None:
        return {"status": "success", "object": obj.name, "cleared": 0}
    removed = 0
    for fc in list(action.fcurves):
        if property == "all" or fc.data_path == property:
            action.fcurves.remove(fc)
            removed += 1
    return {"status": "success", "object": obj.name, "property": property,
            "cleared": removed}


def animate_from_scratch(object_name="", start_frame=1, end_frame=48,
                         start_loc=None, end_loc=None, revolutions=0.0,
                         axis="Z", interpolation="BEZIER",
                         set_range=True):
    """Sekali jalan: bersihkan animasi lama, buat gerak baru, atur rentang.

    Menggabungkan clear -> animate_location/rotation -> interpolasi ->
    set_render_range supaya agent tidak perlu merangkai empat panggilan yang
    bisa gagal di tengah dan meninggalkan keyframe setengah jadi.
    """
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}

    langkah = []
    # Mulai dari kondisi bersih supaya keyframe lama tidak bercampur.
    if obj.animation_data is not None and obj.animation_data.action is not None:
        obj.animation_data_clear()
        langkah.append("clear")

    if start_loc is not None and end_loc is not None:
        r = animate_location(object_name=obj.name, start_frame=start_frame,
                             end_frame=end_frame, start_loc=start_loc,
                             end_loc=end_loc, interpolation=interpolation)
        if isinstance(r, dict) and "error" in r:
            return r
        langkah.append("animate_location")

    if float(revolutions) != 0.0:
        r = animate_rotation(object_name=obj.name, start_frame=start_frame,
                             end_frame=end_frame,
                             revolutions=float(revolutions), axis=axis,
                             interpolation=interpolation)
        if isinstance(r, dict) and "error" in r:
            return r
        langkah.append("animate_rotation")

    if not langkah or langkah == ["clear"]:
        return {"error": "Tidak ada gerak yang diminta: isi start_loc/end_loc "
                         "atau revolutions."}

    if set_range:
        set_render_range(start=int(start_frame), end=int(end_frame))
        langkah.append("set_render_range")

    fcurves = 0
    keyframes = 0
    if obj.animation_data is not None and obj.animation_data.action is not None:
        for fc in obj.animation_data.action.fcurves:
            fcurves += 1
            keyframes += len(fc.keyframe_points)

    return {"status": "success", "object": obj.name, "steps": langkah,
            "frame_start": int(start_frame), "frame_end": int(end_frame),
            "fcurves": fcurves, "keyframes": keyframes}
