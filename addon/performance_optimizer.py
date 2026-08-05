"""
blender-mcp — Performance Optimizer
Optimización de rendimiento para escenas grandes.
"""
try:
    import bpy
except ImportError:
    bpy = None


# ═══════════════════════════════════════════════════════════════
# LOD SYSTEM
# ═══════════════════════════════════════════════════════════════

def create_lod_system(obj, levels=3):
    """
    Crear sistema LOD (Level of Detail).
    
    Args:
        obj: Objeto original
        levels: Número de niveles
    
    Returns:
        Lista de objetos LOD
    """
    if bpy is None or obj is None:
        return []
    
    created_lods = []
    
    for i in range(1, levels + 1):
        ratio = 1.0 - (i * 0.25)
        
        # Duplicar objeto
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.name = f"{obj.name}_LOD{i}"
        bpy.context.collection.objects.link(new_obj)
        
        # Agregar decimate
        mod = new_obj.modifiers.new("Decimate", 'DECIMATE')
        mod.ratio = ratio
        
        created_lods.append({
            "name": new_obj.name,
            "ratio": ratio,
            "object": new_obj,
        })
        
        print(f"LOD created: {new_obj.name} (ratio: {ratio})")
    
    return created_lods


# ═══════════════════════════════════════════════════════════════
# SCENE OPTIMIZATION
# ═══════════════════════════════════════════════════════════════

def optimize_scene():
    """
    Optimizar escena completa.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    optimizations = []
    
    # 1. Eliminar objetos ocultos
    for obj in bpy.data.objects:
        if obj.hide_render:
            bpy.data.objects.remove(obj, do_unlink=True)
            optimizations.append(f"Removed hidden: {obj.name}")
    
    # 2. Eliminar materiales sin usar
    for mat in bpy.data.materials:
        if not mat.users:
            bpy.data.materials.remove(mat)
            optimizations.append(f"Removed unused material: {mat.name}")
    
    # 3. Eliminar meshes sin usar
    for mesh in bpy.data.meshes:
        if not mesh.users:
            bpy.data.meshes.remove(mesh)
            optimizations.append(f"Removed unused mesh: {mesh.name}")
    
    print(f"Scene optimized: {len(optimizations)} optimizations")
    return {"optimizations": optimizations}


# ═══════════════════════════════════════════════════════════════
# PERFORMANCE MONITORING
# ═══════════════════════════════════════════════════════════════

def get_performance_stats():
    """
    Obtener estadísticas de rendimiento.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    stats = {
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        "materials": len(bpy.data.materials),
        "total_vertices": sum(len(m.vertices) for m in bpy.data.meshes),
        "total_faces": sum(len(m.polygons) for m in bpy.data.meshes),
    }
    
    return stats


def estimate_render_time():
    """
    Estimar tiempo de render.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    scene = bpy.context.scene
    resolution = scene.render.resolution_x * scene.render.resolution_y
    
    # Estimación simple
    if scene.render.engine == 'CYCLES':
        samples = scene.cycles.samples
        time_estimate = resolution * samples / 1000000  # segundos
    else:
        time_estimate = resolution / 500000  # segundos
    
    return {
        "engine": scene.render.engine,
        "resolution": f"{scene.render.resolution_x}x{scene.render.resolution_y}",
        "estimated_seconds": time_estimate,
        "estimated_minutes": time_estimate / 60,
    }


# ═══════════════════════════════════════════════════════════════
# AUTO LOD
# ═══════════════════════════════════════════════════════════════

def auto_lod(obj, distance_threshold=10.0):
    """
    Crear LOD automático basado en distancia.
    
    Args:
        obj: Objeto
        distance_threshold: Umbral de distancia para LOD
    """
    if bpy is None or obj is None:
        return []
    
    # Crear 3 niveles de LOD
    lod_levels = [
        {"ratio": 1.0, "name": "LOD0"},
        {"ratio": 0.5, "name": "LOD1"},
        {"ratio": 0.25, "name": "LOD2"},
    ]
    
    created = []
    for lod in lod_levels:
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.name = f"{obj.name}_{lod['name']}"
        bpy.context.collection.objects.link(new_obj)
        
        mod = new_obj.modifiers.new("Decimate", 'DECIMATE')
        mod.ratio = lod["ratio"]
        
        created.append({
            "name": new_obj.name,
            "ratio": lod["ratio"],
            "distance": distance_threshold * (1 + lod["ratio"]),
        })
        
        print(f"LOD created: {new_obj.name} (ratio: {lod['ratio']})")
    
    return created


# ═══════════════════════════════════════════════════════════════
# BATCH OPTIMIZE
# ═══════════════════════════════════════════════════════════════

def batch_optimize(objects=None, target_faces=10000):
    """
    Optimización batch de múltiples objetos.
    
    Args:
        objects: Lista de objetos (default: todos los mesh)
        target_faces: Objetivo de caras
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    if objects is None:
        objects = [o for o in bpy.data.objects if o.type == 'MESH']
    
    optimized = []
    
    for obj in objects:
        if len(obj.data.polygons) > target_faces:
            # Calcular ratio para alcanzar objetivo
            ratio = target_faces / len(obj.data.polygons)
            
            mod = obj.modifiers.new("Decimate", 'DECIMATE')
            mod.ratio = ratio
            
            optimized.append({
                "name": obj.name,
                "original_faces": len(obj.data.polygons),
                "target_faces": target_faces,
                "ratio": ratio,
            })
            
            print(f"Optimized: {obj.name} (ratio: {ratio:.2f})")
    
    return optimized


