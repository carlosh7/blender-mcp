"""
blender-mcp — Unit Tests for Transform Reset
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Mock bpy before importing
sys.modules['bpy'] = MagicMock()
sys.modules['bpy.props'] = MagicMock()
sys.modules['bpy.types'] = MagicMock()
sys.modules['mathutils'] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'addon'))


class TestTransformReset:
    """Tests for transform reset functions."""

    def test_get_transform_status_returns_dict(self):
        from transform_reset import get_transform_status
        mock_obj = MagicMock()
        mock_obj.name = "TestObj"
        mock_obj.location = MagicMock()
        mock_obj.location.__iter__ = lambda self: iter([0, 0, 0])
        mock_obj.rotation_euler = MagicMock()
        mock_obj.rotation_euler.__iter__ = lambda self: iter([0, 0, 0])
        mock_obj.scale = MagicMock()
        mock_obj.scale.__iter__ = lambda self: iter([1, 1, 1])
        mock_obj.type = 'MESH'
        mock_obj.data = MagicMock()
        mock_obj.data.vertices = []
        status = get_transform_status(mock_obj)
        assert isinstance(status, dict)
        assert "name" in status
        assert "scale" in status

    def test_get_scene_transform_report_returns_string(self):
        from transform_reset import get_scene_transform_report
        with patch('transform_reset.bpy') as mock_bpy:
            mock_bpy.context.scene.objects = []
            report = get_scene_transform_report()
            assert isinstance(report, str)
            assert "TRANSFORM REPORT" in report

    def test_reset_scene_transforms_returns_dict(self):
        from transform_reset import reset_scene_transforms
        with patch('transform_reset.bpy') as mock_bpy:
            result = reset_scene_transforms([])
            assert isinstance(result, dict)
            assert "total" in result
            assert "success" in result
