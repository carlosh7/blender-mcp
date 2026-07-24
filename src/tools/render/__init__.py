"""
blender-mcp-ultra — Render Tools
"""
from typing import Any, Dict
from core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool("render.render", ToolCategory.RENDER, "Render current scene", ToolPermission.WRITE,
         {"filepath": {"type": "str"}, "engine": {"type": "str"}}),
    Tool("render.viewport", ToolCategory.RENDER, "Render viewport screenshot", ToolPermission.READ_ONLY,
         {"filepath": {"type": "str"}}),
    Tool("render.settings", ToolCategory.RENDER, "Get/set render settings", ToolPermission.WRITE,
         {"engine": {"type": "str"}, "samples": {"type": "int"}, "resolution_x": {"type": "int"},
          "resolution_y": {"type": "int"}, "denoising": {"type": "bool"}}),
    Tool("render.set_engine", ToolCategory.RENDER, "Set render engine", ToolPermission.WRITE,
         {"engine": {"type": "str", "required": True}}),
    Tool("render.set_output", ToolCategory.RENDER, "Set render output path and format", ToolPermission.WRITE,
         {"filepath": {"type": "str"}, "format": {"type": "str"}}),
    Tool("render.set_cycles_settings", ToolCategory.RENDER, "Set Cycles render settings", ToolPermission.WRITE,
         {"samples": {"type": "int"}, "denoising": {"type": "bool"}, "max_bounces": {"type": "int"},
          "use_gpu": {"type": "bool"}}),
    Tool("render.set_eevee_settings", ToolCategory.RENDER, "Set EEVEE render settings", ToolPermission.WRITE,
         {"taa_render_samples": {"type": "int"}, "use_ssr": {"type": "bool"},
          "use_bloom": {"type": "bool"}}),
    Tool("render.set_filmic", ToolCategory.RENDER, "Set Filmic color management", ToolPermission.WRITE,
         {"look": {"type": "str"}, "exposure": {"type": "float"}, "gamma": {"type": "float"}}),
]

def render_scene(filepath: str = "/tmp/render.png", engine: str = None) -> Dict:
    try:
        import bpy
        if engine: bpy.context.scene.render.engine = engine
        bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        return {"success": True, "filepath": filepath}
    except ImportError: return {"error": "Blender not available"}

def viewport_screenshot(filepath: str = "/tmp/viewport.png") -> Dict:
    try:
        import bpy
        bpy.ops.screen.screenshot_area(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except ImportError: return {"error": "Blender not available"}

def get_settings(engine: str = None, samples: int = None, resolution_x: int = None,
                resolution_y: int = None, denoising: bool = None) -> Dict:
    try:
        import bpy
        s = bpy.context.scene
        if engine:
            # Map engine names for compatibility
            engine_map = {
                'BLENDER_EEVEE_NEXT': 'BLENDER_EEVEE',
                'EEVEE': 'BLENDER_EEVEE',
                'EEVEE_NEXT': 'BLENDER_EEVEE',
                'CYCLES': 'CYCLES',
            }
            s.render.engine = engine_map.get(engine, engine)
        if samples and s.render.engine == 'CYCLES': s.cycles.samples = samples
        if resolution_x: s.render.resolution_x = resolution_x
        if resolution_y: s.render.resolution_y = resolution_y
        if denoising is not None and s.render.engine == 'CYCLES': s.cycles.use_denoising = denoising
        return {"engine": s.render.engine, "resolution_x": s.render.resolution_x,
                "resolution_y": s.render.resolution_y, "samples": getattr(s.cycles, 'samples', None)}
    except ImportError: return {"error": "Blender not available"}

def set_engine(engine: str) -> Dict:
    try:
        import bpy
        bpy.context.scene.render.engine = engine
        return {"success": True, "engine": engine}
    except ImportError: return {"error": "Blender not available"}

def set_output(filepath: str = None, format: str = None) -> Dict:
    try:
        import bpy
        s = bpy.context.scene.render
        if filepath: s.filepath = filepath
        if format: s.image_settings.file_format = format
        return {"success": True, "filepath": s.filepath, "format": s.image_settings.file_format}
    except ImportError: return {"error": "Blender not available"}

def set_cycles(samples: int = None, denoising: bool = None, max_bounces: int = None, use_gpu: bool = None) -> Dict:
    try:
        import bpy
        c = bpy.context.scene.cycles
        updated = []
        if samples is not None: c.samples = samples; updated.append("samples")
        if denoising is not None: c.use_denoising = denoising; updated.append("denoising")
        if max_bounces is not None: c.max_bounces = max_bounces; updated.append("max_bounces")
        if use_gpu is not None:
            c.device = 'GPU' if use_gpu else 'CPU'
            updated.append("device")
        return {"success": True, "updated": updated}
    except ImportError: return {"error": "Blender not available"}

def set_eevee(taa_render_samples: int = None, use_ssr: bool = None, use_bloom: bool = None) -> Dict:
    try:
        import bpy
        e = bpy.context.scene.eevee
        updated = []
        if taa_render_samples is not None: e.taa_render_samples = taa_render_samples; updated.append("samples")
        if use_ssr is not None: e.use_ssr = use_ssr; updated.append("ssr")
        if use_bloom is not None:
            if hasattr(e, 'use_bloom'): e.use_bloom = use_bloom; updated.append("bloom")
        return {"success": True, "updated": updated}
    except ImportError: return {"error": "Blender not available"}

def set_filmic(look: str = None, exposure: float = None, gamma: float = None) -> Dict:
    try:
        import bpy
        v = bpy.context.scene.view_settings
        updated = []
        if look: v.look = look; updated.append("look")
        if exposure is not None: v.exposure = exposure; updated.append("exposure")
        if gamma is not None: v.gamma = gamma; updated.append("gamma")
        return {"success": True, "updated": updated}
    except ImportError: return {"error": "Blender not available"}

HANDLERS = {
    "render.render": render_scene, "render.viewport": viewport_screenshot,
    "render.settings": get_settings, "render.set_engine": set_engine,
    "render.set_output": set_output, "render.set_cycles_settings": set_cycles,
    "render.set_eevee_settings": set_eevee, "render.set_filmic": set_filmic,
}
