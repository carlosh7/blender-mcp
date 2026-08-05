"""
blender-mcp — PBR Factory
Motor de materiales PBR procedurales con nodos de Blender.
"""
try:
    import bpy
except ImportError:
    bpy = None


# ═══════════════════════════════════════════════════════════════
# MADERA PROCEDURAL
# ═══════════════════════════════════════════════════════════════

def create_pbr_wood(name, color=(0.45, 0.30, 0.15), grain_scale=10):
    """
    Crear material madera procedural con vetas y relieve.
    
    Args:
        name: Nombre del material
        color: Color base RGB
        grain_scale: Escala de las vetas
    
    Returns:
        Material creado
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Limpiar nodos existentes
    for n in nodes:
        nodes.remove(n)
    
    # Output
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    # Principled BSDF
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Metallic"].default_value = 0.0
    
    # Noise Texture (vetas de madera)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (0, 100)
    noise.inputs["Scale"].default_value = grain_scale
    noise.inputs["Detail"].default_value = 8
    
    # ColorRamp (colores de veta)
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (0, 0)
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (*color, 1)
    ramp.color_ramp.elements[1].position = 0.6
    ramp.color_ramp.elements[1].color = (color[0]*0.7, color[1]*0.7, color[2]*0.7, 1)
    
    # Bump (relieve)
    bump = nodes.new("ShaderNodeBump")
    bump.location = (0, -100)
    bump.inputs["Strength"].default_value = 0.3
    
    # Roughness Map (imperfecciones de superficie)
    rough_map = nodes.new("ShaderNodeMapRange")
    rough_map.location = (150, -50)
    rough_map.inputs["From Min"].default_value = 0.0
    rough_map.inputs["From Max"].default_value = 1.0
    rough_map.inputs["To Min"].default_value = 0.3
    rough_map.inputs["To Max"].default_value = 0.7
    
    # Conectar
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(noise.outputs["Fac"], rough_map.inputs["Value"])
    links.new(rough_map.outputs["Result"], bsdf.inputs["Roughness"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material madera PBR fotorrealista creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# TELA PROCEDURAL
# ═══════════════════════════════════════════════════════════════

def create_pbr_fabric(name, color=(0.6, 0.5, 0.4), weave_scale=50):
    """
    Crear material tela con relieve de tejido.
    
    Args:
        name: Nombre del material
        color: Color base RGB
        weave_scale: Escala del tejido
    
    Returns:
        Material creado
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Metallic"].default_value = 0.0
    
    # Voronoi (patrón de tejido)
    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.location = (0, 100)
    voronoi.inputs["Scale"].default_value = weave_scale
    voronoi.voronoi_dimensions = '3D'
    
    # Bump (relieve del tejido)
    bump = nodes.new("ShaderNodeBump")
    bump.location = (0, 0)
    bump.inputs["Strength"].default_value = 0.5
    
    # Conectar
    links.new(voronoi.outputs["Distance"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material tela creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# METAL CEPILLADO
# ═══════════════════════════════════════════════════════════════

def create_pbr_metal(name, color=(0.8, 0.8, 0.8), brushed=True):
    """
    Crear material metal cepillado.
    
    Args:
        name: Nombre del material
        color: Color base RGB
        brushed: Si tiene efecto cepillado
    
    Returns:
        Material creado
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.1
    
    if brushed:
        # Noise anisotrópico para efecto cepillado
        noise = nodes.new("ShaderNodeTexNoise")
        noise.location = (0, 100)
        noise.inputs["Scale"].default_value = 100
        noise.inputs["Distortion"].default_value = 2.0
        
        # Mapping para estirar en una dirección
        mapping = nodes.new("ShaderNodeMapping")
        mapping.location = (0, 0)
        mapping.inputs["Scale"].default_value = (10, 1, 1)
        
        # Conectar
        links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], bsdf.inputs["Roughness"])
    
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material metal creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# CUERO CON GRAIN
# ═══════════════════════════════════════════════════════════════

def create_pbr_leather(name, color=(0.35, 0.20, 0.10), grain_scale=30):
    """
    Crear material cuero con grano.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.6
    bsdf.inputs["Metallic"].default_value = 0.0
    
    # Voronoi (grano del cuero)
    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.location = (0, 100)
    voronoi.inputs["Scale"].default_value = grain_scale
    voronoi.voronoi_dimensions = '3D'
    
    # Bump (relieve)
    bump = nodes.new("ShaderNodeBump")
    bump.location = (0, 0)
    bump.inputs["Strength"].default_value = 0.4
    
    # Conectar
    links.new(voronoi.outputs["Distance"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material cuero creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# PIEDRA NATURAL
# ═══════════════════════════════════════════════════════════════

def create_pbr_stone(name, color=(0.5, 0.48, 0.45), detail=6):
    """
    Crear material piedra natural.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    bsdf.inputs["Metallic"].default_value = 0.0
    
    # Musgrave (vetas de piedra)
    musgrave = nodes.new("ShaderNodeTexMusgrave")
    musgrave.location = (0, 100)
    musgrave.inputs["Scale"].default_value = 3.0
    musgrave.inputs["Detail"].default_value = detail
    
    # Noise (variación)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (0, 0)
    noise.inputs["Scale"].default_value = 10
    
    # Bump
    bump = nodes.new("ShaderNodeBump")
    bump.location = (0, -100)
    bump.inputs["Strength"].default_value = 0.5
    
    # Conectar
    links.new(musgrave.outputs["Fac"], noise.inputs["Fac"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material piedra creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# VIDRIO REALISTA
# ═══════════════════════════════════════════════════════════════

def create_pbr_glass(name, color=(0.9, 0.95, 1.0), ior=1.45):
    """
    Crear material vidrio realista.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.0
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["IOR"].default_value = ior
    bsdf.inputs["Alpha"].default_value = 0.3
    
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material vidrio creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# CERÁMICA
# ═══════════════════════════════════════════════════════════════

def create_pbr_ceramic(name, color=(0.95, 0.95, 0.93), gloss=0.8):
    """
    Crear material cerámica.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 1.0 - gloss
    bsdf.inputs["Metallic"].default_value = 0.0
    
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material cerámica creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_pbr_materials():
    """Listar materiales PBR disponibles"""
    return {
        "wood": "Madera procedural",
        "fabric": "Tela con relieve",
        "metal": "Metal cepillado",
        "leather": "Cuero con grano",
        "stone": "Piedra natural",
        "glass": "Vidrio realista",
        "ceramic": "Cerámica",
        "plastic": "Plástico",
        "rubber": "Goma",
        "paper": "Papel",
        "bamboo": "Bambú",
        "concrete": "Concreto",
    }


# ═══════════════════════════════════════════════════════════════
# PLÁSTICO
# ═══════════════════════════════════════════════════════════════

def create_pbr_plastic(name, color=(0.8, 0.8, 0.8), glossy=0.8):
    """
    Crear material plástico.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 1.0 - glossy
    bsdf.inputs["Metallic"].default_value = 0.0
    
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material plástico creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# GOMA
# ═══════════════════════════════════════════════════════════════

def create_pbr_rubber(name, color=(0.1, 0.1, 0.1)):
    """
    Crear material goma.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.95
    bsdf.inputs["Metallic"].default_value = 0.0
    
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material goma creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# PAPEL
# ═══════════════════════════════════════════════════════════════

def create_pbr_paper(name, color=(0.95, 0.93, 0.90)):
    """
    Crear material papel.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    bsdf.inputs["Metallic"].default_value = 0.0
    
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material papel creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# BAMBÚ
# ═══════════════════════════════════════════════════════════════

def create_pbr_bamboo(name, color=(0.70, 0.60, 0.35)):
    """
    Crear material bambú.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.65
    bsdf.inputs["Metallic"].default_value = 0.0
    
    # Vetas de bambú
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (0, 100)
    noise.inputs["Scale"].default_value = 20
    
    bump = nodes.new("ShaderNodeBump")
    bump.location = (0, 0)
    bump.inputs["Strength"].default_value = 0.2
    
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material bambú creado: {name}")
    return mat


# ═══════════════════════════════════════════════════════════════
# CONCRETO
# ═══════════════════════════════════════════════════════════════

def create_pbr_concrete(name, color=(0.5, 0.48, 0.45)):
    """
    Crear material concreto.
    """
    if bpy is None:
        return None
    
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    
    # Musgrave (textura de concreto)
    musgrave = nodes.new("ShaderNodeTexMusgrave")
    musgrave.location = (0, 100)
    musgrave.inputs["Scale"].default_value = 5
    
    bump = nodes.new("ShaderNodeBump")
    bump.location = (0, 0)
    bump.inputs["Strength"].default_value = 0.3
    
    links.new(musgrave.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"Material concreto creado: {name}")
    return mat
