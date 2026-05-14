import os
import sys
import platform
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve() / "src"))

from blender_mcp.platform import get_opencode_config_paths, get_opencode_auth_path, find_blender as _find_platform, SYSTEM

# ─── Paths ───
PLANNER_MODELS_DIR = Path.home() / "check-3d-planner" / "public" / "models"
MODELS_DIR = Path(__file__).parent.resolve() / "models"

# ─── Cross-platform opencode config paths ───
OPENCODE_CONFIG_PATHS = get_opencode_config_paths()

# API config per provider for fetching live model lists
PROVIDER_API_CONFIG = {
    "deepseek": {
        "url": "https://api.deepseek.com/v1/models",
        "auth": True,
        "name": "DeepSeek",
    },
    "opencode-go": {
        "url": "https://opencode.ai/zen/go/v1/models",
        "auth": True,
        "name": "OpenCode Go",
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/models",
        "auth": False,
        "name": "OpenRouter",
    },
}


def find_opencode_config() -> Path | None:
    """Find the first existing opencode config file."""
    for p in OPENCODE_CONFIG_PATHS:
        if p.exists():
            return p
    return None


def read_opencode_config() -> dict:
    """Read opencode config and return parsed JSON + metadata."""
    config_file = find_opencode_config()
    if not config_file:
        return {"found": False, "config_file": None, "data": {}}

    try:
        data = json.loads(config_file.read_text())
    except Exception:
        return {"found": False, "config_file": str(config_file), "data": {}}

    # Detect provider from model name
    model = data.get("model", "")
    current_model_provider = "opencode"
    if model and "/" in model:
        current_model_provider = model.split("/")[0]

    # Detect which providers have API keys
    # Sources: auth.json (from /connect), opencode.json, env vars
    detected_providers = {}

    # 1. Read auth.json (where /connect stores keys)
    auth_path = get_opencode_auth_path()
    if auth_path.exists():
        try:
            auth_data = json.loads(auth_path.read_text())
            for prov_id in auth_data:
                if isinstance(auth_data[prov_id], dict) and auth_data[prov_id].get("key"):
                    detected_providers[prov_id] = True
        except: pass

    # 2. Check opencode.json for explicit provider configs
    for prov_id in PROVIDER_API_CONFIG:
        key = data.get(prov_id, {}).get("api_key") or data.get("provider", {}).get(prov_id, {}).get("api_key")
        if key:
            detected_providers[prov_id] = True

    # 3. Check environment variables
    env_keys = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    for prov_id, env_var in env_keys.items():
        if os.environ.get(env_var):
            detected_providers[prov_id] = True

    # Build providers list (only connected providers managed by blender-mcp)
    providers_list = []
    for prov_id in sorted(detected_providers):
        cfg = PROVIDER_API_CONFIG.get(prov_id)
        if cfg:
            providers_list.append({
                "id": prov_id,
                "name": cfg["name"],
                "connected": True,
                "api_url": cfg["url"],
                "auth_required": cfg["auth"],
            })

    return {
        "found": True,
        "config_file": str(config_file),
        "data": data,
        "model": model,
        "current_provider": current_model_provider,
        "providers": providers_list,
    }


def write_opencode_model(model_name: str) -> dict:
    """Write a new model name to the opencode config file."""
    config_file = find_opencode_config()
    if not config_file:
        return {"success": False, "error": "No opencode config file found"}

    try:
        data = json.loads(config_file.read_text())
    except Exception as e:
        return {"success": False, "error": f"Failed to read config: {e}"}

    old_model = data.get("model")
    data["model"] = model_name

    try:
        config_file.write_text(json.dumps(data, indent=2) + "\n")
        return {
            "success": True,
            "config_file": str(config_file),
            "old_model": old_model,
            "new_model": model_name,
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to write config: {e}"}


def get_provider_from_model(model_name: str) -> str:
    """Extract provider prefix from model name (e.g. 'anthropic/claude...' → 'anthropic')."""
    if "/" in model_name:
        return model_name.split("/")[0]
    return "opencode"


def get_api_key(provider_id: str) -> str | None:
    """Get API key for a provider from auth.json or env vars."""
    # Check env vars first
    env_map = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    env_var = env_map.get(provider_id)
    if env_var:
        key = os.environ.get(env_var)
        if key:
            return key

    # Check auth.json (cross-platform)
    auth_path = get_opencode_auth_path()
    if auth_path.exists():
        try:
            auth_data = json.loads(auth_path.read_text())
            entry = auth_data.get(provider_id)
            if isinstance(entry, dict):
                return entry.get("key")
        except: pass

    # Check opencode config
    config_file = find_opencode_config()
    if config_file:
        try:
            data = json.loads(config_file.read_text())
            key = data.get(provider_id, {}).get("api_key") or data.get("provider", {}).get(provider_id, {}).get("api_key")
            if key:
                return key
        except: pass

    return None


def find_blender() -> str | None:
    """Find Blender executable path across platforms."""
    return _find_platform()


def find_python() -> str | None:
    """Find Python 3 executable."""
    if SYSTEM == "Windows":
        return shutil.which("python") or shutil.which("python3")
    return shutil.which("python3") or shutil.which("python")


def get_blender_version(blender_path: str) -> str | None:
    """Return Blender version string (e.g. '4.0.2')."""
    try:
        result = subprocess.run(
            [blender_path, "--version"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split("\n"):
            if line.strip().startswith("Blender"):
                return line.strip()
        return result.stdout.split("\n")[0].strip()
    except:
        return None


def check_disk_space(path: str = ".") -> dict:
    """Check available disk space in MB."""
    try:
        if SYSTEM == "Windows":
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(os.path.abspath(path)),
                None, None, ctypes.pointer(free_bytes)
            )
            free_mb = free_bytes.value / (1024 * 1024)
        else:
            st = os.statvfs(path)
            free_mb = (st.f_frsize * st.f_bavail) / (1024 * 1024)
        return {"free_mb": round(free_mb, 1), "enough": free_mb > 500}
    except:
        return {"free_mb": 0, "enough": False}


def get_system_info() -> dict:
    """Return all system info for diagnostics."""
    blender_path = find_blender()
    blender_ver = get_blender_version(blender_path) if blender_path else None
    python_path = find_python()
    disk = check_disk_space()

    return {
        "system": SYSTEM,
        "python": python_path,
        "python_version": sys.version.split()[0] if python_path else None,
        "blender": blender_path,
        "blender_version": blender_ver,
        "disk_free_mb": disk["free_mb"],
        "disk_ok": disk["enough"],
    }


def print_summary():
    info = get_system_info()
    print(f"\n{'='*50}")
    print(f"  blender-mcp — System Check")
    print(f"{'='*50}")
    print(f"  OS:          {info['system']}")
    print(f"  Python:      {info['python']} ({info['python_version']})")
    print(f"  Blender:     {info['blender']} ({info['blender_version']})")
    print(f"  Disk free:   {info['disk_free_mb']} MB")
    print(f"{'='*50}")
    if info['blender'] and info['python']:
        print(f"  ✅ Sistema listo para blender-mcp")
    else:
        print(f"  ❌ Faltan componentes. Revisa check.py para más detalles.")
    print(f"{'='*50}\n")
    return info


if __name__ == "__main__":
    print_summary()
