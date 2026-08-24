"""
blender-mcp-ultra — Mesh Edit Tools
Edición de malla por componentes (vértices/aristas/caras) vía bmesh.

Convención para agentes:
- Los índices son los que devuelve `mesh.get_topology` (orden de
  vértices/aristas/caras del mesh).
- CUALQUIER operación que cambie la topología invalida índices:
  vuelve a llamar a get_topology antes de la siguiente edición.
"""

from typing import Any, Dict, List

try:
    import bmesh
    import bpy
    from mathutils import Vector
except ImportError:  # fuera de Blender: solo definiciones
    bmesh = None
    bpy = None
    Vector = None

from ...core.entities import Tool, ToolCategory, ToolPermission


def _get_obj(object_name: str) -> bpy.types.Object:
    obj = bpy.data.objects.get(object_name)
    if obj is None or obj.type != "MESH":
        raise ValueError(f"Objeto mesh no encontrado: {object_name}")
    return obj


def _edit_bm(obj: bpy.types.Object) -> bmesh.types.BMesh:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm


def _finish(obj: bpy.types.Object, bm: bmesh.types.BMesh) -> dict[str, int]:
    bm.normal_update()
    bm.to_mesh(obj.data)
    counts = {"vertices": len(bm.verts), "edges": len(bm.edges), "faces": len(bm.faces)}
    bm.free()
    obj.data.update()
    return counts


def _pick_faces(bm, indices: list[int]):
    try:
        return [bm.faces[i] for i in indices]
    except IndexError as e:
        raise ValueError(f"Índice de cara fuera de rango: {e}") from e


def _pick_edges(bm, indices: list[int]):
    try:
        return [bm.edges[i] for i in indices]
    except IndexError as e:
        raise ValueError(f"Índice de arista fuera de rango: {e}") from e


def _pick_verts(bm, indices: list[int]):
    try:
        return [bm.verts[i] for i in indices]
    except IndexError as e:
        raise ValueError(f"Índice de vértice fuera de rango: {e}") from e


# ═══════════════════════════════════════════════════════════════
# Handlers
# ═══════════════════════════════════════════════════════════════


def get_topology(object_name: str, include_faces: bool = True, max_faces: int = 500) -> dict:
    obj = _get_obj(object_name)
    out: dict[str, Any] = {
        "object": object_name,
        "vertices": len(obj.data.vertices),
        "edges": len(obj.data.edges),
        "faces": len(obj.data.polygons),
    }
    if include_faces:
        faces = []
        for i, poly in enumerate(obj.data.polygons):
            if max_faces and i >= max_faces:
                faces.append({"truncated": True, "hint": "sube max_faces o consulta por rangos"})
                break
            faces.append(
                {
                    "index": i,
                    "center": [round(c, 4) for c in poly.center],
                    "normal": [round(c, 3) for c in poly.normal],
                    "verts": list(poly.vertices),
                }
            )
        out["face_data"] = faces
    return out


def select(object_name: str, face_indices=None, edge_indices=None, vert_indices=None) -> dict:
    """Selecciona componentes (los índices se validan; no hay estado previo)."""
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    sel = {
        "faces": [f.index for f in _pick_faces(bm, face_indices or [])],
        "edges": [e.index for e in _pick_edges(bm, edge_indices or [])],
        "verts": [v.index for v in _pick_verts(bm, vert_indices or [])],
    }
    bm.free()
    return {"object": object_name, "selected": sel}


def extrude_faces(object_name: str, face_indices: list[int], thickness: float = 0.1) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    faces = _pick_faces(bm, face_indices)
    # Blender 5.x: extrude_face_region toma `geom`; 4.x usaba `faces`
    try:
        res = bmesh.ops.extrude_face_region(bm, geom=faces)
    except TypeError:
        res = bmesh.ops.extrude_face_region(bm, faces=faces)
    new_verts = [g for g in res.get("geom", []) if isinstance(g, bmesh.types.BMVert)]
    normal = Vector((0.0, 0.0, 0.0))
    for f in faces:
        normal += f.normal
    if normal.length > 0:
        normal.normalize()
    bmesh.ops.translate(bm, verts=new_verts, vec=normal * thickness)
    counts = _finish(obj, bm)
    return {"extruded": len(face_indices), "moved_by": thickness, **counts}


