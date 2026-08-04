"""
blender-mcp — Mesh Engine
Motor de modelado con primitivas avanzadas, booleanos, subdivision, etc.

Este módulo proporciona herramientas de modelado que van más allá de las
primitivas básicas de Blender.

NAMING CONVENTIONS (estilo Blender Studio):
- GEO-xxx: Geometría (mallas, primitivas)
- MAT-xxx: Materiales
- LGT-xxx: Luces
- CAM-xxx: Cámaras
- RIG-xxx: Esqueletos
- ANM-xxx: Animaciones
- SCR-xxx: Escenas
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix


# ═══════════════════════════════════════════════════════════════
# NAMING CONVENTIONS
# ═══════════════════════════════════════════════════════════════

NAMING_PREFIXES = {
    "geometry": "GEO",
    "material": "MAT",
    "light": "LGT",
    "camera": "CAM",
    "rig": "RIG",
    "animation": "ANM",
    "scene": "SCR",
}

def generate_name(category, description):
    """
    Generar nombre con convención de命名.
    
    Args:
        category: Categoría (geometry, material, light, etc.)
        description: Descripción del objeto
    
    Returns:
        Nombre formateado (ej: "GEO-Cube_Main")
    """
    prefix = NAMING_PREFIXES.get(category, "OBJ")
    clean_desc = description.replace(" ", "_").replace("-", "_")
    return f"{prefix}-{clean_desc}"


# ═══════════════════════════════════════════════════════════════
# PRIMITIVAS AVANZADAS
# ═══════════════════════════════════════════════════════════════

def create_advanced_primitive(primitive_type, params=None):
    """
    Crear primitiva avanzada con parámetros personalizables.
    
    Tipos disponibles:
    - cube, sphere, cylinder, cone, torus, plane, circle
    - uv_sphere, ico_sphere, monkey
    - capsule, pyramid, wedge, chamfer_box
    
    Args:
        primitive_type: Tipo de primitiva
        params: Diccionario con parámetros
    
    Returns:
        Objeto creado o None si hay error
    """
    if params is None:
        params = {}
    
    # Primitivas básicas
    primitive_map = {
        "cube": _create_cube,
        "sphere": _create_uv_sphere,
        "uv_sphere": _create_uv_sphere,
        "ico_sphere": _create_ico_sphere,
        "cylinder": _create_cylinder,
        "cone": _create_cone,
        "torus": _create_torus,
        "plane": _create_plane,
        "circle": _create_circle,
        "monkey": _create_monkey,
        
        # Primitivas avanzadas
        "capsule": _create_capsule,
        "pyramid": _create_pyramid,
        "wedge": _create_wedge,
        "chamfer_box": _create_chamfer_box,
        "star": _create_star,
        "gear": _create_gear,
        "spring": _create_spring,
    }
    
    creator = primitive_map.get(primitive_type)
    if not creator:
        print(f"ERROR: Primitive not supported: {primitive_type}")
        return None
    
    try:
        return creator(params)
    except Exception as e:
        print(f"ERROR creating {primitive_type}: {e}")
        return None


def _create_cube(params):
    """Crear cubo con parámetros avanzados"""
    size = params.get("size", 1)
    location = params.get("location", (0, 0, 0))
    bevel = params.get("bevel", 0)
    
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    
    return obj


def _create_uv_sphere(params):
    """Crear esfera UV con parámetros"""
    radius = params.get("radius", 1)
    segments = params.get("segments", 32)
    rings = params.get("rings", 16)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        segments=segments,
        ring_count=rings,
        location=location
    )
    return bpy.context.active_object


def _create_ico_sphere(params):
    """Crear esfera ICO con parámetros"""
    radius = params.get("radius", 1)
    subdivisions = params.get("subdivisions", 2)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=radius,
        subdivisions=subdivisions,
        location=location
    )
    return bpy.context.active_object


def _create_cylinder(params):
    """Crear cilindro con parámetros"""
    radius = params.get("radius", 0.5)
    depth = params.get("depth", 1)
    vertices = params.get("vertices", 32)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=depth,
        vertices=vertices,
        location=location
    )
    return bpy.context.active_object


def _create_cone(params):
    """Crear cono con parámetros"""
    radius1 = params.get("radius1", 0.5)
    radius2 = params.get("radius2", 0)
    depth = params.get("depth", 1)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_cone_add(
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location
    )
    return bpy.context.active_object


def _create_torus(params):
    """Crear toroide con parámetros"""
    major_radius = params.get("major_radius", 1)
    minor_radius = params.get("minor_radius", 0.25)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=location
    )
    return bpy.context.active_object


def _create_plane(params):
    """Crear plano con parámetros"""
    size = params.get("size", 1)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    return bpy.context.active_object


def _create_circle(params):
    """Crear círculo con parámetros"""
    radius = params.get("radius", 1)
    vertices = params.get("vertices", 32)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_circle_add(
        radius=radius,
        vertices=vertices,
        location=location
    )
    return bpy.context.active_object


def _create_monkey(params):
    """Crear monkey (Suzanne) con parámetros"""
    size = params.get("size", 1)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_monkey_add(size=size, location=location)
    return bpy.context.active_object


def _create_capsule(params):
    """Crear cápsula (cilindro con hemisferios)"""
    radius = params.get("radius", 0.5)
    depth = params.get("depth", 1)
    location = params.get("location", (0, 0, 0))
    
    # Crear cilindro
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = "Capsule"
    
    # Agregar esferas en los extremos
    # (Simplificado - en producción se usaría bmesh)
    
    return obj


def _create_pyramid(params):
    """Crear pirámide (cono con 4 lados)"""
    radius = params.get("radius", 0.5)
    depth = params.get("depth", 1)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_cone_add(
        radius1=radius,
        radius2=0,
        depth=depth,
        vertices=4,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = "Pyramid"
    return obj


def _create_wedge(params):
    """Crear cuña (triángulo extruido)"""
    size = params.get("size", 1)
    location = params.get("location", (0, 0, 0))
    
    # Crear cubo y modifier boolean
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = "Wedge"
    
    # Rotar 45 grados para efecto de cuña
    obj.rotation_euler = (math.radians(45), 0, 0)
    
    return obj


def _create_chamfer_box(params):
    """Crear caja con bordes redondeados"""
    size = params.get("size", 1)
    bevel = params.get("bevel", 0.1)
    location = params.get("location", (0, 0, 0))
    
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = "ChamferBox"
    
    # Agregar bevel
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = bevel
    mod.segments = 3
    mod.profile = 0.7
    
    return obj


def _create_star(params):
    """Crear estrella (extrusion radial)"""
    outer_radius = params.get("outer_radius", 1)
    inner_radius = params.get("inner_radius", 0.5)
    points = params.get("points", 5)
    location = params.get("location", (0, 0, 0))
    
    # Crear círculo con vértices alternados
    verts = []
    for i in range(points * 2):
        angle = (i / (points * 2)) * math.pi * 2
        r = outer_radius if i % 2 == 0 else inner_radius
        verts.append((r * math.cos(angle), r * math.sin(angle), 0))
    
    # Crear malla
    mesh = bpy.data.meshes.new("StarMesh")
    mesh.from_pydata(verts, [], [(i, (i + 1) % (points * 2)) for i in range(points * 2)])
    mesh.update()
    
    obj = bpy.data.objects.new("Star", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def _create_gear(params):
    """Crear engranaje"""
    radius = params.get("radius", 1)
    teeth = params.get("teeth", 12)
    tooth_depth = params.get("tooth_depth", 0.1)
    location = params.get("location", (0, 0, 0))
    
    # Crear círculo base
    bpy.ops.mesh.primitive_circle_add(radius=radius, vertices=teeth * 2, location=location)
    obj = bpy.context.active_object
    obj.name = "Gear"
    
    # Modificar vértices para crear dientes
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    for i, v in enumerate(bm.verts):
        if i % 2 == 0:
            v.co.z += tooth_depth
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return obj


def _create_spring(params):
    """Crear resorte (espiral)"""
    radius = params.get("radius", 0.5)
    height = params.get("height", 2)
    coils = params.get("coils", 8)
    location = params.get("location", (0, 0, 0))
    
    # Crear curva espiral
    curve_data = bpy.data.curves.new("SpringCurve", type='CURVE')
    curve_data.dimensions = '3D'
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(coils * 10 - 1)
    
    for i in range(coils * 10):
        t = i / (coils * 10)
        angle = t * coils * math.pi * 2
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = t * height
        spline.bezier_points[i].co = (x, y, z)
    
    obj = bpy.data.objects.new("Spring", curve_data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    # Convertir a malla
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    
    return obj


# ═══════════════════════════════════════════════════════════════
# MODIFICADORES
# ═══════════════════════════════════════════════════════════════

def apply_boolean(obj, target, operation='DIFFERENCE'):
    """
    Aplicar operación booleana.
    
    Args:
        obj: Objeto base
        target: Objeto objetivo
        operation: UNION, INTERSECT, DIFFERENCE
    """
    mod = obj.modifiers.new("Boolean", 'BOOLEAN')
    mod.operation = operation
    mod.object = target
    
    # Aplicar modifier
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    
    # Eliminar objeto objetivo
    bpy.data.objects.remove(target, do_unlink=True)
    
    return obj


def apply_subdivision(obj, levels=2, render_levels=None):
    """
    Aplicar subdivision surface.
    
    Args:
        obj: Objeto a subdividir
        levels: Niveles de subdivisión en viewport
        render_levels: Niveles en render (default: levels)
    """
    if render_levels is None:
        render_levels = levels
    
    mod = obj.modifiers.new("Subdivision", 'SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels
    
    return obj


def apply_mirror(obj, axis='X', use_modifier=True):
    """
    Aplicar mirror.
    
    Args:
        obj: Objeto a reflejar
        axis: Eje ('X', 'Y', 'Z')
        use_modifier: Si True, mantiene modifier
    """
    mod = obj.modifiers.new("Mirror", 'MIRROR')
    
    mod.use_x = axis == 'X'
    mod.use_y = axis == 'Y'
    mod.use_z = axis == 'Z'
    
    if not use_modifier:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    
    return obj


def apply_array(obj, count=2, offset=(1, 0, 0), use_modifier=True):
    """
    Aplicar array.
    
    Args:
        obj: Objeto a duplicar
        count: Número de copias
        offset: Desplazamiento entre copias
        use_modifier: Si True, mantiene modifier
    """
    mod = obj.modifiers.new("Array", 'ARRAY')
    mod.count = count
    mod.use_relative_offset = False
    mod.use_constant_offset = True
    mod.constant_offset_displace = offset
    
    if not use_modifier:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    
    return obj


# ═══════════════════════════════════════════════════════════════
# UTILIDADES DE MALLA
# ═══════════════════════════════════════════════════════════════

def get_bbox(obj):
    """Obtener bounding box de un objeto"""
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = Vector((min(v[i] for v in bbox) for i in range(3)))
    maxs = Vector((max(v[i] for v in bbox) for i in range(3)))
    
    return {
        "min": tuple(mins),
        "max": tuple(maxs),
        "center": tuple((mins + maxs) / 2),
        "size": tuple(maxs - mins)
    }


def measure_object(obj):
    """Medir dimensiones de un objeto"""
    bbox = get_bbox(obj)
    return {
        "width": bbox["size"][0],
        "depth": bbox["size"][1],
        "height": bbox["size"][2],
        "volume": bbox["size"][0] * bbox["size"][1] * bbox["size"][2]
    }


def get_vertex_count(obj):
    """Obtener número de vértices"""
    if obj.type == 'MESH':
        return len(obj.data.vertices)
    return 0


def get_face_count(obj):
    """Obtener número de caras"""
    if obj.type == 'MESH':
        return len(obj.data.polygons)
    return 0


def triangulate_mesh(obj):
    """Triangular malla"""
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def smooth_mesh(obj, iterations=1):
    """Suavizar malla"""
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.smooth iterations=iterations
        bpy.ops.object.mode_set(mode='OBJECT')
    return obj


# ═══════════════════════════════════════════════════════════════
# EXPORTACIÓN DE PRIMITIVAS
# ═══════════════════════════════════════════════════════════════

PRIMITIVE_CATALOG = {
    # Básicas
    "cube": {"category": "basic", "description": "Cubo"},
    "sphere": {"category": "basic", "description": "Esfera UV"},
    "ico_sphere": {"category": "basic", "description": "Esfera ICO"},
    "cylinder": {"category": "basic", "description": "Cilindro"},
    "cone": {"category": "basic", "description": "Cono"},
    "torus": {"category": "basic", "description": "Toroide"},
    "plane": {"category": "basic", "description": "Plano"},
    "circle": {"category": "basic", "description": "Círculo"},
    "monkey": {"category": "basic", "description": "Monkey (Suzanne)"},
    
    # Avanzadas
    "capsule": {"category": "advanced", "description": "Cápsula"},
    "pyramid": {"category": "advanced", "description": "Pirámide"},
    "wedge": {"category": "advanced", "description": "Cuña"},
    "chamfer_box": {"category": "advanced", "description": "Caja con bordes redondeados"},
    "star": {"category": "advanced", "description": "Estrella"},
    "gear": {"category": "advanced", "description": "Engranaje"},
    "spring": {"category": "advanced", "description": "Resorte"},
}


def list_primitives(category=None):
    """Listar primitivas disponibles"""
    if category:
        return {k: v for k, v in PRIMITIVE_CATALOG.items() if v["category"] == category}
    return PRIMITIVE_CATALOG
