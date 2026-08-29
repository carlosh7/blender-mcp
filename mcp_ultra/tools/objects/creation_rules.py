"""
blender-mcp — Creation Rules
Dimensiones estándar, conexiones padre-hijo, colecciones, validación.

Regla de oro: SIEMPRE usar estas funciones para crear objetos.
NUNCA crear objetos sueltos sin conexión.
"""

import bpy
from mathutils import Vector

# ═══════════════════════════════════════════════════════════════
# DIMENSIONES ESTÁNDAR (en metros)
# ═══════════════════════════════════════════════════════════════

STANDARD_OBJECTS = {
    "chair": {
        "description": "Silla de escritorio estándar",
        "seat": {"w": 0.45, "d": 0.45, "h": 0.04},
        "leg": {"r": 0.02, "h": 0.45},
        "backrest": {"w": 0.40, "h": 0.50, "bar_r": 0.015, "bars": 3},
        "total_height": 0.94,
        "material": {"color": (0.4, 0.25, 0.12), "roughness": 0.7, "metallic": 0.0},
    },
    "table": {
        "description": "Mesa de escritorio",
        "top": {"w": 1.20, "d": 0.80, "h": 0.04},
        "leg": {"w": 0.05, "d": 0.05, "h": 0.75},
        "drawer": {"w": 0.35, "d": 0.18, "h": 0.10},
        "total_height": 0.79,
        "material": {"color": (0.3, 0.18, 0.08), "roughness": 0.65, "metallic": 0.0},
    },
    "cup": {
        "description": "Taza de café con plato",
        "body": {"r": 0.04, "h": 0.10},
        "handle": {"r": 0.03, "tube_r": 0.005},
        "plate": {"r": 0.07, "h": 0.01},
        "total_height": 0.11,
        "material": {"color": (0.95, 0.95, 0.93), "roughness": 0.15, "metallic": 0.0},
    },
    "book": {
        "description": "Libro tamaño A4",
        "w": 0.21,
        "d": 0.15,
        "h": 0.03,
        "material": {"color": (0.7, 0.1, 0.1), "roughness": 0.6, "metallic": 0.0},
    },
    "clock": {
        "description": "Reloj de pared circular",
        "r": 0.15,
        "depth": 0.03,
        "markers": 12,
        "material": {"color": (0.1, 0.1, 0.1), "roughness": 0.2, "metallic": 0.5},
    },
    "lamp": {
        "description": "Lámpara de escritorio",
        "base": {"r": 0.08, "h": 0.02},
        "pole": {"r": 0.008, "h": 0.40},
        "shade": {"r_top": 0.03, "r_bot": 0.08, "h": 0.10},
        "total_height": 0.52,
        "material": {"color": (0.05, 0.05, 0.05), "roughness": 0.3, "metallic": 0.8},
    },
    "pot": {
        "description": "Maceta con planta",
        "body": {"r_top": 0.08, "r_bot": 0.06, "h": 0.12},
        "rim": {"r": 0.08, "tube_r": 0.008},
        "soil": {"r": 0.07, "h": 0.02},
        "stem": {"r": 0.005, "h": 0.15},
        "leaves": {"count": 5, "r": 0.03},
        "total_height": 0.30,
        "material": {"color": (0.7, 0.35, 0.15), "roughness": 0.8, "metallic": 0.0},
    },
    "floor": {
        "description": "Suelo plano",
        "size": 10.0,
        "material": {"color": (0.6, 0.55, 0.5), "roughness": 0.4, "metallic": 0.0},
    },
    "wall": {
        "description": "Pared vertical",
        "size": 10.0,
        "height": 3.0,
        "material": {"color": (0.85, 0.83, 0.8), "roughness": 0.5, "metallic": 0.0},
    },
}

# Colores estándar para materiales
STANDARD_COLORS = {
    "wood_light": (0.4, 0.25, 0.12),
    "wood_dark": (0.3, 0.18, 0.08),
    "wood_medium": (0.55, 0.35, 0.18),
    "metal_black": (0.05, 0.05, 0.05),
    "metal_silver": (0.85, 0.85, 0.85),
    "metal_gold": (0.85, 0.65, 0.1),
    "metal_bronze": (0.8, 0.55, 0.2),
    "ceramic_white": (0.95, 0.95, 0.93),
    "ceramic_blue": (0.2, 0.4, 0.8),
    "glass_clear": (0.8, 0.95, 1.0),
    "plastic_red": (0.9, 0.1, 0.1),
    "plastic_blue": (0.1, 0.1, 0.9),
    "plastic_green": (0.1, 0.7, 0.1),
    "fabric_gray": (0.5, 0.5, 0.5),
    "leather_brown": (0.35, 0.2, 0.1),
    "coffee": (0.15, 0.08, 0.02),
    "leaf_green": (0.1, 0.5, 0.15),
    "flower_yellow": (1.0, 0.8, 0.1),
    "soil_brown": (0.2, 0.12, 0.05),
}


