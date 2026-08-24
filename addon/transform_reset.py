"""
blender-mcp — Auto-Transform Reset
Reseteo automático de escala y origen después de operaciones.

Problema: Escalas no aplicadas causan desfases al unir piezas.
Solución: Aplicar transformaciones automáticamente.
"""

import bpy
from mathutils import Vector

# ═══════════════════════════════════════════════════════════════
# TRANSFORM RESET
# ═══════════════════════════════════════════════════════════════


def reset_scale(obj: bpy.types.Object) -> bool:
    """
    Resetear escala de un objeto a (1,1,1).

    Args:
        obj: Objeto a resetear

    Returns:
        True si éxito
    """
    try:
        # Store original scale for logging
        orig_scale = obj.scale.copy()

        # Apply scale
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(rotation=False, scale=True, location=False)

        print(f"[transform] Scale applied: {obj.name} {list(orig_scale)} → (1,1,1)")
        return True

    except Exception as e:
        print(f"[transform] Error resetting scale: {e}")
        return False


def reset_rotation(obj: bpy.types.Object) -> bool:
    """
    Resetear rotación de un objeto a (0,0,0).

    Args:
        obj: Objeto a resetear

    Returns:
        True si éxito
    """
    try:
        orig_rotation = obj.rotation_euler.copy()

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(rotation=True, scale=False, location=False)

        print(f"[transform] Rotation applied: {obj.name} {list(orig_rotation)} → (0,0,0)")
        return True

    except Exception as e:
        print(f"[transform] Error resetting rotation: {e}")
        return False


def reset_location(obj: bpy.types.Object) -> bool:
    """
    Resetear ubicación de un objeto a (0,0,0).

    Args:
        obj: Objeto a resetear

    Returns:
        True si éxito
    """
    try:
        orig_location = obj.location.copy()

        obj.location = (0, 0, 0)

        print(f"[transform] Location reset: {obj.name} {list(orig_location)} → (0,0,0)")
        return True

    except Exception as e:
        print(f"[transform] Error resetting location: {e}")
        return False


def reset_all_transforms(obj: bpy.types.Object) -> dict[str, bool]:
    """
    Resetear todas las transformaciones de un objeto.

    Args:
        obj: Objeto a resetear

    Returns:
        Dict con resultado de cada operación
    """
    return {
        "scale": reset_scale(obj),
        "rotation": reset_rotation(obj),
        "location": reset_location(obj),
    }


def apply_all_transforms(obj: bpy.types.Object) -> bool:
    """
    Aplicar todas las transformaciones (location, rotation, scale).

    Args:
        obj: Objeto a transformar

    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        print(f"[transform] All transforms applied: {obj.name}")
        return True

    except Exception as e:
        print(f"[transform] Error applying transforms: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# ORIGIN RESET
# ═══════════════════════════════════════════════════════════════


def set_origin_to_geometry(obj: bpy.types.Object) -> bool:
    """
    Centrar origen en la geometría.

    Args:
        obj: Objeto a modificar

    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

        print(f"[transform] Origin set to geometry: {obj.name}")
        return True

    except Exception as e:
        print(f"[transform] Error setting origin: {e}")
        return False


def set_origin_to_bottom(obj: bpy.types.Object) -> bool:
    """
    Centrar origen en la parte inferior del objeto.

    Args:
        obj: Objeto a modificar

    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Get bounding box bottom center
        bbox = [Vector(corner) for corner in obj.bound_box]
        bottom_center = sum(bbox, Vector()) / 8
        bottom_center.z = min(b.z for b in bbox)

        # Set 3D cursor to bottom center
        bpy.context.scene.cursor.location = obj.matrix_world @ bottom_center

        # Set origin to 3D cursor
        bpy.ops.object.origin_set(type="ORIGIN_3D_CURSOR", center="MEDIAN")

        print(f"[transform] Origin set to bottom: {obj.name}")
        return True

    except Exception as e:
        print(f"[transform] Error setting origin to bottom: {e}")
        return False


def set_origin_to_center(obj: bpy.types.Object) -> bool:
    """
    Centrar origen en el centro del objeto.

    Args:
        obj: Objeto a modificar

    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Get bounding box center
        bbox = [Vector(corner) for corner in obj.bound_box]
        center = sum(bbox, Vector()) / 8

        # Set 3D cursor to center
        bpy.context.scene.cursor.location = obj.matrix_world @ center

        # Set origin to 3D cursor
        bpy.ops.object.origin_set(type="ORIGIN_3D_CURSOR", center="MEDIAN")

        print(f"[transform] Origin set to center: {obj.name}")
        return True

    except Exception as e:
        print(f"[transform] Error setting origin to center: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# BATCH OPERATIONS
# ═══════════════════════════════════════════════════════════════


def reset_scene_transforms(objects: list[bpy.types.Object] | None = None) -> dict[str, any]:
    """
    Resetear transformaciones de múltiples objetos.

    Args:
        objects: Lista de objetos (None = todos los objetos de la escena)

    Returns:
        Dict con resultados
    """
    if objects is None:
        objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]

    results = {
        "total": len(objects),
        "success": 0,
        "failed": 0,
        "details": [],
    }

    for obj in objects:
        result = reset_all_transforms(obj)
        if all(result.values()):
            results["success"] += 1
        else:
            results["failed"] += 1
        results["details"].append({"object": obj.name, "result": result})

    print(f"[transform] Scene reset: {results['success']}/{results['total']} objects")
    return results


def apply_scene_transforms(objects: list[bpy.types.Object] | None = None) -> dict[str, any]:
    """
    Aplicar transformaciones de múltiples objetos.

    Args:
        objects: Lista de objetos (None = todos los objetos de la escena)

    Returns:
        Dict con resultados
    """
    if objects is None:
        objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]

    results = {
        "total": len(objects),
        "success": 0,
        "failed": 0,
        "details": [],
    }

    for obj in objects:
        success = apply_all_transforms(obj)
        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
        results["details"].append({"object": obj.name, "success": success})

    print(f"[transform] Scene apply: {results['success']}/{results['total']} objects")
    return results


# ═══════════════════════════════════════════════════════════════
# TRANSFORM ANALYSIS
# ═══════════════════════════════════════════════════════════════


def get_transform_status(obj: bpy.types.Object) -> dict[str, any]:
    """
    Obtener estado actual de transformaciones de un objeto.

    Args:
        obj: Objeto a analizar

    Returns:
        Dict con estado de transformaciones
    """
    return {
        "name": obj.name,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "needs_scale_reset": obj.scale != Vector((1, 1, 1)),
        "needs_rotation_reset": obj.rotation_euler != Vector((0, 0, 0)),
        "origin_offset": list(obj.data.vertices[0].co)
        if obj.type == "MESH" and obj.data.vertices
        else None,
    }


def get_scene_transform_report() -> str:
    """
    Generar reporte de transformaciones de la escena.

    Returns:
        String con reporte formateado
    """
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]

    lines = ["=== SCENE TRANSFORM REPORT ==="]

    needs_reset = 0
    for obj in objects:
        status = get_transform_status(obj)
        if status["needs_scale_reset"] or status["needs_rotation_reset"]:
            needs_reset += 1
            issues = []
            if status["needs_scale_reset"]:
                issues.append(f"scale={status['scale']}")
            if status["needs_rotation_reset"]:
                issues.append(f"rotation={status['rotation']}")
            lines.append(f"  ⚠️ {obj.name}: {', '.join(issues)}")

    lines.append(f"\nTotal: {len(objects)} objects, {needs_reset} need reset")
    lines.append("==============================")

    return "\n".join(lines)
