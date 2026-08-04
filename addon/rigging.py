"""
rigging.py — Perintah rigging: armature, tulang, bone collection (4.0+),
constraint IK/FK, vertex group, automatic weight. Seluruh operasi termasuk
edit-mode berjalan di `blender -b` (background) maupun di GUI.
"""
import bpy
from mathutils import Euler, Matrix, Vector

from . import compat

CONSTRAINT_TYPES = (
    "COPY_LOCATION", "COPY_ROTATION", "COPY_SCALE", "COPY_TRANSFORMS",
    "TRACK_TO", "IK", "CHILD_OF", "LIMIT_LOCATION", "LIMIT_ROTATION",
    "LIMIT_SCALE", "TRANSFORM", "DAMPED_TRACK", "STRETCH_TO", "LOCKED_TRACK",
    "ACTION", "FLOOR", "FOLLOW_PATH", "CLAMP_TO", "SHRINKWRAP", "PIVOT",
)


def _get_armature(name):
    """Ambil objek armature berdasarkan nama.

    Mengembalikan None bila nama itu dipakai objek non-armature, supaya
    pemanggil tidak menerima mesh lalu gagal dengan pesan membingungkan.
    """
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "ARMATURE":
        return None
    return obj


def _armature_data(obj):
    if obj is None or obj.type != "ARMATURE":
        return None
    return obj.data


def create_armature(name="Armature", location=(0.0, 0.0, 0.0),
                    add_root_bone=True):
    """Buat objek armature (tulang root opsional). Aman di mode background."""
    if bpy.data.objects.get(name) is not None:
        return {"error": f"Objek '{name}' sudah ada."}
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(location)
    result = {"status": "success", "object": obj.name, "bones": 0}
    if add_root_bone:
        r = add_bone(obj.name, "Root", (0.0, 0.0, 0.0), (0.0, 0.0, 0.2))
        if "error" not in r:
            result["bones"] = 1
    return result


def _enter_edit_mode(arm_obj):
    """Masuk mode EDIT armature. Berfungsi juga di mode background.

    Sebelumnya di background kode hanya *menyentuh* `arm_obj.data.edit_bones`
    lalu menganggap berhasil. Membaca koleksi itu tidak memindahkan objek ke
    mode edit, sehingga `edit_bones.new()` selalu gagal dengan
    "not in edit mode". `bpy.ops.object.mode_set` sendiri terbukti jalan di
    background asalkan objeknya aktif dan terpilih.
    """
    data = _armature_data(arm_obj)
    punya_edit_bones = data is not None and hasattr(data, "edit_bones")
    try:
        vl = getattr(bpy.context, "view_layer", None)
        vl_objects = getattr(vl, "objects", None) if vl is not None else None
        if vl_objects is None:
            return None if punya_edit_bones else \
                {"error": "edit_bones tidak tersedia di lingkungan ini."}

        # Objek yang baru di-link belum tentu langsung terdaftar di view
        # layer karena depsgraph baru disegarkan belakangan.
        if arm_obj.name not in vl_objects:
            try:
                vl.update()
            except Exception:
                pass

        # Objek di luar view layer tidak bisa dijadikan aktif, jadi
        # mode_set dilewati. Selama edit_bones bisa dipakai, pembuatan
        # tulang tetap dilanjutkan lewat data API.
        if arm_obj.name not in vl_objects:
            return None if punya_edit_bones else \
                {"error": f"{arm_obj.name} tidak ada di view layer aktif."}

        if bpy.context.object is not None and getattr(bpy.context.object, "mode", "OBJECT") != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        arm_obj.select_set(True)
        vl_objects.active = arm_obj
        bpy.ops.object.mode_set(mode="EDIT")
        return None
    except Exception as e:
        if punya_edit_bones:
            return None
        return {"error": f"Gagal masuk mode EDIT: {e}"}


def _leave_edit_mode():
    """Kembali ke mode OBJECT agar tulang tersalin ke `armature.bones`.

    Selama masih di mode edit, tulang baru hanya ada sebagai `edit_bones`;
    `armature.bones` baru terisi setelah keluar dari mode edit.
    """
    try:
        if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass


