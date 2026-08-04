"""
blender-mcp — Reference System
Sistema de imágenes de referencia para guiar la creación de modelos.
Inspirado en cc-blender-skill's reference-to-3d workflow.
"""
try:
    import bpy
except ImportError:
    bpy = None

import os
import json
import math
from pathlib import Path


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
            name: Nombre de la referencia (opcional)
        
        Returns:
            Objeto Empty con la imagen
        """
        if not os.path.exists(image_path):
            return {"error": f"Imagen no encontrada: {image_path}"}
        
        if name is None:
            name = Path(image_path).stem
        
        # Crear empty con imagen
        bpy.ops.object.empty_add(type='IMAGE', location=(0, 0, 0))
        empty = bpy.context.active_object
        empty.name = f"REF-{name}"
        
        # Cargar imagen
        img = bpy.data.images.load(image_path)
        empty.data = img
        
        # Configurar tamaño
        empty.empty_display_size = 2
        
        # Guardar referencia
        self.references[name] = {
            "path": image_path,
            "object": empty,
            "name": name,
        }
        
        print(f"Referencia cargada: {name} ({image_path})")
        return empty
    
    def set_as_background(self, reference_name):
        """
        Establecer imagen como fondo de cámara.
        """
        if reference_name not in self.references:
            return {"error": f"Referencia no encontrada: {reference_name}"}
        
        ref = self.references[reference_name]
        img = bpy.data.images.load(ref["path"])
        
        # Configurar en cámara activa
        cam = bpy.context.scene.camera
        if cam:
            cam.data.background_image = img
            cam.data.background_alpha = 0.5
            print(f"Fondo establecido: {reference_name}")
            return True
        
        return {"error": "No hay cámara activa"}
    
    def analyze_reference(self, reference_name):
        """
        Analizar imagen de referencia para extraer información.
        
        Returns:
            dict con información de la imagen
        """
        if reference_name not in self.references:
            return {"error": f"Referencia no encontrada: {reference_name}"}
        
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
        """Listar todas las referencias cargadas"""
        return {k: v["path"] for k, v in self.references.items()}
    
    def remove_reference(self, reference_name):
        """Eliminar una referencia"""
        if reference_name in self.references:
            obj = self.references[reference_name]["object"]
            bpy.data.objects.remove(obj, do_unlink=True)
            del self.references[reference_name]
            print(f"Referencia eliminada: {reference_name}")
            return True
        return False


# ═══════════════════════════════════════════════════════════════
# REFERENCE TEMPLATES
# ═══════════════════════════════════════════════════════════════

REFERENCE_TEMPLATES = {
    "front_view": {
        "description": "Vista frontal",
        "camera_position": (0, -10, 0),
        "camera_rotation": (math.radians(90), 0, 0),
    },
    "side_view": {
        "description": "Vista lateral",
        "camera_position": (10, 0, 0),
        "camera_rotation": (0, 0, math.radians(90)),
    },
    "top_view": {
        "description": "Vista superior",
        "camera_position": (0, 0, 10),
        "camera_rotation": (0, 0, 0),
    },
    "perspective_view": {
        "description": "Vista perspectiva",
        "camera_position": (5, -5, 5),
        "camera_rotation": (math.radians(45), 0, math.radians(45)),
    },
}


def setup_reference_camera(template_name="perspective_view"):
    """
    Configurar cámara para vista de referencia.
    """
    if template_name not in REFERENCE_TEMPLATES:
        return {"error": f"Template no encontrado: {template_name}"}
    
    template = REFERENCE_TEMPLATES[template_name]
    
    # Crear cámara
    bpy.ops.object.camera_add(
        location=template["camera_position"],
        rotation=template["camera_rotation"]
    )
    cam = bpy.context.active_object
    cam.name = f"REF-Cam_{template_name}"
    
    # Establecer como cámara activa
    bpy.context.scene.camera = cam
    
    print(f"Cámara de referencia: {template_name}")
    return cam


import math
