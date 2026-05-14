"""
blender-mcp — 3D Printing Handler
MM-scale, manifold check, bed layout, STL optimization.
Inspired by yuri-schmaltz/mcp-blender 3D Printing Toolkit.
"""
import bpy
import bmesh
import math
from mathutils import Vector
from . import BaseHandler


class PrintingHandler(BaseHandler):
    """3D Printing tools: manifold check, mm-scale, bed layout, wall thickness."""

    namespace = "printing"

    @staticmethod
    def cmd_check_manifold(object_name=""):
        """Check if a mesh is manifold (watertight)."""
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj or obj.type != 'MESH':
            return {"error": "No mesh object"}
        dg = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(dg)
        mesh = eval_obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.edges.ensure_lookup_table()
        non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
        eval_obj.to_mesh_clear()
        return {
            "object": obj.name,
            "non_manifold_edges": non_manifold,
            "is_manifold": non_manifold == 0,
            "vertices": len(mesh.vertices),
            "polygons": len(mesh.polygons),
        }

    @staticmethod
    def cmd_set_dimensions_mm(object_name="", width_mm=0, depth_mm=0, height_mm=0):
        """Set object dimensions in millimeters."""
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        # 1 Blender unit = 1 meter = 1000 mm
        new_dims = []
        if width_mm > 0:
            new_dims.append(width_mm / 1000.0)
        else:
            new_dims.append(obj.dimensions.x)
        if depth_mm > 0:
            new_dims.append(depth_mm / 1000.0)
        else:
            new_dims.append(obj.dimensions.y)
        if height_mm > 0:
            new_dims.append(height_mm / 1000.0)
        else:
            new_dims.append(obj.dimensions.z)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(scale=True)
        scale_x = new_dims[0] / obj.dimensions.x if obj.dimensions.x > 0 else 1
        scale_y = new_dims[1] / obj.dimensions.y if obj.dimensions.y > 0 else 1
        scale_z = new_dims[2] / obj.dimensions.z if obj.dimensions.z > 0 else 1
        obj.scale = (scale_x, scale_y, scale_z)
        bpy.ops.object.transform_apply(scale=True)
        return {
            "object": obj.name,
            "dimensions_mm": {
                "x": round(obj.dimensions.x * 1000, 2),
                "y": round(obj.dimensions.y * 1000, 2),
                "z": round(obj.dimensions.z * 1000, 2),
            },
        }

    @staticmethod
    def cmd_export_stl_mm(filepath="", object_name=""):
        """Export model as STL with millimeter scale."""
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        # Global scale: 1 BU = 1000 mm for STL export
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True, global_scale=1000.0)
        import os
        size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        return {"filepath": filepath, "size_bytes": size, "scale_mm": True}

    @staticmethod
    def cmd_bed_layout(object_names=None, bed_size_x_mm=200, bed_size_y_mm=200):
        """Arrange objects on a print bed (top-down layout)."""
        bed_x = bed_size_x_mm / 1000.0
        bed_y = bed_size_y_mm / 1000.0
        if not object_names:
            object_names = [o.name for o in bpy.context.scene.objects if o.type == 'MESH']
        objs = [bpy.data.objects.get(n) for n in object_names if bpy.data.objects.get(n)]
        x, y = -bed_x / 2, -bed_y / 2
        row_h = 0
        for obj in objs:
            if x + obj.dimensions.x > bed_x / 2:
                x = -bed_x / 2
                y += row_h + 0.01
                row_h = 0
            obj.location = (x + obj.dimensions.x / 2, y + obj.dimensions.y / 2, obj.dimensions.z / 2)
            x += obj.dimensions.x + 0.01
            row_h = max(row_h, obj.dimensions.y)
        return {"objects_placed": len(objs), "bed_size_mm": (bed_size_x_mm, bed_size_y_mm)}

    @staticmethod
    def cmd_add_wall_thickness(object_name="", thickness_mm=2.0):
        """Add a Solidify modifier for wall thickness (3D printing prep)."""
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        mod = obj.modifiers.new(name="WallThickness", type='SOLIDIFY')
        if not mod:
            return {"error": "Failed to create Solidify modifier"}
        try:
            mod.thickness = thickness_mm / 1000.0
            mod.offset = -1.0
            mod.use_even_offset = True
        except AttributeError as e:
            return {"error": f"Modifier property error: {e}"}
        return {"object": obj.name, "thickness_mm": thickness_mm}
