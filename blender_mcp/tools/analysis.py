"""
blender-mcp — Analysis MCP tools
"""
import json
from ...blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool(**RO())
    def get_model_blueprint(obj_name: str = "") -> str:
        """Genera una ficha técnica total (Blueprint v0.4.0) de un objeto: topología, masa, IOR y 27 puntos de anclaje."""
        b = get_blender()
        r = b.send_command("get_model_blueprint", {"obj_name": obj_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def get_screenshot_as_base64(max_size: int = 800) -> str:
        """Capture a screenshot of the 3D viewport and return as base64 PNG. Use this for visual validation."""
        b = get_blender()
        r = b.send_command("get_screenshot_as_base64", {"max_size": max_size})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def get_objects_summary() -> str:
        """Get a summary table of ALL objects in the scene: name, type, location, dimensions, visibility."""
        b = get_blender()
        r = b.send_command("get_objects_summary")
        return json.dumps(r, indent=2)

    @mcp.tool()
    def get_object_detail_summary(name: str) -> str:
        """Get comprehensive detail for a single object: transforms, modifiers, materials, mesh data, children/parent."""
        b = get_blender()
        r = b.send_command("get_object_detail_summary", {"name": name})
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_datablocks() -> str:
        """Get a count summary of ALL data-block types in the blend file (meshes, materials, scenes, etc.)."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_datablocks")
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_missing_files() -> str:
        """Report all missing external file references (textures, images, sounds, etc.) in the blend file."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_missing_files")
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_of_linked_libraries() -> str:
        """Get the tree of direct and indirect linked libraries in the blend file."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_of_linked_libraries")
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_path_info() -> str:
        """Get blend file path, save status, age, file size, and backup versions."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_path_info")
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_usage_guess() -> str:
        """Score likelihood (0-100) of each use-case for the current blend file (Animation, Modeling, Rendering, etc.)."""
        b = get_blender()
        r = b.send_command("get_blendfile_summary_usage_guess")
        return json.dumps(r, indent=2)

    # ── CLI variants (analyze .blend without running Blender) ──

    @mcp.tool(**RO())
    def get_blendfile_summary_datablocks_for_cli(blend_file: str) -> str:
        """Analyze a .blend file on disk for data-block counts (no Blender instance needed)."""
        from blender_mcp.blender_cli import run_blender_cli
        code = "import bpy; result = {k: len(getattr(bpy.data, k)) for k in dir(bpy.data) if not k.startswith('_') and hasattr(getattr(bpy.data, k), '__len__')}"
        r = run_blender_cli(blend_file, code)
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_path_info_for_cli(blend_file: str) -> str:
        """Get file path, save status, age, and backups from a .blend file on disk (no Blender instance needed)."""
        from blender_mcp.blender_cli import run_blender_cli
        import os, time
        code = "import bpy, os, time; fp = bpy.data.filepath; st = os.stat(fp) if fp and os.path.exists(fp) else None; result = {'filepath': fp, 'is_saved': bool(fp), 'is_dirty': bpy.data.is_dirty, 'age_seconds': round(time.time() - st.st_mtime, 1) if st else None, 'file_size_bytes': st.st_size if st else None}"
        r = run_blender_cli(blend_file, code)
        return json.dumps(r, indent=2)

    @mcp.tool(**RO())
    def get_blendfile_summary_missing_files_for_cli(blend_file: str) -> str:
        """Find missing external file references in a .blend file on disk (no Blender instance needed)."""
        from blender_mcp.blender_cli import run_blender_cli
        code = "import bpy, os; missing = []; checked = [0]; f = lambda id_data, path, _: (checked.__setitem__(0, checked[0]+1) or missing.append({'id_type': type(id_data).__name__, 'id_name': getattr(id_data, 'name', ''), 'path': bpy.path.abspath(path)}) if not os.path.exists(bpy.path.abspath(path)) else None); bpy.data.file_path_foreach(f, flags={'SKIP_PACKED', 'SKIP_WEAK_REFERENCES', 'RESOLVE_TOKEN'}); result = {'missing_files': missing, 'total_checked': checked[0]}"
        r = run_blender_cli(blend_file, code)
        return json.dumps(r, indent=2)
