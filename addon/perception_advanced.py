"""
blender-mcp — Perception Advanced Engine
Motor de percepción avanzada: Escáner, Quality Check, Reference Compare.
"""

try:
    import bpy
except ImportError:
    bpy = None

try:
    from mathutils import Vector
except ImportError:
    Vector = None


# ═══════════════════════════════════════════════════════════════
# SCENE SCANNER ADVANCED
# ═══════════════════════════════════════════════════════════════


def scene_scanner_advanced(scene=None):
    """
    Escáner avanzado de escena.

    Returns:
        dict con análisis completo
    """
    if bpy is None:
        return {"error": "bpy not available"}

    if scene is None:
        scene = bpy.context.scene

    # Escanear objetos
    objects = []
    for obj in scene.objects:
        obj_data = {
            "name": obj.name,
            "type": obj.type,
            "location": tuple(obj.location),
            "rotation": tuple(obj.rotation_euler),
            "scale": tuple(obj.scale),
        }

        if obj.type == "MESH":
            obj_data["vertices"] = len(obj.data.vertices)
            obj_data["faces"] = len(obj.data.polygons)
            obj_data["has_material"] = bool(obj.data.materials)
            obj_data["has_smooth"] = any(p.use_smooth for p in obj.data.polygons)

        objects.append(obj_data)

    # Estadísticas
    stats = {
        "total_objects": len(objects),
        "meshes": len([o for o in objects if o["type"] == "MESH"]),
        "lights": len([o for o in objects if o["type"] == "LIGHT"]),
        "cameras": len([o for o in objects if o["type"] == "CAMERA"]),
        "materials": len(bpy.data.materials),
    }

    return {
        "objects": objects,
        "stats": stats,
        "timestamp": str(bpy.context.scene.frame_current),
    }


