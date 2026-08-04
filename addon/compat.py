"""
compat.py — Lapisan kompatibilitas versi Blender.

Menargetkan Blender 4.2 LTS sampai 5.x. Memusatkan beberapa API yang berubah
pada rentang tersebut agar modul perintah tetap bersih dan kompatibel ke depan:
  * temp_override            (4.0+; legacy fallback for <=3.6)
  * bone collections         (4.0+ replaces armature layers)
  * EEVEE render settings    (4.2 "EEVEE Next" moved sample settings)
  * Cycles device naming     (4.0+ uses "GPU"/"CPU")
"""
import bpy

BLENDER_4_0 = (4, 0, 0)
BLENDER_4_2 = (4, 2, 0)
BLENDER_5_0 = (5, 0, 0)


def version() -> tuple:
    return tuple(bpy.app.version)


def at_least(min_version: tuple) -> bool:
    return bpy.app.version >= min_version


def is_background() -> bool:
    """True saat menjalankan `blender -b` (tanpa konteks window/area)."""
    return bool(getattr(bpy.app, "background", False))


def render_engine():
    """Engine render scene saat ini (dinormalisasi)."""
    return getattr(bpy.context.scene.render, "engine", "BLENDER_EEVEE_NEXT")


def temp_override(**kwargs):
    """Context override kompatibel Blender 4.0+; no-op di versi lama."""
    ctx = bpy.context
    if hasattr(ctx, "temp_override"):
        return ctx.temp_override(**kwargs)

    import contextlib

    @contextlib.contextmanager
    def _legacy():
        yield ctx

    return _legacy()


def view3d_area():
    """Area VIEW_3D pertama dari window pertama, atau None (mode background)."""
    wm = bpy.context.window_manager
    for win in getattr(wm, "windows", []):
        for area in getattr(getattr(win, "screen", None), "areas", []):
            if area.type == "VIEW_3D":
                return win, area
    return None, None


def run_ui_operator(op_path, **kwargs):
    """Jalankan operator yang bergantung UI; mengembalikan dict atau error jelas."""
    if is_background():
        return {"error": "Perintah ini memerlukan antarmuka Blender (tidak berfungsi di mode background)."}
    win, area = view3d_area()
    if area is None:
        return {"error": "Tidak ada window 3D untuk operasi ini."}
    parts = op_path.split(".")
    target = bpy.ops
    for part in parts:
        target = getattr(target, part)
    with temp_override(window=win, area=area):
        return target(**kwargs)


def get_bone_collections(armature):
    """API bone collections (4.0+); fallback ke pelabelan layer lama."""
    if hasattr(armature, "collections"):
        return armature.collections
    return None


def assign_bone_to_layer(bone, layer_index):
    """Fallback lama: letakkan tulang pada layer (armature.layers pra-4.0)."""
    try:
        arm = bone.id_data
        arm.layers[layer_index] = True
        bone.layers = [i == layer_index for i in range(32)]
    except Exception:
        pass


def set_bone_collection(armature, bone, collection_name=None):
    """Tetapkan Bone/PoseBone/EditBone ke bone collection Blender 4.0+."""
    colls = get_bone_collections(armature)
    if colls is not None:
        name = collection_name or "MCP_Bones"
        target = next((collection for collection in colls if collection.name == name), None)
        if target is None:
            target = colls.new(name=name)
        try:
            target.assign(bone)
            return True
        except (AttributeError, TypeError, RuntimeError):
            return False
    assign_bone_to_layer(bone, 0)
    return True


def cycles_device(device: str) -> str:
    """Normalkan nama device Cycles untuk Blender saat ini."""
    d = str(device).upper()
    if d in ("CPU", "GPU", "OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        return d
    return "CPU"


def set_render_samples(scene, samples: int):
    """Atur sample render untuk engine aktif (EEVEE Next vs Cycles)."""
    engine = render_engine()
    try:
        if "CYCLES" in engine.upper():
            scene.cycles.samples = int(samples)
        elif "EEVEE" in engine.upper():
            # EEVEE Next (4.2+): scene.eevee.samples; legacy: taa_render_samples
            eevee = scene.eevee
            if hasattr(eevee, "samples"):
                eevee.samples = int(samples)
            elif hasattr(eevee, "taa_render_samples"):
                eevee.taa_render_samples = int(samples)
        return {"engine": engine, "samples": int(samples)}
    except Exception as e:
        return {"engine": engine, "samples": int(samples), "warning": str(e)}


def select_and_activate(obj):
    """Jadikan obj aktif + terpilih tanpa mengubah seleksi lain."""
    try:
        bpy.context.view_layer.objects.active = obj
    except Exception:
        pass
    try:
        obj.select_set(True, view_layer=bpy.context.view_layer)
    except Exception:
        try:
            obj.select_set(True)
        except Exception:
            pass
    return obj
