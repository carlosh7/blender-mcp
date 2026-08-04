"""
blender-mcp — AI Assets Engine
Motor de IA + Assets: Text→3D, Photo→3D, PolyHaven, AmbientCG.
"""
try:
    import bpy
except ImportError:
    bpy = None

import json
import os
import urllib.request


# ═══════════════════════════════════════════════════════════════
# TEXT TO 3D (con API externa)
# ═══════════════════════════════════════════════════════════════

def text_to_3d_model(description, api="meshy"):
    """
    Crear modelo 3D desde descripción textual.
    
    Args:
        description: Descripción del objeto
        api: API a usar (meshy, tripo, shap-e)
    
    Returns:
        Objeto creado o None
    """
    if bpy is None:
        return None
    
    print(f"Text→3D: {description}")
    
    # Intentar con Meshy API
    if api == "meshy":
        return _meshy_text_to_3d(description)
    
    # Fallback: crear objeto genérico
    return _create_generic_from_text(description)


def _meshy_text_to_3d(description):
    """Usar Meshy API para text→3d"""
    try:
        # Meshy API (requiere API key)
        api_key = os.environ.get("MESHY_API_KEY", "")
        if not api_key:
            print("WARNING: MESHY_API_KEY not set, using fallback")
            return None
        
        url = "https://api.meshy.ai/v2/text-to-3d"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "mode": "preview",
            "prompt": description,
            "art_style": "realistic"
        }
        
        req = urllib.request.Request(url, json.dumps(payload).encode(), headers)
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
            # Descargar modelo
            model_url = result.get("model_url")
            if model_url:
                return _download_and_import(model_url)
    except Exception as e:
        print(f"Meshy API error: {e}")
    
    return None


def _create_generic_from_text(description):
    """Crear objeto genérico desde descripción"""
    if bpy is None:
        return None
    
    # Analizar descripción
    desc_lower = description.lower()
    
    # Detectar tipo
    if any(w in desc_lower for w in ["chair", "silla", "seat"]):
        from ..organic.character_gen import _create_humanoid
        # Crear silla simplificada
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.45))
        obj = bpy.context.active_object
        obj.name = "AI_Chair"
        obj.scale = (0.45, 0.45, 0.04)
        return obj
    
    elif any(w in desc_lower for w in ["table", "mesa"]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
        obj = bpy.context.active_object
        obj.name = "AI_Table"
        obj.scale = (1.2, 0.8, 0.04)
        return obj
    
    elif any(w in desc_lower for w in ["car", "coche", "vehicle"]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.3))
        obj = bpy.context.active_object
        obj.name = "AI_Vehicle"
        obj.scale = (2, 1, 0.4)
        return obj
    
    else:
        # Objeto genérico
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
        obj = bpy.context.active_object
        obj.name = "AI_Object"
        return obj


# ═══════════════════════════════════════════════════════════════
# PHOTO TO 3D
# ═══════════════════════════════════════════════════════════════

def photo_to_3d_model(image_path, api="meshy"):
    """
    Crear modelo 3D desde imagen.
    
    Args:
        image_path: Ruta de la imagen
        api: API a usar
    
    Returns:
        Objeto creado o None
    """
    if bpy is None:
        return None
    
    print(f"Photo→3D: {image_path}")
    
    # Intentar con Meshy API
    if api == "meshy":
        return _meshy_image_to_3d(image_path)
    
    # Fallback: crear objeto basado en nombre de archivo
    return _create_from_filename(image_path)


def _meshy_image_to_3d(image_path):
    """Usar Meshy API para image→3d"""
    try:
        api_key = os.environ.get("MESHY_API_KEY", "")
        if not api_key:
            print("WARNING: MESHY_API_KEY not set")
            return None
        
        # Aquí iría la llamada a la API de Meshy
        # Por ahora return None
        return None
    except Exception as e:
        print(f"Meshy API error: {e}")
        return None


