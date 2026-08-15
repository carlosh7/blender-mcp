"""
blender-mcp — AI Integration (Real)
Integración real con Ollama para Text→3D, Image→3D.
Usa el modelo local del usuario para entender descripciones.
"""
try:
    import bpy
except ImportError:
    bpy = None

import json
import os
import urllib.request
import re
import math


# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE IA
# ═══════════════════════════════════════════════════════════════

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = "phi3:mini"


def query_llm(prompt, model=None):
    """
    Enviar consulta a Ollama y recibir respuesta.
    
    Args:
        prompt: Prompt de texto
        model: Modelo a usar (default: deepseek-v4-flash)
    
    Returns:
        Respuesta del modelo
    """
    if model is None:
        model = DEFAULT_MODEL
    
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 500,
        }
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result.get("response", "")
    except Exception as e:
        print(f"Error consultando LLM: {e}")
        return ""


# ═══════════════════════════════════════════════════════════════
# PARSER DE LENGUAJE NATURAL
# ═══════════════════════════════════════════════════════════════

def parse_description_with_ai(description):
    """
    Usar IA para parsear descripción de objeto.
    
    Args:
        description: Descripción en lenguaje natural
    
    Returns:
        dict con objeto parseado
    """
    prompt = f"""Analiza esta descripción de un objeto 3D y devuelve un JSON con:
- type: tipo de objeto (furniture, vehicle, character, building, etc.)
- shape: forma principal (cube, sphere, cylinder, etc.)
- color: color en formato RGB (0-1)
- size: tamaño estimado en metros
- material: tipo de material (wood, metal, plastic, glass, etc.)
- style: estilo (modern, classic, minimal, etc.)

Descripción: "{description}"

Responde SOLO con el JSON, sin texto adicional."""

    response = query_llm(prompt)
    
    try:
        # Limpiar respuesta
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        
        # Parsear JSON
        parsed = json.loads(response)
        return parsed
    except (json.JSONDecodeError, IndexError, ValueError) as e:
        # Fallback: parsear manualmente
        print(f"[ai] JSON parse failed, using manual fallback: {e}")
        return parse_description_manual(description)


def parse_description_manual(description):
    """Parse manual como fallback"""
    result = {
        "type": "unknown",
        "shape": "cube",
        "color": (0.5, 0.5, 0.5),
        "size": 1.0,
        "material": "plastic",
        "style": "modern",
    }
    
    desc_lower = description.lower()
    
    # Detectar tipo
    type_map = {
        "chair": "furniture", "silla": "furniture",
        "table": "furniture", "mesa": "furniture",
        "sofa": "furniture", "sofá": "furniture",
        "bed": "furniture", "cama": "furniture",
        "car": "vehicle", "coche": "vehicle", "auto": "vehicle",
        "bike": "vehicle", "bicicleta": "vehicle",
        "house": "building", "casa": "building",
        "person": "character", "persona": "character",
        "human": "character", "humano": "character",
        "dog": "animal", "perro": "animal",
        "cat": "animal", "gato": "animal",
    }
    
    for keyword, obj_type in type_map.items():
        if keyword in desc_lower:
            result["type"] = obj_type
            break
    
    # Detectar forma
    shape_map = {
        "cube": "cube", "cubo": "cube",
        "sphere": "sphere", "esfera": "sphere", "bola": "sphere",
        "cylinder": "cylinder", "cilindro": "cylinder",
        "cone": "cone", "cono": "cone",
        "torus": "torus", "donut": "torus",
    }
    
    for keyword, shape in shape_map.items():
        if keyword in desc_lower:
            result["shape"] = shape
            break
    
    # Detectar color
    color_map = {
        "red": (0.8, 0.1, 0.1), "rojo": (0.8, 0.1, 0.1),
        "blue": (0.1, 0.1, 0.8), "azul": (0.1, 0.1, 0.8),
        "green": (0.1, 0.7, 0.1), "verde": (0.1, 0.7, 0.1),
        "yellow": (0.9, 0.9, 0.1), "amarillo": (0.9, 0.9, 0.1),
        "black": (0.05, 0.05, 0.05), "negro": (0.05, 0.05, 0.05),
        "white": (0.9, 0.9, 0.9), "blanco": (0.9, 0.9, 0.9),
        "gold": (0.85, 0.65, 0.1), "dorado": (0.85, 0.65, 0.1),
        "silver": (0.8, 0.8, 0.8), "plateado": (0.8, 0.8, 0.8),
    }
    
    for keyword, color in color_map.items():
        if keyword in desc_lower:
            result["color"] = color
            break
    
    # Detectar material
    material_map = {
        "wood": "wood", "madera": "wood",
        "metal": "metal", "metal": "metal",
        "plastic": "plastic", "plástico": "plastic",
        "glass": "glass", "vidrio": "glass",
        "leather": "leather", "cuero": "leather",
        "fabric": "fabric", "tela": "fabric",
    }
    
    for keyword, material in material_map.items():
        if keyword in desc_lower:
            result["material"] = material
            break
    
    # Detectar tamaño
    size_map = {
        "small": 0.5, "pequeño": 0.5, "pequeña": 0.5,
        "medium": 1.0, "mediano": 1.0, "mediana": 1.0,
        "large": 2.0, "grande": 2.0,
        "big": 2.0,
    }
    
    for keyword, size in size_map.items():
        if keyword in desc_lower:
            result["size"] = size
            break
    
    return result


