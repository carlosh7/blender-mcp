"""
blender-mcp — Modifiers Handler
Apply SubSurf, Bevel, Boolean, Array, Mirror, etc.
"""
import bpy
from . import BaseHandler


MODIFIER_TYPES = {
    "subdivision_surface": "SUBSURF",
    "subsurf": "SUBSURF",
    "bevel": "BEVEL",
    "boolean": "BOOLEAN",
    "array": "ARRAY",
    "mirror": "MIRROR",
    "solidify": "SOLIDIFY",
    "screw": "SCREW",
    "wireframe": "WIREFRAME",
    "skin": "SKIN",
    "displace": "DISPLACE",
    "simple_deform": "SIMPLE_DEFORM",
    "lattice": "LATTICE",
    "cast": "CAST",
    "curve": "CURVE",
    "shrinkwrap": "SHRINKWRAP",
    "remesh": "REMESH",
    "decimate": "DECIMATE",
    "triangulate": "TRIANGULATE",
    "weld": "WELD",
    "weighted_normal": "WEIGHTED_NORMAL",
    "smooth": "SMOOTH",
    "laplacian_smooth": "LAPLACIANSMOOTH",
    "laplacian_deform": "LAPLACIANDEFORM",
    "ocean": "OCEAN",
    "particle_instance": "PARTICLE_INSTANCE",
    "explode": "EXPLODE",
    "mesh_sequence_cache": "MESH_SEQUENCE_CACHE",
    "surface_deform": "SURFACE_DEFORM",
    "mesh_to_volume": "MESH_TO_VOLUME",
    "volume_to_mesh": "VOLUME_TO_MESH",
    "grease_pencil": "GREASEPENCIL",
    "uv_project": "UV_PROJECT",
    "uv_warp": "UV_WARP",
    "vertex_weight_edit": "VERTEX_WEIGHT_EDIT",
    "vertex_weight_mix": "VERTEX_WEIGHT_MIX",
    "vertex_weight_proximity": "VERTEX_WEIGHT_PROXIMITY",
}


class ModifiersHandler(BaseHandler):
    """Apply and manage 22+ modifier types."""

    namespace = "modifiers"

    @staticmethod
    def cmd_add_modifier(object_name="", modifier_type="subsurf", **kwargs):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No active object and no object_name provided"}
        bpy_type = MODIFIER_TYPES.get(modifier_type.lower())
        if not bpy_type:
            return {"error": f"Unknown modifier: {modifier_type}. Available: {', '.join(sorted(set(m for m in MODIFIER_TYPES.values())))}"}
        mod = obj.modifiers.new(name=modifier_type.title(), type=bpy_type)
        for key, val in kwargs.items():
            if hasattr(mod, key):
                setattr(mod, key, val)
        return {"object": obj.name, "modifier": mod.name, "type": bpy_type}

    @staticmethod
    def cmd_remove_modifier(object_name="", modifier_name=""):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        mod = obj.modifiers.get(modifier_name)
        if not mod:
            return {"error": f"Modifier not found: {modifier_name}"}
        obj.modifiers.remove(mod)
        return {"removed": modifier_name, "from": object_name}

    @staticmethod
    def cmd_list_modifiers(object_name=""):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        mods = [{"name": m.name, "type": m.type} for m in obj.modifiers]
        return {"object": obj.name, "modifiers": mods}

    @staticmethod
    def cmd_apply_modifier(object_name="", modifier_name=""):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        return {"applied": modifier_name, "to": obj.name}