def inset_faces(
    object_name: str, face_indices: list[int], thickness: float = 0.05, depth: float = 0.0
) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    faces = _pick_faces(bm, face_indices)
    bmesh.ops.inset_region(bm, faces=faces, thickness=thickness, depth=depth, use_even_offset=True)
    counts = _finish(obj, bm)
    return {"inset": len(face_indices), "thickness": thickness, "depth": depth, **counts}


def bevel_edges(
    object_name: str, edge_indices: list[int], width: float = 0.02, segments: int = 2
) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    edges = _pick_edges(bm, edge_indices)
    geom = list(edges)
    for e in edges:
        geom.extend([v for v in e.verts if v not in geom])
    bmesh.ops.bevel(
        bm,
        geom=geom,
        offset=width,
        segments=segments,
        affect="EDGES",
        clamp_overlap=True,
    )
    counts = _finish(obj, bm)
    return {"beveled_edges": len(edge_indices), "width": width, "segments": segments, **counts}


def subdivide_faces(object_name: str, face_indices: list[int], cuts: int = 1) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    faces = _pick_faces(bm, face_indices) if face_indices else list(bm.faces)
    edges = {e for f in faces for e in f.edges}
    bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=int(cuts), use_grid_fill=True)
    counts = _finish(obj, bm)
    return {"subdivided": len(face_indices) or "todo", "cuts": cuts, **counts}


def move_verts(
    object_name: str,
    vert_indices: list[int],
    offset: list[float] = None,
    positions: dict[str, list[float]] = None,
) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    verts = _pick_verts(bm, vert_indices or [])
    if offset:
        vec = Vector(offset)
        for v in verts:
            v.co = v.co + vec
    if positions:
        for idx_str, co in positions.items():
            v = bm.verts[int(idx_str)]
            v.co = Vector(co)
    counts = _finish(obj, bm)
    return {"moved": len(vert_indices or []) + len(positions or {}), **counts}


def delete_elements(
    object_name: str,
    face_indices: list[int] = None,
    edge_indices: list[int] = None,
    vert_indices: list[int] = None,
) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    deleted = 0
    if face_indices:
        bmesh.ops.delete(bm, geom=_pick_faces(bm, face_indices), context="FACES")
        deleted += len(face_indices)
    if edge_indices:
        bmesh.ops.delete(bm, geom=_pick_edges(bm, edge_indices), context="EDGES")
        deleted += len(edge_indices)
    if vert_indices:
        bmesh.ops.delete(bm, geom=_pick_verts(bm, vert_indices), context="VERTS")
        deleted += len(vert_indices)
    counts = _finish(obj, bm)
    return {"deleted": deleted, **counts}


def merge_verts(object_name: str, vert_indices: list[int], dist: float = 0.001) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    verts = _pick_verts(bm, vert_indices)
    before = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=verts, dist=dist)
    merged = before - len(bm.verts)
    counts = _finish(obj, bm)
    return {"merged": merged, **counts}


def smooth_verts(object_name: str, iterations: int = 1, face_indices: list[int] = None) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    if face_indices:
        target_verts = {v for f in _pick_faces(bm, face_indices) for v in f.verts}
    else:
        target_verts = set(bm.verts)
    for _ in range(int(iterations)):
        avg = {}
        for v in target_verts:
            if not v.link_edges:
                continue
            acc = Vector((0.0, 0.0, 0.0))
            for e in v.link_edges:
                acc += e.other_vert(v).co
            avg[v.index] = acc / len(v.link_edges)
        for v, co in avg.items():
            v.co = co
    counts = _finish(obj, bm)
    return {"smoothed_verts": len(target_verts), "iterations": iterations, **counts}


def recalc_normals(object_name: str) -> dict:
    obj = _get_obj(object_name)
    bm = _edit_bm(obj)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    counts = _finish(obj, bm)
    return {"recalculated": True, **counts}


