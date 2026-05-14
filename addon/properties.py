"""
blender-mcp — Scene Properties
All shared bpy.types.Scene properties for integrations and UI state.
"""
import bpy
from bpy.props import (
    BoolProperty, StringProperty, IntProperty, FloatProperty,
    EnumProperty, PointerProperty, CollectionProperty,
)
from bpy.types import PropertyGroup


def register_properties():
    """Register all shared properties onto bpy.types.Scene."""
    Scene = bpy.types.Scene

    # ─── Integration Toggles (Fase 1) ───
    Scene.blendermcp_port = IntProperty(
        name="MCP Port", default=9876, min=1024, max=65535,
        description="Port for the Blender MCP socket server",
    )
    Scene.blendermcp_server_running = BoolProperty(default=False)

    # Poly Haven
    Scene.blendermcp_use_polyhaven = BoolProperty(
        name="Use Poly Haven", default=False,
        description="Enable Poly Haven HDRI/texture/model downloads",
    )

    # Sketchfab
    Scene.blendermcp_use_sketchfab = BoolProperty(
        name="Use Sketchfab", default=False,
        description="Enable Sketchfab model search and download",
    )
    Scene.blendermcp_sketchfab_api_key = StringProperty(
        name="Sketchfab API Key", default="", subtype='PASSWORD',
    )

    # Hyper3D Rodin
    Scene.blendermcp_use_hyper3d = BoolProperty(
        name="Use Hyper3D Rodin", default=False,
        description="Enable AI 3D model generation via Hyper3D Rodin",
    )
    Scene.blendermcp_hyper3d_mode = EnumProperty(
        name="Rodin Mode", default='MAIN_SITE',
        items=[
            ('MAIN_SITE', "Main Site", "Use hyper3d.ai (free trial or private key)"),
            ('FAL_AI', "FAL AI", "Use fal.ai (private key required)"),
        ],
    )
    Scene.blendermcp_hyper3d_api_key = StringProperty(
        name="Rodin API Key", default="", subtype='PASSWORD',
    )

    # Hunyuan3D
    Scene.blendermcp_use_hunyuan3d = BoolProperty(
        name="Use Hunyuan3D", default=False,
        description="Enable Tencent Hunyuan 3D model generation",
    )
    Scene.blendermcp_hunyuan3d_mode = EnumProperty(
        name="Hunyuan3D Mode", default='OFFICIAL_API',
        items=[
            ('OFFICIAL_API', "Official API", "Use Tencent Cloud API"),
            ('LOCAL_API', "Local API", "Use local Hunyuan3D API server"),
        ],
    )
    Scene.blendermcp_hunyuan3d_secret_id = StringProperty(
        name="SecretId", default="", subtype='PASSWORD',
    )
    Scene.blendermcp_hunyuan3d_secret_key = StringProperty(
        name="SecretKey", default="", subtype='PASSWORD',
    )
    Scene.blendermcp_hunyuan3d_api_url = StringProperty(
        name="API URL", default="http://localhost:8080",
    )
    Scene.blendermcp_hunyuan3d_octree_resolution = IntProperty(
        name="Octree Resolution", default=256, min=128, max=512,
    )
    Scene.blendermcp_hunyuan3d_num_inference_steps = IntProperty(
        name="Inference Steps", default=50, min=10, max=200,
    )
    Scene.blendermcp_hunyuan3d_guidance_scale = FloatProperty(
        name="Guidance Scale", default=5.0, min=1.0, max=20.0,
    )
    Scene.blendermcp_hunyuan3d_texture = BoolProperty(
        name="Generate Texture", default=True,
    )

    # AmbientCG
    Scene.blendermcp_use_ambientcg = BoolProperty(
        name="Use AmbientCG", default=False,
        description="Enable AmbientCG PBR material downloads",
    )

    # ─── Provider selector (Config panel) ───
    Scene.aimcp_provider = StringProperty(
        name="Provider", default="opencode-go",
        description="Current LLM provider ID",
    )

    # ─── Agent Mode (Fase 4) ───
    Scene.blendermcp_agent_mode = EnumProperty(
        name="Agent Mode", default='AUTO',
        items=[
            ('AUTO', "Auto", "Use proxy if external MCP client connected, else autonomous"),
            ('PROXY', "Proxy", "Only use external MCP client (Claude/Cursor)"),
            ('AUTONOMOUS', "Autonomous", "Always use built-in agent (no external client needed)"),
        ],
        description="AI agent operation mode",
    )


def unregister_properties():
    """Clean up all registered properties."""
    attrs = [
        "blendermcp_port", "blendermcp_server_running",
        "blendermcp_use_polyhaven",
        "blendermcp_use_sketchfab", "blendermcp_sketchfab_api_key",
        "blendermcp_use_hyper3d", "blendermcp_hyper3d_mode", "blendermcp_hyper3d_api_key",
        "blendermcp_use_hunyuan3d", "blendermcp_hunyuan3d_mode",
        "blendermcp_hunyuan3d_secret_id", "blendermcp_hunyuan3d_secret_key",
        "blendermcp_hunyuan3d_api_url", "blendermcp_hunyuan3d_octree_resolution",
        "blendermcp_hunyuan3d_num_inference_steps", "blendermcp_hunyuan3d_guidance_scale",
        "blendermcp_hunyuan3d_texture",
        "blendermcp_use_ambientcg",
        "aimcp_provider",
        "blendermcp_agent_mode",
    ]
    for a in attrs:
        if hasattr(bpy.types.Scene, a):
            try:
                delattr(bpy.types.Scene, a)
            except:
                pass