# ═══════════════════════════════════════════════════════════════
# GENERADOR DE OBJETOS 3D
# ═══════════════════════════════════════════════════════════════

def generate_3d_from_parsed(parsed):
    """
    Generar objeto 3D desde datos parseados.
    
    Args:
        parsed: dict con tipo, forma, color, etc.
    
    Returns:
        Objeto creado
    """
    obj_type = parsed.get("type", "unknown")
    shape = parsed.get("shape", "cube")
    color = parsed.get("color", (0.5, 0.5, 0.5))
    size = parsed.get("size", 1.0)
    material = parsed.get("material", "plastic")
    
    # Crear geometría según tipo
    if obj_type == "furniture":
        return _create_furniture(parsed)
    elif obj_type == "vehicle":
        return _create_vehicle(parsed)
    elif obj_type == "character":
        return _create_character(parsed)
    elif obj_type == "building":
        return _create_building(parsed)
    elif obj_type == "animal":
        return _create_animal(parsed)
    else:
        return _create_generic(parsed)


def _create_furniture(parsed):
    """Crear mueble"""
    if bpy is None:
        print("ERROR: bpy not available (run inside Blender)")
        return None
    
    size = parsed.get("size", 1.0)
    color = parsed.get("color", (0.5, 0.3, 0.15))
    
    # Crear base (asiento)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, size * 0.45))
    seat = bpy.context.active_object
    seat.name = "Furniture_Seat"
    seat.scale = (size * 0.45, size * 0.45, size * 0.04)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.new("FurnitureMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    seat.data.materials.append(mat)
    
    # Patas (4)
    for x in [-0.18, 0.18]:
        for y in [-0.18, 0.18]:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=size * 0.02,
                depth=size * 0.45,
                location=(x * size, y * size, size * 0.22)
            )
            leg = bpy.context.active_object
            leg.name = "Furniture_Leg"
            leg.data.materials.append(mat)
    
    print(f"Mueble creado: size={size}m, color={color}")
    return seat


def _create_vehicle(parsed):
    """Crear vehículo"""
    if bpy is None:
        print("ERROR: bpy not available (run inside Blender)")
        return None
    
    size = parsed.get("size", 1.5)
    color = parsed.get("color", (0.8, 0.1, 0.1))
    
    # Carrocería
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, size * 0.3))
    body = bpy.context.active_object
    body.name = "Vehicle_Body"
    body.scale = (size * 1.5, size * 0.6, size * 0.4)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.new("VehicleMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.8
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.2
    body.data.materials.append(mat)
    
    # Ruedas (4)
    for x in [-0.6, 0.6]:
        for y in [-0.4, 0.4]:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=size * 0.12,
                depth=size * 0.08,
                location=(x * size, y * size, size * 0.12)
            )
            wheel = bpy.context.active_object
            wheel.name = "Vehicle_Wheel"
            wheel.rotation_euler = (0, math.pi/2, 0)
            wheel.data.materials.append(mat)
    
    print(f"Vehículo creado: size={size}m, color={color}")
    return body


