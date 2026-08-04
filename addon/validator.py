"""
blender-mcp — Validator
Validación de objetos: dimensiones, conexiones, colisiones, materiales.

Regla de oro: SIEMPRE validar después de crear cada objeto.
"""
import bpy
import math
from mathutils import Vector


# ═══════════════════════════════════════════════════════════════
# VALIDACIÓN DE OBJETOS
# ═══════════════════════════════════════════════════════════════

def validate_object(name, expected_location=None, expected_type=None, 
                    expected_dimensions=None, tolerance=0.01):
    """
    Validar que un objeto existe y cumple con las expectativas.
    
    Args:
        name: Nombre del objeto
        expected_location: Posición esperada (x, y, z) o None
        expected_type: Tipo esperado (MESH, CURVE, etc.) o None
        expected_dimensions: Dimensiones esperadas (w, d, h) o None
        tolerance: Tolerancia para comparaciones
    
    Returns:
        dict con {valid: bool, errors: list, warnings: list}
    """
    errors = []
    warnings = []
    
    # Verificar que existe
    obj = bpy.data.objects.get(name)
    if not obj:
        return {
            "valid": False,
            "errors": [f"Objeto '{name}' no existe"],
            "warnings": [],
        }
    
    # Verificar tipo
    if expected_type and obj.type != expected_type:
        errors.append(f"Tipo esperado: {expected_type}, actual: {obj.type}")
    
    # Verificar ubicación
    if expected_location:
        loc = obj.location
        for i, (actual, expected) in enumerate(zip(loc, expected_location)):
            if abs(actual - expected) > tolerance:
                axis = ['X', 'Y', 'Z'][i]
                errors.append(f"Ubicación {axis}: esperado {expected:.3f}, actual {actual:.3f}")
    
    # Verificar dimensiones
    if expected_dimensions:
        bbox = get_bbox(obj)
        actual_dims = bbox["size"]
        for i, (actual, expected) in enumerate(zip(actual_dims, expected_dimensions)):
            if abs(actual - expected) > tolerance:
                axis = ['Ancho', 'Profundidad', 'Alto'][i]
                warnings.append(f"Dimensión {axis}: esperado {expected:.3f}, actual {actual:.3f}")
    
    # Verificar material
    if obj.type == 'MESH' and not obj.data.materials:
        warnings.append("Sin material asignado")
    
    # Verificar que no está en origen exacto (posible error)
    if obj.location == Vector((0, 0, 0)) and obj.name not in ['Cube', 'Camera', 'Light']:
        warnings.append("Ubicación en origen (0,0,0) - ¿es correcto?")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_all_objects():
    """
    Validar todos los objetos de la escena.
    
    Returns:
        dict con resumen de validación
    """
    results = {}
    
    for obj in bpy.data.objects:
        result = validate_object(obj.name)
        results[obj.name] = result
    
    total = len(results)
    valid = sum(1 for r in results.values() if r["valid"])
    with_errors = sum(1 for r in results.values() if r["errors"])
    with_warnings = sum(1 for r in results.values() if r["warnings"])
    
    return {
        "total": total,
        "valid": valid,
        "with_errors": with_errors,
        "with_warnings": with_warnings,
        "details": results,
    }


# ═══════════════════════════════════════════════════════════════
# BOUNDING BOX
# ═══════════════════════════════════════════════════════════════

def get_bbox(obj):
    """
    Obtener bounding box de un objeto.
    
    Returns:
        dict con min, max, center, size
    """
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = Vector((min(v[i] for v in bbox) for i in range(3)))
    maxs = Vector((max(v[i] for v in bbox) for i in range(3)))
    
    return {
        "min": tuple(mins),
        "max": tuple(maxs),
        "center": tuple((mins + maxs) / 2),
        "size": tuple(maxs - mins),
    }


def measure_object(name):
    """
    Medir un objeto y retornar sus dimensiones.
    
    Returns:
        dict con todas las medidas
    """
    obj = bpy.data.objects.get(name)
    if not obj:
        return None
    
    bbox = get_bbox(obj)
    
    return {
        "name": obj.name,
        "type": obj.type,
        "location": tuple(obj.location),
        "rotation": tuple(obj.rotation_euler),
        "scale": tuple(obj.scale),
        "dimensions": {
            "width": bbox["size"][0],
            "depth": bbox["size"][1],
            "height": bbox["size"][2],
        },
        "bounding_box": bbox,
        "volume": bbox["size"][0] * bbox["size"][1] * bbox["size"][2],
        "materials": [m.name for m in obj.data.materials] if obj.data else [],
        "parent": obj.parent.name if obj.parent else None,
    }


