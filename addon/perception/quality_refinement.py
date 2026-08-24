"""
blender-mcp — Quality Refinement System
Sistema de refinamiento de calidad automático.
Inspirado en cc-blender-skill's quality-refinement-autoloop.
"""

try:
    import bpy
except ImportError:
    bpy = None


# ═══════════════════════════════════════════════════════════════
# QUALITY DIMENSIONS
# ═══════════════════════════════════════════════════════════════

QUALITY_DIMENSIONS = {
    "geometry": {
        "description": "Calidad geométrica",
        "checks": ["vertex_count", "face_count", "manifold", "normals"],
        "weight": 0.25,
    },
    "materials": {
        "description": "Calidad de materiales",
        "checks": ["pbr_correct", "uv_mapping", "texture_resolution"],
        "weight": 0.25,
    },
    "structure": {
        "description": "Integridad estructural",
        "checks": ["connections", "stability", "proportions"],
        "weight": 0.25,
    },
    "aesthetics": {
        "description": "Calidad estética",
        "checks": ["symmetry", "balance", "color_harmony"],
        "weight": 0.25,
    },
}


# ═══════════════════════════════════════════════════════════════
# QUALITY CHECKER
# ═══════════════════════════════════════════════════════════════


class QualityRefiner:
    """Sistema de refinamiento de calidad automático"""

    def __init__(self):
        self.max_iterations = 3
        self.quality_threshold = 80

    def refine(self, scene_objects, target_quality=85):
        """
        Refinar calidad de la escena hasta alcanzar el objetivo.

        Args:
            scene_objects: Objetos de la escena
            target_quality: Calidad objetivo (0-100)

        Returns:
            dict con resultados del refinamiento
        """
        results = {
            "iterations": 0,
            "initial_quality": 0,
            "final_quality": 0,
            "improvements": [],
            "success": False,
        }

        # Evaluar calidad inicial
        initial = self.evaluate_quality(scene_objects)
        results["initial_quality"] = initial["score"]

        # Iterar hasta alcanzar calidad objetivo
        current_quality = initial["score"]

        for iteration in range(self.max_iterations):
            results["iterations"] = iteration + 1

            if current_quality >= target_quality:
                results["success"] = True
                break

            # Identificar problemas
            issues = self.identify_issues(scene_objects)

            if not issues:
                break

            # Aplicar mejoras
            improvements = self.apply_improvements(scene_objects, issues)
            results["improvements"].extend(improvements)

            # Re-evaluar
            new_quality = self.evaluate_quality(scene_objects)
            current_quality = new_quality["score"]

        results["final_quality"] = current_quality
        results["success"] = current_quality >= target_quality

        return results

    def evaluate_quality(self, scene_objects):
        """Evaluar calidad de la escena"""
        scores = {}

        # Geometría
        scores["geometry"] = self.evaluate_geometry(scene_objects)

        # Materiales
        scores["materials"] = self.evaluate_materials(scene_objects)

        # Estructura
        scores["structure"] = self.evaluate_structure(scene_objects)

        # Estética
        scores["aesthetics"] = self.evaluate_aesthetics(scene_objects)

        # Score total ponderado
        total = sum(scores[dim] * QUALITY_DIMENSIONS[dim]["weight"] for dim in scores)

        return {
            "score": total,
            "dimensions": scores,
        }

    def evaluate_geometry(self, objects):
        """Evaluar calidad geométrica"""
        score = 100

        for obj in objects:
            if obj.type == "MESH":
                # Verificar que tiene vértices
                if len(obj.data.vertices) == 0:
                    score -= 20

                # Verificar que tiene caras
                if len(obj.data.polygons) == 0:
                    score -= 20

        return max(0, score)

    def evaluate_materials(self, objects):
        """Evaluar calidad de materiales"""
        score = 100

        mesh_objects = [o for o in objects if o.type == "MESH"]
        objects_with_material = [o for o in mesh_objects if o.data.materials]

        if mesh_objects:
            material_ratio = len(objects_with_material) / len(mesh_objects)
            score = int(material_ratio * 100)

        return score

    def evaluate_structure(self, objects):
        """Evaluar integridad estructural"""
        score = 100

        # Verificar conexiones
        orphans = [o for o in objects if o.parent is None and o.type == "MESH"]
        if orphans:
            score -= len(orphans) * 5

        return max(0, score)

    def evaluate_aesthetics(self, objects):
        """Evaluar calidad estética"""
        # Simplificado - en producción usaría análisis visual
        return 85

    def identify_issues(self, objects):
        """Identificar problemas de calidad"""
        issues = []

        for obj in objects:
            # Sin material
            if obj.type == "MESH" and not obj.data.materials:
                issues.append(
                    {
                        "object": obj.name,
                        "type": "missing_material",
                        "severity": "medium",
                    }
                )

            # Tamaño cero
            bbox = self._get_bbox(obj)
            if any(s < 0.001 for s in bbox["size"]):
                issues.append(
                    {
                        "object": obj.name,
                        "type": "zero_size",
                        "severity": "high",
                    }
                )

        return issues

    def apply_improvements(self, objects, issues):
        """Aplicar mejoras automáticas"""
        improvements = []

        for issue in issues:
            if issue["type"] == "missing_material":
                # Asignar material por defecto
                obj = bpy.data.objects.get(issue["object"])
                if obj and obj.type == "MESH":
                    mat = bpy.data.materials.new(f"AutoMat_{obj.name}")
                    mat.use_nodes = True
                    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
                        0.5,
                        0.5,
                        0.5,
                        1,
                    )
                    obj.data.materials.append(mat)
                    improvements.append(f"Material asignado a {obj.name}")

            elif issue["type"] == "zero_size":
                # Escalar objeto
                obj = bpy.data.objects.get(issue["object"])
                if obj:
                    obj.scale = (1, 1, 1)
                    improvements.append(f"Escalado {obj.name}")

        return improvements

    def _get_bbox(self, obj):
        """Obtener bounding box"""
        from mathutils import Vector

        bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        mins = Vector(min(v[i] for v in bbox) for i in range(3))
        maxs = Vector(max(v[i] for v in bbox) for i in range(3))
        return {"min": tuple(mins), "max": tuple(maxs), "size": tuple(maxs - mins)}


