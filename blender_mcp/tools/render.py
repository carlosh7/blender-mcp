"""
blender-mcp — Render MCP tools
"""
import json
from blender_connection import get_blender
from mcp.types import ToolAnnotations

def RO(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=True), **kw)
def RW(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True), **kw)
def ADD(**kw): return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False), **kw)


def register_tools(mcp):
    @mcp.tool()
    def set_render_engine(engine: str = "CYCLES") -> str:
        """Set the render engine: CYCLES, EEVEE, or WORKBENCH."""
        b = get_blender()
        r = b.send_command("set_render_engine", {"engine": engine})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def set_render_resolution(width: int = 1920, height: int = 1080, percentage: int = 100) -> str:
        """Set the render resolution."""
        b = get_blender()
        r = b.send_command("set_render_resolution", {"width": width, "height": height, "percentage": percentage})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def set_render_samples(samples: int = 128) -> str:
        """Set Cycles render samples."""
        b = get_blender()
        r = b.send_command("set_render_samples", {"samples": samples})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def render_frame(filepath: str = "") -> str:
        """Render the current frame to an image file."""
        b = get_blender()
        r = b.send_command("render_frame", {"filepath": filepath})
        return json.dumps(r, indent=2)

    @mcp.tool()
    def set_cycles_device(device: str = "GPU") -> str:
        """Set Cycles compute device: GPU or CPU."""
        b = get_blender()
        r = b.send_command("set_cycles_device", {"device": device})
        return json.dumps(r, indent=2)
