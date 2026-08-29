"""
blender-mcp-ultra — Sketchfab Asset Integration
"""

import json
import os
import tempfile
import urllib.request
from typing import Any


class Sketchfab:
    """Sketchfab asset integration."""

    BASE_URL = "https://api.sketchfab.com/v3"

    def __init__(self, api_key: str = None, cache_dir: str = None):
        self.api_key = api_key or os.environ.get("SKETCHFAB_API_KEY", "")
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "sketchfab_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search Sketchfab models."""
        try:
            url = f"{self.BASE_URL}/search?type=models&q={query}&count={limit}"
            headers = {"User-Agent": "blender-mcp-ultra"}
            if self.api_key:
                headers["Authorization"] = f"Token {self.api_key}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                models = []
                for result in data.get("results", []):
                    models.append(
                        {
                            "uid": result.get("uid"),
                            "name": result.get("name"),
                            "author": result.get("user", {}).get("displayName"),
                            "downloadable": result.get("isDownloadable", False),
                        }
                    )
                return {"success": True, "count": len(models), "models": models}
        except Exception as e:
            return {"error": str(e)}

    def get_model(self, model_uid: str) -> dict[str, Any]:
        """Get model details."""
        try:
            url = f"{self.BASE_URL}/models/{model_uid}"
            headers = {"User-Agent": "blender-mcp-ultra"}
            if self.api_key:
                headers["Authorization"] = f"Token {self.api_key}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return {"success": True, "model": data}
        except Exception as e:
            return {"error": str(e)}

    def download(self, model_uid: str, format: str = "gltf") -> dict[str, Any]:
        """Download a model."""
        if not self.api_key:
            return {"error": "API key required for download"}

        try:
            url = f"{self.BASE_URL}/models/{model_uid}/download"
            headers = {
                "User-Agent": "blender-mcp-ultra",
                "Authorization": f"Token {self.api_key}",
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                if data.get("status") == "success":
                    download_url = data.get("gltf", {}).get("url")
                    if download_url:
                        filepath = os.path.join(self.cache_dir, f"{model_uid}.glb")
                        urllib.request.urlretrieve(download_url, filepath)
                        return {"success": True, "filepath": filepath}
                return {"error": "Download failed", "status": data.get("status")}
        except Exception as e:
            return {"error": str(e)}