# ═══════════════════════════════════════════════════════════════
# GESTIÓN DE COLECCIONES
# ═══════════════════════════════════════════════════════════════


def create_collection(name, parent=None):
    """
    Crear una colección en la escena.

    Args:
        name: Nombre de la colección (ej: "Chair", "Table")
        parent: Colección padre (opcional)

    Returns:
        La colección creada o la existente
    """
    if name in bpy.data.collections:
        return bpy.data.collections[name]

    col = bpy.data.collections.new(name)

    if parent and parent in bpy.data.collections:
        bpy.data.collections[parent].children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)

    return col


def move_to_collection(obj, collection_name):
    """
    Mover un objeto a una colección específica.

    Args:
        obj: Objeto Blender
        collection_name: Nombre de la colección destino
    """
    # Remover de todas las colecciones actuales
    for col in obj.users_collection:
        col.objects.unlink(obj)

    # Agregar a la colección destino
    if collection_name in bpy.data.collections:
        bpy.data.collections[collection_name].objects.link(obj)
    else:
        col = create_collection(collection_name)
        col.objects.link(obj)


def get_collection_hierarchy():
    """
    Retornar la jerarquía de colecciones como diccionario.

    Returns:
        dict con estructura: {col_name: [obj_names]}
    """
    result = {}
    for col in bpy.data.collections:
        result[col.name] = [obj.name for obj in col.objects]
    return result


def list_collections():
    """Listar todas las colecciones con sus objetos."""
    for col in bpy.data.collections:
        objs = [f"{o.name} ({o.type})" for o in col.objects]
        print(f"📁 {col.name}: {', '.join(objs) if objs else '(vacía)'}")


# ═══════════════════════════════════════════════════════════════
# MATERIALES
# ═══════════════════════════════════════════════════════════════


def create_material(name, color=None, roughness=0.5, metallic=0.0, emission=None):
    """
    Crear un material PBR.

    Args:
        name: Nombre del material
        color: Tupla RGBA (0-1)
        roughness: Rugosidad (0-1)
        metallic: Metalicidad (0-1)
        emission: Tupla RGBA para emisión (opcional)

    Returns:
        El material creado
    """
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]

    if color:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0) if len(color) == 3 else color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic

    if emission:
        em = mat.node_tree.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*emission, 1.0) if len(emission) == 3 else emission
        em.inputs["Strength"].default_value = 3.0
        output = mat.node_tree.nodes["Material Output"]
        mat.node_tree.links.new(em.outputs["Emission"], output.inputs["Surface"])

    return mat


def apply_material(obj, material_name):
    """
    Aplicar un material a un objeto.

    Args:
        obj: Objeto Blender
        material_name: Nombre del material (de STANDARD_COLORS o crear nuevo)
    """
    if material_name in STANDARD_COLORS:
        color = STANDARD_COLORS[material_name]
        mat = create_material(f"Mat_{material_name}", color=color, roughness=0.5)
    elif material_name in bpy.data.materials:
        mat = bpy.data.materials[material_name]
    else:
        mat = create_material(material_name)

    obj.data.materials.append(mat)
    return mat


# ═══════════════════════════════════════════════════════════════
# SISTEMA DE CONEXIÓN PADRE-HIJO
# ═══════════════════════════════════════════════════════════════


def get_bounding_box(obj):
    """
    Obtener bounding box de un objeto.

    Returns:
        dict con min, max, center, size
    """
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = Vector(min(v[i] for v in bbox) for i in range(3))
    maxs = Vector(max(v[i] for v in bbox) for i in range(3))

    return {
        "min": tuple(mins),
        "max": tuple(maxs),
        "center": tuple((mins + maxs) / 2),
        "size": tuple(maxs - mins),
    }


