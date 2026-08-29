"""
blender-mcp — Test Configuration
"""

import os
import sys

# Add addon to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "addon"))

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
