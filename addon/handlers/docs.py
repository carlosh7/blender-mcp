"""
blender-mcp — Blender API Documentation Handler
Uses built-in Blender introspection: bpy.types, bpy.ops, and operator docstrings.
"""
import bpy
import re
from . import BaseHandler


class DocsHandler(BaseHandler):
    """Blender Python API documentation via introspection — no external docs needed."""

    namespace = "docs"

    @staticmethod
    def cmd_search_api_docs(query=""):
        q = query.lower().strip()
        results = []

        category_map = {
            "mesh": ("MESH", bpy.types.Mesh, dir(bpy.types.Mesh)),
            "object": ("OBJECT", bpy.types.Object, dir(bpy.types.Object)),
            "material": ("MATERIAL", bpy.types.Material, dir(bpy.types.Material)),
            "scene": ("SCENE", bpy.types.Scene, dir(bpy.types.Scene)),
            "world": ("WORLD", bpy.types.World, dir(bpy.types.World)),
            "light": ("LIGHT", bpy.types.Light, dir(bpy.types.Light)),
            "camera": ("CAMERA", bpy.types.Camera, dir(bpy.types.Camera)),
            "collection": ("COLLECTION", bpy.types.Collection, dir(bpy.types.Collection)),
            "image": ("IMAGE", bpy.types.Image, dir(bpy.types.Image)),
            "texture": ("TEXTURE", bpy.types.Texture, dir(bpy.types.Texture)),
            "action": ("ACTION", bpy.types.Action, dir(bpy.types.Action)),
            "node": ("NODE", bpy.types.Node, dir(bpy.types.Node)),
            "node_tree": ("NODE_TREE", bpy.types.NodeTree, dir(bpy.types.NodeTree)),
            "modifier": ("MODIFIER", bpy.types.Modifier, dir(bpy.types.Modifier)),
            "bone": ("BONE", bpy.types.Bone, dir(bpy.types.Bone)),
            "armature": ("ARMATURE", bpy.types.Armature, dir(bpy.types.Armature)),
            "keyframe": ("KEYFRAME", bpy.types.Keyframe, dir(bpy.types.Keyframe)),
            "curve": ("CURVE", bpy.types.Curve, dir(bpy.types.Curve)),
            "grease_pencil": ("GPENCIL", bpy.types.GreasePencil, dir(bpy.types.GreasePencil)),
        }

        for cat_key, (cat_label, cls, attrs) in category_map.items():
            if q and q not in cat_key and not any(q in a.lower() for a in attrs[:200]):
                continue
            matched = [a for a in attrs if q in a.lower()] if q else attrs[:5]
            results.append({
                "category": cat_label,
                "type": cls.__name__,
                "matched_properties": matched[:20],
            })

        if not q or q in ("ops", "operator"):
            op_cats = {}
            for cat in dir(bpy.ops):
                if cat.startswith("_"):
                    continue
                sub = getattr(bpy.ops, cat, None)
                if not sub:
                    continue
                ops_list = [o for o in dir(sub) if not o.startswith("_")]
                matched = [o for o in ops_list if q in o.lower()] if q else ops_list[:5]
                if matched:
                    op_cats[cat] = matched[:10]

            if op_cats:
                results.append({
                    "category": "OPERATORS",
                    "categories": op_cats,
                })

        return {
            "query": query,
            "results_count": len(results),
            "results": results,
            "note": "Use get_python_api_docs(topic) for detailed docs on a specific property or operator.",
        }

    @staticmethod
    def cmd_get_python_api_docs(topic=""):
        topic = topic.strip()
        if not topic:
            return {"error": "Provide a topic name (e.g. 'Object.location', 'ops.mesh.primitive_cube_add')"}

        parts = topic.split(".")
        result = {}

        if parts[0] == "ops" and len(parts) >= 3:
            cat = parts[1]
            op_name = parts[2]
            try:
                sub = getattr(bpy.ops, cat, None)
                if sub:
                    op_func = getattr(sub, op_name, None)
                    if op_func:
                        doc = op_func.__doc__ or ""
                        result["topic"] = topic
                        result["doc"] = doc.strip()[:2000]
                        result["type"] = "operator"
                        return result
            except:
                pass
            return {"error": f"Operator not found: {topic}"}

        if len(parts) >= 2:
            type_name = parts[0]
            attr_path = ".".join(parts[1:])
            cls = getattr(bpy.types, type_name, None)
            if not cls:
                return {"error": f"Type not found: {type_name}. Use search_api_docs to find valid types."}

            obj = cls.__doc__ or ""
            result["topic"] = topic
            result["type_doc"] = obj.strip()[:1000]

            current = cls
            for i, p in enumerate(parts[1:]):
                try:
                    prop = getattr(current, p, None)
                    if prop is None:
                        result["error_part"] = f"'{p}' not found in {'>'.join(parts[:i+2])}"
                        break
                    doc = ""
                    if isinstance(prop, property):
                        doc = prop.__doc__ if prop.__doc__ else ""
                        if not doc and prop.fget:
                            doc = prop.fget.__doc__ or ""
                    elif callable(prop):
                        doc = prop.__doc__ or ""
                    doc = doc.strip()[:1000]
                    result[f"{p}_doc"] = doc
                    current = prop
                except Exception as e:
                    result[f"{p}_error"] = str(e)
                    break

            result["resolved_type"] = type_name
            return result

        cls = getattr(bpy.types, topic, None)
        if cls:
            doc = cls.__doc__ or ""
            attrs = [a for a in dir(cls) if not a.startswith("_")]
            return {
                "topic": topic,
                "doc": doc.strip()[:2000],
                "properties": attrs[:50],
                "total_properties": len(attrs),
            }

        try:
            bln = getattr(bpy.ops, topic, None)
            if bln:
                ops = [o for o in dir(bln) if not o.startswith("_")]
                return {"topic": topic, "type": "operator_category", "operators": ops}
        except:
            pass

        return {"error": f"Topic not found: {topic}"}
