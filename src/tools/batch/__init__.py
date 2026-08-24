"""
blender-mcp-ultra — Batch Tools
"""

from typing import Any, Dict, List

from ...core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool(
        "batch.rename",
        ToolCategory.BATCH,
        "Batch rename objects",
        ToolPermission.WRITE,
        {"pattern": {"type": "str"}, "replace": {"type": "str"}, "type_filter": {"type": "str"}},
    ),
    Tool(
        "batch.delete_by_type",
        ToolCategory.BATCH,
        "Delete all objects of a type",
        ToolPermission.DESTRUCTIVE,
        {"type": {"type": "str", "required": True}},
    ),
    Tool(
        "batch.apply_transforms",
        ToolCategory.BATCH,
        "Apply transforms to all objects",
        ToolPermission.WRITE,
        {"type_filter": {"type": "str"}},
    ),
    Tool(
        "batch.add_modifier",
        ToolCategory.BATCH,
        "Add modifier to multiple objects",
        ToolPermission.WRITE,
        {
            "object_names": {"type": "list", "required": True},
            "modifier_type": {"type": "str", "required": True},
        },
    ),
    Tool(
        "batch.set_material",
        ToolCategory.BATCH,
        "Set material for multiple objects",
        ToolPermission.WRITE,
        {
            "object_names": {"type": "list", "required": True},
            "material_name": {"type": "str", "required": True},
        },
    ),
    Tool(
        "batch.turntable",
        ToolCategory.BATCH,
        "Create turntable animation",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}, "frames": {"type": "int"}, "axis": {"type": "str"}},
    ),
]


def rename(pattern: str, replace: str, type_filter: str = None) -> dict:
    try:
        import re

        import bpy

        count = 0
        for obj in bpy.context.scene.objects:
            if type_filter and obj.type != type_filter.upper():
                continue
            if pattern in obj.name:
                obj.name = obj.name.replace(pattern, replace)
                count += 1
        return {"success": True, "renamed": count}
    except Exception as e:
        return {"error": str(e)}


def delete_by_type(type: str) -> dict:
    try:
        import bpy

        count = 0
        for obj in list(bpy.context.scene.objects):
            if obj.type == type.upper():
                bpy.data.objects.remove(obj, do_unlink=True)
                count += 1
        return {"success": True, "deleted": count, "type": type}
    except Exception as e:
        return {"error": str(e)}


def apply_transforms(type_filter: str = None) -> dict:
    try:
        import bpy

        count = 0
        for obj in bpy.context.scene.objects:
            if type_filter and obj.type != type_filter.upper():
                continue
            if obj.type == "MESH":
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                obj.select_set(False)
                count += 1
        return {"success": True, "applied": count}
    except Exception as e:
        return {"error": str(e)}


def add_modifier_batch(object_names: list[str], modifier_type: str) -> dict:
    try:
        import bpy

        results = []
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if obj:
                mod = obj.modifiers.new(name=modifier_type, type=modifier_type)
                results.append({"name": name, "modifier": mod.name})
        return {"success": True, "modified": len(results)}
    except Exception as e:
        return {"error": str(e)}


def set_material_batch(object_names: list[str], material_name: str) -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}
        count = 0
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if obj and hasattr(obj, "data") and hasattr(obj.data, "materials"):
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
                count += 1
        return {"success": True, "assigned": count, "material": material_name}
    except Exception as e:
        return {"error": str(e)}


def turntable(object_name: str = None, frames: int = 120, axis: str = "Z") -> dict:
    try:
        import bpy

        obj = (
            bpy.data.objects.get(object_name)
            if object_name
            else getattr(bpy.context, "active_object", None)
        )
        if not obj:
            return {"error": "No object specified or found"}
        import math

        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = frames
        for f in range(frames + 1):
            angle = (f / frames) * 2 * math.pi
            if axis.upper() == "Z":
                obj.rotation_euler = (0, 0, angle)
            elif axis.upper() == "Y":
                obj.rotation_euler = (0, angle, 0)
            else:
                obj.rotation_euler = (angle, 0, 0)
            obj.keyframe_insert(data_path="rotation_euler", frame=f)
        return {"success": True, "object": obj.name, "frames": frames}
    except Exception as e:
        return {"error": str(e)}


HANDLERS = {
    "batch.rename": rename,
    "batch.delete_by_type": delete_by_type,
    "batch.apply_transforms": apply_transforms,
    "batch.add_modifier": add_modifier_batch,
    "batch.set_material": set_material_batch,
    "batch.turntable": turntable,
}
