import bpy
import mathutils
from mathutils import Vector, Matrix

class AssemblyEngine:
    """Motor de ensamblaje paramétrico para posicionamiento determinista."""
    
    @staticmethod
    def get_bbox_anchors(obj):
        """Calcula los 27 puntos de ancla de un objeto en espacio global (v2.0)."""
        mw = obj.matrix_world
        local_coords = [Vector(v) for v in obj.bound_box]
        
        l_min = Vector((min(v.x for v in local_coords), min(v.y for v in local_coords), min(v.z for v in local_coords)))
        l_max = Vector((max(v.x for v in local_coords), max(v.y for v in local_coords), max(v.z for v in local_coords)))
        l_center = (l_min + l_max) / 2
        
        steps_x = [l_min.x, l_center.x, l_max.x]
        steps_y = [l_min.y, l_center.y, l_max.y]
        steps_z = [l_min.z, l_center.z, l_max.z]
        
        anchors = {}
        names = ["MIN", "CENTER", "MAX"]
        for zi, zv in enumerate(steps_z):
            for yi, yv in enumerate(steps_y):
                for xi, xv in enumerate(steps_x):
                    anchor_name = f"A_{names[xi]}_{names[yi]}_{names[zi]}"
                    anchors[anchor_name] = mw @ Vector((xv, yv, zv))
                    
        return anchors

    @staticmethod
    def snap_to_anchor(obj_move, obj_target, anchor_move_key, anchor_target_key):
        """Mueve un objeto para que un ancla específica coincida con la de otro objeto."""
        anchors_move = AssemblyEngine.get_bbox_anchors(obj_move)
        anchors_target = AssemblyEngine.get_bbox_anchors(obj_target)
        
        if anchor_move_key not in anchors_move or anchor_target_key not in anchors_target:
            return {"error": f"Ancla no válida: {anchor_move_key} o {anchor_target_key}"}
            
        target_pos = anchors_target[anchor_target_key]
        current_pos = anchors_move[anchor_move_key]
        
        translation = target_pos - current_pos
        obj_move.location += translation
        
        return {"status": "SUCCESS", "translation": list(translation)}

    @staticmethod
    def snap_and_parent(obj_move, obj_target, anchor_move_key, anchor_target_key):
        """Snap determinista y vinculación jerárquica automática."""
        result = AssemblyEngine.snap_to_anchor(obj_move, obj_target, anchor_move_key, anchor_target_key)
        if "error" in result:
            return result
            
        # Vincular manteniendo transformación global
        mw_orig = obj_move.matrix_world.copy()
        obj_move.parent = obj_target
        obj_move.matrix_world = mw_orig
        
        return {"status": "SUCCESS_PARENTED", "parent": obj_target.name}

    @staticmethod
    def apply_symmetry(obj, axes=('X', 'Y')):
        """Aplica un modificador Mirror para asegurar simetría industrial."""
        mod_name = "AXIOM_Mirror"
        mod = obj.modifiers.get(mod_name) or obj.modifiers.new(mod_name, 'MIRROR')
        mod.use_axis[0] = 'X' in axes
        mod.use_axis[1] = 'Y' in axes
        mod.use_axis[2] = 'Z' in axes
        return {"status": "MIRROR_APPLIED", "axes": axes}

    @staticmethod
    def fix_normals(obj):
        """Recalcula las normales para asegurar colisiones correctas."""
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            return {"status": "NORMALS_FIXED"}
        return {"error": "No es una malla"}
