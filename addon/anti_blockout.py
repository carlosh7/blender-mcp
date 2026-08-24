"""
blender-mcp — Anti-Blockout Validation
Validación para evitar objetos blockout/blocking.

REGLA ABSOLUTA: No se permiten objetos que sean solo primitivas básicas
sin detalles, materiales reales, biselado ni formas orgánicas.
"""

import bpy

# ═══════════════════════════════════════════════════════════════
# BLOCKOUT DETECTION
# ═══════════════════════════════════════════════════════════════

# Umbral mínimo de vértices para considerar un objeto "detallado"
MIN_VERTICES = {
    "chair": 20,
    "table": 16,
    "cup": 32,
    "book": 8,
    "lamp": 24,
    "pot": 32,
    "person": 100,
    "animal": 80,
    "vehicle": 60,
    "building": 40,
    "default": 12,
}


def is_blockout(obj: bpy.types.Object) -> dict[str, any]:
    """
    Detectar si un objeto es blockout (prohibido).

    Args:
        obj: Objeto a evaluar

    Returns:
        Dict con {is_blockout: bool, reasons: list, score: int}
    """
    reasons = []
    score = 100  # Empieza perfecto, se resta por cada problema

    # 1. Verificar vértices
    if obj.type == "MESH":
        vert_count = len(obj.data.vertices)
        obj_type = _detect_object_type(obj)
        min_verts = MIN_VERTICES.get(obj_type, MIN_VERTICES["default"])

        if vert_count < min_verts:
            reasons.append(f"Muy pocos vértices: {vert_count} (mínimo: {min_verts})")
            score -= 30

    # 2. Verificar biselado (modifiers)
    has_bevel = False
    for mod in obj.modifiers:
        if mod.type == "BEVEL":
            has_bevel = True
            break

    if not has_bevel and obj.type == "MESH":
        reasons.append("Sin biselado (Bevel modifier)")
        score -= 20

    # 3. Verificar materiales
    if obj.type == "MESH":
        if not obj.data.materials:
            reasons.append("Sin material asignado")
            score -= 25
        elif len(obj.data.materials) == 1:
            mat = obj.data.materials[0]
            if mat and mat.use_nodes:
                # Verificar si es solo un color básico
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    # Si roughness es 0.5 exacto y metallic es 0, probablemente es básico
                    roughness = bsdf.inputs.get("Roughness")
                    metallic = bsdf.inputs.get("Metallic")
                    if roughness and metallic:
                        if roughness.default_value == 0.5 and metallic.default_value == 0.0:
                            reasons.append("Material demasiado básico (sin variación PBR)")
                            score -= 10

    # 4. Verificar sombreado suave
    if obj.type == "MESH" and hasattr(obj.data, "polygons"):
        if len(obj.data.polygons) > 0:
            # Verificar si tiene smooth shading
            smooth_count = sum(1 for p in obj.data.polygons if p.use_smooth)
            if smooth_count == 0 and len(obj.data.polygons) > 4:
                reasons.append("Sin sombreado suave (Shade Auto Smooth)")
                score -= 15

    # 5. Verificar si es primitiva sin modificar
    if obj.type == "MESH":
        # Contar caras planas (posible primitiva)
        if len(obj.data.polygons) <= 6:  # Cubo tiene 6 caras
            # Verificar si tiene subdivision o deformación
            has_subsurf = any(m.type == "SUBSURF" for m in obj.modifiers)
            has_solidify = any(m.type == "SOLIDIFY" for m in obj.modifiers)

            if not has_subsurf and not has_solidify:
                reasons.append("Primitiva básica sin modificar")
                score -= 30

    # 6. Verificar UV mapping
    if obj.type == "MESH" and obj.data.uv_layers:
        if len(obj.data.uv_layers) == 0:
            reasons.append("Sin UV mapping")
            score -= 10

    # Determinar si es blockout
    is_blockout_obj = score < 50

    return {
        "is_blockout": is_blockout_obj,
        "reasons": reasons,
        "score": max(0, score),
        "object_name": obj.name,
    }


def _detect_object_type(obj: bpy.types.Object) -> str:
    """Detectar tipo de objeto por nombre o forma."""
    name_lower = obj.name.lower()

    type_keywords = {
        "chair": ["chair", "silla", "seat"],
        "table": ["table", "mesa", "desk"],
        "cup": ["cup", "taza", "mug"],
        "book": ["book", "libro"],
        "lamp": ["lamp", "luz", "light"],
        "pot": ["pot", "maceta", "vase"],
        "person": ["person", "human", "body", "head", "torso"],
        "animal": ["animal", "dog", "cat", "bird"],
        "vehicle": ["car", "bike", "vehicle", "coche"],
        "building": ["house", "building", "casa"],
    }

    for obj_type, keywords in type_keywords.items():
        if any(kw in name_lower for kw in keywords):
            return obj_type

    return "default"


# ═══════════════════════════════════════════════════════════════
# SCENE VALIDATION
# ═══════════════════════════════════════════════════════════════


