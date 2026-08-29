"""
blender-mcp-ultra — Central Configuration (Pydantic Settings)
Loads config from config.yaml + environment variables.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# CONFIG MODELS
# ═══════════════════════════════════════════════════════════════


@dataclass
class BlenderConfig:
    """Blender connection settings."""

    host: str = "localhost"
    port: int = 9876
    timeout: int = 30
    auto_start: bool = True


@dataclass
class AssetsConfig:
    """Asset library settings."""

    dir: str = "~/.local/share/blender-mcp/assets"
    cache_size_mb: int = 500
    providers: list[str] = field(default_factory=lambda: ["polyhaven", "ambientcg"])


@dataclass
class SecurityConfig:
    """Security settings."""

    ast_mode: str = "allowlist"  # allowlist | blocklist
    sandbox_enabled: bool = True
    sandbox_timeout: int = 10
    rate_limit: int = 60
    blocked_ops: list[str] = field(
        default_factory=lambda: [
            "wm.quit_blender",
            "wm.read_factory_settings",
            "wm.read_factory_userpref",
            "wm.read_userpref",
        ]
    )


@dataclass
class LoggingConfig:
    """Logging settings."""

    level: str = "INFO"
    audit_file: str = "/tmp/blender-mcp-audit.json"
    max_audit_size_mb: int = 10


@dataclass
class PerformanceConfig:
    """Performance settings."""

    max_objects: int = 10000
    max_polygons: int = 1000000
    auto_purge_threshold: int = 50
    viewport_update_delay: float = 0.1


@dataclass
class ToolsConfig:
    """Tools registry settings."""

    version: str = "1.0.0"
    lazy_loading: bool = True
    core_tools_count: int = 15


@dataclass
class Settings:
    """Main settings container."""

    blender: BlenderConfig = field(default_factory=BlenderConfig)
    assets: AssetsConfig = field(default_factory=AssetsConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    tools: ToolsConfig = field(default_factory=ToolsConfig)


# ═══════════════════════════════════════════════════════════════
# CONFIG LOADER
# ═══════════════════════════════════════════════════════════════


def load_yaml_config(config_path: str = None) -> dict:
    """Load YAML config file."""
    if config_path is None:
        # Look for config.yaml in project root
        config_path = Path(__file__).parent.parent.parent.parent / "config.yaml"

    config_path = Path(config_path)

    if not config_path.exists():
        return {}

    try:
        import yaml

        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback: parse YAML manually (basic)
        return _parse_yaml_basic(config_path)
    except Exception as e:
        print(f"[config] Error loading {config_path}: {e}")
        return {}


def _parse_yaml_basic(config_path: Path) -> dict:
    """Basic YAML parser without PyYAML."""
    result = {}
    try:
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    # Basic type conversion
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace(".", "").isdigit():
                        value = float(value)
                    result[key] = value
    except Exception:
        pass
    return result


def apply_env_overrides(config: dict) -> dict:
    """Apply environment variable overrides."""
    env_prefix = "BLENDER_MCP_"

    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            # Convert BLENDER_MCP_BLENDER_PORT -> config['blender']['port']
            parts = key[len(env_prefix) :].lower().split("_")
            if len(parts) == 2:
                section, field = parts
                if section not in config:
                    config[section] = {}
                config[section][field] = value

    return config


def dict_to_settings(data: dict) -> Settings:
    """Convert dict to Settings object."""
    settings = Settings()

    if "blender" in data:
        b = data["blender"]
        settings.blender = BlenderConfig(
            host=b.get("host", settings.blender.host),
            port=int(b.get("port", settings.blender.port)),
            timeout=int(b.get("timeout", settings.blender.timeout)),
            auto_start=b.get("auto_start", settings.blender.auto_start),
        )

    if "assets" in data:
        a = data["assets"]
        settings.assets = AssetsConfig(
            dir=a.get("dir", settings.assets.dir),
            cache_size_mb=int(a.get("cache_size_mb", settings.assets.cache_size_mb)),
            providers=a.get("providers", settings.assets.providers),
        )

    if "security" in data:
        s = data["security"]
        settings.security = SecurityConfig(
            ast_mode=s.get("ast_mode", settings.security.ast_mode),
            sandbox_enabled=s.get("sandbox_enabled", settings.security.sandbox_enabled),
            sandbox_timeout=int(s.get("sandbox_timeout", settings.security.sandbox_timeout)),
            rate_limit=int(s.get("rate_limit", settings.security.rate_limit)),
            blocked_ops=s.get("blocked_ops", settings.security.blocked_ops),
        )

    if "logging" in data:
        logging_data = data["logging"]
        settings.logging = LoggingConfig(
            level=logging_data.get("level", settings.logging.level),
            audit_file=logging_data.get("audit_file", settings.logging.audit_file),
            max_audit_size_mb=int(
                logging_data.get("max_audit_size_mb", settings.logging.max_audit_size_mb)
            ),
        )

    if "performance" in data:
        p = data["performance"]
        settings.performance = PerformanceConfig(
            max_objects=int(p.get("max_objects", settings.performance.max_objects)),
            max_polygons=int(p.get("max_polygons", settings.performance.max_polygons)),
            auto_purge_threshold=int(
                p.get("auto_purge_threshold", settings.performance.auto_purge_threshold)
            ),
            viewport_update_delay=float(
                p.get("viewport_update_delay", settings.performance.viewport_update_delay)
            ),
        )

    if "tools" in data:
        t = data["tools"]
        settings.tools = ToolsConfig(
            version=t.get("version", settings.tools.version),
            lazy_loading=t.get("lazy_loading", settings.tools.lazy_loading),
            core_tools_count=int(t.get("core_tools_count", settings.tools.core_tools_count)),
        )

    return settings


# ═══════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════

_settings: Settings | None = None


def get_settings(config_path: str = None) -> Settings:
    """Get singleton settings instance."""
    global _settings
    if _settings is None:
        config = load_yaml_config(config_path)
        config = apply_env_overrides(config)
        _settings = dict_to_settings(config)
    return _settings


def reload_settings(config_path: str = None) -> Settings:
    """Reload settings from config file."""
    global _settings
    _settings = None
    return get_settings(config_path)
