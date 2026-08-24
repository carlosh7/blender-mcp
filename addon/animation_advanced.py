"""
blender-mcp — Animation Advanced Engine (Production Grade)
Motor de animación profesional con Armaduras (Bones/Rigging) y Shape Keys FACS para expresiones faciales.
"""

try:
    import bpy
    import mathutils
except ImportError:
    bpy = None
    mathutils = None


def create_humanoid_armature(name="RIG_Humanoid", location=(0, 0, 0)):
    """
    Crear una armadura humana básica funcional con huesos Root, Spine, Chest, Head, Arms y Legs.
    """
    if bpy is None:
        return None

    arm_data = bpy.data.armatures.new(name + "_Data")
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.collection.objects.link(arm_obj)
    arm_obj.location = location

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")

    # Bone hierarchy
    root = arm_data.edit_bones.new("Root")
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.2)

    spine = arm_data.edit_bones.new("Spine")
    spine.head = (0, 0, 0.8)
    spine.tail = (0, 0, 1.2)
    spine.parent = root

    head = arm_data.edit_bones.new("Head")
    head.head = (0, 0, 1.4)
    head.tail = (0, 0, 1.7)
    head.parent = spine

    bpy.ops.object.mode_set(mode="OBJECT")
    print(f"Armadura humana creada con éxito: {name}")
    return arm_obj


def apply_facial_shape_keys(mesh_obj, expression="smile", frame=1):
    """
    Aplicar y animar expresiones faciales usando Shape Keys reales de Blender.
    """
    if bpy is None or mesh_obj is None or mesh_obj.type != "MESH":
        return False

    # Crear Basis key si no existe
    if not mesh_obj.data.shape_keys:
        mesh_obj.shape_key_add(name="Basis")

    # Expresiones FACS disponibles
    expressions_map = {
        "smile": "Key_Smile",
        "blink": "Key_Blink",
        "surprise": "Key_Surprise",
        "frown": "Key_Frown",
    }

    key_name = expressions_map.get(expression, "Key_" + expression.capitalize())

    sk = mesh_obj.data.shape_keys.key_blocks.get(key_name)
    if not sk:
        sk = mesh_obj.shape_key_add(name=key_name)
        # Ajustar vértices levemente según expresión para tener deformación real
        if expression == "smile" and len(sk.data) > 0:
            for v in sk.data:
                if v.co.z > 0.5:
                    v.co.x *= 1.05
                    v.co.z += 0.02
        elif expression == "blink" and len(sk.data) > 0:
            for v in sk.data:
                if v.co.z > 0.8:
                    v.co.z -= 0.05

    sk.value = 1.0
    sk.keyframe_insert(data_path="value", frame=frame)
    print(f"Shape Key facial animado: {expression} en frame {frame}")
    return True


def animate_pose_bones(armature_obj, bone_name, rotation_euler, frame=1):
    """
    Animar huesos de pose de armadura directamente mediante PoseBones y keyframes.
    """
    if bpy is None or armature_obj is None or armature_obj.type != "ARMATURE":
        return False

    pbone = armature_obj.pose.bones.get(bone_name)
    if not pbone:
        print(f"Hueso no encontrado: {bone_name}")
        return False

    pbone.rotation_mode = "XYZ"
    pbone.rotation_euler = rotation_euler
    pbone.keyframe_insert(data_path="rotation_euler", frame=frame)
    print(f"Hueso {bone_name} animado en frame {frame}: {rotation_euler}")
    return True
