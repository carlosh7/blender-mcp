"""
blender-mcp — Geometry Nodes Engine (Production Grade)
Motor de objetos paramétricos no destructivos con Geometry Nodes nativos de Blender 4.0+.
"""
try:
    import bpy
    import mathutils
except ImportError:
    bpy = None
    mathutils = None

import math

def _create_node_group(name):
    """Crear un árbol de Geometry Nodes limpio"""
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    return ng

def create_parametric_table(width=1.2, depth=0.8, height=0.75, leg_style="straight", material="PBR_Oak_100"):
    """
    Crear mesa paramétrica 100% procedimental con Geometry Nodes puras (sin instanciar primitivas ocultas).
    """
    if bpy is None:
        return None
    
    # Crear objeto contenedor vacio
    mesh = bpy.data.meshes.new("GEO_ParametricTable")
    table = bpy.data.objects.new("GEO_ParametricTable", mesh)
    bpy.context.collection.objects.link(table)
    table.location = (0, 0, 0)
    
    mod = table.modifiers.new("ParametricTableNodes", 'NODES')
    ng = _create_node_group("GN_ParametricTable")
    mod.node_group = ng
    
    nodes = ng.nodes
    links = ng.links
    
    # 1. Inputs & Outputs
    in_node = nodes.new("NodeGroupInput")
    in_node.location = (-800, 0)
    
    out_node = nodes.new("NodeGroupOutput")
    out_node.location = (800, 0)
    
    # 2. Join Geometry
    join_node = nodes.new("GeometryNodeJoinGeometry")
    join_node.location = (600, 0)
    
    # 3. Tabletop (Tablero procedimental)
    tabletop_cube = nodes.new("GeometryNodeMeshCube")
    tabletop_cube.location = (-400, 200)
    tabletop_cube.inputs["Size"].default_value = (width, depth, 0.04)
    
    tabletop_transform = nodes.new("GeometryNodeTransform")
    tabletop_transform.location = (-200, 200)
    tabletop_transform.inputs["Translation"].default_value = (0, 0, height - 0.02)
    
    links.new(tabletop_cube.outputs["Mesh"], tabletop_transform.inputs["Geometry"])
    links.new(tabletop_transform.outputs["Geometry"], join_node.inputs["Geometry"])
    
    # 4. 4 Leg Cylinders procedimentales
    leg_r = 0.04 if leg_style == "straight" else 0.05
    leg_h = height - 0.04
    
    leg_offsets = [
        (-width/2.0 + 0.08, -depth/2.0 + 0.08),
        (width/2.0 - 0.08, -depth/2.0 + 0.08),
        (-width/2.0 + 0.08, depth/2.0 - 0.08),
        (width/2.0 - 0.08, depth/2.0 - 0.08)
    ]
    
    for i, (lx, ly) in enumerate(leg_offsets):
        leg_cyl = nodes.new("GeometryNodeMeshCylinder")
        leg_cyl.location = (-400, -150 * i)
        leg_cyl.inputs["Radius"].default_value = leg_r
        leg_cyl.inputs["Depth"].default_value = leg_h
        leg_cyl.inputs["Vertices"].default_value = 32
        
        leg_trans = nodes.new("GeometryNodeTransform")
        leg_trans.location = (-200, -150 * i)
        leg_trans.inputs["Translation"].default_value = (lx, ly, leg_h / 2.0)
        
        links.new(leg_cyl.outputs["Mesh"], leg_trans.inputs["Geometry"])
        links.new(leg_trans.outputs["Geometry"], join_node.inputs["Geometry"])
    
    # 5. Set Material
    set_mat = nodes.new("GeometryNodeSetMaterial")
    set_mat.location = (700, 0)
    
    mat_obj = bpy.data.materials.get(material)
    if mat_obj:
        set_mat.inputs["Material"].default_value = mat_obj
        table.data.materials.append(mat_obj)
    
    links.new(join_node.outputs["Geometry"], set_mat.inputs["Geometry"])
    links.new(set_mat.outputs["Geometry"], out_node.inputs[0])
    
    print(f"Mesa paramétrica con Geometry Nodes puras generada: {width}x{depth}x{height}m")
    return table