# ═══════════════════════════════════════════════════════════════
# DETECCIÓN DE COLISIONES
# ═══════════════════════════════════════════════════════════════

def check_collision(obj1_name, obj2_name):
    """
    Verificar si dos objetos están colisionando.
    
    Returns:
        dict con {colliding: bool, overlap_volume: float}
    """
    obj1 = bpy.data.objects.get(obj1_name)
    obj2 = bpy.data.objects.get(obj2_name)
    
    if not obj1 or not obj2:
        return {"colliding": False, "error": "Objeto no encontrado"}
    
    bb1 = get_bbox(obj1)
    bb2 = get_bbox(obj2)
    
    # Verificar superposición en cada eje
    overlap_x = max(0, min(bb1["max"][0], bb2["max"][0]) - max(bb1["min"][0], bb2["min"][0]))
    overlap_y = max(0, min(bb1["max"][1], bb2["max"][1]) - max(bb1["min"][1], bb2["min"][1]))
    overlap_z = max(0, min(bb1["max"][2], bb2["max"][2]) - max(bb1["min"][2], bb2["min"][2]))
    
    colliding = overlap_x > 0 and overlap_y > 0 and overlap_z > 0
    overlap_volume = overlap_x * overlap_y * overlap_z
    
    return {
        "colliding": colliding,
        "overlap_volume": overlap_volume,
        "overlap_dimensions": (overlap_x, overlap_y, overlap_z),
    }


def check_all_collisions():
    """
    Verificar colisiones entre todos los pares de objetos.
    
    Returns:
        lista de colisiones encontradas
    """
    objects = list(bpy.data.objects)
    collisions = []
    
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            result = check_collision(objects[i].name, objects[j].name)
            if result.get("colliding"):
                collisions.append({
                    "object1": objects[i].name,
                    "object2": objects[j].name,
                    "overlap_volume": result["overlap_volume"],
                })
    
    return collisions


# ═══════════════════════════════════════════════════════════════
# VALIDACIÓN DE CONEXIONES
# ═══════════════════════════════════════════════════════════════

def validate_connections(collection_name=None):
    """
    Validar que todos los objetos en una colección están conectados.
    
    Returns:
        dict con {connected: list, disconnected: list}
    """
    connected = []
    disconnected = []
    
    if collection_name:
        objects = list(bpy.data.collections[collection_name].objects)
    else:
        objects = list(bpy.data.objects)
    
    for obj in objects:
        if obj.parent:
            # Verificar que está cerca del padre
            parent_bb = get_bbox(obj.parent)
            child_bb = get_bbox(obj)
            
            # Calcular distancia entre bordes
            parent_max = Vector(parent_bb["max"])
            child_min = Vector(child_bb["min"])
            
            distance = (parent_max - child_min).length
            
            if distance < 0.01:  # 1cm tolerance
                connected.append(obj.name)
            else:
                disconnected.append({
                    "object": obj.name,
                    "parent": obj.parent.name,
                    "distance": distance,
                })
        else:
            # Objeto sin padre (raíz)
            connected.append(obj.name)
    
    return {
        "connected": connected,
        "disconnected": disconnected,
        "all_connected": len(disconnected) == 0,
    }


# ═══════════════════════════════════════════════════════════════
# VALIDACIÓN DE MATERIALES
# ═══════════════════════════════════════════════════════════════

def validate_materials():
    """
    Validar que todos los objetos mesh tienen materiales.
    
    Returns:
        dict con {with_material: list, without_material: list}
    """
    with_material = []
    without_material = []
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if obj.data.materials:
                with_material.append(obj.name)
            else:
                without_material.append(obj.name)
    
    return {
        "with_material": with_material,
        "without_material": without_material,
        "all_have_materials": len(without_material) == 0,
    }


# ═══════════════════════════════════════════════════════════════
# VALIDACIÓN COMPLETA
# ═══════════════════════════════════════════════════════════════

