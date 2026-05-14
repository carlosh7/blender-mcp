"""
blender-mcp — Animation MCP tools
"""
import json
from blender_connection import get_blender


def register_tools(mcp):
    @mcp.tool()
    def insert_keyframe(object_name: str, frame: int = 1, property: str = "location", value: list = None) -> str:
        """Insert a keyframe on an object property at a specific frame."""
        b = get_blender()
        r = b.send_command("insert_keyframe", {"object_name": object_name, "frame": frame, "property": property, "value": value})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def animate_location(object_name: str, start_frame: int = 1, end_frame: int = 60, start_loc: list = None, end_loc: list = None) -> str:
        """Animate an object moving from one location to another."""
        start_loc = start_loc or [0, 0, 0]
        end_loc = end_loc or [5, 0, 0]
        b = get_blender()
        r = b.send_command("animate_location", {"object_name": object_name, "start_frame": start_frame, "end_frame": end_frame, "start_loc": start_loc, "end_loc": end_loc})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def animate_rotation(object_name: str, start_frame: int = 1, end_frame: int = 60, revolutions: float = 1.0) -> str:
        """Animate an object rotating around Z axis."""
        import math
        end_rot = [0, 0, math.radians(360 * revolutions)]
        b = get_blender()
        r = b.send_command("animate_rotation", {"object_name": object_name, "start_frame": start_frame, "end_frame": end_frame, "start_rot": [0, 0, 0], "end_rot": end_rot})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def animate_scale(object_name: str, start_frame: int = 1, end_frame: int = 60, start_scale: list = None, end_scale: list = None) -> str:
        """Animate an object scaling over time."""
        start_scale = start_scale or [1, 1, 1]
        end_scale = end_scale or [2, 2, 2]
        b = get_blender()
        r = b.send_command("animate_scale", {"object_name": object_name, "start_frame": start_frame, "end_frame": end_frame, "start_scale": start_scale, "end_scale": end_scale})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def set_render_range(start_frame: int = 1, end_frame: int = 250) -> str:
        """Set the render frame range."""
        b = get_blender()
        r = b.send_command("set_render_range", {"start": start_frame, "end": end_frame})
        return json.dumps(r, indent=2)
