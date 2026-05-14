"""
blender-mcp — Scene Analysis Handler
Inspired by official blender.org MCP: scene analysis and data-block introspection.
"""
import bpy
import base64
import tempfile
import os
import time
from . import BaseHandler


class AnalysisHandler(BaseHandler):
    """Scene and data-block analysis: object summaries, detail inspection, blendfile audit."""

    namespace = "analysis"

    @staticmethod
    def cmd_get_objects_summary():
        objects = []
        for obj in bpy.context.scene.objects:
            objects.append({
                "name": obj.name,
                "type": obj.type,
                "location": [round(float(obj.location.x), 2), round(float(obj.location.y), 2), round(float(obj.location.z), 2)],
                "dimensions": [round(float(d), 3) for d in obj.dimensions],
                "visible": obj.visible_get(),
            })
        return {
            "total": len(objects),
            "objects": objects,
        }

    @staticmethod
    def cmd_get_object_detail_summary(name=""):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": f"Object not found: {name}"}
        info = {
            "name": obj.name,
            "type": obj.type,
            "location": [obj.location.x, obj.location.y, obj.location.z],
            "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
            "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            "dimensions": [float(d) for d in obj.dimensions],
            "visible": obj.visible_get(),
            "selectable": obj.hide_select,
            "collections": [c.name for c in obj.users_collection],
            "materials": [s.material.name for s in obj.material_slots if s.material],
            "modifiers": [],
            "parent": obj.parent.name if obj.parent else None,
            "children": [c.name for c in obj.children],
            "data": None,
        }
        for mod in obj.modifiers:
            info["modifiers"].append({
                "name": mod.name,
                "type": mod.type,
                "enabled": not mod.show_viewport,
            })
        if obj.type == 'MESH' and obj.data:
            mesh = obj.data
            info["data"] = {
                "type": "MESH",
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
                "uv_layers": len(mesh.uv_layers),
                "vertex_colors": len(mesh.vertex_colors),
            }
        elif obj.type == 'LIGHT' and obj.data:
            light = obj.data
            info["data"] = {
                "type": "LIGHT",
                "light_type": light.type,
                "energy": light.energy,
                "color": list(light.color),
            }
        elif obj.type == 'CAMERA' and obj.data:
            cam = obj.data
            info["data"] = {
                "type": "CAMERA",
                "lens": cam.lens,
                "sensor_width": cam.sensor_width,
                "clip_start": cam.clip_start,
                "clip_end": cam.clip_end,
            }
        return info

    @staticmethod
    def cmd_get_blendfile_summary_datablocks():
        data_attrs = [
            "scenes", "objects", "meshes", "materials",
            "textures", "images", "lights", "cameras",
            "collections", "actions", "node_groups", "worlds",
            "grease_pencils", "curves", "lattices", "armatures",
            "speakers", "linestyles", "movieclips", "sounds",
            "fonts", "brushes", "workspaces", "screens",
            "libraries", "masks",
        ]
        summary = {}
        for attr in data_attrs:
            try:
                summary[attr] = len(getattr(bpy.data, attr))
            except AttributeError:
                summary[attr] = 0
        return {"data_blocks": summary}

    @staticmethod
    def cmd_get_blendfile_summary_missing_files():
        import os
        import bpy
        missing = []
        checked = 0
        def _visit(id_data, path, _placeholder):
            nonlocal checked
            checked += 1
            fp = bpy.path.abspath(path)
            if not os.path.exists(fp):
                missing.append({"id_type": type(id_data).__name__, "id_name": getattr(id_data, "name", ""), "path": fp})
        bpy.data.file_path_foreach(_visit, flags={"SKIP_PACKED", "SKIP_WEAK_REFERENCES", "RESOLVE_TOKEN"})
        return {"status": "ok", "missing_files": missing, "total_checked": checked}

    @staticmethod
    def cmd_get_blendfile_summary_of_linked_libraries():
        import bpy
        direct, indirect = [], []
        for lib in bpy.data.libraries:
            info = {"filepath": lib.filepath, "name": lib.name}
            count = 0
            for attr in dir(bpy.data):
                coll = getattr(bpy.data, attr, None)
                if not hasattr(coll, "__iter__"):
                    continue
                try:
                    for item in coll:
                        if hasattr(item, "library") and item.library == lib:
                            count += 1
                except:
                    pass
            info["linked_datablocks_count"] = count
            if lib.parent is None:
                direct.append(info)
            else:
                info["parent_library"] = lib.parent.name
                indirect.append(info)
        return {"status": "ok", "direct_libraries": direct, "indirect_libraries": indirect, "total_library_count": len(bpy.data.libraries)}

    @staticmethod
    def cmd_get_blendfile_summary_path_info():
        import os, time, bpy
        fp = bpy.data.filepath
        age = size = None
        backups = []
        if fp and os.path.exists(fp):
            stat = os.stat(fp)
            age = round(time.time() - stat.st_mtime, 1)
            size = stat.st_size
            for i in range(1, 32):
                bp = fp + str(i)
                if not os.path.exists(bp):
                    break
                bs = os.stat(bp)
                backups.append({"path": bp, "age_seconds": round(time.time() - bs.st_mtime, 1), "size_bytes": bs.st_size})
        return {"status": "ok", "filepath": fp or "", "is_saved": bool(fp), "is_dirty": bpy.data.is_dirty, "age_seconds": age, "file_size_bytes": size, "backups": backups}

    @staticmethod
    def cmd_get_blendfile_summary_usage_guess():
        import bpy
        DEFAULT_CUBE_VERTS = 8
        signals = {}

        def _summarize(sigs):
            if not sigs:
                return (0, 0)
            n = len(sigs)
            return (round(100 * sum(c for c, _ in sigs) / n), round(100 * sum(k for _, k in sigs) / n))

        data = bpy.data
        scene = bpy.context.scene
        non_default = [m for m in data.meshes if m.name != "Cube" or len(m.vertices) != DEFAULT_CUBE_VERTS]

        usages = {
            "Animation": _summarize([(float(bool(data.actions)), 1.0), (float(bool(data.armatures)), 1.0)]),
            "Modeling": _summarize([(float(bool(non_default)), 0.8), (float(bool(data.curves) or bool(data.metaballs)), 0.7), (float(any(bool(o.modifiers) for o in data.objects)), 0.5)]),
            "Rendering": _summarize([(float(scene.render.engine not in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE")), 0.5), (float(bool(scene.render.filepath not in ("/tmp/", "/tmp\\", ""))), 0.8)]),
            "Scripting": _summarize([(float(bool(data.texts)), 1.0)]),
            "Geometry Nodes": _summarize([(float(any(any(m.type == "NODES" and m.node_group for m in o.modifiers) for o in data.objects)), 1.0)]),
            "Grease Pencil": _summarize([(float(bool(data.grease_pencils)), 1.0)]),
            "UV Unwrapping": _summarize([(float(any(len(m.uv_layers) > 1 for m in data.meshes)), 1.0)]),
        }
        result = {k: {"score": s, "certainty": c} for k, (s, c) in usages.items()}
        return {"status": "ok", "usage_guesses": result}

    @staticmethod
    def cmd_get_screenshot_as_base64(max_size=800):
        filepath = os.path.join(tempfile.gettempdir(), f"blender_mcp_shot_{int(time.time())}.png")
        try:
            area = next((a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'), None)
            if not area:
                return {"error": "No 3D viewport found"}
            with bpy.context.temp_override(area=area):
                bpy.ops.screen.screenshot_area(filepath=filepath)
            with open(filepath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            os.unlink(filepath)
            return {"base64": b64, "mime": "image/png"}
        except Exception as e:
            return {"error": str(e)}
