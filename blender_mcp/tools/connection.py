"""
blender-mcp — Connection & Sync tools
Provides high-level tools to connect and sync with Blender in one go.
"""
import json
from ...blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)

def register_tools(mcp):
    @mcp.tool(**RO())
    def sync_blender_state() -> str:
        """Syncs with Blender: connects, checks health, and gets scene info in one call.
        Connects to Blender and retrieves health + scene info to avoid multiple authorizations."""
        try:
            b = get_blender()
            if not b.connect():
                return json.dumps({"error": "No se pudo conectar a Blender. ¿Está abierto?"})
            
            health = b.send_command("ping")
            scene_info = b.send_command("get_scene_info")
            
            return json.dumps({
                "status": "connected",
                "health": health,
                "scene": scene_info
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
