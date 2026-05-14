"""
blender-mcp — Config Panel
Model selector with provider browsing, status, connection state.
"""
import bpy
import importlib
from bpy.types import Panel
from .. import PROVIDER_ORDER, PROVIDER_LABELS


class PN_PT_Config(Panel):
    bl_label = "Axiom Engine Config"
    bl_idname = "PN_PT_Config"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, ctx):
        L = self.layout
        c = ctx.scene

        # ── Status ──
        bsock = importlib.import_module("blender_socket")
        box = L.box()
        box.label(text="Status", icon='LINKED')
        row = box.row(align=True)
        is_connected = bsock._socket_server is not None and bsock._socket_server.running
        row.label(text="Socket: Online" if is_connected else "Socket: Offline",
                  icon='CHECKBOX_HLT' if is_connected else 'CHECKBOX_DEHLT')

        # ── Connection status ──
        conn = c.aimcp_connection_status
        if conn:
            row = box.row(align=True)
            icon = 'CHECKBOX_HLT' if "✅" in conn else 'ERROR' if "🔴" in conn else 'SORTTIME' if "🟡" in conn else 'INFO'
            row.label(text=conn, icon=icon)

        L.separator()

        # ── AI Provider & Model ──
        box = L.box()
        box.label(text="AI Model", icon='SETTINGS')
        current = c.aimcp_model or "(none selected)"
        box.label(text=f"Current: {current}")
        row = box.row(align=True)
        row.operator("aimcp.refresh", text="Refresh Models", icon='FILE_REFRESH')

        # ── Provider sections (collapsible) ──
        md = c.aimcp_models
        if md and md.count > 0:
            for prov_id in PROVIDER_ORDER:
                prov_models = [m for m in md.items if m.provider == prov_id]
                if not prov_models:
                    continue

                prop_name = f"aimcp_show_{prov_id.replace('-','_')}"
                is_expanded = getattr(c, prop_name, False)

                box_prov = box.box()
                row = box_prov.row(align=True)
                row.prop(c, prop_name,
                         text=PROVIDER_LABELS.get(prov_id, prov_id),
                         icon='TRIA_DOWN' if is_expanded else 'TRIA_RIGHT',
                         icon_only=False, emboss=False)

                if is_expanded:
                    col = box_prov.column(align=True)
                    for m in prov_models:
                        row = col.row(align=True)
                        if m.model_id == current:
                            row.label(text="", icon='RADIOBUT_ON')
                            row.label(text=f"{m.model_name}")
                        else:
                            op = row.operator("aimcp.select", text=m.model_id, icon='RADIOBUT_OFF')
                            op.model_id = m.model_id
        else:
            row = box.row(align=True)
            row.operator("aimcp.refresh", text="Load models", icon='FILE_REFRESH')

        # ── Agent Mode ──
        row = box.row(align=True)
        row.label(text="Agent Mode:", icon='MODIFIER')
        row.prop(c, "blendermcp_agent_mode", text="")

        # ── Status message ──
        status = c.aimcp_status
        if status:
            L.label(text=status, icon='INFO')
