# blender-mcp — AI Assistant for Blender v0.12.2
# Panels: Config (Properties) + Chat (3D View Sidebar)
# Includes internal HTTP server (port 9878) for direct bpy commands from MCP/HTTP bridge
bl_info = {
    "name": "AI Assistant (blender-mcp)",
    "author": "carlosh7",
    "version": (0, 12, 2),
    "blender": (4, 0, 0),
    "location": "Properties > Scene > AI Config | View3D > Sidebar (N) > AI Chat",
    "description": "AI chat with direct bpy execution in Blender scene.",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}
import bpy, os, json, sys, time, threading, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import blender_socket as bsock
from bpy.types import Panel, Operator, PropertyGroup, UIList
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, CollectionProperty

# ─── Provider API config for fetching model lists ───
_PROVIDER_API = {
    "deepseek": {"url": "https://api.deepseek.com/v1/models", "auth": True},
    "opencode-go": {"url": "https://opencode.ai/zen/go/v1/models", "auth": True},
    "openrouter": {"url": "https://openrouter.ai/api/v1/models", "auth": False},
}
def _get_api_key(provider_id):
    """Get API key for a provider from auth.json or env vars."""
    auth_path = os.path.expanduser("~/.local/share/opencode/auth.json")
    if os.path.exists(auth_path):
        try:
            auth = json.loads(open(auth_path).read())
            entry = auth.get(provider_id)
            if isinstance(entry, dict) and entry.get("key"):
                return entry["key"]
        except: pass
    # Check env vars
    env_map = {"deepseek": "DEEPSEEK_API_KEY", "openrouter": "OPENROUTER_API_KEY"}
    env_var = env_map.get(provider_id)
    if env_var:
        return os.environ.get(env_var)
    return None

SPINNER_FRAMES = ["\u280b", "\u2819", "\u2839", "\u2838", "\u283c", "\u2834", "\u2826", "\u2827", "\u2807", "\u280f"]

# ─── Chat ───
class ChatMsg(PropertyGroup):
    role: StringProperty(); text: StringProperty()

class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg); count: IntProperty(default=0)
    def add(self, r, t): m = self.msgs.add(); m.role = r; m.text = t; self.count = len(self.msgs)
    def clear_all(self):
        while self.msgs: self.msgs.remove(0); self.count = 0

