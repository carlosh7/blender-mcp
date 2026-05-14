"""
blender-mcp — AmbientCG Handler
Real integration: search/download PBR materials via ambientcg.com API (free, no key needed)
"""
import bpy
import json
import os
import tempfile
import urllib.request
import shutil


def _api_get(path):
    url = f"https://ambientcg.com/api/v2/{path}"
    headers = {"User-Agent": "blender-mcp/0.8"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def cmd_search_ambientcg(query="", limit=20, categories=""):
    """Search AmbientCG PBR materials."""
    params = f"?limit={limit}"
    if query:
        params += f"&q={urllib.request.quote(query)}"
    if categories:
        params += f"&categories={categories}"
    data = _api_get(f"files_json{params}")
    results = []
    for item in data.get("foundAssets", {}).values():
        results.append({
            "id": item.get("assetId", ""),
            "name": item.get("displayName", ""),
            "categories": item.get("categories", []),
            "tags": item.get("tags", []),
            "download_count": item.get("downloadCount", 0),
        })
    return {"results": results, "total": len(results)}


def cmd_get_ambientcg_categories():
    """Get AmbientCG categories."""
    data = _api_get("categories")
    return {"categories": list(data.keys()) if isinstance(data, dict) else data}


def cmd_download_ambientcg_material(asset_id="", resolution="1K"):
    """Download an AmbientCG PBR material and create Blender material."""
    file_info = _api_get(f"files_json?assetId={asset_id}")
    asset = file_info.get("foundAssets", {}).get(asset_id, {})
    if not asset:
        return {"error": f"Asset {asset_id} not found"}

    # Find the download URL
    downloads = asset.get("fileDownload", {}).get("downloadFolders", {})
    res_key = resolution.upper()
    folder = downloads.get(res_key, downloads.get("2K", downloads.get("1K")))
    if not folder:
        return {"error": f"Resolution {resolution} not available"}

    dl_url = folder.get("fileDownloadUrl", "")
    if not dl_url:
        return {"error": "No download URL"}

    tmp_dir = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(tmp_dir, "material.zip")
        req = urllib.request.Request(dl_url, headers={"User-Agent": "blender-mcp/0.8"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as f:
                f.write(resp.read())

        import zipfile
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        # Find image files
        images = {}
        for root, _dirs, files in os.walk(tmp_dir):
            for f in files:
                f_lower = f.lower()
                for map_type in ("color", "albedo", "diffuse", "roughness", "normal", "displacement", "ao", "metallic", "height"):
                    if map_type in f_lower and f.endswith((".jpg", ".png", ".exr", ".tif")):
                        images[map_type] = os.path.join(root, f)

        if not images:
            return {"error": "No texture maps found in downloaded material"}

        mat = bpy.data.materials.new(name=asset_id)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled.location = (0, 0)
        links.new(principled.outputs[0], output.inputs[0])

        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 0)
        mapping.vector_type = 'TEXTURE'
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

        x, y = -400, 300
        for map_type, filepath in images.items():
            img = bpy.data.images.load(filepath)
            img.name = f"{asset_id}_{map_type}"
            img.pack()
            cs = 'sRGB' if map_type in ('color', 'albedo', 'diffuse') else 'Non-Color'
            try:
                img.colorspace_settings.name = cs
            except:
                pass
            tex = nodes.new(type='ShaderNodeTexImage')
            tex.location = (x, y)
            tex.image = img
            links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
            mt = map_type.lower()
            if mt in ('color', 'albedo', 'diffuse'):
                links.new(tex.outputs['Color'], principled.inputs['Base Color'])
            elif mt in ('roughness',):
                links.new(tex.outputs['Color'], principled.inputs['Roughness'])
            elif mt in ('metallic',):
                links.new(tex.outputs['Color'], principled.inputs['Metallic'])
            elif mt in ('normal',):
                nm = nodes.new(type='ShaderNodeNormalMap')
                nm.location = (x + 200, y)
                links.new(tex.outputs['Color'], nm.inputs['Color'])
                links.new(nm.outputs['Normal'], principled.inputs['Normal'])
            elif mt in ('displacement', 'height'):
                disp = nodes.new(type='ShaderNodeDisplacement')
                disp.location = (x + 200, y - 200)
                links.new(tex.outputs['Color'], disp.inputs['Height'])
                links.new(disp.outputs['Displacement'], output.inputs['Displacement'])
            y -= 250

        return {
            "success": True,
            "material": mat.name,
            "maps": list(images.keys()),
            "message": f"PBR material {asset_id} created",
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
