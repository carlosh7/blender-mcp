"""
blender-mcp — Config Cache (cross-platform)
"""
import json
import os
from pathlib import Path
from .platform import get_config_dir

CONFIG_DIR = get_config_dir()
CONFIG_FILE = CONFIG_DIR / "provider_cache.json"


def load_config():
    """Load cached provider configuration."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {}


def save_config(config):
    """Save provider configuration."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_provider_config(provider_id):
    """Get config for a specific provider."""
    config = load_config()
    return config.get(provider_id, {})


def set_provider_config(provider_id, **kwargs):
    """Update config for a specific provider."""
    config = load_config()
    if provider_id not in config:
        config[provider_id] = {}
    config[provider_id].update(kwargs)
    save_config(config)


def get_last_model():
    """Get the last used model."""
    config = load_config()
    return config.get("_last_model", "")


def set_last_model(model):
    """Save the last used model."""
    config = load_config()
    config["_last_model"] = model
    save_config(config)
