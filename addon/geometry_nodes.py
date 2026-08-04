"""
geometry_nodes.py — Perintah modifier Geometry Nodes.
Aman di background: wiring node group + modifier murni data API.
"""
import bpy


def _ensure_gn_group(name):
    group = bpy.data.node_groups.get(name)
    if group is None:
        group = bpy.data.node_groups.new(name, type="GeometryNodeTree")
        if hasattr(group, "interface"):
            group.interface.new_socket(
                name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
            group.interface.new_socket(
                name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        else:
            group.inputs.new("NodeSocketGeometry", "Geometry")
            group.outputs.new("NodeSocketGeometry", "Geometry")
        inp = group.nodes.new("NodeGroupInput")
        out = group.nodes.new("NodeGroupOutput")
        group.links.new(inp.outputs["Geometry"], out.inputs["Geometry"])
    return group


def add_geometry_nodes_modifier(object_name="", name="GeometryNodes"):
    """Tambahkan modifier dan node group Geometry Nodes baru ke objek."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    group = _ensure_gn_group(f"{obj.name}_GN")
    mod = obj.modifiers.new(name=name, type="NODES")
    mod.node_group = group
    return {"status": "success", "object": obj.name, "modifier": mod.name,
            "node_group": group.name}


def list_gn_modifiers(object_name=""):
    """Daftar modifier Geometry Nodes pada objek."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    gns = [{"name": m.name,
            "node_group": m.node_group.name if m.node_group else None}
           for m in obj.modifiers if m.type == "NODES"]
    return {"object": obj.name, "count": len(gns), "modifiers": gns}


def scatter_instances(object_name="", instance_object="", count=100,
                      seed=0, scale=(1.0, 1.0, 1.0)):
    """Sebarkan instance pada permukaan objek lewat Geometry Nodes."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    inst = bpy.data.objects.get(instance_object)
    if inst is None:
        return {"error": f"Objek instance tidak ditemukan: {instance_object}"}

    group = _ensure_gn_group(f"{obj.name}_Scatter")
    nodes = group.nodes
    # clear default wiring, rebuild: Input -> Distribute Points -> Instance on Points -> Output
    for n in list(nodes):
        nodes.remove(n)

    inp = nodes.new("NodeGroupInput")
    out = nodes.new("NodeGroupOutput")
    dist = nodes.new("GeometryNodeDistributePointsOnFaces")
    dist.distribute_method = "RANDOM"
    dist.inputs["Density"].default_value = max(1, int(count))
    dist.inputs["Seed"].default_value = int(seed)
    inst_node = nodes.new("GeometryNodeInstanceOnPoints")
    obj_node = nodes.new("GeometryNodeObjectInfo")
    obj_node.inputs["Object"].default_value = inst
    scale_node = nodes.new("GeometryNodeTransform")
    from mathutils import Vector
    scale_node.inputs["Scale"].default_value = Vector(scale)

    group.links.new(inp.outputs["Geometry"], dist.inputs["Mesh"])
    group.links.new(dist.outputs["Points"], inst_node.inputs["Points"])
    group.links.new(obj_node.outputs["Geometry"], scale_node.inputs["Geometry"])
    group.links.new(scale_node.outputs["Geometry"], inst_node.inputs["Instance"])
    group.links.new(inst_node.outputs["Instances"], out.inputs["Geometry"])

    mod = obj.modifiers.new(name="Scatter_GN", type="NODES")
    mod.node_group = group
    return {"status": "success", "object": obj.name, "modifier": mod.name,
            "instance": inst.name, "count": count, "seed": seed}


def gn_add_node(object_name="", node_type="GeometryNodeTransform", name=""):
    """Tambahkan node ke node group Geometry Nodes pertama pada objek."""
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    mod = next((m for m in obj.modifiers if m.type == "NODES"), None)
    if mod is None or mod.node_group is None:
        return {"error": f"{obj.name} belum punya modifier Geometry Nodes."}
    node = mod.node_group.nodes.new(node_type)
    if name:
        node.name = name
    return {"status": "success", "node": node.name, "type": node.type}
