"""
blender-mcp — Building Generator
Generador de edificios y arquitectura procedural.
Inspirado en building_tools.
"""
try:
    import bpy
except ImportError:
    bpy = None
import math
from mathutils import Vector


# ═══════════════════════════════════════════════════════════════
# BUILDING TEMPLATES
# ═══════════════════════════════════════════════════════════════

BUILDING_TEMPLATES = {
    "house": {
        "description": "Casa residencial",
        "default_size": (10, 8, 3),
        "floors": 1,
        "windows": 4,
        "doors": 1,
    },
    "apartment": {
        "description": "Edificio de apartamentos",
        "default_size": (15, 10, 9),
        "floors": 3,
        "windows": 12,
        "doors": 6,
    },
    "office": {
        "description": "Edificio de oficinas",
        "default_size": (20, 15, 12),
        "floors": 4,
        "windows": 20,
        "doors": 8,
    },
    "warehouse": {
        "description": "Almacén",
        "default_size": (30, 20, 6),
        "floors": 1,
        "windows": 4,
        "doors": 2,
    },
    "skyscraper": {
        "description": "Rascacielos",
        "default_size": (15, 15, 60),
        "floors": 20,
        "windows": 100,
        "doors": 4,
    },
}


# ═══════════════════════════════════════════════════════════════
# BUILDING GENERATOR
# ═══════════════════════════════════════════════════════════════

def create_building(building_type, params=None):
    """
    Crear edificio desde plantilla.
    
    Args:
        building_type: Tipo de edificio
        params: Parámetros personalizados
    
    Returns:
        dict con objetos creados
    """
    if building_type not in BUILDING_TEMPLATES:
        print(f"Tipo no encontrado: {building_type}")
        return {}
    
    template = BUILDING_TEMPLATES[building_type]
    
    if params is None:
        params = {}
    
    size = params.get("size", template["default_size"])
    location = params.get("location", (0, 0, 0))
    
    results = {}
    
    # Crear estructura base
    results["structure"] = _create_structure(size, location)
    
    # Crear paredes
    results["walls"] = _create_walls(size, location)
    
    # Crear ventanas
    results["windows"] = _create_windows(size, location, template["windows"])
    
    # Crear puertas
    results["doors"] = _create_doors(size, location, template["doors"])
    
    # Crear techo
    results["roof"] = _create_roof(size, location)
    
    print(f"Edificio creado: {building_type} ({len(results)} componentes)")
    return results


def _create_structure(size, location):
    """Crear estructura base del edificio"""
    x, y, z = size
    lx, ly, lz = location
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly, lz + z/2))
    structure = bpy.context.active_object
    structure.name = "Building_Structure"
    structure.scale = (x, y, z)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.new("StructureMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.7, 0.68, 0.65, 1)
    structure.data.materials.append(mat)
    
    return structure


def _create_walls(size, location):
    """Crear paredes"""
    x, y, z = size
    lx, ly, lz = location
    
    walls = []
    thickness = 0.2
    
    # Pared frontal
    bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly - y/2, lz + z/2))
    wall_f = bpy.context.active_object
    wall_f.name = "Wall_Front"
    wall_f.scale = (x, thickness, z)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    mat = bpy.data.materials.new("WallMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.83, 0.8, 1)
    wall_f.data.materials.append(mat)
    walls.append(wall_f)
    
    # Pared trasera
    bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly + y/2, lz + z/2))
    wall_b = bpy.context.active_object
    wall_b.name = "Wall_Back"
    wall_b.scale = (x, thickness, z)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    wall_b.data.materials.append(mat)
    walls.append(wall_b)
    
    print(f"Paredes creadas: {len(walls)}")
    return walls


def _create_windows(size, location, count):
    """Crear ventanas"""
    x, y, z = size
    lx, ly, lz = location
    
    windows = []
    spacing = x / (count + 1)
    
    for i in range(count):
        wx = lx - x/2 + spacing * (i + 1)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(wx, ly - y/2 - 0.1, lz + z * 0.6))
        win = bpy.context.active_object
        win.name = f"Window_{i}"
        win.scale = (0.6, 0.05, 0.4)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        
        # Material vidrio
        mat = bpy.data.materials.new(f"WindowMat_{i}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.9, 1.0, 1)
        mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.0
        win.data.materials.append(mat)
        
        windows.append(win)
    
    print(f"Ventanas creadas: {len(windows)}")
    return windows


def _create_doors(size, location, count):
    """Crear puertas"""
    x, y, z = size
    lx, ly, lz = location
    
    doors = []
    spacing = x / (count + 1)
    
    for i in range(count):
        dx = lx - x/2 + spacing * (i + 1)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(dx, ly - y/2 - 0.1, lz + 0.5))
        door = bpy.context.active_object
        door.name = f"Door_{i}"
        door.scale = (0.4, 0.05, 1.0)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        
        # Material madera
        mat = bpy.data.materials.new(f"DoorMat_{i}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.4, 0.25, 0.12, 1)
        door.data.materials.append(mat)
        
        doors.append(door)
    
    print(f"Puertas creadas: {len(doors)}")
    return doors


def _create_roof(size, location):
    """Crear techo"""
    x, y, z = size
    lx, ly, lz = location
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly, lz + z + 0.1))
    roof = bpy.context.active_object
    roof.name = "Roof"
    roof.scale = (x + 0.4, y + 0.4, 0.2)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material techo
    mat = bpy.data.materials.new("RoofMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1)
    roof.data.materials.append(mat)
    
    print("Techo creado")
    return roof


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_building_types():
    """Listar tipos de edificios disponibles"""
    return {k: v["description"] for k, v in BUILDING_TEMPLATES.items()}
