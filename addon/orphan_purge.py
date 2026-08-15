"""
blender-mcp — Orphan Data Purge
Limpieza automática de datos huérfanos en RAM.

Problema: Al crear/eliminar objetos, materiales y texturas quedan en memoria.
Solución: Purga periódica y bajo demanda.
"""
import bpy
from typing import Dict, List, Optional
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# ORPHAN DATA PURGE
# ═══════════════════════════════════════════════════════════════

def get_orphan_stats() -> Dict[str, int]:
    """
    Obtener estadísticas de datos huérfanos.
    
    Returns:
        Dict con conteo por tipo de dato
    """
    stats = {
        "meshes": 0,
        "materials": 0,
        "textures": 0,
        "images": 0,
        "cameras": 0,
        "lights": 0,
        "curves": 0,
        "armatures": 0,
        "actions": 0,
        "total": 0,
    }
    
    # Count meshes without users
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            stats["meshes"] += 1
    
    # Count materials without users
    for mat in bpy.data.materials:
        if mat.users == 0:
            stats["materials"] += 1
    
    # Count textures without users
    for tex in bpy.data.textures:
        if tex.users == 0:
            stats["textures"] += 1
    
    # Count images without users
    for img in bpy.data.images:
        if img.users == 0:
            stats["images"] += 1
    
    # Count cameras without users
    for cam in bpy.data.cameras:
        if cam.users == 0:
            stats["cameras"] += 1
    
    # Count lights without users
    for light in bpy.data.lights:
        if light.users == 0:
            stats["lights"] += 1
    
    # Count curves without users
    for curve in bpy.data.curves:
        if curve.users == 0:
            stats["curves"] += 1
    
    # Count armatures without users
    for arm in bpy.data.armatures:
        if arm.users == 0:
            stats["armatures"] += 1
    
    # Count actions without users
    for action in bpy.data.actions:
        if action.users == 0:
            stats["actions"] += 1
    
    stats["total"] = sum(stats.values())
    
    return stats


def purge_orphans(do_local_ids: bool = True, 
                  do_linked_ids: bool = True,
                  do_recursive: bool = True) -> Dict[str, any]:
    """
    Purgar todos los datos huérfanos.
    
    Args:
        do_local_ids: Purgar IDs locales
        do_linked_ids: Purgar IDs linked
        do_recursive: Purgar recursivamente
    
    Returns:
        Dict con resultado de la purga
    """
    # Get stats before purge
    stats_before = get_orphan_stats()
    
    try:
        # Use Blender's built-in purge
        bpy.ops.outliner.orphans_purge(
            do_local_ids=do_local_ids,
            do_linked_ids=do_linked_ids,
            do_recursive=do_recursive
        )
        
        # Get stats after purge
        stats_after = get_orphan_stats()
        
        # Calculate freed
        freed = {
            "meshes": stats_before["meshes"] - stats_after["meshes"],
            "materials": stats_before["materials"] - stats_after["materials"],
            "textures": stats_before["textures"] - stats_after["textures"],
            "images": stats_before["images"] - stats_after["images"],
            "cameras": stats_before["cameras"] - stats_after["cameras"],
            "lights": stats_before["lights"] - stats_after["lights"],
            "curves": stats_before["curves"] - stats_after["curves"],
            "armatures": stats_before["armatures"] - stats_after["armatures"],
            "actions": stats_before["actions"] - stats_after["actions"],
        }
        freed["total"] = sum(freed.values())
        
        return {
            "success": True,
            "before": stats_before,
            "after": stats_after,
            "freed": freed,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "before": stats_before,
            "timestamp": datetime.now().isoformat(),
        }


def purge_meshes() -> int:
    """Purgar solo meshes huérfanos. Retorna cantidad eliminada."""
    count = 0
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
            count += 1
    return count


def purge_materials() -> int:
    """Purgar solo materiales huérfanos. Retorna cantidad eliminada."""
    count = 0
    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materiales.remove(mat)
            count += 1
    return count


def purge_textures() -> int:
    """Purgar solo texturas huérfanas. Retorna cantidad eliminada."""
    count = 0
    for tex in bpy.data.textures:
        if tex.users == 0:
            bpy.data.textures.remove(tex)
            count += 1
    return count


def purge_images() -> int:
    """Purgar solo imágenes huérfanas. Retorna cantidad eliminada."""
    count = 0
    for img in bpy.data.images:
        if img.users == 0:
            bpy.data.images.remove(img)
            count += 1
    return count


def auto_purge_if_needed(threshold: int = 50) -> Optional[Dict]:
    """
    Purgar automáticamente si hay demasiados datos huérfanos.
    
    Args:
        threshold: Umbral para activar purga automática
    
    Returns:
        Dict con resultado o None si no se purgó
    """
    stats = get_orphan_stats()
    
    if stats["total"] > threshold:
        print(f"[orphan_purge] Auto-purging {stats['total']} orphan blocks...")
        return purge_orphans()
    
    return None


# ═══════════════════════════════════════════════════════════════
# MEMORY MONITOR
# ═══════════════════════════════════════════════════════════════

def get_memory_usage() -> Dict[str, any]:
    """
    Obtener uso de memoria de Blender.
    
    Returns:
        Dict con estadísticas de memoria
    """
    import sys
    
    # Get Python memory usage
    python_memory = sys.getsizeof(bpy.data.objects) + \
                    sys.getsizeof(bpy.data.materials) + \
                    sys.getsizeof(bpy.data.meshes)
    
    # Get orphan stats
    orphans = get_orphan_stats()
    
    return {
        "python_objects": len(bpy.data.objects),
        "python_materials": len(bpy.data.materials),
        "python_meshes": len(bpy.data.meshes),
        "orphan_blocks": orphans["total"],
        "timestamp": datetime.now().isoformat(),
    }


def get_memory_report() -> str:
    """
    Generar reporte legible de memoria.
    
    Returns:
        String con reporte formateado
    """
    stats = get_orphan_stats()
    usage = get_memory_usage()
    
    lines = [
        "=== MEMORY REPORT ===",
        f"Objects: {usage['python_objects']}",
        f"Materials: {usage['python_materials']}",
        f"Meshes: {usage['python_meshes']}",
        f"Orphan Blocks: {usage['orphan_blocks']}",
        "",
        "--- ORPHAN BREAKDOWN ---",
        f"  Meshes: {stats['meshes']}",
        f"  Materials: {stats['materials']}",
        f"  Textures: {stats['textures']}",
        f"  Images: {stats['images']}",
        f"  Cameras: {stats['cameras']}",
        f"  Lights: {stats['lights']}",
        f"  Curves: {stats['curves']}",
        f"  Armatures: {stats['armatures']}",
        f"  Actions: {stats['actions']}",
        "=======================",
    ]
    
    return "\n".join(lines)
