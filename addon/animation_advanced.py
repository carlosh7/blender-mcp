"""
blender-mcp — Animation Advanced Engine
Motor de animación avanzada: Walk/Run cycles, Facial, Gestures, Procedural.
"""
try:
    import bpy
except ImportError:
    bpy = None

import math


# ═══════════════════════════════════════════════════════════════
# WALK CYCLE PROCEDURAL
# ═══════════════════════════════════════════════════════════════

def walk_cycle_procedural(obj, frames=30, speed=1.0, bounce=0.05):
    """
    Crear walk cycle procedural realista.
    
    Args:
        obj: Objeto a animar
        frames: Duración del ciclo
        speed: Velocidad
        bounce: Amplitud del bounce
    """
    if bpy is None or obj is None:
        return False
    
    keyframes = []
    for i in range(frames + 1):
        t = i / frames
        frame = i
        
        # Movimiento hacia adelante
        y = t * speed
        
        # Bounce vertical
        z = bounce * math.sin(t * math.pi * 4)
        
        # Lean forward
        lean = 0.02 * math.sin(t * math.pi * 2)
        
        keyframes.append((frame, (lean, y, z)))
    
    for frame, loc in keyframes:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    
    print(f"Walk cycle: {frames} frames, speed={speed}")
    return True


# ═══════════════════════════════════════════════════════════════
# RUN CYCLE PROCEDURAL
# ═══════════════════════════════════════════════════════════════

def run_cycle_procedural(obj, frames=20, speed=2.0, bounce=0.1):
    """
    Crear run cycle procedural realista.
    """
    if bpy is None or obj is None:
        return False
    
    keyframes = []
    for i in range(frames + 1):
        t = i / frames
        frame = i
        
        y = t * speed * 2
        z = bounce * math.sin(t * math.pi * 2)
        lean = 0.05 * math.sin(t * math.pi * 2)
        
        keyframes.append((frame, (lean, y, z)))
    
    for frame, loc in keyframes:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    
    print(f"Run cycle: {frames} frames, speed={speed}")
    return True


# ═══════════════════════════════════════════════════════════════
# FACIAL ANIMATION
# ═══════════════════════════════════════════════════════════════