# ═══════════════════════════════════════════════════════════════
# VALIDATION GATES
# ═══════════════════════════════════════════════════════════════


class ValidationGate:
    """Puerto de validación para cada paso del workflow"""

    def __init__(self):
        self.gates = {
            "modeling": self.validate_modeling,
            "texturing": self.validate_texturing,
            "rigging": self.validate_rigging,
            "animation": self.validate_animation,
            "physics": self.validate_physics,
            "sculpting": self.validate_sculpting,
            "procedural": self.validate_procedural,
            "export": self.validate_export,
        }

    def validate(self, stage, scene_data):
        """Validar un paso específico"""
        if stage not in self.gates:
            return {"valid": True, "message": f"Etapa no reconocida: {stage}"}

        return self.gates[stage](scene_data)

    def validate_modeling(self, data):
        """Validar modelado"""
        issues = []

        for obj in data.get("objects", []):
            if obj.type == "MESH":
                if len(obj.data.vertices) == 0:
                    issues.append(f"{obj.name}: sin vértices")
                if len(obj.data.polygons) == 0:
                    issues.append(f"{obj.name}: sin caras")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Modelado válido" if not issues else f"{len(issues)} problemas",
        }

    def validate_texturing(self, data):
        """Validar texturizado"""
        issues = []

        for obj in data.get("objects", []):
            if obj.type == "MESH" and not obj.data.materials:
                issues.append(f"{obj.name}: sin material")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Texturizado válido" if not issues else f"{len(issues)} sin material",
        }

    def validate_rigging(self, data):
        """Validar rigging"""
        issues = []

        armatures = [o for o in data.get("objects", []) if o.type == "ARMATURE"]

        if not armatures and data.get("requires_rig"):
            issues.append("No se encontró armature")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Rigging válido" if not issues else f"{len(issues)} problemas",
        }

    def validate_animation(self, data):
        """Validar animación"""
        issues = []

        for obj in data.get("objects", []):
            if obj.animation_data and obj.animation_data.action:
                if len(obj.animation_data.action.fcurves) == 0:
                    issues.append(f"{obj.name}: animación sin curvas")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Animación válida" if not issues else f"{len(issues)} problemas",
        }

    def validate_export(self, data):
        """Validar exportación"""
        issues = []

        # Verificar que hay objetos para exportar
        if not data.get("objects"):
            issues.append("No hay objetos para exportar")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Exportación válida" if not issues else f"{len(issues)} problemas",
        }

    def validate_physics(self, data):
        """Validar física"""
        issues = []

        for obj in data.get("objects", []):
            if hasattr(obj, "rigid_body") and obj.rigid_body:
                if obj.rigid_body.mass <= 0:
                    issues.append(f"{obj.name}: masa inválida")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Física válida" if not issues else f"{len(issues)} problemas",
        }

    def validate_sculpting(self, data):
        """Validar sculpting"""
        issues = []

        for obj in data.get("objects", []):
            if obj.type == "MESH" and len(obj.data.vertices) < 100:
                issues.append(f"{obj.name}: pocos vértices para sculpting")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Sculpting válido" if not issues else f"{len(issues)} problemas",
        }

    def validate_procedural(self, data):
        """Validar procedural generation"""
        issues = []

        for obj in data.get("objects", []):
            if obj.type == "MESH" and len(obj.data.polygons) > 10000:
                issues.append(f"{obj.name}: demasiados polígonos")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Procedural válido" if not issues else f"{len(issues)} problemas",
        }


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════


def refine_quality(target_quality=85, max_iterations=3):
    """
    Refinar calidad de la escena actual.

    Args:
        target_quality: Calidad objetivo (0-100)
        max_iterations: Máximo de iteraciones

    Returns:
        dict con resultados
    """
    refiner = QualityRefiner()
    refiner.max_iterations = max_iterations

    # Obtener objetos de la escena
    objects = list(bpy.data.objects)

    # Ejecutar refinamiento
    results = refiner.refine(objects, target_quality)

    print("Refinamiento completado:")
    print(f"  Iteraciones: {results['iterations']}")
    print(f"  Calidad inicial: {results['initial_quality']}/100")
    print(f"  Calidad final: {results['final_quality']}/100")
    print(f"  Mejoras aplicadas: {len(results['improvements'])}")
    print(f"  Objetivo alcanzado: {'Sí' if results['success'] else 'No'}")

    return results


def validate_stage(stage):
    """
    Validar un paso del workflow.

    Args:
        stage: 'modeling', 'texturing', 'rigging', 'animation', 'export'

    Returns:
        dict con resultado de validación
    """
    gate = ValidationGate()

    # Obtener objetos de la escena
    data = {"objects": list(bpy.data.objects)}

    return gate.validate(stage, data)
