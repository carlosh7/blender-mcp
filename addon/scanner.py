import bpy
import bmesh
from mathutils import Vector

class GeometryScanner:
    """Analiza geometría existente para extraer planos técnicos (Blueprints)."""
    
    @staticmethod
    def get_blueprint(obj):
        """Genera una especificación técnica total (v0.4.0) del objeto."""
        if obj.type != 'MESH':
            return {"error": "El objeto no es una malla (Mesh)"}
            
        # Forzar actualización de Blender
        dg = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(dg)
        mesh = obj_eval.to_mesh()
        
        # 1. Dimensiones y Transformación
        mw = obj.matrix_world
        local_coords = [Vector(v) for v in obj.bound_box]
        global_coords = [mw @ v for v in local_coords]
        
        l_min = Vector((min(v.x for v in local_coords), min(v.y for v in local_coords), min(v.z for v in local_coords)))
        l_max = Vector((max(v.x for v in local_coords), max(v.y for v in local_coords), max(v.z for v in local_coords)))
        l_center = (l_min + l_max) / 2
        
        # 2. Motor de 27 Anclas (Determinista)
        steps_x = [l_min.x, l_center.x, l_max.x]
        steps_y = [l_min.y, l_center.y, l_max.y]
        steps_z = [l_min.z, l_center.z, l_max.z]
        
        anchors = {}
        idx = 0
        names = ["MIN", "CENTER", "MAX"]
        for zi, zv in enumerate(steps_z):
            for yi, yv in enumerate(steps_y):
                for xi, xv in enumerate(steps_x):
                    anchor_name = f"A_{names[xi]}_{names[yi]}_{names[zi]}"
                    anchors[anchor_name] = list(mw @ Vector((xv, yv, zv)))
                    idx += 1
        
        # 3. Propiedades Físicas y Ópticas
        # Intentar obtener IOR del material Principled BSDF
        ior = 1.45
        if obj.active_material and obj.active_material.use_nodes:
            node = obj.active_material.node_tree.nodes.get("Principled BSDF")
            if node:
                ior = node.inputs["IOR"].default_value
        
        # Estimar masa basada en volumen (promedio 500kg/m3 para equipos AV)
        volume = obj.dimensions.x * obj.dimensions.y * obj.dimensions.z
        mass = obj.get("axiom_mass", volume * 500.0)
        
        # 4. Topología y Hash
        topo_hash = hash(f"{len(mesh.vertices)}_{len(mesh.polygons)}")
        
        blueprint = {
            "object_name": obj.name,
            "version": "0.4.0",
            "status": "HIGH_FIDELITY",
            "topology": {
                "vertices": len(mesh.vertices),
                "faces": len(mesh.polygons),
                "hash": str(topo_hash)
            },
            "physics": {
                "mass_kg": round(float(mass), 2),
                "ior": round(float(ior), 3)
            },
            "dimensions": {
                "width_x": round(obj.dimensions.x, 4),
                "depth_y": round(obj.dimensions.y, 4),
                "height_z": round(obj.dimensions.z, 4),
                "center_global": list(mw.translation)
            },
            "anchors_27pt": anchors
        }
        
        obj_eval.to_mesh_clear()
        return blueprint

    @staticmethod
    def detect_holes(obj):
        """Busca perforaciones o centros de agujeros en la malla."""
        # Lógica para detectar huecos (simplificada para V1)
        # En una mesa de billar, buscamos áreas vacías cerca de las esquinas del bounding box.
        return {"status": "feature_under_development", "message": "Hole detection requires bmesh topology analysis."}
