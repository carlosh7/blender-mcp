"""
blender-mcp-ultra — Shader Node Tools
"""
from typing import Any, Dict, Optional
from core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool("shader.add_node", ToolCategory.SHADER_NODES, "Add a shader node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "node_type": {"type": "str", "required": True},
          "location": {"type": "tuple"}}),
    Tool("shader.connect_nodes", ToolCategory.SHADER_NODES, "Connect two nodes", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "from_node": {"type": "str", "required": True},
          "from_socket": {"type": "str", "required": True}, "to_node": {"type": "str", "required": True},
          "to_socket": {"type": "str", "required": True}}),
    Tool("shader.set_node_value", ToolCategory.SHADER_NODES, "Set a node input value", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "node_name": {"type": "str", "required": True},
          "input_name": {"type": "str", "required": True}, "value": {"required": True}}),
    Tool("shader.delete_node", ToolCategory.SHADER_NODES, "Delete a shader node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "node_name": {"type": "str", "required": True}}),
    Tool("shader.list_nodes", ToolCategory.SHADER_NODES, "List all nodes in material", ToolPermission.READ_ONLY,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.create_material_nodes", ToolCategory.SHADER_NODES, "Create common material setups", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "preset": {"type": "str", "required": True}}),
    Tool("shader.group_nodes", ToolCategory.SHADER_NODES, "Group selected nodes", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "node_names": {"type": "list", "required": True},
          "group_name": {"type": "str"}}),
    Tool("shader.ungroup_nodes", ToolCategory.SHADER_NODES, "Ungroup a node group", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "group_name": {"type": "str", "required": True}}),
]

def add_node(material_name: str, node_type: str, location: tuple = (0, 0)) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new(type=node_type)
        node.location = location
        return {"success": True, "node": node.name, "type": node_type}
    except Exception as e: return {"error": str(e)}

