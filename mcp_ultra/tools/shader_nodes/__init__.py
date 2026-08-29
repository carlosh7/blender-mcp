"""
blender-mcp-ultra — Shader Node Tools
"""

from typing import Any, Dict, Optional

from ...core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool(
        "shader.add_node",
        ToolCategory.SHADER_NODES,
        "Add a shader node",
        ToolPermission.WRITE,
        {
            "material_name": {"type": "str", "required": True},
            "node_type": {"type": "str", "required": True},
            "location": {"type": "tuple"},
        },
    ),
    Tool(
        "shader.connect_nodes",
        ToolCategory.SHADER_NODES,
        "Connect two nodes",
        ToolPermission.WRITE,
        {
            "material_name": {"type": "str", "required": True},
            "from_node": {"type": "str", "required": True},
            "from_socket": {"type": "str", "required": True},
            "to_node": {"type": "str", "required": True},
            "to_socket": {"type": "str", "required": True},
        },
    ),
    Tool(
        "shader.set_node_value",
        ToolCategory.SHADER_NODES,
        "Set a node input value",
        ToolPermission.WRITE,
        {
            "material_name": {"type": "str", "required": True},
            "node_name": {"type": "str", "required": True},
            "input_name": {"type": "str", "required": True},
            "value": {"required": True},
        },
    ),
    Tool(
        "shader.delete_node",
        ToolCategory.SHADER_NODES,
        "Delete a shader node",
        ToolPermission.WRITE,
        {
            "material_name": {"type": "str", "required": True},
            "node_name": {"type": "str", "required": True},
        },
    ),
    Tool(
        "shader.list_nodes",
        ToolCategory.SHADER_NODES,
        "List all nodes in material",
        ToolPermission.READ_ONLY,
        {"material_name": {"type": "str", "required": True}},
    ),
    Tool(
        "shader.create_material_nodes",
        ToolCategory.SHADER_NODES,
        "Create common material setups",
        ToolPermission.WRITE,
        {
            "material_name": {"type": "str", "required": True},
            "preset": {"type": "str", "required": True},
        },
    ),
    Tool(
        "shader.group_nodes",
        ToolCategory.SHADER_NODES,
        "Group selected nodes",
        ToolPermission.WRITE,
        {
            "material_name": {"type": "str", "required": True},
            "node_names": {"type": "list", "required": True},
            "group_name": {"type": "str"},
        },
    ),
    Tool(
        "shader.ungroup_nodes",
        ToolCategory.SHADER_NODES,
        "Ungroup a node group",
        ToolPermission.WRITE,
        {
            "material_name": {"type": "str", "required": True},
            "group_name": {"type": "str", "required": True},
        },
    ),
]


def add_node(material_name: str, node_type: str, location: tuple = (0, 0)) -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new(type=node_type)
        node.location = location
        return {"success": True, "node": node.name, "type": node_type}
    except Exception as e:
        return {"error": str(e)}


def connect_nodes(
    material_name: str, from_node: str, from_socket: str, to_node: str, to_socket: str
) -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material not found: {material_name}"}
        nt = mat.node_tree
        src = nt.nodes.get(from_node)
        dst = nt.nodes.get(to_node)
        if not src:
            return {"error": f"Source node not found: {from_node}"}
        if not dst:
            return {"error": f"Target node not found: {to_node}"}
        nt.links.new(src.outputs[from_socket], dst.inputs[to_socket])
        return {
            "success": True,
            "from": f"{from_node}.{from_socket}",
            "to": f"{to_node}.{to_socket}",
        }
    except Exception as e:
        return {"error": str(e)}


def set_node_value(material_name: str, node_name: str, input_name: str, value) -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.get(node_name)
        if not node:
            return {"error": f"Node not found: {node_name}"}
        node.inputs[input_name].default_value = value
        return {"success": True, "node": node_name, "input": input_name}
    except Exception as e:
        return {"error": str(e)}


def delete_node(material_name: str, node_name: str) -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.get(node_name)
        if not node:
            return {"error": f"Node not found: {node_name}"}
        mat.node_tree.nodes.remove(node)
        return {"success": True, "node": node_name}
    except Exception as e:
        return {"error": str(e)}


def list_nodes(material_name: str) -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material not found: {material_name}"}
        nodes = [
            {"name": n.name, "type": n.type, "location": list(n.location)}
            for n in mat.node_tree.nodes
        ]
        return {"material": material_name, "count": len(nodes), "nodes": nodes}
    except ImportError:
        return {"error": "Blender not available"}


def create_material_nodes(material_name: str, preset: str) -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        output = nt.nodes.new("ShaderNodeOutputMaterial")
        output.location = (400, 0)
        if preset.lower() == "glass":
            shader = nt.nodes.new("ShaderNodeBsdfGlass")
            shader.inputs["Color"].default_value = (0.8, 0.9, 1.0, 1)
            shader.inputs["Roughness"].default_value = 0.0
        elif preset.lower() == "emission":
            shader = nt.nodes.new("ShaderNodeEmission")
            shader.inputs["Color"].default_value = (1, 1, 1, 1)
            shader.inputs["Strength"].default_value = 5.0
        else:
            shader = nt.nodes.new("ShaderNodeBsdfPrincipled")
        shader.location = (0, 0)
        nt.links.new(shader.outputs[0], output.inputs[0])
        return {"success": True, "material": material_name, "preset": preset}
    except Exception as e:
        return {"error": str(e)}


def group_nodes(material_name: str, node_names: list, group_name: str = "NodeGroup") -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material not found: {material_name}"}
        nt = mat.node_tree
        nodes_to_group = [nt.nodes.get(n) for n in node_names if nt.nodes.get(n)]
        if len(nodes_to_group) < 2:
            return {"error": "Need at least 2 nodes"}
        # Try to set active object for node editing
        try:
            active = getattr(bpy.context, "active_object", None)
            if active:
                bpy.context.view_layer.objects.active = active
        except Exception:
            pass
        for n in nodes_to_group:
            n.select = True
        bpy.ops.node.group()
        return {"success": True, "group_name": group_name}
    except Exception as e:
        return {"error": str(e)}


def ungroup_nodes(material_name: str, group_name: str) -> dict:
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.get(group_name)
        if not node:
            return {"error": f"Node group not found: {group_name}"}
        mat.node_tree.nodes.active = node
        bpy.ops.node.group_unmake()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


HANDLERS = {
    "shader.add_node": add_node,
    "shader.connect_nodes": connect_nodes,
    "shader.set_node_value": set_node_value,
    "shader.delete_node": delete_node,
    "shader.list_nodes": list_nodes,
    "shader.create_material_nodes": create_material_nodes,
    "shader.group_nodes": group_nodes,
    "shader.ungroup_nodes": ungroup_nodes,
}
