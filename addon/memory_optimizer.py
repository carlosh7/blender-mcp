"""
blender-mcp — Memory Optimization
Optimización de memoria y monitoreo de uso.
"""
import bpy
import sys
from typing import Dict, List
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# MEMORY MONITOR
# ═══════════════════════════════════════════════════════════════

def get_detailed_memory_usage() -> Dict[str, any]:
    """
    Obtener uso detallado de memoria.
    
    Returns:
        Dict con estadísticas de memoria
    """
    # Blender data blocks
    meshes = len(bpy.data.meshes)
    materials = len(bpy.data.materials)
    textures = len(bpy.data.textures)
    images = len(bpy.data.images)
    objects = len(bpy.data.objects)
    
    # Count users per block
    mesh_users = sum(m.users for m in bpy.data.meshes)
    mat_users = sum(m.users for m in bpy.data.materials)
    
    # Orphan blocks
    orphan_meshes = sum(1 for m in bpy.data.meshes if m.users == 0)
    orphan_materials = sum(1 for m in bpy.data.materials if m.users == 0)
    orphan_textures = sum(1 for t in bpy.data.textures if t.users == 0)
    orphan_images = sum(1 for i in bpy.data.images if i.users == 0)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "data_blocks": {
            "meshes": meshes,
            "materials": materials,
            "textures": textures,
            "images": images,
            "objects": objects,
        },
        "users": {
            "mesh_users": mesh_users,
            "material_users": mat_users,
        },
        "orphans": {
            "meshes": orphan_meshes,
            "materials": orphan_materials,
            "textures": orphan_textures,
            "images": orphan_images,
            "total": orphan_meshes + orphan_materials + orphan_textures + orphan_images,
        },
        "python": {
            "objects_in_memory": sys.getsizeof(bpy.data.objects),
            "materials_in_memory": sys.getsizeof(bpy.data.materials),
        },
    }


# ═══════════════════════════════════════════════════════════════
# OPTIMIZATION
# ═══════════════════════════════════════════════════════════════

def optimize_scene() -> Dict[str, any]:
    """
    Optimizar escena completa.
    
    Returns:
        Dict con optimizaciones realizadas
    """
    results = {
        "merged_vertices": 0,
        "removed_objects": 0,
        "orphan_blocks_purged": 0,
    }
    
    # 1. Merge by distance
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            before_verts = len(obj.data.vertices)
            
            try:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles(threshold=0.0001)
                bpy.ops.object.mode_set(mode='OBJECT')
                
                after_verts = len(obj.data.vertices)
                results["merged_vertices"] += before_verts - after_verts
            except Exception as e:
                print(f"[optimize] Merge failed for {obj.name}: {e}")
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except Exception:
                    pass
            
            obj.select_set(False)
    
    # 2. Purge orphan data
    try:
        before = len(bpy.data.meshes) + len(bpy.data.materials)
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True,
            do_linked_ids=True,
            do_recursive=True
        )
        after = len(bpy.data.meshes) + len(bpy.data.materials)
        results["orphan_blocks_purged"] = before - after
    except Exception as e:
        print(f"[optimize] Orphan purge failed: {e}")
    
    # 3. Remove default objects
    default_names = {'Cube', 'Sphere', 'Cylinder', 'Cone', 'Plane'}
    for obj in list(bpy.context.scene.objects):
        if obj.name in default_names and obj.location == (0, 0, 0):
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
                results["removed_objects"] += 1
            except Exception:
                pass
    
    print(f"[optimize] Scene optimized: {results}")
    return results


def get_memory_report() -> str:
    """
    Generar reporte legible de memoria.
    
    Returns:
        String con reporte formateado
    """
    usage = get_detailed_memory_usage()
    
    lines = [
        "=== MEMORY REPORT ===",
        f"Timestamp: {usage['timestamp']}",
        "",
        "--- DATA BLOCKS ---",
        f"  Meshes: {usage['data_blocks']['meshes']}",
        f"  Materials: {usage['data_blocks']['materials']}",
        f"  Textures: {usage['data_blocks']['textures']}",
        f"  Images: {usage['data_blocks']['images']}",
        f"  Objects: {usage['data_blocks']['objects']}",
        "",
        "--- USERS ---",
        f"  Mesh users: {usage['users']['mesh_users']}",
        f"  Material users: {usage['users']['material_users']}",
        "",
        "--- ORPHAN BLOCKS ---",
        f"  Meshes: {usage['orphans']['meshes']}",
        f"  Materials: {usage['orphans']['materials']}",
        f"  Textures: {usage['orphans']['textures']}",
        f"  Images: {usage['orphans']['images']}",
        f"  Total: {usage['orphans']['total']}",
        "=======================",
    ]
    
    return "\n".join(lines)
