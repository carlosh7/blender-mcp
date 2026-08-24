"""
blender-mcp-ultra — Scene Utils Tools
"""

from typing import Any, Dict

from ...core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool(
        "scene_utils.cleanup",
        ToolCategory.SCENE_UTILS,
        "Clean up scene (orphans, unused)",
        ToolPermission.WRITE,
        {},
    ),
    Tool(
        "scene_utils.purge_orphans",
        ToolCategory.SCENE_UTILS,
        "Purge orphan data blocks",
        ToolPermission.WRITE,
        {},
    ),
    Tool(
        "scene_utils.mesh_analysis",
        ToolCategory.SCENE_UTILS,
        "Analyze mesh for issues",
        ToolPermission.READ_ONLY,
        {"object_name": {"type": "str"}},
    ),
    Tool(
        "scene_utils.apply_all_transforms",
        ToolCategory.SCENE_UTILS,
        "Apply all transforms",
        ToolPermission.WRITE,
        {},
    ),
    Tool(
        "scene_utils.origin_to_geometry",
        ToolCategory.SCENE_UTILS,
        "Set origin to geometry center",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}},
    ),
    Tool(
        "scene_utils.fix_normals",
        ToolCategory.SCENE_UTILS,
        "Recalculate normals",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}},
    ),
    Tool(
        "scene_utils.remove_doubles",
        ToolCategory.SCENE_UTILS,
        "Remove duplicate vertices",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}, "distance": {"type": "float"}},
    ),
    Tool(
        "scene_utils.triangulate",
        ToolCategory.SCENE_UTILS,
        "Triangulate mesh",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}},
    ),
]


def cleanup() -> dict:
    try:
        import bpy

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        return {"success": True, "message": "Scene cleaned up"}
    except Exception as e:
        return {"error": str(e)}


def purge_orphans() -> dict:
    try:
        import bpy

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def mesh_analysis(object_name: str) -> dict:
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != "MESH":
            return {"error": f"Mesh not found: {object_name}"}
        mesh = obj.data
        return {
            "name": obj.name,
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "tris": sum(len(p.vertices) - 2 for p in mesh.polygons),
        }
    except ImportError:
        return {"error": "Blender not available"}


def apply_all_transforms() -> dict:
    try:
        import bpy

        count = 0
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                obj.select_set(False)
                count += 1
        return {"success": True, "applied": count}
    except Exception as e:
        return {"error": str(e)}


def origin_to_geometry(object_name: str = None) -> dict:
    try:
        import bpy

        if object_name:
            obj = bpy.data.objects.get(object_name)
            if obj:
                bpy.context.view_layer.objects.active = obj
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def fix_normals(object_name: str = None) -> dict:
    """Fix normals using bmesh (works in background mode)."""
    try:
        import bpy

        obj = bpy.data.objects.get(object_name) if object_name else None
        if obj is None:
            for o in bpy.context.scene.objects:
                if o.type == "MESH":
                    obj = o
                    break
        if obj is None or obj.type != "MESH":
            return {"error": "No mesh object found"}
        import bmesh

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def remove_doubles(object_name: str = None, distance: float = 0.001) -> dict:
    """Remove doubles using bmesh (works in background mode)."""
    try:
        import bpy

        obj = bpy.data.objects.get(object_name) if object_name else None
        if obj is None:
            for o in bpy.context.scene.objects:
                if o.type == "MESH":
                    obj = o
                    break
        if obj is None or obj.type != "MESH":
            return {"error": "No mesh object found"}
        import bmesh

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        return {"success": True, "distance": distance}
    except Exception as e:
        return {"error": str(e)}


def triangulate(object_name: str = None) -> dict:
    try:
        import bpy

        obj = bpy.data.objects.get(object_name) if object_name else None
        if obj is None:
            for o in bpy.context.scene.objects:
                if o.type == "MESH":
                    obj = o
                    break
        if obj is None or obj.type != "MESH":
            return {"error": "No mesh object found"}
        import bmesh

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


HANDLERS = {
    "scene_utils.cleanup": cleanup,
    "scene_utils.purge_orphans": purge_orphans,
    "scene_utils.mesh_analysis": mesh_analysis,
    "scene_utils.apply_all_transforms": apply_all_transforms,
    "scene_utils.origin_to_geometry": origin_to_geometry,
    "scene_utils.fix_normals": fix_normals,
    "scene_utils.remove_doubles": remove_doubles,
    "scene_utils.triangulate": triangulate,
}
