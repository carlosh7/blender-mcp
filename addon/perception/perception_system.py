"""
blender-mcp — Perception System
Sistema de visión alternativa: Scanner, Filter, Analyzer, Checker, Decision Engine.
"""

import bpy
from mathutils import Vector

# ═══════════════════════════════════════════════════════════════
# SCENE SCANNER (Radar Geométrico)
# ═══════════════════════════════════════════════════════════════


class SceneScanner:
    """Escáner de escena - como un radar, mapea toda la escena"""

    def scan(self, scene=None):
        """Escaneo completo de la escena"""
        if scene is None:
            scene = bpy.context.scene

        return {
            "objects": self._scan_objects(scene),
            "relationships": self._scan_relationships(scene),
            "materials": self._scan_materials(scene),
            "anomalies": self._scan_anomalies(scene),
        }

    def _scan_objects(self, scene):
        """Escanear todos los objetos"""
        objects = []
        for obj in scene.objects:
            bbox = self._get_bbox(obj)
            objects.append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": tuple(obj.location),
                    "rotation": tuple(obj.rotation_euler),
                    "scale": tuple(obj.scale),
                    "bbox_min": bbox["min"],
                    "bbox_max": bbox["max"],
                    "bbox_size": bbox["size"],
                    "material": self._get_material_name(obj),
                    "parent": obj.parent.name if obj.parent else None,
                }
            )
        return objects

    def _scan_relationships(self, scene):
        """Escanear relaciones entre objetos"""
        relationships = []
        for obj in scene.objects:
            if obj.parent:
                relationships.append(
                    {"child": obj.name, "parent": obj.parent.name, "type": "parent_child"}
                )
        return relationships

    def _scan_materials(self, scene):
        """Escanear materiales"""
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
                        }
                    )
        return materials

    def _scan_anomalies(self, scene):
        """Escanear anomalías"""
        anomalies = []

        for obj in scene.objects:
            # Verificar si está flotando
            if self._is_floating(obj):
                anomalies.append({"object": obj.name, "type": "floating", "severity": "high"})

            # Verificar tamaño cero
            bbox = self._get_bbox(obj)
            if any(s < 0.001 for s in bbox["size"]):
                anomalies.append({"object": obj.name, "type": "zero_size", "severity": "medium"})

        return anomalies

    def _get_bbox(self, obj):
        """Obtener bounding box"""
        bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        mins = Vector(min(v[i] for v in bbox) for i in range(3))
        maxs = Vector(max(v[i] for v in bbox) for i in range(3))
        return {"min": tuple(mins), "max": tuple(maxs), "size": tuple(maxs - mins)}

    def _get_material_name(self, obj):
        """Obtener nombre del material"""
        if obj.type == "MESH" and obj.data.materials:
            return obj.data.materials[0].name
        return None

    def _is_floating(self, obj):
        """Verificar si un objeto está flotando"""
        if obj.type != "MESH":
            return False
        bbox = self._get_bbox(obj)
        return bbox["min"][2] > 0.01


# ═══════════════════════════════════════════════════════════════
# ATTENTION FILTER
# ═══════════════════════════════════════════════════════════════


class AttentionFilter:
    """Filtro de atención - decide qué es relevante"""

    def filter(self, scan_data, context=None):
        """Filtrar datos por relevancia"""
        result = {
            "critical": [],
            "important": [],
            "minor": [],
        }

        for anomaly in scan_data.get("anomalies", []):
            if anomaly["severity"] == "high":
                result["critical"].append(anomaly)
            elif anomaly["severity"] == "medium":
                result["important"].append(anomaly)
            else:
                result["minor"].append(anomaly)

        # Agregar información de objetos
        for obj in scan_data.get("objects", []):
            if self._has_issue(obj):
                result["important"].append(
                    {"object": obj["name"], "type": "object_issue", "details": obj}
                )

        return result

    def _has_issue(self, obj):
        """Verificar si un objeto tiene problemas"""
        # Verificar material
        if obj["material"] is None and obj["type"] == "MESH":
            return True

        # Verificar escala
        if any(s < 0.001 for s in obj["scale"]):
            return True

        return False


# ═══════════════════════════════════════════════════════════════
# PATTERN ANALYZER
# ═══════════════════════════════════════════════════════════════


