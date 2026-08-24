"""
blender-mcp — Export Advanced Engine (Production Grade)
Motor de exportación avanzada: Game Engine collisions (UCX_), LOD generation, Batch, Web, Print, Film.
"""

try:
    import bpy
except ImportError:
    bpy = None

import os


def generate_game_engine_collision(obj, engine="unreal"):
    """Generar malla de colisión convexa para Unreal (UCX_) o Unity (COL_)."""
    if bpy is None or obj is None or obj.type != "MESH":
        return None

    col_name = f"UCX_{obj.name}" if engine == "unreal" else f"COL_{obj.name}"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=obj.location)
    col_obj = bpy.context.active_object
    col_obj.name = col_name
    col_obj.scale = obj.dimensions
    col_obj.display_type = "WIRE"
    print(f"Colisionador de fisica {engine.upper()} generado: {col_name}")
    return col_obj


def generate_lod_levels(obj, lod_ratios=None):
    """Generar niveles de detalle (LOD0, LOD1, LOD2) usando Decimate."""
    if lod_ratios is None:
        lod_ratios = [1.0, 0.5, 0.25]
    if bpy is None or obj is None or obj.type != "MESH":
        return []

    lods = []
    for i, ratio in enumerate(lod_ratios):
        lod_obj = obj.copy()
        lod_obj.data = obj.data.copy()
        lod_obj.name = f"{obj.name}_LOD{i}"
        bpy.context.collection.objects.link(lod_obj)

        if ratio < 1.0:
            mod = lod_obj.modifiers.new("Decimate_LOD", "DECIMATE")
            mod.ratio = ratio
            bpy.context.view_layer.objects.active = lod_obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        lods.append(lod_obj)

    print(f"Generados {len(lods)} niveles LOD para {obj.name}")
    return lods


def export_batch(directory, formats=None, selection_only=False):
    """Exportar a múltiples formatos."""
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


def export_for_game_engine(filepath, engine="unity", selection_only=False):
    """Exportar optimizado para game engines."""
    if bpy is None:
        return {"error": "bpy not available"}

    try:
        if engine in ["unity", "unreal", "godot"]:
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=selection_only,
                apply_scale_options="FBX_SCALE_ALL",
                mesh_smooth_type="OFF",
                path_mode="COPY",
                embed_textures=True,
            )

        size = os.path.getsize(filepath)
        kb_size = round(size / 1024.0, 1)
        print(f"Exported for {engine}: {filepath} ({kb_size} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_for_web(filepath, selection_only=False):
    """Exportar para web/AR/VR."""
    if bpy is None:
        return {"error": "bpy not available"}

    try:
        bpy.ops.export_scene.gltf(
            filepath=filepath, export_format="GLB", use_selection=selection_only
        )
        size = os.path.getsize(filepath)
        kb_size = round(size / 1024.0, 1)
        print(f"Exported for web: {filepath} ({kb_size} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_for_print(filepath, fmt="STL", selection_only=False):
    """Exportar para impresion 3D."""
    if bpy is None:
        return {"error": "bpy not available"}

    try:
        if fmt == "STL":
            bpy.ops.export_mesh.stl(filepath=filepath, use_selection=selection_only)
        elif fmt == "OBJ":
            bpy.ops.export_scene.obj(filepath=filepath, use_selection=selection_only)

        size = os.path.getsize(filepath)
        kb_size = round(size / 1024.0, 1)
        print(f"Exported for print ({fmt}): {filepath} ({kb_size} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_for_film(filepath, fmt="ALEMBIC", selection_only=False):
    """Exportar para pelicula/VFX."""
    if bpy is None:
        return {"error": "bpy not available"}

    try:
        if fmt == "ALEMBIC":
            bpy.ops.export_scene.alembic(filepath=filepath, use_selection=selection_only)
        elif fmt == "FBX":
            bpy.ops.export_scene.fbx(filepath=filepath, use_selection=selection_only)

        size = os.path.getsize(filepath)
        kb_size = round(size / 1024.0, 1)
        print(f"Exported for film ({fmt}): {filepath} ({kb_size} KB)")
        return {"success": True, "filepath": filepath, "size": size}
    except Exception as e:
        return {"success": False, "error": str(e)}


def lod_generator(obj, levels=3):
    """Generar niveles de detalle (LOD)."""
    if bpy is None or obj is None:
        return []

    created_lods = []
    for i in range(1, levels + 1):
        ratio = 1.0 - (i * 0.25)
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.name = f"{obj.name}_LOD{i}"
        bpy.context.collection.objects.link(new_obj)

        mod = new_obj.modifiers.new("Decimate", "DECIMATE")
        mod.ratio = ratio

        created_lods.append(
            {
                "name": new_obj.name,
                "ratio": ratio,
                "object": new_obj,
            }
        )
        print(f"LOD created: {new_obj.name} (ratio: {ratio})")

    return created_lods


def list_export_targets():
    """Listar targets de exportacion"""
    return {
        "unity": "Unity (FBX)",
        "unreal": "Unreal Engine (FBX)",
        "godot": "Godot (glTF)",
        "web": "Web/AR/VR (glTF)",
        "print": "3D Print (STL/OBJ)",
        "film": "Film (Alembic/FBX)",
    }