def add_bone(armature_name="", bone_name="Bone", head=(0.0, 0.0, 0.0),
             tail=(0.0, 0.0, 1.0), parent="", collection="MCP_Bones"):
    """Tambah tulang ke armature. Berfungsi di GUI maupun background."""
    arm_obj = _get_armature(armature_name)
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    arm = _armature_data(arm_obj)
    if arm is None:
        return {"error": f"{armature_name} bukan armature."}
    err = _enter_edit_mode(arm_obj)
    if err:
        return err
    try:
        edit_bones = arm.edit_bones
        if edit_bones.get(bone_name) is not None:
            return {"error": f"Tulang '{bone_name}' sudah ada."}
        bone = edit_bones.new(bone_name)
        bone.head = Vector(head)
        bone.tail = Vector(tail)
        if bone.length == 0.0:
            edit_bones.remove(bone)
            return {"error": "head dan tail tidak boleh sama; tulang "
                             "berpanjang nol akan dibuang Blender."}
        if parent:
            p = edit_bones.get(parent)
            if p is None:
                edit_bones.remove(bone)
                return {"error": f"Tulang induk tidak ditemukan: {parent}"}
            bone.parent = p
        nama = bone.name
        h, t = list(bone.head), list(bone.tail)
        assigned = compat.set_bone_collection(arm, bone, collection)
        if not assigned:
            edit_bones.remove(bone)
            _leave_edit_mode()
            return {"error": f"Gagal menetapkan tulang ke koleksi: {collection}"}
        _leave_edit_mode()
        return {"status": "success", "armature": arm_obj.name, "bone": nama,
                "head": h, "tail": t, "total": len(arm.bones),
                "collection": collection}
    except Exception as e:
        _leave_edit_mode()
        return {"error": f"Gagal membuat tulang: {e}"}


def remove_bone(armature_name="", bone_name=""):
    arm_obj = _get_armature(armature_name)
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    arm = _armature_data(arm_obj)
    if arm is None:
        return {"error": f"{armature_name} bukan armature."}
    err = _enter_edit_mode(arm_obj)
    if err:
        return err
    try:
        eb = arm.edit_bones.get(bone_name)
        if eb is None:
            _leave_edit_mode()
            return {"error": f"Tulang tidak ditemukan: {bone_name}"}
        arm.edit_bones.remove(eb)
        _leave_edit_mode()
        return {"status": "success", "removed": bone_name,
                "total": len(arm.bones)}
    except Exception as e:
        _leave_edit_mode()
        return {"error": f"Gagal menghapus tulang: {e}"}


def list_bones(armature_name=""):
    arm_obj = _get_armature(armature_name)
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    arm = _armature_data(arm_obj)
    if arm is None:
        return {"error": f"{armature_name} bukan armature."}
    bones = []
    for b in arm.bones:
        bones.append({
            "name": b.name,
            "parent": b.parent.name if b.parent else None,
            "head": [round(v, 4) for v in b.head],
            "tail": [round(v, 4) for v in b.tail],
            "use_deform": bool(b.use_deform),
        })
    return {"armature": arm_obj.name, "count": len(bones), "bones": bones}


def rename_bone(armature_name="", bone_name="", new_name=""):
    arm_obj = _get_armature(armature_name)
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    arm = _armature_data(arm_obj)
    if arm is None or not new_name:
        return {"error": "Parameter tidak valid."}
    err = _enter_edit_mode(arm_obj)
    if err:
        return err
    try:
        edit_bone = arm.edit_bones.get(bone_name)
        if edit_bone is None:
            return {"error": f"Tulang tidak ditemukan: {bone_name}"}
        edit_bone.name = new_name
        actual_name = edit_bone.name
        return {"status": "success", "renamed": bone_name, "to": actual_name}
    finally:
        _leave_edit_mode()


