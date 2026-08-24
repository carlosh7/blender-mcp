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

# ═══════════════════════════════════════════════════════════════
# 27 ANCHOR POINTS DEFINITION
# ═══════════════════════════════════════════════════════════════

ANCHOR_NAMES = [
    # 8 Corners
    "FRONT_BOTTOM_LEFT",
    "FRONT_BOTTOM_RIGHT",
    "FRONT_TOP_LEFT",
    "FRONT_TOP_RIGHT",
    "BACK_BOTTOM_LEFT",
    "BACK_BOTTOM_RIGHT",
    "BACK_TOP_LEFT",
    "BACK_TOP_RIGHT",
    # 12 Edge Centers
    "FRONT_BOTTOM_CENTER",
    "FRONT_TOP_CENTER",
    "BACK_BOTTOM_CENTER",
    "BACK_TOP_CENTER",
    "LEFT_BOTTOM_CENTER",
    "LEFT_TOP_CENTER",
    "RIGHT_BOTTOM_CENTER",
    "RIGHT_TOP_CENTER",
    "FRONT_LEFT_CENTER",
    "FRONT_RIGHT_CENTER",
    "BACK_LEFT_CENTER",
    "BACK_RIGHT_CENTER",
    # 6 Face Centers
    "FRONT_CENTER",
    "BACK_CENTER",
    "LEFT_CENTER",
    "RIGHT_CENTER",
    "TOP_CENTER",
    "BOTTOM_CENTER",
    # 1 Centroid
    "CENTROID",
]


def get_bbox_anchors(obj: bpy.types.Object) -> dict[str, Vector]:
    """
    Obtener 27 puntos de anclaje de un objeto.

    Args:
        obj: Objeto Blender

    Returns:
        Dict con nombre → Vector position (en world space)
    """
    # Derive min/max per axis from bound_box corners (robust to index order)
    corners = [Vector(corner) for corner in obj.bound_box]
    mn = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    mx = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))

    # X: BACK(-) / FRONT(+) · Y: LEFT(-) / RIGHT(+) · Z: BOTTOM(-) / TOP(+)
    front, back = mx.x, mn.x
    right, left = mx.y, mn.y
    top, bottom = mx.z, mn.z
    center_x, center_y, center_z = (mn.x + mx.x) / 2, (mn.y + mx.y) / 2, (mn.z + mx.z) / 2

    anchors = {
        # 8 Corners
        "FRONT_BOTTOM_LEFT": Vector((front, left, bottom)),
        "FRONT_BOTTOM_RIGHT": Vector((front, right, bottom)),
        "FRONT_TOP_LEFT": Vector((front, left, top)),
        "FRONT_TOP_RIGHT": Vector((front, right, top)),
        "BACK_BOTTOM_LEFT": Vector((back, left, bottom)),
        "BACK_BOTTOM_RIGHT": Vector((back, right, bottom)),
        "BACK_TOP_LEFT": Vector((back, left, top)),
        "BACK_TOP_RIGHT": Vector((back, right, top)),
        # 12 Edge Centers
        "FRONT_BOTTOM_CENTER": Vector((front, center_y, bottom)),
        "FRONT_TOP_CENTER": Vector((front, center_y, top)),
        "BACK_BOTTOM_CENTER": Vector((back, center_y, bottom)),
        "BACK_TOP_CENTER": Vector((back, center_y, top)),
        "LEFT_BOTTOM_CENTER": Vector((center_x, left, bottom)),
        "LEFT_TOP_CENTER": Vector((center_x, left, top)),
        "RIGHT_BOTTOM_CENTER": Vector((center_x, right, bottom)),
        "RIGHT_TOP_CENTER": Vector((center_x, right, top)),
        "FRONT_LEFT_CENTER": Vector((front, left, center_z)),
        "FRONT_RIGHT_CENTER": Vector((front, right, center_z)),
        "BACK_LEFT_CENTER": Vector((back, left, center_z)),
        "BACK_RIGHT_CENTER": Vector((back, right, center_z)),
        # 6 Face Centers
        "FRONT_CENTER": Vector((front, center_y, center_z)),
        "BACK_CENTER": Vector((back, center_y, center_z)),
        "LEFT_CENTER": Vector((center_x, left, center_z)),
        "RIGHT_CENTER": Vector((center_x, right, center_z)),
        "TOP_CENTER": Vector((center_x, center_y, top)),
        "BOTTOM_CENTER": Vector((center_x, center_y, bottom)),
        # 1 Centroid
        "CENTROID": Vector((center_x, center_y, center_z)),
    }

    # Transform to world space
    matrix = obj.matrix_world
    world_anchors = {name: matrix @ pos for name, pos in anchors.items()}

    return world_anchors


def get_closest_anchor(obj: bpy.types.Object, target_pos: Vector) -> tuple[str, Vector]:
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
    closest_dist = float("inf")
    closest_pos = None

    for name, pos in anchors.items():
        dist = (pos - target_pos).length
        if dist < closest_dist:
            closest_dist = dist
            closest_name = name
            closest_pos = pos

    return closest_name, closest_pos


def snap_to_anchor(
    obj_move: bpy.types.Object, obj_target: bpy.types.Object, anchor_move: str, anchor_target: str
) -> bool:
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


def snap_and_parent(
    obj_move: bpy.types.Object, obj_target: bpy.types.Object, anchor_move: str, anchor_target: str
) -> bool:
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


def get_assembly_plan(objects: list[bpy.types.Object]) -> list[dict]:
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
        best_dist = float("inf")

        for name_b, pos_b in anchors_below.items():
            if "TOP" in name_b or "CENTROID" == name_b:
                for name_a, pos_a in anchors_above.items():
                    if "BOTTOM" in name_a or "CENTROID" == name_a:
                        dist = (pos_b - pos_a).length
                        if dist < best_dist:
                            best_dist = dist
                            best_pair = (name_b, name_a)

        if best_pair:
            plan.append(
                {
                    "step": i + 1,
                    "object_below": obj_below.name,
                    "object_above": obj_above.name,
                    "anchor_below": best_pair[0],
                    "anchor_above": best_pair[1],
                    "distance": round(best_dist, 4),
                }
            )

    return plan


# ═══════════════════════════════════════════════════════════════
# ANCHOR VISUALIZATION
# ═══════════════════════════════════════════════════════════════


def create_anchor_empty(
    obj: bpy.types.Object, anchor_name: str, size: float = 0.02
) -> bpy.types.Object | None:
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
        empty.empty_display_type = "PLAIN_AXES"
        empty.empty_display_size = size
        empty.location = pos

        bpy.context.collection.objects.link(empty)

        # Parent to object
        empty.parent = obj

        return empty

    except Exception as e:
        print(f"[anchor] Error creating empty: {e}")
        return None


def visualize_all_anchors(obj: bpy.types.Object, size: float = 0.02) -> list[bpy.types.Object]:
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
