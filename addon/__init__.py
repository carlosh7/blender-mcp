# blender-mcp v0.8.0 — Embedded-first Blender MCP
# Cero configuración: el addon auto-instala dependencias y arranca el servidor.
bl_info = {
    "name": "AXIOM Precision Engine",
    "author": "CarlosH & Antigravity",
    "version": (0, 8, 2),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Axiom tab",
    "description": "AI-powered Blender MCP — 82 tools, 5 integrations. Zero-config.",
    "doc_url": "https://github.com/carlosh7/blender-mcp",
    "category": "3D View",
}

import bpy, os, json, time, mathutils, sys, subprocess, importlib
from pathlib import Path
from bpy.props import StringProperty, IntProperty, CollectionProperty, BoolProperty, PointerProperty
from bpy.types import Panel, Operator, PropertyGroup, UIList

sys.path.insert(0, os.path.dirname(__file__))
import blender_socket as bsock
from . import spatial

# ─── Auto-install pip dependencies (first time only) ───
_REQUIRED_PACKAGES = ["mcp>=1.3.0", "requests>=2.25.0"]

def _ensure_deps():
    """Install missing pip packages into Blender's Python."""
    for pkg in _REQUIRED_PACKAGES:
        try:
            pkg_name = pkg.split(">=")[0].split("==")[0].split("<")[0]
            importlib.import_module(pkg_name)
        except ImportError:
            print(f"[blender-mcp] Installing {pkg}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                    timeout=60,
                )
                print(f"[blender-mcp] ✅ {pkg} installed")
            except Exception as e:
                print(f"[blender-mcp] ⚠️  Could not install {pkg}: {e}")

# ─── Auto-start embedded MCP server + external auto-process at startup ───
_EMBEDDED_STARTED = False
_MCP_PROCESS = None

def _start_embedded():
    global _EMBEDDED_STARTED
    if _EMBEDDED_STARTED:
        return
    try:
        from .server import start_embedded_server
        start_embedded_server()
        _EMBEDDED_STARTED = True
        print("[blender-mcp] ✅ Embedded MCP server ready on :45677")
    except Exception as e:
        print(f"[blender-mcp] ⚠️  Embedded server: {e}")