def add_vertex_group(object_name="", group_name="Group"):
    """Buat vertex group pada objek mesh. Aman di mode background."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    for vg in obj.vertex_groups:
        if vg.name == group_name:
            return {"error": f"Grup '{group_name}' sudah ada."}
    vg = obj.vertex_groups.new(name=group_name)
    return {"status": "success", "object": obj.name, "group": vg.name}


def assign_vertex_weights(object_name="", group_name="", vertex_indices=None,
                          weight=1.0, mode="ADD"):
    """Isi bobot sebuah vertex group lewat data API. Aman di background."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    vg = None
    for g in obj.vertex_groups:
        if g.name == group_name:
            vg = g
            break
    if vg is None:
        return {"error": f"Grup tidak ditemukan: {group_name}"}
    idx = vertex_indices if vertex_indices is not None else list(range(len(obj.data.vertices)))
    indices = [int(index) for index in idx]
    if any(index < 0 or index >= len(obj.data.vertices) for index in indices):
        return {"error": "Indeks vertex di luar jangkauan."}
    weight = float(weight)
    if not 0.0 <= weight <= 1.0:
        return {"error": "weight harus berada pada rentang 0..1."}
    mode = str(mode).upper()
    if mode not in {"REPLACE", "ADD", "SUBTRACT"}:
        return {"error": f"Mode bobot tidak valid: {mode}"}
    vg.add(indices, weight, mode)
    return {"status": "success", "object": obj.name, "group": vg.name,
            "vertices": len(indices), "weight": weight}


def remove_vertex_group(object_name="", group_name=""):
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    vg = None
    for g in obj.vertex_groups:
        if g.name == group_name:
            vg = g
            break
    if vg is None:
        return {"error": f"Grup tidak ditemukan: {group_name}"}
    obj.vertex_groups.remove(vg)
    return {"status": "success", "removed": group_name}