def fix_geometry_anomalies(obj):
    """
    Detectar y reparar automáticamente anomalías en la malla (normales invertidas, vértices sueltos).
    """
    if bpy is None or obj is None or obj.type != "MESH":
        return False

    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.select_set(False)
        print(f"Geometría reparada para: {obj.name}")
        return True
    except Exception as e:
        print(f"Error al reparar geometría de {obj.name}: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# QUALITY CHECK ADVANCED
# ═══════════════════════════════════════════════════════════════


def quality_check_advanced(scene=None):
    """
    Verificación avanzada de calidad.

    Returns:
        dict con score y detalles
    """
    if bpy is None:
        return {"error": "bpy not available"}

    if scene is None:
        scene = bpy.context.scene

    issues = []

    # Verificar objetos
    for obj in scene.objects:
        if obj.type == "MESH":
            # Verificar vértices
            if len(obj.data.vertices) == 0:
                issues.append(f"{obj.name}: sin vértices")

            # Verificar caras
            if len(obj.data.polygons) == 0:
                issues.append(f"{obj.name}: sin caras")

            # Verificar material
            if not obj.data.materials:
                issues.append(f"{obj.name}: sin material")

            # Verificar smooth shading
            if not any(p.use_smooth for p in obj.data.polygons):
                issues.append(f"{obj.name}: sin smooth shading")

    # Calcular score
    total = len([o for o in scene.objects if o.type == "MESH"])
    issues_count = len(issues)
    score = max(0, 100 - (issues_count * 5))

    return {
        "score": score,
        "issues": issues,
        "total_objects": total,
        "passed": issues_count == 0,
    }


# ═══════════════════════════════════════════════════════════════
# REFERENCE COMPARE ADVANCED
# ═══════════════════════════════════════════════════════════════


def reference_compare_advanced(scene_objects, reference_data):
    """
    Comparar escena con datos de referencia.

    Args:
        scene_objects: Objetos de la escena
        reference_data: Datos de referencia esperados

    Returns:
        dict con comparación
    """
    matches = []
    mismatches = []

    for ref in reference_data:
        # Buscar objeto correspondiente
        found = False
        for obj in scene_objects:
            if obj["name"] == ref.get("name"):
                # Comparar tipo
                if obj["type"] == ref.get("type"):
                    matches.append(obj["name"])
                else:
                    mismatches.append(f"{obj['name']}: tipo diferente")
                found = True
                break

        if not found:
            mismatches.append(f"{ref.get('name')}: no encontrado")

    return {
        "matches": len(matches),
        "mismatches": len(mismatches),
        "score": len(matches) / max(len(reference_data), 1) * 100,
    }


# ═══════════════════════════════════════════════════════════════
# SCREENSHOT WITH ANALYSIS
# ═══════════════════════════════════════════════════════════════


def screenshot_with_analysis(filepath="/tmp/blender_analysis.png"):
    """
    Tomar screenshot y analizar.
    """
    if bpy is None:
        return {"error": "bpy not available"}

    try:
        # Tomar screenshot
        bpy.ops.screen.screenshot_area(filepath=filepath)

        # Analizar escena
        analysis = scene_scanner_advanced()

        return {
            "filepath": filepath,
            "analysis": analysis,
            "message": f"Screenshot saved: {filepath}",
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def list_perception_tools():
    """Listar herramientas de percepción"""
    return {
        "scene_scanner": "Escaneo completo de escena",
        "quality_check": "Verificación de calidad",
        "reference_compare": "Comparación con referencia",
        "screenshot_analysis": "Screenshot + análisis",
        "object_detector": "Detección de objetos",
        "material_analyzer": "Análisis de materiales",
        "spatial_analyzer": "Análisis espacial",
        "anomaly_detector": "Detección de anomalías",
    }


# ═══════════════════════════════════════════════════════════════
# OBJECT DETECTOR
# ═══════════════════════════════════════════════════════════════


def object_detector(scene=None, filter_type=None):
    """
    Detectar objetos por tipo.

    Args:
        scene: Escena (default: actual)
        filter_type: Filtrar por tipo ('MESH', 'LIGHT', etc.)

    Returns:
        Lista de objetos detectados
    """
    if bpy is None:
        return []

    if scene is None:
        scene = bpy.context.scene

    detected = []

    for obj in scene.objects:
        if filter_type and obj.type != filter_type:
            continue

        detected.append(
            {
                "name": obj.name,
                "type": obj.type,
                "location": tuple(obj.location),
                "size": tuple(obj.scale),
            }
        )

    print(f"Detected {len(detected)} objects")
    return detected


# ═══════════════════════════════════════════════════════════════
# MATERIAL ANALYZER
# ═══════════════════════════════════════════════════════════════


def material_analyzer(scene=None):
    """
    Analizar materiales de la escena.
    """
    if bpy is None:
        return []

    if scene is None:
        scene = bpy.context.scene

    materials = []

    for mat in bpy.data.materials:
        if mat.use_nodes:
            bsdf = None
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    bsdf = node
                    break

            if bsdf:
                materials.append(
                    {
                        "name": mat.name,
                        "color": tuple(bsdf.inputs["Base Color"].default_value[:3]),
                        "roughness": bsdf.inputs["Roughness"].default_value,
                        "metallic": bsdf.inputs["Metallic"].default_value,
                        "users": mat.users,
                    }
                )

    print(f"Analyzed {len(materials)} materials")
    return materials


# ═══════════════════════════════════════════════════════════════
# SPATIAL ANALYZER
# ═══════════════════════════════════════════════════════════════


def spatial_analyzer(scene=None):
    """
    Análisis espacial de la escena.
    """
    if bpy is None:
        return {}

    if scene is None:
        scene = bpy.context.scene

    # Calcular bounds de la escena
    all_points = []
    for obj in scene.objects:
        if obj.type == "MESH":
            bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            all_points.extend(bbox)

    if not all_points:
        return {"error": "No mesh objects found"}

    mins = Vector(min(p[i] for p in all_points) for i in range(3))
    maxs = Vector(max(p[i] for p in all_points) for i in range(3))

    return {
        "bounds_min": tuple(mins),
        "bounds_max": tuple(maxs),
        "size": tuple(maxs - mins),
        "center": tuple((mins + maxs) / 2),
    }


# ═══════════════════════════════════════════════════════════════
# ANOMALY DETECTOR
# ═══════════════════════════════════════════════════════════════


def anomaly_detector(scene=None):
    """
    Detectar anomalías en la escena.
    """
    if bpy is None:
        return []

    if scene is None:
        scene = bpy.context.scene

    anomalies = []

    for obj in scene.objects:
        # Objeto muy lejos del centro
        if obj.location.length > 100:
            anomalies.append({"object": obj.name, "type": "far_from_center", "severity": "medium"})

        # Objeto muy pequeño
        if obj.type == "MESH":
            bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            size = Vector(max(p[i] for p in bbox) - min(p[i] for p in bbox) for i in range(3))
            if size.length < 0.001:
                anomalies.append({"object": obj.name, "type": "too_small", "severity": "low"})

        # Objeto muy grande
        if obj.type == "MESH":
            bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            size = Vector(max(p[i] for p in bbox) - min(p[i] for p in bbox) for i in range(3))
            if size.length > 100:
                anomalies.append({"object": obj.name, "type": "too_large", "severity": "medium"})

    print(f"Detected {len(anomalies)} anomalies")
    return anomalies


# ═══════════════════════════════════════════════════════════════
# DISTANCE CALCULATOR
# ═══════════════════════════════════════════════════════════════


def distance_calculator(obj1_name, obj2_name):
    """
    Calcular distancia entre dos objetos.

    Args:
        obj1_name: Nombre del primer objeto
        obj2_name: Nombre del segundo objeto

    Returns:
        Distancia en metros
    """
    if bpy is None:
        return None

    obj1 = bpy.data.objects.get(obj1_name)
    obj2 = bpy.data.objects.get(obj2_name)

    if not obj1 or not obj2:
        return None

    # Calcular centros
    bb1 = [obj1.matrix_world @ Vector(c) for c in obj1.bound_box]
    bb2 = [obj2.matrix_world @ Vector(c) for c in obj2.bound_box]

    center1 = Vector(sum(p[i] for p in bb1) / len(bb1) for i in range(3))
    center2 = Vector(sum(p[i] for p in bb2) / len(bb2) for i in range(3))

    distance = (center1 - center2).length

    return {
        "object1": obj1_name,
        "object2": obj2_name,
        "distance": distance,
    }


# ═══════════════════════════════════════════════════════════════
# VOLUME CALCULATOR
# ═══════════════════════════════════════════════════════════════


def volume_calculator(obj_name):
    """
    Calcular volumen de un objeto.

    Args:
        obj_name: Nombre del objeto

    Returns:
        Volumen en metros cúbicos
    """
    if bpy is None:
        return None

    obj = bpy.data.objects.get(obj_name)
    if not obj or obj.type != "MESH":
        return None

    # Calcular bounding box
    bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mins = Vector(min(p[i] for p in bbox) for i in range(3))
    maxs = Vector(max(p[i] for p in bbox) for i in range(3))

    # Volumen aproximado
    volume = (maxs[0] - mins[0]) * (maxs[1] - mins[1]) * (maxs[2] - mins[2])

    return {
        "object": obj_name,
        "volume": volume,
        "dimensions": {
            "width": maxs[0] - mins[0],
            "depth": maxs[1] - mins[1],
            "height": maxs[2] - mins[2],
        },
    }


# ═══════════════════════════════════════════════════════════════
# BBOX ANALYZER
# ═══════════════════════════════════════════════════════════════


def bbox_analyzer(scene=None):
    """
    Analizar bounding boxes de todos los objetos.
    """
    if bpy is None:
        return []

    if scene is None:
        scene = bpy.context.scene

    results = []

    for obj in scene.objects:
        if obj.type == "MESH":
            bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            mins = Vector(min(p[i] for p in bbox) for i in range(3))
            maxs = Vector(max(p[i] for p in bbox) for i in range(3))
            center = (mins + maxs) / 2
            size = maxs - mins

            results.append(
                {
                    "name": obj.name,
                    "center": tuple(center),
                    "size": tuple(size),
                    "volume": size[0] * size[1] * size[2],
                }
            )

    print(f"Analyzed {len(results)} bounding boxes")
    return results