def _start_mcp_process():
    """Start mcp_server.py as a subprocess so _auto_process runs."""
    global _MCP_PROCESS
    if _MCP_PROCESS is not None:
        return
    try:
        import subprocess, sys
        root = os.path.dirname(__file__)
        server_script = os.path.join(root, "..", "mcp_server.py")
        if os.path.exists(server_script):
            _MCP_PROCESS = subprocess.Popen(
                [sys.executable, server_script],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            print(f"[blender-mcp] ✅ MCP auto-process started (PID {_MCP_PROCESS.pid})")
    except Exception as e:
        print(f"[blender-mcp] ⚠️  Could not start MCP process: {e}")

def _stop_mcp_process():
    global _MCP_PROCESS
    if _MCP_PROCESS:
        try:
            _MCP_PROCESS.terminate()
            _MCP_PROCESS.wait(timeout=5)
        except:
            try:
                _MCP_PROCESS.kill()
            except:
                pass
        _MCP_PROCESS = None
        print("[blender-mcp] MCP auto-process stopped")

SPINNER_FRAMES = ["\u280b", "\u2819", "\u2839", "\u2838", "\u283c", "\u2834", "\u2826", "\u2827", "\u2807", "\u280f"]

# ─── Persistencia ───
def get_history_path():
    """Devuelve la ruta del chat solo si el archivo .blend está guardado."""
    blend_path = bpy.data.filepath
    if not blend_path: return None
    return blend_path + ".chat"

def load_history(chat):
    path = get_history_path()
    if not path:
        chat.msgs.clear()
        chat.count = 0
        return
    
    chat.msgs.clear()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.loads(f.read())
                for m in data:
                    item = chat.msgs.add()
                    item.role = m['role']; item.text = m['text']
            chat.count = len(chat.msgs)
        except: pass

def wrap_text(text, max_chars=45):
    lines = []
    for p in text.split("\n"):
        if not p: lines.append(""); continue
        words = p.split()
        curr = []
        curr_len = 0
        for w in words:
            if curr_len + len(w) > max_chars:
                lines.append(" ".join(curr)); curr = [w]; curr_len = len(w)
            else:
                curr.append(w); curr_len += len(w) + 1
        if curr: lines.append(" ".join(curr))
    return lines

def save_history(chat):
    path = get_history_path()
    if not path: return
    
    # Reagrupamos las líneas en mensajes completos para el archivo JSON
    full_msgs = []
    curr_text = []
    curr_role = ""
    
    for m in chat.msgs:
        if m.role == 'status': continue
        if m.is_new:
            if curr_role:
                full_msgs.append({"role": curr_role, "text": " ".join(curr_text)})
            curr_role = m.role
            curr_text = [m.text]
        else:
            curr_text.append(m.text)
            
    if curr_role:
        full_msgs.append({"role": curr_role, "text": " ".join(curr_text)})
        
    try:
        with open(path, 'w') as f:
            f.write(json.dumps(full_msgs, indent=2))
    except: pass

# ─── Chat ───
class ChatMsg(PropertyGroup):
    role: StringProperty()
    text: StringProperty()
    is_new: BoolProperty(default=False)

class ChatData(PropertyGroup):
    msgs: CollectionProperty(type=ChatMsg)
    count: IntProperty(default=0)
    def add(self, r, t, is_update=False, scene=None):
        # Detectamos si el usuario ya estaba al final para decidir si le seguimos (Smart Scroll)
        was_at_bottom = False
        if scene:
            was_at_bottom = (scene.aimcp_chat_index >= len(self.msgs) - 1)

        if is_update:
            while len(self.msgs) > 0 and self.msgs[-1].role == r and not self.msgs[-1].is_new:
                self.msgs.remove(len(self.msgs)-1)
            if len(self.msgs) > 0 and self.msgs[-1].role == r and self.msgs[-1].is_new:
                self.msgs.remove(len(self.msgs)-1)

        lines = wrap_text(t)
        for i, l_txt in enumerate(lines):
            m = self.msgs.add()
            m.role = r; m.text = l_txt
            m.is_new = (i == 0)
            
        self.count = len(self.msgs)
        # Scroll inteligente: bajamos si ya estábamos al final o si es un mensaje nuevo tuyo
        if scene and (was_at_bottom or r == 'user' or (not is_update and r == 'assistant')):
            scene.aimcp_chat_index = self.count - 1
        save_history(self)

    def clear_all(self):
        # Limpiamos TODAS las escenas para evitar resurrecciones del archivo
        for s in bpy.data.scenes:
            while s.aimcp_chat.msgs:
                s.aimcp_chat.msgs.remove(0)
            s.aimcp_chat.count = 0
        txt_block = bpy.data.texts.get("aimcp_chat_history")
        if txt_block:
            bpy.data.texts.remove(txt_block)

# --- Chat Drawing ---

class MCP_UL_Chat(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if not item: return
        row = layout.row(align=True)
        if item.is_new:
            tag = "Usted" if item.role == "user" else "IA" if item.role == "assistant" else "Pensando" if item.role == "status" else "Sys"
            row.label(text=f"[{tag}] {item.text}")
        else:
            row.label(text=f"      {item.text}")

# ─── Model ───
class ModelItem(PropertyGroup):
    model_id: StringProperty(); model_name: StringProperty(); provider: StringProperty()

class ModelsData(PropertyGroup):
    items: CollectionProperty(type=ModelItem); count: IntProperty(default=0)
    def add(self, mid, name, prov):
        m = self.items.add(); m.model_id = mid; m.model_name = name; m.provider = prov; self.count = len(self.items)
    def clear_all(self):
        while self.items: self.items.remove(0); self.count = 0

PROVIDER_ORDER = ["google", "anthropic", "deepseek", "opencode-go", "openrouter"]
PROVIDER_LABELS = {
    "google": "Google Gemini", 
    "anthropic": "Anthropic Claude",
    "deepseek": "DeepSeek", 
    "opencode-go": "OpenCode Go", 
    "openrouter": "OpenRouter"
}

# ─── Panels (modulares) — importados de addon/panels/ ───
from .panels import chat as _chat_panel, config as _config_panel, integrations as _integrations

# ─── Register (modular) ───
from . import properties as _props
from . import preferences as _prefs
from .operators import connect as _conn_ops
from .operators import chat as _chat_ops
from .operators import capture as _capture_ops
from .operators import export as _export_ops
from .operators import setup as _setup_ops
from .operators import embedded as _embedded_ops
from .operators import model_ops as _model_ops
from .panels.chat import BLENDERMCP_OT_OpenWeb

classes = [
    ChatMsg, ChatData, MCP_UL_Chat, ModelItem, ModelsData,
    BLENDERMCP_OT_OpenWeb,
]

def register():
    # 0. Auto-dependencies + embedded server + auto-process + client
    _ensure_deps()
    _start_embedded()
    _start_mcp_process()
    try:
        from .operators.embedded import auto_start
        auto_start()
    except Exception as e:
        print(f"[blender-mcp] auto_start: {e}")

    # 1. Module-level registrations
    _props.register_properties()
    _prefs.register_preferences()
    _conn_ops.register_connect_operators()
    _chat_ops.register_chat_operators()
    _capture_ops.register_capture_operators()
    _export_ops.register_export_operators()
    _setup_ops.register_setup_operators()
    _embedded_ops.register_embedded_operators()
    _model_ops.register_model_operators()

    # Register modular panels
    for panel_cls in [_chat_panel.PN_PT_Chat, _config_panel.PN_PT_Config]:
        bpy.utils.register_class(panel_cls)
    for panel_cls in _integrations.PANELS:
        bpy.utils.register_class(panel_cls)

    # 2. Core classes
    for cls in classes:
        bpy.utils.register_class(cls)

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
    Scene.aimcp_connection_status = StringProperty(default="")
    for pid in PROVIDER_ORDER:
        setattr(Scene, f"aimcp_search_{pid.replace('-','_')}", StringProperty(default=""))
        setattr(Scene, f"aimcp_show_{pid.replace('-','_')}", BoolProperty(default=False))

    # ─── Timers (CRITICAL: must always register) ───
    def delayed_load():
        for s in bpy.data.scenes:
            load_history(s.aimcp_chat)
        try:
            bpy.ops.aimcp.refresh()
        except:
            pass
        return None
    bpy.app.timers.register(delayed_load, first_interval=0.5)

    def _redraw_areas():
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type in ('VIEW_3D', 'PROPERTIES'):
                    area.tag_redraw()

    def spinner_tick():
        any_waiting = False
        for s in bpy.data.scenes:
            if s.aimcp_waiting:
                s.aimcp_spinner_idx = (s.aimcp_spinner_idx + 1) % len(SPINNER_FRAMES)
                any_waiting = True
        if any_waiting:
            _redraw_areas()
        return 0.1
    bpy.app.timers.register(spinner_tick, first_interval=0.1)

    def health_check():
        changed = False
        now = time.time()
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
        return 1.0
    bpy.app.timers.register(health_check, first_interval=0.1)

    try:
        bsock.start_socket_server()
    except:
        print("[blender-mcp] Socket server failed")

def unregister():
    try:
        from .operators.embedded import auto_stop
        auto_stop()
    except:
        pass
    _stop_mcp_process()
    bsock.stop_socket_server()
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass
    for panel_cls in reversed([_chat_panel.PN_PT_Chat, _config_panel.PN_PT_Config]):
        try:
            bpy.utils.unregister_class(panel_cls)
        except:
            pass
    for panel_cls in reversed(_integrations.PANELS):
        try:
            bpy.utils.unregister_class(panel_cls)
        except:
            pass
    _conn_ops.unregister_connect_operators()
    _chat_ops.unregister_chat_operators()
    _capture_ops.unregister_capture_operators()
    _export_ops.unregister_export_operators()
    _model_ops.unregister_model_operators()
    _embedded_ops.unregister_embedded_operators()
    _setup_ops.unregister_setup_operators()
    _prefs.unregister_preferences()
    _props.unregister_properties()

    attrs = ["aimcp_models", "aimcp_status", "aimcp_model",
             "aimcp_pending_msg_id", "aimcp_chat_index", "aimcp_waiting", "aimcp_refreshing",
             "aimcp_connected", "aimcp_input", "aimcp_chat",
             "aimcp_ai_state", "aimcp_spinner_idx", "aimcp_connection_status"]
    for pid in PROVIDER_ORDER:
        attrs.append(f"aimcp_search_{pid.replace('-','_')}")
    for a in attrs:
        if hasattr(bpy.types.Scene, a):
            try:
                delattr(bpy.types.Scene, a)
            except:
                pass

if __name__ == "__main__":
    register()
