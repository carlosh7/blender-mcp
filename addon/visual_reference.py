"""
blender-mcp — Visual Reference System
Sistema para comparar objetos con imágenes de referencia.
"""

try:
    import bpy
except ImportError:
    bpy = None

try:
    import math

    from mathutils import Vector
except ImportError:
    Vector = None

import os

# ═══════════════════════════════════════════════════════════════
# REFERENCE IMAGE MANAGER
# ═══════════════════════════════════════════════════════════════


class ReferenceManager:
    """Gestor de imágenes de referencia"""

    def __init__(self):
        self.references = {}
        self.current_reference = None

    def load_reference(self, image_path, name=None):
        """
        Cargar imagen de referencia al viewport.

        Args:
            image_path: Ruta de la imagen
            name: Nombre de la referencia
        """
        if bpy is None:
            return {"error": "bpy not available"}

        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_path}"}

        if name is None:
            name = os.path.basename(image_path)

        # Crear empty con imagen
        bpy.ops.object.empty_add(type="IMAGE", location=(0, 0, 0))
        empty = bpy.context.active_object
        empty.name = f"REF-{name}"

        # Cargar imagen
        img = bpy.data.images.load(image_path)
        empty.data = img
        empty.empty_display_size = 2

        # Guardar referencia
        self.references[name] = {
            "path": image_path,
            "object": empty,
            "name": name,
        }

        print(f"Reference loaded: {name} ({image_path})")
        return empty

    def set_as_background(self, reference_name):
        """Establecer imagen como fondo de cámara"""
        if reference_name not in self.references:
            return {"error": f"Reference not found: {reference_name}"}

        ref = self.references[reference_name]
        img = bpy.data.images.load(ref["path"])

        cam = bpy.context.scene.camera
        if cam:
            cam.data.background_image = img
            cam.data.background_alpha = 0.5
            print(f"Background set: {reference_name}")
            return True

        return {"error": "No active camera"}

    def analyze_reference(self, reference_name):
        """Analizar imagen de referencia"""
        if reference_name not in self.references:
            return {"error": f"Reference not found: {reference_name}"}

        ref = self.references[reference_name]
        img = bpy.data.images.load(ref["path"])

        return {
            "name": reference_name,
            "path": ref["path"],
            "width": img.size[0],
            "height": img.size[1],
            "aspect_ratio": img.size[0] / img.size[1] if img.size[1] > 0 else 1,
        }

    def list_references(self):
        """Listar todas las referencias"""
        return {k: v["path"] for k, v in self.references.items()}

    def remove_reference(self, reference_name):
        """Eliminar una referencia"""
        if reference_name in self.references:
            obj = self.references[reference_name]["object"]
            bpy.data.objects.remove(obj, do_unlink=True)
            del self.references[reference_name]
            print(f"Reference removed: {reference_name}")
            return True
        return False


# ═══════════════════════════════════════════════════════════════
# REFERENCE COMPARISON
# ═══════════════════════════════════════════════════════════════


def compare_with_reference(scene_objects, reference_data):
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
        found = False
        for obj in scene_objects:
            if obj["name"] == ref.get("name"):
                if obj["type"] == ref.get("type"):
                    matches.append(obj["name"])
                else:
                    mismatches.append(f"{obj['name']}: type mismatch")
                found = True
                break

        if not found:
            mismatches.append(f"{ref.get('name')}: not found")

    return {
        "matches": len(matches),
        "mismatches": len(mismatches),
        "score": len(matches) / max(len(reference_data), 1) * 100,
    }


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def list_reference_views():
    """Listar vistas de referencia disponibles"""
    return {
        "front": "Vista frontal",
        "back": "Vista trasera",
        "left": "Vista lateral izquierda",
        "right": "Vista lateral derecha",
        "top": "Vista superior",
        "perspective": "Vista perspectiva",
    }


# ═══════════════════════════════════════════════════════════════
# REFERENCE GRID
# ═══════════════════════════════════════════════════════════════


