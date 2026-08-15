"""
blender-mcp — 27-Point Anchor System
Sistema de anclaje determinista para unir piezas como LEGO.

Cada objeto tiene 27 puntos de anclaje en su bounding box:
- 8 esquinas (corners)
- 12 aristas (edge centers)
- 6 caras (face centers)
- 1 centro (centroid)

Permite unir piezas con precisión milimétrica.
"""
import bpy
from mathutils import Vector
from typing import Dict, List, Tuple, Optional


# ═══════════════════════════════════════════════════════════════
# 27 ANCHOR POINTS DEFINITION
# ═══════════════════════════════════════════════════════════════

ANCHOR_NAMES = [
    # 8 Corners
    "FRONT_BOTTOM_LEFT", "FRONT_BOTTOM_RIGHT",
    "FRONT_TOP_LEFT", "FRONT_TOP_RIGHT",
    "BACK_BOTTOM_LEFT", "BACK_BOTTOM_RIGHT",
    "BACK_TOP_LEFT", "BACK_TOP_RIGHT",
    
    # 12 Edge Centers
    "FRONT_BOTTOM_CENTER", "FRONT_TOP_CENTER",
    "BACK_BOTTOM_CENTER", "BACK_TOP_CENTER",
    "LEFT_BOTTOM_CENTER", "LEFT_TOP_CENTER",
    "RIGHT_BOTTOM_CENTER", "RIGHT_TOP_CENTER",
    "FRONT_LEFT_CENTER", "FRONT_RIGHT_CENTER",
    "BACK_LEFT_CENTER", "BACK_RIGHT_CENTER",
    
    # 6 Face Centers
    "FRONT_CENTER", "BACK_CENTER",
    "LEFT_CENTER", "RIGHT_CENTER",
    "TOP_CENTER", "BOTTOM_CENTER",
    
    # 1 Centroid
    "CENTROID",
]


def get_bbox_anchors(obj: bpy.types.Object) -> Dict[str, Vector]:
    """
    Obtener 27 puntos de anclaje de un objeto.
    
    Args:
        obj: Objeto Blender
    
    Returns:
        Dict con nombre → Vector position (en world space)
    """
    # Get bounding box corners (local space)
    bbox = [Vector(corner) for corner in obj.bound_box]
    
    # bbox order in Blender:
    # 0: (-x, -y, -z) = FRONT_BOTTOM_LEFT
    # 1: (+x, -y, -z) = FRONT_BOTTOM_RIGHT
    # 2: (+x, +y, -z) = BACK_BOTTOM_RIGHT
    # 3: (-x, +y, -z) = BACK_BOTTOM_LEFT
    # 4: (-x, -y, +z) = FRONT_TOP_LEFT
    # 5: (+x, -y, +z) = FRONT_TOP_RIGHT
    # 6: (+x, +y, +z) = BACK_TOP_RIGHT
    # 7: (-x, +y, +z) = BACK_TOP_LEFT
    
    front_bottom_left = bbox[0]
    front_bottom_right = bbox[1]
    back_bottom_right = bbox[2]
    back_bottom_left = bbox[3]
    front_top_left = bbox[4]
    front_top_right = bbox[5]
    back_top_right = bbox[6]
    back_top_left = bbox[7]
    
    # Calculate midpoints
    def mid(a, b):
        return (a + b) / 2
    
    anchors = {
        # 8 Corners (local space)
        "FRONT_BOTTOM_LEFT": front_bottom_left,
        "FRONT_BOTTOM_RIGHT": front_bottom_right,
        "FRONT_TOP_LEFT": front_top_left,
        "FRONT_TOP_RIGHT": front_top_right,
        "BACK_BOTTOM_LEFT": back_bottom_left,
        "BACK_BOTTOM_RIGHT": back_bottom_right,
        "BACK_TOP_LEFT": back_top_left,
        "BACK_TOP_RIGHT": back_top_right,
        
        # 12 Edge Centers
        "FRONT_BOTTOM_CENTER": mid(front_bottom_left, front_bottom_right),
        "FRONT_TOP_CENTER": mid(front_top_left, front_top_right),
        "BACK_BOTTOM_CENTER": mid(back_bottom_left, back_bottom_right),
        "BACK_TOP_CENTER": mid(back_top_left, back_top_right),
        "LEFT_BOTTOM_CENTER": mid(front_bottom_left, back_bottom_left),
        "LEFT_TOP_CENTER": mid(front_top_left, back_top_left),
        "RIGHT_BOTTOM_CENTER": mid(front_bottom_right, back_bottom_right),
        "RIGHT_TOP_CENTER": mid(front_top_right, back_top_right),
        "FRONT_LEFT_CENTER": mid(front_bottom_left, front_top_left),
        "FRONT_RIGHT_CENTER": mid(front_bottom_right, front_top_right),
        "BACK_LEFT_CENTER": mid(back_bottom_left, back_top_left),
        "BACK_RIGHT_CENTER": mid(back_bottom_right, back_top_right),
        
        # 6 Face Centers
        "FRONT_CENTER": mid(mid(front_bottom_left, front_bottom_right), mid(front_top_left, front_top_right)),
        "BACK_CENTER": mid(mid(back_bottom_left, back_bottom_right), mid(back_top_left, back_top_right)),
        "LEFT_CENTER": mid(mid(front_bottom_left, back_bottom_left), mid(front_top_left, back_top_left)),
        "RIGHT_CENTER": mid(mid(front_bottom_right, back_bottom_right), mid(front_top_right, back_top_right)),
        "TOP_CENTER": mid(mid(front_top_left, front_top_right), mid(back_top_left, back_top_right)),
        "BOTTOM_CENTER": mid(mid(front_bottom_left, front_bottom_right), mid(back_bottom_left, back_bottom_right)),
        
        # 1 Centroid
        "CENTROID": sum(bbox, Vector()) / 8,
    }
    
    # Transform to world space
    matrix = obj.matrix_world
    world_anchors = {name: matrix @ pos for name, pos in anchors.items()}
    
    return world_anchors


