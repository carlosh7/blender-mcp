"""
blender-mcp — Visual Reference System
Sistema para comparar objetos con imágenes de referencia.
"""
try:
    import bpy
except ImportError:
    bpy = None

import os
import json


# ═══════════════════════════════════════════════════════════════
# REFERENCE IMAGE MANAGER
# ═══════════════════════════════════════════════════════════════

class ReferenceManager:
    """Gestor de imágenes de referencia"""
    
    def __init__(self):
        self.references = {}
        self.current_reference = None
    
    def load_reference(self, image_path, name=None):
        """
        Cargar imagen de referencia al viewport.
        
        Args:
            image_path: Ruta de la imagen
            name: Nombre de la referencia
        """
        if bpy is None:
            return {"error": "bpy not available"}
        
        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_path}"}
        
        if name is None:
            name = os.path.basename(image_path)
        
        # Crear empty con imagen
        bpy.ops.object.empty_add(type='IMAGE', location=(0, 0, 0))
        empty = bpy.context.active_object
        empty.name = f"REF-{name}"
        
        # Cargar imagen
        img = bpy.data.images.load(image_path)
        empty.data = img
        empty.empty_display_size = 2
        
        # Guardar referencia
        self.references[name] = {
            "path": image_path,
            "object": empty,
            "name": name,
        }
        
        print(f"Reference loaded: {name} ({image_path})")
        return empty
    
    def set_as_background(self, reference_name):
        """Establecer imagen como fondo de cámara"""
        if reference_name not in self.references:
            return {"error": f"Reference not found: {reference_name}"}
        
        ref = self.references[reference_name]
        img = bpy.data.images.load(ref["path"])
        
        cam = bpy.context.scene.camera
        if cam:
            cam.data.background_image = img
            cam.data.background_alpha = 0.5
            print(f"Background set: {reference_name}")
            return True
        
        return {"error": "No active camera"}
    
    def analyze_reference(self, reference_name):
        """Analizar imagen de referencia"""
        if reference_name not in self.references:
            return {"error": f"Reference not found: {reference_name}"}
        
        ref = self.references[reference_name]
        img = bpy.data.images.load(ref["path"])
        
        return {
            "name": reference_name,
            "path": ref["path"],
            "width": img.size[0],
            "height": img.size[1],
            "aspect_ratio": img.size[0] / img.size[1] if img.size[1] > 0 else 1,
        }
    
    def list_references(self):
        """Listar todas las referencias"""
        return {k: v["path"] for k, v in self.references.items()}
    
    def remove_reference(self, reference_name):
        """Eliminar una referencia"""
        if reference_name in self.references:
            obj = self.references[reference_name]["object"]
            bpy.data.objects.remove(obj, do_unlink=True)
            del self.references[reference_name]
            print(f"Reference removed: {reference_name}")
            return True
        return False


# ═══════════════════════════════════════════════════════════════
# REFERENCE COMPARISON
# ═══════════════════════════════════════════════════════════════

def compare_with_reference(scene_objects, reference_data):
    """
    Comparar escena con datos de referencia.
    
    Args:
        scene_objects: Objetos de la escena
        reference_data: Datos de referencia esperados
    
    Returns:
        dict con comparación
    """
    matches = []
    mismatches = []
    
    for ref in reference_data:
        found = False
        for obj in scene_objects:
            if obj["name"] == ref.get("name"):
                if obj["type"] == ref.get("type"):
                    matches.append(obj["name"])
                else:
                    mismatches.append(f"{obj['name']}: type mismatch")
                found = True
                break
        
        if not found:
            mismatches.append(f"{ref.get('name')}: not found")
    
    return {
        "matches": len(matches),
        "mismatches": len(mismatches),
        "score": len(matches) / max(len(reference_data), 1) * 100,
    }


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_reference_views():
    """Listar vistas de referencia disponibles"""
    return {
        "front": "Vista frontal",
        "back": "Vista trasera",
        "left": "Vista lateral izquierda",
        "right": "Vista lateral derecha",
        "top": "Vista superior",
        "perspective": "Vista perspectiva",
    }
