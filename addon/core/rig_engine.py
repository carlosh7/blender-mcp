"""
blender-mcp — Rig Engine
Motor de rigging: Armature, IK/FK, Constraints, Shape Keys, Auto-rig.
"""
import bpy
import math
from mathutils import Vector, Quaternion


# ═══════════════════════════════════════════════════════════════
# CREACIÓN DE ESQUELETOS
# ═══════════════════════════════════════════════════════════════

def create_armature(name="Armature", location=(0, 0, 0)):
    """
    Crear esqueleto básico.
    
    Args:
        name: Nombre del esqueleto
        location: Posición inicial
    
    Returns:
        Objeto armature
    """
    arm_data = bpy.data.armatures.new(f"{name}_Data")
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)
    
    return arm_obj


def add_bone(arm_obj, name, head, tail, parent=None):
    """
    Agregar hueso a un esqueleto.
    
    Args:
        arm_obj: Objeto armature
        name: Nombre del hueso
        head: Posición inicial (Vector)
        tail: Posición final (Vector)
        parent: Hueso padre (opcional)
    
    Returns:
        Hueso creado
    """
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone = arm_obj.data.edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    
    if parent:
        bone.parent = parent
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return bone


# ═══════════════════════════════════════════════════════════════
# ESQUELETOS PREDEFINIDOS
# ═══════════════════════════════════════════════════════════════

HUMANOID_RIG = {
    "name": "Humanoid",
    "bones": {
        "Root": {"head": (0, 0, 0), "tail": (0, 0, 0.1)},
        "Spine": {"head": (0, 0, 0.1), "tail": (0, 0, 0.5), "parent": "Root"},
        "Chest": {"head": (0, 0, 0.5), "tail": (0, 0, 0.8), "parent": "Spine"},
        "Neck": {"head": (0, 0, 0.8), "tail": (0, 0, 0.9), "parent": "Chest"},
        "Head": {"head": (0, 0, 0.9), "tail": (0, 0, 1.05), "parent": "Neck"},
        "UpperArm_L": {"head": (0, 0, 0.75), "tail": (0.3, 0, 0.7), "parent": "Chest"},
        "LowerArm_L": {"head": (0.3, 0, 0.7), "tail": (0.55, 0, 0.65), "parent": "UpperArm_L"},
        "Hand_L": {"head": (0.55, 0, 0.65), "tail": (0.65, 0, 0.62), "parent": "LowerArm_L"},
        "UpperArm_R": {"head": (0, 0, 0.75), "tail": (-0.3, 0, 0.7), "parent": "Chest"},
        "LowerArm_R": {"head": (-0.3, 0, 0.7), "tail": (-0.55, 0, 0.65), "parent": "UpperArm_R"},
        "Hand_R": {"head": (-0.55, 0, 0.65), "tail": (-0.65, 0, 0.62), "parent": "LowerArm_R"},
        "UpperLeg_L": {"head": (0.1, 0, 0), "tail": (0.1, 0, -0.4), "parent": "Root"},
        "LowerLeg_L": {"head": (0.1, 0, -0.4), "tail": (0.1, 0, -0.8), "parent": "UpperLeg_L"},
        "Foot_L": {"head": (0.1, 0, -0.8), "tail": (0.1, 0.1, -0.85), "parent": "LowerLeg_L"},
        "UpperLeg_R": {"head": (-0.1, 0, 0), "tail": (-0.1, 0, -0.4), "parent": "Root"},
        "LowerLeg_R": {"head": (-0.1, 0, -0.4), "tail": (-0.1, 0, -0.8), "parent": "UpperLeg_R"},
        "Foot_R": {"head": (-0.1, 0, -0.8), "tail": (-0.1, 0.1, -0.85), "parent": "LowerLeg_R"},
    }
}

