"""
blender-mcp — Export Manager
Exportación automática: glTF, FBX, OBJ, STL, render.

Regla de oro: SIEMPRE ofrecer exportación al finalizar.

.. DEPRECATED (v2.2): usar src/tools/io + export.for_target (addon_bridge). Se elimina en v3.0.
"""

import os
from datetime import datetime
from pathlib import Path

import bpy

# ═══════════════════════════════════════════════════════════════
# EXPORTACIÓN
# ═══════════════════════════════════════════════════════════════

EXPORT_DIR = Path("/tmp/blender_exports")


def export_glTF(filepath=None, selection_only=False):
    """
    Exportar escena a glTF/GLB.

    Args:
        filepath: Ruta de salida (default: auto-generada)
        selection_only: Exportar solo selección

    Returns:
        dict con resultado
    """
    if not filepath:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(EXPORT_DIR / f"scene_{timestamp}.glb")

    try:
        if selection_only:
            bpy.ops.export_scene.gltf(filepath=filepath, export_format="GLB", use_selection=True)
        else:
            bpy.ops.export_scene.gltf(filepath=filepath, export_format="GLB")

        size = os.path.getsize(filepath)
        print(f"[export] glTF exportado: {filepath} ({size / 1024:.1f} KB)")

        return {
            "success": True,
            "filepath": filepath,
            "size": size,
            "format": "glTF",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_FBX(filepath=None, selection_only=False):
    """
    Exportar escena a FBX.

    Args:
        filepath: Ruta de salida
        selection_only: Exportar solo selección

    Returns:
        dict con resultado
    """
    if not filepath:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(EXPORT_DIR / f"scene_{timestamp}.fbx")

    try:
        bpy.ops.export_scene.fbx(
            filepath=filepath, use_selection=selection_only, apply_scale_options="FBX_SCALE_ALL"
        )

        size = os.path.getsize(filepath)
        print(f"[export] FBX exportado: {filepath} ({size / 1024:.1f} KB)")

        return {
            "success": True,
            "filepath": filepath,
            "size": size,
            "format": "FBX",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_OBJ(filepath=None, selection_only=False):
    """
    Exportar escena a OBJ.

    Args:
        filepath: Ruta de salida
        selection_only: Exportar solo selección

    Returns:
        dict con resultado
    """
    if not filepath:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(EXPORT_DIR / f"scene_{timestamp}.obj")

    try:
        bpy.ops.export_scene.obj(filepath=filepath, use_selection=selection_only)

        size = os.path.getsize(filepath)
        print(f"[export] OBJ exportado: {filepath} ({size / 1024:.1f} KB)")

        return {
            "success": True,
            "filepath": filepath,
            "size": size,
            "format": "OBJ",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_STL(filepath=None, selection_only=False):
    """
    Exportar escena a STL (para impresión 3D).

    Args:
        filepath: Ruta de salida
        selection_only: Exportar solo selección

    Returns:
        dict con resultado
    """
    if not filepath:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(EXPORT_DIR / f"scene_{timestamp}.stl")

    try:
        bpy.ops.export_mesh.stl(filepath=filepath, use_selection=selection_only)

        size = os.path.getsize(filepath)
        print(f"[export] STL exportado: {filepath} ({size / 1024:.1f} KB)")

        return {
            "success": True,
            "filepath": filepath,
            "size": size,
            "format": "STL",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_all_formats(directory=None, selection_only=False):
    """
    Exportar a todos los formatos disponibles.

    Args:
        directory: Directorio de salida
        selection_only: Exportar solo selección

    Returns:
        dict con resultados de cada formato
    """
    if not directory:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        directory = str(EXPORT_DIR / f"export_{timestamp}")

    os.makedirs(directory, exist_ok=True)

    results = {}

    # glTF
    results["glTF"] = export_glTF(os.path.join(directory, "scene.glb"), selection_only)

    # FBX
    results["FBX"] = export_FBX(os.path.join(directory, "scene.fbx"), selection_only)

    # OBJ
    results["OBJ"] = export_OBJ(os.path.join(directory, "scene.obj"), selection_only)

    # STL
    results["STL"] = export_STL(os.path.join(directory, "scene.stl"), selection_only)

    print(f"\n[export] Exportación completa: {directory}")
    for fmt, result in results.items():
        status = "✅" if result.get("success") else "❌"
        print(f"  {status} {fmt}")

    return results


# ═══════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════


def render_image(filepath=None, engine=None, resolution=None):
    """
    Renderizar la escena actual.

    Args:
        filepath: Ruta de salida (default: auto-generada)
        engine: Motor de render (default: actual)
        resolution: Tupla (width, height)

    Returns:
        dict con resultado
    """
    scene = bpy.context.scene

    if not filepath:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(EXPORT_DIR / f"render_{timestamp}.png")

    # Configurar motor
    if engine:
        scene.render.engine = engine

    # Configurar resolución
    if resolution:
        scene.render.resolution_x = resolution[0]
        scene.render.resolution_y = resolution[1]

    # Renderizar
    scene.render.filepath = filepath
    scene.render.image_settings.file_format = "PNG"

    try:
        bpy.ops.render.render(write_still=True)

        size = os.path.getsize(filepath)
        print(f"[render] Imagen renderizada: {filepath} ({size / 1024:.1f} KB)")

        return {
            "success": True,
            "filepath": filepath,
            "size": size,
            "resolution": (scene.render.resolution_x, scene.render.resolution_y),
            "engine": scene.render.engine,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def render_preview(filepath=None, max_size=800):
    """
    Renderizar preview rápido del viewport.

    Args:
        filepath: Ruta de salida
        max_size: Tamaño máximo en píxeles

    Returns:
        dict con resultado
    """
    if not filepath:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(EXPORT_DIR / f"preview_{timestamp}.png")

    try:
        # Tomar screenshot del viewport
        bpy.ops.screen.screenshot_area(filepath=filepath)

        size = os.path.getsize(filepath)
        print(f"[render] Preview guardado: {filepath} ({size / 1024:.1f} KB)")

        return {
            "success": True,
            "filepath": filepath,
            "size": size,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_render_preset(preset):
    """
    Aplicar preset de render.

    Args:
        preset: Nombre del preset (preview, standard, high, ultra)

    Returns:
        dict con configuración aplicada
    """
    scene = bpy.context.scene

    presets = {
        "preview": {
            "engine": "BLENDER_EEVEE_NEXT",
            "resolution": (640, 480),
            "samples": 16,
        },
        "standard": {
            "engine": "BLENDER_EEVEE_NEXT",
            "resolution": (1280, 720),
            "samples": 32,
        },
        "high": {
            "engine": "BLENDER_EEVEE_NEXT",
            "resolution": (1920, 1080),
            "samples": 64,
        },
        "ultra": {
            "engine": "CYCLES",
            "resolution": (3840, 2160),
            "samples": 128,
        },
    }

    if preset not in presets:
        return {"error": f"Preset no encontrado: {preset}"}

    config = presets[preset]

    scene.render.engine = config["engine"]
    scene.render.resolution_x = config["resolution"][0]
    scene.render.resolution_y = config["resolution"][1]

    if config["engine"] == "CYCLES":
        scene.cycles.samples = config["samples"]
    else:
        scene.eevee.taa_render_samples = config["samples"]

    print(f"[render] Preset aplicado: {preset}")
    print(f"  Motor: {config['engine']}")
    print(f"  Resolución: {config['resolution'][0]}x{config['resolution'][1]}")
    print(f"  Samples: {config['samples']}")

    return {
        "preset": preset,
        "config": config,
    }


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def get_export_formats():
    """Obtener formatos de exportación disponibles."""
    return {
        "glTF": {"ext": ".glb", "desc": "Formato web/realidad aumentada"},
        "FBX": {"ext": ".fbx", "desc": "Formato game engines (Unity, Unreal)"},
        "OBJ": {"ext": ".obj", "desc": "Formato universal 3D"},
        "STL": {"ext": ".stl", "desc": "Formato impresión 3D"},
    }


def list_exports():
    """Listar exportaciones existentes."""
    if not EXPORT_DIR.exists():
        print("[export] No hay exportaciones")
        return []

    exports = []
    for f in sorted(EXPORT_DIR.iterdir()):
        if f.is_file():
            size = f.stat().st_size / 1024
            exports.append(
                {
                    "name": f.name,
                    "path": str(f),
                    "size_kb": size,
                }
            )
            print(f"  📄 {f.name} ({size:.1f} KB)")

    return exports
