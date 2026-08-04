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
    }
