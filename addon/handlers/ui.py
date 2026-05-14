"""
blender-mcp — UI Context Inspector
JSON Layout Mapping: window → screens → areas → spaces.active
Permite al agente saber qué editores están abiertos y en qué modo.
"""
import bpy
from . import BaseHandler


class UIHandler(BaseHandler):
    """Inspect Blender's UI layout: areas, spaces, shading, geometry."""

    namespace = "ui"

    @staticmethod
    def cmd_get_ui_layout():
        result = []
        for window in bpy.context.window_manager.windows:
            for screen in window.screens:
                for area in screen.areas:
                    info = {
                        "type": area.type,
                        "x": area.x,
                        "y": area.y,
                        "width": area.width,
                        "height": area.height,
                        "regions": [r.type for r in area.regions],
                    }
                    space = area.spaces.active
                    if area.type == 'VIEW_3D':
                        r3d = space.region_3d
                        info["view"] = {
                            "perspective": r3d.view_perspective,
                            "shading_type": space.shading.type,
                            "show_overlays": space.overlay.show_overlays,
                            "show_gizmo": space.show_gizmo,
                            "view_matrix": [list(r) for r in r3d.view_matrix],
                            "view_location": list(r3d.view_location),
                        }
                    elif area.type == 'NODE_EDITOR':
                        info["node"] = {
                            "tree_type": space.tree_type,
                            "tree_name": space.node_tree.name if space.node_tree else None,
                        }
                    elif area.type == 'PROPERTIES':
                        info["properties"] = {
                            "context": space.context,
                        }
                    elif area.type == 'IMAGE_EDITOR':
                        info["image"] = {
                            "mode": space.mode,
                            "image_name": space.image.name if space.image else None,
                        }
                    result.append(info)
        return {"windows_count": len(bpy.context.window_manager.windows), "areas": result}