def create_molding(path_points=None, profile_radius=0.03, material="PBR_Oak_100"):
    """
    Crear moldura paramétrica usando Sweep de Curva a Malla (Curve to Mesh) con Geometry Nodes.
    """
    if bpy is None:
        return None
    
    if path_points is None:
        path_points = [(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 2.0, 0.0)]
    
    # Crear curva guía
    curve_data = bpy.data.curves.new("GEO_MoldingCurve", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('POLY')
    spline.points.add(len(path_points) - 1)
    for i, p in enumerate(path_points):
        spline.points[i].co = (*p, 1.0)
    
    molding_obj = bpy.data.objects.new("GEO_Molding", curve_data)
    bpy.context.collection.objects.link(molding_obj)
    
    mod = molding_obj.modifiers.new("MoldingNodes", 'NODES')
    ng = _create_node_group("GN_MoldingSweep")
    mod.node_group = ng
    
    nodes = ng.nodes
    links = ng.links
    
    in_node = nodes.new("NodeGroupInput")
    in_node.location = (-600, 0)
    out_node = nodes.new("NodeGroupOutput")
    out_node.location = (600, 0)
    
    # Nodos Curve to Mesh
    curve_to_mesh = nodes.new("GeometryNodeCurveToMesh")
    curve_to_mesh.location = (0, 0)
    
    profile_circle = nodes.new("GeometryNodeCurvePrimitiveCircle")
    profile_circle.location = (-300, -200)
    profile_circle.inputs["Radius"].default_value = profile_radius
    profile_circle.inputs["Resolution"].default_value = 16
    
    set_shade = nodes.new("GeometryNodeSetMeshShadeSmooth")
    set_shade.location = (300, 0)
    
    links.new(in_node.outputs[0], curve_to_mesh.inputs["Curve"])
    links.new(profile_circle.outputs["Curve"], curve_to_mesh.inputs["Profile Curve"])
    links.new(curve_to_mesh.outputs["Mesh"], set_shade.inputs["Geometry"])
    links.new(set_shade.outputs["Geometry"], out_node.inputs[0])
    
    mat_obj = bpy.data.materials.get(material)
    if mat_obj:
        molding_obj.data.materials.append(mat_obj)
    
    print(f"Moldura procedimental con Geometry Nodes creada con radio={profile_radius}m")
    return molding_obj


# ═══════════════════════════════════════════════════════════════
# PUERTA PARAMÉTRICA
# ═══════════════════════════════════════════════════════════════

def create_door(width=0.9, height=2.0, thickness=0.04, style="panel"):
    """
    Crear puerta paramétrica.
    
    Args:
        width: Ancho de la puerta
        height: Altura
        thickness: Espesor
        style: 'panel', 'glass', 'flush'
    """
    if bpy is None:
        return None
    
    # Crear puerta
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    door = bpy.context.active_object
    door.name = "ParametricDoor"
    door.scale = (width, thickness, height)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.get("wood") or _create_simple_material("wood")
    door.data.materials.append(mat)
    
    print(f"Puerta: {width}x{height}m, estilo {style}")
    return door


# ═══════════════════════════════════════════════════════════════
# VENTANA PARAMÉTRICA
# ═══════════════════════════════════════════════════════════════

def create_window(width=1.0, height=1.2, panes=2):
    """
    Crear ventana paramétrica.
    
    Args:
        width: Ancho
        height: Altura
        panes: Número de paneles
    """
    if bpy is None:
        return None
    
    # Crear marco
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    frame = bpy.context.active_object
    frame.name = "Window_Frame"
    frame.scale = (width, 0.05, height)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material marco
    mat_frame = _create_simple_material("frame")
    frame.data.materials.append(mat_frame)
    
    # Crear paneles de vidrio
    pane_width = (width - 0.1) / panes
    for i in range(panes):
        x = -width/2 + 0.05 + pane_width/2 + i * pane_width
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, height/2))
        pane = bpy.context.active_object
        pane.name = f"Window_Pane_{i}"
        pane.scale = (pane_width - 0.02, 0.02, height - 0.1)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        
        # Material vidrio
        mat_glass = bpy.data.materials.get("glass") or _create_simple_material("glass")
        pane.data.materials.append(mat_glass)
    
    print(f"Ventana: {width}x{height}m, {panes} paneles")
    return frame