def get_closest_anchor(obj: bpy.types.Object, target_pos: Vector) -> Tuple[str, Vector]:
    """
    Obtener el ancla más cercana a una posición objetivo.
    
    Args:
        obj: Objeto Blender
        target_pos: Posición objetivo
    
    Returns:
        Tuple con (nombre_ancla, posición_ancla)
    """
    anchors = get_bbox_anchors(obj)
    
    closest_name = None
    closest_dist = float('inf')
    closest_pos = None
    
    for name, pos in anchors.items():
        dist = (pos - target_pos).length
        if dist < closest_dist:
            closest_dist = dist
            closest_name = name
            closest_pos = pos
    
    return closest_name, closest_pos


def snap_to_anchor(obj_move: bpy.types.Object, obj_target: bpy.types.Object,
                   anchor_move: str, anchor_target: str) -> bool:
    """
    Mover objeto para que un ancla coincida con otra.
    
    Args:
        obj_move: Objeto a mover
        obj_target: Objeto destino
        anchor_move: Nombre del ancla en obj_move
        anchor_target: Nombre del ancla en obj_target
    
    Returns:
        True si éxito, False si error
    """
    try:
        anchors_move = get_bbox_anchors(obj_move)
        anchors_target = get_bbox_anchors(obj_target)
        
        if anchor_move not in anchors_move:
            print(f"[anchor] Ancla '{anchor_move}' no encontrada en {obj_move.name}")
            return False
        
        if anchor_target not in anchors_target:
            print(f"[anchor] Ancla '{anchor_target}' no encontrada en {obj_target.name}")
            return False
        
        pos_move = anchors_move[anchor_move]
        pos_target = anchors_target[anchor_target]
        
        # Calculate offset
        offset = pos_target - pos_move
        
        # Apply offset
        obj_move.location += offset
        
        print(f"[anchor] {obj_move.name}.{anchor_move} → {obj_target.name}.{anchor_target}")
        return True
        
    except Exception as e:
        print(f"[anchor] Error: {e}")
        return False