def connect_nodes(material_name: str, from_node: str, from_socket: str, to_node: str, to_socket: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        nt = mat.node_tree
        src = nt.nodes.get(from_node)
        dst = nt.nodes.get(to_node)
        if not src: return {"error": f"Source node not found: {from_node}"}
        if not dst: return {"error": f"Target node not found: {to_node}"}
        nt.links.new(src.outputs[from_socket], dst.inputs[to_socket])
        return {"success": True, "from": f"{from_node}.{from_socket}", "to": f"{to_node}.{to_socket}"}
    except Exception as e: return {"error": str(e)}

def set_node_value(material_name: str, node_name: str, input_name: str, value) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.get(node_name)
        if not node: return {"error": f"Node not found: {node_name}"}
        node.inputs[input_name].default_value = value
        return {"success": True, "node": node_name, "input": input_name}
    except Exception as e: return {"error": str(e)}

def delete_node(material_name: str, node_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.get(node_name)
        if not node: return {"error": f"Node not found: {node_name}"}
        mat.node_tree.nodes.remove(node)
        return {"success": True, "node": node_name}
    except Exception as e: return {"error": str(e)}

def list_nodes(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        nodes = [{"name": n.name, "type": n.type, "location": list(n.location)} for n in mat.node_tree.nodes]
        return {"material": material_name, "count": len(nodes), "nodes": nodes}
    except ImportError: return {"error": "Blender not available"}

def create_material_nodes(material_name: str, preset: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat: return {"error": f"Material not found: {material_name}"}
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        output = nt.nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, 0)
        if preset.lower() == "glass":
            shader = nt.nodes.new('ShaderNodeBsdfGlass')
            shader.inputs['Color'].default_value = (0.8, 0.9, 1.0, 1)
            shader.inputs['Roughness'].default_value = 0.0
        elif preset.lower() == "emission":
            shader = nt.nodes.new('ShaderNodeEmission')
            shader.inputs['Color'].default_value = (1, 1, 1, 1)
            shader.inputs['Strength'].default_value = 5.0
        else:
            shader = nt.nodes.new('ShaderNodeBsdfPrincipled')
        shader.location = (0, 0)
        nt.links.new(shader.outputs[0], output.inputs[0])
        return {"success": True, "material": material_name, "preset": preset}
    except Exception as e: return {"error": str(e)}

def group_nodes(material_name: str, node_names: list, group_name: str = "NodeGroup") -> Dict:
    """Kumpulkan beberapa node ke dalam satu node group.

    Memakai data API (bukan `bpy.ops.node.group`), karena operator itu butuh
    editor node yang terbuka sehingga gagal di mode background, dan namanya
    sudah berubah di Blender 4.4 (`group_make`).
    """
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material tidak ditemukan: {material_name}"}
        nt = mat.node_tree
        picked = [nt.nodes.get(n) for n in node_names]
        picked = [n for n in picked if n is not None]
        if len(picked) < 2:
            return {"error": "Butuh minimal 2 node yang valid untuk digrupkan."}

        group = bpy.data.node_groups.new(group_name, "ShaderNodeTree")
        _group_io(group, "INPUT")
        _group_io(group, "OUTPUT")

        # Salin node ke dalam group, lalu hapus aslinya dari material.
        mapping = {}
        for node in picked:
            clone = group.nodes.new(node.bl_idname)
            clone.location = node.location
            for src_in, dst_in in zip(node.inputs, clone.inputs):
                if hasattr(src_in, "default_value") and hasattr(dst_in, "default_value"):
                    try:
                        dst_in.default_value = src_in.default_value
                    except Exception:
                        pass
            mapping[node.name] = clone

        # Pertahankan koneksi yang kedua ujungnya ikut masuk group.
        inside = {n.name for n in picked}
        for link in list(nt.links):
            if link.from_node.name in inside and link.to_node.name in inside:
                group.links.new(
                    mapping[link.from_node.name].outputs[link.from_socket.name],
                    mapping[link.to_node.name].inputs[link.to_socket.name])

        for node in picked:
            nt.nodes.remove(node)

        holder = nt.nodes.new("ShaderNodeGroup")
        holder.node_tree = group
        holder.name = group_name
        return {"success": True, "group_name": group.name,
                "grouped": len(mapping), "node": holder.name}
    except Exception as e:
        return {"error": str(e)}


def _group_io(group, in_out: str):
    """Siapkan socket antarmuka group, lintas versi.

    Blender 4.0+ memakai `group.interface.new_socket(...)`; versi lama
    memakai `group.inputs.new(...)` / `group.outputs.new(...)`.
    """
    try:
        group.interface.new_socket(
            name="Shader", in_out=in_out, socket_type="NodeSocketShader")
    except AttributeError:
        coll = group.inputs if in_out == "INPUT" else group.outputs
        coll.new("NodeSocketShader", "Shader")


def ungroup_nodes(material_name: str, group_name: str) -> Dict:
    """Bongkar node group: isinya dikembalikan ke node tree material."""
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree:
            return {"error": f"Material tidak ditemukan: {material_name}"}
        nt = mat.node_tree
        holder = nt.nodes.get(group_name)
        if not holder or holder.bl_idname != "ShaderNodeGroup":
            return {"error": f"Node group tidak ditemukan: {group_name}"}
        inner = holder.node_tree
        if inner is None:
            return {"error": f"{group_name} tidak menyimpan node tree."}

        mapping = {}
        for node in inner.nodes:
            if node.bl_idname in ("NodeGroupInput", "NodeGroupOutput"):
                continue
            clone = nt.nodes.new(node.bl_idname)
            clone.location = (holder.location[0] + node.location[0],
                              holder.location[1] + node.location[1])
            for src_in, dst_in in zip(node.inputs, clone.inputs):
                if hasattr(src_in, "default_value") and hasattr(dst_in, "default_value"):
                    try:
                        dst_in.default_value = src_in.default_value
                    except Exception:
                        pass
            mapping[node.name] = clone

        for link in inner.links:
            a = mapping.get(link.from_node.name)
            b = mapping.get(link.to_node.name)
            if a is not None and b is not None:
                nt.links.new(a.outputs[link.from_socket.name],
                             b.inputs[link.to_socket.name])

        nt.nodes.remove(holder)
        return {"success": True, "ungrouped": len(mapping)}
    except Exception as e:
        return {"error": str(e)}

HANDLERS = {
    "shader.add_node": add_node, "shader.connect_nodes": connect_nodes,
    "shader.set_node_value": set_node_value, "shader.delete_node": delete_node,
    "shader.list_nodes": list_nodes, "shader.create_material_nodes": create_material_nodes,
    "shader.group_nodes": group_nodes, "shader.ungroup_nodes": ungroup_nodes,
}
