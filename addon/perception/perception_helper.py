"""
blender-mcp — Perception Helper
Helper que fuerza el flujo de percepción para cualquier agente.
"""
import socket
import json
import time


def send_command(cmd, params=None, timeout=25):
    """Ejecutar comando en Blender"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(('localhost', 9876))
    s.send(json.dumps({'command': cmd, 'params': params or {}}).encode() + b'\n')
    r = b''
    dl = time.time() + timeout - 5
    while time.time() < dl:
        try:
            c = s.recv(65536)
            if c:
                r += c
                if b'\n' in r:
                    break
        except:
            continue
    s.close()
    if r:
        return json.loads(r.decode().strip()).get('result', {})
    return {}


# ═══════════════════════════════════════════════════════════════
# PERCEPCIÓN OBLIGATORIA
# ═══════════════════════════════════════════════════════════════

def analyze_scene():
    """Analizar escena actual"""
    return send_command('''
import bpy
from mathutils import Vector

objects = bpy.data.objects
meshes = [o for o in objects if o.type == \"MESH\"]
materials = bpy.data.materials
meshes_with_mat = [o for o in meshes if o.data.materials]
quality = int(len(meshes_with_mat) / max(len(meshes), 1) * 100)

result = {
    \"objects\": len(objects),
    \"meshes\": len(meshes),
    \"materials\": len(materials),
    \"quality\": quality,
}
print(f\"Scene: {result}\")
''')
    return result


def validate_object(obj_name):
    """Validar un objeto específico"""
    return send_command(f'''
import bpy
from mathutils import Vector

obj = bpy.data.objects.get(\"{obj_name}\")
if obj:
    bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mins = Vector((min(v[i] for v in bbox) for i in range(3)))
    maxs = Vector((max(v[i] for v in bbox) for i in range(3)))
    size = maxs - mins
    
    result = {{
        \"name\": obj.name,
        \"type\": obj.type,
        \"position\": tuple(obj.location),
        \"size\": tuple(size),
        \"has_material\": bool(obj.data.materials) if obj.type == \"MESH\" else False,
    }}
    print(f\"Validated: {{result}}\")
''')
    return result


def take_screenshot(filepath=\"/tmp/blender_screenshot.png\"):
    """Tomar screenshot del viewport"""
    return send_command(f'''
import bpy
bpy.ops.screen.screenshot_area(filepath=\"{filepath}\")
print(f\"Screenshot: {filepath}\")
''')


def get_scene_info():
    """Obtener información de la escena"""
    return send_command('''
import bpy
result = {{
    \"objects\": len(bpy.data.objects),
    \"meshes\": len([o for o in bpy.data.objects if o.type == \"MESH\"]),
    \"materials\": len(bpy.data.materials),
    \"collections\": [c.name for c in bpy.data.collections],
}}
print(f\"Scene info: {result}\")
''')


# ═══════════════════════════════════════════════════════════════
# FLUJO OBLIGATORIO
# ═══════════════════════════════════════════════════════════════

def before_create():
    """ANTES de crear: analizar escena"""
    print(\"\\nBEFORE CREATE:\")
    info = get_scene_info()
    print(f\"  Scene has {info.get('objects', 0)} objects\")
    return info


def after_create(obj_name):
    """DESPUÉS de crear: validar y ver"""
    print(f\"\\nAFTER CREATE: {obj_name}\")
    
    # Validar objeto
    validation = validate_object(obj_name)
    print(f\"  Validation: {validation}\")
    
    # Tomar screenshot
    take_screenshot(f\"/tmp/after_{obj_name}.png\")
    print(f\"  Screenshot saved\")


def verify_connection(obj_name, parent_name):
    """Verificar conexión entre piezas"""
    return send_command(f'''
import bpy
from mathutils import Vector

child = bpy.data.objects.get(\"{obj_name}\")
parent = bpy.data.objects.get(\"{parent_name}\")

if child and parent:
    child_bb = [child.matrix_world @ Vector(c) for c in child.bound_box]
    parent_bb = [parent.matrix_world @ Vector(c) for c in parent.bound_box]
    
    child_min = Vector((min(v[i] for v in child_bb) for i in range(3)))
    parent_max = Vector((max(v[i] for v in parent_bb) for i in range(3)))
    
    distance = (child_min - parent_max).length
    connected = distance < 0.01
    
    print(f\"Connection: {obj_name} to {parent_name}\")
    print(f\"  Distance: {distance:.4f}m\")
    print(f\"  Connected: {connected}\")
''')