def snap_and_parent(obj_move: bpy.types.Object, obj_target: bpy.types.Object,
                    anchor_move: str, anchor_target: str) -> bool:
    """
    Mover y parentear objeto.
    
    Args:
        obj_move: Objeto a mover
        obj_target: Objeto destino
        anchor_move: Nombre del ancla en obj_move
        anchor_target: Nombre del ancla en obj_target
    
    Returns:
        True si éxito, False si error
    """
    try:
        # Snap
        success = snap_to_anchor(obj_move, obj_target, anchor_move, anchor_target)
        if not success:
            return False
        
        # Parent
        obj_move.parent = obj_target
        
        print(f"[anchor] Parented: {obj_move.name} → {obj_target.name}")
        return True
        
    except Exception as e:
        print(f"[anchor] Error: {e}")
        return False


def get_assembly_plan(objects: List[bpy.types.Object]) -> List[Dict]:
    """
    Generar plan de ensamblaje para múltiples objetos.
    
    Args:
        objects: Lista de objetos a ensamblar
    
    Returns:
        Lista de pasos de ensamblaje
    """
    if len(objects) < 2:
        return []
    
    plan = []
    
    # Sort by Z position (bottom to top)
    sorted_objects = sorted(objects, key=lambda o: o.location.z)
    
    for i in range(len(sorted_objects) - 1):
        obj_below = sorted_objects[i]
        obj_above = sorted_objects[i + 1]
        
        # Get top anchor of bottom object
        anchors_below = get_bbox_anchors(obj_below)
        anchors_above = get_bbox_anchors(obj_above)
        
        # Find best pairing
        best_pair = None
        best_dist = float('inf')
        
        for name_b, pos_b in anchors_below.items():
            if "TOP" in name_b or "CENTROID" == name_b:
                for name_a, pos_a in anchors_above.items():
                    if "BOTTOM" in name_a or "CENTROID" == name_a:
                        dist = (pos_b - pos_a).length
                        if dist < best_dist:
                            best_dist = dist
                            best_pair = (name_b, name_a)
        
        if best_pair:
            plan.append({
                "step": i + 1,
                "object_below": obj_below.name,
                "object_above": obj_above.name,
                "anchor_below": best_pair[0],
                "anchor_above": best_pair[1],
                "distance": round(best_dist, 4),
            })
    
    return plan


# ═══════════════════════════════════════════════════════════════
# ANCHOR VISUALIZATION
# ═══════════════════════════════════════════════════════════════

def create_anchor_empty(obj: bpy.types.Object, anchor_name: str, 
                        size: float = 0.02) -> Optional[bpy.types.Object]:
    """
    Crear empty visual para un ancla.
    
    Args:
        obj: Objeto padre
        anchor_name: Nombre del ancla
        size: Tamaño del empty
    
    Returns:
        Empty creado o None
    """
    try:
        anchors = get_bbox_anchors(obj)
        if anchor_name not in anchors:
            return None
        
        pos = anchors[anchor_name]
        
        # Create empty
        empty = bpy.data.objects.new(f"ANC_{anchor_name}", None)
        empty.empty_display_type = 'PLAIN_AXES'
        empty.empty_display_size = size
        empty.location = pos
        
        bpy.context.collection.objects.link(empty)
        
        # Parent to object
        empty.parent = obj
        
        return empty
        
    except Exception as e:
        print(f"[anchor] Error creating empty: {e}")
        return None


def visualize_all_anchors(obj: bpy.types.Object, size: float = 0.02) -> List[bpy.types.Object]:
    """
    Visualizar todos los anclas de un objeto.
    
    Args:
        obj: Objeto
        size: Tamaño de los empties
    
    Returns:
        Lista de empties creados
    """
    empties = []
    for anchor_name in ANCHOR_NAMES:
        empty = create_anchor_empty(obj, anchor_name, size)
        if empty:
            empties.append(empty)
    
    return empties
