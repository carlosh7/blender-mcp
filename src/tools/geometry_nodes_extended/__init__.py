"""
blender-mcp-ultra — Geometry Nodes Extended
Additional geometry node tools for procedural modeling.
"""
from typing import Any, Dict
from core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    # Input Nodes
    Tool("geonodes.mesh_cube", ToolCategory.GEOMETRY_NODES, "Add mesh cube node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "size": {"type": "float"}}),
    Tool("geonodes.mesh_circle", ToolCategory.GEOMETRY_NODES, "Add mesh circle node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "radius": {"type": "float"}}),
    Tool("geonodes.mesh_line", ToolCategory.GEOMETRY_NODES, "Add mesh line node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "count": {"type": "int"}}),
    Tool("geonodes.mesh_grid", ToolCategory.GEOMETRY_NODES, "Add mesh grid node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "size_x": {"type": "float"}, "size_y": {"type": "float"}}),
    Tool("geonodes.mesh_ico_sphere", ToolCategory.GEOMETRY_NODES, "Add mesh ico sphere node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "radius": {"type": "float"}}),
    Tool("geonodes.mesh_uv_sphere", ToolCategory.GEOMETRY_NODES, "Add mesh UV sphere node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "radius": {"type": "float"}}),
    Tool("geonodes.mesh_cone", ToolCategory.GEOMETRY_NODES, "Add mesh cone node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "radius": {"type": "float"}}),
    Tool("geonodes.mesh_cylinder", ToolCategory.GEOMETRY_NODES, "Add mesh cylinder node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "radius": {"type": "float"}}),
    Tool("geonodes.mesh_torus", ToolCategory.GEOMETRY_NODES, "Add mesh torus node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "radius": {"type": "float"}}),
    Tool("geonodes.curve_line", ToolCategory.GEOMETRY_NODES, "Add curve line node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.curve_circle", ToolCategory.GEOMETRY_NODES, "Add curve circle node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "radius": {"type": "float"}}),
    Tool("geonodes.curve_quadratic_bezier", ToolCategory.GEOMETRY_NODES, "Add curve quadratic bezier node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.curve_cubic_bezier", ToolCategory.GEOMETRY_NODES, "Add curve cubic bezier node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.curve_spiral", ToolCategory.GEOMETRY_NODES, "Add curve spiral node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.curve_star", ToolCategory.GEOMETRY_NODES, "Add curve star node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.curve_quadrilateral", ToolCategory.GEOMETRY_NODES, "Add curve quadrilateral node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    
    # Geometry Operations
    Tool("geonodes.transform_geometry", ToolCategory.GEOMETRY_NODES, "Add transform geometry node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.set_position", ToolCategory.GEOMETRY_NODES, "Add set position node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.node_delete_geometry", ToolCategory.GEOMETRY_NODES, "Add delete geometry node to a node group", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.duplicate_elements", ToolCategory.GEOMETRY_NODES, "Add duplicate elements node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.realize_instances", ToolCategory.GEOMETRY_NODES, "Add realize instances node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.merge_by_distance", ToolCategory.GEOMETRY_NODES, "Add merge by distance node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "distance": {"type": "float"}}),
    Tool("geonodes.subdivide_mesh", ToolCategory.GEOMETRY_NODES, "Add subdivide mesh node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "level": {"type": "int"}}),
    Tool("geonodes.triangulate_mesh", ToolCategory.GEOMETRY_NODES, "Add triangulate mesh node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.dual_mesh", ToolCategory.GEOMETRY_NODES, "Add dual mesh node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.scale_elements", ToolCategory.GEOMETRY_NODES, "Add scale elements node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.raycast", ToolCategory.GEOMETRY_NODES, "Add raycast node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.convex_hull", ToolCategory.GEOMETRY_NODES, "Add convex hull node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.bounding_box", ToolCategory.GEOMETRY_NODES, "Add bounding box node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.bmesh_to_mesh", ToolCategory.GEOMETRY_NODES, "Add BMesh to mesh node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.mesh_to_bmesh", ToolCategory.GEOMETRY_NODES, "Add mesh to BMesh node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    
    # Curve Operations
    Tool("geonodes.curve_to_mesh", ToolCategory.GEOMETRY_NODES, "Add curve to mesh node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.mesh_to_curve", ToolCategory.GEOMETRY_NODES, "Add mesh to curve node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.curve_to_points", ToolCategory.GEOMETRY_NODES, "Add curve to points node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.resample_curve", ToolCategory.GEOMETRY_NODES, "Add resample curve node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "count": {"type": "int"}}),
    Tool("geonodes.fill_curve", ToolCategory.GEOMETRY_NODES, "Add fill curve node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.fillet_curve", ToolCategory.GEOMETRY_NODES, "Add fillet curve node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "count": {"type": "int"}}),
    Tool("geonodes.reverse_curve", ToolCategory.GEOMETRY_NODES, "Add reverse curve node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.set_curve_radius", ToolCategory.GEOMETRY_NODES, "Add set curve radius node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.set_curve_tilt", ToolCategory.GEOMETRY_NODES, "Add set curve tilt node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.spline_to_bezier", ToolCategory.GEOMETRY_NODES, "Add spline to bezier node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.string_to_curve", ToolCategory.GEOMETRY_NODES, "Add string to curve node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    
    # Instance Operations
    Tool("geonodes.instance_on_points", ToolCategory.GEOMETRY_NODES, "Add instance on points node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.on_points", ToolCategory.GEOMETRY_NODES, "Add on points node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.rotate_instances", ToolCategory.GEOMETRY_NODES, "Add rotate instances node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.scale_instances", ToolCategory.GEOMETRY_NODES, "Add scale instances node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.translate_instances", ToolCategory.GEOMETRY_NODES, "Add translate instances node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.pick_instances", ToolCategory.GEOMETRY_NODES, "Add pick instances node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    
    # Attribute Operations
    Tool("geonodes.capture_attribute", ToolCategory.GEOMETRY_NODES, "Add capture attribute node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.store_named_attribute", ToolCategory.GEOMETRY_NODES, "Add store named attribute node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "name": {"type": "str"}}),
    Tool("geonodes.remove_named_attribute", ToolCategory.GEOMETRY_NODES, "Add remove named attribute node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "name": {"type": "str"}}),
    Tool("geonodes.blur_attribute", ToolCategory.GEOMETRY_NODES, "Add blur attribute node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.attribute_statistic", ToolCategory.GEOMETRY_NODES, "Add attribute statistic node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.domain_size", ToolCategory.GEOMETRY_NODES, "Add domain size node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.transfer_attribute", ToolCategory.GEOMETRY_NODES, "Add transfer attribute node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    
    # Simulation
    Tool("geonodes.simulation_zone", ToolCategory.GEOMETRY_NODES, "Add simulation zone", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.simulation_input", ToolCategory.GEOMETRY_NODES, "Add simulation input node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.simulation_output", ToolCategory.GEOMETRY_NODES, "Add simulation output node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    
    # Math/Utilities
    Tool("geonodes.math", ToolCategory.GEOMETRY_NODES, "Add math node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "operation": {"type": "str"}}),
    Tool("geonodes.compare", ToolCategory.GEOMETRY_NODES, "Add compare node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "operation": {"type": "str"}}),
    Tool("geonodes.boolean", ToolCategory.GEOMETRY_NODES, "Add boolean node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}, "operation": {"type": "str"}}),
    Tool("geonodes.random_value", ToolCategory.GEOMETRY_NODES, "Add random value node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.accumulate_field", ToolCategory.GEOMETRY_NODES, "Add accumulate field node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.index", ToolCategory.GEOMETRY_NODES, "Add index node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.position", ToolCategory.GEOMETRY_NODES, "Add position node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.normal", ToolCategory.GEOMETRY_NODES, "Add normal node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.face_area", ToolCategory.GEOMETRY_NODES, "Add face area node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
    Tool("geonodes.edge_neighbors", ToolCategory.GEOMETRY_NODES, "Add edge neighbors node", ToolPermission.WRITE,
         {"group_name": {"type": "str", "required": True}}),
]


def mesh_cube(group_name: str, size: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshCube')
        node.inputs['Size'].default_value = (size, size, size)
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_circle(group_name: str, radius: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshCircle')
        node.inputs['Radius'].default_value = radius
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_line(group_name: str, count: int = 10) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshLine')
        node.inputs['Count'].default_value = count
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_grid(group_name: str, size_x: float = 1.0, size_y: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshGrid')
        node.inputs['Size X'].default_value = size_x
        node.inputs['Size Y'].default_value = size_y
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_ico_sphere(group_name: str, radius: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshIcoSphere')
        node.inputs['Radius'].default_value = radius
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_uv_sphere(group_name: str, radius: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshUVSphere')
        node.inputs['Radius'].default_value = radius
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_cone(group_name: str, radius: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshCone')
        node.inputs['Radius'].default_value = radius
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_cylinder(group_name: str, radius: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshCylinder')
        node.inputs['Radius'].default_value = radius
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_torus(group_name: str, radius: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshTorus')
        node.inputs['Radius'].default_value = radius
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_line(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeCurveLine')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_circle(group_name: str, radius: float = 1.0) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeCurveCircle')
        node.inputs['Radius'].default_value = radius
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_quadratic_bezier(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeCurveQuadraticBezier')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_cubic_bezier(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeCurveCubicBezier')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_spiral(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeSpiral')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_star(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeStar')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_quadrilateral(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeCurveQuadrilateral')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def transform_geometry(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeTransformGeometry')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def set_position(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeSetPosition')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def delete_geometry(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeDeleteGeometry')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def duplicate_elements(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeDuplicateElements')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def realize_instances(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeRealizeInstances')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def merge_by_distance(group_name: str, distance: float = 0.001) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMergeByDistance')
        node.inputs['Distance'].default_value = distance
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def subdivide_mesh(group_name: str, level: int = 1) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeSubdivideMesh')
        node.inputs['Level'].default_value = level
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def triangulate_mesh(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeTriangulate')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def dual_mesh(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeDualMesh')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def scale_elements(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeScaleElements')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def raycast(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeRaycast')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def convex_hull(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeConvexHull')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def bounding_box(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeBoundingBox')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def bmesh_to_mesh(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeBMeshToMesh')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_to_bmesh(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshToBMesh')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_to_mesh(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeCurveToMesh')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def mesh_to_curve(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeMeshToCurve')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def curve_to_points(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeCurveToPoints')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def resample_curve(group_name: str, count: int = 10) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeResampleCurve')
        node.inputs['Count'].default_value = count
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def fill_curve(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeFillCurve')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def fillet_curve(group_name: str, count: int = 3) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeFilletCurve')
        node.inputs['Count'].default_value = count
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def reverse_curve(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeReverseCurve')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def set_curve_radius(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeSetCurveRadius')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def set_curve_tilt(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeSetCurveTilt')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def spline_to_bezier(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeSplineToBezier')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def string_to_curve(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeStringToCurve')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def instance_on_points(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeInstanceOnPoints')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def on_points(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeOnPoints')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def rotate_instances(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeRotateInstances')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def scale_instances(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeScaleInstances')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def translate_instances(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeTranslateInstances')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def pick_instances(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodePickInstances')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def capture_attribute(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeCaptureAttribute')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def store_named_attribute(group_name: str, name: str = "attribute") -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeStoreNamedAttribute')
        node.inputs['Name'].default_value = name
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def remove_named_attribute(group_name: str, name: str = "attribute") -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeRemoveNamedAttribute')
        node.inputs['Name'].default_value = name
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def blur_attribute(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeBlurAttribute')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def attribute_statistic(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeAttributeStatistic')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def domain_size(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeDomainSize')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def transfer_attribute(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeTransferAttribute')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def simulation_zone(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeSimulationZone')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def simulation_input(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('SimulationInput')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def simulation_output(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('SimulationOutput')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def math_node(group_name: str, operation: str = "ADD") -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('FunctionNodeMath')
        node.operation = operation
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def compare(group_name: str, operation: str = "EQUAL") -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('FunctionNodeCompare')
        node.data_type = 'FLOAT'
        node.operation = operation
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def boolean(group_name: str, operation: str = "AND") -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('FunctionNodeBooleanMath')
        node.operation = operation
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def random_value(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('FunctionNodeRandomValue')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def accumulate_field(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('FunctionNodeAccumulateField')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def index(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeInputIndex')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def position(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeInputPosition')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def normal(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeInputNormal')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def face_area(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeInputFaceArea')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

def edge_neighbors(group_name: str) -> Dict:
    try:
        import bpy
        ng = bpy.data.node_groups.get(group_name)
        if not ng: return {"error": f"Node group not found: {group_name}"}
        node = ng.nodes.new('GeometryNodeInputEdgeNeighbors')
        return {"success": True, "node": node.name}
    except Exception as e: return {"error": str(e)}

HANDLERS = {
    "geonodes.mesh_cube": mesh_cube, "geonodes.mesh_circle": mesh_circle,
    "geonodes.mesh_line": mesh_line, "geonodes.mesh_grid": mesh_grid,
    "geonodes.mesh_ico_sphere": mesh_ico_sphere, "geonodes.mesh_uv_sphere": mesh_uv_sphere,
    "geonodes.mesh_cone": mesh_cone, "geonodes.mesh_cylinder": mesh_cylinder,
    "geonodes.mesh_torus": mesh_torus, "geonodes.curve_line": curve_line,
    "geonodes.curve_circle": curve_circle, "geonodes.curve_quadratic_bezier": curve_quadratic_bezier,
    "geonodes.curve_cubic_bezier": curve_cubic_bezier, "geonodes.curve_spiral": curve_spiral,
    "geonodes.curve_star": curve_star, "geonodes.curve_quadrilateral": curve_quadrilateral,
    "geonodes.transform_geometry": transform_geometry, "geonodes.set_position": set_position,
    "geonodes.node_delete_geometry": delete_geometry, "geonodes.duplicate_elements": duplicate_elements,
    "geonodes.realize_instances": realize_instances, "geonodes.merge_by_distance": merge_by_distance,
    "geonodes.subdivide_mesh": subdivide_mesh, "geonodes.triangulate_mesh": triangulate_mesh,
    "geonodes.dual_mesh": dual_mesh, "geonodes.scale_elements": scale_elements,
    "geonodes.raycast": raycast, "geonodes.convex_hull": convex_hull,
    "geonodes.bounding_box": bounding_box, "geonodes.bmesh_to_mesh": bmesh_to_mesh,
    "geonodes.mesh_to_bmesh": mesh_to_bmesh, "geonodes.curve_to_mesh": curve_to_mesh,
    "geonodes.mesh_to_curve": mesh_to_curve, "geonodes.curve_to_points": curve_to_points,
    "geonodes.resample_curve": resample_curve, "geonodes.fill_curve": fill_curve,
    "geonodes.fillet_curve": fillet_curve, "geonodes.reverse_curve": reverse_curve,
    "geonodes.set_curve_radius": set_curve_radius, "geonodes.set_curve_tilt": set_curve_tilt,
    "geonodes.spline_to_bezier": spline_to_bezier, "geonodes.string_to_curve": string_to_curve,
    "geonodes.instance_on_points": instance_on_points, "geonodes.on_points": on_points,
    "geonodes.rotate_instances": rotate_instances, "geonodes.scale_instances": scale_instances,
    "geonodes.translate_instances": translate_instances, "geonodes.pick_instances": pick_instances,
    "geonodes.capture_attribute": capture_attribute, "geonodes.store_named_attribute": store_named_attribute,
    "geonodes.remove_named_attribute": remove_named_attribute, "geonodes.blur_attribute": blur_attribute,
    "geonodes.attribute_statistic": attribute_statistic, "geonodes.domain_size": domain_size,
    "geonodes.transfer_attribute": transfer_attribute, "geonodes.simulation_zone": simulation_zone,
    "geonodes.simulation_input": simulation_input, "geonodes.simulation_output": simulation_output,
    "geonodes.math": math_node, "geonodes.compare": compare, "geonodes.boolean": boolean,
    "geonodes.random_value": random_value, "geonodes.accumulate_field": accumulate_field,
    "geonodes.index": index, "geonodes.position": position, "geonodes.normal": normal,
    "geonodes.face_area": face_area, "geonodes.edge_neighbors": edge_neighbors,
}
