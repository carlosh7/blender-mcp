"""
blender-mcp — Export Advanced Engine
Motor de exportación avanzada: Batch, Game Engines, Film, Print, LOD.
"""
try:
    import bpy
except ImportError:
    bpy = None

import os


# ═══════════════════════════════════════════════════════════════
# EXPORT BATCH
# ═══════════════════════════════════════════════════════════════

def export_batch(directory, formats=None, selection_only=False):
    """
    Exportar a múltiples formatos.
    
    Args:
        directory: Directorio de salida
        formats: Lista de formatos (default: todos)
        selection_only: Exportar solo selección
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    if formats is None:
        formats = ["FBX", "GLB", "OBJ", "STL"]
    
    os.makedirs(directory, exist_ok=True)
    
    results = {}
    
    format_map = {
        "FBX": (".fbx", export_for_game_engine),
        "GLB": (".glb", export_for_web),
        "OBJ": (".obj", export_for_print),
        "STL": (".stl", export_for_print),
    }
    
    for fmt in formats:
        if fmt in format_map:
            ext, exporter = format_map[fmt]
            filepath = os.path.join(directory, f"model{ext}")
            result = exporter(filepath, selection_only)
            results[fmt] = result
    
    return results


# ═══════════════════════════════════════════════════════════════
# EXPORT FOR GAME ENGINES
# ═══════════════════════════════════════════════════════════════

def export_for_game_engine(filepath, engine="unity", selection_only=False):
    """
    Exportar optimizado para game engines.
    
    Args:
        filepath: Ruta de salida
        engine: 'unity', 'unreal', 'godot'
        selection_only: Solo selección
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    try:
        if engine in ["unity", "unreal", "godot"]:
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=selection_only,
                apply_scale_options='FBX_SCALE_ALL',
                mesh_smooth_type='OFF',
                path_mode='COPY',
                embed_textures=True
            )
        
        size = os.path.getsize(filepath)
        print(f"Exported for {engine}: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# EXPORT FOR WEB
# ═══════════════════════════════════════════════════════════════

def export_for_web(filepath, selection_only=False):
    """
    Exportar para web/AR/VR.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    try:
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB',
            use_selection=selection_only
        )
        size = os.path.getsize(filepath)
        print(f"Exported for web: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# EXPORT FOR PRINT
# ═══════════════════════════════════════════════════════════════

def export_for_print(filepath, format="STL", selection_only=False):
    """
    Exportar para impresión 3D.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    try:
        if format == "STL":
            bpy.ops.export_mesh.stl(filepath=filepath, use_selection=selection_only)
        elif format == "OBJ":
            bpy.ops.export_scene.obj(filepath=filepath, use_selection=selection_only)
        
        size = os.path.getsize(filepath)
        print(f"Exported for print ({format}): {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# EXPORT FOR FILM
# ═══════════════════════════════════════════════════════════════

def export_for_film(filepath, format="ALEMBIC", selection_only=False):
    """
    Exportar para película/VFX.
    """
    if bpy is None:
        return {"error": "bpy not available"}
    
    try:
        if format == "ALEMBIC":
            bpy.ops.export_scene.alembic(filepath=filepath, use_selection=selection_only)
        elif format == "FBX":
            bpy.ops.export_scene.fbx(filepath=filepath, use_selection=selection_only)
        
        size = os.path.getsize(filepath)
        print(f"Exported for film ({format}): {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# LOD GENERATOR
# ═══════════════════════════════════════════════════════════════

def lod_generator(obj, levels=3):
    """
    Generar niveles de detalle (LOD).
    
    Args:
        obj: Objeto original
        levels: Número de niveles
    
    Returns:
        Lista de objetos LOD creados
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
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_export_targets():
    """Listar targets de exportación"""
    return {
        "unity": "Unity (FBX)",
        "unreal": "Unreal Engine (FBX)",
        "godot": "Godot (glTF)",
        "web": "Web/AR/VR (glTF)",
        "print": "3D Print (STL/OBJ)",
        "film": "Film (Alembic/FBX)",
    }
