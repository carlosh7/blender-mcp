"""
blender-mcp — Export Engine
Sistema de exportación: Game Engines, Web, Print, Film, LOD.
"""
try:
    import bpy
except ImportError:
    bpy = None
import os
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# EXPORTACIÓN A GAME ENGINES
# ═══════════════════════════════════════════════════════════════

def export_to_unity(filepath, selected_only=False):
    """
    Exportar para Unity (FBX).
    
    Args:
        filepath: Ruta de salida
        selected_only: Exportar solo selección
    """
    try:
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=selected_only,
            apply_scale_options='FBX_SCALE_ALL',
            mesh_smooth_type='OFF',
            path_mode='COPY',
            embed_textures=True
        )
        size = os.path.getsize(filepath)
        print(f"Exportado para Unity: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_to_unreal(filepath, selected_only=False):
    """
    Exportar para Unreal Engine (FBX).
    """
    try:
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=selected_only,
            apply_scale_options='FBX_SCALE_ALL',
            mesh_smooth_type='OFF',
            path_mode='COPY',
            embed_textures=True,
            use_mesh_modifiers=True
        )
        size = os.path.getsize(filepath)
        print(f"Exportado para Unreal: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_to_godot(filepath, selected_only=False):
    """
    Exportar para Godot (glTF).
    """
    return export_to_gltf(filepath, selected_only)


# ═══════════════════════════════════════════════════════════════
# EXPORTACIÓN A WEB/AR/VR
# ═══════════════════════════════════════════════════════════════

def export_to_gltf(filepath, selected_only=False):
    """
    Exportar a glTF/GLB (web, AR, VR).
    """
    try:
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB',
            use_selection=selected_only
        )
        size = os.path.getsize(filepath)
        print(f"Exportado glTF: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_to_usd(filepath, selected_only=False):
    """
    Exportar a USD (Apple Vision Pro, Pixar).
    """
    try:
        bpy.ops.wm.usd_export(
            filepath=filepath,
            export_selected_objects=selected_only
        )
        size = os.path.getsize(filepath)
        print(f"Exportado USD: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# EXPORTACIÓN A IMPRESIÓN 3D
# ═══════════════════════════════════════════════════════════════

def export_to_stl(filepath, selected_only=False):
    """
    Exportar a STL (impresión 3D).
    """
    try:
        bpy.ops.export_mesh.stl(
            filepath=filepath,
            use_selection=selected_only
        )
        size = os.path.getsize(filepath)
        print(f"Exportado STL: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_to_obj(filepath, selected_only=False):
    """
    Exportar a OBJ (universal).
    """
    try:
        bpy.ops.export_scene.obj(
            filepath=filepath,
            use_selection=selected_only
        )
        size = os.path.getsize(filepath)
        print(f"Exportado OBJ: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# EXPORTACIÓN A PELÍCULAS
# ═══════════════════════════════════════════════════════════════

def export_to_alembic(filepath, selected_only=False):
    """
    Exportar a Alembic (películas, efectos).
    """
    try:
        bpy.ops.export_scene.alembic(
            filepath=filepath,
            use_selection=selected_only
        )
        size = os.path.getsize(filepath)
        print(f"Exportado Alembic: {filepath} ({size/1024:.1f} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# LOD SYSTEM (Level of Detail)
# ═══════════════════════════════════════════════════════════════

def create_lod(obj, lod_levels=None):
    """
    Crear niveles de detail (LOD) automático.
    
    Args:
        obj: Objeto original
        lod_levels: Lista de niveles [{'ratio': 0.5, 'name': 'LOD1'}, ...]
    
    Returns:
        Lista de objetos LOD creados
    """
    if lod_levels is None:
        lod_levels = [
            {"ratio": 0.75, "name": "LOD1"},
            {"ratio": 0.5, "name": "LOD2"},
            {"ratio": 0.25, "name": "LOD3"},
        ]
    
    created_lods = []
    
    for lod in lod_levels:
        # Duplicar objeto
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.name = f"{obj.name}_{lod['name']}"
        bpy.context.collection.objects.link(new_obj)
        
        # Aplicar decimate para reducir polígonos
        mod = new_obj.modifiers.new("Decimate", 'DECIMATE')
        mod.ratio = lod["ratio"]
        
        created_lods.append({
            "name": new_obj.name,
            "ratio": lod["ratio"],
            "object": new_obj
        })
        
        print(f"LOD creado: {new_obj.name} (ratio: {lod['ratio']})")
    
    return created_lods


def auto_lod(obj, levels=3):
    """
    Crear LODs automáticos.
    """
    lod_levels = []
    for i in range(1, levels + 1):
        ratio = 1.0 - (i * 0.25)
        lod_levels.append({
            "ratio": ratio,
            "name": f"LOD{i}"
        })
    
    return create_lod(obj, lod_levels)


# ═══════════════════════════════════════════════════════════════
# EXPORTACIÓN INTELIGENTE
# ═══════════════════════════════════════════════════════════════

def smart_export(filepath, target="auto", selected_only=False):
    """
    Exportación inteligente - elige el mejor formato automáticamente.
    
    Args:
        filepath: Ruta de salida
        target: 'unity', 'unreal', 'godot', 'web', 'print', 'film', 'auto'
        selected_only: Exportar solo selección
    """
    if target == "auto":
        # Auto-detectar basado en extensión
        ext = Path(filepath).suffix.lower()
        
        if ext in ['.fbx']:
            target = "unity"
        elif ext in ['.glb', '.gltf']:
            target = "web"
        elif ext in ['.stl']:
            target = "print"
        elif ext in ['.obj']:
            target = "universal"
        elif ext in ['.usd', '.usda', '.usdc']:
            target = "film"
        else:
            target = "unity"
    
    # Exportar según target
    export_map = {
        "unity": export_to_unity,
        "unreal": export_to_unreal,
        "godot": export_to_godot,
        "web": export_to_gltf,
        "print": export_to_stl,
        "universal": export_to_obj,
        "film": export_to_alembic,
    }
    
    exporter = export_map.get(target)
    if exporter:
        return exporter(filepath, selected_only)
    else:
        return {"success": False, "error": f"Target no soportado: {target}"}


def export_all_formats(directory, prefix="model", selected_only=False):
    """
    Exportar a todos los formatos disponibles.
    """
    results = {}
    
    formats = {
        "FBX": (f"{prefix}.fbx", export_to_unity),
        "glTF": (f"{prefix}.glb", export_to_gltf),
        "STL": (f"{prefix}.stl", export_to_stl),
        "OBJ": (f"{prefix}.obj", export_to_obj),
    }
    
    for fmt, (filename, exporter) in formats.items():
        filepath = os.path.join(directory, filename)
        results[fmt] = exporter(filepath, selected_only)
    
    return results


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_export_formats():
    """Listar formatos de exportación disponibles"""
    return {
        "FBX": {"ext": ".fbx", "targets": ["Unity", "Unreal"], "desc": "Game engines"},
        "glTF": {"ext": ".glb", "targets": ["Web", "AR", "VR"], "desc": "Web/AR/VR"},
        "USD": {"ext": ".usd", "targets": ["Pixar", "Apple Vision Pro"], "desc": "Film/AR"},
        "STL": {"ext": ".stl", "targets": ["3D Printing"], "desc": "Impresión 3D"},
        "OBJ": {"ext": ".obj", "targets": ["Universal"], "desc": "Formato universal"},
        "Alembic": {"ext": ".abc", "targets": ["Film", "VFX"], "desc": "Películas"},
    }
