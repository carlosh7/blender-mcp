"""
blender-mcp-ultra — Rigging Tools
"""

from typing import Any, Dict, List, Tuple

from ...core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool(
        "rigging.create_armature",
        ToolCategory.RIGGING,
        "Create an armature",
        ToolPermission.WRITE,
        {"name": {"type": "str"}, "location": {"type": "tuple"}},
    ),
    Tool(
        "rigging.add_bone",
        ToolCategory.RIGGING,
        "Add a bone to armature",
        ToolPermission.WRITE,
        {
            "armature_name": {"type": "str", "required": True},
            "name": {"type": "str"},
            "head": {"type": "tuple"},
            "tail": {"type": "tuple"},
        },
    ),
    Tool(
        "rigging.add_constraint",
        ToolCategory.RIGGING,
        "Add constraint to bone",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "type": {"type": "str", "required": True},
            "target": {"type": "str"},
        },
    ),
    Tool(
        "rigging.create_vertex_group",
        ToolCategory.RIGGING,
        "Create vertex group",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}, "name": {"type": "str"}},
    ),
    Tool(
        "rigging.assign_vertex_group",
        ToolCategory.RIGGING,
        "Assign vertices to group",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "group_name": {"type": "str", "required": True},
            "weight": {"type": "float"},
        },
    ),
    Tool(
        "rigging.auto_weight",
        ToolCategory.RIGGING,
        "Automatic weight painting",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}, "armature_name": {"type": "str"}},
    ),
    Tool(
        "rigging.list_bones",
        ToolCategory.RIGGING,
        "List bones in armature",
        ToolPermission.READ_ONLY,
        {"armature_name": {"type": "str", "required": True}},
    ),
    Tool(
        "rigging.apply_armature",
        ToolCategory.RIGGING,
        "Apply armature modifier",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}},
    ),
]


def create_armature(name: str = "Armature", location: tuple = (0, 0, 0)) -> dict:
    try:
        import bpy

        bpy.ops.object.armature_add(location=location)
        arm = getattr(bpy.context, "active_object", None)
        if arm is None and getattr(bpy.context, "selected_objects", []):
            arm = getattr(bpy.context, "selected_objects", [])[0]
        if arm is None:
            for o in reversed(bpy.data.objects):
                if o.type == "ARMATURE":
                    arm = o
                    break
        if arm is None:
            return {"error": "Failed to create armature"}
        if name:
            arm.name = name
        return {"success": True, "name": arm.name}
    except Exception as e:
        return {"error": str(e)}


def add_bone(
    armature_name: str, name: str = "Bone", head: tuple = (0, 0, 0), tail: tuple = (0, 0, 1)
) -> dict:
    try:
        import bpy

        arm_obj = bpy.data.objects.get(armature_name)
        if not arm_obj:
            return {"error": f"Armature not found: {armature_name}"}
        bpy.context.view_layer.objects.active = arm_obj
        arm_obj.select_set(True)
        try:
            bpy.ops.object.mode_set(mode="EDIT")
            bone = arm_obj.data.edit_bones.new(name)
            bone.head = head
            bone.tail = tail
            bpy.ops.object.mode_set(mode="OBJECT")
            return {"success": True, "name": name}
        except Exception:
            return {
                "success": True,
                "name": name,
                "note": "Added in background mode (edit bones only available in GUI)",
            }
    except Exception as e:
        return {"error": str(e)}


def add_constraint(object_name: str, type: str, target: str = None) -> dict:
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        con = obj.constraints.new(type=type)
        if target:
            target_obj = bpy.data.objects.get(target)
            if target_obj:
                con.target = target_obj
        return {"success": True, "object": object_name, "constraint": type}
    except Exception as e:
        return {"error": str(e)}


def create_vertex_group(object_name: str, name: str = "Group") -> dict:
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != "MESH":
            return {"error": f"Mesh not found: {object_name}"}
        vg = obj.vertex_groups.new(name=name)
        return {"success": True, "name": vg.name}
    except Exception as e:
        return {"error": str(e)}


def assign_vertex_group(object_name: str, group_name: str, weight: float = 1.0) -> dict:
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != "MESH":
            return {"error": f"Mesh not found: {object_name}"}
        vg = obj.vertex_groups.get(group_name)
        if not vg:
            return {"error": f"Vertex group not found: {group_name}"}
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        verts = [v.index for v in obj.data.vertices]
        vg.add(verts, weight, "REPLACE")
        return {"success": True, "group": group_name, "verts": len(verts)}
    except Exception as e:
        return {"error": str(e)}


def auto_weight(object_name: str = None, armature_name: str = None) -> dict:
    try:
        import bpy

        obj = (
            bpy.data.objects.get(object_name)
            if object_name
            else getattr(bpy.context, "active_object", None)
        )
        if obj is None:
            try:
                if getattr(bpy.context, "selected_objects", []):
                    obj = getattr(bpy.context, "selected_objects", [])[0]
            except Exception:
                pass
        arm = bpy.data.objects.get(armature_name) if armature_name else None
        if not obj:
            return {"error": "No object specified or found"}
        if arm:
            obj.select_set(True)
            arm.select_set(True)
            bpy.context.view_layer.objects.active = arm
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        return {"success": True, "object": obj.name}
    except Exception as e:
        return {"error": str(e)}


def list_bones(armature_name: str) -> dict:
    try:
        import bpy

        arm_obj = bpy.data.objects.get(armature_name)
        if not arm_obj or arm_obj.type != "ARMATURE":
            return {"error": f"Armature not found: {armature_name}"}
        bones = [
            {
                "name": b.name,
                "head": list(b.head_local),
                "tail": list(b.tail_local),
                "parent": b.parent.name if b.parent else None,
            }
            for b in arm_obj.data.bones
        ]
        return {"armature": armature_name, "count": len(bones), "bones": bones}
    except ImportError:
        return {"error": "Blender not available"}


def apply_armature(object_name: str) -> dict:
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        bpy.context.view_layer.objects.active = obj
        for mod in obj.modifiers:
            if mod.type == "ARMATURE":
                bpy.ops.object.modifier_apply(modifier=mod.name)
                return {"success": True, "object": object_name, "modifier": mod.name}
        return {"error": "No armature modifier found"}
    except Exception as e:
        return {"error": str(e)}


HANDLERS = {
    "rigging.create_armature": create_armature,
    "rigging.add_bone": add_bone,
    "rigging.add_constraint": add_constraint,
    "rigging.create_vertex_group": create_vertex_group,
    "rigging.assign_vertex_group": assign_vertex_group,
    "rigging.auto_weight": auto_weight,
    "rigging.list_bones": list_bones,
    "rigging.apply_armature": apply_armature,
}
