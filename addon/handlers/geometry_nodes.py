"""
blender-mcp — Geometry Nodes Handler
Create and modify Geometry Nodes modifiers and node groups.
"""
import bpy
from . import BaseHandler


class GeometryNodesHandler(BaseHandler):
    """Create and edit Geometry Nodes setups, scatter, array along curve."""

    namespace = "geometry_nodes"

    @staticmethod
    def cmd_add_geometry_nodes_modifier(object_name=""):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object specified"}
        mod = obj.modifiers.new(name="GeometryNodes", type='NODES')
        # Create a new node group
        group = bpy.data.node_groups.new(name=f"{obj.name}_GN", type='GeometryNodeTree')
        mod.node_group = group
        # Add default input/output nodes
        group.nodes.new('NodeGroupInput').location = (-200, 0)
        group.nodes.new('NodeGroupOutput').location = (200, 0)
        return {"object": obj.name, "modifier": "GeometryNodes", "group": group.name}

    @staticmethod
    def cmd_add_gn_node(object_name="", node_type="GeometryNodeDistributePointsOnFaces", location=(0, 0)):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        mod = obj.modifiers.get("GeometryNodes")
        if not mod or not mod.node_group:
            return {"error": "No Geometry Nodes modifier on object"}
        group = mod.node_group
        node = group.nodes.new(type=node_type)
        node.location = location
        return {"node": node.name, "type": node_type, "group": group.name}

    @staticmethod
    def cmd_connect_gn_nodes(object_name="", from_node="", from_socket="", to_node="", to_socket=""):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        mod = obj.modifiers.get("GeometryNodes")
        if not mod or not mod.node_group:
            return {"error": "No Geometry Nodes modifier"}
        group = mod.node_group
        src = group.nodes.get(from_node)
        dst = group.nodes.get(to_node)
        if not src or not dst:
            return {"error": "Source or destination node not found"}
        out = src.outputs.get(from_socket) or list(src.outputs)[0]
        inp = dst.inputs.get(to_socket) or list(dst.inputs)[0]
        group.links.new(out, inp)
        return {"connected": f"{from_node} → {to_node}"}

    @staticmethod
    def cmd_setup_scatter(object_name="", scatter_density=10.0, seed=0):
        """Quick scatter setup: distribute points + instance on points."""
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        mod = obj.modifiers.new(name="Scatter", type='NODES')
        group = bpy.data.node_groups.new(name=f"{obj.name}_Scatter", type='GeometryNodeTree')
        mod.node_group = group

        input_node = group.nodes.new('NodeGroupInput')
        input_node.location = (-600, 0)
        output_node = group.nodes.new('NodeGroupOutput')
        output_node.location = (400, 0)

        distribute = group.nodes.new('GeometryNodeDistributePointsOnFaces')
        distribute.location = (-300, 0)
        distribute.inputs['Density'].default_value = scatter_density
        distribute.inputs['Seed'].default_value = seed

        instance = group.nodes.new('GeometryNodeInstanceOnPoints')
        instance.location = (0, 0)

        join = group.nodes.new('GeometryNodeJoinGeometry')
        join.location = (200, 0)

        group.links.new(input_node.outputs['Geometry'], distribute.inputs['Mesh'])
        group.links.new(distribute.outputs['Points'], instance.inputs['Points'])
        group.links.new(instance.outputs['Instances'], join.inputs['Geometry'])
        group.links.new(join.outputs['Geometry'], output_node.inputs['Geometry'])
        group.links.new(input_node.outputs['Geometry'], output_node.inputs['Geometry'])

        return {"object": obj.name, "modifier": "Scatter", "density": scatter_density}

    @staticmethod
    def cmd_list_gn_modifiers(object_name=""):
        obj = bpy.data.objects.get(object_name) or bpy.context.active_object
        if not obj:
            return {"error": "No object"}
        mods = []
        for m in obj.modifiers:
            if m.type == 'NODES' and m.node_group:
                nodes_list = [{"name": n.name, "type": n.type} for n in m.node_group.nodes]
                mods.append({"name": m.name, "group": m.node_group.name, "nodes": nodes_list})
        return {"object": obj.name, "modifiers": mods}
