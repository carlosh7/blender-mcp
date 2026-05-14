"""
blender-mcp — Hyper3D Rodin MCP tools
"""
import json
from ...blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def _process_bbox(bbox):
    if bbox is None:
        return None
    if all(isinstance(i, int) for i in bbox):
        return bbox
    if any(i <= 0 for i in bbox):
        raise ValueError("bbox values must be positive")
    m = max(bbox)
    return [int(float(i) / m * 100) for i in bbox]


def register_tools(mcp):
    @mcp.tool()
    def get_hyper3d_status() -> str:
        """Check if Hyper3D Rodin integration is enabled.
        Hyper3D Rodin generates 3D models from text or images using AI."""
        b = get_blender()
        result = b.send_command("get_hyper3d_status")
        return json.dumps(result, indent=2)

    @mcp.tool()
    def generate_hyper3d_text(text_prompt: str, bbox_condition: list = None) -> str:
        """Generate a 3D model using Hyper3D Rodin from a text description.
        Args:
            text_prompt: Description of the desired 3D model in English
            bbox_condition: Optional [length, width, height] ratio
        """
        b = get_blender()
        result = b.send_command("create_rodin_job", {
            "text_prompt": text_prompt,
            "bbox_condition": _process_bbox(bbox_condition),
        })
        return json.dumps(result, indent=2)

    @mcp.tool()
    def poll_rodin_job(subscription_key: str = "", request_id: str = "") -> str:
        """Check if a Hyper3D Rodin generation job is complete.
        Args:
            subscription_key: For MAIN_SITE mode (from generate_hyper3d_text)
            request_id: For FAL_AI mode (from generate_hyper3d_text)
        """
        b = get_blender()
        kwargs = {}
        if subscription_key:
            kwargs["subscription_key"] = subscription_key
        if request_id:
            kwargs["request_id"] = request_id
        result = b.send_command("poll_rodin_job", kwargs)
        return json.dumps(result, indent=2)

    @mcp.tool()
    def import_rodin_asset(name: str = "", task_uuid: str = "", request_id: str = "") -> str:
        """Import a completed Hyper3D Rodin generated model into Blender.
        Args:
            name: Name for the imported object
            task_uuid: For MAIN_SITE mode
            request_id: For FAL_AI mode
        """
        b = get_blender()
        result = b.send_command("import_generated_asset", {
            "name": name, "task_uuid": task_uuid, "request_id": request_id,
        })
        return json.dumps(result, indent=2)
