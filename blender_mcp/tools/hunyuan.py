"""
blender-mcp — Hunyuan3D MCP tools
"""
import json
from ...blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def get_hunyuan3d_status() -> str:
        """Check if Hunyuan3D integration is enabled.
        Hunyuan3D generates 3D models from text descriptions or images using Tencent's AI."""
        b = get_blender()
        result = b.send_command("get_hunyuan3d_status")
        return json.dumps(result, indent=2)

    @mcp.tool()
    def generate_hunyuan3d(text_prompt: str = "", image_url: str = "") -> str:
        """Generate a 3D model using Hunyuan3D from text or image.
        Args:
            text_prompt: Optional text description of the model
            image_url: Optional URL of a reference image
        """
        b = get_blender()
        result = b.send_command("create_hunyuan_job", {"text_prompt": text_prompt, "image": image_url})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def poll_hunyuan_job(job_id: str = "") -> str:
        """Check if a Hunyuan3D generation job is complete.
        Args:
            job_id: The job ID from generate_hunyuan3d (format: 'job_xxx')
        """
        b = get_blender()
        result = b.send_command("poll_hunyuan_job", {"job_id": job_id})
        return json.dumps(result, indent=2)

    @mcp.tool()
    def import_hunyuan_asset(name: str = "", zip_file_url: str = "") -> str:
        """Import a completed Hunyuan3D model into Blender.
        Args:
            name: Name for the imported object
            zip_file_url: URL of the generated ZIP from poll_hunyuan_job
        """
        b = get_blender()
        result = b.send_command("import_hunyuan_asset", {"name": name, "zip_file_url": zip_file_url})
        return json.dumps(result, indent=2)
