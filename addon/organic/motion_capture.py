"""
blender-mcp — Motion Capture System
Sistema de captura de movimiento básico.
Inspirado en BlendArMocap.
"""

import math

import bpy

# ═══════════════════════════════════════════════════════════════
# MOTION DATA
# ═══════════════════════════════════════════════════════════════

MOTION_PRESETS = {
    "wave": {
        "description": "Gesto de saludo",
        "frames": 40,
        "bones": {
            "UpperArm_R": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 10, "rotation": (0, 0, math.radians(-120))},
                {"frame": 20, "rotation": (math.radians(20), 0, math.radians(-120))},
                {"frame": 30, "rotation": (0, 0, math.radians(-120))},
                {"frame": 40, "rotation": (0, 0, 0)},
            ],
        },
    },
    "point": {
        "description": "Gesto de señalar",
        "frames": 30,
        "bones": {
            "UpperArm_R": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 15, "rotation": (0, 0, math.radians(-90))},
                {"frame": 30, "rotation": (0, 0, math.radians(-90))},
            ],
            "LowerArm_R": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 15, "rotation": (0, 0, math.radians(-45))},
                {"frame": 30, "rotation": (0, 0, math.radians(-45))},
            ],
        },
    },
    "nod": {
        "description": "Asentir con la cabeza",
        "frames": 30,
        "bones": {
            "Head": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 10, "rotation": (math.radians(15), 0, 0)},
                {"frame": 20, "rotation": (0, 0, 0)},
                {"frame": 30, "rotation": (0, 0, 0)},
            ],
        },
    },
    "shake_head": {
        "description": "Negar con la cabeza",
        "frames": 30,
        "bones": {
            "Head": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 10, "rotation": (0, math.radians(20), 0)},
                {"frame": 20, "rotation": (0, math.radians(-20), 0)},
                {"frame": 30, "rotation": (0, 0, 0)},
            ],
        },
    },
    "shrug": {
        "description": "Encogerse de hombros",
        "frames": 30,
        "bones": {
            "UpperArm_L": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 10, "rotation": (0, 0, math.radians(10))},
                {"frame": 20, "rotation": (0, 0, math.radians(10))},
                {"frame": 30, "rotation": (0, 0, 0)},
            ],
            "UpperArm_R": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 10, "rotation": (0, 0, math.radians(-10))},
                {"frame": 20, "rotation": (0, 0, math.radians(-10))},
                {"frame": 30, "rotation": (0, 0, 0)},
            ],
        },
    },
    "clap": {
        "description": "Aplaudir",
        "frames": 20,
        "bones": {
            "UpperArm_L": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 10, "rotation": (0, 0, math.radians(60))},
                {"frame": 15, "rotation": (0, 0, math.radians(60))},
                {"frame": 20, "rotation": (0, 0, 0)},
            ],
            "UpperArm_R": [
                {"frame": 1, "rotation": (0, 0, 0)},
                {"frame": 10, "rotation": (0, 0, math.radians(-60))},
                {"frame": 15, "rotation": (0, 0, math.radians(-60))},
                {"frame": 20, "rotation": (0, 0, 0)},
            ],
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# MOTION CAPTURE
# ═══════════════════════════════════════════════════════════════


def apply_motion_preset(arm_obj, preset_name):
    """
    Aplicar preset de movimiento a un esqueleto.

    Args:
        arm_obj: Objeto armature
        preset_name: Nombre del preset

    Returns:
        bool: True si fue exitoso
    """
    if preset_name not in MOTION_PRESETS:
        print(f"Preset no encontrado: {preset_name}")
        return False

    preset = MOTION_PRESETS[preset_name]

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")

    for bone_name, keyframes in preset["bones"].items():
        bone = arm_obj.pose.bones.get(bone_name)
        if not bone:
            print(f"Hueso no encontrado: {bone_name}")
            continue

        bone.rotation_mode = "XYZ"

        for kf in keyframes:
            bone.rotation_euler = kf["rotation"]
            bone.keyframe_insert("rotation_euler", frame=kf["frame"])

    bpy.ops.object.mode_set(mode="OBJECT")

    # Configurar frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = preset["frames"]

    print(f"Preset aplicado: {preset_name} ({preset['frames']} frames)")
    return True


def record_motion(arm_obj, frames=100, fps=24):
    """
    Grabar movimiento desde la pose actual.

    Args:
        arm_obj: Objeto armature
        frames: Número de frames a grabar
        fps: Frames por segundo

    Returns:
        dict con datos grabados
    """
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")

    recorded = {}

    for frame in range(1, frames + 1):
        bpy.context.scene.frame_set(frame)

        frame_data = {}
        for bone in arm_obj.pose.bones:
            frame_data[bone.name] = {
                "location": list(bone.location),
                "rotation": list(bone.rotation_euler),
                "scale": list(bone.scale),
            }

        recorded[frame] = frame_data

    bpy.ops.object.mode_set(mode="OBJECT")

    print(f"Movimiento grabado: {frames} frames")
    return recorded


def playback_motion(arm_obj, motion_data):
    """
    Reproducir movimiento grabado.

    Args:
        arm_obj: Objeto armature
        motion_data: Datos de movimiento grabados
    """
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")

    for frame, frame_data in motion_data.items():
        for bone_name, bone_data in frame_data.items():
            bone = arm_obj.pose.bones.get(bone_name)
            if bone:
                bone.location = bone_data["location"]
                bone.rotation_euler = bone_data["rotation"]
                bone.scale = bone_data["scale"]
                bone.keyframe_insert("location", frame=frame)
                bone.keyframe_insert("rotation_euler", frame=frame)
                bone.keyframe_insert("scale", frame=frame)

    bpy.ops.object.mode_set(mode="OBJECT")

    # Configurar frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = max(motion_data.keys())

    print(f"Movimiento reproducido: {len(motion_data)} frames")


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def list_motion_presets():
    """Listar presets de movimiento disponibles"""
    return {k: v["description"] for k, v in MOTION_PRESETS.items()}


def get_motion_info(preset_name):
    """Obtener información de un preset"""
    if preset_name not in MOTION_PRESETS:
        return None

    preset = MOTION_PRESETS[preset_name]
    return {
        "name": preset_name,
        "description": preset["description"],
        "frames": preset["frames"],
        "bones": list(preset["bones"].keys()),
    }
