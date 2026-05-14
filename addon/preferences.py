"""
blender-mcp — Addon Preferences
Telemetry consent + general addon settings.
"""
import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences
from bpy.utils import register_class, unregister_class


class BLENDERMCP_AddonPreferences(AddonPreferences):
    bl_idname = __package__ or "blender-mcp"

    telemetry_consent: BoolProperty(
        name="Allow Telemetry",
        default=True,
        description="Collect anonymous usage data to help improve blender-mcp",
    )

    def draw(self, context):
        L = self.layout
        box = L.box()
        box.label(text="Telemetry & Privacy:", icon='PREFERENCES')
        row = box.row()
        row.prop(self, "telemetry_consent", text="Allow anonymous telemetry")
        if self.telemetry_consent:
            row = box.row()
            row.label(text="   Collects: tool names, success/failure, duration", icon='INFO')
        else:
            row = box.row()
            row.label(text="   Only minimal anonymous data collected", icon='INFO')
        row = box.row()
        row.label(text="DISABLE_TELEMETRY=true to disable completely", icon='FILE_SCRIPT')


def register_preferences():
    try:
        register_class(BLENDERMCP_AddonPreferences)
    except:
        pass


def unregister_preferences():
    try:
        unregister_class(BLENDERMCP_AddonPreferences)
    except:
        pass
