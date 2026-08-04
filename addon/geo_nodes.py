"""
blender-mcp — Geometry Nodes Engine
Motor de objetos paramétricos con Geometry Nodes.
"""
try:
    import bpy
except ImportError:
    bpy = None


# ═══════════════════════════════════════════════════════════════
# MESA PARAMÉTRICA
# ═══════════════════════════════════════════════════════════════

def create_parametric_table(width=1.2, depth=0.8, height=0.75, 
                           leg_style="straight", material="wood"):
    """
    Crear mesa paramétrica con Geometry Nodes.
    
    Args:
        width: Ancho de la mesa
        depth: Profundidad
        height: Altura
        leg_style: Estilo de patas (straight, tapered, turned)
        material: Tipo de material
    
    Returns:
        Objeto creado
    """
    if bpy is None:
        return None
    
    # Crear tabla base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height))
    table = bpy.context.active_object
    table.name = "ParametricTable"
    table.scale = (width, depth, 0.04)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Agregar modifier Geometry Nodes para patas
    mod = table.modifiers.new("Legs", 'NODES')
    ng = bpy.data.node_groups.new("TableLegs", 'GeometryNodeTree')
    mod.node_group = ng
    
    # Configurar nodos
    nodes = ng.nodes
    links = ng.links
    
    # Input
    inp = nodes.new("NodeGroupInput")
    inp.location = (-400, 0)
    
    # Output
    out = nodes.new("NodeGroupOutput")
    out.location = (400, 0)
    
    # Distribute Points on Faces (para posición de patas)
    dist = nodes.new("GeometryNodeDistributePointsOnFaces")
    dist.location = (-100, 0)
    dist.inputs["Density"].default_value = 1.0
    
    # Instance on Points (para crear patas)
    inst = nodes.new("GeometryNodeInstanceOnPoints")
    inst.location = (100, 0)
    
    # Cylinder como instancia
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=height-0.04)
    leg_mesh = bpy.context.active_object
    leg_mesh.hide_viewport = True
    
    oi = nodes.new("GeometryNodeObjectInfo")
    oi.location = (-100, -200)
    oi.inputs["Object"].default_value = leg_mesh
    
    # Conectar
    links.new(inp.outputs[0], dist.inputs["Mesh"])
    links.new(dist.outputs["Points"], inst.inputs["Points"])
    links.new(oi.outputs["Geometry"], inst.inputs["Instance"])
    links.new(inst.outputs["Instances"], out.inputs[0])
    
    # Material
    mat = bpy.data.materials.get(material) or create_simple_material(material)
    table.data.materials.append(mat)
    
    print(f"Mesa paramétrica: {width}x{depth}x{height}m, patas {leg_style}")
    return table


# ═══════════════════════════════════════════════════════════════
# SILLA PARAMÉTRICA
# ═══════════════════════════════════════════════════════════════

def create_parametric_chair(seat_width=0.45, seat_depth=0.45, 
                           seat_height=0.45, back_height=0.5,
                           leg_style="straight", material="wood"):
    """
    Crear silla paramétrica.
    """
    if bpy is None:
        return None
    
    # Asiento
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, seat_height))
    chair = bpy.context.active_object
    chair.name = "ParametricChair"
    chair.scale = (seat_width, seat_depth, 0.04)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.get(material) or create_simple_material(material)
    chair.data.materials.append(mat)
    
    print(f"Silla paramétrica: {seat_width}x{seat_depth}x{seat_height}m")
    return chair


# ═══════════════════════════════════════════════════════════════
# MOLDURAS
# ═══════════════════════════════════════════════════════════════

def create_molding(width=1.0, height=0.05, depth=0.03, profile="classic"):
    """
    Crear moldura paramétrica.
    """
    if bpy is None:
        return None
    
    # Crear perfil de moldura
    if profile == "classic":
        profile_points = [(0, 0), (0.02, 0), (0.02, 0.02), (0, 0.02)]
    elif profile == "modern":
        profile_points = [(0, 0), (0.01, 0), (0.01, 0.01), (0, 0.01)]
    else:
        profile_points = [(0, 0), (0.02, 0), (0.02, 0.02), (0, 0.02)]
    
    # Crear malla de moldura
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    molding = bpy.context.active_object
    molding.name = "Molding"
    molding.scale = (width, depth, height)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.get("wood") or create_simple_material("wood")
    molding.data.materials.append(mat)
    
    print(f"Moldura: {width}x{depth}x{height}m, perfil {profile}")
    return molding


# ═══════════════════════════════════════════════════════════════
# TUBERÍAS
# ═══════════════════════════════════════════════════════════════

