"""
blender-mcp — Unit Tests for Orphan Purge
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Mock bpy before importing
sys.modules["bpy"] = MagicMock()
sys.modules["bpy.props"] = MagicMock()
sys.modules["bpy.types"] = MagicMock()
sys.modules["mathutils"] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "addon"))


class TestOrphanPurge:
    """Tests for orphan purge functions."""

    def test_get_orphan_stats_returns_dict(self):
        from orphan_purge import get_orphan_stats

        with patch("orphan_purge.bpy") as mock_bpy:
            mock_bpy.data.meshes = []
            mock_bpy.data.materials = []
            mock_bpy.data.textures = []
            mock_bpy.data.images = []
            mock_bpy.data.cameras = []
            mock_bpy.data.lights = []
            mock_bpy.data.curves = []
            mock_bpy.data.armatures = []
            mock_bpy.data.actions = []
            stats = get_orphan_stats()
            assert isinstance(stats, dict)
            assert "total" in stats

    def test_purge_orphans_returns_dict(self):
        from orphan_purge import purge_orphans

        with patch("orphan_purge.bpy"), patch("orphan_purge.get_orphan_stats") as mock_stats:
            mock_stats.return_value = {
                "meshes": 0,
                "materials": 0,
                "textures": 0,
                "images": 0,
                "cameras": 0,
                "lights": 0,
                "curves": 0,
                "armatures": 0,
                "actions": 0,
                "total": 0,
            }
            result = purge_orphans()
            assert isinstance(result, dict)
            assert "success" in result

    def test_get_memory_report_returns_string(self):
        from orphan_purge import get_memory_report

        with (
            patch("orphan_purge.bpy") as mock_bpy,
            patch("orphan_purge.get_orphan_stats") as mock_stats,
            patch("orphan_purge.get_memory_usage") as mock_usage,
        ):
            mock_bpy.data.objects = []
            mock_bpy.data.materials = []
            mock_bpy.data.meshes = []
            mock_stats.return_value = {
                "meshes": 0,
                "materials": 0,
                "textures": 0,
                "images": 0,
                "cameras": 0,
                "lights": 0,
                "curves": 0,
                "armatures": 0,
                "actions": 0,
                "total": 0,
            }
            mock_usage.return_value = {
                "python_objects": 0,
                "python_materials": 0,
                "python_meshes": 0,
                "orphan_blocks": 0,
                "timestamp": "now",
            }
            report = get_memory_report()
            assert isinstance(report, str)
            assert "MEMORY REPORT" in report
