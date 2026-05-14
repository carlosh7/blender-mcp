"""
blender-mcp — Integrations Panel
Toggles for Poly Haven, Sketchfab, Hyper3D, Hunyuan3D, AmbientCG
Adds a "Setup" section with Local Setup buttons.
"""
import bpy
from bpy.types import Panel


class PN_PT_Integrations(Panel):
    bl_label = "Integrations"
    bl_idname = "PN_PT_Integrations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Axiom'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, ctx):
        L = self.layout
        scene = ctx.scene

        L.label(text="Asset Providers", icon='ASSET_MANAGER')

        # Poly Haven
        box = L.box()
        row = box.row(align=True)
        row.prop(scene, "blendermcp_use_polyhaven", text="")
        row.label(text="Poly Haven", icon='WORLD')
        if scene.blendermcp_use_polyhaven:
            box.label(text="   HDRI / Textures / Models", icon='FILE_IMAGE')

        # Sketchfab
        box = L.box()
        row = box.row(align=True)
        row.prop(scene, "blendermcp_use_sketchfab", text="")
        row.label(text="Sketchfab", icon='URL')
        if scene.blendermcp_use_sketchfab:
            box.prop(scene, "blendermcp_sketchfab_api_key", text="API Key")

        # Hyper3D Rodin
        box = L.box()
        row = box.row(align=True)
        row.prop(scene, "blendermcp_use_hyper3d", text="")
        row.label(text="Hyper3D Rodin", icon='MESH_CUBE')
        if scene.blendermcp_use_hyper3d:
            box.prop(scene, "blendermcp_hyper3d_mode", text="Mode")
            box.prop(scene, "blendermcp_hyper3d_api_key", text="API Key")
            box.operator("blendermcp.set_hyper3d_free_trial", text="Set Free Trial Key", icon='ADD')

        # Hunyuan3D
        box = L.box()
        row = box.row(align=True)
        row.prop(scene, "blendermcp_use_hunyuan3d", text="")
        row.label(text="Hunyuan3D", icon='MESH_MONKEY')
        if scene.blendermcp_use_hunyuan3d:
            box.prop(scene, "blendermcp_hunyuan3d_mode", text="Mode")
            if scene.blendermcp_hunyuan3d_mode == 'OFFICIAL_API':
                box.prop(scene, "blendermcp_hunyuan3d_secret_id", text="SecretId")
                box.prop(scene, "blendermcp_hunyuan3d_secret_key", text="SecretKey")
            elif scene.blendermcp_hunyuan3d_mode == 'LOCAL_API':
                box.prop(scene, "blendermcp_hunyuan3d_api_url", text="API URL")
                box.prop(scene, "blendermcp_hunyuan3d_octree_resolution", text="Resolution")
                box.prop(scene, "blendermcp_hunyuan3d_num_inference_steps", text="Steps")
                box.prop(scene, "blendermcp_hunyuan3d_guidance_scale", text="Guidance")

        # AmbientCG
        box = L.box()
        row = box.row(align=True)
        row.prop(scene, "blendermcp_use_ambientcg", text="")
        row.label(text="AmbientCG (PBR)", icon='TEXTURE')

        L.separator()
        L.label(text="Setup", icon='TOOL_SETTINGS')
        box = L.box()
        row = box.row(align=True)
        row.operator("blendermcp.install_deps", text="Deps", icon='PREFERENCES')
        row.operator("blendermcp.copy_config", text="Config", icon='COPY_ID')
        row.operator("blendermcp.open_logs", text="Logs", icon='TEXT')
        row.operator("blendermcp.health_check", text="Check", icon='VIEWZOOM')


PANELS = [PN_PT_Integrations]