def create_reference_grid(size=10, spacing=1):
    """
    Crear cuadrícula de referencia.

    Args:
        size: Tamaño de la cuadrícula
        spacing: Espaciado entre líneas
    """
    if bpy is None:
        return None

    # Crear grid
    bpy.ops.mesh.primitive_grid_add(size=size, location=(0, 0, 0))
    grid = bpy.context.active_object
    grid.name = "ReferenceGrid"

    # Material
    mat = bpy.data.materials.new("GridMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.5
    grid.data.materials.append(mat)

    print(f"Reference grid: {size}m x {size}m")
    return grid


# ═══════════════════════════════════════════════════════════════
# MEASURE DISTANCE
# ═══════════════════════════════════════════════════════════════


def measure_distance(obj1_name, obj2_name):
    """
    Medir distancia entre dos objetos.

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

    print(f"Distance: {obj1_name} to {obj2_name} = {distance:.3f}m")
    return distance


# ═══════════════════════════════════════════════════════════════
# COMPARE DIMENSIONS
# ═══════════════════════════════════════════════════════════════


def compare_dimensions(obj_name, expected_width, expected_depth, expected_height, tolerance=0.01):
    """
    Comparar dimensiones con valores esperados.

    Args:
        obj_name: Nombre del objeto
        expected_width: Ancho esperado
        expected_depth: Profundidad esperada
        expected_height: Altura esperada
        tolerance: Tolerancia (0-1)

    Returns:
        dict con comparación
    """
    if bpy is None:
        return None

    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return {"error": f"Object not found: {obj_name}"}

    # Obtener dimensiones actuales
    bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mins = Vector(min(p[i] for p in bbox) for i in range(3))
    maxs = Vector(max(p[i] for p in bbox) for i in range(3))

    actual_width = maxs[0] - mins[0]
    actual_depth = maxs[1] - mins[1]
    actual_height = maxs[2] - mins[2]

    # Comparar
    width_match = abs(actual_width - expected_width) / expected_width < tolerance
    depth_match = abs(actual_depth - expected_depth) / expected_depth < tolerance
    height_match = abs(actual_height - expected_height) / expected_height < tolerance

    return {
        "matches": width_match and depth_match and height_match,
        "width": {"actual": actual_width, "expected": expected_width, "match": width_match},
        "depth": {"actual": actual_depth, "expected": expected_depth, "match": depth_match},
        "height": {"actual": actual_height, "expected": expected_height, "match": height_match},
    }


# ═══════════════════════════════════════════════════════════════
# OVERLAY REFERENCE
# ═══════════════════════════════════════════════════════════════


def overlay_reference(obj_name, reference_image_path):
    """
    Superponer imagen de referencia sobre un objeto.

    Args:
        obj_name: Nombre del objeto
        reference_image_path: Ruta de la imagen
    """
    if bpy is None:
        return {"error": "bpy not available"}

    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return {"error": f"Object not found: {obj_name}"}

    # Cargar imagen
    img = bpy.data.images.load(reference_image_path)

    # Crear plano con imagen
    bpy.ops.mesh.primitive_plane_add(size=2, location=obj.location)
    plane = bpy.context.active_object
    plane.name = f"Overlay_{obj.name}"

    # Material con imagen
    mat = bpy.data.materials.new(f"OverlayMat_{obj.name}")
    mat.use_nodes = True

    # Image Texture node
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img

    # Connect to base color
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    plane.data.materials.append(mat)

    print(f"Reference overlay created: {obj_name}")
    return plane


# ═══════════════════════════════════════════════════════════════
# ANNOTATION
# ═══════════════════════════════════════════════════════════════


def create_annotation(obj_name, text, offset=(0, 0, 0.5)):
    """
    Crear anotación sobre un objeto.

    Args:
        obj_name: Nombre del objeto
        text: Texto de la anotación
        offset: Desplazamiento desde el objeto
    """
    if bpy is None:
        return None

    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return None

    # Crear empty como marcador
    bpy.ops.object.empty_add(
        type="PLAIN_AXES",
        location=(
            obj.location.x + offset[0],
            obj.location.y + offset[1],
            obj.location.z + offset[2],
        ),
    )
    marker = bpy.context.active_object
    marker.name = f"Annotation_{obj_name}"
    marker.empty_display_size = 0.1

    # Agregar texto
    bpy.ops.object.text_add(
        location=(
            obj.location.x + offset[0],
            obj.location.y + offset[1],
            obj.location.z + offset[2] + 0.1,
        )
    )
    text_obj = bpy.context.active_object
    text_obj.name = f"Text_{obj_name}"
    text_obj.data.body = text
    text_obj.data.size = 0.1

    print(f"Annotation created: {obj_name} - {text}")
    return marker


# ═══════════════════════════════════════════════════════════════
# MEASURE ANGLE
# ═══════════════════════════════════════════════════════════════


def measure_angle(obj1_name, obj2_name, obj3_name):
    """
    Medir ángulo entre tres objetos.

    Args:
        obj1_name: Primer objeto (vértice del ángulo)
        obj2_name: Segundo objeto
        obj3_name: Tercer objeto

    Returns:
        Ángulo en grados
    """
    if bpy is None:
        return None

    obj1 = bpy.data.objects.get(obj1_name)
    obj2 = bpy.data.objects.get(obj2_name)
    obj3 = bpy.data.objects.get(obj3_name)

    if not obj1 or not obj2 or not obj3:
        return None

    # Obtener posiciones
    p1 = Vector(obj1.location)
    p2 = Vector(obj2.location)
    p3 = Vector(obj3.location)

    # Calcular ángulo
    v1 = p2 - p1
    v2 = p3 - p1

    angle = v1.angle(v2)
    angle_deg = math.degrees(angle)

    print(f"Angle: {obj1_name} - {obj2_name} - {obj3_name} = {angle_deg:.1f}°")
    return angle_deg


# ═══════════════════════════════════════════════════════════════
# DIMENSION LINE
# ═══════════════════════════════════════════════════════════════


def create_dimension_line(obj1_name, obj2_name, offset=(0, 0, 0)):
    """
    Crear línea de dimensión entre dos objetos.

    Args:
        obj1_name: Primer objeto
        obj2_name: Segundo objeto
        offset: Desplazamiento
    """
    if bpy is None:
        return None

    obj1 = bpy.data.objects.get(obj1_name)
    obj2 = bpy.data.objects.get(obj2_name)

    if not obj1 or not obj2:
        return None

    # Obtener centros
    bb1 = [obj1.matrix_world @ Vector(c) for c in obj1.bound_box]
    bb2 = [obj2.matrix_world @ Vector(c) for c in obj2.bound_box]

    center1 = Vector(sum(p[i] for p in bb1) / len(bb1) for i in range(3))
    center2 = Vector(sum(p[i] for p in bb2) / len(bb2) for i in range(3))

    # Crear curva como línea de dimensión
    curve_data = bpy.data.curves.new("DimensionLine", type="CURVE")
    curve_data.dimensions = "3D"

    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(1)
    spline.bezier_points[0].co = center1 + Vector(offset)
    spline.bezier_points[1].co = center2 + Vector(offset)

    obj = bpy.data.objects.new("DimensionLine", curve_data)
    bpy.context.collection.objects.link(obj)

    # Calcular distancia
    distance = (center1 - center2).length

    print(f"Dimension line: {obj1_name} to {obj2_name} = {distance:.3f}m")
    return obj
