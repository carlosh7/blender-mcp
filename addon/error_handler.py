"""
blender-mcp — Error Handler
Manejo de errores: rollback, retry, fallback, error boundaries.

Regla de oro: NUNCA dejar la escena en estado inconsistente.
"""

import time
from datetime import datetime

import bpy

# ═══════════════════════════════════════════════════════════════
# ESTADO DE ERRORES
# ═══════════════════════════════════════════════════════════════

_error_log = []
_rollback_points = []


# ═══════════════════════════════════════════════════════════════
# ROLLBACK SYSTEM
# ═══════════════════════════════════════════════════════════════


def create_rollback_point(label=None):
    """
    Crear un punto de rollback (snapshot del estado actual).

    Args:
        label: Etiqueta para identificar el punto

    Returns:
        dict con el punto de rollback creado
    """
    point = {
        "label": label or f"point_{len(_rollback_points)}",
        "timestamp": datetime.now().isoformat(),
        "objects": [obj.name for obj in bpy.data.objects],
        "materials": [mat.name for mat in bpy.data.materials],
        "collections": [col.name for col in bpy.data.collections],
    }

    _rollback_points.append(point)

    print(f"[error_handler] Rollback point creado: {point['label']}")
    return point


def rollback(point_index=-1):
    """
    Restaurar el estado desde un punto de rollback.

    Args:
        point_index: Índice del punto a restaurar (-1 = último)

    Returns:
        dict con el resultado del rollback
    """
    if not _rollback_points:
        return {"success": False, "error": "No hay puntos de rollback"}

    point = _rollback_points[point_index]

    print(f"[error_handler] Restaurando desde: {point['label']}")

    # Identificar objetos que se agregaron después del punto
    current_objects = set(obj.name for obj in bpy.data.objects)
    point_objects = set(point["objects"])

    objects_to_remove = current_objects - point_objects

    # Eliminar objetos agregados
    for obj_name in objects_to_remove:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
            print(f"  Eliminado: {obj_name}")

    # Identificar materiales que se agregaron
    current_materials = set(mat.name for mat in bpy.data.materials)
    point_materials = set(point["materials"])

    materials_to_remove = current_materials - point_materials

    # Eliminar materiales agregados
    for mat_name in materials_to_remove:
        mat = bpy.data.materials.get(mat_name)
        if mat:
            bpy.data.materials.remove(mat)
            print(f"  Material eliminado: {mat_name}")

    print(
        f"[error_handler] Rollback completado: {len(objects_to_remove)} objetos, {len(materials_to_remove)} materiales eliminados"
    )

    return {
        "success": True,
        "objects_removed": list(objects_to_remove),
        "materials_removed": list(materials_to_remove),
    }


def clear_rollback_points():
    """Limpiar todos los puntos de rollback."""
    _rollback_points.clear()
    print("[error_handler] Puntos de rollback limpiados")


# ═══════════════════════════════════════════════════════════════
# RETRY SYSTEM
# ═══════════════════════════════════════════════════════════════


def retry(func, max_attempts=3, delay=1.0, backoff=2.0):
    """
    Ejecutar una función con reintentos automáticos.

    Args:
        func: Función a ejecutar (callable)
        max_attempts: Número máximo de intentos
        delay: Tiempo inicial entre reintentos (segundos)
        backoff: Factor de multiplicación del delay

    Returns:
        Resultado de la función o último error
    """
    last_error = None
    current_delay = delay

    for attempt in range(max_attempts):
        try:
            result = func()
            if attempt > 0:
                print(f"[error_handler] Éxito en intento {attempt + 1}/{max_attempts}")
            return result
        except Exception as e:
            last_error = e
            print(f"[error_handler] Intento {attempt + 1}/{max_attempts} falló: {e}")

            if attempt < max_attempts - 1:
                print(f"[error_handler] Reintentando en {current_delay:.1f}s...")
                time.sleep(current_delay)
                current_delay *= backoff

    # Todos los intentos fallaron
    error_entry = {
        "function": func.__name__ if hasattr(func, "__name__") else str(func),
        "error": str(last_error),
        "attempts": max_attempts,
        "timestamp": datetime.now().isoformat(),
    }
    _error_log.append(error_entry)

    raise last_error


def retry_with_fallback(primary_func, fallback_func, max_attempts=2):
    """
    Ejecutar función primaria con fallback.

    Args:
        primary_func: Función principal a intentar
        fallback_func: Función de respaldo si la principal falla

    Returns:
        Resultado de cualquiera de las dos funciones
    """
    try:
        return retry(primary_func, max_attempts=max_attempts)
    except Exception as primary_error:
        print(f"[error_handler] Función primaria falló: {primary_error}")
        print("[error_handler] Ejecutando fallback...")

        try:
            return fallback_func()
        except Exception as fallback_error:
            print(f"[error_handler] Fallback también falló: {fallback_error}")

            error_entry = {
                "primary_error": str(primary_error),
                "fallback_error": str(fallback_error),
                "timestamp": datetime.now().isoformat(),
            }
            _error_log.append(error_entry)

            raise fallback_error


