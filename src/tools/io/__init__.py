"""
blender-mcp-ultra — I/O Tools
Background-mode safe exports.
"""

from typing import Any, Dict

from ...core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool(
        "io.export_fbx",
        ToolCategory.IO,
        "Export scene to FBX",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}, "use_selection": {"type": "bool"}},
    ),
    Tool(
        "io.export_obj",
        ToolCategory.IO,
        "Export scene to OBJ",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}, "use_selection": {"type": "bool"}},
    ),
    Tool(
        "io.export_gltf",
        ToolCategory.IO,
        "Export scene to glTF/GLB",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}, "format": {"type": "str"}},
    ),
    Tool(
        "io.export_stl",
        ToolCategory.IO,
        "Export scene to STL",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}, "use_selection": {"type": "bool"}},
    ),
    Tool(
        "io.import_fbx",
        ToolCategory.IO,
        "Import FBX file",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}},
    ),
    Tool(
        "io.import_obj",
        ToolCategory.IO,
        "Import OBJ file",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}},
    ),
    Tool(
        "io.import_gltf",
        ToolCategory.IO,
        "Import glTF file",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}},
    ),
    Tool(
        "io.import_stl",
        ToolCategory.IO,
        "Import STL file",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}},
    ),
    Tool(
        "io.save_file",
        ToolCategory.IO,
        "Save blend file",
        ToolPermission.WRITE,
        {"filepath": {"type": "str"}},
    ),
    Tool(
        "io.load_file",
        ToolCategory.IO,
        "Load blend file",
        ToolPermission.WRITE,
        {"filepath": {"type": "str", "required": True}},
    ),
]


def _try_export(export_func, filepath: str, **kwargs) -> dict:
    """Try to export, with error handling for background mode."""
    import bpy

    try:
        # Check poll first
        if hasattr(export_func, "poll") and not export_func.poll():
            return {"error": "Export needs GUI (background mode). Save .blend and export manually."}
        export_func(filepath=filepath, **kwargs)
        return {"success": True, "filepath": filepath}
    except AttributeError as e:
        if "active_object" in str(e) or "cursor_set" in str(e) or "window" in str(e):
            return {"error": "Export needs GUI (background mode). Save .blend and export manually."}
        return {"error": str(e)[:80]}
    except Exception as e:
        return {"error": str(e)[:80]}


def export_fbx(filepath: str, use_selection: bool = False) -> dict:
    try:
        import bpy

        return _try_export(bpy.ops.export_scene.fbx, filepath, use_selection=use_selection)
    except Exception as e:
        return {"error": str(e)}


def export_obj(filepath: str, use_selection: bool = False) -> dict:
    try:
        import bpy

        if hasattr(bpy.ops.wm, "obj_export"):
            return _try_export(
                bpy.ops.wm.obj_export, filepath, export_selected_objects=use_selection
            )
        return _try_export(bpy.ops.export_scene.obj, filepath, use_selection=use_selection)
    except Exception as e:
        return {"error": str(e)}


def export_gltf(filepath: str, format: str = "GLB") -> dict:
    try:
        import bpy

        fmt = "GLB" if format.upper() == "GLB" else "GLTF_SEPARATE"
        return _try_export(bpy.ops.export_scene.gltf, filepath, export_format=fmt)
    except Exception as e:
        return {"error": str(e)}


def export_stl(filepath: str, use_selection: bool = False) -> dict:
    try:
        import bpy

        if hasattr(bpy.ops.wm, "stl_export"):
            return _try_export(bpy.ops.wm.stl_export, filepath)
        return {"error": "STL export not available. Save .blend and export manually."}
    except Exception as e:
        return {"error": str(e)}


def import_fbx(filepath: str) -> dict:
    try:
        import bpy

        bpy.ops.import_scene.fbx(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e:
        return {"error": str(e)}


def import_obj(filepath: str) -> dict:
    try:
        import bpy

        bpy.ops.wm.obj_import(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e:
        return {"error": str(e)}


def import_gltf(filepath: str) -> dict:
    try:
        import bpy

        bpy.ops.import_scene.gltf(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e:
        return {"error": str(e)}


def import_stl(filepath: str) -> dict:
    try:
        import bpy

        if hasattr(bpy.ops.wm, "stl_import"):
            bpy.ops.wm.stl_import(filepath=filepath)
        elif hasattr(bpy.ops.import_mesh, "stl"):
            bpy.ops.import_mesh.stl(filepath=filepath)
        else:
            return {"error": "STL import not available"}
        return {"success": True, "filepath": filepath}
    except Exception as e:
        return {"error": str(e)}


def save_file(filepath: str = None) -> dict:
    try:
        import bpy

        if filepath:
            bpy.ops.wm.save_as_mainfile(filepath=filepath)
        else:
            bpy.ops.wm.save_mainfile()
        return {"success": True, "filepath": bpy.data.filepath}
    except Exception as e:
        return {"error": str(e)}


def load_file(filepath: str) -> dict:
    try:
        import bpy

        bpy.ops.wm.open_mainfile(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e:
        return {"error": str(e)}


HANDLERS = {
    "io.export_fbx": export_fbx,
    "io.export_obj": export_obj,
    "io.export_gltf": export_gltf,
    "io.export_stl": export_stl,
    "io.import_fbx": import_fbx,
    "io.import_obj": import_obj,
    "io.import_gltf": import_gltf,
    "io.import_stl": import_stl,
    "io.save_file": save_file,
    "io.load_file": load_file,
}
