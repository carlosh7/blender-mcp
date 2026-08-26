"""
blender-mcp-ultra — Scene Presets & Moods
Escenas base de un click y "moods" de iluminación que transforman el ambiente
sin tocar la geometría. Inspirado en Kozer94/blender-ai-studio.
"""

from __future__ import annotations

import math
from typing import Any, Dict

try:
    import bpy
except ImportError:  # fuera de Blender (indexación/tests)
    bpy = None

from ...core.entities import Tool, ToolCategory, ToolPermission

PRESETS = {
    "estudio": "fondo infinito gris + 3 puntos de luz (producto)",
    "sala": "sala de estar: suelo, pared trasera, ventana de luz fría",
    "oficina": "escritorio, silla, monitor, lámpara y pared",
    "exterior": "terreno verde, cielo azul, sol cálido",
    "noche": "exterior nocturno: luna azulada + farol cálido",
    "cyberpunk": "suelo oscuro reflectante + neones magenta/cian",
    "galeria": "sala blanca de museo con luz cenital suave",
    "cocina": "mesada, nevera y luz de ventana",
    "desierto": "arena cálida, sol duro, cielo pálido",
    "bosque": "terreno musgo, luz verde filtrada, niebla suave",
}

MOODS = {
    "cinematic": {
        "key": (1.0, 0.9, 0.75, 2500),
        "fill": (0.4, 0.5, 0.8, 400),
        "world": (0.08, 0.09, 0.12, 0.5),
        "contrast": True,
    },
    "cyberpunk": {
        "key": (1.0, 0.1, 0.9, 3000),
        "fill": (0.0, 0.7, 1.0, 1200),
        "world": (0.02, 0.0, 0.05, 0.6),
    },
    "horror": {
        "key": (0.6, 0.65, 0.7, 600),
        "fill": (0.1, 0.1, 0.15, 50),
        "world": (0.01, 0.01, 0.02, 0.3),
    },
    "fantasy": {
        "key": (1.0, 0.8, 0.5, 2000),
        "fill": (0.3, 0.9, 0.5, 500),
        "world": (0.05, 0.1, 0.08, 0.7),
    },
    "minimal": {"key": (1, 1, 1, 2000), "fill": (1, 1, 1, 800), "world": (0.9, 0.9, 0.9, 1.0)},
    "warm_sunset": {
        "key": (1.0, 0.55, 0.2, 2800),
        "fill": (0.3, 0.4, 0.8, 300),
        "world": (0.25, 0.15, 0.1, 0.8),
    },
}


def _scene():
    return bpy.context.scene


def _resp(payload):
    if bpy is not None:
        payload["scene"] = _scene().name
    return payload


def _add_light(name, loc, energy, color, size=2.0, type_="AREA"):
    ld = bpy.data.lights.new(name, type_)
    ld.energy = energy
    ld.color = color[:3]
    if type_ == "AREA":
        ld.size = size
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    _scene().collection.objects.link(lo)
    return lo


