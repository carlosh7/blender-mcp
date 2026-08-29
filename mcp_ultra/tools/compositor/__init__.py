"""
blender-mcp-ultra — Compositor Tools
Nodos de composición: crear, conectar y fijar inputs en scene.node_tree.
"""

from typing import Any, Dict, List

from ...core.entities import Tool, ToolCategory, ToolPermission

try:
    import bpy
except ImportError:  # fuera de Blender: solo definiciones
    bpy = None


def _comp_tree():
    scene = bpy.context.scene
    tree = getattr(scene, "node_tree", None)  # ≤4.x
    if tree is not None:
        scene.use_nodes = True
        return tree
    # 5.x: el compositor es un node group asignado a la escena
    tree = scene.compositing_node_group
    if tree is None:
        tree = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
        scene.compositing_node_group = tree
        tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        out = tree.nodes.new("NodeGroupOutput")
        out.location = (400, 0)
    return tree


def node_add(node_type: str, location: list[float] = None) -> dict:
    """Añadir nodo de composición por bl_idname (p.ej. CompositorBlurNode)."""
    tree = _comp_tree()
    node = tree.nodes.new(type=node_type)
    if location:
        node.location = location
    return {"node": node.name, "type": node_type}


def node_set_input(
    node_name: str, input_name: str, value: Any = None, link_from: str = None
) -> dict:
    """Fijar valor de un input (o enlazarlo a un output de otro nodo)."""
    tree = _comp_tree()
    node = tree.nodes.get(node_name)
    if node is None:
        raise ValueError(f"Nodo no encontrado: {node_name}")
    sock = node.inputs.get(input_name)
    if sock is None:
        raise ValueError(f"Input '{input_name}' no existe en {node_name}")
    if link_from:
        src_node_name, _, src_out = link_from.partition(".")
        src = tree.nodes.get(src_node_name)
        if src is None:
            raise ValueError(f"Nodo origen no encontrado: {src_node_name}")
        out_sock = src.outputs.get(src_out or src.outputs[0].name)
        tree.links.new(out_sock, sock)
        return {"linked": f"{src_node_name}.{out_sock.name} -> {node_name}.{input_name}"}
    if hasattr(sock, "default_value"):
        sock.default_value = value
        return {"set": f"{node_name}.{input_name}", "value": str(value)}
    raise ValueError(f"Input '{input_name}' no acepta valor directo")


def connect(from_node: str, from_socket: str = "", to_node: str = "", to_socket: str = "") -> dict:
    """Enlazar output→input entre nodos de composición."""
    tree = _comp_tree()
    src = tree.nodes.get(from_node)
    dst = tree.nodes.get(to_node)
    if src is None or dst is None:
        raise ValueError("Nodo origen o destino no encontrado")
    out_sock = src.outputs.get(from_socket) or src.outputs[0]
    in_sock = dst.inputs.get(to_socket) or dst.inputs[0]
    tree.links.new(out_sock, in_sock)
    return {"link": f"{from_node}.{out_sock.name} -> {to_node}.{in_sock.name}"}


def list_nodes() -> dict:
    tree = _comp_tree()
    nodes = []
    for n in tree.nodes:
        nodes.append(
            {
                "name": n.name,
                "type": n.bl_idname,
                "inputs": [s.name for s in n.inputs],
                "outputs": [s.name for s in n.outputs],
            }
        )
    return {"enabled": bpy.context.scene.use_nodes, "nodes": nodes}


TOOLS = [
    Tool(
        "compositor.node_add",
        ToolCategory.RENDER,
        "Añadir nodo de composición por bl_idname (activa use_nodes)",
        ToolPermission.WRITE,
        {
            "node_type": {"type": "str", "required": True},
            "location": {"type": "list"},
        },
    ),
    Tool(
        "compositor.node_set_input",
        ToolCategory.RENDER,
        "Fijar valor de input o enlazar desde otro nodo (link_from='Nodo.Output')",
        ToolPermission.WRITE,
        {
            "node_name": {"type": "str", "required": True},
            "input_name": {"type": "str", "required": True},
            "value": {"type": "any"},
            "link_from": {"type": "str"},
        },
    ),
    Tool(
        "compositor.connect",
        ToolCategory.RENDER,
        "Enlazar output→input entre nodos",
        ToolPermission.WRITE,
        {
            "from_node": {"type": "str", "required": True},
            "from_socket": {"type": "str"},
            "to_node": {"type": "str", "required": True},
            "to_socket": {"type": "str"},
        },
    ),
    Tool(
        "compositor.list_nodes",
        ToolCategory.RENDER,
        "Listar nodos del compositor con inputs/outputs",
        ToolPermission.READ_ONLY,
        {},
    ),
]

HANDLERS = {
    "compositor.node_add": node_add,
    "compositor.node_set_input": node_set_input,
    "compositor.connect": connect,
    "compositor.list_nodes": list_nodes,
}
