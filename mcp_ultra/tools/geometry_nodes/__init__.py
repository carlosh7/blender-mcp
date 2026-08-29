"""
blender-mcp-ultra — Geometry Node Tools
"""

from typing import Any, Dict

from ...core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool(
        "geonodes.add_modifier",
        ToolCategory.GEOMETRY_NODES,
        "Add Geometry Nodes modifier",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}, "node_group": {"type": "str"}},
    ),
    Tool(
        "geonodes.create_group",
        ToolCategory.GEOMETRY_NODES,
        "Create a new geometry node group",
        ToolPermission.WRITE,
        {"name": {"type": "str"}},
    ),
    Tool(
        "geonodes.add_node",
        ToolCategory.GEOMETRY_NODES,
        "Add a node to geometry node group",
        ToolPermission.WRITE,
        {
            "group_name": {"type": "str", "required": True},
            "node_type": {"type": "str", "required": True},
        },
    ),
    Tool(
        "geonodes.node_set_input",
        ToolCategory.GEOMETRY_NODES,
        "Fijar valor default de un input de nodo (sin link)",
        ToolPermission.WRITE,
        {
            "group_name": {"type": "str", "required": True},
            "node_name": {"type": "str", "required": True},
            "input_name": {"type": "str", "required": True},
            "value": {"type": "any", "required": True},
        },
    ),
    Tool(
        "geonodes.connect",
        ToolCategory.GEOMETRY_NODES,
        "Connect nodes in geometry node group",
        ToolPermission.WRITE,
        {
            "group_name": {"type": "str", "required": True},
            "from_node": {"type": "str", "required": True},
            "from_socket": {"type": "str", "required": True},
            "to_node": {"type": "str", "required": True},
            "to_socket": {"type": "str", "required": True},
        },
    ),
    Tool(
        "geonodes.list_groups",
        ToolCategory.GEOMETRY_NODES,
        "List all geometry node groups",
        ToolPermission.READ_ONLY,
        {},
    ),
    Tool(
        "geonodes.scatter",
        ToolCategory.GEOMETRY_NODES,
        "Quick scatter setup on faces",
        ToolPermission.WRITE,
        {
            "object_name": {"type": "str"},
            "density": {"type": "float"},
            "instance_name": {"type": "str"},
        },
    ),
    Tool(
        "geonodes.array",
        ToolCategory.GEOMETRY_NODES,
        "Quick array setup",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}, "count": {"type": "int"}, "offset_axis": {"type": "str"}},
    ),
    Tool(
        "geonodes.delete_geometry",
        ToolCategory.GEOMETRY_NODES,
        "Delete geometry by selection",
        ToolPermission.WRITE,
        {"object_name": {"type": "str"}, "mode": {"type": "str"}},
    ),
]


def add_modifier(object_name: str, node_group: str = None) -> dict:
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}
        mod = obj.modifiers.new(name="GeometryNodes", type="NODES")
        if node_group:
            ng = bpy.data.node_groups.get(node_group)
            if ng:
                mod.node_group = ng
        return {"success": True, "object": object_name, "modifier": mod.name}
    except Exception as e:
        return {"error": str(e)}


def create_group(name: str = "GeometryNodes") -> dict:
    try:
        import bpy

        ng = bpy.data.node_groups.new(name=name, type="GeometryNodeTree")
        ng.nodes.new("NodeGroupInput")
        ng.nodes.new("NodeGroupOutput")
        return {"success": True, "name": ng.name}
    except Exception as e:
        return {"error": str(e)}


def add_node_to_group(group_name: str, node_type: str) -> dict:
    try:
        import bpy

        ng = bpy.data.node_groups.get(group_name)
        if not ng:
            return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new(type=node_type)
        return {"success": True, "node": node.name, "type": node_type}
    except Exception as e:
        return {"error": str(e)}


def set_node_input(group_name: str, node_name: str, input_name: str, value) -> dict:
    """Fijar el default value de un input de nodo (valores, no links)."""
    import bpy

    ng = bpy.data.node_groups.get(group_name)
    if not ng:
        return {"error": f"Node group not found: {group_name}"}
    node = ng.nodes.get(node_name)
    if node is None:
        return {"error": f"Node not found: {node_name}"}
    sock = node.inputs.get(input_name)
    if sock is None:
        return {"error": f"Input '{input_name}' no existe en {node_name}"}
    if not hasattr(sock, "default_value"):
        return {"error": f"Input '{input_name}' no acepta valor directo"}
    sock.default_value = value
    return {"success": True, "set": f"{node_name}.{input_name}", "value": str(value)}


