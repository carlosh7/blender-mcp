"""
blender-mcp-ultra — I/O Tools
"""
from typing import Any, Dict
from core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool("io.export_fbx", ToolCategory.IO, "Export scene to FBX", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}, "use_selection": {"type": "bool"}}),
    Tool("io.export_obj", ToolCategory.IO, "Export scene to OBJ", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}, "use_selection": {"type": "bool"}}),
    Tool("io.export_gltf", ToolCategory.IO, "Export scene to glTF/GLB", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}, "format": {"type": "str"}}),
    Tool("io.export_stl", ToolCategory.IO, "Export scene to STL", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}, "use_selection": {"type": "bool"}}),
    Tool("io.import_fbx", ToolCategory.IO, "Import FBX file", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}}),
    Tool("io.import_obj", ToolCategory.IO, "Import OBJ file", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}}),
    Tool("io.import_gltf", ToolCategory.IO, "Import glTF file", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}}),
    Tool("io.import_stl", ToolCategory.IO, "Import STL file", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}}),
    Tool("io.save_file", ToolCategory.IO, "Save blend file", ToolPermission.WRITE,
         {"filepath": {"type": "str"}}),
    Tool("io.load_file", ToolCategory.IO, "Load blend file", ToolPermission.WRITE,
         {"filepath": {"type": "str", "required": True}}),
]

def export_fbx(filepath: str, use_selection: bool = False) -> Dict:
    try:
        import bpy
        if use_selection: bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.fbx(filepath=filepath, use_selection=use_selection)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

def export_obj(filepath: str, use_selection: bool = False) -> Dict:
    try:
        import bpy
        bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=use_selection)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

def export_gltf(filepath: str, format: str = "GLB") -> Dict:
    try:
        import bpy
        fmt = 'GLB' if format.upper() == 'GLB' else 'GLTF_SEPARATE'
        bpy.ops.export_scene.gltf(filepath=filepath, export_format=fmt)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

def export_stl(filepath: str, use_selection: bool = False) -> Dict:
    try:
        import bpy
        bpy.ops.export_mesh.stl(filepath=filepath, use_selection=use_selection)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

def import_fbx(filepath: str) -> Dict:
    try:
        import bpy
        bpy.ops.import_scene.fbx(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

def import_obj(filepath: str) -> Dict:
    try:
        import bpy
        bpy.ops.wm.obj_import(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

def import_gltf(filepath: str) -> Dict:
    try:
        import bpy
        bpy.ops.import_scene.gltf(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

def import_stl(filepath: str) -> Dict:
    try:
        import bpy
        bpy.ops.import_mesh.stl(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

def save_file(filepath: str = None) -> Dict:
    try:
        import bpy
        if filepath: bpy.ops.wm.save_as_mainfile(filepath=filepath)
        else: bpy.ops.wm.save_mainfile()
        return {"success": True, "filepath": bpy.data.filepath}
    except Exception as e: return {"error": str(e)}

def load_file(filepath: str) -> Dict:
    try:
        import bpy
        bpy.ops.wm.open_mainfile(filepath=filepath)
        return {"success": True, "filepath": filepath}
    except Exception as e: return {"error": str(e)}

HANDLERS = {
    "io.export_fbx": export_fbx, "io.export_obj": export_obj,
    "io.export_gltf": export_gltf, "io.export_stl": export_stl,
    "io.import_fbx": import_fbx, "io.import_obj": import_obj,
    "io.import_gltf": import_gltf, "io.import_stl": import_stl,
    "io.save_file": save_file, "io.load_file": load_file,
}
