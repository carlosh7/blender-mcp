"""
blender-mcp — Perception Advanced Engine
Motor de percepción avanzada: Escáner, Quality Check, Reference Compare.
"""
try:
    import bpy
except ImportError:
    bpy = None

import json
import os


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
        
        if obj.type == 'MESH':
            obj_data["vertices"] = len(obj.data.vertices)
            obj_data["faces"] = len(obj.data.polygons)
            obj_data["has_material"] = bool(obj.data.materials)
            obj_data["has_smooth"] = any(p.use_smooth for p in obj.data.polygons)
        
        objects.append(obj_data)
    
    # Estadísticas
    stats = {
        "total_objects": len(objects),
        "meshes": len([o for o in objects if o["type"] == 'MESH']),
        "lights": len([o for o in objects if o["type"] == 'LIGHT']),
        "cameras": len([o for o in objects if o["type"] == 'CAMERA']),
        "materials": len(bpy.data.materials),
    }
    
    return {
        "objects": objects,
        "stats": stats,
        "timestamp": str(bpy.context.scene.frame_current),
    }


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
        if obj.type == 'MESH':
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
    total = len([o for o in scene.objects if o.type == 'MESH'])
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
            "message": f"Screenshot saved: {filepath}"
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
    }
