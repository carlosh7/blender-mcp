# Test Configuration for blender-mcp-ultra
import sys
import os
import pytest

# Add src to path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Check if bpy is available
try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

# Skip marker for tests requiring Blender
skip_without_bpy = pytest.mark.skipif(not HAS_BPY, reason="Blender not available")

# Blender mock for testing without Blender
class MockBpy:
    """Mock bpy module for testing."""
    class context:
        scene = None
        view_layer = None
        selected_objects = []
    
    class data:
        objects = []
        materials = []
        node_groups = []
    
    class ops:
        @staticmethod
        def object_add(**kwargs):
            return {'name': 'TestObject'}
        
        @staticmethod
        def light_add(**kwargs):
            return {'name': 'TestLight'}
        
        @staticmethod
        def camera_add(**kwargs):
            return {'name': 'TestCamera'}
        
        @staticmethod
        def mode_set(**kwargs):
            return None

# Mock bpy module
if not HAS_BPY:
    sys.modules['bpy'] = MockBpy()

# Test configuration
PYTEST_MARKS = {
    'e2e': 'End-to-end tests requiring real Blender',
    'slow': 'Tests that take more than 10 seconds',
    'security': 'Security validation tests',
    'integration': 'Integration tests with Blender',
}