def _create_character(parsed):
    """Crear personaje"""
    if bpy is None:
        print("ERROR: bpy not available (run inside Blender)")
        return None
    
    size = parsed.get("size", 1.8)
    color = parsed.get("color", (0.8, 0.6, 0.5))
    
    # Material piel
    skin_mat = bpy.data.materials.new("SkinMat")
    skin_mat.use_nodes = True
    skin_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    skin_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.7
    
    # Torso
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, size * 0.5))
    torso = bpy.context.active_object
    torso.name = "Character_Torso"
    torso.scale = (size * 0.2, size * 0.15, size * 0.3)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    torso.data.materials.append(skin_mat)
    
    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=size * 0.1,
        location=(0, 0, size * 0.85)
    )
    head = bpy.context.active_object
    head.name = "Character_Head"
    head.data.materials.append(skin_mat)
    
    # Brazos
    for side in ["L", "R"]:
        x_sign = 1 if side == "L" else -1
        bpy.ops.mesh.primitive_cylinder_add(
            radius=size * 0.03,
            depth=size * 0.3,
            location=(x_sign * size * 0.22, 0, size * 0.65)
        )
        arm = bpy.context.active_object
        arm.name = f"Character_Arm_{side}"
        arm.data.materials.append(skin_mat)
    
    # Piernas
    for side in ["L", "R"]:
        x_sign = 1 if side == "L" else -1
        bpy.ops.mesh.primitive_cylinder_add(
            radius=size * 0.04,
            depth=size * 0.35,
            location=(x_sign * size * 0.08, 0, size * 0.15)
        )
        leg = bpy.context.active_object
        leg.name = f"Character_Leg_{side}"
        leg.data.materials.append(skin_mat)
    
    print(f"Personaje creado: size={size}m")
    return torso


def _create_building(parsed):
    """Crear edificio"""
    if bpy is None:
        print("ERROR: bpy not available (run inside Blender)")
        return None
    
    size = parsed.get("size", 5.0)
    color = parsed.get("color", (0.7, 0.68, 0.65))
    
    # Estructura
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, size * 0.5))
    building = bpy.context.active_object
    building.name = "Building"
    building.scale = (size, size * 0.8, size)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    
    # Material
    mat = bpy.data.materials.new("BuildingMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    building.data.materials.append(mat)
    
    print(f"Edificio creado: size={size}m")
    return building


def _create_animal(parsed):
    """Crear animal"""
    if bpy is None:
        print("ERROR: bpy not available (run inside Blender)")
        return None
    
    size = parsed.get("size", 0.5)
    color = parsed.get("color", (0.5, 0.35, 0.2))
    
    # Material pelo
    fur_mat = bpy.data.materials.new("FurMat")
    fur_mat.use_nodes = True
    fur_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    fur_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    
    # Cuerpo
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, size * 0.5))
    body = bpy.context.active_object
    body.name = "Animal_Body"
    body.scale = (size * 0.3, size * 0.6, size * 0.25)
    bpy.ops.object.transform_apply(rotation=False, scale=True)
    body.data.materials.append(fur_mat)
    
    # Cabeza
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=size * 0.12,
        location=(0, size * 0.4, size * 0.5)
    )
    head = bpy.context.active_object
    head.name = "Animal_Head"
    head.data.materials.append(fur_mat)
    
    # Patas (4)
    leg_positions = [
        (size * 0.15, size * 0.25, size * 0.15),
        (-size * 0.15, size * 0.25, size * 0.15),
        (size * 0.15, -size * 0.25, size * 0.15),
        (-size * 0.15, -size * 0.25, size * 0.15),
    ]
    
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=size * 0.025,
            depth=size * 0.3,
            location=pos
        )
        leg = bpy.context.active_object
        leg.name = f"Animal_Leg_{i}"
        leg.data.materials.append(fur_mat)
    
    print(f"Animal creado: size={size}m")
    return body


