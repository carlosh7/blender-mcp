"""
blender-mcp-ultra — Material Tools
Tools for material management.
"""

from typing import Any, Dict, List, Optional, Tuple

from ...core.entities import Tool, ToolCategory, ToolPermission

# Tool definitions
TOOLS = [
    Tool(
        name="material.create",
        category=ToolCategory.MATERIALS,
        description="Create a new material",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Material name"},
            "color": {
                "type": "tuple",
                "default": (0.8, 0.8, 0.8, 1.0),
                "description": "Base color (RGBA)",
            },
            "metallic": {"type": "float", "default": 0.0, "description": "Metallic value (0-1)"},
            "roughness": {"type": "float", "default": 0.5, "description": "Roughness value (0-1)"},
        },
        examples=[
            "material.create(name='RedMetal', color=(1, 0, 0, 1), metallic=0.8)",
        ],
    ),
    Tool(
        name="material.delete",
        category=ToolCategory.MATERIALS,
        description="Delete a material",
        permission=ToolPermission.DESTRUCTIVE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Material name"},
        },
        examples=[
            "material.delete(name='RedMetal')",
        ],
    ),
    Tool(
        name="material.assign",
        category=ToolCategory.MATERIALS,
        description="Assign material to object",
        permission=ToolPermission.WRITE,
        parameters={
            "object_name": {"type": "str", "required": True, "description": "Object name"},
            "material_name": {"type": "str", "required": True, "description": "Material name"},
        },
        examples=[
            "material.assign(object_name='Cube', material_name='RedMetal')",
        ],
    ),
    Tool(
        name="material.get_info",
        category=ToolCategory.MATERIALS,
        description="Get information about a material",
        permission=ToolPermission.READ_ONLY,
        parameters={
            "name": {"type": "str", "required": True, "description": "Material name"},
        },
        examples=[
            "material.get_info(name='RedMetal')",
        ],
    ),
    Tool(
        name="material.list",
        category=ToolCategory.MATERIALS,
        description="List all materials in the scene",
        permission=ToolPermission.READ_ONLY,
        parameters={},
        examples=[
            "material.list()",
        ],
    ),
    Tool(
        name="material.update",
        category=ToolCategory.MATERIALS,
        description="Update material properties",
        permission=ToolPermission.WRITE,
        parameters={
            "name": {"type": "str", "required": True, "description": "Material name"},
            "color": {"type": "tuple", "default": None, "description": "New base color (RGBA)"},
            "metallic": {"type": "float", "default": None, "description": "New metallic value"},
            "roughness": {"type": "float", "default": None, "description": "New roughness value"},
        },
        examples=[
            "material.update(name='RedMetal', roughness=0.2)",
        ],
    ),
]


def create(
    name: str,
    color: tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    metallic: float = 0.0,
    roughness: float = 0.5,
) -> dict[str, Any]:
    """Create a new material."""
    try:
        import bpy

        # Check if material exists
        if name in bpy.data.materials:
            return {"error": f"Material already exists: {name}"}

        # Create material
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True

        # Get Principled BSDF node
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Metallic"].default_value = metallic
            bsdf.inputs["Roughness"].default_value = roughness

        return {
            "success": True,
            "name": name,
            "color": [c for c in color],
            "metallic": metallic,
            "roughness": roughness,
        }

    except ImportError:
        return {"error": "Blender not available"}


def delete(name: str) -> dict[str, Any]:
    """Delete a material."""
    try:
        import bpy

        mat = bpy.data.materials.get(name)
        if not mat:
            return {"error": f"Material not found: {name}"}

        bpy.data.materials.remove(mat)

        return {"success": True, "name": name}

    except ImportError:
        return {"error": "Blender not available"}


def assign(object_name: str, material_name: str) -> dict[str, Any]:
    """Assign material to object."""
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}

        mat = bpy.data.materials.get(material_name)
        if not mat:
            return {"error": f"Material not found: {material_name}"}

        # Check if object has data
        if not hasattr(obj, "data") or not hasattr(obj.data, "materials"):
            return {"error": f"Object {object_name} cannot have materials"}

        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        return {
            "success": True,
            "object": object_name,
            "material": material_name,
        }

    except ImportError:
        return {"error": "Blender not available"}


def get_info(name: str) -> dict[str, Any]:
    """Get information about a material."""
    try:
        import bpy

        mat = bpy.data.materials.get(name)
        if not mat:
            return {"error": f"Material not found: {name}"}

        result = {
            "name": mat.name,
            "use_nodes": mat.use_nodes,
            "nodes_count": len(mat.node_tree.nodes) if mat.node_tree else 0,
        }

        # Get Principled BSDF values if available
        if mat.node_tree:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                result["color"] = [c for c in bsdf.inputs["Base Color"].default_value]
                result["metallic"] = bsdf.inputs["Metallic"].default_value
                result["roughness"] = bsdf.inputs["Roughness"].default_value

        return result

    except ImportError:
        return {"error": "Blender not available"}


def list_materials() -> dict[str, Any]:
    """List all materials in the scene."""
    try:
        import bpy

        materials = []
        for mat in bpy.data.materials:
            materials.append(
                {
                    "name": mat.name,
                    "use_nodes": mat.use_nodes,
                    "users": mat.users,
                }
            )

        return {
            "count": len(materials),
            "materials": materials,
        }

    except ImportError:
        return {"error": "Blender not available"}


def update(
    name: str,
    color: tuple[float, float, float, float] = None,
    metallic: float = None,
    roughness: float = None,
) -> dict[str, Any]:
    """Update material properties."""
    try:
        import bpy

        mat = bpy.data.materials.get(name)
        if not mat:
            return {"error": f"Material not found: {name}"}

        if not mat.node_tree:
            return {"error": f"Material {name} does not use nodes"}

        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            return {"error": f"Material {name} does not have Principled BSDF"}

        updated = []

        if color is not None:
            bsdf.inputs["Base Color"].default_value = color
            updated.append("color")

        if metallic is not None:
            bsdf.inputs["Metallic"].default_value = metallic
            updated.append("metallic")

        if roughness is not None:
            bsdf.inputs["Roughness"].default_value = roughness
            updated.append("roughness")

        return {
            "success": True,
            "name": name,
            "updated": updated,
        }

    except ImportError:
        return {"error": "Blender not available"}


# Handler mapping
HANDLERS = {
    "material.create": create,
    "material.delete": delete,
    "material.assign": assign,
    "material.get_info": get_info,
    "material.list": list_materials,
    "material.update": update,
}