def full_validation(collection_name=None):
    """
    Validación completa de la escena.
    
    Returns:
        dict con todos los resultados de validación
    """
    print("\n" + "="*60)
    print("VALIDACIÓN COMPLETA")
    print("="*60)
    
    # 1. Validar objetos
    print("\n1. Validando objetos...")
    objects_validation = validate_all_objects()
    print(f"   ✅ Válidos: {objects_validation['valid']}/{objects_validation['total']}")
    if objects_validation['with_errors']:
        print(f"   ❌ Con errores: {objects_validation['with_errors']}")
    if objects_validation['with_warnings']:
        print(f"   ⚠️  Con warnings: {objects_validation['with_warnings']}")
    
    # 2. Validar colisiones
    print("\n2. Verificando colisiones...")
    collisions = check_all_collisions()
    if collisions:
        print(f"   ❌ Colisiones encontradas: {len(collisions)}")
        for c in collisions:
            print(f"      - {c['object1']} ↔ {c['object2']}")
    else:
        print("   ✅ Sin colisiones")
    
    # 3. Validar materiales
    print("\n3. Verificando materiales...")
    materials_validation = validate_materials()
    print(f"   ✅ Con material: {len(materials_validation['with_material'])}")
    if materials_validation['without_material']:
        print(f"   ⚠️  Sin material: {materials_validation['without_material']}")
    
    # 4. Validar conexiones
    print("\n4. Verificando conexiones...")
    connections = validate_connections(collection_name)
    print(f"   ✅ Conectados: {len(connections['connected'])}")
    if connections['disconnected']:
        print(f"   ⚠️  Desconectados: {len(connections['disconnected'])}")
        for d in connections['disconnected']:
            print(f"      - {d['object']} (dist: {d['distance']:.4f}m)")
    
    print("\n" + "="*60)
    
    return {
        "objects": objects_validation,
        "collisions": collisions,
        "materials": materials_validation,
        "connections": connections,
        "is_valid": (
            objects_validation["with_errors"] == 0
            and len(collisions) == 0
            and connections["all_connected"]
        ),
    }


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def print_measurements(name):
    """Imprimir medidas de un objeto."""
    m = measure_object(name)
    if not m:
        print(f"Objeto '{name}' no encontrado")
        return
    
    print(f"\n📏 Medidas de {m['name']}:")
    print(f"   Tipo: {m['type']}")
    print(f"   Posición: ({m['location'][0]:.3f}, {m['location'][1]:.3f}, {m['location'][2]:.3f})")
    print(f"   Dimensiones: {m['dimensions']['width']:.3f} x {m['dimensions']['depth']:.3f} x {m['dimensions']['height']:.3f}m")
    print(f"   Volumen: {m['volume']:.6f} m³")
    print(f"   Materiales: {', '.join(m['materials']) if m['materials'] else 'Ninguno'}")
    print(f"   Padre: {m['parent'] or 'Ninguno'}")


def compare_dimensions(obj_name, expected_type):
    """
    Comparar dimensiones reales con las estándar.
    
    Args:
        obj_name: Nombre del objeto
        expected_type: Tipo estándar (chair, table, cup, etc.)
    
    Returns:
        dict con comparación
    """
    from .creation_rules import STANDARD_OBJECTS
    
    if expected_type not in STANDARD_OBJECTS:
        return {"error": f"Tipo no soportado: {expected_type}"}
    
    actual = measure_object(obj_name)
    if not actual:
        return {"error": f"Objeto no encontrado: {obj_name}"}
    
    config = STANDARD_OBJECTS[expected_type]
    
    # Obtener dimensiones esperadas según tipo
    expected_dims = {}
    if expected_type == "chair":
        expected_dims = {
            "width": config["seat"]["w"],
            "depth": config["seat"]["d"],
            "height": config["total_height"],
        }
    elif expected_type == "table":
        expected_dims = {
            "width": config["top"]["w"],
            "depth": config["top"]["d"],
            "height": config["total_height"],
        }
    elif expected_type == "cup":
        expected_dims = {
            "width": config["body"]["r"] * 2,
            "depth": config["body"]["r"] * 2,
            "height": config["total_height"],
        }
    
    comparison = {}
    for dim, expected_val in expected_dims.items():
        actual_val = actual["dimensions"][dim]
        diff = abs(actual_val - expected_val)
        diff_percent = (diff / expected_val) * 100 if expected_val > 0 else 0
        
        comparison[dim] = {
            "expected": expected_val,
            "actual": actual_val,
            "difference": diff,
            "difference_percent": diff_percent,
            "ok": diff_percent < 10,  # 10% tolerance
        }
    
    return comparison
