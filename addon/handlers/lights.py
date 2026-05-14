"""
blender-mcp — Lights Handler
"""
import bpy
import math
from . import BaseHandler


LIGHT_TYPES = {
    "point": "POINT",
    "sun": "SUN",
    "spot": "SPOT",
    "area": "AREA",
}


class LightsHandler(BaseHandler):
    """Create and control lights: Point, Sun, Spot, Area, 3-point lighting."""

    namespace = "lights"

    @staticmethod
    def cmd_create_light(name="Light", light_type="point", energy=100.0, color=(1.0, 1.0, 1.0), location=(0.0, 0.0, 5.0)):
        bpy_type = LIGHT_TYPES.get(light_type.lower())
        if not bpy_type:
            return {"error": f"Unknown type: {light_type}. Use: {', '.join(LIGHT_TYPES.keys())}"}
        bpy.ops.object.light_add(type=bpy_type, location=location)
        obj = bpy.context.active_object
        obj.name = name
        obj.data.energy = energy
        obj.data.color = color
        return {"name": obj.name, "type": light_type, "energy": energy}

    @staticmethod
    def cmd_setup_three_point_lighting(target_name=""):
        target = bpy.data.objects.get(target_name)
        target_loc = target.location if target else (0, 0, 0)
        x, y, z = target_loc
        configs = [
            ("Key_Light", "area", 500.0, (1.0, 0.95, 0.9), (x + 3, y - 2, z + 4)),
            ("Fill_Light", "area", 200.0, (0.8, 0.85, 1.0), (x - 3, y + 2, z + 2)),
            ("Rim_Light", "spot", 300.0, (1.0, 1.0, 1.0), (x + 2, y + 3, z + 1)),
        ]
        results = []
        for name, lt, energy, col, loc in configs:
            result = LightsHandler.cmd_create_light(name=name, light_type=lt, energy=energy, color=col, location=loc)
            results.append(result)
        return {"lights": results, "target": target_name or "scene center"}
