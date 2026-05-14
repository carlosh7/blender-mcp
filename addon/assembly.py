import bpy
import mathutils
from mathutils import Vector, Matrix

class AssemblyEngine:
    """Motor de ensamblaje paramétrico para posicionamiento determinista."""
    
    @staticmethod
    def get_bbox_anchors(obj):
        """Calcula los 27 puntos de ancla de un objeto en espacio global."""
        mw = obj.matrix_world
        bbox = [Vector(corner) for corner in obj.bound_box]
        
        # Encontrar min/max locales
        min_v = Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox)))
        max_v = Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))
        mid_v = (min_v + max_v) / 2
        
        anchors = {}
        # Mapeo de anclas (X: L/M/R, Y: B/M/F, Z: B/M/T)
        # L=Left, R=Right, M=Middle, B=Bottom/Back, F=Front, T=Top
        x_vals = {'L': min_v.x, 'M': mid_v.x, 'R': max_v.x}
        y_vals = {'B': min_v.y, 'M': mid_v.y, 'F': max_v.y}
        z_vals = {'B': min_v.z, 'M': mid_v.z, 'T': max_v.z}
        
        for x_key, x_val in x_vals.items():
            for y_key, y_val in y_vals.items():
                for z_key, z_val in z_vals.items():
                    anchors[f"{x_key}{y_key}{z_key}"] = mw @ Vector((x_val, y_val, z_val))
                    
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
    def apply_symmetry(obj, axes=('X', 'Y')):
        """Aplica un modificador Mirror para asegurar simetría industrial."""
        mod_name = "CNC_Mirror"
        mod = obj.modifiers.get(mod_name) or obj.modifiers.new(mod_name, 'MIRROR')
        
        mod.use_axis[0] = 'X' in axes
        mod.use_axis[1] = 'Y' in axes
        mod.use_axis[2] = 'Z' in axes
        
        # Asegurar que el origen esté en el centro de la escena para el mirror
        # O usar un objeto 'Empty' como espejo si es necesario
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
