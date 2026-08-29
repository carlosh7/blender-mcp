"""Fuente única de versión: blender_mcp.__version__ == manifest == bl_info."""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _manifest_version() -> str:
    for line in (REPO / "addon" / "blender_manifest.toml").read_text().splitlines():
        if line.startswith("version"):
            return line.split("=")[1].strip().strip('"')
    return ""


def _bl_info_version() -> str:
    sys.path.insert(0, str(REPO))
    import addon as addon_pkg  # noqa: PLC0415 — necesita bpy-stub? addon/__init__ tolera sin bpy

    return ".".join(str(n) for n in addon_pkg.bl_info["version"])


def test_versions_match():
    from blender_mcp import __version__

    assert _manifest_version() == __version__, "manifest != blender_mcp.__version__"


def test_manifest_version_format():
    v = _manifest_version()
    assert v.count(".") == 2 and all(part.isdigit() for part in v.split("."))
