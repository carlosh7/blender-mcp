"""
blender-mcp — Scene Handler
"""
import bpy
from . import BaseHandler


class SceneHandler(BaseHandler):
    """Scene inspection: objects, counts, names, materials."""

    namespace = "scene"

    @staticmethod
    def cmd_get_scene_info():
        info = {
            "name": bpy.context.scene.name,
            "object_count": len(bpy.context.scene.objects),
            "materials_count": len(bpy.data.materials),
            "objects": [],
        }
        for i, obj in enumerate(bpy.context.scene.objects):
            if i >= 20:
                break
            info["objects"].append({
                "name": obj.name,
                "type": obj.type,
                "location": [round(float(obj.location.x), 2), round(float(obj.location.y), 2), round(float(obj.location.z), 2)],
            })
        return info

    @staticmethod
    def cmd_get_object_info(name=""):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        info = {
            "name": obj.name,
            "type": obj.type,
            "location": [obj.location.x, obj.location.y, obj.location.z],
            "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
            "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            "visible": obj.visible_get(),
            "materials": [s.material.name for s in obj.material_slots if s.material],
        }
        if obj.type == 'MESH' and obj.data:
            mesh = obj.data
            info["mesh"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
            }
        return info

    @staticmethod
    def cmd_ping():
        return {"pong": True}

    @staticmethod
    def cmd_execute_code(code=""):
        import io
        from contextlib import redirect_stdout
        ns = {"bpy": bpy, "C": bpy.context, "D": bpy.data, "ops": bpy.ops}
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(code, ns)
        return {"output": buf.getvalue()}
