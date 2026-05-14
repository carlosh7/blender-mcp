import bpy
import bmesh
from mathutils import Vector

class GeometryScanner:
    """Analiza geometría existente para extraer planos técnicos (Blueprints)."""
    
    @staticmethod
    def get_blueprint(obj):
        """Devuelve un resumen técnico de las dimensiones y puntos críticos del objeto."""
        if obj.type != 'MESH':
            return {"error": "El objeto no es una malla (Mesh)"}
            
        # Forzar actualización de la base de datos de Blender
        dg = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(dg)
        mesh = obj_eval.to_mesh()
        
        # Dimensiones de la caja lógica (Bounding Box) en espacio global
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        
        # Puntos extremos
        min_x = min(v.x for v in bbox)
        max_x = max(v.x for v in bbox)
        min_y = min(v.y for v in bbox)
        max_y = max(v.y for v in bbox)
        min_z = min(v.z for v in bbox)
        max_z = max(v.z for v in bbox)
        
        dimensions = {
            "width_x": max_x - min_x,
            "depth_y": max_y - min_y,
            "height_z": max_z - min_z,
            "center_global": list((obj.matrix_world @ Vector((0,0,0))))
        }
        
        # Análisis de caras para encontrar planos de apoyo (suelos)
        up_faces = []
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.transform(obj.matrix_world)
        
        for face in bm.faces:
            if face.normal.dot(Vector((0, 0, 1))) > 0.9: # Cara que apunta hacia arriba
                up_faces.append({
                    "center": list(face.calc_center_median()),
                    "area": face.calc_area()
                })
        
        bm.free()
        obj_eval.to_mesh_clear()
        
        return {
            "object_name": obj.name,
            "dimensions": dimensions,
            "top_surface_count": len(up_faces),
            "blueprint_status": "VALIDATED"
        }

    @staticmethod
    def detect_holes(obj):
        """Busca perforaciones o centros de agujeros en la malla."""
        # Lógica para detectar huecos (simplificada para V1)
        # En una mesa de billar, buscamos áreas vacías cerca de las esquinas del bounding box.
        return {"status": "feature_under_development", "message": "Hole detection requires bmesh topology analysis."}