def connect_to_parent(child, parent, anchor="TOP_CENTER", offset=(0, 0, 0)):
    """
    Conectar un objeto hijo a un objeto padre en un anchor específico.

    Args:
        child: Objeto hijo a posicionar
        parent: Objeto padre
        anchor: Punto de conexión del padre
            - TOP_CENTER, TOP_FRONT, TOP_BACK, TOP_LEFT, TOP_RIGHT
            - CENTER, CENTER_FRONT, CENTER_BACK
            - BOTTOM_CENTER, BOTTOM_FRONT, BOTTOM_BACK
        offset: Desplazamiento adicional (x, y, z)

    Returns:
        Posición calculada
    """
    parent_bb = get_bounding_box(parent)
    child_bb = get_bounding_box(child)

    # Calcular posición del anchor en el padre
    p_min = Vector(parent_bb["min"])
    p_max = Vector(parent_bb["max"])
    p_center = Vector(parent_bb["center"])

    anchor_map = {
        "TOP_CENTER": Vector((p_center.x, p_center.y, p_max.z)),
        "TOP_FRONT": Vector((p_center.x, p_min.y, p_max.z)),
        "TOP_BACK": Vector((p_center.x, p_max.y, p_max.z)),
        "TOP_LEFT": Vector((p_min.x, p_center.y, p_max.z)),
        "TOP_RIGHT": Vector((p_max.x, p_center.y, p_max.z)),
        "CENTER": p_center,
        "CENTER_FRONT": Vector((p_center.x, p_min.y, p_center.z)),
        "CENTER_BACK": Vector((p_center.x, p_max.y, p_center.z)),
        "BOTTOM_CENTER": Vector((p_center.x, p_center.y, p_min.z)),
        "BOTTOM_FRONT": Vector((p_center.x, p_min.y, p_min.z)),
        "BOTTOM_BACK": Vector((p_center.x, p_max.y, p_min.z)),
    }

    anchor_pos = anchor_map.get(anchor, p_center)

    # Posicionar hijo: borde inferior del hijo toca el anchor del padre
    child_height = child_bb["size"][2]
    new_pos = anchor_pos + Vector((0, 0, child_height / 2)) + Vector(offset)

    child.location = new_pos

    # Establecer parent
    child.parent = parent

    return tuple(new_pos)


def validate_connection(obj1, obj2, max_distance=0.001):
    """
    Verificar que dos objetos están conectados.

    Returns:
        dict con {connected: bool, distance: float, message: str}
    """
    bb1 = get_bounding_box(obj1)
    bb2 = get_bounding_box(obj2)

    # Calcular distancia entre bordes más cercanos
    min1 = Vector(bb1["min"])
    max1 = Vector(bb1["max"])
    min2 = Vector(bb2["min"])
    max2 = Vector(bb2["max"])

    # Puntos más cercanos
    closest_dist = float("inf")
    for p1 in [min1, max1]:
        for p2 in [min2, max2]:
            dist = (p1 - p2).length
            if dist < closest_dist:
                closest_dist = dist

    connected = closest_dist <= max_distance

    return {
        "connected": connected,
        "distance": closest_dist,
        "max_distance": max_distance,
        "message": "Conectados" if connected else f"Separados por {closest_dist:.4f}m",
    }


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE CREACIÓN (con reglas aplicadas)
# ═══════════════════════════════════════════════════════════════


def create_part(name, primitive, params, collection, material=None, parent=None, anchor=None):
    """
    Crear una pieza con todas las reglas aplicadas.

    Args:
        name: Nombre de la pieza
        primitive: Tipo de primitiva (cube, cylinder, sphere, etc.)
        params: Parámetros de la primitiva
        collection: Nombre de la colección
        material: Nombre del material (opcional)
        parent: Objeto padre para conectar (opcional)
        anchor: Punto de conexión en el padre (opcional)

    Returns:
        El objeto creado
    """
    # Crear primitiva
    primitive_map = {
        "cube": bpy.ops.mesh.primitive_cube_add,
        "cylinder": bpy.ops.mesh.primitive_cylinder_add,
        "sphere": bpy.ops.mesh.primitive_uv_sphere_add,
        "ico_sphere": bpy.ops.mesh.primitive_ico_sphere_add,
        "cone": bpy.ops.mesh.primitive_cone_add,
        "torus": bpy.ops.mesh.primitive_torus_add,
        "plane": bpy.ops.mesh.primitive_plane_add,
        "circle": bpy.ops.mesh.primitive_circle_add,
    }

    func = primitive_map.get(primitive)
    if not func:
        raise ValueError(f"Primitiva no soportada: {primitive}")

    func(**params)
    obj = bpy.context.active_object
    obj.name = name

    # Mover a colección
    move_to_collection(obj, collection)

    # Aplicar material
    if material:
        apply_material(obj, material)

    # Conectar al padre
    if parent and anchor:
        connect_to_parent(obj, parent, anchor)

    return obj


