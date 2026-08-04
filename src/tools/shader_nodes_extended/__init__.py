"""
blender-mcp-ultra — Shader Nodes Extended
Additional shader node tools for complex materials.
"""
from typing import Any, Dict
from core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    # Texture Nodes
    Tool("shader.brick_texture", ToolCategory.SHADER_NODES, "Create brick texture", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "offset": {"type": "float"}, "scale": {"type": "float"}}),
    Tool("shader.checker_texture", ToolCategory.SHADER_NODES, "Create checker texture", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "scale": {"type": "float"}}),
    Tool("shader.gradient_texture", ToolCategory.SHADER_NODES, "Create gradient texture", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "gradient_type": {"type": "str"}}),
    Tool("shader.magic_texture", ToolCategory.SHADER_NODES, "Create magic texture", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "scale": {"type": "float"}}),
    Tool("shader.musgrave_texture", ToolCategory.SHADER_NODES, "Create musgrave texture", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "scale": {"type": "float"}}),
    Tool("shader.voronoi_texture", ToolCategory.SHADER_NODES, "Create voronoi texture", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "scale": {"type": "float"}}),
    Tool("shader.wave_texture", ToolCategory.SHADER_NODES, "Create wave texture", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "scale": {"type": "float"}}),
    Tool("shader.white_noise_texture", ToolCategory.SHADER_NODES, "Create white noise texture", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    
    # Color Nodes
    Tool("shader.mix_rgb", ToolCategory.SHADER_NODES, "Mix RGB colors", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "factor": {"type": "float"}}),
    Tool("shader.rgb_curves", ToolCategory.SHADER_NODES, "Add RGB curves", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.hue_saturation", ToolCategory.SHADER_NODES, "Add hue saturation", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.invert", ToolCategory.SHADER_NODES, "Add invert node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    
    # Converter Nodes
    Tool("shader.math", ToolCategory.SHADER_NODES, "Add math node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "operation": {"type": "str"}}),
    Tool("shader.vector_math", ToolCategory.SHADER_NODES, "Add vector math node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "operation": {"type": "str"}}),
    Tool("shader.mapping", ToolCategory.SHADER_NODES, "Add mapping node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.combine_xyz", ToolCategory.SHADER_NODES, "Add combine XYZ node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.separate_xyz", ToolCategory.SHADER_NODES, "Add separate XYZ node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    
    # Input Nodes
    Tool("shader.texture_coordinate", ToolCategory.SHADER_NODES, "Add texture coordinate node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.object_info", ToolCategory.SHADER_NODES, "Add object info node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.geometry", ToolCategory.SHADER_NODES, "Add geometry node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.camera_data", ToolCategory.SHADER_NODES, "Add camera data node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.fresnel", ToolCategory.SHADER_NODES, "Add fresnel node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.layer_weight", ToolCategory.SHADER_NODES, "Add layer weight node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.rgb", ToolCategory.SHADER_NODES, "Add RGB node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "color": {"type": "tuple"}}),
    Tool("shader.value", ToolCategory.SHADER_NODES, "Add value node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "value": {"type": "float"}}),
    
    # Vector Nodes
    Tool("shader.displacement", ToolCategory.SHADER_NODES, "Add displacement node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.normal_map", ToolCategory.SHADER_NODES, "Add normal map node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.bump", ToolCategory.SHADER_NODES, "Add bump node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.vector_transform", ToolCategory.SHADER_NODES, "Add vector transform node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    
    # Output Nodes
    Tool("shader.material_output", ToolCategory.SHADER_NODES, "Add material output node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.displacement_output", ToolCategory.SHADER_NODES, "Add displacement output node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    
    # Shader Nodes
    Tool("shader.add_shader", ToolCategory.SHADER_NODES, "Add add shader node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.mix_shader", ToolCategory.SHADER_NODES, "Add mix shader node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "factor": {"type": "float"}}),
    Tool("shader.glass_bsdf", ToolCategory.SHADER_NODES, "Add glass BSDF node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "color": {"type": "tuple"}, "roughness": {"type": "float"}}),
    Tool("shader.emission", ToolCategory.SHADER_NODES, "Add emission node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}, "color": {"type": "tuple"}, "strength": {"type": "float"}}),
    Tool("shader.transparent_bsdf", ToolCategory.SHADER_NODES, "Add transparent BSDF node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.translucent_bsdf", ToolCategory.SHADER_NODES, "Add translucent BSDF node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.refraction_bsdf", ToolCategory.SHADER_NODES, "Add refraction BSDF node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.velvet_bsdf", ToolCategory.SHADER_NODES, "Add velvet BSDF node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.sss_bsdf", ToolCategory.SHADER_NODES, "Add subsurface scattering node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
    Tool("shader.toon_bsdf", ToolCategory.SHADER_NODES, "Add toon BSDF node", ToolPermission.WRITE,
         {"material_name": {"type": "str", "required": True}}),
]


def brick_texture(material_name: str, offset: float = 0.0, scale: float = 5.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexBrick')
        node.offset = offset
        node.offset_frequency = 2
        node.squash = 1.0
        node.squash_frequency = 2
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def checker_texture(material_name: str, scale: float = 5.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexChecker')
        node.inputs['Scale'].default_value = scale
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def gradient_texture(material_name: str, gradient_type: str = "LINEAR") -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexGradient')
        node.gradient_type = gradient_type
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def magic_texture(material_name: str, scale: float = 5.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexMagic')
        node.inputs['Scale'].default_value = scale
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def musgrave_texture(material_name: str, scale: float = 5.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexNoise')
        node.inputs['Scale'].default_value = scale
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def voronoi_texture(material_name: str, scale: float = 5.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexVoronoi')
        node.inputs['Scale'].default_value = scale
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def wave_texture(material_name: str, scale: float = 5.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexWave')
        node.inputs['Scale'].default_value = scale
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def white_noise_texture(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexWhiteNoise')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mix_rgb(material_name: str, factor: float = 0.5) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeMixRGB')
        node.inputs['Fac'].default_value = factor
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def rgb_curves(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeRGBCurve')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def hue_saturation(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeHueSaturation')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def invert(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeInvert')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def math(material_name: str, operation: str = "ADD") -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeMath')
        node.operation = operation
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def vector_math(material_name: str, operation: str = "ADD") -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeVectorMath')
        node.operation = operation
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mapping(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeMapping')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def combine_xyz(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeCombineXYZ')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def separate_xyz(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeSeparateXYZ')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def texture_coordinate(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeTexCoord')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def object_info(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeObjectInfo')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def geometry(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeNewGeometry')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def camera_data(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeCameraData')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def fresnel(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeFresnel')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def layer_weight(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeLayerWeight')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def rgb(material_name: str, color: tuple = (1, 1, 1)) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeRGB')
        node.outputs[0].default_value = color + (1,) if len(color) == 3 else color
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def value(material_name: str, value: float = 0.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeValue')
        node.outputs[0].default_value = value
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def displacement(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeDisplacement')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def normal_map(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeNormalMap')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def bump(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeBump')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def vector_transform(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeVectorTransform')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def material_output(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def displacement_output(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeDisplacement')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def add_shader(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeAddShader')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mix_shader(material_name: str, factor: float = 0.5) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeMixShader')
        node.inputs[0].default_value = factor
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def glass_bsdf(material_name: str, color: tuple = (1, 1, 1), roughness: float = 0.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeBsdfGlass')
        node.inputs['Color'].default_value = color + (1,) if len(color) == 3 else color
        node.inputs['Roughness'].default_value = roughness
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def emission(material_name: str, color: tuple = (1, 1, 1), strength: float = 1.0) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeEmission')
        node.inputs['Color'].default_value = color + (1,) if len(color) == 3 else color
        node.inputs['Strength'].default_value = strength
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def transparent_bsdf(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def translucent_bsdf(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeBsdfTranslucent')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def refraction_bsdf(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeBsdfRefraction')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def velvet_bsdf(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeBsdfSheen')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def sss_bsdf(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeSubsurfaceScattering')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def toon_bsdf(material_name: str) -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        node = mat.node_tree.nodes.new('ShaderNodeBsdfToon')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

HANDLERS = {
    "shader.brick_texture": brick_texture, "shader.checker_texture": checker_texture,
    "shader.gradient_texture": gradient_texture, "shader.magic_texture": magic_texture,
    "shader.musgrave_texture": musgrave_texture, "shader.voronoi_texture": voronoi_texture,
    "shader.wave_texture": wave_texture, "shader.white_noise_texture": white_noise_texture,
    "shader.mix_rgb": mix_rgb, "shader.rgb_curves": rgb_curves,
    "shader.hue_saturation": hue_saturation, "shader.invert": invert,
    "shader.math": math, "shader.vector_math": vector_math,
    "shader.mapping": mapping, "shader.combine_xyz": combine_xyz,
    "shader.separate_xyz": separate_xyz, "shader.texture_coordinate": texture_coordinate,
    "shader.object_info": object_info, "shader.geometry": geometry,
    "shader.camera_data": camera_data, "shader.fresnel": fresnel,
    "shader.layer_weight": layer_weight, "shader.rgb": rgb, "shader.value": value,
    "shader.displacement": displacement, "shader.normal_map": normal_map,
    "shader.bump": bump, "shader.vector_transform": vector_transform,
    "shader.material_output": material_output, "shader.displacement_output": displacement_output,
    "shader.add_shader": add_shader, "shader.mix_shader": mix_shader,
    "shader.glass_bsdf": glass_bsdf, "shader.emission": emission,
    "shader.transparent_bsdf": transparent_bsdf, "shader.translucent_bsdf": translucent_bsdf,
    "shader.refraction_bsdf": refraction_bsdf, "shader.velvet_bsdf": velvet_bsdf,
    "shader.sss_bsdf": sss_bsdf, "shader.toon_bsdf": toon_bsdf,
}