def add_constraint(object_name="", constraint_type="COPY_LOCATION",
                   target_name="", subtarget="", influence=1.0, **extra):
    """Tambah constraint pada objek atau pose bone. Aman di background."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    ctype = str(constraint_type).upper()
    if ctype not in CONSTRAINT_TYPES:
        return {"error": f"Tipe constraint tidak dikenal: {constraint_type}. "
                         f"Tersedia: {', '.join(CONSTRAINT_TYPES)}"}
    target_obj = bpy.data.objects.get(target_name) if target_name else None
    if target_name and target_obj is None:
        return {"error": f"Objek target tidak ditemukan: {target_name}"}

    if ctype == "IK" and subtarget and obj.type == "ARMATURE":
        # IK lives on a pose bone
        pb = obj.pose.bones.get(subtarget)
        if pb is None:
            return {"error": f"Tulang pose tidak ditemukan: {subtarget}"}
        con = pb.constraints.new(ctype)
    else:
        con = obj.constraints.new(ctype)

    try:
        con.target = target_obj
        con.influence = float(influence)
        if not 0.0 <= con.influence <= 1.0:
            raise ValueError("influence harus berada pada rentang 0..1.")
        if subtarget:
            if not hasattr(con, "subtarget"):
                raise ValueError(f"Constraint {ctype} tidak mendukung subtarget.")
            con.subtarget = subtarget
        for key, value in extra.items():
            if not hasattr(con, key):
                raise ValueError(f"Properti constraint tidak dikenal: {key}")
            setattr(con, key, value)
    except (AttributeError, TypeError, ValueError) as exc:
        (pb.constraints if ctype == "IK" and subtarget and obj.type == "ARMATURE"
         else obj.constraints).remove(con)
        return {"error": str(exc)}
    return {"status": "success", "object": obj.name, "constraint": con.name,
            "type": ctype, "target": target_name}


def setup_ik_chain(armature_name="", bone_name="", target_object="",
                   pole_object="", chain_count=3):
    """Pasang constraint IK di pose bone, dengan pole target opsional."""
    arm_obj = _get_armature(armature_name)
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    if arm_obj.type != "ARMATURE":
        return {"error": f"{armature_name} bukan armature."}
    # `pose` ada di OBJEK armature, bukan di datanya (`bpy.types.Armature`).
    pose = getattr(arm_obj, "pose", None)
    pb = pose.bones.get(bone_name) if pose else None
    if pb is None:
        return {"error": f"Tulang pose tidak ditemukan: {bone_name}"}

    con = pb.constraints.new("IK")
    con.chain_count = int(chain_count)

    # Tanpa target, IK tetap sah: rantainya memakai target kosong sampai
    # nanti diisi. Jadi target yang tidak ada bukan alasan untuk gagal total.
    target = bpy.data.objects.get(target_object) if target_object else None
    if target_object and target is None:
        pb.constraints.remove(con)
        return {"error": f"Target tidak ditemukan: {target_object}"}
    if target is not None:
        con.target = target

    pole = bpy.data.objects.get(pole_object) if pole_object else None
    if pole_object and pole is None:
        pb.constraints.remove(con)
        return {"error": f"Pole target tidak ditemukan: {pole_object}"}
    if pole is not None:
        con.pole_target = pole
        con.pole_angle = 0.0

    return {"status": "success", "armature": arm_obj.name, "bone": bone_name,
            "constraint": con.name, "chain_count": int(chain_count),
            "target": target.name if target else None}


def auto_rig_weight(object_name="", armature_name=""):
    """Ikat mesh ke armature memakai bobot otomatis (ARMATURE_AUTO)."""
    obj = bpy.data.objects.get(object_name)
    arm_obj = _get_armature(armature_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    if obj.type != "MESH":
        return {"error": "auto_rig_weight hanya berlaku untuk mesh."}
    if compat.is_background():
        return {"error": "auto_rig_weight memerlukan antarmuka Blender; "
                         "gunakan add_armature_modifier dan assign_vertex_weights "
                         "untuk alur background yang deterministik."}
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        return {"status": "success", "object": obj.name,
                "armature": arm_obj.name, "parented": True,
                "weights": "AUTOMATIC"}
    except Exception as exc:
        return {"error": f"Auto-weight gagal: {exc}"}


def mirror_bones(armature_name="", axis="X"):
    """Cerminkan tulang armature agar simetris kiri-kanan."""
    arm_obj = _get_armature(armature_name)
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    raw_axis = str(axis).upper()
    if raw_axis not in {"X", "+X", "-X"}:
        return {"error": "mirror_bones hanya mendukung sumbu X, +X, atau -X."}
    err = _enter_edit_mode(arm_obj)
    if err:
        return err
    direction = "POSITIVE_X" if raw_axis == "-X" else "NEGATIVE_X"
    try:
        bpy.ops.armature.select_all(action="SELECT")
        bpy.ops.armature.symmetrize(direction=direction)
        return {"status": "success", "armature": arm_obj.name, "axis": axis,
                "direction": direction}
    except Exception as exc:
        return {"error": f"Symmetrize gagal: {exc}"}
    finally:
        _leave_edit_mode()




def reset_pose(armature_name="", bone_name=""):
    """Kembalikan transform pose bone ke posisi rest."""
    arm_obj = _get_armature(armature_name)
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    pose = getattr(arm_obj, "pose", None)
    if arm_obj.type != "ARMATURE" or pose is None:
        return {"error": f"{armature_name} bukan armature."}
    if bone_name:
        pb = pose.bones.get(bone_name)
        if pb is None:
            return {"error": f"Tulang pose tidak ditemukan: {bone_name}"}
        pb.matrix_basis = Matrix.Identity(4)
        return {"status": "success", "bone": bone_name, "reset": True}
    jumlah = 0
    for pb in pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
        jumlah += 1
    return {"status": "success", "reset": "all", "bones": jumlah}


def pose_bone(armature_name="", bone_name="", location=None, rotation=None,
              scale=None, relative=True):
    """Atur transform pose bone (ruang pose)."""
    arm_obj = _get_armature(armature_name)
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    pose = getattr(arm_obj, "pose", None)
    if arm_obj.type != "ARMATURE" or pose is None:
        return {"error": f"{armature_name} bukan armature."}
    pb = pose.bones.get(bone_name)
    if pb is None:
        return {"error": f"Tulang pose tidak ditemukan: {bone_name}"}

    if location is not None:
        v = Vector(location)
        pb.location = pb.location + v if relative else v
    if rotation is not None:
        r = Vector(rotation)
        # Menulis ke `rotation_euler` tidak berpengaruh bila mode rotasi
        # tulang QUATERNION (umum pada rig hasil impor). Jadi nilainya
        # ditulis ke kanal yang sesuai dengan `rotation_mode`.
        if pb.rotation_mode == "QUATERNION":
            e = Euler((r.x, r.y, r.z), "XYZ")
            q = e.to_quaternion()
            pb.rotation_quaternion = (pb.rotation_quaternion @ q) if relative else q
        elif pb.rotation_mode == "AXIS_ANGLE":
            pb.rotation_axis_angle = (r.length, r.x, r.y, r.z)
        else:
            e = pb.rotation_euler
            pb.rotation_euler = (e.x + r.x, e.y + r.y, e.z + r.z) if relative else tuple(r)
    if scale is not None:
        s = Vector(scale)
        pb.scale = pb.scale * s if relative else s

    return {"status": "success", "bone": bone_name,
            "rotation_mode": pb.rotation_mode,
            "location": [round(v, 4) for v in pb.location]}


def add_armature_modifier(object_name="", armature_name=""):
    """Tambah modifier Armature ke mesh tanpa membuat bobot otomatis."""
    obj = bpy.data.objects.get(object_name)
    arm_obj = _get_armature(armature_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    if arm_obj is None:
        return {"error": f"Armature tidak ditemukan: {armature_name}"}
    if obj.type != "MESH":
        return {"error": "add_armature_modifier hanya berlaku untuk mesh."}
    existing = next((modifier for modifier in obj.modifiers
                     if modifier.type == "ARMATURE" and modifier.object == arm_obj), None)
    modifier = existing or obj.modifiers.new(name="Armature", type="ARMATURE")
    modifier.object = arm_obj
    world_matrix = obj.matrix_world.copy()
    obj.parent = arm_obj
    obj.matrix_world = world_matrix
    return {"status": "success", "object": obj.name,
            "armature": arm_obj.name, "modifier": modifier.name}


def rig_from_scratch(object_name="", armature_name="", bones=None,
                     auto_weight=True):
    """Buat armature, rantai tulang, modifier, lalu binding deterministik.

    `bones` berupa daftar dict {"name", "head", "tail", "parent"}. Di mode
    background, pembobotan otomatis operator tidak tersedia; satu tulang akan
    menerima seluruh vertex. Rig multi-tulang harus memasok pembobotan manual
    melalui `assign_vertex_weights` atau dijalankan lewat UI.
    """
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    if obj.type != "MESH":
        return {"error": f"Rig butuh objek mesh, bukan {obj.type}."}

    nama_arm = armature_name or f"Rig_{obj.name}"
    if _get_armature(nama_arm) is not None:
        return {"error": f"Armature '{nama_arm}' sudah ada."}
    result = create_armature(name=nama_arm, location=tuple(obj.location),
                             add_root_bone=False)
    if "error" in result:
        return result
    arm_obj = _get_armature(nama_arm)

    if not bones:
        height = max(float(obj.dimensions.z), 0.001)
        bones = [{"name": "Root", "head": (0.0, 0.0, -height / 2.0),
                  "tail": (0.0, 0.0, height / 2.0)}]
    if not isinstance(bones, list) or not bones:
        return {"error": "bones harus berupa daftar tulang yang tidak kosong."}

    created = []
    for spec in bones:
        if not isinstance(spec, dict):
            return {"error": "Setiap tulang harus berupa objek/dict."}
        result = add_bone(
            armature_name=arm_obj.name,
            bone_name=spec.get("name", "Bone"),
            head=spec.get("head", (0.0, 0.0, 0.0)),
            tail=spec.get("tail", (0.0, 0.0, 1.0)),
            parent=spec.get("parent", ""),
            collection=spec.get("collection", "MCP_Bones"),
        )
        if "error" in result:
            return {"error": f"Gagal pada tulang '{spec.get('name', 'Bone')}': "
                             f"{result['error']}", "created": created}
        created.append(result["bone"])

    modifier = add_armature_modifier(object_name=obj.name, armature_name=arm_obj.name)
    if "error" in modifier:
        return modifier

    binding = {"mode": "MODIFIER_ONLY"}
    if auto_weight:
        if compat.is_background():
            if len(created) != 1:
                return {"error": "Pembobotan otomatis multi-tulang memerlukan UI. "
                                 "Gunakan assign_vertex_weights untuk setiap tulang.",
                        "armature": arm_obj.name, "bones": created}
            group = add_vertex_group(obj.name, created[0])
            if "error" in group:
                return group
            weights = assign_vertex_weights(obj.name, created[0], None, 1.0, "REPLACE")
            if "error" in weights:
                return weights
            binding = {"mode": "SINGLE_BONE_BACKGROUND", "group": created[0]}
        else:
            binding = auto_rig_weight(obj.name, arm_obj.name)
            if "error" in binding:
                return binding

    return {"status": "success", "object": obj.name,
            "armature": arm_obj.name, "bones": created,
            "auto_weight": bool(auto_weight), "binding": binding}
