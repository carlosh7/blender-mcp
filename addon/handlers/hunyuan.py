"""
blender-mcp — Hunyuan3D Handler
Real integration: 3D model generation via Tencent Hunyuan3D (Official API or Local API)
"""
import bpy
import json
import os
import tempfile
import urllib.request
import hashlib
import hmac
import base64
import time
import shutil
from datetime import datetime


def _config():
    scene = bpy.context.scene
    mode = scene.blendermcp_hunyuan3d_mode
    return mode


def _official_config():
    scene = bpy.context.scene
    return {
        "secret_id": scene.blendermcp_hunyuan3d_secret_id,
        "secret_key": scene.blendermcp_hunyuan3d_secret_key,
    }


def _local_config():
    scene = bpy.context.scene
    return {
        "url": scene.blendermcp_hunyuan3d_api_url,
        "octree": scene.blendermcp_hunyuan3d_octree_resolution,
        "steps": scene.blendermcp_hunyuan3d_num_inference_steps,
        "guidance": scene.blendermcp_hunyuan3d_guidance_scale,
        "texture": scene.blendermcp_hunyuan3d_texture,
    }


def cmd_get_hunyuan3d_status():
    """Check Hunyuan3D status."""
    enabled = getattr(bpy.context.scene, "blendermcp_use_hunyuan3d", False)
    mode = _config()
    if not enabled:
        return {"enabled": False, "message": "Enable Hunyuan3D in Integrations panel"}
    if mode == "OFFICIAL_API":
        cfg = _official_config()
        if not cfg["secret_id"] or not cfg["secret_key"]:
            return {"enabled": False, "message": "Set SecretId and SecretKey for Hunyuan3D Official API"}
        return {"enabled": True, "mode": "OFFICIAL_API", "message": "Hunyuan3D Official API ready"}
    else:
        return {"enabled": True, "mode": "LOCAL_API", "message": "Hunyuan3D Local API ready"}


def _sign(secret_key, service, action, timestamp):
    """Generate Tencent Cloud API signature."""
    date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
    payload = f'{{"Action":"{action}","Version":"2023-12-30","Timestamp":{timestamp}}}'
    sign_str = f"POST\n/\n\ncontent-type:application/json\nhost={service}.tencentcloudapi.com\n\n{payload}"
    secret_date = hmac.new(secret_key.encode(), date.encode(), hashlib.sha256).digest()
    secret_service = hmac.new(secret_date, service.encode(), hashlib.sha256).digest()
    signature = hmac.new(secret_service, "tc3_request".encode(), hashlib.sha256).digest()
    sign_result = hmac.new(signature, sign_str.encode(), hashlib.sha256).digest()
    return base64.b64encode(sign_result).decode()


def _call_official(action, payload):
    cfg = _official_config()
    ts = int(time.time())
    service = "hunyuan3d"
    signature = _sign(cfg["secret_key"], service, action, ts)

    url = f"https://{service}.tencentcloudapi.com"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"TC3-HMAC-SHA256 Credential={cfg['secret_id']}/{datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')}/{service}/tc3_request, SignedHeaders=content-type;host, Signature={signature}",
        "X-TC-Action": action,
        "X-TC-Timestamp": str(ts),
        "X-TC-Version": "2023-12-30",
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def _call_local(endpoint, payload):
    cfg = _local_config()
    url = f"{cfg['url'].rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json", "User-Agent": "blender-mcp/0.8"}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def cmd_create_hunyuan_job(text_prompt="", image=""):
    """Create a Hunyuan3D generation job from text or image."""
    mode = _config()
    if mode == "OFFICIAL_API":
        payload = {}
        if text_prompt:
            payload["Prompt"] = text_prompt
        if image:
            payload["InputImage"] = image
        result = _call_official("SubmitJob", payload)
        return {"Response": result.get("Response", {})}
    else:
        payload = {
            "octree_resolution": _local_config()["octree"],
            "num_inference_steps": _local_config()["steps"],
            "guidance_scale": _local_config()["guidance"],
            "generate_texture": _local_config()["texture"],
        }
        if text_prompt:
            payload["text_prompt"] = text_prompt
        if image:
            payload["input_image"] = image
        result = _call_local("generate", payload)
        return {"job_id": result.get("job_id", "")}


def cmd_poll_hunyuan_job(job_id=""):
    """Poll Hunyuan3D job status."""
    mode = _config()
    if mode == "OFFICIAL_API":
        payload = {"JobId": job_id.replace("job_", "")}
        result = _call_official("QueryJob", payload)
        return result.get("Response", {})
    else:
        result = _call_local("status", {"job_id": job_id})
        return result


def cmd_import_hunyuan_asset(name="", zip_file_url=""):
    """Import Hunyuan3D generated model."""
    if not zip_file_url:
        return {"error": "No zip_file_url provided"}

    tmp_dir = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(tmp_dir, "model.zip")
        req = urllib.request.Request(zip_file_url, headers={"User-Agent": "blender-mcp/0.8"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as f:
                f.write(resp.read())

        import zipfile
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        # Find OBJ file
        obj_path = None
        for root, _dirs, files in os.walk(tmp_dir):
            for f in files:
                if f.endswith(".obj"):
                    obj_path = os.path.join(root, f)
                    break
            if obj_path:
                break

        if not obj_path:
            return {"error": "No OBJ file in Hunyuan3D output"}

        before = set(bpy.data.objects.keys())
        bpy.ops.import_scene.obj(filepath=obj_path)
        imported = [o for o in bpy.data.objects if o.name not in before]

        if imported and name:
            imported[0].name = name

        return {
            "success": True,
            "imported_objects": [o.name for o in imported],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