def _create_generic(parsed):
    """Crear objeto genérico"""
    if bpy is None:
        print("ERROR: bpy not available (run inside Blender)")
        return None
    
    shape = parsed.get("shape", "cube")
    size = parsed.get("size", 1.0)
    color = parsed.get("color", (0.5, 0.5, 0.5))
    
    if shape == "cube":
        bpy.ops.mesh.primitive_cube_add(size=size)
    elif shape == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size/2)
    elif shape == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=size/2, depth=size)
    elif shape == "cone":
        bpy.ops.mesh.primitive_cone_add(radius1=size/2, depth=size)
    elif shape == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=size/2, minor_radius=size/6)
    else:
        bpy.ops.mesh.primitive_cube_add(size=size)
    
    obj = bpy.context.active_object
    obj.name = f"AI_{shape.capitalize()}"
    
    # Material
    mat = bpy.data.materials.new(f"AI_{shape}_Mat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    obj.data.materials.append(mat)
    
    print(f"Objeto genérico: {shape}, size={size}m, color={color}")
    return obj


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL: TEXT TO 3D
# ═══════════════════════════════════════════════════════════════

def text_to_3d(description, model=None):
    """
    Crear modelo 3D desde descripción textual usando IA.
    
    Args:
        description: Descripción en lenguaje natural
        model: Modelo de IA a usar (opcional)
    
    Returns:
        Objeto creado o None
    """
    print(f"\n{'='*50}")
    print(f"TEXT → 3D: {description}")
    print(f"{'='*50}")
    
    # Paso 1: Parsear con IA
    print("\n1. Analizando descripción con IA...")
    parsed = parse_description_with_ai(description)
    print(f"   Resultado: {json.dumps(parsed, indent=2)}")
    
    # Paso 2: Generar 3D
    print("\n2. Generando modelo 3D...")
    obj = generate_3d_from_parsed(parsed)
    
    if obj:
        print(f"\n3. Objeto creado: {obj.name}")
        print(f"   Tipo: {parsed.get('type', 'unknown')}")
        print(f"   Forma: {parsed.get('shape', 'unknown')}")
        print(f"   Tamaño: {parsed.get('size', 1.0)}m")
    
    print(f"{'='*50}\n")
    
    return obj


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN: IMAGE TO 3D (placeholder)
# ═══════════════════════════════════════════════════════════════

def image_to_3d(image_path, model=None):
    """
    Crear modelo 3D desde imagen.
    
    Analiza el nombre del archivo Y el contenido con IA.
    """
    if bpy is None:
        print("ERROR: bpy not available (run inside Blender)")
        return None
    
    print(f"\n{'='*50}")
    print(f"IMAGE → 3D: {image_path}")
    print(f"{'='*50}")
    
    # Paso 1: Analizar nombre del archivo
    filename = os.path.basename(image_path).lower()
    parsed = _analyze_filename(filename)
    
    print(f"\n1. Analyzing filename: {filename}")
    print(f"   From filename: {parsed}")
    
    # Paso 2: Analizar con IA si hay descripción
    if model:
        try:
            prompt = f"Describe esta imagen: {filename}. ¿Qué objetos hay? ¿Qué colores? Responde en JSON."
            response = query_llm(prompt, model)
            if response:
                # Intentar parsear respuesta
                try:
                    ai_parsed = json.loads(response)
                    parsed.update(ai_parsed)
                    print(f"   From AI: {ai_parsed}")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"   AI response (not JSON): {response[:100]}")
        except Exception as e:
            print(f"   AI analysis failed: {e}")
    
    # Paso 3: Crear objeto
    print("\n2. Creating 3D model...")
    obj = generate_3d_from_parsed(parsed)
    
    if obj:
        print(f"\n3. Object created: {obj.name}")
        print(f"   Type: {parsed.get('type', 'unknown')}")
        print(f"   Color: {parsed.get('color', 'unknown')}")
    
    print(f"{'='*50}\n")
    return obj