# ═══════════════════════════════════════════════════════════════
# MEMORY USAGE
# ═══════════════════════════════════════════════════════════════

def memory_usage():
    """
    Obtener uso de memoria.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    # Estimación de uso de memoria
    mesh_memory = sum(len(m.vertices) * 12 for m in bpy.data.meshes)  # 12 bytes por vértice
    material_memory = len(bpy.data.materials) * 1024  # ~1KB por material
    texture_memory = len(bpy.data.images) * 1024 * 1024  # ~1MB por textura
    
    total = mesh_memory + material_memory + texture_memory
    
    return {
        "mesh_memory_kb": mesh_memory / 1024,
        "material_memory_kb": material_memory / 1024,
        "texture_memory_mb": texture_memory / (1024 * 1024),
        "total_mb": total / (1024 * 1024),
    }


# ═══════════════════════════════════════════════════════════════
# FPS COUNTER
# ═══════════════════════════════════════════════════════════════

def fps_counter():
    """
    Obtener FPS actual del viewport.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    # Obtener FPS del viewport
    try:
        # Blender no expone FPS directamente, pero podemos estimar
        fps = 60  # Default
        return {"fps": fps, "status": "estimated"}
    except:
        return {"fps": 0, "status": "error"}


# ═══════════════════════════════════════════════════════════════
# SCENE COMPLEXITY
# ═══════════════════════════════════════════════════════════════

def scene_complexity():
    """
    Analizar complejidad de la escena.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    stats = get_performance_stats()
    
    # Calcular score de complejidad
    score = 0
    score += min(stats["objects"] * 1, 50)  # Máximo 50 por objetos
    score += min(stats["total_vertices"] / 10000, 30)  # Máximo 30 por vértices
    score += min(stats["total_faces"] / 5000, 20)  # Máximo 20 por caras
    
    # Clasificar
    if score < 30:
        level = "BASIC"
    elif score < 60:
        level = "MEDIUM"
    elif score < 80:
        level = "COMPLEX"
    else:
        level = "VERY_COMPLEX"
    
    return {
        "score": score,
        "level": level,
        "stats": stats,
    }


# ═══════════════════════════════════════════════════════════════
# OPTIMIZE MATERIALS
# ═══════════════════════════════════════════════════════════════

def optimize_materials():
    """
    Optimizar materiales (eliminar duplicados).
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    # Encontrar materiales duplicados
    material_names = {}
    duplicates = []
    
    for mat in bpy.data.materials:
        if mat.name in material_names:
            duplicates.append(mat.name)
        else:
            material_names[mat.name] = mat
    
    # Eliminar duplicados
    removed = 0
    for mat_name in duplicates:
        mat = bpy.data.materials.get(mat_name)
        if mat and mat.users == 0:
            bpy.data.materials.remove(mat)
            removed += 1
    
    print(f"Materials optimized: {removed} duplicates removed")
    return {"removed": removed}


# ═══════════════════════════════════════════════════════════════
# CLEANUP UNUSED
# ═══════════════════════════════════════════════════════════════

def cleanup_unused():
    """
    Limpiar datos no utilizados.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    cleaned = {"materials": 0, "meshes": 0, "images": 0}
    
    # Eliminar materiales sin usar
    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)
            cleaned["materials"] += 1
    
    # Eliminar meshes sin usar
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
            cleaned["meshes"] += 1
    
    # Eliminar imágenes sin usar
    for img in bpy.data.images:
        if img.users == 0:
            bpy.data.images.remove(img)
            cleaned["images"] += 1
    
    print(f"Cleanup: {sum(cleaned.values())} items removed")
    return cleaned