def validate_scene_blockout() -> dict[str, any]:
    """
    Validar toda la escena contra blockout.

    Returns:
        Dict con resultados
    """
    results = {
        "total_objects": 0,
        "blockout_objects": 0,
        "clean_objects": 0,
        "details": [],
    }

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            results["total_objects"] += 1
            check = is_blockout(obj)

            if check["is_blockout"]:
                results["blockout_objects"] += 1
                results["details"].append(
                    {
                        "name": obj.name,
                        "is_blockout": True,
                        "reasons": check["reasons"],
                        "score": check["score"],
                    }
                )
            else:
                results["clean_objects"] += 1

    results["all_clean"] = results["blockout_objects"] == 0
    results["blockout_ratio"] = (
        results["blockout_objects"] / results["total_objects"]
        if results["total_objects"] > 0
        else 0
    )

    return results


def get_blockout_report() -> str:
    """
    Generar reporte legible de blockout.

    Returns:
        String con reporte formateado
    """
    results = validate_scene_blockout()

    lines = [
        "=== BLOCKOUT VALIDATION REPORT ===",
        f"Total objects: {results['total_objects']}",
        f"Clean objects: {results['clean_objects']}",
        f"Blockout objects: {results['blockout_objects']}",
        f"Blockout ratio: {results['blockout_ratio']:.1%}",
        "",
    ]

    if results["blockout_objects"] > 0:
        lines.append("--- BLOCKOUT OBJECTS ---")
        for detail in results["details"]:
            lines.append(f"  ❌ {detail['name']} (score: {detail['score']})")
            for reason in detail["reasons"]:
                lines.append(f"     - {reason}")
        lines.append("")
        lines.append("⛔ SCENE FAILED: Blockout objects detected!")
    else:
        lines.append("✅ SCENE PASSED: All objects meet quality standards.")

    lines.append("===================================")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# AUTO-FIX SUGGESTIONS
# ═══════════════════════════════════════════════════════════════


def suggest_fixes(obj: bpy.types.Object) -> list[str]:
    """
    Sugerir mejoras para un objeto blockout.

    Args:
        obj: Objeto a evaluar

    Returns:
        Lista de sugerencias
    """
    suggestions = []
    check = is_blockout(obj)

    if not check["is_blockout"]:
        return ["Object is not blockout. No fixes needed."]

    # Sugerir biselado
    has_bevel = any(m.type == "BEVEL" for m in obj.modifiers)
    if not has_bevel:
        suggestions.append("Add Bevel modifier (1-2 segments, 0.02 width)")

    # Sugerir material
    if not obj.data.materials:
        suggestions.append("Add PBR material (wood, metal, fabric, etc.)")

    # Sugerir smooth shading
    if obj.type == "MESH" and len(obj.data.polygons) > 4:
        smooth_count = sum(1 for p in obj.data.polygons if p.use_smooth)
        if smooth_count == 0:
            suggestions.append("Apply Shade Auto Smooth")

    # Sugerir más detalles
    vert_count = len(obj.data.vertices) if obj.type == "MESH" else 0
    if vert_count < 20:
        suggestions.append("Add more geometry (subdivide or extrude)")

    # Sugerir UV unwrap
    if obj.type == "MESH" and not obj.data.uv_layers:
        suggestions.append("Apply Smart UV Unwrap")

    return suggestions


def auto_fix_blockout(obj: bpy.types.Object) -> dict[str, any]:
    """
    Intentar auto-corregir un objeto blockout.

    Args:
        obj: Objeto a corregir

    Returns:
        Dict con correcciones aplicadas
    """
    fixes_applied = []

    try:
        # 1. Agregar biselado si no tiene
        has_bevel = any(m.type == "BEVEL" for m in obj.modifiers)
        if not has_bevel and obj.type == "MESH":
            mod = obj.modifiers.new(name="AntiBlockout_Bevel", type="BEVEL")
            mod.width = 0.02
            mod.segments = 2
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
            fixes_applied.append("Added Bevel modifier")

        # 2. Aplicar sombreado suave
        if obj.type == "MESH" and len(obj.data.polygons) > 4:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.shade_smooth()
            fixes_applied.append("Applied Shade Smooth")

        # 3. Agregar material PBR básico si no tiene
        if obj.type == "MESH" and not obj.data.materials:
            mat = bpy.data.materials.new(name=f"AntiBlockout_Mat_{obj.name}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Roughness"].default_value = 0.6
            obj.data.materials.append(mat)
            fixes_applied.append("Added basic PBR material")

        # 4. Smart UV Unwrap
        if obj.type == "MESH" and not obj.data.uv_layers:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
            bpy.ops.object.mode_set(mode="OBJECT")
            fixes_applied.append("Applied Smart UV Unwrap")

        print(f"[anti-blockout] Fixed {obj.name}: {fixes_applied}")

    except Exception as e:
        print(f"[anti-blockout] Auto-fix failed for {obj.name}: {e}")

    return {
        "object_name": obj.name,
        "fixes_applied": fixes_applied,
        "total_fixes": len(fixes_applied),
    }