class PatternAnalyzer:
    """Analizador de patrones - extrae patrones y anomalías"""

    def analyze(self, scan_data):
        """Analizar patrones en los datos"""
        return {
            "symmetry": self._check_symmetry(scan_data),
            "alignment": self._check_alignment(scan_data),
            "distribution": self._check_distribution(scan_data),
        }

    def _check_symmetry(self, data):
        """Verificar simetría"""
        objects = data.get("objects", [])
        if len(objects) < 2:
            return {"detected": False}

        # Verificar simetría bilateral simple
        positions = [obj["location"] for obj in objects]

        # Contar objetos en cada lado del eje X
        left = sum(1 for p in positions if p[0] < 0)
        right = sum(1 for p in positions if p[0] > 0)

        return {"detected": abs(left - right) <= 1, "left_count": left, "right_count": right}

    def _check_alignment(self, data):
        """Verificar alineación"""
        objects = data.get("objects", [])

        # Verificar si los objetos están alineados en Z
        z_positions = [obj["location"][2] for obj in objects if obj["type"] == "MESH"]

        if not z_positions:
            return {"aligned": True}

        z_min = min(z_positions)
        z_max = max(z_positions)
        z_range = z_max - z_min

        return {
            "aligned": z_range < 1.0,  # Menos de 1m de diferencia
            "z_range": z_range,
        }

    def _check_distribution(self, data):
        """Verificar distribución"""
        objects = data.get("objects", [])

        if len(objects) < 3:
            return {"uniform": True}

        # Verificar si hay agrupaciones
        positions = [obj["location"] for obj in objects]

        # Calcular distancias promedio
        distances = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = sum((a - b) ** 2 for a, b in zip(positions[i], positions[j])) ** 0.5
                distances.append(dist)

        avg_dist = sum(distances) / len(distances) if distances else 0

        return {
            "uniform": avg_dist < 5.0,  # Distancia promedio < 5m
            "average_distance": avg_dist,
        }


# ═══════════════════════════════════════════════════════════════
# QUALITY CHECKER
# ═══════════════════════════════════════════════════════════════


class QualityChecker:
    """Verificador de calidad - verifica contra estándares"""

    def check(self, scan_data, standards=None):
        """Verificar calidad"""
        results = {
            "completeness": self._check_completeness(scan_data),
            "materials": self._check_materials(scan_data),
            "dimensions": self._check_dimensions(scan_data),
            "score": 0,
        }

        # Calcular score
        score = 100
        for check in results.values():
            if isinstance(check, dict) and not check.get("passed", True):
                score -= 10

        results["score"] = max(0, score)
        return results

    def _check_completeness(self, data):
        """Verificar completitud"""
        objects = data.get("objects", [])
        data.get("materials", [])

        mesh_objects = [o for o in objects if o["type"] == "MESH"]
        objects_with_material = [o for o in mesh_objects if o["material"]]

        return {
            "passed": len(objects_with_material) == len(mesh_objects),
            "mesh_objects": len(mesh_objects),
            "with_material": len(objects_with_material),
        }

    def _check_materials(self, data):
        """Verificar materiales"""
        materials = data.get("materials", [])

        issues = []
        for mat in materials:
            if mat["roughness"] < 0 or mat["roughness"] > 1:
                issues.append(f"{mat['name']}: roughness fuera de rango")
            if mat["metallic"] < 0 or mat["metallic"] > 1:
                issues.append(f"{mat['name']}: metallic fuera de rango")

        return {"passed": len(issues) == 0, "issues": issues}

    def _check_dimensions(self, data):
        """Verificar dimensiones"""
        objects = data.get("objects", [])

        issues = []
        for obj in objects:
            size = obj["bbox_size"]
            if any(s < 0.001 for s in size):
                issues.append(f"{obj['name']}: tamaño muy pequeño")
            if any(s > 100 for s in size):
                issues.append(f"{obj['name']}: tamaño muy grande")

        return {"passed": len(issues) == 0, "issues": issues}


# ═══════════════════════════════════════════════════════════════
# DECISION ENGINE
# ═══════════════════════════════════════════════════════════════


class DecisionEngine:
    """Motor de decisiones - toma acciones basadas en análisis"""

    def decide(self, scan_data, filtered_data, patterns, quality):
        """Tomar decisión basada en todo el análisis"""

        # ¿Hay errores críticos?
        if filtered_data["critical"]:
            return {
                "action": "fix_critical",
                "issues": filtered_data["critical"],
                "priority": "high",
                "message": f"Hay {len(filtered_data['critical'])} errores críticos",
            }

        # ¿Calidad baja?
        if quality["score"] < 70:
            return {
                "action": "improve",
                "score": quality["score"],
                "issues": quality.get("materials", {}).get("issues", []),
                "priority": "medium",
                "message": f"Calidad baja: {quality['score']}/100",
            }

        # Todo bien
        return {
            "action": "proceed",
            "score": quality["score"],
            "message": f"Calidad aceptable: {quality['score']}/100",
        }


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════


def analyze_scene(scene=None):
    """
    Análisis completo de escena usando el pipeline de percepción.

    Returns:
        dict con análisis completo
    """
    # 1. Escanear
    scanner = SceneScanner()
    scan_data = scanner.scan(scene)

    # 2. Filtrar
    filter = AttentionFilter()
    filtered = filter.filter(scan_data)

    # 3. Analizar patrones
    analyzer = PatternAnalyzer()
    patterns = analyzer.analyze(scan_data)

    # 4. Verificar calidad
    checker = QualityChecker()
    quality = checker.check(scan_data)

    # 5. Decidir
    engine = DecisionEngine()
    decision = engine.decide(scan_data, filtered, patterns, quality)

    return {
        "scan": scan_data,
        "filtered": filtered,
        "patterns": patterns,
        "quality": quality,
        "decision": decision,
        "summary": {
            "total_objects": len(scan_data["objects"]),
            "anomalies": len(scan_data["anomalies"]),
            "score": quality["score"],
            "action": decision["action"],
        },
    }
