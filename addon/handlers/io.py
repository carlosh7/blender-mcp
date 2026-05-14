"""
blender-mcp — Import/Export Handler
FBX, OBJ, GLTF/GLB, USD, STL, DAE, PLY, SVG, ABC.
"""
import bpy
import os
from . import BaseHandler


EXPORT_FORMATS = {
    "glb": "export_scene.gltf",
    "gltf": "export_scene.gltf",
    "fbx": "export_scene.fbx",
    "obj": "export_scene.obj",
    "stl": "export_mesh.stl",
    "ply": "export_mesh.ply",
    "usd": "export_scene.usd",
    "usdc": "export_scene.usd",
    "dae": "export_scene.dae",
    "abc": "export_alembic.abc",
    "x3d": "export_scene.x3d",
    "svg": "export_curves.svg",
}

IMPORT_FORMATS = {
    "glb": "import_scene.gltf",
    "gltf": "import_scene.gltf",
    "fbx": "import_scene.fbx",
    "obj": "import_scene.obj",
    "stl": "import_mesh.stl",
    "ply": "import_mesh.ply",
    "usd": "import_scene.usd",
    "usdc": "import_scene.usd",
    "dae": "import_scene.dae",
    "abc": "import_alembic.abc",
    "svg": "import_curves.svg",
    "x3d": "import_scene.x3d",
    "blend": "import_scene.blend",  # append
}


class IOHandler(BaseHandler):
    """Import and export 3D models in various formats."""

    namespace = "io"

    @staticmethod
    def cmd_export_scene(filepath="", format="glb"):
        fmt = format.lower().lstrip(".")
        op = EXPORT_FORMATS.get(fmt)
        if not op:
            return {"error": f"Unsupported export format: {format}"}
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        kwargs = {"filepath": filepath, "check_existing": False}
        if fmt in ("glb", "gltf"):
            kwargs["export_format"] = "GLB" if fmt == "glb" else "GLTF_SEPARATE"
        getattr(bpy.ops, op)(**kwargs)
        size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        return {"filepath": filepath, "format": fmt, "size_bytes": size}

    @staticmethod
    def cmd_export_selected(filepath="", format="glb"):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.selected_objects:
            obj.select_set(True)
        return IOHandler.cmd_export_scene(filepath, format)

    @staticmethod
    def cmd_import_model(filepath="", format=""):
        if not format:
            format = filepath.split(".")[-1].lower()
        fmt = format.lower().lstrip(".")
        op = IMPORT_FORMATS.get(fmt)
        if not op:
            return {"error": f"Unsupported import format: {format}"}
        if not os.path.exists(filepath):
            return {"error": f"File not found: {filepath}"}
        before = set(bpy.data.objects.keys())
        getattr(bpy.ops, op)(filepath=filepath)
        imported = [o.name for o in bpy.data.objects if o.name not in before]
        return {"imported": imported, "format": fmt}

    @staticmethod
    def cmd_list_export_formats():
        return {"formats": sorted(EXPORT_FORMATS.keys())}

    @staticmethod
    def cmd_list_import_formats():
        return {"formats": sorted(IMPORT_FORMATS.keys())}