# ═══════════════════════════════════════════════════════════════
# Definiciones de tools
# ═══════════════════════════════════════════════════════════════

TOOLS = [
    Tool(
        "mesh.get_topology",
        ToolCategory.OBJECTS,
        "Topología del mesh: conteos + caras (índice, centro, normal, vértices)",
        ToolPermission.READ_ONLY,
        {
            "object_name": {"type": "str", "required": True, "description": "Nombre del objeto"},
            "include_faces": {"type": "bool", "description": "Incluir datos por cara"},
            "max_faces": {"type": "int", "description": "Límite de caras listadas"},
        },
    ),
    Tool(
        "mesh.select",
        ToolCategory.OBJECTS,
        "Valida y devuelve los componentes seleccionables por índice",
        ToolPermission.READ_ONLY,
        {
            "object_name": {"type": "str", "required": True},
            "face_indices": {"type": "list"},
            "edge_indices": {"type": "list"},
            "vert_indices": {"type": "list"},
        },
    ),
    Tool(
        "mesh.extrude_faces",
        ToolCategory.OBJECTS,
        "Extruir caras a lo largo de su normal media",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "face_indices": {"type": "list", "required": True},
            "thickness": {"type": "float"},
        },
    ),
    Tool(
        "mesh.inset_faces",
        ToolCategory.OBJECTS,
        "Inset en caras (mismo plano) con profundidad opcional",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "face_indices": {"type": "list", "required": True},
            "thickness": {"type": "float"},
            "depth": {"type": "float"},
        },
    ),
    Tool(
        "mesh.bevel_edges",
        ToolCategory.OBJECTS,
        "Biselar aristas concretas",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "edge_indices": {"type": "list", "required": True},
            "width": {"type": "float"},
            "segments": {"type": "int"},
        },
    ),
    Tool(
        "mesh.subdivide_faces",
        ToolCategory.OBJECTS,
        "Subdividir caras (o todo el mesh si no se dan índices)",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "face_indices": {"type": "list"},
            "cuts": {"type": "int"},
        },
    ),
    Tool(
        "mesh.move_verts",
        ToolCategory.OBJECTS,
        "Mover vértices por offset o a posiciones absolutas",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "vert_indices": {"type": "list"},
            "offset": {"type": "list"},
            "positions": {"type": "dict"},
        },
    ),
    Tool(
        "mesh.delete_elements",
        ToolCategory.OBJECTS,
        "Borrar caras/aristas/vértices por índice",
        ToolPermission.DESTRUCTIVE,
        {
            "object_name": {"type": "str", "required": True},
            "face_indices": {"type": "list"},
            "edge_indices": {"type": "list"},
            "vert_indices": {"type": "list"},
        },
    ),
    Tool(
        "mesh.merge_verts",
        ToolCategory.OBJECTS,
        "Fusionar vértices cercanos (remove doubles) en una selección",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "vert_indices": {"type": "list", "required": True},
            "dist": {"type": "float"},
        },
    ),
    Tool(
        "mesh.smooth_verts",
        ToolCategory.OBJECTS,
        "Suavizar posiciones de vértices (Laplaciano simple)",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str", "required": True},
            "iterations": {"type": "int"},
            "face_indices": {"type": "list"},
        },
    ),
    Tool(
        "mesh.recalc_normals",
        ToolCategory.OBJECTS,
        "Recalcular normales hacia fuera",
        ToolPermission.WRITE,
        {"object_name": {"type": "str", "required": True}},
    ),
]

HANDLERS = {
    "mesh.get_topology": get_topology,
    "mesh.select": select,
    "mesh.extrude_faces": extrude_faces,
    "mesh.inset_faces": inset_faces,
    "mesh.bevel_edges": bevel_edges,
    "mesh.subdivide_faces": subdivide_faces,
    "mesh.move_verts": move_verts,
    "mesh.delete_elements": delete_elements,
    "mesh.merge_verts": merge_verts,
    "mesh.smooth_verts": smooth_verts,
    "mesh.recalc_normals": recalc_normals,
}
