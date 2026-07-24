"""
blender-mcp-ultra — Blender Background Mode Helpers
Provides workarounds for operations that fail in background mode.
"""
try:
    import bpy
    HAS_BPY = True
except ImportError:
    bpy = None
    HAS_BPY = False

from typing import Any, Dict, Optional, List


def ensure_active_object(obj_name: str = None) -> Optional[Any]:
    """
    Ensure there's an active object for operations that require it.
    
    Args:
        obj_name: Optional object name to set as active
        
    Returns:
        Active object or None
    """
    if not HAS_BPY:
        return None
    
    # Try to get active object
    try:
        active = bpy.context.active_object
        if active is not None:
            return active
    except AttributeError:
        pass
    
    # Try to get from view_layer
    try:
        active = bpy.context.view_layer.objects.active
        if active is not None:
            return active
    except:
        pass
    
    # Try to find object by name
    if obj_name:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            try:
                bpy.context.view_layer.objects.active = obj
                return obj
            except:
                pass
    
    # Find first mesh object
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            try:
                bpy.context.view_layer.objects.active = obj
                return obj
            except:
                pass
    
    return None


def execute_with_active_object(func, *args, **kwargs):
    """
    Execute a function that requires active_object, with fallback.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Function result or error dict
    """
    try:
        return func(*args, **kwargs)
    except AttributeError as e:
        if 'active_object' in str(e) or 'mode_set' in str(e):
            # Try to set active object and retry
            obj = ensure_active_object()
            if obj:
                try:
                    return func(*args, **kwargs)
                except:
                    pass
        return {"error": str(e)}


def safe_mode_set(mode: str) -> bool:
    """
    Safely set object mode, handling background mode issues.
    
    Args:
        mode: Target mode ('EDIT', 'OBJECT', 'SCULPT', etc.)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        bpy.ops.object.mode_set(mode=mode)
        return True
    except AttributeError:
        # Try to work around by setting active object first
        obj = ensure_active_object()
        if obj:
            try:
                bpy.ops.object.mode_set(mode=mode)
                return True
            except:
                pass
    except Exception:
        pass
    return False


def safe_uv_operation(func, *args, **kwargs):
    """
    Safely execute UV operations that require edit mode.
    
    Args:
        func: UV operation function
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Function result or error dict
    """
    obj = ensure_active_object()
    if not obj:
        return {"error": "No active object for UV operation"}
    
    # Try to enter edit mode
    was_in_edit = False
    try:
        if obj.mode == 'OBJECT':
            safe_mode_set('EDIT')
        else:
            was_in_edit = True
    except:
        pass
    
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        if not was_in_edit:
            safe_mode_set('OBJECT')


def safe_mesh_operation(func, *args, **kwargs):
    """
    Safely execute mesh operations that require edit mode.
    
    Args:
        func: Mesh operation function
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Function result or error dict
    """
    obj = ensure_active_object()
    if not obj:
        return {"error": "No active object for mesh operation"}
    
    # Try to enter edit mode
    was_in_edit = False
    try:
        if obj.mode == 'OBJECT':
            safe_mode_set('EDIT')
        else:
            was_in_edit = True
    except:
        pass
    
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        if not was_in_edit:
            safe_mode_set('OBJECT')


def create_mesh_with_bmesh(vertices: List[tuple], faces: List[tuple], name: str = "Mesh") -> Optional[Any]:
    """
    Create a mesh using bmesh (works in background mode).
    
    Args:
        vertices: List of vertex coordinates
        faces: List of face indices
        name: Mesh name
        
    Returns:
        Created mesh object
    """
    import bmesh
    
    # Create mesh
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    # Add vertices
    for v in vertices:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()
    
    # Add faces
    for f in faces:
        bm.faces.new([bm.verts[i] for i in f])
    
    # Update mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Create object
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def remove_doubles_with_bmesh(obj_name: str, distance: float = 0.001) -> Dict[str, Any]:
    """
    Remove doubles using bmesh (works in background mode).
    
    Args:
        obj_name: Object name
        distance: Merge distance
        
    Returns:
        Result dict
    """
    import bmesh
    
    obj = bpy.data.objects.get(obj_name)
    if not obj or obj.type != 'MESH':
        return {"error": f"Mesh not found: {obj_name}"}
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    result = bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
    
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    
    return {"success": True, "removed": result.get('geom', [])}


def fix_normals_with_bmesh(obj_name: str) -> Dict[str, Any]:
    """
    Fix normals using bmesh (works in background mode).
    
    Args:
        obj_name: Object name
        
    Returns:
        Result dict
    """
    import bmesh
    
    obj = bpy.data.objects.get(obj_name)
    if not obj or obj.type != 'MESH':
        return {"error": f"Mesh not found: {obj_name}"}
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    
    return {"success": True}


def triangulate_with_bmesh(obj_name: str) -> Dict[str, Any]:
    """
    Triangulate mesh using bmesh (works in background mode).
    
    Args:
        obj_name: Object name
        
    Returns:
        Result dict
    """
    import bmesh
    
    obj = bpy.data.objects.get(obj_name)
    if not obj or obj.type != 'MESH':
        return {"error": f"Mesh not found: {obj_name}"}
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    bmesh.ops.triangulate(bm, faces=bm.faces)
    
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    
    return {"success": True}


def subdivide_with_bmesh(obj_name: str, cuts: int = 1) -> Dict[str, Any]:
    """
    Subdivide mesh using bmesh (works in background mode).
    
    Args:
        obj_name: Object name
        cuts: Number of cuts
        
    Returns:
        Result dict
    """
    import bmesh
    
    obj = bpy.data.objects.get(obj_name)
    if not obj or obj.type != 'MESH':
        return {"error": f"Mesh not found: {obj_name}"}
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=cuts)
    
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    
    return {"success": True, "cuts": cuts}