def create_object(object_type, position=(0, 0, 0), collection_name=None, material_override=None):
    """
    Crear un objeto completo basado en tipo estándar.

    Args:
        object_type: Tipo de objeto (chair, table, cup, etc.)
        position: Posición base (x, y, z)
        collection_name: Nombre de la colección (default: object_type)
        material_override: Material personalizado (opcional)

    Returns:
        dict con todos los objetos creados
    """
    if object_type not in STANDARD_OBJECTS:
        raise ValueError(
            f"Objeto no soportado: {object_type}. Disponibles: {list(STANDARD_OBJECTS.keys())}"
        )

    config = STANDARD_OBJECTS[object_type]
    col_name = collection_name or object_type.capitalize()
    create_collection(col_name)

    created = {}

    if object_type == "chair":
        created = _create_chair(config, position, col_name, material_override)
    elif object_type == "table":
        created = _create_table(config, position, col_name, material_override)
    elif object_type == "cup":
        created = _create_cup(config, position, col_name, material_override)
    elif object_type == "book":
        created = _create_book(config, position, col_name, material_override)
    elif object_type == "lamp":
        created = _create_lamp(config, position, col_name, material_override)
    elif object_type == "pot":
        created = _create_pot(config, position, col_name, material_override)
    elif object_type == "floor":
        created = _create_floor(config, position, col_name, material_override)
    elif object_type == "wall":
        created = _create_wall(config, position, col_name, material_override)

    return created


# ═══════════════════════════════════════════════════════════════
# CREADORES ESPECÍFICOS POR OBJETO
# ═══════════════════════════════════════════════════════════════


def _create_chair(config, pos, col, mat_override):
    """Crear silla completa con piezas conectadas."""
    x, y, z = pos
    mat_name = mat_override or "wood_light"
    results = {}

    # Asiento
    seat = create_part(
        f"{col}_Seat",
        "cube",
        {"size": 1, "location": (x, y, z + config["seat"]["h"] / 2)},
        col,
        mat_name,
    )
    seat.scale = (config["seat"]["w"], config["seat"]["d"], config["seat"]["h"])
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    results["seat"] = seat

    # Patas (4)
    leg_positions = [
        (
            config["seat"]["w"] / 2 - config["leg"]["r"],
            config["seat"]["d"] / 2 - config["leg"]["r"],
        ),
        (
            config["seat"]["w"] / 2 - config["leg"]["r"],
            -(config["seat"]["d"] / 2 - config["leg"]["r"]),
        ),
        (
            -(config["seat"]["w"] / 2 - config["leg"]["r"]),
            config["seat"]["d"] / 2 - config["leg"]["r"],
        ),
        (
            -(config["seat"]["w"] / 2 - config["leg"]["r"]),
            -(config["seat"]["d"] / 2 - config["leg"]["r"]),
        ),
    ]

    for i, (lx, ly) in enumerate(leg_positions):
        leg = create_part(
            f"{col}_Leg_{i + 1}",
            "cylinder",
            {
                "radius": config["leg"]["r"],
                "depth": config["leg"]["h"],
                "location": (x + lx, y + ly, z - config["leg"]["h"] / 2),
            },
            col,
            mat_name,
            parent=seat,
            anchor="BOTTOM_CENTER",
        )
        results[f"leg_{i + 1}"] = leg

    # Respaldo (barras verticales)
    bar_spacing = config["backrest"]["w"] / (config["backrest"]["bars"] + 1)
    for i in range(config["backrest"]["bars"]):
        bx = x - config["backrest"]["w"] / 2 + bar_spacing * (i + 1)
        bar = create_part(
            f"{col}_BackBar_{i + 1}",
            "cylinder",
            {
                "radius": config["backrest"]["bar_r"],
                "depth": config["backrest"]["h"],
                "location": (
                    bx,
                    y - config["seat"]["d"] / 2,
                    z + config["seat"]["h"] + config["backrest"]["h"] / 2,
                ),
            },
            col,
            mat_name,
            parent=seat,
            anchor="TOP_BACK",
        )
        results[f"back_bar_{i + 1}"] = bar

    # Barra superior
    top_bar = create_part(
        f"{col}_BackTop",
        "cylinder",
        {
            "radius": config["backrest"]["bar_r"],
            "depth": config["backrest"]["w"],
            "location": (
                x,
                y - config["seat"]["d"] / 2,
                z + config["seat"]["h"] + config["backrest"]["h"],
            ),
        },
        col,
        mat_name,
        parent=seat,
        anchor="TOP_BACK",
    )
    top_bar.rotation_euler = (0, 3.14159 / 2, 0)
    results["back_top"] = top_bar

    return results


