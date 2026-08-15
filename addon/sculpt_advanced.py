"""
blender-mcp — Advanced Sculpting
Herramientas avanzadas de escultura procedural.
"""
import bpy
import bmesh
import math
from mathutils import Vector
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════
# SCULPT OPERATIONS
# ═══════════════════════════════════════════════════════════════

def remesh_voxel(obj: bpy.types.Object, voxel_size: float = 0.05) -> bool:
    """
    Remesh con voxel para topología uniforme.
    
    Args:
        obj: Objeto a remesh
        voxel_size: Tamaño del voxel
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add voxel remesh modifier
        mod = obj.modifiers.new(name="VoxelRemesh", type='REMESH')
        mod.mode = 'VOXEL'
        mod.voxel_size = voxel_size
        
        # Apply modifier
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        print(f"[sculpt] Voxel remesh applied: {obj.name}, size={voxel_size}")
        return True
        
    except Exception as e:
        print(f"[sculpt] Remesh failed: {e}")
        return False


def remesh_quad(obj: bpy.types.Object, target_faces: int = 1000) -> bool:
    """
    Remesh con quads para topología cuadrangular.
    
    Args:
        obj: Objeto a remesh
        target_faces: Caras objetivo
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add quad remesh modifier
        mod = obj.modifiers.new(name="QuadRemesh", type='REMESH')
        mod.mode = 'QUAD'
        mod.octree_depth = 6
        mod.scale = 0.9
        mod.threshold = 0.001
        
        # Apply modifier
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        print(f"[sculpt] Quad remesh applied: {obj.name}, target={target_faces}")
        return True
        
    except Exception as e:
        print(f"[sculpt] Quad remesh failed: {e}")
        return False


def decimate(obj: bpy.types.Object, ratio: float = 0.5) -> bool:
    """
    Decimar malla para reducir polígonos.
    
    Args:
        obj: Objeto a decimar
        ratio: Ratio de decimación (0-1)
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add decimate modifier
        mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
        mod.ratio = ratio
        
        # Apply modifier
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        print(f"[sculpt] Decimate applied: {obj.name}, ratio={ratio}")
        return True
        
    except Exception as e:
        print(f"[sculpt] Decimate failed: {e}")
        return False


def smooth_mesh(obj: bpy.types.Object, factor: float = 0.5, iterations: int = 1) -> bool:
    """
    Suavizar malla.
    
    Args:
        obj: Objeto a suavizar
        factor: Factor de suavizado (0-1)
        iterations: Número de iteraciones
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Smooth
        bpy.ops.mesh.smooth(factor=factor, iterations=iterations)
        
        # Back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"[sculpt] Smooth applied: {obj.name}, factor={factor}")
        return True
        
    except Exception as e:
        print(f"[sculpt] Smooth failed: {e}")
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
        return False


def inflate_mesh(obj: bpy.types.Object, factor: float = 0.1) -> bool:
    """
    Inflar malla.
    
    Args:
        obj: Objeto a inflar
        factor: Factor de inflación
    
    Returns:
        True si éxito
    """
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Transform normals
        bpy.ops.transform.shrink_fatten(value=factor)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"[sculpt] Inflate applied: {obj.name}, factor={factor}")
        return True
        
    except Exception as e:
        print(f"[sculpt] Inflate failed: {e}")
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
        return False


# ═══════════════════════════════════════════════════════════════
# SCULPT PRESETS
# ═══════════════════════════════════════════════════════════════

SCULPT_PRESETS = {
    "smooth": {"smooth_factor": 0.5, "smooth_iterations": 2},
    "inflate": {"inflate_factor": 0.2},
    "deflate": {"inflate_factor": -0.2},
    "flatten": {"smooth_factor": 0.8, "smooth_iterations": 3},
    "sharpen": {"decimate_ratio": 0.8},
    "organic": {"voxel_size": 0.02, "smooth_factor": 0.3},
    "low_poly": {"decimate_ratio": 0.3},
    "high_detail": {"voxel_size": 0.01},
    "blocky": {"decimate_ratio": 0.2, "smooth_factor": 0.1},
    "round": {"smooth_factor": 0.7, "smooth_iterations": 3},
}


def apply_sculpt_preset(obj: bpy.types.Object, preset_name: str) -> bool:
    """
    Aplicar preset de escultura.
    
    Args:
        obj: Objeto a esculturar
        preset_name: Nombre del preset
    
    Returns:
        True si éxito
    """
    if preset_name not in SCULPT_PRESETS:
        print(f"[sculpt] Unknown preset: {preset_name}")
        return False
    
    preset = SCULPT_PRESETS[preset_name]
    
    # Apply operations in order
    if "voxel_size" in preset:
        remesh_voxel(obj, preset["voxel_size"])
    
    if "decimate_ratio" in preset:
        decimate(obj, preset["decimate_ratio"])
    
    if "smooth_factor" in preset:
        smooth_mesh(obj, preset["smooth_factor"], preset.get("smooth_iterations", 1))
    
    if "inflate_factor" in preset:
        inflate_mesh(obj, preset["inflate_factor"])
    
    print(f"[sculpt] Preset '{preset_name}' applied to {obj.name}")
    return True


# ═══════════════════════════════════════════════════════════════
# ORGANIC SHAPES
# ═══════════════════════════════════════════════════════════════

def create_organic_blob(radius: float = 1.0, detail: int = 3) -> Optional[bpy.types.Object]:
    """
    Crear forma orgánica tipo blob.
    
    Args:
        radius: Radio
        detail: Nivel de detalle
    
    Returns:
        Objeto creado
    """
    try:
        # Create base sphere
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius,
            segments=32,
            ring_count=16,
            location=(0, 0, 0)
        )
        obj = bpy.context.active_object
        obj.name = "Organic_Blob"
        
        # Add displacement for organic feel
        mod = obj.modifiers.new(name="Displace", type='DISPLACE')
        mod.strength = radius * 0.2
        
        # Add smooth
        mod2 = obj.modifiers.new(name="Smooth", type='SMOOTH')
        mod2.factor = 0.5
        mod2.iterations = 3
        
        # Apply modifiers
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.ops.object.modifier_apply(modifier=mod2.name)
        
        print(f"[sculpt] Organic blob created: radius={radius}")
        return obj
        
    except Exception as e:
        print(f"[sculpt] Blob creation failed: {e}")
        return None


def create_rock(radius: float = 0.5, roughness: float = 0.3) -> Optional[bpy.types.Object]:
    """
    Crear roca procedural.
    
    Args:
        radius: Radio base
        roughness: Rugosidad
    
    Returns:
        Objeto creado
    """
    try:
        # Create base ico sphere
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=radius,
            location=(0, 0, 0)
        )
        obj = bpy.context.active_object
        obj.name = "Rock"
        
        # Random displacement
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Randomize vertices
        import random
        bm = bmesh.from_edit_mesh(obj.data)
        for v in bm.verts:
            v.co += Vector((
                random.uniform(-roughness, roughness),
                random.uniform(-roughness, roughness),
                random.uniform(-roughness, roughness),
            )) * radius
        bmesh.update_edit_mesh(obj.data)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Smooth slightly
        smooth_mesh(obj, 0.3, 1)
        
        print(f"[sculpt] Rock created: radius={radius}")
        return obj
        
    except Exception as e:
        print(f"[sculpt] Rock creation failed: {e}")
        return None
