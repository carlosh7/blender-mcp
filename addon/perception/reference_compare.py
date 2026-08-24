"""
blender-mcp — Reference Compare
Sistema para comparar objetos con imágenes de referencia.
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
# REFERENCE COMPARISON
# ═══════════════════════════════════════════════════════════════


class ReferenceComparator:
    """Comparador de objetos con imágenes de referencia"""

    def __init__(self):
        self.references = {}

    def add_reference(self, name, image_path, expected_type=None, expected_color=None):
        """Agregar imagen de referencia"""
        self.references[name] = {
            "path": image_path,
            "expected_type": expected_type,
            "expected_color": expected_color,
        }

    def compare_with_scene(self):
        """Comparar referencias con escena actual"""
        if bpy is None:
            return {"error": "bpy not available"}

        results = []

        for name, ref in self.references.items():
            # Analizar escena actual
            scene_objects = self._analyze_scene()

            # Comparar con referencia
            comparison = self._compare(name, ref, scene_objects)
            results.append(comparison)

        return results

    def _analyze_scene(self):
        """Analizar escena actual"""
        objects = []

        for obj in bpy.data.objects:
            if obj.type == "MESH":
                bbox = self._get_bbox(obj)
                objects.append(
                    {
                        "name": obj.name,
                        "type": self._guess_type(obj),
                        "color": self._guess_color(obj),
                        "size": bbox["size"],
                    }
                )

        return objects

    def _get_bbox(self, obj):
        """Obtener bounding box"""
        if bpy is None:
            return {"min": (0, 0, 0), "max": (1, 1, 1), "size": (1, 1, 1)}

        from mathutils import Vector

        bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        mins = Vector(min(v[i] for v in bbox) for i in range(3))
        maxs = Vector(max(v[i] for v in bbox) for i in range(3))

        return {"min": tuple(mins), "max": tuple(maxs), "size": tuple(maxs - mins)}

    def _guess_type(self, obj):
        """Adivinar tipo de objeto"""
        name_lower = obj.name.lower()

        type_keywords = {
            "chair": "furniture",
            "silla": "furniture",
            "table": "furniture",
            "mesa": "furniture",
            "cube": "cube",
            "cubo": "cube",
            "sphere": "sphere",
            "esfera": "sphere",
            "cylinder": "cylinder",
            "cilindro": "cylinder",
        }

        for keyword, obj_type in type_keywords.items():
            if keyword in name_lower:
                return obj_type

        return "unknown"

    def _guess_color(self, obj):
        """Adivinar color dominante"""
        if obj.type != "MESH" or not obj.data.materials:
            return None

        mat = obj.data.materials[0]
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    color = node.inputs["Base Color"].default_value[:3]
                    # Convertir a nombre
                    if color[0] > 0.7 and color[1] < 0.3 and color[2] < 0.3:
                        return "red"
                    elif color[0] < 0.3 and color[1] < 0.3 and color[2] > 0.7:
                        return "blue"
                    elif color[0] < 0.3 and color[1] > 0.7 and color[2] < 0.3:
                        return "green"
                    elif color[0] > 0.7 and color[1] > 0.7 and color[2] < 0.3:
                        return "yellow"
                    elif sum(color) < 0.3:
                        return "black"
                    elif sum(color) > 2.4:
                        return "white"
                    else:
                        return "other"

        return None

    def _compare(self, ref_name, ref, scene_objects):
        """Comparar referencia con escena"""
        result = {
            "reference": ref_name,
            "matches": [],
            "mismatches": [],
            "score": 0,
        }

        # Buscar objetos que coincidan con la referencia
        for obj in scene_objects:
            score = 0

            # Comparar tipo
            if ref.get("expected_type") and obj["type"] == ref["expected_type"]:
                score += 50

            # Comparar color
            if ref.get("expected_color") and obj["color"] == ref["expected_color"]:
                score += 50

            if score > 0:
                result["matches"].append(
                    {
                        "object": obj["name"],
                        "score": score,
                    }
                )
            else:
                result["mismatches"].append(obj["name"])

        # Calcular score total
        if result["matches"]:
            result["score"] = max(m["score"] for m in result["matches"])

        return result


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════


def compare_scene_with_references(references):
    """
    Comparar escena con lista de referencias.

    Args:
        references: Lista de dict con name, expected_type, expected_color

    Returns:
        dict con resultados de comparación
    """
    comparator = ReferenceComparator()

    for ref in references:
        comparator.add_reference(
            ref.get("name", "unknown"),
            ref.get("path", ""),
            ref.get("expected_type"),
            ref.get("expected_color"),
        )

    return comparator.compare_with_scene()


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def get_scene_objects():
    """Obtener información de objetos en la escena"""
    if bpy is None:
        return []

    objects = []
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            mins = Vector(min(v[i] for v in bbox) for i in range(3))
            maxs = Vector(max(v[i] for v in bbox) for i in range(3))

            objects.append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": tuple(obj.location),
                    "size": tuple(maxs - mins),
                    "has_material": bool(obj.data.materials),
                }
            )

    return objects
