"""
blender-mcp — Rigging Handler
Armature, bones, vertex groups, constraints.
"""
import bpy
from mathutils import Vector
from . import BaseHandler


class RiggingHandler(BaseHandler):
    """Create armatures, bones, vertex groups, and constraints."""

    namespace = "rigging"

    @staticmethod
    def cmd_create_armature(name="Armature", location=(0, 0, 0)):
        bpy.ops.object.armature_add(location=location)
        arm = bpy.context.active_object
        arm.name = name
        return {"name": arm.name, "bones": len(arm.data.bones)}

    @staticmethod
    def cmd_add_bone(armature_name="", bone_name="Bone", head=(0, 0, 0), tail=(0, 0, 1), parent_name=""):
        arm = bpy.data.objects.get(armature_name)
        if not arm or arm.type != 'ARMATURE':
            return {"error": f"Armature not found: {armature_name}"}
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='EDIT')
        bone = arm.data.edit_bones.new(bone_name)
        bone.head = Vector(head)
        bone.tail = Vector(tail)
        if parent_name:
            parent = arm.data.edit_bones.get(parent_name)
            if parent:
                bone.parent = parent
        bpy.ops.object.mode_set(mode='OBJECT')
        return {"armature": armature_name, "bone": bone_name}

    @staticmethod
    def cmd_add_vertex_group(object_name="", group_name="Group"):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj or obj.type != 'MESH':
            return {"error": "No mesh object"}
        vg = obj.vertex_groups.new(name=group_name)
        return {"object": obj.name, "group": vg.name}

    @staticmethod
    def cmd_assign_vertex_group(object_name="", group_name="", vertex_indices=None, weight=1.0):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        vg = obj.vertex_groups.get(group_name)
        if not vg:
            return {"error": f"Vertex group not found: {group_name}"}
        if vertex_indices:
            vg.add(vertex_indices, weight, 'REPLACE')
        else:
            # Assign all selected vertices
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.mode_set(mode='OBJECT')
        return {"object": obj.name, "group": group_name, "weight": weight}

    @staticmethod
    def cmd_add_constraint(object_name="", constraint_type="COPY_LOCATION", target_name=""):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        target = bpy.data.objects.get(target_name) if target_name else None
        constraint = obj.constraints.new(type=constraint_type)
        constraint.name = f"{constraint_type}_{target_name or 'None'}"
        if target:
            constraint.target = target
        return {"object": obj.name, "constraint": constraint.name, "type": constraint_type}

    @staticmethod
    def cmd_parent_with_armature(object_name="", armature_name=""):
        obj = bpy.data.objects.get(object_name)
        arm = bpy.data.objects.get(armature_name)
        if not obj or not arm:
            return {"error": "Object or armature not found"}
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm
        obj.parent = arm
        return {"object": obj.name, "armature": arm.name}

    @staticmethod
    def cmd_auto_rig_weight(object_name="", armature_name=""):
        obj = bpy.data.objects.get(object_name)
        arm = bpy.data.objects.get(armature_name)
        if not obj or not arm:
            return {"error": "Object or armature not found"}
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        return {"object": obj.name, "armature": arm.name, "method": "auto"}