def _create_from_filename(image_path):
    """Crear objeto basado en nombre de archivo"""
    filename = os.path.basename(image_path).lower()
    
    # Analizar nombre para detectar tipo
    if any(w in filename for w in ["chair", "silla"]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.45))
        obj = bpy.context.active_object
        obj.name = "Photo_Chair"
        obj.scale = (0.45, 0.45, 0.04)
        return obj
    
    # Default: crear cubo
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    obj = bpy.context.active_object
    obj.name = "Photo_Object"
    return obj


# ═══════════════════════════════════════════════════════════════
# POLYHAVEN API
# ═══════════════════════════════════════════════════════════════

def search_polyhaven(query, asset_type="hdris"):
    """
    Buscar en PolyHaven.
    
    Args:
        query: Término de búsqueda
        asset_type: 'hdris', 'textures', 'models'
    
    Returns:
        Lista de assets encontrados
    """
    try:
        url = f"https://api.polyhaven.com/assets?t={asset_type}&q={query}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            assets = []
            for asset_id, asset_info in data.items():
                assets.append({
                    "id": asset_id,
                    "name": asset_info.get("name", ""),
                    "type": asset_info.get("type", ""),
                    "url": asset_info.get("url", ""),
                })
            print(f"PolyHaven: {len(assets)} assets found")
            return assets
    except Exception as e:
        print(f"PolyHaven error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# AMBIENTCG API
# ═══════════════════════════════════════════════════════════════

def search_ambientcg(query, asset_type="materials"):
    """
    Buscar en AmbientCG.
    
    Args:
        query: Término de búsqueda
        asset_type: 'materials', 'hdris', 'models'
    
    Returns:
        Lista de assets encontrados
    """
    try:
        url = f"https://ambientcg.com/api/v2/?q={query}&type={asset_type}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            assets = []
            for item in data.get("assets", []):
                assets.append({
                    "id": item.get("asset_id", ""),
                    "name": item.get("name", ""),
                    "type": item.get("type", ""),
                    "url": item.get("download_url", ""),
                })
            print(f"AmbientCG: {len(assets)} assets found")
            return assets
    except Exception as e:
        print(f"AmbientCG error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# IMPORT ASSET
# ═══════════════════════════════════════════════════════════════

def import_asset(asset_path, asset_type="auto"):
    """
    Importar asset 3D.
    
    Args:
        asset_path: Ruta del asset
        asset_type: 'auto', 'glb', 'fbx', 'obj'
    
    Returns:
        Lista de objetos importados
    """
    if bpy is None:
        return []
    
    # Detectar tipo por extensión
    if asset_type == "auto":
        ext = os.path.splitext(asset_path)[1].lower()
        type_map = {
            ".glb": "glb", ".gltf": "glb",
            ".fbx": "fbx",
            ".obj": "obj",
            ".stl": "stl",
        }
        asset_type = type_map.get(ext, "auto")
    
    # Importar según tipo
    imported = []
    try:
        if asset_type == "glb":
            bpy.ops.import_scene.gltf(filepath=asset_path)
        elif asset_type == "fbx":
            bpy.ops.import_scene.fbx(filepath=asset_path)
        elif asset_type == "obj":
            bpy.ops.import_scene.obj(filepath=asset_path)
        elif asset_type == "stl":
            bpy.ops.import_mesh.stl(filepath=asset_path)
        
        imported = [obj for obj in bpy.context.selected_objects]
        print(f"Imported {len(imported)} objects from {asset_path}")
    except Exception as e:
        print(f"Import error: {e}")
    
    return imported


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

def list_ai_apis():
    """Listar APIs de IA disponibles"""
    return {
        "meshy": "Meshy AI (text/image → 3D)",
        "tripo": "Tripo AI (text/image → 3D)",
        "polyhaven": "PolyHaven (HDRIs, textures, models)",
        "ambientcg": "AmbientCG (materials, HDRIs)",
    }


def list_asset_formats():
    """Listar formatos de asset soportados"""
    return {
        ".glb": "glTF Binary",
        ".gltf": "glTF JSON",
        ".fbx": "FilmBox",
        ".obj": "Wavefront OBJ",
        ".stl": "STL (3D Print)",
        ".usd": "Universal Scene Description",
    }


# ═══════════════════════════════════════════════════════════════
# DOWNLOAD ASSETS
# ═══════════════════════════════════════════════════════════════

def download_polyhaven_asset(asset_id, asset_type="textures", save_dir="/tmp/assets"):
    """
    Descargar asset desde PolyHaven.
    
    Args:
        asset_id: ID del asset
        asset_type: 'hdris', 'textures', 'models'
        save_dir: Directorio de guardado
    
    Returns:
        Ruta del archivo descargado
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        
        # Obtener info del asset
        url = f"https://api.polyhaven.com/files/{asset_id}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            
            # Descargar archivo principal
            files = data.get("hdri", data.get("diff", data.get("normal", {})))
            if files:
                file_url = list(files.values())[0] if isinstance(files, dict) else files
                filepath = os.path.join(save_dir, f"{asset_id}.exr")
                
                urllib.request.urlretrieve(file_url, filepath)
                print(f"Downloaded: {filepath}")
                return filepath
    
    return None


def download_ambientcg_asset(asset_id, asset_type="materials", save_dir="/tmp/assets"):
    """
    Descargar asset desde AmbientCG.
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        
        # Obtener info del asset
        url = f"https://ambientcg.com/api/v2/?type={asset_type}&asset_id={asset_id}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            
            # Descargar archivo
            download_url = data.get("download_url")
            if download_url:
                filepath = os.path.join(save_dir, f"{asset_id}.zip")
                urllib.request.urlretrieve(download_url, filepath)
                print(f"Downloaded: {filepath}")
                return filepath
    
    return None


def get_asset_info(asset_id, source="polyhaven"):
    """
    Obtener información de un asset.
    
    Args:
        asset_id: ID del asset
        source: 'polyhaven', 'ambientcg'
    
    Returns:
        dict con información del asset
    """
    try:
        if source == "polyhaven":
            url = f"https://api.polyhaven.com/assets/{asset_id}"
        elif source == "ambientcg":
            url = f"https://ambientcg.com/api/v2/?asset_id={asset_id}"
        else:
            return {"error": f"Unknown source: {source}"}
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read())
    except Exception as e:
        return {"error": str(e)}


def batch_import_assets(asset_list, save_dir="/tmp/assets"):
    """
    Importar múltiples assets.
    
    Args:
        asset_list: Lista de dicts [{id, source, type}, ...]
        save_dir: Directorio de guardado
    
    Returns:
        Lista de assets importados
    """
    imported = []
    
    for asset in asset_list:
        asset_id = asset.get("id")
        source = asset.get("source", "polyhaven")
        
        if source == "polyhaven":
            filepath = download_polyhaven_asset(asset_id, save_dir=save_dir)
        elif source == "ambientcg":
            filepath = download_ambientcg_asset(asset_id, save_dir=save_dir)
        else:
            filepath = None
        
        if filepath:
            imported.append({
                "id": asset_id,
                "source": source,
                "filepath": filepath,
            })
    
    print(f"Batch import: {len(imported)} assets imported")
    return imported


# ═══════════════════════════════════════════════════════════════
# AI TEXTURE GENERATION
# ═══════════════════════════════════════════════════════════════

def create_ai_texture(description, style="realistic"):
    """
    Generar textura con IA.
    
    Args:
        description: Descripción de la textura
        style: Estilo (realistic, cartoon, stylized)
    
    Returns:
        Material con textura generada
    """
    if bpy is None:
        return None
    
    # Por ahora, crear textura procedural basada en descripción
    mat = bpy.data.materials.new(f"AI_{description[:20]}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    for n in nodes:
        nodes.remove(n)
    
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    
    # Analizar descripción para color
    desc_lower = description.lower()
    if "red" in desc_lower or "rojo" in desc_lower:
        bsdf.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1)
    elif "blue" in desc_lower or "azul" in desc_lower:
        bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.8, 1)
    elif "green" in desc_lower or "verde" in desc_lower:
        bsdf.inputs["Base Color"].default_value = (0.1, 0.7, 0.1, 1)
    else:
        bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
    
    # Agregar textura procedural
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (0, 100)
    noise.inputs["Scale"].default_value = 10
    
    links.new(noise.outputs["Fac"], bsdf.inputs["Roughness"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    
    print(f"AI texture created: {description}")
    return mat
