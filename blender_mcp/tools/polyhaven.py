"""
blender-mcp — Poly Haven MCP tools
"""
import json
from ...blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def get_polyhaven_status() -> str:
        """Check if Poly Haven integration is enabled.
        Poly Haven provides HDRI environments, PBR textures, and 3D models."""
        b = get_blender()
        result = b.send_command("get_polyhaven_status")
        return json.dumps(result, indent=2)

    @mcp.tool()
    def search_polyhaven(asset_type: str = "all", query: str = "", limit: int = 20) -> str:
        """Search Poly Haven assets.
        Args:
            asset_type: 'hdris', 'textures', 'models', or 'all'
            query: Search term to filter results
            limit: Max results (default 20)
        """
        b = get_blender()
        result = b.send_command("search_polyhaven", {"asset_type": asset_type, "query": query, "limit": limit})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_polyhaven_categories(asset_type: str = "hdris") -> str:
        """Get available categories for a Poly Haven asset type.
        Args:
            asset_type: 'hdris', 'textures', or 'models'
        """
        b = get_blender()
        result = b.send_command("get_polyhaven_categories", {"asset_type": asset_type})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def download_polyhaven_hdri(asset_id: str, resolution: str = "1k") -> str:
        """Download and apply a Poly Haven HDRI as world environment lighting.
        Args:
            asset_id: The HDRI asset ID (e.g., 'syferfontein_18d_clear')
            resolution: '1k', '2k', '4k', '8k' (default '1k')
        """
        b = get_blender()
        result = b.send_command("download_polyhaven_hdri", {"asset_id": asset_id, "resolution": resolution})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def download_polyhaven_texture(asset_id: str, resolution: str = "1k") -> str:
        """Download a Poly Haven texture and create a PBR material in Blender.
        Args:
            asset_id: The texture asset ID (e.g., 'bamboo_forest_01')
            resolution: '1k', '2k', '4k', '8k' (default '1k')
        """
        b = get_blender()
        result = b.send_command("download_polyhaven_texture", {"asset_id": asset_id, "resolution": resolution})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def download_polyhaven_model(asset_id: str, resolution: str = "1k") -> str:
        """Download a Poly Haven 3D model and import into scene.
        Args:
            asset_id: The model asset ID
            resolution: '1k', '2k', '4k' (default '1k')
        """
        b = get_blender()
        result = b.send_command("download_polyhaven_model", {"asset_id": asset_id, "resolution": resolution})
        return json.dumps(result, indent=2)