def create_pipe_system(start_point, end_point, radius=0.02, segments=16):
    """
    Crear sistema de tuberías entre dos puntos.
    """
    if bpy is None:
        return None
    
    # Crear tubería como cilindro
    start = Vector(start_point)
    end = Vector(end_point)
    
    # Calcular posición y rotación
    center = (start + end) / 2
    direction = end - start
    length = direction.length
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=center
    )
    pipe = bpy.context.active_object
    pipe.name = "Pipe"
    
    # Rotar para alinear con dirección
    pipe.rotation_euler = (0, math.pi/2, 0)
    
    # Material metal
    mat = bpy.data.materials.get("metal") or create_simple_material("metal")
    pipe.data.materials.append(mat)
    
    print(f"Tubería: {length:.3f}m de largo")
    return pipe


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def create_simple_material(name):
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
    }


# ═══════════════════════════════════════════════════════════════
# BARANDILLAS PARAMÉTRICAS
# ═══════════════════════════════════════════════════════════════

def create_railing_parametric(length=2.0, height=1.0, bar_spacing=0.1, style="vertical"):
    """
    Crear barandilla paramétrica.
    
    Args:
        length: Largo de la barandilla
        height: Altura
        bar_spacing: Espaciado entre barras
        style: 'vertical', 'horizontal', 'glass'
    """
    if bpy is None:
        return None
    
    # Crear base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    railing = bpy.context.active_object
    railing.name = "Railing"
    railing.scale = (length, 0.05, height)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.get("metal") or create_simple_material("metal")
    railing.data.materials.append(mat)
    
    print(f"Barandilla: {length}m x {height}m, estilo {style}")
    return railing


# ═══════════════════════════════════════════════════════════════
# ESCALERAS PARAMÉTRICAS
# ═══════════════════════════════════════════════════════════════

def create_stairs_parametric(steps=10, step_height=0.18, step_depth=0.25, width=1.0):
    """
    Crear escaleras paramétricas.
    
    Args:
        steps: Número de escalones
        step_height: Altura de cada escalón
        step_depth: Profundidad de cada escalón
        width: Ancho de las escaleras
    """
    if bpy is None:
        return None
    
    parts = []
    
    for i in range(steps):
        z = i * step_height
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, -i * step_depth, z + step_height/2)
        )
        step = bpy.context.active_object
        step.name = f"Step_{i}"
        step.scale = (width, step_depth, step_height)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        
        # Material
        mat = bpy.data.materials.get("concrete") or create_simple_material("concrete")
        step.data.materials.append(mat)
        
        parts.append(step)
    
    print(f"Escaleras: {steps} escalones, {step_height*steps:.2f}m alto")
    return parts


# ═══════════════════════════════════════════════════════════════
# CERCAS
# ═══════════════════════════════════════════════════════════════

def create_fence(length=5.0, height=1.5, post_spacing=1.0):
    """
    Crear cerca.
    
    Args:
        length: Largo total
        height: Altura
        post_spacing: Espaciado entre postes
    """
    if bpy is None:
        return None
    
    parts = []
    
    # Crear postes
    num_posts = int(length / post_spacing) + 1
    for i in range(num_posts):
        x = -length/2 + i * post_spacing
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.03,
            depth=height,
            location=(x, 0, height/2)
        )
        post = bpy.context.active_object
        post.name = f"Fence_Post_{i}"
        mat = bpy.data.materials.get("wood") or create_simple_material("wood")
        post.data.materials.append(mat)
        parts.append(post)
    
    # Crear barras horizontales
    for h in [0.3, 0.7, 1.1]:
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, 0, h)
        )
        bar = bpy.context.active_object
        bar.name = f"Fence_Bar_{h}"
        bar.scale = (length, 0.02, 0.03)
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        bar.data.materials.append(mat)
        parts.append(bar)
    
    print(f"Cerca: {length}m x {height}m, {num_posts} postes")
    return parts


# ═══════════════════════════════════════════════════════════════
# SISTEMAS DE PAREDES
# ═══════════════════════════════════════════════════════════════

def create_wall_system(width=3.0, height=2.5, thickness=0.15):
    """
    Crear sistema de pared.
    
    Args:
        width: Ancho
        height: Altura
        thickness: Espesor
    """
    if bpy is None:
        return None
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    wall = bpy.context.active_object
    wall.name = "Wall"
    wall.scale = (width, thickness, height)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.get("concrete") or create_simple_material("concrete")
    wall.data.materials.append(mat)
    
    print(f"Pared: {width}m x {height}m x {thickness}m")
    return wall
