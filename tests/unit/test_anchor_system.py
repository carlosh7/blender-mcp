"""
blender-mcp — Unit Tests for Anchor System
Tests for 27-point anchor alignment system.
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


class TestAnchorNames:
    """Tests for anchor name definitions."""

    def test_anchor_names_count(self):
        from anchor_system import ANCHOR_NAMES

        assert len(ANCHOR_NAMES) == 27

    def test_anchor_names_unique(self):
        from anchor_system import ANCHOR_NAMES

        assert len(ANCHOR_NAMES) == len(set(ANCHOR_NAMES))

    def test_centroid_present(self):
        from anchor_system import ANCHOR_NAMES

        assert "CENTROID" in ANCHOR_NAMES

    def test_face_centers_present(self):
        from anchor_system import ANCHOR_NAMES

        for face in [
            "FRONT_CENTER",
            "BACK_CENTER",
            "LEFT_CENTER",
            "RIGHT_CENTER",
            "TOP_CENTER",
            "BOTTOM_CENTER",
        ]:
            assert face in ANCHOR_NAMES


class TestAnchorCalculation:
    """Tests for anchor calculation functions."""

    def test_get_bbox_anchors_returns_dict(self):
        import anchor_system
        from anchor_system import get_bbox_anchors

        class FakeVector:
            def __init__(self, seq):
                self.x, self.y, self.z = (float(v) for v in seq)

            def __iter__(self):
                return iter((self.x, self.y, self.z))

        mock_obj = MagicMock()
        mock_obj.bound_box = [
            (-0.5, -0.5, -0.5),
            (0.5, -0.5, -0.5),
            (0.5, 0.5, -0.5),
            (-0.5, 0.5, -0.5),
            (-0.5, -0.5, 0.5),
            (0.5, -0.5, 0.5),
            (0.5, 0.5, 0.5),
            (-0.5, 0.5, 0.5),
        ]
        mock_matrix = MagicMock()
        mock_matrix.__matmul__ = lambda self, other: other
        mock_obj.matrix_world = mock_matrix

        with patch.object(anchor_system, "Vector", FakeVector):
            anchors = get_bbox_anchors(mock_obj)

        assert isinstance(anchors, dict)
        assert len(anchors) == 27


class TestAssemblyPlan:
    """Tests for assembly plan generation."""

    def test_empty_list_returns_empty_plan(self):
        from anchor_system import get_assembly_plan

        plan = get_assembly_plan([])
        assert plan == []

    def test_single_object_returns_empty_plan(self):
        from anchor_system import get_assembly_plan

        mock_obj = MagicMock()
        plan = get_assembly_plan([mock_obj])
        assert plan == []
