"""
blender-mcp-ultra — Curves, Text & Metaball Tools
Lo que faltaba para tipografía, trazos y formas orgánicas fusionadas.
"""

from typing import List

try:
    import bpy
except ImportError:  # fuera de Blender
    bpy = None

from ...core.entities import Tool, ToolCategory, ToolPermission


def bezier_add(
    name: str = "Curve",
    points: list[list[float]] = None,
    closed: bool = False,
    bevel_depth: float = 0.0,
) -> dict:
    """Curva Bézier 3D a partir de puntos; bevel_depth la convierte en tubo."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = float(bevel_depth)
    sp = cu.splines.new("BEZIER")
    pts = points or [[0, 0, 0], [1, 0, 0], [1, 1, 0]]
    sp.bezier_points.add(len(pts) - 1)
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    sp.use_cyclic_u = bool(closed)
    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    return {"object": obj.name, "points": len(pts), "closed": closed}


def curve_set_point(object_name: str, index: int, co: list[float], handle: str = "AUTO") -> dict:
    """Mover punto de control de una Bézier (handle: AUTO/VECTOR/FREE)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "CURVE":
        raise ValueError(f"Curva no encontrada: {object_name}")
    sp = obj.data.splines[0]
    if sp.type != "BEZIER" or index >= len(sp.bezier_points):
        raise ValueError(f"Punto {index} fuera de rango")
    bp = sp.bezier_points[index]
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = handle
    return {"object": object_name, "point": index, "co": co, "handle": handle}


def text_add(
    name: str = "Text",
    body: str = "Text",
    size: float = 1.0,
    extrude: float = 0.0,
    bevel_depth: float = 0.0,
    align: str = "CENTER",
    location: list[float] = None,
) -> dict:
    """Objeto de texto 3D (extruible y biselable)."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = float(size)
    cu.extrude = float(extrude)
    cu.bevel_depth = float(bevel_depth)
    cu.align_x = align
    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    if location:
        obj.location = location
    return {"object": obj.name, "body": body}


def text_set_body(object_name: str, body: str) -> dict:
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "FONT":
        raise ValueError(f"Texto no encontrado: {object_name}")
    obj.data.body = body
    return {"object": object_name, "body": body}


def metaball_add(
    name: str = "Meta", location=None, radius: float = 1.0, stiffness: float = 2.0
) -> dict:
    """Metaball que se fusiona con otras del mismo 'familia' (Meta.001...)."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = 0.15
    el = mb.elements.new()
    el.co = (0, 0, 0)
    el.radius = float(radius)
    el.stiffness = float(stiffness)
    obj = bpy.data.objects.new(name, mb)
    bpy.context.collection.objects.link(obj)
    if location:
        obj.location = location
    return {"object": obj.name, "elements": len(mb.elements)}


def metaball_add_element(object_name: str, location: list[float], radius: float = 1.0) -> dict:
    """Añadir elemento a una metaball existente (se fusionan solos)."""
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "META":
        raise ValueError(f"Metaball no encontrada: {object_name}")
    el = obj.data.elements.new()
    el.co = location
    el.radius = float(radius)
    return {"object": object_name, "elements": len(obj.data.elements)}


def grease_pencil_add(name: str = "GPencil") -> dict:
    """Objeto Grease Pencil vacío (dibujo 2D/3D, anotaciones)."""
    gp = bpy.data.grease_pencils.new(name)
    layer = gp.layers.new("Layer", set_active=True)
    obj = bpy.data.objects.new(name, gp)
    bpy.context.collection.objects.link(obj)
    return {"object": obj.name, "layers": len(gp.layers)}


TOOLS = [
    Tool(
        "curve.bezier_add",
        ToolCategory.OBJECTS,
        "Curva Bézier 3D por puntos; bevel_depth > 0 la vuelve tubo",
        ToolPermission.WRITE,
        {
            "name": {"type": "str"},
            "points": {"type": "list", "description": "[[x,y,z], ...]"},
            "closed": {"type": "bool"},
            "bevel_depth": {"type": "float"},
        },
    ),
    Tool(
        "curve.set_point",
        ToolCategory.OBJECTS,
        "Mover punto de control de Bézier",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "index": {"type": "int", "required": True},
            "co": {"type": "list", "required": True},
            "handle": {"type": "str"},
        },
    ),
    Tool(
        "text.add",
        ToolCategory.OBJECTS,
        "Texto 3D extruible/biselable",
        ToolPermission.WRITE,
        {
            "name": {"type": "str"},
            "body": {"type": "str"},
            "size": {"type": "float"},
            "extrude": {"type": "float"},
            "bevel_depth": {"type": "float"},
            "align": {"type": "str"},
        },
    ),
    Tool(
        "text.set_body",
        ToolCategory.OBJECTS,
        "Cambiar el texto de un objeto FONT",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "body": {"type": "str", "required": True},
        },
    ),
    Tool(
        "metaball.add",
        ToolCategory.OBJECTS,
        "Metaball (se fusiona con otras del mismo nombre-base)",
        ToolPermission.WRITE,
        {
            "name": {"type": "str"},
            "location": {"type": "list"},
            "radius": {"type": "float"},
            "stiffness": {"type": "float"},
        },
    ),
    Tool(
        "metaball.add_element",
        ToolCategory.OBJECTS,
        "Elemento adicional en una metaball (fusión orgánica)",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "location": {"type": "list", "required": True},
            "radius": {"type": "float"},
        },
    ),
    Tool(
        "grease_pencil.add",
        ToolCategory.OBJECTS,
        "Objeto Grease Pencil vacío con una capa",
        ToolPermission.WRITE,
        {"name": {"type": "str"}},
    ),
]

HANDLERS = {
    "curve.bezier_add": bezier_add,
    "curve.set_point": curve_set_point,
    "text.add": text_add,
    "text.set_body": text_set_body,
    "metaball.add": metaball_add,
    "metaball.add_element": metaball_add_element,
    "grease_pencil.add": grease_pencil_add,
}
