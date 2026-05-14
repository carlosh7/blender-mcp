"""
blender-mcp — Hyper3D Rodin Handler
Real integration: AI 3D model generation via hyper3d.ai (MAIN_SITE) or fal.ai (FAL_AI)
"""
import bpy
import json
import os
import tempfile
import urllib.request
import time
import shutil


RODIN_FREE_TRIAL_KEY = "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"


def _config():
    scene = bpy.context.scene
    api_key = scene.blendermcp_hyper3d_api_key or RODIN_FREE_TRIAL_KEY
    mode = scene.blendermcp_hyper3d_mode
    return api_key, mode


def cmd_get_hyper3d_status():
    """Check Hyper3D Rodin status."""
    enabled = getattr(bpy.context.scene, "blendermcp_use_hyper3d", False)
    api_key, mode = _config()
    if enabled:
        is_trial = api_key == RODIN_FREE_TRIAL_KEY
        return {
            "enabled": True,
            "mode": mode,
            "key_type": "free_trial" if is_trial else "private",
            "message": f"Hyper3D Rodin ready ({mode})" if not is_trial else "Hyper3D Rodin ready (free trial, limited daily)",
        }
    return {"enabled": False, "message": "Enable Hyper3D Rodin in Integrations panel"}


def _call_main_site(api_key, endpoint, payload):
    url = f"https://hyper3d.xyz/api/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "blender-mcp/0.8",
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def _call_fal_ai(api_key, endpoint, payload):
    url = f"https://fal.ai/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Key {api_key}",
        "User-Agent": "blender-mcp/0.8",
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def _process_bbox(bbox):
    if bbox is None:
        return None
    if any(i <= 0 for i in bbox):
        return None
    if all(isinstance(i, int) for i in bbox):
        return bbox
    m = max(bbox)
    return [int(float(i) / m * 100) for i in bbox]


def cmd_create_rodin_job(text_prompt="", images=None, bbox_condition=None):
    """Create a Hyper3D Rodin generation job."""
    api_key, mode = _config()
    payload = {
        "text_prompt": text_prompt or None,
        "images": images,
        "bbox_condition": _process_bbox(bbox_condition),
    }

    if mode == "MAIN_SITE":
        result = _call_main_site(api_key, "submit", payload)
        return {
            "uuid": result.get("uuid", ""),
            "jobs": result.get("jobs", {}),
            "submit_time": result.get("submit_time", 0),
        }
    else:  # FAL_AI
        result = _call_fal_ai(api_key, "hyper3d/rodin/v1/generation", payload)
        return {
            "request_id": result.get("request_id", ""),
        }


def cmd_poll_rodin_job(subscription_key="", request_id=""):
    """Poll Hyper3D Rodin job status."""
    api_key, mode = _config()
    if mode == "MAIN_SITE":
        payload = {"subscription_key": subscription_key}
        return _call_main_site(api_key, "status", payload)
    else:
        url = f"https://fal.ai/hyper3d/rodin/v1/generation/status?request_id={request_id}"
        headers = {
            "Authorization": f"Key {api_key}",
            "User-Agent": "blender-mcp/0.8",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())


def cmd_import_generated_asset(name="", task_uuid="", request_id=""):
    """Import a generated model into Blender."""
    api_key, mode = _config()
    if mode == "MAIN_SITE":
        payload = {"task_uuid": task_uuid}
        result = _call_main_site(api_key, "retrieve", payload)
        model_url = result.get("model_urls", {}).get("glb", "")
    else:
        url = f"https://fal.ai/hyper3d/rodin/v1/generation/result?request_id={request_id}"
        headers = {
            "Authorization": f"Key {api_key}",
            "User-Agent": "blender-mcp/0.8",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        model_url = result.get("model_urls", {}).get("glb", "")

    if not model_url:
        return {"error": "No GLB URL in result"}

    tmp = tempfile.NamedTemporaryFile(suffix=".glb", delete=False).name
    try:
        req = urllib.request.Request(model_url, headers={"User-Agent": "blender-mcp/0.8"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(tmp, "wb") as f:
                f.write(resp.read())

        before = set(bpy.data.objects.keys())
        bpy.ops.import_scene.gltf(filepath=tmp)
        imported = [o for o in bpy.data.objects if o.name not in before]

        if imported and name:
            imported[0].name = name

        return {
            "success": True,
            "imported_objects": [o.name for o in imported],
            "message": f"Generated model imported ({len(imported)} objects)",
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.unlink(tmp)
        except:
            pass
