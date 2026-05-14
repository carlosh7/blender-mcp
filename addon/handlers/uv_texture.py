"""
blender-mcp — UV & Texture Handler
7 unwrap methods, texture baking, UV manipulation.
"""
import bpy
from . import BaseHandler


UNWRAP_METHODS = {
    "smart": 'SMART_PROJECT',
    "smart_project": 'SMART_PROJECT',
    "unwrap": 'ANGLE_BASED',
    "angle_based": 'ANGLE_BASED',
    "conformal": 'CONFORMAL',
    "cube": 'CUBE_PROJECTION',
    "cube_projection": 'CUBE_PROJECTION',
    "cylinder": 'CYLINDER_PROJECTION',
    "cylinder_projection": 'CYLINDER_PROJECTION',
    "sphere": 'SPHERE_PROJECTION',
    "sphere_projection": 'SPHERE_PROJECTION',
    "project": 'PROJECT',
    "project_from_view": 'PROJECT',
}


class UVTextureHandler(BaseHandler):
    """UV unwrap, texture baking, and UV manipulation."""

    namespace = "uv_texture"

    @staticmethod
    def cmd_unwrap_object(object_name="", method="smart"):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj or obj.type != 'MESH':
            return {"error": "No mesh object specified"}
        uv_method = UNWRAP_METHODS.get(method.lower().replace(" ", "_"))
        if not uv_method:
            return {"error": f"Unknown method: {method}. Options: smart, unwrap, conformal, cube, cylinder, sphere"}
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        if uv_method == 'SMART_PROJECT':
            bpy.ops.uv.smart_project()
        elif uv_method == 'CUBE_PROJECTION':
            bpy.ops.uv.cube_project()
        elif uv_method == 'CYLINDER_PROJECTION':
            bpy.ops.uv.cylinder_project()
        elif uv_method == 'SPHERE_PROJECTION':
            bpy.ops.uv.sphere_project()
        elif uv_method == 'PROJECT':
            bpy.ops.uv.project_from_view()
        else:
            bpy.ops.uv.unwrap(method=uv_method)
        bpy.ops.object.mode_set(mode='OBJECT')
        return {"object": obj.name, "method": method}

    @staticmethod
    def cmd_add_uv_map(object_name="", name=""):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj or obj.type != 'MESH':
            return {"error": "No mesh object"}
        uv = obj.data.uv_layers.new(name=name or f"UVMap_{len(obj.data.uv_layers)}")
        return {"object": obj.name, "uv_map": uv.name}

    @staticmethod
    def cmd_bake_textures(object_name="", bake_type="DIFFUSE", filepath="", resolution=1024):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj or obj.type != 'MESH':
            return {"error": "No mesh object"}
        scene = bpy.context.scene
        old_engine = scene.render.engine
        scene.render.engine = 'CYCLES'
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_selected_to_active = False
        scene.render.bake.margin = 16
        bpy.ops.object.bake(type=bake_type)
        scene.render.engine = old_engine
        return {"object": obj.name, "bake_type": bake_type}

    @staticmethod
    def cmd_list_uv_maps(object_name=""):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj or obj.type != 'MESH':
            return {"error": "No mesh object"}
        maps = [{"name": uv.name, "index": i} for i, uv in enumerate(obj.data.uv_layers)]
        return {"object": obj.name, "uv_maps": maps}
