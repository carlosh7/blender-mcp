"""
blender-mcp — Scene Utilities Handler
Cleanup, batch rename, apply transforms, mesh analysis, orphan purge.
"""
import bpy
from . import BaseHandler


class SceneUtilsHandler(BaseHandler):
    """Scene cleanup, batch operations, mesh analysis, data management."""

    namespace = "scene_utils"

    @staticmethod
    def cmd_purge_orphans():
        """Remove unused data blocks (materials, meshes, textures, etc.)."""
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        return {"purged": True}

    @staticmethod
    def cmd_cleanup_scene():
        """Purge orphans, remove unused collections, normalize names."""
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        # Remove empty collections
        removed = 0
        for coll in list(bpy.data.collections):
            if not coll.objects and not coll.children:
                bpy.data.collections.remove(coll)
                removed += 1
        return {"purged": True, "empty_collections_removed": removed}

    @staticmethod
    def cmd_mesh_analysis(object_name=""):
        """Analyze mesh topology and report statistics."""
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj or obj.type != 'MESH':
            return {"error": "No mesh object"}
        mesh = obj.data
        import mathutils
        bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
        return {
            "name": obj.name,
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "uv_layers": len(mesh.uv_layers),
            "material_slots": len(obj.material_slots),
            "dimensions": {
                "x": round(obj.dimensions.x, 3),
                "y": round(obj.dimensions.y, 3),
                "z": round(obj.dimensions.z, 3),
            },
            "location": list(obj.location),
            "triangle_count": sum(len(p.loop_indices) - 2 for p in mesh.polygons if len(p.loop_indices) >= 3),
        }

    @staticmethod
    def cmd_scene_summary():
        """Full scene summary: counts by type and memory usage."""
        counts = {}
        for obj in bpy.data.objects:
            t = obj.type
            counts[t] = counts.get(t, 0) + 1
        return {
            "name": bpy.context.scene.name,
            "total_objects": len(bpy.data.objects),
            "total_materials": len(bpy.data.materials),
            "total_meshes": len(bpy.data.meshes),
            "total_images": len(bpy.data.images),
            "total_collections": len(bpy.data.collections),
            "counts_by_type": counts,
        }

    @staticmethod
    def cmd_select_by_type(object_type="MESH"):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type == object_type:
                obj.select_set(True)
        return {"selected_type": object_type}

    @staticmethod
    def cmd_hide_object(object_name="", hide=True):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        obj.hide_viewport = hide
        obj.hide_render = hide
        return {"object": object_name, "hidden": hide}

    @staticmethod
    def cmd_apply_transform(object_name="", location=True, rotation=True, scale=True):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)
        return {"object": obj.name, "location": location, "rotation": rotation, "scale": scale}

    @staticmethod
    def cmd_join_objects(target_name="", source_names=None):
        target = bpy.data.objects.get(target_name)
        if not target:
            return {"error": f"Target not found: {target_name}"}
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.select_all(action='DESELECT')
        target.select_set(True)
        if source_names:
            for name in source_names:
                obj = bpy.data.objects.get(name)
                if obj:
                    obj.select_set(True)
        bpy.ops.object.join()
        return {"joined": target.name}
