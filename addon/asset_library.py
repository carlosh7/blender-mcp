"""
blender-mcp — Asset Library
Biblioteca de assets: guardar, cargar, reutilizar objetos.

Regla de oro: REUTILIZAR objetos creados anteriormente.
"""
import bpy
import json
import os
import shutil
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

ASSET_DIR = Path("/tmp/blender_assets")
ASSET_INDEX = ASSET_DIR / "index.json"


# ═══════════════════════════════════════════════════════════════
# GESTIÓN DE BIBLIOTECA
# ═══════════════════════════════════════════════════════════════

def _ensure_asset_dir():
    """Crear directorio de assets si no existe."""
    ASSET_DIR.mkdir(parents=True, exist_ok=True)


def _load_index():
    """Cargar índice de assets."""
    _ensure_asset_dir()
    if ASSET_INDEX.exists():
        with open(ASSET_INDEX, 'r') as f:
            return json.load(f)
    return {"assets": {}}


def _save_index(index):
    """Guardar índice de assets."""
    _ensure_asset_dir()
    with open(ASSET_INDEX, 'w') as f:
        json.dump(index, f, indent=2)


# ═══════════════════════════════════════════════════════════════
# GUARDAR ASSETS
# ═══════════════════════════════════════════════════════════════

def save_asset(name, object_names, description="", tags=None):
    """
    Guardar objetos como asset en la biblioteca.
    
    Args:
        name: Nombre del asset
        object_names: Lista de nombres de objetos a guardar
        description: Descripción del asset
        tags: Tags para búsqueda
    
    Returns:
        dict con información del asset guardado
    """
    _ensure_asset_dir()
    
    # Verificar que los objetos existen
    objects = []
    for obj_name in object_names:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            objects.append(obj)
        else:
            print(f"[asset] Objeto no encontrado: {obj_name}")
    
    if not objects:
        return {"error": "No se encontraron objetos válidos"}
    
    # Seleccionar solo los objetos a exportar
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    
    # Crear directorio del asset
    asset_dir = ASSET_DIR / name
    asset_dir.mkdir(exist_ok=True)
    
    # Guardar como .blend
    filepath = asset_dir / f"{name}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(filepath))
    
    # Guardar metadata
    metadata = {
        "name": name,
        "description": description,
        "tags": tags or [],
        "objects": [obj.name for obj in objects],
        "created_at": datetime.now().isoformat(),
        "filepath": str(filepath),
    }
    
    metadata_path = asset_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Actualizar índice
    index = _load_index()
    index["assets"][name] = {
        "description": description,
        "tags": tags or [],
        "objects": [obj.name for obj in objects],
        "created_at": metadata["created_at"],
    }
    _save_index(index)
    
    print(f"[asset] Asset guardado: {name} ({len(objects)} objetos)")
    return metadata


def save_collection_as_asset(collection_name, asset_name=None, description=""):
    """
    Guardar una colección completa como asset.
    
    Args:
        collection_name: Nombre de la colección
        asset_name: Nombre del asset (default: collection_name)
        description: Descripción
    
    Returns:
        dict con información del asset
    """
    col = bpy.data.collections.get(collection_name)
    if not col:
        return {"error": f"Colección no encontrada: {collection_name}"}
    
    obj_names = [obj.name for obj in col.objects]
    
    return save_asset(
        asset_name or collection_name,
        obj_names,
        description or f"Colección {collection_name}",
        tags=[collection_name.lower()]
    )


# ═══════════════════════════════════════════════════════════════
# CARGAR ASSETS
# ═══════════════════════════════════════════════════════════════

def load_asset(name, position=(0, 0, 0)):
    """
    Cargar un asset desde la biblioteca.
    
    Args:
        name: Nombre del asset
        position: Posición donde insertar
    
    Returns:
        dict con los objetos cargados
    """
    asset_dir = ASSET_DIR / name
    filepath = asset_dir / f"{name}.blend"
    
    if not filepath.exists():
        return {"error": f"Asset no encontrado: {name}"}
    
    # Guardar estado actual
    current_objects = set(obj.name for obj in bpy.data.objects)
    
    # Cargar el archivo
    bpy.ops.wm.append(
        filepath=str(filepath),
        directory=str(filepath),
        filename="Collection"
    )
    
    # Identificar objetos nuevos
    new_objects = set(obj.name for obj in bpy.data.objects) - current_objects
    
    # Mover objetos nuevos a la posición deseada
    for obj_name in new_objects:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            obj.location += position
    
    print(f"[asset] Asset cargado: {name} ({len(new_objects)} objetos)")
    
    return {
        "name": name,
        "objects": list(new_objects),
        "position": position,
    }


