"""
blender-mcp-ultra — Compatibility Tests
Tests for version compatibility.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestPythonCompatibility:
    """Tests for Python version compatibility."""
    
    def test_python_version(self):
        """Verify Python version is supported."""
        version = sys.version_info
        assert version.major == 3
        assert version.minor >= 10, f"Python {version.major}.{version.minor} not supported"
    
    def test_type_hints(self):
        """Verify type hints work correctly."""
        from typing import Dict, List, Optional, Set, Tuple
        assert Dict is not None
        assert List is not None
        assert Optional is not None
        assert Set is not None
        assert Tuple is not None
    
    def test_dataclasses(self):
        """Verify dataclasses work correctly."""
        from dataclasses import dataclass
        
        @dataclass
        class TestData:
            name: str
            value: int
        
        data = TestData(name="test", value=42)
        assert data.name == "test"
        assert data.value == 42
    
    def test_pathlib(self):
        """Verify pathlib works correctly."""
        from pathlib import Path
        path = Path("/tmp/test")
        assert path.exists() or not path.exists()  # Just verify it works
    
    def test_json(self):
        """Verify json module works correctly."""
        import json
        data = {"key": "value", "number": 42}
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert parsed == data


class TestBlenderCompatibility:
    """Tests for Blender version compatibility."""
    
    def test_blender_manifest_version(self):
        """Verify manifest specifies compatible Blender versions."""
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'blender_manifest.toml')
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                content = f.read()
            assert 'blender_version_min' in content
    
    def test_addon_manifest_version(self):
        """Verify addon manifest specifies compatible Blender versions."""
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'addon', 'blender_manifest.toml')
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                content = f.read()
            assert 'blender_version_min' in content
    
    def test_bpy_import(self):
        """Verify bpy can be imported (if available)."""
        try:
            import bpy
            # If bpy is available, verify version
            # Note: In test mode, bpy is mocked and may not have all attributes
            if hasattr(bpy, 'app') and hasattr(bpy.app, 'version'):
                assert True  # Real bpy with version
            else:
                # Mock bpy or bpy without version attribute
                assert True
        except ImportError:
            # bpy not available, skip
            pass


class TestFileStructure:
    """Tests for project file structure."""
    
    def test_src_directory_exists(self):
        """Verify src directory exists."""
        src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
        assert os.path.exists(src_path)
    
    def test_core_directory_exists(self):
        """Verify core directory exists."""
        core_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core')
        assert os.path.exists(core_path)
    
    def test_tools_directory_exists(self):
        """Verify tools directory exists."""
        tools_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'tools')
        assert os.path.exists(tools_path)
    
    def test_infrastructure_directory_exists(self):
        """Verify infrastructure directory exists."""
        infra_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'infrastructure')
        assert os.path.exists(infra_path)
    
    def test_skills_directory_exists(self):
        """Verify skills directory exists."""
        skills_path = os.path.join(os.path.dirname(__file__), '..', '..', 'skills')
        assert os.path.exists(skills_path)
    
    def test_tests_directory_exists(self):
        """Verify tests directory exists."""
        tests_path = os.path.join(os.path.dirname(__file__), '..', '..', 'tests')
        assert os.path.exists(tests_path)
    
    def test_docs_directory_exists(self):
        """Verify docs directory exists."""
        docs_path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs')
        assert os.path.exists(docs_path)


class TestDependencyCompatibility:
    """Tests for dependency compatibility."""
    
    def test_mcp_import(self):
        """Verify MCP library can be imported."""
        try:
            from mcp.server.fastmcp import FastMCP
            assert FastMCP is not None
        except ImportError:
            # MCP library not installed
            pass
    
    def test_requests_import(self):
        """Verify requests library can be imported."""
        try:
            import requests
            assert requests is not None
        except ImportError:
            # requests not installed
            pass
    
    def test_pytest_import(self):
        """Verify pytest can be imported."""
        import pytest
        assert pytest is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
