"""
blender-mcp-ultra — VLM Feedback
Bucle visual para agentes: captura → análisis con modelo de visión → sugerencias.

Proveedores: ollama (local), openai, claude. Requiere configuración externa
(Ollama corriendo o API keys en preferencias del addon); los handlers devuelven
error claro si no está disponible.
"""

from ...core.entities import Tool, ToolCategory, ToolPermission

try:
    import bpy
except ImportError:  # fuera de Blender: solo definiciones
    bpy = None


def _vlm():
    try:
        import addon.vlm_visual as vlm

        return vlm
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"addon.vlm_visual no disponible: {e}") from e


def _has_window() -> bool:
    return bool(getattr(bpy.context, "window", None))


def capture(filepath: str = "/tmp/opencode/vlm_capture.png", resolution: int = 800) -> dict:
    """Capturar el estado visual actual (viewport en GUI; render rápido en headless)."""
    import os

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    if _has_window():
        path = _vlm().capture_viewport(filepath=filepath, resolution=int(resolution))
        if not path:
            raise RuntimeError("capture_viewport no produjo imagen")
        return {"image": path, "source": "viewport"}
    # headless: render EEVEE rápido como sustituto del viewport
    scene = bpy.context.scene
    if scene.camera is None:
        cams = [o for o in scene.objects if o.type == "CAMERA"]
        if cams:
            scene.camera = cams[0]
    old_engine = scene.render.engine
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        pass
    try:
        scene.eevee.taa_render_samples = 16
    except Exception:
        pass
    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    scene.render.engine = old_engine
    return {"image": filepath, "source": "render_eevee"}


def analyze(image_path: str, prompt: str, provider: str = "ollama") -> dict:
    """Analizar una imagen con el modelo de visión configurado."""
    result = _vlm().analyze_with_vlm(image_path, prompt, provider=provider)
    return result


def quick_check(provider: str = "ollama") -> dict:
    """Chequeo visual rápido de la escena actual."""
    return _vlm().quick_scene_check(provider=provider)


def composition_check(provider: str = "ollama") -> dict:
    return _vlm().composition_check(provider=provider)


def lighting_check(provider: str = "ollama") -> dict:
    return _vlm().lighting_check(provider=provider)


TOOLS = [
    Tool(
        "vlm.capture",
        ToolCategory.RENDER,
        "Captura visual actual (viewport en GUI, render EEVEE rápido en headless)",
        ToolPermission.WRITE,
        {"filepath": {"type": "str"}, "resolution": {"type": "int"}},
    ),
    Tool(
        "vlm.analyze",
        ToolCategory.RENDER,
        "Analizar imagen con VLM (ollama/openai/claude) según un prompt",
        ToolPermission.READ_ONLY,
        {
            "image_path": {"type": "str", "required": True},
            "prompt": {"type": "str", "required": True},
            "provider": {"type": "str"},
        },
    ),
    Tool(
        "vlm.quick_check",
        ToolCategory.RENDER,
        "Chequeo visual rápido de la escena (captura + análisis)",
        ToolPermission.READ_ONLY,
        {"provider": {"type": "str"}},
    ),
    Tool(
        "vlm.composition_check",
        ToolCategory.RENDER,
        "Análisis de composición",
        ToolPermission.READ_ONLY,
        {"provider": {"type": "str"}},
    ),
    Tool(
        "vlm.lighting_check",
        ToolCategory.RENDER,
        "Análisis de iluminación",
        ToolPermission.READ_ONLY,
        {"provider": {"type": "str"}},
    ),
]

HANDLERS = {
    "vlm.capture": capture,
    "vlm.analyze": analyze,
    "vlm.quick_check": quick_check,
    "vlm.composition_check": composition_check,
    "vlm.lighting_check": lighting_check,
}
