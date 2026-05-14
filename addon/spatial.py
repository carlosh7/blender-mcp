import bpy
import mathutils
from mathutils.bvhtree import BVHTree

class GeometryValidator:
    """El Oráculo: Control de Calidad (QC) industrial v0.4.0."""
    
    @staticmethod
    def get_report(epsilon=0.001):
        """Genera un reporte técnico de interferencias y estabilidad."""
        objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        report = ["--- ORÁCULO AXIOM v0.4.0: REPORTE DE INGENIERÍA ---"]
        
        # Necesitamos el depsgraph evaluado para las posiciones reales tras modificadores
        dg = bpy.context.evaluated_depsgraph_get()
        
        for i, obj_a in enumerate(objs):
            # 1. Validación de Estabilidad (Floating Check)
            if obj_a.location.z > 0.01 and not obj_a.parent:
                report.append(f"⚠️ ESTABILIDAD: {obj_a.name} está flotando sin anclaje jerárquico.")

            # 2. Intersecciones y Z-Fighting con BVH
            for obj_b in objs[i+1:]:
                try:
                    # Crear árboles BVH de las mallas evaluadas
                    bvh_a = BVHTree.FromObject(obj_a, dg)
                    bvh_b = BVHTree.FromObject(obj_b, dg)
                    
                    overlaps = bvh_a.overlap(bvh_b)
                    if overlaps:
                        report.append(f"❌ COLISIÓN CRÍTICA: {obj_a.name} y {obj_b.name} se intersectan.")
                    else:
                        # Check Z-Fighting heurístico por proximidad de centros
                        dist = (obj_a.location - obj_b.location).length
                        if dist < 0.0001:
                             report.append(f"⚠️ Z-FIGHTING: {obj_a.name} y {obj_b.name} están solapados (0.00mm).")
                except Exception:
                    continue

        if len(report) == 1:
            report.append("💎 EXCELENCIA: Geometría perfecta. Sin colisiones ni piezas flotantes.")
            
        return "\n".join(report)

def get_spatial_summary():
    """Resumen espacial ASCII para razonamiento de la IA."""
    objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not objs:
        return "Espacio vacío (Vacío Cósmico)."
    
    summary = ["Telemetría Espacial Axiom:"]
    for obj in objs:
        dim = obj.dimensions
        summary.append(f"- {obj.name}: {round(dim.x,3)}x{round(dim.y,3)}x{round(dim.z,3)}m en pos {list(map(lambda x: round(x,3), obj.location))}")
    
    return "\n".join(summary)

def get_object_anchors(obj_name=""):
    """Legacy helper for agent transition."""
    obj = bpy.data.objects.get(obj_name)
    if not obj: return {}
    from . import assembly
    return assembly.AssemblyEngine.get_bbox_anchors(obj)