class MCP_UL_Chat(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        tag = "You" if item.role == "user" else "AI" if item.role == "assistant" else "Sys"
        col = layout.column()
        col.scale_y = 1.5
        col.label(text=f"[{tag}]")
        for line in item.text.split("\n"):
            col.label(text=f"  {line[:150]}")

# ─── Model ───
class ModelItem(PropertyGroup):
    model_id: StringProperty(); model_name: StringProperty(); provider: StringProperty()

class ModelsData(PropertyGroup):
    items: CollectionProperty(type=ModelItem); count: IntProperty(default=0)
    def add(self, mid, name, prov):
        m = self.items.add(); m.model_id = mid; m.model_name = name; m.provider = prov; self.count = len(self.items)
    def clear_all(self):
        while self.items: self.items.remove(0); self.count = 0

PROVIDER_ORDER = ["deepseek", "opencode-go", "openrouter"]
PROVIDER_LABELS = {"deepseek": "DeepSeek", "opencode-go": "OpenCode Go", "openrouter": "OpenRouter"}

# ─── Config Panel ───
class PN_PT_Config(Panel):
    bl_label = "AI Assistant Config"; bl_idname = "PN_PT_Config"
    bl_space_type = 'PROPERTIES'; bl_region_type = 'WINDOW'; bl_context = 'scene'

    def draw(self, ctx):
        L = self.layout; c = ctx.scene
        box = L.box()
        box.label(text="Status", icon='LINKED')
        row = box.row(align=True)
        is_connected = bsock._socket_server is not None and bsock._socket_server.running
        if is_connected:
            row.label(text="Socket: Online", icon='CHECKBOX_HLT')
        else:
            row.label(text="Socket: Offline", icon='CHECKBOX_DEHLT')

        L.separator()
        box = L.box()
        box.label(text="AI Model", icon='SETTINGS')
        current = c.aimcp_model or "(reading from opencode.json...)"
        box.label(text=f"Current: {current}")
        row = box.row(align=True)
        row.operator("aimcp.refresh", text="Refresh", icon='FILE_REFRESH')

        md = c.aimcp_models
        if md and md.count > 0:
            for prov_id in PROVIDER_ORDER:
                prov_models = [m for m in md.items if m.provider == prov_id]
                if not prov_models: continue
                prov_box = box.box()
                label = PROVIDER_LABELS.get(prov_id, prov_id)
                row = prov_box.row(align=True); row.label(text=label, icon='DOT')
                for m in prov_models:
                    row = prov_box.row(align=True)
                    if m.model_id == current:
                        row.label(text="", icon='RADIOBUT_ON')
                        row.label(text=f"{m.model_name}  [{m.model_id}]")
                    else:
                        op = row.operator("aimcp.select", text=m.model_id, icon='RADIOBUT_OFF'); op.model_id = m.model_id
        else:
            row = box.row(align=True)
            row.operator("aimcp.refresh", text="Load models", icon='FILE_REFRESH')

        L.separator()
        status = c.aimcp_status
        if status: L.label(text=status, icon='INFO')

# ─── Chat Panel ───
class PN_PT_Chat(Panel):
    bl_label = "MCP AI Chat"; bl_idname = "PN_PT_Chat"
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = 'AI'

    def draw(self, ctx):
        L = self.layout; c = ctx.scene
        state = c.aimcp_ai_state

        # Status bar (model name on top, state below)
        m = c.aimcp_model or "?"
        if len(m) > 18: m = m[:17] + ".."
        if not c.aimcp_connected:
            row = L.row(align=True)
            row.operator("aimcp.check", text="Connect", icon='ADD')
            row.label(text=m)
        elif state == "processing":
            row = L.row(align=True)
            row.operator("aimcp.disconnect", text="", icon='X')
            row.label(text=m)
            idx = c.aimcp_spinner_idx % len(SPINNER_FRAMES)
            row.label(text=SPINNER_FRAMES[idx], icon='SORTTIME')
            row = L.row(align=True)
            row.label(text="Processing...")
        elif state == "no_mcp":
            row = L.row(align=True)
            row.label(text="Socket OK", icon='CHECKBOX_HLT')
            row.label(text="AI Offline", icon='ERROR')
            row = L.row(align=True)
            row.label(text=m)
        elif state == "disconnected":
            row = L.row(align=True)
            row.operator("aimcp.check", text="Connect", icon='ADD')
            row.label(text=m)
        else:
            row = L.row(align=True)
            row.operator("aimcp.disconnect", text="", icon='X')
            row.label(text=m)
            row.label(text="AI Online", icon='CHECKBOX_HLT')

        row.separator()
        row.operator("aimcp.capture", text="", icon='CAMERA_DATA')
        row.operator("aimcp.export", text="", icon='EXPORT')

        L.separator()
        chat = c.aimcp_chat
        if chat and chat.count > 0:
            row = L.row()
            row.template_list("MCP_UL_Chat", "", chat, "msgs", c, "aimcp_chat_index", rows=min(15, max(8, chat.count)))
        else:
            L.label(text="No messages.")

        L.separator()
        row = L.row(align=True); row.scale_y = 3.0; row.prop(c, "aimcp_input", text="")
        row = L.row(align=True); row.scale_y = 1.5
        row.operator("aimcp.send", text="Send to AI", icon='PLAY')
        row.operator("aimcp.clear_chat", text="Clear", icon='X')

# ─── Operators ───
class OP_Check(Operator):
    bl_idname = "aimcp.check"; bl_label = "Check Connection"
    def execute(self, ctx):
        ctx.scene.aimcp_status = "Checking..."
        if ctx.area: ctx.area.tag_redraw()
        connected = bsock._socket_server is not None and bsock._socket_server.running
        ctx.scene.aimcp_connected = connected
        ctx.scene.aimcp_status = "Connected" if connected else "Socket not running"
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_Refresh(Operator):
    bl_idname = "aimcp.refresh"; bl_label = "Refresh"
    def execute(self, ctx):
        ctx.scene.aimcp_status = "Loading..."
        if ctx.area: ctx.area.tag_redraw()

        # Read current model from opencode config
        model = ""
        for p in [os.path.expanduser("~/.config/opencode/opencode.json"),
                  os.path.expanduser("~/Check/opencode.json")]:
            if os.path.exists(p):
                try:
                    d = json.loads(open(p).read())
                    if d.get("model"): model = d["model"]; break
                except: pass

        # Read connected providers from auth.json
        auth_path = os.path.expanduser("~/.local/share/opencode/auth.json")
        providers = []
        if os.path.exists(auth_path):
            try:
                auth = json.loads(open(auth_path).read())
                for prov_id in auth:
                    if isinstance(auth[prov_id], dict) and auth[prov_id].get("key"):
                        providers.append(prov_id)
            except: pass

        # Fetch models from each provider API (in thread)
        def fetch_all():
            all_models = []
            for prov_id in providers:
                cfg = _PROVIDER_API.get(prov_id)
                if not cfg: continue
                try:
                    headers = {"User-Agent": "blender-mcp/0.12", "Accept": "application/json"}
                    if cfg["auth"]:
                        key = _get_api_key(prov_id)
                        if not key: continue
                        headers["Authorization"] = f"Bearer {key}"
                    req = urllib.request.Request(cfg["url"], headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        raw = json.loads(resp.read())
                    raw_list = raw.get("data", raw)
                    if isinstance(raw_list, list):
                        for m in raw_list:
                            mid = m.get("id", "")
                            if not mid: continue
                            all_models.append({
                                "id": mid,
                                "name": m.get("name") or mid.split("/")[-1].replace("-", " ").title(),
                                "provider": prov_id,
                            })
                except: pass

            def update():
                md = ctx.scene.aimcp_models; md.clear_all()
                if model: ctx.scene.aimcp_model = model
                for m in all_models:
                    md.add(m["id"], m["name"], m["provider"])
                prov_count = len(set(m["provider"] for m in all_models))
                prov_names = ", ".join(PROVIDER_LABELS.get(p, p) for p in sorted(set(m["provider"] for m in all_models)))
                ctx.scene.aimcp_status = f"{len(all_models)} models from {prov_count} providers"
                if ctx.area: ctx.area.tag_redraw()
            bpy.app.timers.register(update, first_interval=0.01)

        threading.Thread(target=fetch_all, daemon=True).start()
        return {'FINISHED'}

class OP_SelectModel(Operator):
    bl_idname = "aimcp.select"; bl_label = "Select"
    model_id: StringProperty()
    def execute(self, ctx):
        ctx.scene.aimcp_model = self.model_id; ctx.scene.aimcp_status = f"Selected: {self.model_id}"
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_ApplyModel(Operator):
    bl_idname = "aimcp.apply_model"; bl_label = "Apply"
    model_id: StringProperty()
    def execute(self, ctx):
        mid = self.model_id
        ctx.scene.aimcp_model = mid
        ctx.scene.aimcp_status = "Saved"
        # Write to opencode config
        config_paths = [
            os.path.expanduser("~/.config/opencode/opencode.json"),
            os.path.expanduser("~/Check/opencode.json"),
        ]
        for p in config_paths:
            if os.path.exists(p):
                try:
                    d = json.loads(open(p).read())
                    d["model"] = mid
                    open(p, "w").write(json.dumps(d, indent=2) + "\n")
                    ctx.scene.aimcp_status = f"Saved to {os.path.basename(p)}"
                    break
                except: pass
        if ctx.area: ctx.area.tag_redraw()
        return {'FINISHED'}

class OP_ClearSearch(Operator):
    bl_idname = "aimcp.clear_search"; bl_label = "Clear"
    search_prop: StringProperty()
    def execute(self, ctx):
        if self.search_prop and hasattr(ctx.scene, self.search_prop): setattr(ctx.scene, self.search_prop, "")
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_Disconnect(Operator):
    bl_idname = "aimcp.disconnect"; bl_label = "Disconnect"
    def execute(self, ctx):
        bsock.stop_socket_server()
        ctx.scene.aimcp_connected = False; ctx.scene.aimcp_status = ""
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_Send(Operator):
    bl_idname = "aimcp.send"; bl_label = "Send"
    def execute(self, ctx):
        txt = ctx.scene.aimcp_input.strip()
        if not txt: return {'CANCELLED'}
        ctx.scene.aimcp_chat.add("user", txt)
        ctx.scene.aimcp_input = ""
        ctx.scene.aimcp_waiting = True
        ctx.scene.aimcp_ai_state = "processing"
        ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
        ctx.scene.aimcp_pending_msg_id = ""
        if ctx.area: ctx.area.tag_redraw()
        # Queue message in-process — socket server reads it, MCP responds
        msg_id = str(time.time())
        with bsock._chat_lock:
            bsock._chat_queue.append({"id": msg_id, "message": txt, "timestamp": time.time()})
        ctx.scene.aimcp_pending_msg_id = msg_id
        def check():
            mid = ctx.scene.aimcp_pending_msg_id
            if not mid: return None
            with bsock._chat_lock:
                resp = bsock._chat_responses.pop(mid, None)
            if resp is None: return 1.0
            ctx.scene.aimcp_chat.add("assistant", resp)
            ctx.scene.aimcp_chat_index = ctx.scene.aimcp_chat.count - 1
            ctx.scene.aimcp_status = ""
            ctx.scene.aimcp_waiting = False
            ctx.scene.aimcp_pending_msg_id = ""
            if ctx.area: ctx.area.tag_redraw()
            return None
        bpy.app.timers.register(check, first_interval=0.5)
        return {'FINISHED'}

class OP_Capture(Operator):
    bl_idname = "aimcp.capture"; bl_label = "Capture"
    def execute(self, ctx):
        n = len(bpy.data.objects); m = sum(1 for o in bpy.data.objects if o.type == 'MESH')
        ctx.scene.aimcp_chat.add("system", f"Scene: {n} objects, {m} meshes")
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_Export(Operator):
    bl_idname = "aimcp.export"; bl_label = "Export"
    def execute(self, ctx):
        out = os.path.expanduser("~/blender-mcp/models/scene.glb")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
        ctx.scene.aimcp_chat.add("system", "Exported")
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

class OP_ClearChat(Operator):
    bl_idname = "aimcp.clear_chat"; bl_label = "Clear"
    def execute(self, ctx):
        ctx.scene.aimcp_chat.clear_all()
        if ctx.area: ctx.area.tag_redraw(); return {'FINISHED'}

# ─── Register ───
classes = [
    ChatMsg, ChatData, MCP_UL_Chat, ModelItem, ModelsData,
    OP_Check, OP_Refresh, OP_SelectModel, OP_ApplyModel, OP_ClearSearch,
    OP_Disconnect, OP_Send, OP_Capture, OP_Export, OP_ClearChat,
    PN_PT_Config, PN_PT_Chat,
]

def register():
    for cls in classes: bpy.utils.register_class(cls)
    Scene = bpy.types.Scene
    Scene.aimcp_chat = PointerProperty(type=ChatData)
    Scene.aimcp_input = StringProperty(default="")
    Scene.aimcp_connected = BoolProperty(default=False)
    Scene.aimcp_refreshing = BoolProperty(default=False)
    Scene.aimcp_waiting = BoolProperty(default=False)
    Scene.aimcp_pending_msg_id = StringProperty(default="")
    Scene.aimcp_chat_index = IntProperty(default=0)
    Scene.aimcp_model = StringProperty(default="")
    Scene.aimcp_status = StringProperty(default="")
    Scene.aimcp_models = PointerProperty(type=ModelsData)
    Scene.aimcp_ai_state = StringProperty(default="connected")
    Scene.aimcp_spinner_idx = IntProperty(default=0)
    for pid in PROVIDER_ORDER:
        setattr(Scene, f"aimcp_search_{pid.replace('-','_')}", StringProperty(default=""))

    # ─── Timers (CRITICAL: must always register) ───

    def _redraw_areas():
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type in ('VIEW_3D', 'PROPERTIES'):
                    area.tag_redraw()

    # Spinner animation (0.3s)
    def spinner_tick():
        any_waiting = False
        for s in bpy.data.scenes:
            if s.aimcp_waiting:
                s.aimcp_spinner_idx = (s.aimcp_spinner_idx + 1) % len(SPINNER_FRAMES)
                any_waiting = True
        if any_waiting:
            _redraw_areas()
        return 0.3
    bpy.app.timers.register(spinner_tick, first_interval=0.3)

    # Health check (5s) — checks socket + MCP state
    def health_check():
        changed = False
        now = time.time()
        # Auto-reset mcp_connected if no ping in 15s
        if bsock.mcp_connected and now - bsock.mcp_last_ping > 15:
            bsock.mcp_connected = False
        for s in bpy.data.scenes:
            old_state = s.aimcp_ai_state
            old_conn = s.aimcp_connected
            is_connected = bsock._socket_server is not None and bsock._socket_server.running
            s.aimcp_connected = is_connected
            if s.aimcp_waiting:
                s.aimcp_ai_state = "processing"
            elif not is_connected:
                s.aimcp_ai_state = "disconnected"
            elif bsock.mcp_connected:
                s.aimcp_ai_state = "connected"
            else:
                s.aimcp_ai_state = "no_mcp"
            if s.aimcp_ai_state != old_state or s.aimcp_connected != old_conn:
                changed = True
        if changed:
            _redraw_areas()
        return 5.0
    bpy.app.timers.register(health_check, first_interval=1.0)

    # ─── Socket server (replaces HTTP bridge) ───
    try:
        bsock.start_socket_server()
    except:
        print("[blender-mcp] Socket server failed")

def unregister():
    bsock.stop_socket_server()
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    attrs = ["aimcp_models", "aimcp_status", "aimcp_model",
             "aimcp_pending_msg_id", "aimcp_chat_index", "aimcp_waiting", "aimcp_refreshing",
             "aimcp_connected", "aimcp_input", "aimcp_chat",
             "aimcp_ai_state", "aimcp_spinner_idx"]
    for pid in PROVIDER_ORDER:
        attrs.append(f"aimcp_search_{pid.replace('-','_')}")
    for a in attrs:
        if hasattr(bpy.types.Scene, a):
            try: delattr(bpy.types.Scene, a)
            except: pass

if __name__ == "__main__":
    register()