def _create_table(config, pos, col, mat_override):
    """Crear mesa completa con piezas conectadas."""
    x, y, z = pos
    mat_name = mat_override or "wood_dark"
    results = {}

    # Tabla superior
    top = create_part(
        f"{col}_Top",
        "cube",
        {"size": 1, "location": (x, y, z + config["leg"]["h"] + config["top"]["h"] / 2)},
        col,
        mat_name,
    )
    top.scale = (config["top"]["w"], config["top"]["d"], config["top"]["h"])
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    results["top"] = top

    # Patas (4)
    leg_positions = [
        (config["top"]["w"] / 2 - config["leg"]["w"], config["top"]["d"] / 2 - config["leg"]["d"]),
        (
            config["top"]["w"] / 2 - config["leg"]["w"],
            -(config["top"]["d"] / 2 - config["leg"]["d"]),
        ),
        (
            -(config["top"]["w"] / 2 - config["leg"]["w"]),
            config["top"]["d"] / 2 - config["leg"]["d"],
        ),
        (
            -(config["top"]["w"] / 2 - config["leg"]["w"]),
            -(config["top"]["d"] / 2 - config["leg"]["d"]),
        ),
    ]

    for i, (lx, ly) in enumerate(leg_positions):
        leg = create_part(
            f"{col}_Leg_{i + 1}",
            "cube",
            {"size": 1, "location": (x + lx, y + ly, z + config["leg"]["h"] / 2)},
            col,
            mat_name,
            parent=top,
            anchor="BOTTOM_CENTER",
        )
        leg.scale = (config["leg"]["w"], config["leg"]["d"], config["leg"]["h"])
        bpy.ops.object.transform_apply(rotation=False, scale=True)
        results[f"leg_{i + 1}"] = leg

    return results


def _create_cup(config, pos, col, mat_override):
    """Crear taza con plato y asa."""
    x, y, z = pos
    results = {}

    # Cuerpo
    body = create_part(
        f"{col}_Body",
        "cylinder",
        {
            "radius": config["body"]["r"],
            "depth": config["body"]["h"],
            "location": (x, y, z + config["body"]["h"] / 2),
        },
        col,
        mat_override or "ceramic_white",
    )
    results["body"] = body

    # Plato
    plate = create_part(
        f"{col}_Plate",
        "cylinder",
        {
            "radius": config["plate"]["r"],
            "depth": config["plate"]["h"],
            "location": (x, y, z + config["plate"]["h"] / 2),
        },
        col,
        mat_override or "ceramic_white",
        parent=body,
        anchor="BOTTOM_CENTER",
    )
    results["plate"] = plate

    # Asa
    handle = create_part(
        f"{col}_Handle",
        "torus",
        {
            "major_radius": config["handle"]["r"],
            "minor_radius": config["handle"]["tube_r"],
            "location": (
                x + config["body"]["r"] + config["handle"]["r"],
                y,
                z + config["body"]["h"] * 0.6,
            ),
        },
        col,
        mat_override or "ceramic_white",
        parent=body,
        anchor="CENTER",
    )
    handle.rotation_euler = (0, 3.14159 / 2, 0)
    results["handle"] = handle

    return results


def _create_book(config, pos, col, mat_override):
    """Crear libro."""
    x, y, z = pos

    book = create_part(
        f"{col}_Book",
        "cube",
        {"size": 1, "location": (x, y, z + config["h"] / 2)},
        col,
        mat_override or "plastic_red",
    )
    book.scale = (config["w"], config["d"], config["h"])
    bpy.ops.object.transform_apply(rotation=False, scale=True)

    return {"book": book}


