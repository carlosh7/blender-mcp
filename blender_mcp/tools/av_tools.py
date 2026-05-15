"""
blender-mcp — Audiovisual Event Tools (High Fidelity)
Advanced procedural generation for event engineering.
"""
import json
import math
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)

def register_tools(mcp):
    @mcp.tool(**RW())
    def av_build_led_wall_hifi(width_m: float, height_m: float, name: str = "LED_Wall_HiFi") -> str:
        """Builds a high-fidelity LED wall with modular cabinets (front/back details).
        Genera una pantalla LED modular con cabinets realistas de 50x50cm."""
        cols = math.ceil(width_m / 0.5)
        rows = math.ceil(height_m / 0.5)
        
        code = f"""
import bpy

def create_hifi_panel(location, name, collection):
    # Frontal (Píxeles)
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    p = bpy.context.active_object
    p.name = name
    p.scale = (0.5, 0.02, 0.5)
    collection.objects.link(p)
    bpy.context.scene.collection.objects.unlink(p)
    
    # Trasera (Estructura)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1]+0.04, location[2]))
    back = bpy.context.active_object
    back.name = name + "_Back"
    back.scale = (0.45, 0.05, 0.45)
    back.parent = p
    collection.objects.link(back)
    bpy.context.scene.collection.objects.unlink(back)

def build_wall(cols, rows, base_name):
    col = bpy.data.collections.new(base_name)
    bpy.context.scene.collection.children.link(col)
    for r in range(rows):
        for c in range(cols):
            x = (c * 0.5) - ((cols * 0.5) / 2) + 0.25
            z = (r * 0.5) + 0.25
            create_hifi_panel((x, 0, z), f"{{base_name}}_P{{c}}_{{r}}", col)
    return cols * rows

result = {{"total_panels": build_wall({cols}, {rows}, "{name}")}}
"""
        b = get_blender()
        return json.dumps(b.send_command("execute_code", {"code": code}), indent=2)

    @mcp.tool(**RW())
    def av_setup_truss_rig_hifi(length_m: float, height_m: float = 6.0, name: str = "Truss_F34_HiFi") -> str:
        """Creates a high-fidelity F34 aluminum truss structure with chords and diagonal webbing.
        Genera una estructura de Truss F34 realista con tubos principales y diagonales."""
        num_sections = math.ceil(length_m / 2.0)
        
        code = f"""
import bpy
import math

def create_truss_section(length, start_x, height, name, collection):
    sec = 0.29
    tube_r = 0.025
    diag_r = 0.01
    
    # 4 Tubos principales
    offsets = [(-sec/2, -sec/2), (sec/2, -sec/2), (sec/2, sec/2), (-sec/2, sec/2)]
    for i, off in enumerate(offsets):
        bpy.ops.mesh.primitive_cylinder_add(radius=tube_r, depth=length, location=(start_x + length/2, off[0], height + off[1]))
        t = bpy.context.active_object
        t.rotation_euler[1] = 1.5708
        t.name = f"{{name}}_Chord_{{i}}"
        collection.objects.link(t)
        bpy.context.scene.collection.objects.unlink(t)

    # Diagonales (Ziz-zag simplificado)
    diag_steps = int(length / 0.4)
    for i in range(diag_steps):
        x = start_x + (i * 0.4) + 0.2
        bpy.ops.mesh.primitive_cylinder_add(radius=diag_r, depth=sec * 1.3, location=(x, 0, height))
        d = bpy.context.active_object
        d.rotation_euler[0] = 0.7854
        collection.objects.link(d)
        bpy.context.scene.collection.objects.unlink(d)

def build_rig(sections, height, base_name):
    col = bpy.data.collections.new(base_name)
    bpy.context.scene.collection.children.link(col)
    for i in range(sections):
        create_truss_section(2.0, (i * 2.0) - ((sections * 2.0) / 2), height, f"{{base_name}}_S{{i}}", col)
    return sections

result = {{"sections": build_rig({num_sections}, {height_m}, "{name}")}}
"""
        b = get_blender()
        return json.dumps(b.send_command("execute_code", {"code": code}), indent=2)

    @mcp.tool(**RW())
    def av_add_moving_heads_hifi(truss_name: str, count: int = 4) -> str:
        """Deploys a high-fidelity moving head fixture (Base, Yoke, Head).
        Distribuye luminarias realistas compuestas por base, yugo y cabeza óptica."""
        code = f"""
import bpy

def create_fixture(location, name):
    # Base
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    base = bpy.context.active_object
    base.name = name + "_Base"
    base.scale = (0.4, 0.4, 0.15)
    
    # Yugo (U-Arm)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.4, location=(location[0], location[1], location[2]+0.25))
    yoke = bpy.context.active_object
    yoke.name = name + "_Yoke"
    yoke.parent = base
    
    # Cabeza (Head)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.4, location=(location[0], location[1], location[2]+0.5))
    head = bpy.context.active_object
    head.name = name + "_Head"
    head.parent = yoke
    return base

def distribute(truss_name, count):
    objs = [o for o in bpy.data.objects if truss_name in o.name]
    if not objs: return 0
    min_x = min(o.location.x for o in objs) - 1.0
    max_x = max(o.location.x for o in objs) + 1.0
    z = objs[0].location.z - 0.6
    step = (max_x - min_x) / (count + 1)
    for i in range(count):
        create_fixture((min_x + step*(i+1), 0, z), f"MH_HiFi_{{i}}")
    return count

result = {{"fixtures": distribute("{truss_name}", {count})}}
"""
        b = get_blender()
        return json.dumps(b.send_command("execute_code", {"code": code}), indent=2)
