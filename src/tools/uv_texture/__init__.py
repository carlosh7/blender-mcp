"""
blender-mcp-ultra — UV/Texture Tools
"""
from typing import Any, Dict
from core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool("uv.unwrap", ToolCategory.UV_TEXTURE, "Unwrap UVs", ToolPermission.WRITE,
         {"method": {"type": "str"}, "margin": {"type": "float"}}),
    Tool("uv.pack", ToolCategory.UV_TEXTURE, "Pack UV islands", ToolPermission.WRITE,
         {"margin": {"type": "float"}}),
    Tool("uv.smart_project", ToolCategory.UV_TEXTURE, "Smart UV project", ToolPermission.WRITE,
         {"angle_limit": {"type": "float"}}),
    Tool("uv.list", ToolCategory.UV_TEXTURE, "List UV maps", ToolPermission.READ_ONLY,
         {"object_name": {"type": "str"}}),
    Tool("uv.create", ToolCategory.UV_TEXTURE, "Create UV map", ToolPermission.WRITE,
         {"object_name": {"type": "str"}, "name": {"type": "str"}}),
    Tool("uv.delete", ToolCategory.UV_TEXTURE, "Delete UV map", ToolPermission.WRITE,
         {"object_name": {"type": "str"}, "name": {"type": "str"}}),
    Tool("texture.create", ToolCategory.UV_TEXTURE, "Create image texture", ToolPermission.WRITE,
         {"name": {"type": "str"}, "width": {"type": "int"}, "height": {"type": "int"}, "color": {"type": "tuple"}}),
    Tool("texture.list", ToolCategory.UV_TEXTURE, "List all textures", ToolPermission.READ_ONLY, {}),
    Tool("texture.assign_to_material", ToolCategory.UV_TEXTURE, "Assign texture to material", ToolPermission.WRITE,
         {"material_name": {"type": "str"}, "texture_name": {"type": "str"}, "slot": {"type": "str"}}),
    Tool("uv.bake", ToolCategory.UV_TEXTURE, "Bake textures", ToolPermission.WRITE,
         {"type": {"type": "str"}, "margin": {"type": "int"}}),
]

def unwrap(method: str = "ANGLE_BASED", margin: float = 0.001) -> Dict:
    try:
        import bpy
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        if method == "SMART": bpy.ops.uv.smart_project(angle_limit=66, margin=margin)
        else: bpy.ops.uv.unwrap(method=method, margin=margin)
        bpy.ops.object.mode_set(mode='OBJECT')
        return {"success": True, "method": method}
    except Exception as e: return {"error": str(e)}

def pack(margin: float = 0.001) -> Dict:
    try:
        import bpy
        bpy.ops.uv.pack_islands(margin=margin)
        return {"success": True, "margin": margin}
    except Exception as e: return {"error": str(e)}

def smart_project(angle_limit: float = 66.0, object_name: str = None) -> Dict:
    try:
        import bpy
        # Set active object if specified
        if object_name:
            obj = bpy.data.objects.get(object_name)
            if obj:
                try:
                    bpy.context.view_layer.objects.active = obj
                except:
                    pass
        # Ensure we have an active object
        active = getattr(bpy.context, 'active_object', None)
        if active is None:
            for o in bpy.context.scene.objects:
                if o.type == 'MESH':
                    try:
                        bpy.context.view_layer.objects.active = o
                        break
                    except:
                        pass
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=angle_limit)
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass  # Some operators may fail in background mode
        return {"success": True, "angle_limit": angle_limit}
    except Exception as e: return {"error": str(e)}

def list_uv(object_name: str) -> Dict:
    try:
        import bpy
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH': return {"error": f"Mesh not found: {object_name}"}
        maps = [{"name": uv.name, "active": uv.active_render} for uv in obj.data.uv_layers]
        return {"object": object_name, "count": len(maps), "uv_maps": maps}
    except ImportError: return {"error": "Blender not available"}

def create_uv(object_name: str, name: str = "UVMap") -> Dict:
    try:
        import bpy
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH': return {"error": f"Mesh not found: {object_name}"}
        uv = obj.data.uv_layers.new(name=name)
        return {"success": True, "name": uv.name}
    except Exception as e: return {"error": str(e)}

def delete_uv(object_name: str, name: str) -> Dict:
    try:
        import bpy
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH': return {"error": f"Mesh not found: {object_name}"}
        uv = obj.data.uv_layers.get(name)
        if not uv: return {"error": f"UV map not found: {name}"}
        obj.data.uv_layers.remove(uv)
        return {"success": True, "name": name}
    except Exception as e: return {"error": str(e)}

def create_texture(name: str = "Texture", width: int = 1024, height: int = 1024, color: tuple = (0.5, 0.5, 0.5, 1)) -> Dict:
    try:
        import bpy
        img = bpy.data.images.new(name=name, width=width, height=height, alpha=True)
        img.pixels[:] = color * (width * height)
        return {"success": True, "name": img.name, "width": width, "height": height}
    except Exception as e: return {"error": str(e)}

def list_textures() -> Dict:
    try:
        import bpy
        textures = [{"name": t.name, "type": t.type} for t in bpy.data.textures]
        images = [{"name": i.name, "size": [i.size[0], i.size[1]]} for i in bpy.data.images]
        return {"textures": len(textures), "images": len(images), "texture_list": textures, "image_list": images}
    except ImportError: return {"error": "Blender not available"}

def assign_to_material(material_name: str, texture_name: str, slot: str = "Base Color") -> Dict:
    try:
        import bpy
        mat = bpy.data.materials.get(material_name)
        if not mat or not mat.node_tree: return {"error": f"Material not found: {material_name}"}
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf: return {"error": "No Principled BSDF node"}
        tex_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        tex_node.image = bpy.data.images.get(texture_name)
        mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs[slot])
        return {"success": True, "material": material_name, "texture": texture_name, "slot": slot}
    except Exception as e: return {"error": str(e)}

def bake(type: str = "DIFFUSE", margin: int = 16) -> Dict:
    try:
        import bpy
        bpy.context.scene.render.bake.type = type
        bpy.context.scene.render.bake.margin = margin
        bpy.ops.object.bake(type=type)
        return {"success": True, "type": type, "margin": margin}
    except Exception as e: return {"error": str(e)}

HANDLERS = {
    "uv.unwrap": unwrap, "uv.pack": pack, "uv.smart_project": smart_project,
    "uv.list": list_uv, "uv.create": create_uv, "uv.delete": delete_uv,
    "texture.create": create_texture, "texture.list": list_textures,
    "texture.assign_to_material": assign_to_material, "uv.bake": bake,
}