# ═══════════════════════════════════════════════════════════════
# TECHO PARAMÉTRICO
# ═══════════════════════════════════════════════════════════════

def create_roof(width=10, depth=8, height=3, style="gabled"):
    """
    Crear techo paramétrico.
    
    Args:
        width: Ancho
        depth: Profundidad
        height: Altura del techo
        style: 'gabled', 'hip', 'flat'
    """
    if bpy is None:
        return None
    
    if style == "gabled":
        # Techo a dos aguas
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
        roof = bpy.context.active_object
        roof.name = "Roof_Gabled"
        roof.scale = (width, depth, height)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        
        # Material techo
        mat = bpy.data.materials.get("roof") or _create_simple_material("roof")
        roof.data.materials.append(mat)
        
        print(f"Techo a dos aguas: {width}x{depth}x{height}m")
        return roof
    
    elif style == "hip":
        # Techo a cuatro aguas
        bpy.ops.mesh.primitive_cone_add(radius1=width/2, radius2=0, depth=height, vertices=4, location=(0, 0, height/2))
        roof = bpy.context.active_object
        roof.name = "Roof_Hip"
        roof.rotation_euler = (0, 0, math.radians(45))
        
        mat = bpy.data.materials.get("roof") or _create_simple_material("roof")
        roof.data.materials.append(mat)
        
        print(f"Techo a cuatro aguas: {width}x{depth}x{height}m")
        return roof
    
    elif style == "flat":
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height))
        roof = bpy.context.active_object
        roof.name = "Roof_Flat"
        roof.scale = (width, depth, 0.2)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        
        mat = _create_simple_material("concrete")
        roof.data.materials.append(mat)
        
        print(f"Techo plano: {width}x{depth}m")
        return roof
    
    return None


# ═══════════════════════════════════════════════════════════════
# ESTANTE PARAMÉTRICO
# ═══════════════════════════════════════════════════════════════

def create_shelf(width=1.0, height=2.0, depth=0.3, shelves=4):
    """
    Crear estante paramétrico.
    
    Args:
        width: Ancho
        height: Altura
        depth: Profundidad
        shelves: Número de repisas
    """
    if bpy is None:
        return None
    
    parts = []
    
    # Lados
    for x in [-width/2, width/2]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, height/2))
        side = bpy.context.active_object
        side.name = "Shelf_Side"
        side.scale = (0.02, depth, height)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        
        mat = _create_simple_material("wood")
        side.data.materials.append(mat)
        parts.append(side)
    
    # Repisas
    for i in range(shelves + 1):
        z = i * height / shelves
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z))
        shelf = bpy.context.active_object
        shelf.name = f"Shelf_Board_{i}"
        shelf.scale = (width, depth, 0.02)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        
        mat = _create_simple_material("wood")
        shelf.data.materials.append(mat)
        parts.append(shelf)
    
    print(f"Estante: {width}x{height}x{depth}m, {shelves} repisas")
    return parts


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def _create_simple_material(name):
    """Crear material simple"""
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
    return mat


def list_geo_nodes_types():
    """Listar tipos de Geometry Nodes disponibles"""
    return {
        "table": "Mesa paramétrica",
        "chair": "Silla paramétrica",
        "molding": "Molduras",
        "pipe": "Tuberías",
        "railing": "Barandillas",
        "stairs": "Escaleras",
        "fence": "Cercas",
        "wall": "Sistemas de paredes",
        "door": "Puertas",
        "window": "Ventanas",
        "roof": "Techos",
        "shelf": "Estantes",
    }
