"""
blender-mcp — BMesh Builder
Motor de modelado profesional con bmesh.
Para crear objetos con calidad de estudio.
"""
try:
    import bpy
    import bmesh
except ImportError:
    bpy = None
    bmesh = None

import math
try:
    from mathutils import Vector, Matrix
except ImportError:
    Vector = None
    Matrix = None


# ═══════════════════════════════════════════════════════════════
# LATHE / REVOLUCIÓN
# ═══════════════════════════════════════════════════════════════

def create_lathe_mesh(profile_points, segments=32, height=1.0, location=(0, 0, 0)):
    """
    Crear malla por revolución de perfil 2D (ideal para patas, jarrones, molduras).
    
    Args:
        profile_points: Lista de puntos 2D [(x, y), ...]
        segments: Número de segmentos de revolución
        height: Altura de la malla
        location: Posición en la escena
    
    Returns:
        Objeto creado
    """
    if bpy is None or bmesh is None:
        return None
    
    # Crear malla vacía
    mesh = bpy.data.meshes.new("LatheMesh")
    bm = bmesh.new()
    
    # Crear vértices por revolución
    for i, (x, y) in enumerate(profile_points):
        angle = (i / len(profile_points)) * math.pi * 2
        for seg in range(segments):
            seg_angle = (seg / segments) * math.pi * 2
            vx = x * math.cos(seg_angle)
            vy = x * math.sin(seg_angle)
            vz = y
            bm.verts.new((vx, vy, vz))
    
    bm.verts.ensure_lookup_table()
    
    # Crear caras
    for seg in range(segments):
        for i in range(len(profile_points) - 1):
            v1 = seg * len(profile_points) + i
            v2 = seg * len(profile_points) + i + 1
            v3 = ((seg + 1) % segments) * len(profile_points) + i + 1
            v4 = ((seg + 1) % segments) * len(profile_points) + i
            
            bm.faces.new([bm.verts[v1], bm.verts[v2], bm.verts[v3], bm.verts[v4]])
    
    # Remover vértices duplicados y recalcular normales
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # Crear objeto
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
    
    obj = bpy.data.objects.new("LatheMesh", mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    
    # Aplicar smooth shading
    for poly in mesh.polygons:
        poly.use_smooth = True

    # Auto UV Unwrap
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
        obj.select_set(False)
    except Exception as e:
        print(f"Auto UV unwrap notice: {e}")
    
    print(f"Lathe mesh creado con Smart UV: {len(mesh.vertices)} vértices, {len(mesh.polygons)} caras")
    return obj


# ═══════════════════════════════════════════════════════════════
# BEVEL + SMOOTH
# ═══════════════════════════════════════════════════════════════

def apply_professional_finish(obj, bevel_width=0.01, bevel_segments=2, subsurf_levels=1):
    """
    Aplicar finish profesional: Bevel + Subdivision + Smooth.
    
    Args:
        obj: Objeto a mejorar
        bevel_width: Ancho del bevel
        bevel_segments: Segmentos del bevel
        subsurf_levels: Niveles de subdivisión
    """
    if bpy is None or obj is None:
        return False
    
    # 1. Bevel
    mod_bevel = obj.modifiers.new("Bevel", 'BEVEL')
    mod_bevel.width = bevel_width
    mod_bevel.segments = bevel_segments
    mod_bevel.limit_method = 'ANGLE'
    mod_bevel.angle_limit = math.radians(30)
    
    # 2. Subdivision
    if subsurf_levels > 0:
        mod_subsurf = obj.modifiers.new("Subdivision", 'SUBSURF')
        mod_subsurf.levels = subsurf_levels
        mod_subsurf.render_levels = subsurf_levels
    
    # 3. Smooth shading
    for poly in obj.data.polygons:
        poly.use_smooth = True
    
    # 4. Auto smooth
    if hasattr(obj.data, 'use_auto_smooth'):
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = math.radians(30)
    
    print(f"Professional finish applied: bevel={bevel_width}, subsurf={subsurf_levels}")
    return True


# ═══════════════════════════════════════════════════════════════
# BOOLEAN
# ═══════════════════════════════════════════════════════════════

def boolean_mesh(obj1, obj2, operation='DIFFERENCE'):
    """
    Aplicar operación booleana entre dos objetos.
    
    Args:
        obj1: Objeto base
        obj2: Objeto operador
        operation: 'UNION', 'DIFFERENCE', 'INTERSECT'
    """
    if bpy is None or obj1 is None or obj2 is None:
        return False
    
    mod = obj1.modifiers.new("Boolean", 'BOOLEAN')
    mod.operation = operation
    mod.object = obj2
    
    print(f"Boolean: {obj1.name} {operation} {obj2.name}")
    return True


# ═══════════════════════════════════════════════════════════════
# SUBDIVISION
# ═══════════════════════════════════════════════════════════════

def subdivide_mesh(obj, levels=2):
    """
    Aplicar subdivision surface.
    
    Args:
        obj: Objeto a subdividir
        levels: Niveles de subdivisión
    """
    if bpy is None or obj is None:
        return False
    
    mod = obj.modifiers.new("Subdivision", 'SUBSURF')
    mod.levels = levels
    mod.render_levels = levels
    
    print(f"Subdivision applied: {levels} levels")
    return True


# ═══════════════════════════════════════════════════════════════
# MIRROR
# ═══════════════════════════════════════════════════════════════

def mirror_mesh(obj, axis='X'):
    """
    Aplicar mirror.
    
    Args:
        obj: Objeto a reflejar
        axis: 'X', 'Y', 'Z'
    """
    if bpy is None or obj is None:
        return False
    
    mod = obj.modifiers.new("Mirror", 'MIRROR')
    mod.use_x = axis == 'X'
    mod.use_y = axis == 'Y'
    mod.use_z = axis == 'Z'
    
    print(f"Mirror applied: {axis}")
    return True


# ═══════════════════════════════════════════════════════════════
# ARRAY
# ═══════════════════════════════════════════════════════════════

def array_mesh(obj, count=2, offset=(1, 0, 0)):
    """
    Aplicar array.
    
    Args:
        obj: Objeto a duplicar
        count: Número de copias
        offset: Desplazamiento entre copias
    """
    if bpy is None or obj is None:
        return False
    
    mod = obj.modifiers.new("Array", 'ARRAY')
    mod.count = count
    mod.use_relative_offset = False
    mod.use_constant_offset = True
    mod.constant_offset_displace = offset
    
    print(f"Array applied: {count} copies")
    return True


# ═══════════════════════════════════════════════════════════════
# EXTRUDE PROFILE
# ═══════════════════════════════════════════════════════════════

def extrude_profile(profile_points, depth=0.1, location=(0, 0, 0)):
    """
    Crear malla extruyendo un perfil 2D.
    
    Args:
        profile_points: Lista de puntos 2D [(x, y), ...]
        depth: Profundidad de extrusión
        location: Posición en la escena
    """
    if bpy is None or bmesh is None:
        return None
    
    # Crear malla
    mesh = bpy.data.meshes.new("ExtrudeMesh")
    bm = bmesh.new()
    
    # Crear vértices del perfil
    for x, y in profile_points:
        bm.verts.new((x, 0, y))
    
    bm.verts.ensure_lookup_table()
    
    # Crear cara
    bm.faces.new(bm.verts)
    
    # Extruir
    geom = bm.faces[:]
    extruded = bmesh.ops.extrude_face_region(bm, geom=geom)
    bmesh.ops.translate(bm, verts=extruded["geom"], vec=(0, depth, 0))
    
    # Crear objeto
    bm.to_mesh(mesh)
    mesh.update()
    
    obj = bpy.data.objects.new("ExtrudeMesh", mesh)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    
    # Smooth shading
    for poly in mesh.polygons:
        poly.use_smooth = True
    
    print(f"Extrude mesh creado: {len(mesh.vertices)} vértices")
    return obj


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def get_mesh_info(obj):
    """Obtener información de la malla"""
    if obj is None or obj.type != 'MESH':
        return None
    
    return {
        "name": obj.name,
        "vertices": len(obj.data.vertices),
        "edges": len(obj.data.edges),
        "faces": len(obj.data.polygons),
        "has_smooth": any(p.use_smooth for p in obj.data.polygons),
        "has_bevel": any(m.type == 'BEVEL' for m in obj.modifiers),
        "has_subsurf": any(m.type == 'SUBSURF' for m in obj.modifiers),
    }


def list_mesh_tools():
    """Listar herramientas de mesh disponibles"""
    return {
        "create_lathe_mesh": "Revolución de perfiles",
        "apply_professional_finish": "Bevel + Smooth",
        "boolean_mesh": "Operaciones booleanas",
        "subdivide_mesh": "Subdivision Surface",
        "mirror_mesh": "Simetría",
        "array_mesh": "Repetición",
        "extrude_profile": "Extrusión de perfil",
        "inset_faces": "Inset de caras",
        "knife_cut": "Corte con cuchillo",
        "vertex_colors": "Colores por vértice",
        "edge_slide": "Deslizar aristas",
        "weld_vertices": "Soldar vértices",
        "bridge_edge_loops": "Conectar edge loops",
    }


# ═══════════════════════════════════════════════════════════════
# INSET FACES
# ═══════════════════════════════════════════════════════════════

def inset_faces(obj, thickness=0.1):
    """
    Aplicar inset a caras seleccionadas.
    
    Args:
        obj: Objeto mesh
        thickness: Grosor del inset
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.inset(thickness=thickness)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Inset applied: thickness={thickness}")
    return True


# ═══════════════════════════════════════════════════════════════
# KNIFE CUT
# ═══════════════════════════════════════════════════════════════

def knife_cut(obj, points):
    """
    Aplicar corte con cuchillo.
    
    Args:
        obj: Objeto mesh
        points: Lista de puntos de corte [(x,y,z), ...]
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Knife project
    for i in range(len(points) - 1):
        p1 = Vector(points[i])
        p2 = Vector(points[i + 1])
        
        # Crear línea de corte
        bpy.ops.mesh.vert_connect(path=[p1, p2])
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Knife cut: {len(points)} points")
    return True


# ═══════════════════════════════════════════════════════════════
# VERTEX COLORS
# ═══════════════════════════════════════════════════════════════

def vertex_colors(obj, color=(1, 0, 0)):
    """
    Aplicar color por vértice.
    
    Args:
        obj: Objeto mesh
        color: Tupla RGBA (0-1)
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    # Crear vertex color layer
    if not obj.data.vertex_colors:
        obj.data.vertex_colors.new()
    
    color_layer = obj.data.vertex_colors.active
    
    # Asignar color a todas las caras
    for poly in obj.data.polygons:
        for loop_idx in poly.loop_indices:
            color_layer.data[loop_idx].color = (*color, 1)
    
    print(f"Vertex colors applied: {color}")
    return True


# ═══════════════════════════════════════════════════════════════
# EDGE SLIDE
# ═══════════════════════════════════════════════════════════════

def edge_slide(obj, edge_index, factor=0.5):
    """
    Deslizar arista.
    
    Args:
        obj: Objeto mesh
        edge_index: Índice de la arista
        factor: Factor de deslizamiento (0-1)
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Seleccionar arista
    bm = bmesh.from_edit_mesh(obj.data)
    if edge_index < len(bm.edges):
        bm.edges[edge_index].select = True
        bmesh.update_edit_mesh(obj.data)
    
    # Edge slide
    bpy.ops.mesh.edge_slide(factor=factor)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Edge slide: factor={factor}")
    return True


# ═══════════════════════════════════════════════════════════════
# WELD VERTICES
# ═══════════════════════════════════════════════════════════════

def weld_vertices(obj, distance=0.01):
    """
    Soldar vértices cercanos.
    
    Args:
        obj: Objeto mesh
        distance: Distancia máxima de weld
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=distance)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Weld vertices: distance={distance}")
    return True


# ═══════════════════════════════════════════════════════════════
# BRIDGE EDGE LOOPS
# ═══════════════════════════════════════════════════════════════

def bridge_edge_loops(obj):
    """
    Conectar edge loops.
    """
    if bpy is None or obj is None or obj.type != 'MESH':
        return False
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bridge_edge_loops()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print("Bridge edge loops applied")
    return True
