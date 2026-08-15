"""
blender-mcp — Asset Cache
Caché local de assets descargados para evitar descargas duplicadas.
"""
import os
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Optional


# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

CACHE_DIR = Path("/tmp/blender_mcp_assets_cache")
CACHE_INDEX = CACHE_DIR / "index.json"
MAX_CACHE_SIZE_MB = 500


# ═══════════════════════════════════════════════════════════════
# CACHE MANAGER
# ═══════════════════════════════════════════════════════════════

class AssetCache:
    """Caché de assets con hashing MD5."""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Cargar índice del caché."""
        if CACHE_INDEX.exists():
            try:
                with open(CACHE_INDEX, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_index(self):
        """Guardar índice del caché."""
        with open(CACHE_INDEX, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _compute_hash(self, data: bytes) -> str:
        """Calcular hash MD5."""
        return hashlib.md5(data).hexdigest()
    
    def get(self, key: str) -> Optional[Path]:
        """
        Obtener asset del caché.
        
        Args:
            key: Clave del asset (URL o nombre)
        
        Returns:
            Path al archivo cacheado o None
        """
        if key in self.index:
            entry = self.index[key]
            cached_path = Path(entry["path"])
            if cached_path.exists():
                return cached_path
            else:
                # File was deleted, remove from index
                del self.index[key]
                self._save_index()
        
        return None
    
    def put(self, key: str, data: bytes, extension: str = ".bin") -> Path:
        """
        Guardar asset en caché.
        
        Args:
            key: Clave del asset
            data: Datos del asset
            extension: Extensión del archivo
        
        Returns:
            Path al archivo cacheado
        """
        file_hash = self._compute_hash(data)
        filename = f"{file_hash}{extension}"
        filepath = self.cache_dir / filename
        
        # Write file
        with open(filepath, 'wb') as f:
            f.write(data)
        
        # Update index
        self.index[key] = {
            "path": str(filepath),
            "hash": file_hash,
            "size": len(data),
            "timestamp": time.time(),
        }
        self._save_index()
        
        return filepath
    
    def has(self, key: str) -> bool:
        """Verificar si un asset está en caché."""
        return key in self.index and Path(self.index[key]["path"]).exists()
    
    def remove(self, key: str) -> bool:
        """Eliminar asset del caché."""
        if key in self.index:
            filepath = Path(self.index[key]["path"])
            if filepath.exists():
                filepath.unlink()
            del self.index[key]
            self._save_index()
            return True
        return False
    
    def clear(self):
        """Limpiar todo el caché."""
        for entry in self.index.values():
            filepath = Path(entry["path"])
            if filepath.exists():
                filepath.unlink()
        self.index.clear()
        self._save_index()
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del caché."""
        total_size = sum(entry["size"] for entry in self.index.values())
        return {
            "total_assets": len(self.index),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "max_size_mb": MAX_CACHE_SIZE_MB,
            "cache_dir": str(self.cache_dir),
        }
    
    def cleanup_old(self, max_age_days: int = 30):
        """Limpiar assets antiguos."""
        cutoff = time.time() - (max_age_days * 86400)
        to_remove = []
        
        for key, entry in self.index.items():
            if entry["timestamp"] < cutoff:
                to_remove.append(key)
        
        for key in to_remove:
            self.remove(key)


# ═══════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL
# ═══════════════════════════════════════════════════════════════

asset_cache = AssetCache()


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE CONVENIENCIA
# ═══════════════════════════════════════════════════════════════

def cache_asset(url: str, data: bytes, extension: str = ".bin") -> Path:
    """Cache an asset from URL."""
    return asset_cache.put(url, data, extension)


def get_cached_asset(url: str) -> Optional[Path]:
    """Get a cached asset by URL."""
    return asset_cache.get(url)


def is_cached(url: str) -> bool:
    """Check if asset is cached."""
    return asset_cache.has(url)


def get_cache_stats() -> Dict:
    """Get cache statistics."""
    return asset_cache.get_stats()
