"""
blender-mcp — Test Configuration
"""
import sys
import os

# Add addon to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'addon'))

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
