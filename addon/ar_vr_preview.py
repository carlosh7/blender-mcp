"""
blender-mcp — AR/VR Preview
Vista previa para realidad aumentada y virtual.
"""
import bpy
import os
import json
from typing import Dict, List, Optional
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# EXPORT FORMATS
# ═══════════════════════════════════════════════════════════════

AR_VR_FORMATS = {
    "webxr": {
        "extension": ".glb",
        "description": "WebXR (Realidad Virtual en navegador)",
        "options": {"export_format": 'GLB', "export_apply": True},
    },
    "arcore": {
        "extension": ".glb",
        "description": "ARCore (Android AR)",
        "options": {"export_format": 'GLB', "export_apply": True},
    },
    "arkit": {
        "extension": ".usdz",
        "description": "ARKit (iOS AR)",
        "options": {},
    },
    "oculus": {
        "extension": ".glb",
        "description": "Oculus Quest",
        "options": {"export_format": 'GLB', "export_apply": True},
    },
    "steamvr": {
        "extension": ".fbx",
        "description": "SteamVR",
        "options": {"export_apply": True},
    },
}


# ═══════════════════════════════════════════════════════════════
# AR/VR EXPORT
# ═══════════════════════════════════════════════════════════════

def export_for_ar_vr(target: str, filepath: Optional[str] = None) -> Dict:
    """
    Exportar escena para plataforma AR/VR.
    
    Args:
        target: Plataforma (webxr, arcore, arkit, oculus, steamvr)
        filepath: Ruta de salida (None = automática)
    
    Returns:
        Dict con resultado
    """
    if target not in AR_VR_FORMATS:
        return {"error": f"Unknown target: {target}"}
    
    config = AR_VR_FORMATS[target]
    
    if filepath is None:
        export_dir = Path("/tmp/blender_mcp_ar_vr")
        export_dir.mkdir(parents=True, exist_ok=True)
        filepath = str(export_dir / f"scene_{target}{config['extension']}")
    
    try:
        # Select all objects
        bpy.ops.object.select_all(action='SELECT')
        
        # Export based on format
        if config["extension"] == ".glb":
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                **config["options"]
            )
        elif config["extension"] == ".fbx":
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                **config["options"]
            )
        elif config["extension"] == ".usdz":
            # USDZ export (requires addon)
            bpy.ops.wm.usd_export(filepath=filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        
        return {
            "success": True,
            "filepath": filepath,
            "format": config["extension"],
            "target": target,
            "description": config["description"],
            "size_mb": round(file_size / (1024 * 1024), 2),
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}


def optimize_for_webxr(obj: bpy.types.Object) -> Dict:
    """
    Optimizar objeto para WebXR.
    
    Args:
        obj: Objeto a optimizar
    
    Returns:
        Dict con optimizaciones aplicadas
    """
    optimizations = {
        "decimated": False,
        "materials_simplified": False,
        "uv_optimized": False,
    }
    
    try:
        # Decimate if too many polygons
        if obj.type == 'MESH' and len(obj.data.polygons) > 10000:
            mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
            mod.ratio = 0.5
            bpy.ops.object.modifier_apply(modifier=mod.name)
            optimizations["decimated"] = True
        
        # Simplify materials
        if obj.data.materials:
            for mat in obj.data.materials:
                if mat.use_nodes:
                    # Keep only Principled BSDF
                    nodes_to_remove = [
                        n for n in mat.node_tree.nodes
                        if n.type != 'OUTPUT_MATERIAL' and n.type != 'BSDF_PRINCIPLED'
                    ]
                    for node in nodes_to_remove:
                        mat.node_tree.nodes.remove(node)
            optimizations["materials_simplified"] = True
        
        # Smart UV project
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
            bpy.ops.object.mode_set(mode='OBJECT')
            optimizations["uv_optimized"] = True
        
        print(f"[ar_vr] Optimized {obj.name} for WebXR")
        return optimizations
        
    except Exception as e:
        print(f"[ar_vr] Optimization failed: {e}")
        return optimizations


def create_ar_marker(obj: bpy.types.Object, marker_type: str = "plane") -> bpy.types.Object:
    """
    Crear marcador AR para un objeto.
    
    Args:
        obj: Objeto padre
        marker_type: Tipo de marcador (plane, cube, sphere)
    
    Returns:
        Objeto marcador creado
    """
    try:
        # Create marker
        if marker_type == "plane":
            bpy.ops.mesh.primitive_plane_add(size=0.1, location=obj.location)
        elif marker_type == "cube":
            bpy.ops.mesh.primitive_cube_add(size=0.1, location=obj.location)
        elif marker_type == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=obj.location)
        
        marker = bpy.context.active_object
        marker.name = f"AR_Marker_{obj.name}"
        
        # Parent to object
        marker.parent = obj
        
        # Create AR material
        mat = bpy.data.materials.new(f"AR_Marker_Mat_{obj.name}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0, 1, 0, 1)  # Green
            bsdf.inputs["Alpha"].default_value = 0.5
        marker.data.materials.append(mat)
        
        print(f"[ar_vr] AR marker created for {obj.name}")
        return marker
        
    except Exception as e:
        print(f"[ar_vr] Marker creation failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# VR PREVIEW
# ═══════════════════════════════════════════════════════════════

def setup_vr_preview() -> bool:
    """
    Configurar Blender para vista previa VR.
    
    Returns:
        True si éxito
    """
    try:
        # Enable VR addon if available
        bpy.ops.preferences.addon_enable(module='viewport_vr_preview')
        
        # Set viewport to rendered mode
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
        
        print("[ar_vr] VR preview setup complete")
        return True
        
    except Exception as e:
        print(f"[ar_vr] VR setup failed: {e}")
        return False


def get_ar_vr_info() -> Dict:
    """
    Obtener información de exportación AR/VR.
    
    Returns:
        Dict con formatos disponibles
    """
    return {
        "formats": {
            name: {
                "extension": config["extension"],
                "description": config["description"],
            }
            for name, config in AR_VR_FORMATS.items()
        },
        "tips": [
            "Use GLB for maximum compatibility",
            "Keep polygon count under 100K for mobile AR",
            "Use PBR materials for realistic rendering",
            "Optimize textures to 1024x1024 for mobile",
        ],
    }
