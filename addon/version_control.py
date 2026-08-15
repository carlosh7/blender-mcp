"""
blender-mcp — Version Control
Control de versiones de escenas Blender.
"""
import bpy
import json
import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# VERSION CONTROL CONFIG
# ═══════════════════════════════════════════════════════════════

VERSION_DIR = Path("/tmp/blender_mcp_versions")
VERSION_INDEX = VERSION_DIR / "versions.json"


# ═══════════════════════════════════════════════════════════════
# VERSION CONTROL
# ═══════════════════════════════════════════════════════════════

class VersionControl:
    """Control de versiones para escenas Blender."""
    
    def __init__(self, version_dir: Path = VERSION_DIR):
        self.version_dir = version_dir
        self.version_dir.mkdir(parents=True, exist_ok=True)
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Cargar índice de versiones."""
        if VERSION_INDEX.exists():
            try:
                with open(VERSION_INDEX, 'r') as f:
                    return json.load(f)
            except Exception:
                return {"versions": []}
        return {"versions": []}
    
    def _save_index(self):
        """Guardar índice de versiones."""
        with open(VERSION_INDEX, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def create_version(self, label: Optional[str] = None) -> str:
        """
        Crear nueva versión de la escena actual.
        
        Args:
            label: Etiqueta descriptiva (opcional)
        
        Returns:
            ID de la versión
        """
        version_id = f"v{int(time.time())}"
        version_path = self.version_dir / f"{version_id}.blend"
        
        # Save current scene
        try:
            bpy.ops.wm.save_as_mainfile(filepath=str(version_path))
        except Exception as e:
            print(f"[version] Save failed: {e}")
            return ""
        
        # Calculate hash
        file_hash = self._compute_hash(version_path)
        
        # Add to index
        version_entry = {
            "id": version_id,
            "path": str(version_path),
            "hash": file_hash,
            "label": label or f"Version {len(self.index['versions']) + 1}",
            "timestamp": datetime.now().isoformat(),
            "object_count": len(bpy.data.objects),
            "description": self._get_scene_summary(),
        }
        
        self.index["versions"].append(version_entry)
        self._save_index()
        
        print(f"[version] Version created: {version_id}")
        return version_id
    
    def restore_version(self, version_id: str) -> bool:
        """
        Restaurar una versión específica.
        
        Args:
            version_id: ID de la versión
        
        Returns:
            True si éxito
        """
        for version in self.index["versions"]:
            if version["id"] == version_id:
                version_path = Path(version["path"])
                if version_path.exists():
                    try:
                        bpy.ops.wm.open_mainfile(filepath=str(version_path))
                        print(f"[version] Restored: {version_id}")
                        return True
                    except Exception as e:
                        print(f"[version] Restore failed: {e}")
                        return False
        return False
    
    def list_versions(self) -> List[Dict]:
        """Listar todas las versiones."""
        return [
            {
                "id": v["id"],
                "label": v["label"],
                "timestamp": v["timestamp"],
                "object_count": v["object_count"],
            }
            for v in self.index["versions"]
        ]
    
    def get_version_info(self, version_id: str) -> Optional[Dict]:
        """Obtener información de una versión."""
        for version in self.index["versions"]:
            if version["id"] == version_id:
                return version
        return None
    
    def delete_version(self, version_id: str) -> bool:
        """Eliminar una versión."""
        for i, version in enumerate(self.index["versions"]):
            if version["id"] == version_id:
                # Delete file
                version_path = Path(version["path"])
                if version_path.exists():
                    version_path.unlink()
                
                # Remove from index
                self.index["versions"].pop(i)
                self._save_index()
                return True
        return False
    
    def compare_versions(self, v1_id: str, v2_id: str) -> Dict:
        """
        Comparar dos versiones.
        
        Args:
            v1_id: ID de la primera versión
            v2_id: ID de la segunda versión
        
        Returns:
            Dict con diferencias
        """
        v1 = self.get_version_info(v1_id)
        v2 = self.get_version_info(v2_id)
        
        if not v1 or not v2:
            return {"error": "Version not found"}
        
        return {
            "v1": {
                "id": v1["id"],
                "label": v1["label"],
                "object_count": v1["object_count"],
                "timestamp": v1["timestamp"],
            },
            "v2": {
                "id": v2["id"],
                "label": v2["label"],
                "object_count": v2["object_count"],
                "timestamp": v2["timestamp"],
            },
            "object_diff": v2["object_count"] - v1["object_count"],
            "same_hash": v1["hash"] == v2["hash"],
        }
    
    def _compute_hash(self, filepath: Path) -> str:
        """Calcular hash MD5 de un archivo."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_scene_summary(self) -> str:
        """Obtener resumen de la escena actual."""
        objects = len(bpy.data.objects)
        meshes = len(bpy.data.meshes)
        materials = len(bpy.data.materials)
        return f"Objects: {objects}, Meshes: {meshes}, Materials: {materials}"


# ═══════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL
# ═══════════════════════════════════════════════════════════════

import time
version_control = VersionControl()


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def create_snapshot(label: Optional[str] = None) -> str:
    """Crear snapshot de la escena actual."""
    return version_control.create_version(label)


def restore_snapshot(version_id: str) -> bool:
    """Restaurar un snapshot."""
    return version_control.restore_version(version_id)


def list_snapshots() -> List[Dict]:
    """Listar todos los snapshots."""
    return version_control.list_versions()
