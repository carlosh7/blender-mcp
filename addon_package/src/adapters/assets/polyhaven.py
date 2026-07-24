"""
blender-mcp-ultra — Poly Haven Asset Integration
"""
import json
import os
import urllib.request
import tempfile
from typing import Any, Dict, Optional


class PolyHaven:
    """Poly Haven asset integration."""
    
    BASE_URL = "https://api.polyhaven.com"
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "polyhaven_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def search(self, query: str, asset_type: str = "hdris", limit: int = 10) -> Dict[str, Any]:
        """Search Poly Haven assets."""
        try:
            url = f"{self.BASE_URL}/assets?t={asset_type}&q={query}&per_page={limit}"
            req = urllib.request.Request(url, headers={"User-Agent": "blender-mcp-ultra"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return {"success": True, "count": len(data), "assets": data}
        except Exception as e:
            return {"error": str(e)}
    
    def get_asset(self, asset_name: str, asset_type: str = "hdris", resolution: str = "2k") -> Dict[str, Any]:
        """Get asset details."""
        try:
            url = f"{self.BASE_URL}/assets/{asset_name}"
            req = urllib.request.Request(url, headers={"User-Agent": "blender-mcp-ultra"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return {"success": True, "asset": data}
        except Exception as e:
            return {"error": str(e)}
    
    def download(self, asset_name: str, asset_type: str = "hdris", resolution: str = "2k") -> Dict[str, Any]:
        """Download an asset."""
        try:
            url = f"{self.BASE_URL}/assets/{asset_name}/{resolution}"
            req = urllib.request.Request(url, headers={"User-Agent": "blender-mcp-ultra"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                file_urls = data.get("hdri", data.get("diffuse", data.get("normal", {})))
                if file_urls:
                    for key, file_url in file_urls.items():
                        filepath = os.path.join(self.cache_dir, f"{asset_name}_{resolution}_{key}.exr")
                        urllib.request.urlretrieve(file_url, filepath)
                        return {"success": True, "filepath": filepath, "name": asset_name}
                return {"error": "No download URL found"}
        except Exception as e:
            return {"error": str(e)}
    
    def list_categories(self) -> Dict[str, Any]:
        """List available categories."""
        return {"categories": ["hdris", "textures", "models"]}
    
    def list_resolutions(self) -> Dict[str, Any]:
        """List available resolutions."""
        return {"resolutions": ["1k", "2k", "4k", "8k"]}
