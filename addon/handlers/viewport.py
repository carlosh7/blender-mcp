"""
blender-mcp — Viewport Navigation Handler
"""
import bpy
from . import BaseHandler


class ViewportHandler(BaseHandler):
    """Viewport navigation: focus on objects, snap to view."""

    namespace = "viewport"

    @staticmethod
    def cmd_jump_to_tab_by_name(name=""):
        import bpy
        if bpy.app.background:
            return {"error": "Not available in background mode"}
        if bpy.context.window is None:
            return {"error": "No active window"}
        ws = bpy.data.workspaces.get(name)
        if ws is None:
            return {"error": f"Workspace '{name}' not found", "available": [w.name for w in bpy.data.workspaces]}
        bpy.context.window.workspace = ws
        return {"workspace": ws.name}

    @staticmethod
    def cmd_jump_to_tab_by_space_type(space_type="", allow_edits=False):
        import bpy
        if bpy.app.background:
            return {"error": "Not available in background mode"}
        if bpy.context.window is None:
            return {"error": "No active window"}
        def _largest(screen):
            return max(screen.areas, key=lambda a: a.width * a.height, default=None)
        for ws in bpy.data.workspaces:
            for screen in ws.screens:
                area = _largest(screen)
                if area and area.type == space_type:
                    bpy.context.window.workspace = ws
                    return {"workspace": ws.name, "space_type": space_type}
        if allow_edits:
            try:
                bpy.ops.workspace.duplicate()
            except RuntimeError as e:
                return {"error": str(e)}
            nw = bpy.context.window.workspace
            nw.name = space_type.replace("_", " ").title()
            area = _largest(bpy.context.screen)
            if area:
                area.type = space_type
            return {"workspace": nw.name, "space_type": space_type, "created": True}
        available = sorted({area.type for ws in bpy.data.workspaces for screen in ws.screens for area in (_largest(screen),) if area})
        return {"error": f"No workspace with space type '{space_type}'", "available": available}

    @staticmethod
    def cmd_jump_to_view3d_object_by_name(name=""):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = bpy.context.temp_override(area=area, region=area.regions[0])
                with override:
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                return {"focused": name}
        return {"error": "No 3D viewport area found", "focused": name}