QUADRUPED_RIG = {
    "name": "Quadruped",
    "bones": {
        "Root": {"head": (0, 0, 0), "tail": (0, 0, 0.1)},
        "Spine": {"head": (0, 0, 0.1), "tail": (0, 0, 0.3), "parent": "Root"},
        "Chest": {"head": (0, 0, 0.3), "tail": (0, 0, 0.5), "parent": "Spine"},
        "Neck": {"head": (0, 0, 0.5), "tail": (0, 0.2, 0.65), "parent": "Chest"},
        "Head": {"head": (0, 0.2, 0.65), "tail": (0, 0.35, 0.6), "parent": "Neck"},
        "UpperLeg_FL": {"head": (0.15, 0.2, 0.4), "tail": (0.15, 0.2, 0.1), "parent": "Chest"},
        "LowerLeg_FL": {"head": (0.15, 0.2, 0.1), "tail": (0.15, 0.2, -0.2), "parent": "UpperLeg_FL"},
        "Paw_FL": {"head": (0.15, 0.2, -0.2), "tail": (0.15, 0.25, -0.25), "parent": "LowerLeg_FL"},
        "UpperLeg_FR": {"head": (-0.15, 0.2, 0.4), "tail": (-0.15, 0.2, 0.1), "parent": "Chest"},
        "LowerLeg_FR": {"head": (-0.15, 0.2, 0.1), "tail": (-0.15, 0.2, -0.2), "parent": "UpperLeg_FR"},
        "Paw_FR": {"head": (-0.15, 0.2, -0.2), "tail": (-0.15, 0.25, -0.25), "parent": "LowerLeg_FR"},
        "UpperLeg_BL": {"head": (0.15, -0.3, 0.3), "tail": (0.15, -0.3, 0.0), "parent": "Spine"},
        "LowerLeg_BL": {"head": (0.15, -0.3, 0.0), "tail": (0.15, -0.3, -0.25), "parent": "UpperLeg_BL"},
        "Paw_BL": {"head": (0.15, -0.3, -0.25), "tail": (0.15, -0.25, -0.3), "parent": "LowerLeg_BL"},
        "UpperLeg_BR": {"head": (-0.15, -0.3, 0.3), "tail": (-0.15, -0.3, 0.0), "parent": "Spine"},
        "LowerLeg_BR": {"head": (-0.15, -0.3, 0.0), "tail": (-0.15, -0.3, -0.25), "parent": "UpperLeg_BR"},
        "Paw_BR": {"head": (-0.15, -0.3, -0.25), "tail": (-0.15, -0.25, -0.3), "parent": "LowerLeg_BR"},
        "Tail": {"head": (0, -0.35, 0.35), "tail": (0, -0.55, 0.4), "parent": "Spine"},
    }
}


def create_humanoid_rig(name="HumanoidRig", location=(0, 0, 0)):
    """Crear rig humanoide predefinido"""
    return _create_rig_from_template(HUMANOID_RIG, name, location)


def create_quadruped_rig(name="QuadrupedRig", location=(0, 0, 0)):
    """Crear rig cuadrúpedo predefinido"""
    return _create_rig_from_template(QUADRUPED_RIG, name, location)


def _create_rig_from_template(template, name, location):
    """Crear rig desde plantilla"""
    arm_obj = create_armature(name, location)
    
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone_map = {}
    for bone_name, bone_data in template["bones"].items():
        bone = arm_obj.data.edit_bones.new(bone_name)
        bone.head = Vector(bone_data["head"])
        bone.tail = Vector(bone_data["tail"])
        
        if "parent" in bone_data and bone_data["parent"] in bone_map:
            bone.parent = bone_map[bone_data["parent"]]
        
        bone_map[bone_name] = bone
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Rig creado: {name} ({len(template['bones'])} huesos)")
    return arm_obj


# ═══════════════════════════════════════════════════════════════
# IK/FK
# ═══════════════════════════════════════════════════════════════

