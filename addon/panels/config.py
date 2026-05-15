"""
blender-mcp — Config Panel
Model selector with provider browsing, status, connection state.
"""
import bpy
import os
from bpy.types import Panel
from .. import PROVIDER_ORDER, PROVIDER_LABELS
from .. import _axsock as bsock

def _docs_installed():
    api_dir = os.path.join(os.path.dirname(__file__), "..", "data", "api")
    return os.path.exists(api_dir) and len(os.listdir(api_dir)) > 10


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
        box = L.box()
        box.label(text="Status", icon='LINKED')

        is_connected = bsock._socket_server is not None and bsock._socket_server.running
        row = box.row(align=True)
        row.label(text="Socket:" + (" Online" if is_connected else " Offline"),
                  icon='CHECKBOX_HLT' if is_connected else 'CHECKBOX_DEHLT')

        is_mcp = bsock.mcp_connected
        row = box.row(align=True)
        row.label(text="MCP:" + (" Connected" if is_mcp else " Waiting"),
                  icon='CHECKBOX_HLT' if is_mcp else 'SORTTIME')

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

        # ── Documentation ──
        L.separator()
        box = L.box()
        box.label(text="Documentación API", icon='INFO')
        if _docs_installed():
            row = box.row(align=True)
            row.label(text="", icon='CHECKBOX_HLT')
            row.label(text="Docs instalados")
            row = box.row(align=True)
            row.prop(c, "aimcp_use_rst", text="Usar RST (búsqueda más precisa)")
        else:
            status = c.aimcp_docs_status
            if status:
                row = box.row(align=True)
                row.label(text=status, icon='INFO')
            row = box.row(align=True)
            row.operator("aimcp.download_docs", text="Descargar RST Docs", icon='DOWNLOAD')
            row = box.row(align=True)
            row.label(text="15 MB — descarga única", icon='INFO')

        # ── Setup ──
        L.separator()
        box = L.box()
        box.label(text="Setup", icon='TOOL_SETTINGS')
        row = box.row(align=True)
        row.operator("blendermcp.install_deps", text="Deps", icon='PREFERENCES')
        row.operator("blendermcp.copy_config", text="Config", icon='COPY_ID')
        row.operator("blendermcp.open_logs", text="Logs", icon='TEXT')
        row.operator("blendermcp.health_check", text="Check", icon='VIEWZOOM')

        # ── Status message ──
        L.separator()
        status = c.aimcp_status
        if status:
            L.label(text=status, icon='INFO')
