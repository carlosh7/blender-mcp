"""
blender-mcp — Audiovisual Event Tools
High-level tools for building event structures (LED walls, Truss, Lighting).
"""
import json
import math
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)

def register_tools(mcp):
    @mcp.tool(**RW(doc="Builds a perfectly aligned LED wall using standard 500x500mm cabinets."))
    def av_build_led_wall(width_m: float, height_m: float, name: str = "LED_Wall") -> str:
        """
        Calcula y construye una pantalla LED basada en el estándar industrial de 0.5m x 0.5m.
        Alinea automáticamente los cabinets en una cuadrícula perfecta.
        """
        cols = math.ceil(width_m / 0.5)
        rows = math.ceil(height_m / 0.5)
        
        code = f"""
import bpy
from mathutils import Vector

def create_led_wall(cols, rows, base_name):
    panel_size = 0.5
    depth = 0.075
    collection = bpy.data.collections.new(base_name)
    bpy.context.scene.collection.children.link(collection)
    
    panels = []
    for r in range(rows):
        for c in range(cols):
            x = (c * panel_size) - ((cols * panel_size) / 2) + (panel_size / 2)
            z = (r * panel_size) + (panel_size / 2)
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, z))
            p = bpy.context.active_object
            p.name = f"{{base_name}}_P{{c}}_{{r}}"
            p.scale = (panel_size, depth, panel_size)
            
            # Asignar a colección y limpiar escena
            for col in p.users_collection:
                col.objects.unlink(p)
            collection.objects.link(p)
            panels.append(p)
            
    return len(panels)

result = {{"panels_created": create_led_wall({cols}, {rows}, "{name}")}}
"""
        b = get_blender()
        r = b.send_command("execute_code", {"code": code})
        return json.dumps({
            "status": "SUCCESS",
            "message": f"LED Wall construida: {cols}x{rows} cabinets.",
            "total_size": f"{cols*0.5}m x {rows*0.5}m",
            "details": r
        }, indent=2)

    @mcp.tool(**RW(doc="Deploys a standard F34 aluminum truss rig at a specific height."))
    def av_setup_truss_rig(length_m: float, height_m: float = 6.0, name: str = "Main_Truss") -> str:
        """
        Crea una estructura de Truss F34 (29cm) de una longitud específica.
        Calcula automáticamente el número de tramos necesarios.
        """
        # Usamos tramos de 2m como estándar
        num_sections = math.ceil(length_m / 2.0)
        actual_length = num_sections * 2.0
        
        code = f"""
import bpy

def setup_truss(num_sections, height, base_name):
    section_len = 2.0
    section_width = 0.29
    
    collection = bpy.data.collections.new(base_name)
    bpy.context.scene.collection.children.link(collection)
    
    for i in range(num_sections):
        x = (i * section_len) - ((num_sections * section_len) / 2) + (section_len / 2)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, height))
        t = bpy.context.active_object
        t.name = f"{{base_name}}_S{{i}}"
        t.scale = (section_len, section_width, section_width)
        
        for col in t.users_collection:
            col.objects.unlink(t)
        collection.objects.link(t)
        
    return num_sections

result = {{"sections": setup_truss({num_sections}, {height_m}, "{name}")}}
"""
        b = get_blender()
        r = b.send_command("execute_code", {"code": code})
        return json.dumps({
            "status": "SUCCESS",
            "actual_length": actual_length,
            "sections": num_sections,
            "details": r
        }, indent=2)

    @mcp.tool(**RW(doc="Distributes moving head lights along a truss structure."))
    def av_add_moving_heads(truss_name: str, count: int = 4) -> str:
        """
        Distribuye cabezas móviles de forma equidistante a lo largo de un truss existente.
        Las posiciona automáticamente debajo de la estructura.
        """
        code = f"""
import bpy
from mathutils import Vector

def add_lights(target_truss, count):
    # Encontrar objetos del truss para calcular extensión
    truss_objs = [obj for obj in bpy.data.objects if target_truss in obj.name]
    if not truss_objs: return 0
    
    # Calcular límites
    min_x = min(o.location.x - (o.dimensions.x/2) for o in truss_objs)
    max_x = max(o.location.x + (o.dimensions.x/2) for o in truss_objs)
    z = truss_objs[0].location.z - 0.5 # Debajo del truss
    
    created = 0
    step = (max_x - min_x) / (count + 1)
    
    for i in range(count):
        x = min_x + (step * (i + 1))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.4, location=(x, 0, z))
        light = bpy.context.active_object
        light.name = f"MH_{{target_truss}}_{{i}}"
        created += 1
    return created

result = {{"created": add_lights("{truss_name}", {count})}}
"""
        b = get_blender()
        r = b.send_command("execute_code", {"code": code})
        return json.dumps(r, indent=2)