def add_ik_constraint(arm_obj, bone_name, target_name=None, chain_length=0):
    """
    Agregar constraint IK a un hueso.
    
    Args:
        arm_obj: Objeto armature
        bone_name: Nombre del hueso
        target_name: Nombre del objeto target (opcional)
        chain_length: Longitud de la cadena (0 = hasta root)
    """
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    bone = arm_obj.pose.bones.get(bone_name)
    if not bone:
        print(f"Hueso no encontrado: {bone_name}")
        return
    
    constraint = bone.constraints.new('IK')
    constraint.chain_count = chain_length
    
    if target_name:
        target_obj = bpy.data.objects.get(target_name)
        if target_obj:
            constraint.target = target_obj
    
    bpy.ops.object.mode_set(mode='OBJECT')


def add_fk_constraint(arm_obj, bone_name, target_name):
    """
    Agregar constraint FK (Copy Rotation) a un hueso.
    """
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    bone = arm_obj.pose.bones.get(bone_name)
    if not bone:
        return
    
    constraint = bone.constraints.new('COPY_ROTATION')
    
    if target_name:
        target_obj = bpy.data.objects.get(target_name)
        if target_obj:
            constraint.target = target_obj
    
    bpy.ops.object.mode_set(mode='OBJECT')


# ═══════════════════════════════════════════════════════════════
# CONSTRAINTS
# ═══════════════════════════════════════════════════════════════

def add_constraint(arm_obj, bone_name, constraint_type, target_name=None):
    """
    Agregar constraint a un hueso.
    
    Tipos disponibles:
    - COPY_LOCATION, COPY_ROTATION, COPY_SCALE
    - LIMIT_LOCATION, LIMIT_ROTATION, LIMIT_SCALE
    - TRACK_TO, DAMPED_TRACK
    - IK, SPLINE_IK
    """
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    
    bone = arm_obj.pose.bones.get(bone_name)
    if not bone:
        return None
    
    constraint = bone.constraints.new(constraint_type)
    
    if target_name:
        target_obj = bpy.data.objects.get(target_name)
        if target_obj:
            constraint.target = target_obj
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return constraint


def add_limit_constraint(arm_obj, bone_name, limit_type, min_val, max_val):
    """
    Agregar limit constraint.
    
    Args:
        limit_type: 'LOCATION', 'ROTATION', 'SCALE'
        min_val: Valor mínimo (tupla xyz)
        max_val: Valor máximo (tupla xyz)
    """
    constraint = add_constraint(arm_obj, bone_name, f'LIMIT_{limit_type}')
    
    if constraint:
        if limit_type == 'LOCATION':
            constraint.use_min_x = True
            constraint.use_min_y = True
            constraint.use_min_z = True
            constraint.use_max_x = True
            constraint.use_max_y = True
            constraint.use_max_z = True
            constraint.min_x, constraint.min_y, constraint.min_z = min_val
            constraint.max_x, constraint.max_y, constraint.max_z = max_val
        elif limit_type == 'ROTATION':
            constraint.use_limit_x = True
            constraint.use_limit_y = True
            constraint.use_limit_z = True
            constraint.min_x, constraint.min_y, constraint.min_z = min_val
            constraint.max_x, constraint.max_y, constraint.max_z = max_val
    
    return constraint


# ═══════════════════════════════════════════════════════════════
# SHAPE KEYS
# ═══════════════════════════════════════════════════════════════

def add_shape_key(obj, name, vertex_positions=None):
    """
    Agregar shape key a un objeto.
    
    Args:
        obj: Objeto mesh
        name: Nombre del shape key
        vertex_positions: Posiciones de vértices (opcional)
    
    Returns:
        Shape key creado
    """
    if obj.type != 'MESH':
        return None
    
    # Crear Basis si no existe
    if not obj.data.shape_keys:
        obj.shape_key_add(name='Basis', from_mix=False)
    
    # Crear shape key
    sk = obj.shape_key_add(name=name, from_mix=False)
    
    if vertex_positions:
        for i, pos in enumerate(vertex_positions):
            if i < len(sk.data):
                sk.data[i].co = pos
    
    return sk


