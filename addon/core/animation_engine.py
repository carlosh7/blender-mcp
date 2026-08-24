"""
blender-mcp — Animation Engine
Motor de animación: Keyframes, Curves, Walk/Run cycles, Facial, Gestures.
"""

try:
    import bpy
except ImportError:
    bpy = None
import math

# ═══════════════════════════════════════════════════════════════
# KEYFRAMES BÁSICOS
# ═══════════════════════════════════════════════════════════════


def set_keyframe(obj, data_path, frame, value):
    """
    Establecer un keyframe.

    Args:
        obj: Objeto
        data_path: Ruta del dato (ej: "location", "rotation_euler")
        frame: Número de frame
        value: Valor a establecer
    """
    # Establecer valor
    setattr(obj, data_path, value)

    # Insertar keyframe
    obj.keyframe_insert(data_path=data_path, frame=frame)


def set_location_keyframes(obj, keyframes):
    """
    Establecer múltiples keyframes de ubicación.

    Args:
        obj: Objeto
        keyframes: Lista de [(frame, (x, y, z)), ...]
    """
    for frame, location in keyframes:
        set_keyframe(obj, "location", frame, location)


def set_rotation_keyframes(obj, keyframes):
    """
    Establecer múltiples keyframes de rotación.

    Args:
        obj: Objeto
        keyframes: Lista de [(frame, (x, y, z)), ...]
    """
    for frame, rotation in keyframes:
        set_keyframe(obj, "rotation_euler", frame, rotation)


def set_scale_keyframes(obj, keyframes):
    """
    Establecer múltiples keyframes de escala.

    Args:
        obj: Objeto
        keyframes: Lista de [(frame, (x, y, z)), ...]
    """
    for frame, scale in keyframes:
        set_keyframe(obj, "scale", frame, scale)


# ═══════════════════════════════════════════════════════════════
# ANIMACIONES PREDEFINIDAS
# ═══════════════════════════════════════════════════════════════


def create_walk_cycle(obj, frames=30, speed=1.0):
    """
    Crear ciclo de caminata REALISTA.

    Args:
        obj: Objeto a animar
        frames: Duración del ciclo
        speed: Velocidad de la animación
    """
    # Walk cycle realista con 4 fases:
    # 1. Contact (talón toca suelo)
    # 2. Passing (pierna pasando)
    # 3. High point (pierna en punto más alto)
    # 4. Down (pierna bajando)

    keyframes = []
    for i in range(frames + 1):
        t = i / frames
        frame = i

        # Movimiento hacia adelante
        y = t * speed

        # Bounce vertical (subir/bajar)
        bounce = 0.05 * math.sin(t * math.pi * 4)

        # Lean forward (inclinación)
        lean = 0.02 * math.sin(t * math.pi * 2)

        keyframes.append((frame, (lean, y, bounce)))

    set_location_keyframes(obj, keyframes)

    # Configurar frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Walk cycle creado: {frames} frames, velocidad {speed}")
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Walk cycle creado: {frames} frames, velocidad {speed}")


def create_run_cycle(obj, frames=20, speed=2.0):
    """
    Crear ciclo de corrida.
    """
    keyframes = []
    for i in range(frames + 1):
        t = i / frames
        frame = i

        y = t * speed * 2
        z_offset = 0.2 * math.sin(t * math.pi * 2)

        keyframes.append((frame, (0, y, z_offset)))

    set_location_keyframes(obj, keyframes)

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Run cycle creado: {frames} frames, velocidad {speed}")


def create_idle_animation(obj, frames=60, breath_amplitude=0.02):
    """
    Crear animación idle (respiración).
    """
    keyframes = []
    for i in range(frames + 1):
        t = i / frames
        frame = i

        # Respiración sinusoidal
        z_offset = breath_amplitude * math.sin(t * math.pi * 4)

        keyframes.append((frame, (0, 0, z_offset)))

    set_location_keyframes(obj, keyframes)

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Idle animation creada: {frames} frames")


def create_jump_animation(obj, frames=30, height=2.0):
    """
    Crear animación de salto.
    """
    keyframes = []
    for i in range(frames + 1):
        t = i / frames
        frame = i

        # Movimiento parabólico
        z = height * math.sin(t * math.pi)
        y = t * 2

        keyframes.append((frame, (0, y, z)))

    set_location_keyframes(obj, keyframes)

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Jump animation creada: {frames} frames")


def create_wave_animation(obj, frames=60, amplitude=0.5):
    """
    Crear animación de onda.
    """
    keyframes = []
    for i in range(frames + 1):
        t = i / frames
        frame = i

        x = amplitude * math.sin(t * math.pi * 4)
        y = amplitude * math.cos(t * math.pi * 4)

        keyframes.append((frame, (x, y, 0)))

    set_location_keyframes(obj, keyframes)

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Wave animation creada: {frames} frames")


def create_spin_animation(obj, frames=60, speed=1.0):
    """
    Crear animación de rotación.
    """
    keyframes = []
    for i in range(frames + 1):
        t = i / frames
        frame = i

        rotation = (0, 0, t * math.pi * 2 * speed)

        keyframes.append((frame, rotation))

    set_rotation_keyframes(obj, keyframes)

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Spin animation creada: {frames} frames")


