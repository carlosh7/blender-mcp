"""
blender-mcp — Scene Analysis Handler
Inspired by official blender.org MCP: scene analysis and data-block introspection.
"""
import bpy
import base64
import tempfile
import os
from . import BaseHandler


class AnalysisHandler(BaseHandler):
    """Scene and data-block analysis: object summaries, detail inspection, blendfile audit."""

    namespace = "analysis"

    @staticmethod
    def cmd_get_objects_summary():
        objects = []
        for obj in bpy.context.scene.objects:
            objects.append({
                "name": obj.name,
                "type": obj.type,
                "location": [round(float(obj.location.x), 2), round(float(obj.location.y), 2), round(float(obj.location.z), 2)],
                "dimensions": [round(float(d), 3) for d in obj.dimensions],
                "visible": obj.visible_get(),
            })
        return {
            "total": len(objects),
            "objects": objects,
        }

    @staticmethod
    def cmd_get_object_detail_summary(name=""):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        info = {
            "name": obj.name,
            "type": obj.type,
            "location": [obj.location.x, obj.location.y, obj.location.z],
            "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
            "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            "dimensions": [float(d) for d in obj.dimensions],
            "visible": obj.visible_get(),
            "selectable": obj.hide_select,
            "collections": [c.name for c in obj.users_collection],
            "materials": [s.material.name for s in obj.material_slots if s.material],
            "modifiers": [],
            "parent": obj.parent.name if obj.parent else None,
            "children": [c.name for c in obj.children],
            "data": None,
        }
        for mod in obj.modifiers:
            info["modifiers"].append({
                "name": mod.name,
                "type": mod.type,
                "enabled": not mod.show_viewport,
            })
        if obj.type == 'MESH' and obj.data:
            mesh = obj.data
            info["data"] = {
                "type": "MESH",
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
                "uv_layers": len(mesh.uv_layers),
                "vertex_colors": len(mesh.vertex_colors),
            }
        elif obj.type == 'LIGHT' and obj.data:
            light = obj.data
            info["data"] = {
                "type": "LIGHT",
                "light_type": light.type,
                "energy": light.energy,
                "color": list(light.color),
            }
        elif obj.type == 'CAMERA' and obj.data:
            cam = obj.data
            info["data"] = {
                "type": "CAMERA",
                "lens": cam.lens,
                "sensor_width": cam.sensor_width,
                "clip_start": cam.clip_start,
                "clip_end": cam.clip_end,
            }
        return info

    @staticmethod
    def cmd_get_blendfile_summary_datablocks():
        data_attrs = [
            "scenes", "objects", "meshes", "materials",
            "textures", "images", "lights", "cameras",
            "collections", "actions", "node_groups", "worlds",
            "grease_pencils", "curves", "lattices", "armatures",
            "speakers", "linestyles", "movieclips", "sounds",
            "fonts", "brushes", "workspaces", "screens",
            "libraries", "masks",
        ]
        summary = {}
        for attr in data_attrs:
            try:
                summary[attr] = len(getattr(bpy.data, attr))
            except AttributeError:
                summary[attr] = 0
        return {"data_blocks": summary}

    @staticmethod
    def cmd_get_screenshot_as_base64(max_size=800):
        filepath = os.path.join(tempfile.gettempdir(), f"blender_mcp_shot_{int(time.time())}.png")
        try:
            area = next((a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'), None)
            if not area:
                return {"error": "No 3D viewport found"}
            with bpy.context.temp_override(area=area):
                bpy.ops.screen.screenshot_area(filepath=filepath)
            with open(filepath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            os.unlink(filepath)
            return {"base64": b64, "mime": "image/png"}
        except Exception as e:
            return {"error": str(e)}
