"""
blender-mcp — Poly Haven Handler
Real integration: search, download HDRI/textures/models via api.polyhaven.com
"""
import bpy
import json
import os
import tempfile
import shutil
import urllib.request
import traceback
from pathlib import Path

REQ_HEADERS = {"User-Agent": "blender-mcp/0.8"}


def _api_get(path):
    url = f"https://api.polyhaven.com/{path}"
    req = urllib.request.Request(url, headers=REQ_HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _download_file(url, dest):
    req = urllib.request.Request(url, headers=REQ_HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        with open(dest, "wb") as f:
            f.write(resp.read())


def cmd_search_polyhaven(asset_type="all", query="", limit=20):
    """Search Poly Haven assets. Types: hdris, textures, models, all."""
    if asset_type and asset_type != "all":
        data = _api_get(f"assets?type={asset_type}")
    else:
        data = _api_get("assets")
    results = []
    for i, (aid, info) in enumerate(data.items()):
        if query and query.lower() not in aid.lower():
            continue
        if i >= limit:
            break
        results.append({
            "id": aid,
            "type": info.get("type", asset_type),
            "categories": list(info.get("categories", {}).keys()),
        })
    return {"results": results, "total": len(results)}


def cmd_get_polyhaven_categories(asset_type="hdris"):
    """Get available categories for an asset type."""
    data = _api_get(f"categories/{asset_type}")
    return {"categories": data}


def cmd_download_polyhaven_hdri(asset_id="", resolution="1k"):
    """Download and set HDRI as world environment."""
    files_data = _api_get(f"files/{asset_id}")
    hdri = files_data.get("hdri", {})
    res = hdri.get(resolution, hdri.get("1k", {}))
    hdr_info = res.get("hdr", res.get("exr"))
    if not hdr_info:
        return {"error": f"No HDRI file found for {asset_id} at {resolution}"}

    url = hdr_info["url"]
    ext = "hdr" if "hdr" in res else "exr"
    tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False).name
    try:
        _download_file(url, tmp)
        # Set up world with HDRI
        if not bpy.data.worlds:
            bpy.data.worlds.new("World")
        world = bpy.data.worlds[0]
        world.use_nodes = True
        tree = world.node_tree
        for node in list(tree.nodes):
            tree.nodes.remove(node)

        tex_coord = tree.nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)
        mapping = tree.nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 0)
        env_tex = tree.nodes.new(type='ShaderNodeTexEnvironment')
        env_tex.location = (-400, 0)
        env_tex.image = bpy.data.images.load(tmp)
        try:
            env_tex.image.colorspace_settings.name = 'Linear'
        except:
            pass
        background = tree.nodes.new(type='ShaderNodeBackground')
        background.location = (-200, 0)
        output = tree.nodes.new(type='ShaderNodeOutputWorld')
        output.location = (0, 0)

        tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        tree.links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
        tree.links.new(env_tex.outputs['Color'], background.inputs['Color'])
        tree.links.new(background.outputs['Background'], output.inputs['Surface'])
        bpy.context.scene.world = world

        return {"success": True, "message": f"HDRI {asset_id} loaded", "image": env_tex.image.name}
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.unlink(tmp)
        except:
            pass


def cmd_download_polyhaven_texture(asset_id="", resolution="1k"):
    """Download Poly Haven textures and create a PBR material."""
    files_data = _api_get(f"files/{asset_id}")
    downloaded = {}
    tmp_files = []

    try:
        for map_type, map_data in files_data.items():
            if map_type in ("blend", "gltf"):
                continue
            res = map_data.get(resolution, map_data.get("1k", {}))
            for fmt in ("jpg", "png", "exr"):
                info = res.get(fmt)
                if info:
                    break
            if not info:
                continue
            ext = fmt
            url = info["url"]
            tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False).name
            _download_file(url, tmp)
            tmp_files.append(tmp)
            img = bpy.data.images.load(tmp)
            img.name = f"{asset_id}_{map_type}.{ext}"
            img.pack()
            cs = 'sRGB' if map_type in ('color', 'diffuse', 'albedo') else 'Non-Color'
            try:
                img.colorspace_settings.name = cs
            except:
                pass
            downloaded[map_type] = img

        if not downloaded:
            return {"error": "No texture maps downloaded"}

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
        for map_type, img in downloaded.items():
            tex = nodes.new(type='ShaderNodeTexImage')
            tex.location = (x, y)
            tex.image = img
            links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
            mt = map_type.lower()
            if mt in ('color', 'diffuse', 'albedo'):
                links.new(tex.outputs['Color'], principled.inputs['Base Color'])
            elif mt in ('roughness', 'rough'):
                links.new(tex.outputs['Color'], principled.inputs['Roughness'])
            elif mt in ('metallic', 'metalness', 'metal'):
                links.new(tex.outputs['Color'], principled.inputs['Metallic'])
            elif mt in ('normal', 'nor', 'gl', 'dx'):
                nm = nodes.new(type='ShaderNodeNormalMap')
                nm.location = (x + 200, y)
                links.new(tex.outputs['Color'], nm.inputs['Color'])
                links.new(nm.outputs['Normal'], principled.inputs['Normal'])
            elif mt in ('displacement', 'disp', 'height'):
                disp = nodes.new(type='ShaderNodeDisplacement')
                disp.location = (x + 200, y - 200)
                disp.inputs['Scale'].default_value = 0.1
                links.new(tex.outputs['Color'], disp.inputs['Height'])
                links.new(disp.outputs['Displacement'], output.inputs['Displacement'])
            y -= 250

        return {
            "success": True,
            "message": f"Material {asset_id} created",
            "material": mat.name,
            "maps": list(downloaded.keys()),
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        for tmp in tmp_files:
            try:
                os.unlink(tmp)
            except:
                pass


def cmd_download_polyhaven_model(asset_id="", resolution="1k"):
    """Download Poly Haven 3D model (glTF) and import."""
    files_data = _api_get(f"files/{asset_id}")
    for fmt in ("gltf", "glb", "fbx", "obj"):
        info = files_data.get(fmt, {}).get(resolution, {}).get(fmt)
        if info:
            break
    if not info:
        return {"error": f"No model file for {asset_id}"}

    url = info["url"]
    tmp_dir = tempfile.mkdtemp()
    try:
        main_name = url.split("/")[-1]
        main_path = os.path.join(tmp_dir, main_name)
        _download_file(url, main_path)

        # Download includes
        inc = info.get("include", {})
        for rel_path, inc_info in inc.items():
            inc_url = inc_info["url"]
            inc_dest = os.path.join(tmp_dir, rel_path)
            os.makedirs(os.path.dirname(inc_dest), exist_ok=True)
            _download_file(inc_url, inc_dest)

        fmt_used = fmt
        if fmt_used == "gltf":
            bpy.ops.import_scene.gltf(filepath=main_path)
        elif fmt_used == "fbx":
            bpy.ops.import_scene.fbx(filepath=main_path)
        elif fmt_used == "obj":
            bpy.ops.import_scene.obj(filepath=main_path)
        else:
            return {"error": f"Unsupported format: {fmt_used}"}

        imported = [o.name for o in bpy.context.selected_objects]
        return {"success": True, "message": f"Model {asset_id} imported", "imported_objects": imported}
    except Exception as e:
        return {"error": str(e)}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def cmd_get_polyhaven_status():
    """Check if Poly Haven is enabled in scene."""
    enabled = getattr(bpy.context.scene, "blendermcp_use_polyhaven", False)
    return {
        "enabled": enabled,
        "message": "Poly Haven ready" if enabled else "Enable Poly Haven in Integrations panel",
    }
