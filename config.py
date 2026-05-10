import os
import sys
import shutil
import platform
import subprocess
import json
from pathlib import Path

SYSTEM = platform.system()  # 'Windows' or 'Linux'

# ─── opencode config paths ───
OPENCODE_CONFIG_PATHS = [
    Path.home() / ".config" / "opencode" / "opencode.json",
    Path.home() / ".config" / "opencode" / "opencode.jsonc",
    Path.cwd() / "opencode.json",
    Path.cwd() / "opencode.jsonc",
    Path.home() / "Check" / "opencode.json",
    Path.home() / "check-3d-planner" / "opencode.json",
]

# Known model lists per provider (when we can't query the API)
KNOWN_MODELS = {
    "anthropic": [
        "anthropic/claude-sonnet-4-5", "anthropic/claude-haiku-4-5",
        "anthropic/claude-opus-4-5", "anthropic/claude-3-5-sonnet",
        "anthropic/claude-3-5-haiku", "anthropic/claude-3-opus",
        "anthropic/claude-3-sonnet", "anthropic/claude-3-haiku",
    ],
    "openai": [
        "openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-4-turbo",
        "openai/gpt-4", "openai/gpt-3.5-turbo",
        "openai/o1", "openai/o1-mini", "openai/o3-mini",
        "openai/o1-pro", "openai/gpt-4.5-preview",
    ],
    "deepseek": [
        "deepseek/deepseek-chat", "deepseek/deepseek-reasoner",
        "deepseek/deepseek-coder",
    ],
    "mistral": [
        "mistralai/mistral-large", "mistralai/mistral-medium",
        "mistralai/mistral-small", "mistralai/codestral",
        "mistralai/mistral-7b-v0.3",
    ],
    "google": [
        "google/gemini-2.0-flash", "google/gemini-2.0-pro",
        "google/gemini-1.5-pro", "google/gemini-1.5-flash",
    ],
    "groq": [
        "groq/llama-3.3-70b", "groq/llama-3.1-8b",
        "groq/mixtral-8x7b", "groq/gemma-7b",
    ],
    "meta": [
        "meta/llama-3.3-70b", "meta/llama-3.1-405b",
        "meta/llama-3.1-70b", "meta/llama-3.1-8b",
    ],
    "cohere": [
        "cohere/command-r-plus", "cohere/command-r",
    ],
}

# Providers that have public model listing APIs
PUBLIC_API_PROVIDERS = ["openrouter"]


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
    auth_path = Path.home() / ".local/share/opencode/auth.json"
    if auth_path.exists():
        try:
            auth_data = json.loads(auth_path.read_text())
            for prov_id in auth_data:
                if isinstance(auth_data[prov_id], dict) and auth_data[prov_id].get("key"):
                    detected_providers[prov_id] = True
        except: pass

    # 2. Check opencode.json provider section
    for prov_id in KNOWN_MODELS:
        key = data.get(prov_id, {}).get("api_key") or data.get("provider", {}).get(prov_id, {}).get("api_key")
        if key:
            detected_providers[prov_id] = True

    # 3. Check environment variables
    env_keys = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    for prov_id, env_var in env_keys.items():
        if os.environ.get(env_var):
            detected_providers[prov_id] = True

    # Build providers list (only connected providers)
    providers_list = []
    for prov_id in sorted(detected_providers):
        is_public_api = prov_id in PUBLIC_API_PROVIDERS
        model_count = len(KNOWN_MODELS.get(prov_id, []))
        providers_list.append({
            "id": prov_id,
            "name": prov_id.capitalize(),
            "connected": True,
            "model_count": model_count if not is_public_api else 300,
            "public_api": is_public_api,
            "api_url": "https://openrouter.ai/api/v1/models" if is_public_api else None,
        })

    # Check if current model's provider is among connected providers
    current_provider_connected = any(p["id"] == current_model_provider for p in providers_list)

    return {
        "found": True,
        "config_file": str(config_file),
        "data": data,
        "model": model,
        "current_provider": current_model_provider,
        "current_provider_connected": current_provider_connected,
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

def find_blender() -> str | None:
    """Find Blender executable path across platforms."""
    if SYSTEM == "Windows":
        # 1. PATH
        blender = shutil.which("blender.exe") or shutil.which("blender")
        if blender:
            return blender

        # 2. Program Files
        common = [
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
        ]
        for base in common:
            path = os.path.join(base, "Blender Foundation")
            if os.isdir(path):
                for entry in os.listdir(path):
                    if entry.startswith("Blender"):
                        exe = os.path.join(path, entry, "blender.exe")
                        if os.path.isfile(exe):
                            return exe

        # 3. Microsoft Store
        store = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps")
        store_exe = os.path.join(store, "blender.exe")
        if os.path.isfile(store_exe):
            return store_exe

        return None

    else:  # Linux
        blender = shutil.which("blender")
        if blender:
            return blender
        # Common paths
        for path in ["/usr/bin/blender", "/snap/bin/blender"]:
            if os.path.isfile(path):
                return path
        return None


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
