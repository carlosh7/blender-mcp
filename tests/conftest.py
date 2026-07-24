"""
blender-mcp-ultra — Test Configuration
"""
import sys
import os

# Add src to path for all tests
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
