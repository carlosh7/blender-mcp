"""
blender-mcp — AmbientCG MCP tools
"""
import json
from blender_connection import get_blender


def register_tools(mcp):
    @mcp.tool()
    def search_ambientcg(query: str = "", limit: int = 20, categories: str = "") -> str:
        """Search AmbientCG for PBR materials. Free, no API key needed.
        Args:
            query: Search term
            limit: Max results (default 20)
            categories: Optional category filter
        """
        b = get_blender()
        result = b.send_command("search_ambientcg", {"query": query, "limit": limit, "categories": categories})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def get_ambientcg_categories() -> str:
        """Get available AmbientCG material categories."""
        b = get_blender()
        result = b.send_command("get_ambientcg_categories")
        return json.dumps(result, indent=2)

    @mcp.tool()
    def download_ambientcg_material(asset_id: str, resolution: str = "1K") -> str:
        """Download an AmbientCG PBR material and create a Blender material.
        Args:
            asset_id: The asset ID (e.g., 'PavingStones071')
            resolution: '1K', '2K', '4K', '8K', '16K' (default '1K')
        """
        b = get_blender()
        result = b.send_command("download_ambientcg_material", {"asset_id": asset_id, "resolution": resolution})
        return json.dumps(result, indent=2)