def facial_animation(obj, expression="neutral", frames=30):
    """
    Crear animación facial.
    
    Args:
        obj: Objeto con shape keys
        expression: 'neutral', 'smile', 'frown', 'surprise', 'angry', 'sad'
        frames: Duración
    """
    if bpy is None or obj is None:
        return False
    
    if not obj.data.shape_keys:
        print("No shape keys found")
        return False
    
    # Valores de expresiones
    expressions = {
        "neutral": {},
        "smile": {"Mouth_Open": 0.3, "Smile_L": 0.8, "Smile_R": 0.8},
        "frown": {"Mouth_Open": 0.2, "Frown_L": 0.8, "Frown_R": 0.8},
        "surprise": {"Mouth_Open": 0.8, "Brow_Up_L": 0.9, "Brow_Up_R": 0.9},
        "angry": {"Brow_Down_L": 0.9, "Brow_Down_R": 0.9, "Jaw_Open": 0.3},
        "sad": {"Brow_Down_L": 0.5, "Brow_Down_R": 0.5, "Mouth_Open": 0.1},
    }
    
    if expression not in expressions:
        print(f"Expression not found: {expression}")
        return False
    
    expr_data = expressions[expression]
    
    for sk_name, value in expr_data.items():
        if sk_name in obj.data.shape_keys.key_blocks:
            sk = obj.data.shape_keys.key_blocks[sk_name]
            
            # Frame 1: 0
            sk.value = 0
            sk.keyframe_insert("value", frame=1)
            
            # Frame mid: target
            sk.value = value
            sk.keyframe_insert("value", frame=frames // 2)
            
            # Frame end: 0
            sk.value = 0
            sk.keyframe_insert("value", frame=frames)
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    
    print(f"Facial animation: {expression}, {frames} frames")
    return True


# ═══════════════════════════════════════════════════════════════
# GESTURE LIBRARY
# ═══════════════════════════════════════════════════════════════

GESTURE_PRESETS = {
    "wave": {"description": "Saludo", "bones": ["UpperArm_R"]},
    "point": {"description": "Señalar", "bones": ["UpperArm_R", "LowerArm_R"]},
    "clap": {"description": "Aplaudir", "bones": ["UpperArm_L", "UpperArm_R"]},
    "shrug": {"description": "Encogerse", "bones": ["UpperArm_L", "UpperArm_R"]},
    "nod": {"description": "Asentir", "bones": ["Head"]},
    "shake_head": {"description": "Negar", "bones": ["Head"]},
}


def gesture_library(arm_obj, gesture_name="wave", frames=30):
    """
    Aplicar gesto de la librería.
    """
    if bpy is None or arm_obj is None:
        return False
    
    if gesture_name not in GESTURE_PRESETS:
        print(f"Gesture not found: {gesture_name}")
        return False
    
    preset = GESTURE_PRESETS[gesture_name]
    
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    # Animar huesos del gesto
    for bone_name in preset["bones"]:
        bone = arm_obj.pose.bones.get(bone_name)
        if bone:
            bone.rotation_mode = 'XYZ'
            
            if gesture_name == "wave":
                bone.rotation_euler = (0, 0, 0)
                bone.keyframe_insert("rotation_euler", frame=1)
                bone.rotation_euler = (0, 0, math.radians(-120))
                bone.keyframe_insert("rotation_euler", frame=10)
                bone.rotation_euler = (0, 0, math.radians(-120))
                bone.keyframe_insert("rotation_euler", frame=20)
                bone.rotation_euler = (0, 0, 0)
                bone.keyframe_insert("rotation_euler", frame=30)
            
            elif gesture_name == "nod":
                bone.rotation_euler = (0, 0, 0)
                bone.keyframe_insert("rotation_euler", frame=1)
                bone.rotation_euler = (math.radians(15), 0, 0)
                bone.keyframe_insert("rotation_euler", frame=15)
                bone.rotation_euler = (0, 0, 0)
                bone.keyframe_insert("rotation_euler", frame=30)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    
    print(f"Gesture: {gesture_name}, {frames} frames")
    return True


# ═══════════════════════════════════════════════════════════════
# PROCEDURAL ANIMATION
# ═══════════════════════════════════════════════════════════════

def procedural_animation(obj, animation_type="orbit", frames=60, params=None):
    """
    Crear animación procedural.
    
    Args:
        obj: Objeto a animar
        animation_type: 'orbit', 'bounce', 'spin', 'wave', 'float'
        frames: Duración
        params: Parámetros adicionales
    """
    if bpy is None or obj is None:
        return False
    
    if params is None:
        params = {}
    
    keyframes = []
    
    if animation_type == "orbit":
        radius = params.get("radius", 2)
        for i in range(frames + 1):
            t = i / frames
            angle = t * math.pi * 2
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            keyframes.append((i, (x, y, 0)))
    
    elif animation_type == "bounce":
        height = params.get("height", 2)
        for i in range(frames + 1):
            t = i / frames
            z = height * math.sin(t * math.pi)
            keyframes.append((i, (0, 0, z)))
    
    elif animation_type == "spin":
        speed = params.get("speed", 1)
        for i in range(frames + 1):
            t = i / frames
            rot = (0, 0, t * math.pi * 2 * speed)
            obj.rotation_euler = rot
            obj.keyframe_insert("rotation_euler", frame=i)
        return True
    
    elif animation_type == "wave":
        amplitude = params.get("amplitude", 0.5)
        for i in range(frames + 1):
            t = i / frames
            x = amplitude * math.sin(t * math.pi * 4)
            keyframes.append((i, (x, 0, 0)))
    
    elif animation_type == "float":
        amplitude = params.get("amplitude", 0.1)
        for i in range(frames + 1):
            t = i / frames
            z = amplitude * math.sin(t * math.pi * 2)
            keyframes.append((i, (0, 0, z)))
    
    for frame, loc in keyframes:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    
    print(f"Procedural animation: {animation_type}, {frames} frames")
    return True


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_animation_types():
    """Listar tipos de animación disponibles"""
    return {
        "walk": "Walk cycle procedural",
        "run": "Run cycle procedural",
        "orbit": "Animación orbital",
        "bounce": "Rebote",
        "spin": "Rotación continua",
        "wave": "Onda sinusoidal",
        "float": "Flotar",
    }


def list_gestures():
    """Listar gestos disponibles"""
    return {k: v["description"] for k, v in GESTURE_PRESETS.items()}


# ═══════════════════════════════════════════════════════════════
# FACIAL EXPRESSIONS EXTENDED
# ═══════════════════════════════════════════════════════════════

EXTENDED_EXPRESSIONS = {
    "disgust": {"Nose_Scrunch": 0.8, "Mouth_Open": 0.3, "Brow_Down_L": 0.4, "Brow_Down_R": 0.4},
    "fear": {"Brow_Up_L": 0.9, "Brow_Up_R": 0.9, "Mouth_Open": 0.5, "Eye_Wide_L": 0.8, "Eye_Wide_R": 0.8},
    "contempt": {"Smile_L": 0.3, "Brow_Down_L": 0.3},
    "pain": {"Brow_Down_L": 0.7, "Brow_Down_R": 0.7, "Mouth_Open": 0.4, "Nose_Scrunch": 0.5},
    "thinking": {"Brow_Up_L": 0.3, "Eye_Up_L": 0.5},
    "wink": {"Blink_R": 1.0},
}


def facial_expression_extended(obj, expression, frames=30):
    """
    Crear expresión facial extendida.
    """
    if bpy is None or obj is None:
        return False
    
    if not obj.data.shape_keys:
        print("No shape keys found")
        return False
    
    # Combinar expresiones básicas y extendidas
    all_expressions = {
        "neutral": {},
        "smile": {"Mouth_Open": 0.3, "Smile_L": 0.8, "Smile_R": 0.8},
        "frown": {"Mouth_Open": 0.2, "Frown_L": 0.8, "Frown_R": 0.8},
        "surprise": {"Mouth_Open": 0.8, "Brow_Up_L": 0.9, "Brow_Up_R": 0.9},
        "angry": {"Brow_Down_L": 0.9, "Brow_Down_R": 0.9, "Jaw_Open": 0.3},
        "sad": {"Brow_Down_L": 0.5, "Brow_Down_R": 0.5, "Mouth_Open": 0.1},
    }
    all_expressions.update(EXTENDED_EXPRESSIONS)
    
    if expression not in all_expressions:
        print(f"Expression not found: {expression}")
        return False
    
    expr_data = all_expressions[expression]
    
    for sk_name, value in expr_data.items():
        if sk_name in obj.data.shape_keys.key_blocks:
            sk = obj.data.shape_keys.key_blocks[sk_name]
            sk.value = 0
            sk.keyframe_insert("value", frame=1)
            sk.value = value
            sk.keyframe_insert("value", frame=frames // 2)
            sk.value = 0
            sk.keyframe_insert("value", frame=frames)
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    
    print(f"Facial expression: {expression}, {frames} frames")
    return True


# ═══════════════════════════════════════════════════════════════
# LIP SYNC
# ═══════════════════════════════════════════════════════════════

def lip_sync(obj, text, frames_per_char=2):
    """
    Crear lip sync básico desde texto.
    
    Args:
        obj: Objeto con shape keys
        text: Texto a sincronizar
        frames_per_char: Frames por carácter
    """
    if bpy is None or obj is None:
        return False
    
    if not obj.data.shape_keys:
        print("No shape keys found")
        return False
    
    # Fonemas básicos
    phonemes = {
        "a": "Mouth_Open",
        "e": "Smile_L",
        "i": "Mouth_Open",
        "o": "Mouth_Open",
        "u": "Mouth_Open",
        "m": "Mouth_Close",
        "b": "Mouth_Close",
        "p": "Mouth_Close",
    }
    
    current_frame = 1
    for char in text.lower():
        if char in phonemes:
            sk_name = phonemes[char]
            if sk_name in obj.data.shape_keys.key_blocks:
                sk = obj.data.shape_keys.key_blocks[sk_name]
                sk.value = 0.5
                sk.keyframe_insert("value", frame=current_frame)
                sk.value = 0
                sk.keyframe_insert("value", frame=current_frame + frames_per_char)
        current_frame += frames_per_char
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = current_frame
    
    print(f"Lip sync: {len(text)} characters, {current_frame} frames")
    return True


# ═══════════════════════════════════════════════════════════════
# EYE TRACKING
# ═══════════════════════════════════════════════════════════════

def eye_tracking(obj, target_obj, frames=60):
    """
    Crear eye tracking (ojos miran a un objeto).
    
    Args:
        obj: Objeto con ojos
        target_obj: Objeto a mirar
        frames: Duración
    """
    if bpy is None or obj is None or target_obj is None:
        return False
    
    # Crear空.Empty como target
    bpy.ops.object.empty_add(location=target_obj.location)
    empty = bpy.context.active_object
    empty.name = f"{obj.name}_EyeTarget"
    
    # Agregar constraint a ojos
    for side in ["L", "R"]:
        eye_name = f"Eye_{side}"
        if eye_name in [o.name for o in bpy.data.objects]:
            eye = bpy.data.objects.get(eye_name)
            constraint = eye.constraints.new('TRACK_TO')
            constraint.target = empty
            constraint.track_axis = 'TRACK_Z'
            constraint.up_axis = 'UP_Y'
    
    print(f"Eye tracking: {obj.name} → {target_obj.name}")
    return True


# ═══════════════════════════════════════════════════════════════
# HEAD MOVEMENT
# ═══════════════════════════════════════════════════════════════

def head_movement(obj, movement_type="nod", frames=30):
    """
    Crear movimiento de cabeza.
    
    Args:
        obj: Objeto (cabeza o armature)
        movement_type: 'nod', 'shake', 'tilt', 'look_around'
        frames: Duración
    """
    if bpy is None or obj is None:
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='POSE')
    
    bone = obj.pose.bones.get("Head") if obj.type == 'ARMATURE' else None
    
    if bone:
        bone.rotation_mode = 'XYZ'
        
        if movement_type == "nod":
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert("rotation_euler", frame=1)
            bone.rotation_euler = (math.radians(15), 0, 0)
            bone.keyframe_insert("rotation_euler", frame=15)
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert("rotation_euler", frame=30)
        
        elif movement_type == "shake":
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert("rotation_euler", frame=1)
            bone.rotation_euler = (0, math.radians(20), 0)
            bone.keyframe_insert("rotation_euler", frame=10)
            bone.rotation_euler = (0, math.radians(-20), 0)
            bone.keyframe_insert("rotation_euler", frame=20)
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert("rotation_euler", frame=30)
        
        elif movement_type == "tilt":
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert("rotation_euler", frame=1)
            bone.rotation_euler = (0, 0, math.radians(20))
            bone.keyframe_insert("rotation_euler", frame=15)
            bone.rotation_euler = (0, 0, -math.radians(20))
            bone.keyframe_insert("rotation_euler", frame=30)
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert("rotation_euler", frame=45)
        
        elif movement_type == "look_around":
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert("rotation_euler", frame=1)
            bone.rotation_euler = (0, math.radians(30), 0)
            bone.keyframe_insert("rotation_euler", frame=15)
            bone.rotation_euler = (math.radians(15), 0, 0)
            bone.keyframe_insert("rotation_euler", frame=30)
            bone.rotation_euler = (0, math.radians(-30), 0)
            bone.keyframe_insert("rotation_euler", frame=45)
            bone.rotation_euler = (0, 0, 0)
            bone.keyframe_insert("rotation_euler", frame=60)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    
    print(f"Head movement: {movement_type}, {frames} frames")
    return True


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_facial_expressions():
    """Listar expresiones faciales disponibles"""
    all_expr = {
        "neutral": "Neutral",
        "smile": "Sonrisa",
        "frown": "Ceño fruncido",
        "surprise": "Sorpresa",
        "angry": "Enojo",
        "sad": "Tristeza",
    }
    all_expr.update({k: v for k, v in EXTENDED_EXPRESSIONS.items()})
    return all_expr


def list_head_movements():
    """Listar movimientos de cabeza"""
    return {
        "nod": "Asentir",
        "shake": "Negar",
        "tilt": "Inclinar",
        "look_around": "Mirar alrededor",
    }
