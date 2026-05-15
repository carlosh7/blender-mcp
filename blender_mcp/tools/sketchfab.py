"""
blender-mcp — Sketchfab MCP tools
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def get_sketchfab_status() -> str:
        """Check if Sketchfab integration is enabled and configured.
        Sketchfab provides realistic 3D models for download."""
        b = get_blender()
        result = b.send_command("get_sketchfab_status")
        return json.dumps(result, indent=2)

    @mcp.tool()
    def search_sketchfab(query: str, count: int = 20, downloadable: bool = True) -> str:
        """Search Sketchfab for 3D models.
        Args:
            query: Text to search for
            count: Max results (default 20)
            downloadable: Only include downloadable models (default True)
        """
        b = get_blender()
        result = b.send_command("search_sketchfab", {"query": query, "count": count, "downloadable": downloadable})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_sketchfab_preview(uid: str) -> str:
        """Get a preview thumbnail of a Sketchfab model as base64.
        Use this to visually confirm a model before downloading.
        Args:
            uid: Sketchfab model UID (from search_sketchfab)
        """
        b = get_blender()
        result = b.send_command("get_sketchfab_preview", {"uid": uid})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def download_sketchfab_model(uid: str, target_size: float = 1.0) -> str:
        """Download and import a Sketchfab model into Blender.
        Args:
            uid: Sketchfab model UID (from search_sketchfab)
            target_size: Size in meters for the largest dimension (default 1.0)
        """
        b = get_blender()
        result = b.send_command("download_sketchfab_model", {"uid": uid, "target_size": target_size})
        return json.dumps(result, indent=2)