# ═══════════════════════════════════════════════════════════════
# ANIMACIÓN FACIAL
# ═══════════════════════════════════════════════════════════════


def create_facial_expression(obj, expression, frames=30):
    """
    Crear expresión facial.

    Expresiones disponibles:
    - smile, frown, surprise, angry, sad, neutral
    """
    expressions = {
        "smile": {"Mouth_Open": 0.3, "Smile_L": 0.8, "Smile_R": 0.8},
        "frown": {"Mouth_Open": 0.2, "Frown_L": 0.8, "Frown_R": 0.8},
        "surprise": {"Mouth_Open": 0.8, "Brow_Up_L": 0.9, "Brow_Up_R": 0.9},
        "angry": {"Brow_Down_L": 0.9, "Brow_Down_R": 0.9, "Jaw_Open": 0.3},
        "sad": {"Brow_Down_L": 0.5, "Brow_Down_R": 0.5, "Mouth_Open": 0.1},
        "neutral": {},
    }

    if expression not in expressions:
        print(f"Expresión no encontrada: {expression}")
        return

    expr_data = expressions[expression]

    # Crear keyframes para cada shape key
    for sk_name, value in expr_data.items():
        if sk_name in obj.data.shape_keys.key_blocks:
            sk = obj.data.shape_keys.key_blocks[sk_name]

            # Frame 1: Valor actual
            sk.value = 0
            sk.keyframe_insert("value", frame=1)

            # Frame mid: Valor objetivo
            sk.value = value
            sk.keyframe_insert("value", frame=frames // 2)

            # Frame end: Volver a 0
            sk.value = 0
            sk.keyframe_insert("value", frame=frames)

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print(f"Expresión facial creada: {expression}")


# ═══════════════════════════════════════════════════════════════
# GESTOS
# ═══════════════════════════════════════════════════════════════


def create_wave_gesture(arm_obj, frames=30):
    """
    Crear gesto de saludo (ondeo de mano).
    """
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")

    # Animar UpperArm_R
    bone = arm_obj.pose.bones.get("UpperArm_R")
    if bone:
        bone.rotation_mode = "XYZ"

        # Frame 1: Brazo abajo
        bone.rotation_euler = (0, 0, 0)
        bone.keyframe_insert("rotation_euler", frame=1)

        # Frame 10: Brazo arriba
        bone.rotation_euler = (0, 0, math.radians(-120))
        bone.keyframe_insert("rotation_euler", frame=10)

        # Frame 20: Ondear
        bone.rotation_euler = (math.radians(20), 0, math.radians(-120))
        bone.keyframe_insert("rotation_euler", frame=20)

        # Frame 30: Volver
        bone.rotation_euler = (0, 0, math.radians(-120))
        bone.keyframe_insert("rotation_euler", frame=30)

        # Frame 40: Bajar
        bone.rotation_euler = (0, 0, 0)
        bone.keyframe_insert("rotation_euler", frame=40)

    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print("Gesto de saludo creado")


def create_point_gesture(arm_obj, frames=30):
    """
    Crear gesto de señalar.
    """
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")

    bone = arm_obj.pose.bones.get("UpperArm_R")
    if bone:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0, 0, math.radians(-90))
        bone.keyframe_insert("rotation_euler", frame=1)

    bone = arm_obj.pose.bones.get("LowerArm_R")
    if bone:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0, 0, math.radians(-45))
        bone.keyframe_insert("rotation_euler", frame=1)

    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames

    print("Gesto de señalar creado")


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def get_animation_info(obj):
    """Obtener información de animación de un objeto"""
    if not obj.animation_data:
        return {"has_animation": False}

    action = obj.animation_data.action
    if not action:
        return {"has_animation": False}

    return {
        "has_animation": True,
        "name": action.name,
        "frame_range": (action.frame_range[0], action.frame_range[1]),
        "fcurves": len(action.fcurves),
    }


def clear_animation(obj):
    """Limpiar animación de un objeto"""
    if obj.animation_data:
        obj.animation_data_clear()
    print(f"Animación limpiada: {obj.name}")


def set_interpolation(obj, interpolation="BEZIER"):
    """
    Establecer interpolación para todas las curvas de animación.

    Args:
        interpolation: 'CONSTANT', 'LINEAR', 'BEZIER', 'SINE'
    """
    if not obj.animation_data or not obj.animation_data.action:
        return

    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = interpolation


def list_animation_presets():
    """Listar presets de animación disponibles"""
    return {
        "walk": "Ciclo de caminata",
        "run": "Ciclo de corrida",
        "idle": "Animación idle (respiración)",
        "jump": "Salto",
        "wave": "Onda sinusoidal",
        "spin": "Rotación continua",
        "smile": "Expresión: sonrisa",
        "frown": "Expresión: ceño fruncido",
        "surprise": "Expresión: sorpresa",
        "angry": "Expresión: enojo",
        "sad": "Expresión: tristeza",
        "wave_gesture": "Gesto: saludo",
        "point_gesture": "Gesto: señalar",
        "dance": "Baile",
        "punch": "Golpe",
        "kick": "Patada",
        "clap": "Aplaudir",
        "nod": "Asentir con cabeza",
        "shake_head": "Negar con cabeza",
        "shrug": "Encogerse de hombros",
    }
