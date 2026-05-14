"""
blender-mcp — Sketchfab Handler
Real integration: search + preview + download models via api.sketchfab.com/v3
"""
import bpy
import json
import os
import tempfile
import shutil
import urllib.request
import base64


def _api_key():
    return getattr(bpy.context.scene, "blendermcp_sketchfab_api_key", "")


def _api_get(path, params=None):
    key = _api_key()
    if not key:
        return {"error": "Sketchfab API key not set"}
    url = f"https://api.sketchfab.com/v3/{path}"
    if params:
        import urllib.parse
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Authorization": f"Token {key}", "User-Agent": "blender-mcp/0.8"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def cmd_search_sketchfab(query="", count=20, downloadable=True):
    """Search Sketchfab models."""
    params = {
        "type": "models",
        "q": query,
        "count": min(count, 100),
        "downloadable": str(downloadable).lower(),
    }
    data = _api_get("search", params)
    if "error" in data:
        return data
    results = []
    for model in data.get("results", []):
        results.append({
            "uid": model.get("uid", ""),
            "name": model.get("name", "Unnamed"),
            "author": (model.get("user") or {}).get("username", "Unknown"),
            "face_count": model.get("faceCount", "Unknown"),
            "downloadable": model.get("isDownloadable", False),
            "license": (model.get("license") or {}).get("label", "Unknown"),
        })
    return {"results": results, "total": len(results)}


def cmd_get_sketchfab_preview(uid=""):
    """Get preview thumbnail of a Sketchfab model."""
    data = _api_get(f"models/{uid}")
    if "error" in data:
        return data
    thumbnails = data.get("thumbnails", {}).get("images", [])
    thumb_url = thumbnails[-1]["url"] if thumbnails else None
    if not thumb_url:
        return {"error": "No thumbnail available"}

    req = urllib.request.Request(thumb_url, headers={"User-Agent": "blender-mcp/0.8"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        img_data = resp.read()

    return {
        "image_data": base64.b64encode(img_data).decode(),
        "format": "jpeg",
        "model_name": data.get("name", ""),
        "author": (data.get("user") or {}).get("username", ""),
    }


def cmd_download_sketchfab_model(uid="", target_size=1.0):
    """Download and import a Sketchfab model by UID."""
    data = _api_get(f"models/{uid}")
    if "error" in data:
        return data

    # Find downloadable archive
    download_url = None
    archives = data.get("archives", {}).get("gltf", {})
    if archives:
        download_url = archives.get("url")
    if not download_url:
        archives2 = _api_get(f"models/{uid}/download")
        if isinstance(archives2, dict):
            gltf = archives2.get("gltf", {})
            download_url = gltf.get("url")

    if not download_url:
        return {"error": "No downloadable model available"}

    tmp_dir = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(tmp_dir, "model.zip")
        req = urllib.request.Request(download_url, headers={"User-Agent": "blender-mcp/0.8"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as f:
                f.write(resp.read())

        # Extract and find glTF
        import zipfile
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        gltf_path = None
        for root, _dirs, files in os.walk(tmp_dir):
            for f in files:
                if f.endswith(".gltf") or f.endswith(".glb"):
                    gltf_path = os.path.join(root, f)
                    break
            if gltf_path:
                break

        if not gltf_path:
            return {"error": "No glTF file found in downloaded archive"}

        # Count objects before import
        before = set(bpy.data.objects.keys())
        bpy.ops.import_scene.gltf(filepath=gltf_path)
        imported = [o.name for o in bpy.data.objects if o.name not in before]

        # Scale to target size
        if imported:
            obj = bpy.data.objects.get(imported[0])
            if obj:
                dims = obj.dimensions
                max_dim = max(dims)
                if max_dim > 0:
                    scale = target_size / max_dim
                    obj.scale = (scale, scale, scale)
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    bpy.ops.object.transform_apply(scale=True)

        return {
            "success": True,
            "imported_objects": imported,
            "message": f"Model imported with {len(imported)} objects",
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def cmd_get_sketchfab_status():
    """Check if Sketchfab is configured."""
    key = _api_key()
    enabled = getattr(bpy.context.scene, "blendermcp_use_sketchfab", False)
    if enabled and key:
        return {"enabled": True, "message": "Sketchfab ready"}
    elif enabled and not key:
        return {"enabled": False, "message": "Set Sketchfab API Key in Integrations panel"}
    return {"enabled": False, "message": "Enable Sketchfab in Integrations panel"}
