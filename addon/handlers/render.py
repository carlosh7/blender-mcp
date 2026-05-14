"""
blender-mcp — Render Handler
Engine settings, resolution, output, render to file.
"""
import bpy
import os
from . import BaseHandler


class RenderHandler(BaseHandler):
    """Configure render settings and execute renders."""

    namespace = "render"

    @staticmethod
    def cmd_set_render_engine(engine="CYCLES"):
        engines = {"CYCLES": "CYCLES", "EEVEE": "BLENDER_EEVEE", "WORKBENCH": "BLENDER_WORKBENCH"}
        bpy_type = engines.get(engine.upper())
        if not bpy_type:
            return {"error": f"Unknown engine: {engine}"}
        bpy.context.scene.render.engine = bpy_type
        return {"engine": engine}

    @staticmethod
    def cmd_set_render_resolution(width=1920, height=1080, percentage=100):
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.resolution_percentage = percentage
        return {"width": width, "height": height, "percentage": percentage}

    @staticmethod
    def cmd_set_render_samples(samples=128):
        scene = bpy.context.scene
        if scene.render.engine == 'CYCLES':
            scene.cycles.samples = samples
        return {"samples": samples}

    @staticmethod
    def cmd_set_render_output(filepath="", format="PNG"):
        scene = bpy.context.scene
        if filepath:
            scene.render.filepath = filepath
        fmts = {"PNG": "PNG", "JPEG": "JPEG", "TIFF": "TIFF", "OPEN_EXR": "OPEN_EXR", "AVI_JPEG": "AVI_JPEG", "FFMPEG": "FFMPEG"}
        scene.render.image_settings.file_format = fmts.get(format.upper(), "PNG")
        return {"filepath": scene.render.filepath, "format": format}

    @staticmethod
    def cmd_render_frame(filepath=""):
        if filepath:
            bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        return {"rendered": bpy.context.scene.render.filepath}

    @staticmethod
    def cmd_render_viewport_to_path(filepath=""):
        if not filepath:
            return {"error": "Provide a filepath to save the render."}
        bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        return {"rendered": filepath, "exists": os.path.exists(filepath)}

    @staticmethod
    def cmd_render_animation(filepath=""):
        if filepath:
            bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(animation=True)
        return {"rendered_animation": True}

    @staticmethod
    def cmd_set_cycles_device(device="GPU"):
        scene = bpy.context.scene
        if scene.render.engine == 'CYCLES':
            if device.upper() == "GPU":
                scene.cycles.device = 'GPU'
            else:
                scene.cycles.device = 'CPU'
        return {"device": device}

    @staticmethod
    def cmd_set_color_management(view_transform="Standard", look="None"):
        scene = bpy.context.scene
        scene.view_settings.view_transform = view_transform
        scene.view_settings.look = look
        return {"view_transform": view_transform, "look": look}
