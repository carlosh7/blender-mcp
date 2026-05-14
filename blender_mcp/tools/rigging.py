"""
blender-mcp — Rigging MCP tools
"""
import json
from ...blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def create_armature(name: str = "Armature", location_x: float = 0, location_y: float = 0, location_z: float = 0) -> str:
        """Create a new armature with a bone."""
        b = get_blender()
        r = b.send_command("create_armature", {"name": name, "location": (location_x, location_y, location_z)})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def add_bone(armature_name: str, bone_name: str = "Bone", head: list = None, tail: list = None, parent_name: str = "") -> str:
        """Add a bone to an armature. Head and tail are [x, y, z] positions."""
        head = head or [0, 0, 0]
        tail = tail or [0, 0, 1]
        b = get_blender()
        r = b.send_command("add_bone", {"armature_name": armature_name, "bone_name": bone_name, "head": head, "tail": tail, "parent_name": parent_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def add_constraint(object_name: str, constraint_type: str = "COPY_LOCATION", target_name: str = "") -> str:
        """Add a constraint to an object. Types: COPY_LOCATION, COPY_ROTATION, COPY_SCALE, TRACK_TO, DAMPED_TRACK, etc."""
        b = get_blender()
        r = b.send_command("add_constraint", {"object_name": object_name, "constraint_type": constraint_type, "target_name": target_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def parent_with_armature(object_name: str, armature_name: str) -> str:
        """Parent a mesh object to an armature with an Armature modifier."""
        b = get_blender()
        r = b.send_command("parent_with_armature", {"object_name": object_name, "armature_name": armature_name})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def auto_rig_weight(object_name: str, armature_name: str) -> str:
        """Auto-rig weight paint: parent mesh to armature with automatic weights."""
        b = get_blender()
        r = b.send_command("auto_rig_weight", {"object_name": object_name, "armature_name": armature_name})
        return json.dumps(r, indent=2)
