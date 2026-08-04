#!/usr/bin/env python3
"""
blender-mcp — Simplified MCP Server
Exposes 6 core tools for controlling Blender via MCP protocol.
Compatible with opencode, Claude Desktop, Cursor, etc.
"""
import json, os, sys, logging

from blender_mcp.platform import get_log_dir
from blender_connection import get_blender

_log_dir = get_log_dir()
_log_file = str(_log_dir / "server.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr), logging.FileHandler(_log_file)]
)
logger = logging.getLogger("blender-mcp")

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
mcp = FastMCP(
    "blender-mcp",
    log_level="INFO",
    host=os.getenv("BLENDER_MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("BLENDER_MCP_PORT", "9879")),
)

def RO():
    return dict(annotations=ToolAnnotations(readOnlyHint=True))
def RW():
    return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))


from mcp_tools import TOOL_FUNCTIONS, READ_ONLY

for _fn in TOOL_FUNCTIONS:
    _kw = RO() if _fn.__name__ in READ_ONLY else RW()
    mcp.tool(**_kw)(_fn)







# ─── Puente al ToolRegistry (228 tools de src/tools/**) ───
# Sin estas tres tools el registry es inalcanzable desde un cliente MCP:
# se exponen como catálogo + despacho genérico en vez de 228 entradas planas,
# que saturarían la lista de tools de cualquier cliente.

@mcp.tool(**RO())
def list_registry_tools(category: str = "") -> str:
    """Lista el catálogo completo de tools de Blender (228: mallas, materiales,
    nodos de geometría/shader, rigging, render, IO, UV, impresión 3D...).
    Filtra por categoría: objects, materials, lights, modifiers, animation,
    render, io, rigging, camera, scene, scene_utils, uv_texture, printing,
    batch, geometry_nodes, geometry_nodes_extended, shader_nodes,
    shader_nodes_extended. Úsala antes de call_registry_tool."""
    r = get_blender().send_command("list_tools", {"category": category or None})
    return json.dumps(r, indent=2)


@mcp.tool(**RO())
def describe_registry_tool(name: str) -> str:
    """Devuelve la firma exacta de una tool del catálogo: parámetros, tipos,
    obligatoriedad, permiso y ejemplos de uso. Consúltala antes de invocar."""
    r = get_blender().send_command("describe_tool", {"name": name})
    return json.dumps(r, indent=2)


@mcp.tool(**RW())
def call_registry_tool(name: str, params: dict | None = None) -> str:
    """Ejecuta una tool del catálogo por nombre, p.ej. name='object.create'
    con params={'type':'MESH','name':'Cubo'}. Usa describe_registry_tool
    primero para conocer los parámetros exactos."""
    r = get_blender().send_command("call_tool", {"tool_name": name, "params": params or {}})
    return json.dumps(r, indent=2)


# ─── Lote transaccional ───

@mcp.tool(**RW())
def run_batch(steps: list[dict], atomic: bool = True, label: str = "Axiom Batch") -> str:
    """Ejecuta varias operaciones como UNA transacción con rollback.

    Cada paso es {"op": <nombre>, "params": {...}}, donde <nombre> es un
    comando (snap_and_parent, create_model, align_objects...) o una tool del
    catálogo (object.create, geonodes.scatter...).

    Con atomic=True un fallo revierte el lote entero y la escena queda intacta.
    Prefiérela a encadenar llamadas sueltas: evita escenas a medio construir.

    Ejemplo: steps=[{"op":"create_model","params":{"primitive":"CUBE","name":"Base"}},
                    {"op":"array_object","params":{"name":"Base","count":4}}]"""
    r = get_blender().send_command(
        "run_batch", {"steps": steps, "atomic": atomic, "label": label})
    return json.dumps(r, indent=2)


# ─── Inspección de escena ───

@mcp.tool(**RO())
def get_scene_graph(include_data: bool = True) -> str:
    """Jerarquía completa de la escena (padre→hijo) con dimensiones, materiales,
    modificadores y polígonos. A diferencia de get_scene_info no trunca ni
    aplana: úsala para entender un ensamblaje antes de modificarlo."""
    r = get_blender().send_command("scene_graph", {"include_data": include_data})
    return json.dumps(r, indent=2)


@mcp.tool(**RO())
def measure(name_a: str, name_b: str = "") -> str:
    """Mide un objeto (dimensiones, bbox, centro, volumen) o la relación entre
    dos: distancia entre centros, hueco real entre superficies por eje
    (negativo = se solapan) y si colisionan. Verifica encajes antes de anclar."""
    r = get_blender().send_command("measure", {"name_a": name_a, "name_b": name_b or None})
    return json.dumps(r, indent=2)


@mcp.tool(**RO())
def find_objects(name_contains: str = "", type: str = "",
                 min_polygons: int | None = None, has_material: str = "") -> str:
    """Busca objetos por nombre, tipo (MESH, LIGHT, CAMERA...), complejidad
    mínima de malla o material. Evita descargar la escena entera."""
    r = get_blender().send_command("find_objects", {
        "name_contains": name_contains, "type": type or None,
        "min_polygons": min_polygons, "has_material": has_material or None})
    return json.dumps(r, indent=2)


# ─── Ensamblaje extendido (sobre el sistema de 27 anclas) ───

@mcp.tool(**RW())
def align_objects(names: list[str], axis: str = "Z", mode: str = "MIN",
                  reference: str = "") -> str:
    """Alinea objetos por su bounding box real (no por su origen, que suele
    estar descentrado). axis: X|Y|Z. mode: MIN (caras inferiores), CENTER o MAX.
    reference fija el objeto que no se mueve; por defecto el primero."""
    r = get_blender().send_command("align_objects", {
        "names": names, "axis": axis, "mode": mode, "reference": reference or None})
    return json.dumps(r, indent=2)


@mcp.tool(**RW())
def distribute_objects(names: list[str], axis: str = "X",
                       spacing: float | None = None) -> str:
    """Reparte objetos sobre un eje. Sin 'spacing' los separa uniformemente
    conservando los dos extremos; con 'spacing' deja ese hueco fijo en metros
    entre superficies consecutivas."""
    r = get_blender().send_command("distribute_objects", {
        "names": names, "axis": axis, "spacing": spacing})
    return json.dumps(r, indent=2)


@mcp.tool(**RW())
def array_object(name: str, count: int = 3, axis: str = "X",
                 gap: float = 0.0, linked: bool = False) -> str:
    """Duplica un objeto en fila separándolo por su propio tamaño más 'gap'
    metros. A diferencia del modificador Array crea objetos reales, cada uno
    seleccionable y editable. linked=True comparte la malla (más ligero)."""
    r = get_blender().send_command("array_object", {
        "name": name, "count": count, "axis": axis, "gap": gap, "linked": linked})
    return json.dumps(r, indent=2)


@mcp.resource("blender://scene/info")
def resource_scene_info() -> str:
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)


def main():
    transport = os.getenv("BLENDER_MCP_MODE", "stdio")
    logger.info("Memulai MCP Server (%s transport)...", transport)
    mcp.run(transport=transport)

if __name__ == "__main__":
    main()
