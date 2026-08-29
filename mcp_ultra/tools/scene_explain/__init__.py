"""
blender-mcp-ultra — Scene Explain
Explica en lenguaje natural estructurado qué ES un objeto: geometría,
materiales (con árbol de nodos), modificadores, física y jerarquía.
Inspirado en NodeArchitect (Houdini) — adaptado al bpy de Blender.
"""

from __future__ import annotations

from typing import Any, Dict, List

try:
    import bpy
except ImportError:  # fuera de Blender (indexación/tests)
    bpy = None

from ...core.entities import Tool, ToolCategory, ToolPermission


def _scene():
    return bpy.context.scene


def _resp(payload):
    if bpy is not None:
        payload["scene"] = _scene().name
    return payload


def _explain_material(mat) -> dict[str, Any]:
    if mat is None or not mat.use_nodes:
        return {"material": mat.name if mat else None, "nodes": "sin nodos"}
    nodos_resumen: list[str] = []
    for n in mat.node_tree.nodes:
        tipo = n.type.replace("SHADERNODE", "").lower()
        detalle = ""
        if n.type == "TEX_NOISE":
            detalle = f"scale={n.inputs['Scale'].default_value:.1f}"
        elif n.type == "VALTORGB":
            detalle = f"{len(n.color_ramp.elements)} paradas"
        elif n.type == "BSDF_PRINCIPLED":
            bc = n.inputs["Base Color"]
            col = bc.default_value
            detalle = (
                f"color={'enlazado' if bc.is_linked else tuple(round(c, 2) for c in col)}, "
                f"metal={n.inputs['Metallic'].default_value:.2f}, "
                f"rough={n.inputs['Roughness'].default_value:.2f}"
            )
        nodos_resumen.append(f"{n.name} ({tipo}{', ' + detalle if detalle else ''})")
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    out: dict[str, Any] = {
        "material": mat.name,
        "n_nodos": len(mat.node_tree.nodes),
        "nodos": nodos_resumen,
    }
    if bsdf:
        out["metallic"] = round(bsdf.inputs["Metallic"].default_value, 2)
        out["roughness"] = round(bsdf.inputs["Roughness"].default_value, 2)
    return out


def _explain_object(obj) -> dict[str, Any]:
    from mathutils import Vector

    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box] if obj.type == "MESH" else []
    info: dict[str, Any] = {
        "name": obj.name,
        "type": obj.type,
        "location": [round(v, 3) for v in obj.location],
        "parent": obj.parent.name if obj.parent else None,
    }
    if pts:
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        dims = mx - mn
        info["bbox_dims_m"] = [round(v, 3) for v in dims]
        info["apoyado_en_z"] = round(mn.z, 3)
        info["materiales"] = [_explain_material(m) for m in obj.data.materials]
        mods = []
        for mod in obj.modifiers:
            detalle = {"type": mod.type}
            if mod.type == "BEVEL":
                detalle["width"] = round(getattr(mod, "width", 0), 4)
            elif mod.type == "SUBSURF":
                detalle["levels"] = getattr(mod, "levels", 0)
            elif mod.type == "NODES":
                detalle["node_group"] = mod.node_group.name if mod.node_group else None
            mods.append({"name": mod.name, **detalle})
        info["modifiers"] = mods
        info["fisica"] = obj.rigid_body.type if obj.rigid_body else None
    if obj.animation_data and obj.animation_data.action:
        info["animado"] = True
    return info


def scene_explain(target: str = "", **_kw) -> dict:
    """Explica un objeto (geometría, materiales con nodos, modifiers, física).

    Pensado para que el agente ENTIENDA qué hay antes de modificarlo.
    """
    obj = bpy.data.objects.get(target)
    if obj is None:
        parecidos = [o.name for o in _scene().objects if target.lower() in o.name.lower()][:8]
        return _resp({"error": f"no encontrado: {target}", "parecidos": parecidos})
    out = _explain_object(obj)
    if obj.children:
        out["hijos"] = [c.name for c in obj.children]
    return _resp(out)


TOOLS = [
    Tool(
        name="scene.explain",
        category=ToolCategory.SCENE_UTILS,
        description="Explica un objeto en detalle: geometría, bbox, materiales (con resumen del árbol de nodos), modifiers, física y jerarquía",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "target": {"type": "str", "required": True, "description": "nombre del objeto"}
        },
        examples=["scene.explain(target='Mug')"],
    ),
]

HANDLERS = {
    "scene.explain": scene_explain,
}