def scene_preset(name: str = "", keep_objects: bool = False, **_kw) -> dict:
    """Crea el entorno base de un preset (luces + entorno + suelo/paredes).

    Con keep_objects=False limpia la escena primero (destructivo).
    """
    if name not in PRESETS:
        return _resp({"error": f"preset inválido: {name}", "disponibles": sorted(PRESETS)})
    sc = _scene()
    if not keep_objects:
        for o in list(sc.objects):
            bpy.data.objects.remove(o, do_unlink=True)

    def floor(size=24, loc=(0, 0, 0), mat_color=(0.5, 0.5, 0.5)):
        bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
        f = bpy.context.active_object
        m = bpy.data.materials.new(f"Piso_{name}")
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*mat_color, 1)
        m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
        f.data.materials.append(m)
        return f

    w = bpy.data.worlds.new(f"W_{name}")
    w.use_nodes = True
    sc.world = w

    if name == "estudio":
        floor()
        bg = w.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.35, 0.35, 0.38, 1)
        bg.inputs[1].default_value = 0.8
        _add_light("Key", (5, -5, 7), 2500, (1, 0.97, 0.92))
        _add_light("Fill", (-6, -3, 4), 700, (0.8, 0.85, 1.0))
        _add_light("Rim", (0, 7, 5), 1500, (1, 0.9, 0.8))
    elif name in ("sala", "oficina", "cocina", "galeria"):
        floor(30, (0, 0, 0), (0.7, 0.68, 0.65) if name == "galeria" else (0.55, 0.52, 0.48))
        bpy.ops.mesh.primitive_plane_add(
            size=30, location=(0, 8, 0), rotation=(math.radians(90), 0, 0)
        )
        pared = bpy.context.active_object
        pm = bpy.data.materials.new("Pared")
        pm.use_nodes = True
        pm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
            0.85,
            0.83,
            0.8,
            1,
        )
        pared.data.materials.append(pm)
        bg = w.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.6, 0.7, 0.85, 1)
        bg.inputs[1].default_value = 1.0
        _add_light("Ventana", (0, 5, 4), 1800, (0.85, 0.9, 1.0), size=4)
        _add_light("Ambient", (0, -3, 5), 600, (1, 1, 1))
    elif name in ("exterior", "desierto", "bosque"):
        floor(
            60,
            (0, 0, 0),
            (0.15, 0.35, 0.1)
            if name == "bosque"
            else (0.75, 0.65, 0.45)
            if name == "desierto"
            else (0.2, 0.45, 0.12),
        )
        bg = w.node_tree.nodes["Background"]
        cielo = (0.35, 0.55, 0.85, 1) if name != "desierto" else (0.8, 0.75, 0.6, 1)
        bg.inputs[0].default_value = cielo
        bg.inputs[1].default_value = 1.2
        sd = bpy.data.lights.new("Sol", "SUN")
        sd.energy = 4 if name != "desierto" else 6
        sd.color = (1, 0.9, 0.75) if name != "bosque" else (0.75, 1, 0.8)
        sd.angle = 0.1 if name == "desierto" else 0.3
        so = bpy.data.objects.new("Sol", sd)
        so.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
        sc.collection.objects.link(so)
    elif name == "noche":
        floor(40, (0, 0, 0), (0.08, 0.09, 0.12))
        bg = w.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.02, 0.03, 0.08, 1)
        bg.inputs[1].default_value = 0.6
        _add_light("Luna", (-6, 4, 9), 900, (0.6, 0.7, 1.0), type_="SUN") if False else None
        sd = bpy.data.lights.new("Luna", "SUN")
        sd.energy = 1.2
        sd.color = (0.6, 0.7, 1.0)
        lo = bpy.data.objects.new("Luna", sd)
        lo.rotation_euler = (math.radians(60), 0, math.radians(-40))
        sc.collection.objects.link(lo)
        _add_light("Farol", (2, -2, 2.5), 300, (1, 0.6, 0.25), size=0.5)
    elif name in ("cyberpunk",):
        floor(30, (0, 0, 0), (0.05, 0.05, 0.07))
        fmat = floor.data.materials[0]
        fmat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.15
        bg = w.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.02, 0.0, 0.05, 1)
        bg.inputs[1].default_value = 0.8
        _add_light("NeonMagenta", (-5, 0, 4), 2500, (1, 0.1, 0.9), size=5)
        _add_light("NeonCian", (5, 0, 4), 2500, (0.0, 0.8, 1.0), size=5)
    return _resp(
        {"ok": True, "preset": name, "descripcion": PRESETS[name], "objetos": len(sc.objects)}
    )


def scene_mood(mood: str = "", **_kw) -> dict:
    """Aplica un mood de iluminación: reemplaza luces y mundo SIN tocar geometría."""
    if mood not in MOODS:
        return _resp({"error": f"mood inválido: {mood}", "disponibles": sorted(MOODS)})
    cfg = MOODS[mood]
    sc = _scene()
    # quitar luces existentes
    for o in list(sc.objects):
        if o.type == "LIGHT":
            bpy.data.objects.remove(o, do_unlink=True)
    kx, ky, kz, ke = cfg["key"]
    fx, fy, fz, fe = cfg["fill"]
    _add_light(f"{mood}_Key", (4, -5, 6), ke, (kx, ky, kz), size=3)
    _add_light(f"{mood}_Fill", (-5, -2, 3), fe, (fx, fy, fz), size=4)
    wx, wy, wz, ws = cfg["world"]
    w = sc.world or bpy.data.worlds.new("W")
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (wx, wy, wz, 1)
    bg.inputs[1].default_value = ws
    sc.world = w
    return _resp({"ok": True, "mood": mood, "luces": 2})


TOOLS = [
    Tool(
        name="scene.preset",
        category=ToolCategory.SCENE,
        description="Crea el entorno base de un preset (luces+entorno+suelo). Presets: "
        + ", ".join(sorted(PRESETS)),
        permission=ToolPermission.DESTRUCTIVE,
        parameters={
            "name": {"type": "str", "required": True},
            "keep_objects": {
                "type": "bool",
                "default": False,
                "description": "False = limpia la escena primero",
            },
        },
        examples=[
            "scene.preset(name='estudio')",
            "scene.preset(name='cyberpunk', keep_objects=True)",
        ],
    ),
    Tool(
        name="scene.mood",
        category=ToolCategory.LIGHTS,
        description="Aplica un mood de iluminación (reemplaza luces y mundo, sin tocar geometría). Moods: "
        + ", ".join(sorted(MOODS)),
        permission=ToolPermission.WRITE,
        parameters={"mood": {"type": "str", "required": True}},
        examples=["scene.mood(mood='cinematic')"],
    ),
]

HANDLERS = {
    "scene.preset": scene_preset,
    "scene.mood": scene_mood,
}