# ═══════════════════════════════════════════════════════════════
# ERROR BOUNDARIES
# ═══════════════════════════════════════════════════════════════


def safe_execute(func, default=None, log_error=True):
    """
    Ejecutar función de forma segura (no lanza excepciones).

    Args:
        func: Función a ejecutar
        default: Valor por defecto si falla
        log_error: Si se debe registrar el error

    Returns:
        Resultado de la función o valor por defecto
    """
    try:
        return func()
    except Exception as e:
        if log_error:
            error_entry = {
                "function": func.__name__ if hasattr(func, "__name__") else str(func),
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            _error_log.append(error_entry)
            print(f"[error_handler] Error capturado: {e}")

        return default


def with_error_handling(func, operation_name="operation"):
    """
    Ejecutar función con manejo de errores completo.

    Args:
        func: Función a ejecutar
        operation_name: Nombre de la operación para logging

    Returns:
        dict con {success: bool, result: any, error: str}
    """
    print(f"[error_handler] Iniciando: {operation_name}")

    try:
        result = func()
        print(f"[error_handler] Completado: {operation_name}")
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        error_entry = {
            "operation": operation_name,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
        _error_log.append(error_entry)

        print(f"[error_handler] Error en {operation_name}: {e}")

        return {"success": False, "result": None, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# FALLBACK STRATEGIES
# ═══════════════════════════════════════════════════════════════


def create_with_fallback(object_type, position, collection=None):
    """
    Crear objeto con estrategia de fallback.

    Si la creación completa falla, intenta una versión simplificada.
    """
    import creation_rules

    # Intento 1: Creación completa
    try:
        return creation_rules.create_object(object_type, position, collection)
    except Exception as e:
        print(f"[error_handler] Creación completa falló: {e}")

    # Intento 2: Creación simplificada (sin material, sin conexión)
    try:
        print("[error_handler] Intentando creación simplificada...")
        # Crear solo la pieza principal
        if object_type in creation_rules.STANDARD_OBJECTS:
            config = creation_rules.STANDARD_OBJECTS[object_type]
            # Determinar primitiva principal
            if "seat" in config:
                params = {"size": 1, "location": position}
                primitive = "cube"
            elif "body" in config:
                params = {
                    "radius": config["body"]["r"],
                    "depth": config["body"]["h"],
                    "location": position,
                }
                primitive = "cylinder"
            else:
                params = {"size": 1, "location": position}
                primitive = "cube"

            return creation_rules.create_part(
                f"{object_type}_fallback", primitive, params, collection or object_type
            )
    except Exception as e2:
        print(f"[error_handler] Creación simplificada también falló: {e2}")

    # Intento 3: Crear primitiva básica
    try:
        print("[error_handler] Creando primitiva básica...")
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=position)
        obj = bpy.context.active_object
        obj.name = f"{object_type}_basic"
        return {obj.name: obj}
    except Exception as e3:
        print(f"[error_handler] Todos los intentos fallaron: {e3}")
        return None


# ═══════════════════════════════════════════════════════════════
# LOG Y REPORTE
# ═══════════════════════════════════════════════════════════════


def get_error_log(limit=20):
    """Obtener las últimas N entradas del log de errores."""
    return _error_log[-limit:]


def print_error_log():
    """Imprimir el log de errores."""
    print("\n" + "=" * 60)
    print("LOG DE ERRORES")
    print("=" * 60)

    if not _error_log:
        print("✅ Sin errores registrados")
    else:
        for i, entry in enumerate(_error_log[-10:], 1):
            print(f"\n{i}. {entry.get('timestamp', 'N/A')}")
            if "operation" in entry:
                print(f"   Operación: {entry['operation']}")
            if "function" in entry:
                print(f"   Función: {entry['function']}")
            print(f"   Error: {entry.get('error', 'N/A')}")

    print("=" * 60)


def clear_error_log():
    """Limpiar el log de errores."""
    _error_log.clear()
    print("[error_handler] Log de errores limpiado")


def get_error_stats():
    """Obtener estadísticas de errores."""
    total = len(_error_log)

    # Agrupar por tipo de error
    error_types = {}
    for entry in _error_log:
        error_msg = entry.get("error", "unknown")
        # Extraer tipo de error
        if ":" in error_msg:
            error_type = error_msg.split(":")[0]
        else:
            error_type = error_msg[:50]

        error_types[error_type] = error_types.get(error_type, 0) + 1

    return {
        "total_errors": total,
        "error_types": error_types,
        "most_common": max(error_types.items(), key=lambda x: x[1]) if error_types else None,
    }
