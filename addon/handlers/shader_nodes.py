"""
blender-mcp — Shader Nodes Handler
Full node tree control: create, connect, modify nodes in any material or world.
"""
import bpy
from . import BaseHandler


NODE_TYPES = {
    "bsdf_principled": "ShaderNodeBsdfPrincipled",
    "bsdf_diffuse": "ShaderNodeBsdfDiffuse",
    "bsdf_glossy": "ShaderNodeBsdfGlossy",
    "bsdf_transparent": "ShaderNodeBsdfTransparent",
    "bsdf_glass": "ShaderNodeBsdfGlass",
    "bsdf_translucent": "ShaderNodeBsdfTranslucent",
    "emission": "ShaderNodeEmission",
    "mix_shader": "ShaderNodeMixShader",
    "add_shader": "ShaderNodeAddShader",
    "rgb": "ShaderNodeRGB",
    "value": "ShaderNodeValue",
    "mix_rgb": "ShaderNodeMixRGB",
    "color_ramp": "ShaderNodeValToRGB",
    "math": "ShaderNodeMath",
    "vector_math": "ShaderNodeVectorMath",
    "map_range": "ShaderNodeMapRange",
    "clamp": "ShaderNodeClamp",
    "separate_rgb": "ShaderNodeSeparateRGB",
    "combine_rgb": "ShaderNodeCombineRGB",
    "separate_xyz": "ShaderNodeSeparateXYZ",
    "combine_xyz": "ShaderNodeCombineXYZ",
    "bump": "ShaderNodeBump",
    "normal_map": "ShaderNodeNormalMap",
    "displacement": "ShaderNodeDisplacement",
    "tex_image": "ShaderNodeTexImage",
    "tex_environment": "ShaderNodeTexEnvironment",
    "tex_noise": "ShaderNodeTexNoise",
    "tex_wave": "ShaderNodeTexWave",
    "tex_musgrave": "ShaderNodeTexMusgrave",
    "tex_voronoi": "ShaderNodeTexVoronoi",
    "tex_checker": "ShaderNodeTexChecker",
    "tex_gradient": "ShaderNodeTexGradient",
    "tex_coord": "ShaderNodeTexCoord",
    "mapping": "ShaderNodeMapping",
    "uv_map": "ShaderNodeUVMap",
    "object_info": "ShaderNodeObjectInfo",
    "fresnel": "ShaderNodeFresnel",
    "layer_weight": "ShaderNodeLayerWeight",
    "light_path": "ShaderNodeLightPath",
    "attribute": "ShaderNodeAttribute",
    "volume_principled": "ShaderNodeVolumePrincipled",
    "volume_absorption": "ShaderNodeVolumeAbsorption",
    "volume_scatter": "ShaderNodeVolumeScatter",
    "output_material": "ShaderNodeOutputMaterial",
    "output_world": "ShaderNodeOutputWorld",
    "output_light": "ShaderNodeOutputLight",
}


class ShaderNodesHandler(BaseHandler):
    """Create and connect shader nodes in any material or world node tree."""

    namespace = "shader_nodes"

    @staticmethod
    def cmd_add_shader_node(material_name="", node_type="bsdf_principled", location=(0, 0)):
        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}
        mat.use_nodes = True
        bpy_type = NODE_TYPES.get(node_type.lower())
        if not bpy_type:
            return {"error": f"Unknown node type: {node_type}"}
        node = mat.node_tree.nodes.new(type=bpy_type)
        node.location = location
        return {"name": node.name, "type": node_type, "material": material_name}

    @staticmethod
    def cmd_connect_nodes(material_name="", from_node="", from_socket="", to_node="", to_socket=""):
        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}
        tree = mat.node_tree
        src = tree.nodes.get(from_node)
        dst = tree.nodes.get(to_node)
        if not src or not dst:
            return {"error": "Source or destination node not found"}
        out = src.outputs.get(from_socket) or list(src.outputs)[0]
        inp = dst.inputs.get(to_socket) or list(dst.inputs)[0]
        tree.links.new(out, inp)
        return {"connected": f"{from_node}.{out.name} → {to_node}.{inp.name}"}

    @staticmethod
    def cmd_set_node_value(material_name="", node_name="", input_name="", value=None):
        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.get(node_name)
        if not node:
            return {"error": f"Node not found: {node_name}"}
        inp = node.inputs.get(input_name)
        if not inp:
            return {"error": f"Input not found: {input_name}"}
        if hasattr(inp, "default_value"):
            inp.default_value = value
        return {"set": f"{node_name}.{input_name} = {value}"}

    @staticmethod
    def cmd_list_shader_nodes(material_name=""):
        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}
        nodes = []
        for n in mat.node_tree.nodes:
            nodes.append({
                "name": n.name,
                "type": n.type,
                "location": list(n.location),
                "inputs": [i.name for i in n.inputs if i.enabled],
                "outputs": [o.name for o in n.outputs if o.enabled],
            })
        return {"material": material_name, "nodes": nodes}

    @staticmethod
    def cmd_remove_shader_node(material_name="", node_name=""):
        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.get(node_name)
        if not node:
            return {"error": f"Node not found: {node_name}"}
        mat.node_tree.nodes.remove(node)
        return {"removed": node_name, "from": material_name}