def connect_in_group(
    group_name: str, from_node: str, from_socket: str, to_node: str, to_socket: str
) -> dict:
    try:
        import bpy

        ng = bpy.data.node_groups.get(group_name)
        if not ng:
            return {"error": f"Node group not found: {group_name}"}
        src = ng.nodes.get(from_node)
        dst = ng.nodes.get(to_node)
        if not src:
            return {"error": f"Source node not found: {from_node}"}
        if not dst:
            return {"error": f"Target node not found: {to_node}"}
        ng.links.new(src.outputs[from_socket], dst.inputs[to_socket])
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def list_groups() -> dict:
    try:
        import bpy

        groups = [
            {"name": ng.name, "type": ng.type, "users": ng.users}
            for ng in bpy.data.node_groups
            if ng.type == "GEOMETRY"
        ]
        return {"count": len(groups), "groups": groups}
    except ImportError:
        return {"error": "Blender not available"}


def scatter(object_name: str = None, density: float = 10.0, instance_name: str = None) -> dict:
    try:
        import bpy

        obj = (
            bpy.data.objects.get(object_name)
            if object_name
            else getattr(bpy.context, "active_object", None)
        )
        if not obj:
            return {"error": "No object specified or found"}
        ng = bpy.data.node_groups.new(name="Scatter", type="GeometryNodeTree")
        inp = ng.nodes.new("NodeGroupInput")
        out = ng.nodes.new("NodeGroupOutput")
        dop = ng.nodes.new("GeometryNodeDistributePointsOnFaces")
        dop.inputs["Density"].default_value = density
        iop = ng.nodes.new("GeometryNodeInstanceOnPoints")
        if instance_name:
            inst = bpy.data.objects.get(instance_name)
            if inst:
                oinfo = ng.nodes.new("GeometryNodeObjectInfo")
                oinfo.inputs["Object"].default_value = inst
                ng.links.new(oinfo.outputs["Geometry"], iop.inputs["Instance"])
        ng.links.new(inp.outputs[0], dop.inputs["Geometry"])
        ng.links.new(dop.outputs["Points"], iop.inputs["Points"])
        ng.links.new(iop.outputs["Instances"], out.inputs[0])
        mod = obj.modifiers.new(name="Scatter", type="NODES")
        mod.node_group = ng
        return {"success": True, "object": obj.name, "density": density}
    except Exception as e:
        return {"error": str(e)}


def array(object_name: str = None, count: int = 5, offset_axis: str = "X") -> dict:
    try:
        import bpy

        obj = (
            bpy.data.objects.get(object_name)
            if object_name
            else getattr(bpy.context, "active_object", None)
        )
        if not obj:
            return {"error": "No object specified or found"}
        mod = obj.modifiers.new(name="Array", type="ARRAY")
        mod.count = count
        axis_map = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}
        offset = axis_map.get(offset_axis.upper(), (1, 0, 0))
        mod.use_relative_offset = True
        mod.relative_offset_displace = offset
        return {"success": True, "object": obj.name, "count": count, "axis": offset_axis}
    except Exception as e:
        return {"error": str(e)}


def delete_geometry(object_name: str = None, mode: str = "ALL") -> dict:
    try:
        import bpy

        obj = (
            bpy.data.objects.get(object_name)
            if object_name
            else getattr(bpy.context, "active_object", None)
        )
        if not obj:
            return {"error": "No object specified or found"}
        ng = bpy.data.node_groups.new(name="DeleteGeometry", type="GeometryNodeTree")
        inp = ng.nodes.new("NodeGroupInput")
        out = ng.nodes.new("NodeGroupOutput")
        del_geo = ng.nodes.new("GeometryNodeDeleteGeometry")
        del_geo.domain = "FACE"
        ng.links.new(inp.outputs[0], del_geo.inputs["Geometry"])
        ng.links.new(del_geo.outputs["Geometry"], out.inputs[0])
        mod = obj.modifiers.new(name="DeleteGeo", type="NODES")
        mod.node_group = ng
        return {"success": True, "object": obj.name}
    except Exception as e:
        return {"error": str(e)}


HANDLERS = {
    "geonodes.add_modifier": add_modifier,
    "geonodes.create_group": create_group,
    "geonodes.add_node": add_node_to_group,
    "geonodes.node_set_input": set_node_input,
    "geonodes.connect": connect_in_group,
    "geonodes.list_groups": list_groups,
    "geonodes.scatter": scatter,
    "geonodes.array": array,
    "geonodes.delete_geometry": delete_geometry,
}