# ═══════════════════════════════════════════════════════════════
# BUSCAR ASSETS
# ═══════════════════════════════════════════════════════════════

def search_assets(query=None, tags=None):
    """
    Buscar assets en la biblioteca.
    
    Args:
        query: Texto de búsqueda
        tags: Tags a filtrar
    
    Returns:
        Lista de assets encontrados
    """
    index = _load_index()
    results = []
    
    for name, info in index["assets"].items():
        # Filtro por query
        if query:
            query_lower = query.lower()
            name_match = query_lower in name.lower()
            desc_match = query_lower in info.get("description", "").lower()
            if not name_match and not desc_match:
                continue
        
        # Filtro por tags
        if tags:
            asset_tags = set(info.get("tags", []))
            if not set(tags).intersection(asset_tags):
                continue
        
        results.append({
            "name": name,
            "description": info.get("description", ""),
            "tags": info.get("tags", []),
            "objects": info.get("objects", []),
            "created_at": info.get("created_at", ""),
        })
    
    return results


def list_assets():
    """Listar todos los assets disponibles."""
    index = _load_index()
    
    print("\n📚 BIBLIOTECA DE ASSETS")
    print("="*50)
    
    if not index["assets"]:
        print("  (Vacía)")
        return []
    
    for name, info in index["assets"].items():
        tags = ", ".join(info.get("tags", []))
        print(f"\n  📦 {name}")
        print(f"     {info.get('description', 'Sin descripción')}")
        print(f"     Tags: {tags or 'Ninguno'}")
        print(f"     Objetos: {len(info.get('objects', []))}")
    
    print("="*50)
    return list(index["assets"].keys())


# ═══════════════════════════════════════════════════════════════
# GESTIONAR ASSETS
# ═══════════════════════════════════════════════════════════════

def delete_asset(name):
    """
    Eliminar un asset de la biblioteca.
    
    Args:
        name: Nombre del asset
    
    Returns:
        bool
    """
    asset_dir = ASSET_DIR / name
    
    if asset_dir.exists():
        shutil.rmtree(asset_dir)
    
    index = _load_index()
    if name in index["assets"]:
        del index["assets"][name]
        _save_index(index)
    
    print(f"[asset] Asset eliminado: {name}")
    return True


def get_asset_info(name):
    """
    Obtener información detallada de un asset.
    
    Args:
        name: Nombre del asset
    
    Returns:
        dict con información del asset
    """
    index = _load_index()
    
    if name not in index["assets"]:
        return {"error": f"Asset no encontrado: {name}"}
    
    info = index["assets"][name]
    asset_dir = ASSET_DIR / name
    
    return {
        "name": name,
        "description": info.get("description", ""),
        "tags": info.get("tags", []),
        "objects": info.get("objects", []),
        "created_at": info.get("created_at", ""),
        "filepath": str(asset_dir / f"{name}.blend"),
        "has_file": (asset_dir / f"{name}.blend").exists(),
    }


# ═══════════════════════════════════════════════════════════════
# ASSETS PREDEFINIDOS
# ═══════════════════════════════════════════════════════════════

BUILTIN_ASSETS = {
    "chair_wood": {
        "description": "Silla de madera estándar",
        "tags": ["furniture", "chair", "wood"],
        "create_func": "chair",
    },
    "table_desk": {
        "description": "Mesa de escritorio",
        "tags": ["furniture", "table", "desk"],
        "create_func": "table",
    },
    "cup_coffee": {
        "description": "Taza de café con plato",
        "tags": ["kitchen", "cup", "coffee"],
        "create_func": "cup",
    },
}


def create_builtin_asset(asset_type, position=(0, 0, 0)):
    """
    Crear un asset predefinido y guardarlo en la biblioteca.
    
    Args:
        asset_type: Tipo de asset (chair_wood, table_desk, cup_coffee)
        position: Posición de creación
    
    Returns:
        dict con el asset creado
    """
    if asset_type not in BUILTIN_ASSETS:
        return {"error": f"Asset predefinido no encontrado: {asset_type}"}
    
    import creation_rules
    
    config = BUILTIN_ASSETS[asset_type]
    
    # Crear objeto
    created = creation_rules.create_object(
        config["create_func"],
        position
    )
    
    # Guardar como asset
    obj_names = [obj.name for obj in created.values()]
    result = save_asset(
        asset_type,
        obj_names,
        config["description"],
        config["tags"]
    )
    
    return result