def _create_lamp(config, pos, col, mat_override):
    """Crear lámpara de escritorio."""
    x, y, z = pos
    results = {}

    # Base
    base = create_part(
        f"{col}_Base",
        "cylinder",
        {
            "radius": config["base"]["r"],
            "depth": config["base"]["h"],
            "location": (x, y, z + config["base"]["h"] / 2),
        },
        col,
        mat_override or "metal_black",
    )
    results["base"] = base

    # Vara
    pole = create_part(
        f"{col}_Pole",
        "cylinder",
        {
            "radius": config["pole"]["r"],
            "depth": config["pole"]["h"],
            "location": (x, y, z + config["base"]["h"] + config["pole"]["h"] / 2),
        },
        col,
        mat_override or "metal_black",
        parent=base,
        anchor="TOP_CENTER",
    )
    results["pole"] = pole

    # Pantalla
    shade = create_part(
        f"{col}_Shade",
        "cone",
        {
            "radius1": config["shade"]["r_bot"],
            "radius2": config["shade"]["r_top"],
            "depth": config["shade"]["h"],
            "location": (
                x,
                y,
                z + config["base"]["h"] + config["pole"]["h"] + config["shade"]["h"] / 2,
            ),
        },
        col,
        "ceramic_white",
        parent=pole,
        anchor="TOP_CENTER",
    )
    results["shade"] = shade

    return results


def _create_pot(config, pos, col, mat_override):
    """Crear maceta con planta."""
    x, y, z = pos
    results = {}

    # Maceta
    body = create_part(
        f"{col}_Body",
        "cone",
        {
            "radius1": config["body"]["r_top"],
            "radius2": config["body"]["r_bot"],
            "depth": config["body"]["h"],
            "location": (x, y, z + config["body"]["h"] / 2),
        },
        col,
        mat_override or "terracota",
    )
    results["body"] = body

    # Tierra
    soil = create_part(
        f"{col}_Soil",
        "cylinder",
        {
            "radius": config["soil"]["r"],
            "depth": config["soil"]["h"],
            "location": (x, y, z + config["body"]["h"] - config["soil"]["h"] / 2),
        },
        col,
        "soil_brown",
        parent=body,
        anchor="TOP_CENTER",
    )
    results["soil"] = soil

    # Tallo
    stem = create_part(
        f"{col}_Stem",
        "cylinder",
        {
            "radius": config["stem"]["r"],
            "depth": config["stem"]["h"],
            "location": (x, y, z + config["body"]["h"] + config["stem"]["h"] / 2),
        },
        col,
        "leaf_green",
        parent=soil,
        anchor="TOP_CENTER",
    )
    results["stem"] = stem

    return results


def _create_floor(config, pos, col, mat_override):
    """Crear suelo."""
    x, y, z = pos

    floor = create_part(
        f"{col}_Floor",
        "plane",
        {"size": config["size"], "location": (x, y, z)},
        col,
        mat_override or "wood_medium",
    )

    return {"floor": floor}


def _create_wall(config, pos, col, mat_override):
    """Crear pared."""
    x, y, z = pos

    wall = create_part(
        f"{col}_Wall",
        "plane",
        {"size": config["size"], "location": (x, y, z + config["height"] / 2)},
        col,
        mat_override or "ceramic_white",
    )
    wall.rotation_euler = (3.14159 / 2, 0, 0)

    return {"wall": wall}


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def get_object_info(name):
    """Obtener información detallada de un objeto."""
    obj = bpy.data.objects.get(name)
    if not obj:
        return None

    bb = get_bounding_box(obj)
    return {
        "name": obj.name,
        "type": obj.type,
        "location": tuple(obj.location),
        "rotation": tuple(obj.rotation_euler),
        "scale": tuple(obj.scale),
        "bounding_box": bb,
        "materials": [m.name for m in obj.data.materials] if obj.data else [],
        "parent": obj.parent.name if obj.parent else None,
        "collection": obj.users_collection[0].name if obj.users_collection else None,
    }


def print_scene_summary():
    """Imprimir resumen de la escena."""
    print("\n" + "=" * 60)
    print("RESUMEN DE ESCENA")
    print("=" * 60)

    collections = get_collection_hierarchy()
    for col_name, objs in collections.items():
        print(f"\n📁 {col_name} ({len(objs)} objetos):")
        for obj_name in objs:
            info = get_object_info(obj_name)
            if info:
                loc = info["location"]
                print(
                    f"   • {obj_name} ({info['type']}) en [{loc[0]:.2f}, {loc[1]:.2f}, {loc[2]:.2f}]"
                )

    print(f"\nTotal: {len(bpy.data.objects)} objetos, {len(bpy.data.materials)} materiales")
    print("=" * 60)
