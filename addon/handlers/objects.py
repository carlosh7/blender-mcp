"""
blender-mcp — Objects Handler
"""
import bpy
import mathutils
from . import BaseHandler


class ObjectsHandler(BaseHandler):
    """Create, modify, delete, and transform 3D objects."""

    namespace = "objects"

    @staticmethod
    def cmd_create_object(type="CUBE", name="", location=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0), rotation=(0.0, 0.0, 0.0)):
        type_map = {
            "CUBE": "primitive_cube_add",
            "SPHERE": "primitive_uv_sphere_add",
            "CYLINDER": "primitive_cylinder_add",
            "CONE": "primitive_cone_add",
            "TORUS": "primitive_torus_add",
            "PLANE": "primitive_plane_add",
            "MONKEY": "primitive_monkey_add",
            "CIRCLE": "primitive_circle_add",
        }
        op = type_map.get(type.upper())
        if not op:
            return {"error": f"Unknown type: {type}. Use: {', '.join(type_map.keys())}"}

        getattr(bpy.ops.mesh, op)(location=location)
        obj = bpy.context.active_object
        if name:
            obj.name = name
        obj.scale = scale
        obj.rotation_euler = rotation
        return {"name": obj.name, "type": obj.type, "location": list(obj.location)}

    @staticmethod
    def cmd_delete_object(name=""):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"deleted": name}

    @staticmethod
    def cmd_transform_object(name="", location=None, rotation=None, scale=None):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        if location:
            obj.location = location
        if rotation:
            obj.rotation_euler = rotation
        if scale:
            obj.scale = scale
        return {"name": obj.name, "location": list(obj.location)}

    @staticmethod
    def cmd_duplicate_object(name="", new_name=""):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        bpy.context.collection.objects.link(new_obj)
        if new_name:
            new_obj.name = new_name
        return {"name": new_obj.name, "duplicated_from": name}

    @staticmethod
    def cmd_select_object(name="", deselect_others=True):
        if deselect_others:
            bpy.ops.object.select_all(action='DESELECT')
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return {"selected": name}