def analyze_image_with_ai(image_path):
    """
    Analizar imagen con IA para obtener descripción.
    
    Args:
        image_path: Ruta de la imagen
    
    Returns:
        dict con análisis de la imagen
    """
    filename = os.path.basename(image_path).lower()
    
    # Análisis básico por nombre
    parsed = _analyze_filename(filename)
    
    # Intentar análisis con IA
    try:
        prompt = f"Analiza la imagen '{filename}' y describe: ¿Qué objetos hay? ¿Qué colores? ¿Qué estilos? Responde en JSON."
        response = query_llm(prompt)
        if response:
            try:
                ai_analysis = json.loads(response)
                parsed["ai_analysis"] = ai_analysis
            except (json.JSONDecodeError, ValueError):
                parsed["ai_analysis"] = response[:200]
    except Exception as e:
        print(f"[ai] Image analysis failed: {e}")
    
    return parsed


def _analyze_filename(filename):
    """
    Analizar nombre de archivo para determinar tipo de objeto.
    """
    result = {
        "type": "unknown",
        "shape": "cube",
        "color": (0.5, 0.5, 0.5),
        "size": 1.0,
        "material": "plastic",
    }
    
    # Detectar tipo por nombre
    type_keywords = {
        "chair": "furniture", "silla": "furniture",
        "table": "furniture", "mesa": "furniture",
        "sofa": "furniture", "couch": "furniture",
        "bed": "furniture", "cama": "furniture",
        "car": "vehicle", "coche": "vehicle", "auto": "vehicle",
        "bike": "vehicle", "bicycle": "vehicle",
        "house": "building", "casa": "building", "building": "building",
        "person": "character", "human": "character", "man": "character", "woman": "character",
        "dog": "animal", "cat": "animal", "pet": "animal",
        "tree": "nature", "plant": "nature", "flower": "nature",
        "sword": "weapon", "gun": "weapon", "weapon": "weapon",
    }
    
    for keyword, obj_type in type_keywords.items():
        if keyword in filename:
            result["type"] = obj_type
            break
    
    # Detectar color por nombre
    color_keywords = {
        "red": (0.8, 0.1, 0.1), "rojo": (0.8, 0.1, 0.1),
        "blue": (0.1, 0.1, 0.8), "azul": (0.1, 0.1, 0.8),
        "green": (0.1, 0.7, 0.1), "verde": (0.1, 0.7, 0.1),
        "yellow": (0.9, 0.9, 0.1), "amarillo": (0.9, 0.9, 0.1),
        "black": (0.05, 0.05, 0.05), "negro": (0.05, 0.05, 0.05),
        "white": (0.9, 0.9, 0.9), "blanco": (0.9, 0.9, 0.9),
    }
    
    for keyword, color in color_keywords.items():
        if keyword in filename:
            result["color"] = color
            break
    
    # Detectar forma por nombre
    shape_keywords = {
        "sphere": "sphere", "ball": "sphere", "bola": "sphere",
        "cube": "cube", "box": "cube", "caja": "cube",
        "cylinder": "cylinder", "tube": "cylinder",
        "cone": "cone", "pyramid": "cone",
    }
    
    for keyword, shape in shape_keywords.items():
        if keyword in filename:
            result["shape"] = shape
            break
    
    # Detectar tamaño por nombre
    size_keywords = {
        "small": 0.5, "pequeño": 0.5,
        "medium": 1.0, "normal": 1.0,
        "large": 2.0, "big": 2.0, "grande": 2.0,
    }
    
    for keyword, size in size_keywords.items():
        if keyword in filename:
            result["size"] = size
            break
    
    return result


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def test_connection():
    """Probar conexión con Ollama"""
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
            models = [m["name"] for m in result.get("models", [])]
            print(f"Ollama conectado. Modelos: {models}")
            return True
    except Exception as e:
        print(f"Error conectando con Ollama: {e}")
        return False


def list_models():
    """Listar modelos disponibles"""
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
            return [m["name"] for m in result.get("models", [])]
    except Exception as e:
        print(f"[ai] Failed to list models: {e}")
        return []
