"""
blender-mcp — Materials Handler
"""
import bpy
from . import BaseHandler


class MaterialsHandler(BaseHandler):
    """Create and apply PBR materials, colors, textures."""

    namespace = "materials"

    @staticmethod
    def cmd_create_material(name="Material", color=(0.5, 0.5, 0.5, 1.0), roughness=0.5, metallic=0.0):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        return {"name": mat.name}

    @staticmethod
    def cmd_assign_material(object_name="", material_name=""):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        return {"object": object_name, "material": material_name}

    @staticmethod
    def cmd_set_color(object_name="", color=(1.0, 0.0, 0.0, 1.0)):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        mat = bpy.data.materials.new(f"color_{object_name}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = color
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        return {"object": object_name, "color": list(color)}

    @staticmethod
    def cmd_list_materials():
        mats = []
        for mat in bpy.data.materials:
            mats.append({"name": mat.name, "users": mat.users})
        return {"materials": mats}
