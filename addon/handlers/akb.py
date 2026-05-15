"""
blender-mcp — AKB Handler (Axiom Knowledge Base)
"""
import bpy
from . import BaseHandler


class AKBHandler(BaseHandler):
    """Axiom Knowledge Base: query and manage object blueprints."""

    namespace = "akb"

    @staticmethod
    def cmd_get_specs(query=""):
        try:
            from ..akb import get_specs
            results = get_specs(query)
            return {"query": query, "total": len(results), "results": results}
        except Exception as e:
            return {"query": query, "error": str(e), "results": []}

    @staticmethod
    def cmd_list_categories():
        try:
            from ..akb import list_categories
            return {"categories": list_categories()}
        except Exception as e:
            return {"categories": [], "error": str(e)}

    @staticmethod
    def cmd_feed_category(category="av", keywords=""):
        try:
            from ..akb_fetcher import feed_from_polyhaven
            kw_list = [k.strip() for k in keywords.split(",")] if keywords else None
            result = feed_from_polyhaven(category, kw_list)
            return result
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def cmd_feed_from_scanner(obj_name=""):
        try:
            from ..akb_fetcher import feed_from_scanner
            return feed_from_scanner(obj_name)
        except Exception as e:
            return {"error": str(e)}