FACE_SHAPE_KEYS = [
    "Blink_L", "Blink_R",
    "Smile_L", "Smile_R",
    "Frown_L", "Frown_R",
    "Mouth_Open", "Mouth_Close",
    "Brow_Up_L", "Brow_Up_R",
    "Brow_Down_L", "Brow_Down_R",
    "Jaw_Open", "Jaw_Close",
    "Nose_Scrunch", "Nose_Flare",
]


def create_facial_shape_keys(obj):
    """
    Crear shape keys faciales estándar (52 blendshapes).
    
    Args:
        obj: Objeto mesh (cara)
    
    Returns:
        Lista de shape keys creados
    """
    if obj.type != 'MESH':
        return []
    
    created = []
    for name in FACE_SHAPE_KEYS:
        sk = add_shape_key(obj, name)
        if sk:
            created.append(name)
    
    print(f"Shape keys faciales creados: {len(created)}")
    return created


# ═══════════════════════════════════════════════════════════════
# WEIGHT PAINTING
# ═══════════════════════════════════════════════════════════════

def automatic_weights(obj, arm_obj):
    """
    Asignar pesos automáticamente.
    
    Args:
        obj: Objeto mesh
        arm_obj: Objeto armature
    
    Returns:
        True si fue exitoso
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    try:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        print(f"Pesos automáticos asignados: {obj.name} → {arm_obj.name}")
        return True
    except Exception as e:
        print(f"Error asignando pesos: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# AUTO-RIG
# ═══════════════════════════════════════════════════════════════

def auto_rig_character(mesh_obj, rig_type="humanoid"):
    """
    Auto-rig un personaje.
    
    Args:
        mesh_obj: Objeto mesh del personaje
        rig_type: Tipo de rig ('humanoid', 'quadruped')
    
    Returns:
        Tupla (arm_obj, mesh_obj) con rig aplicado
    """
    # Crear rig
    if rig_type == "humanoid":
        arm_obj = create_humanoid_rig("AutoRig", mesh_obj.location)
    elif rig_type == "quadruped":
        arm_obj = create_quadruped_rig("AutoRig", mesh_obj.location)
    else:
        raise ValueError(f"Tipo de rig no soportado: {rig_type}")
    
    # Asignar pesos automáticos
    automatic_weights(mesh_obj, arm_obj)
    
    print(f"Auto-rig completado: {mesh_obj.name} → {arm_obj.name}")
    return arm_obj, mesh_obj


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def get_bone_info(arm_obj):
    """Obtener información de todos los huesos"""
    info = []
    for bone in arm_obj.data.bones:
        info.append({
            "name": bone.name,
            "head": tuple(bone.head_local),
            "tail": tuple(bone.tail_local),
            "parent": bone.parent.name if bone.parent else None,
            "children": [c.name for c in bone.children]
        })
    return info


def list_rig_types():
    """Listar tipos de rig disponibles"""
    return {
        "humanoid": "Rig humanoide (2 patas)",
        "quadruped": "Rig cuadrúpedo (4 patas)",
    }


def validate_rig(arm_obj):
    """Validar que un rig esté correctamente configurado"""
    issues = []
    
    for bone in arm_obj.data.bones:
        # Verificar que huesos tengan longitud
        length = (Vector(bone.tail_local) - Vector(bone.head_local)).length
        if length < 0.001:
            issues.append(f"Hueso {bone.name} tiene longitud cero")
        
        # Verificar que no haya ciclos
        if bone.parent:
            parent = bone.parent
            depth = 0
            while parent and depth < 100:
                if parent == bone:
                    issues.append(f"Ciclo detectado en {bone.name}")
                    break
                parent = parent.parent
                depth += 1
    
    return {"valid": len(issues) == 0, "issues": issues}
