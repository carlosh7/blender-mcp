# blender-mcp v0.8.111 — Extension for Blender 4.2+
# Config via blender_manifest.toml
import bpy, os, json, time, mathutils, sys, threading, subprocess, importlib, traceback
from pathlib import Path
from bpy.props import StringProperty, IntProperty, CollectionProperty, BoolProperty, PointerProperty
from bpy.types import Panel, Operator, PropertyGroup, UIList

from . import _axsock as bsock
from . import spatial

# ─── Auto-install pip dependencies + auto-start servers ───
_EMBEDDED_STARTED = False
_DEPS_INSTALLED = False

def _ensure_deps():
    global _DEPS_INSTALLED
    if _DEPS_INSTALLED:
        return
    packages = []
    for pkg_name, import_name in [("mcp", "mcp"), ("requests", "requests")]:
        try:
            __import__(import_name)
        except ImportError:
            packages.append(pkg_name)
    if not packages:
        _DEPS_INSTALLED = True
        return
    print(f"[blender-mcp] Instalando dependencias: {', '.join(packages)}...")
    for pkg in packages:
        try:
            cmd = [sys.executable, "-m", "pip", "install", pkg, "--quiet"]
            # PEP 668 / externally-managed-environment workaround
            if sys.prefix != sys.base_prefix:
                pass  # dentro de venv, no hace falta flag
            else:
                cmd.append("--break-system-packages")
            subprocess.check_call(cmd, timeout=120)
            print(f"[blender-mcp] ✅ {pkg} instalado")
            _DEPS_INSTALLED = True
        except subprocess.CalledProcessError as e:
            print(f"[blender-mcp] ⚠️  No se pudo instalar {pkg}: {e}")
        except Exception as e:
            print(f"[blender-mcp] ⚠️  Error instalando {pkg}: {e}")

def _start_embedded():
    global _EMBEDDED_STARTED
    if _EMBEDDED_STARTED:
        return
    try:
        from .server import start_embedded_server
        start_embedded_server()
        _EMBEDDED_STARTED = True
        print("[blender-mcp] ✅ Embedded MCP server ready on :45677")
    except ImportError as e:
        print(f"[blender-mcp] ⚠️  Embedded server requiere mcp SDK: {e}")
    except Exception as e:
        print(f"[blender-mcp] ⚠️  Embedded server: {e}")

SPINNER_FRAMES = ["\u280b", "\u2819", "\u2839", "\u2838", "\u283c", "\u2834", "\u2826", "\u2827", "\u2807", "\u280f"]

# ─── Persistencia (per-project con fallback global) ───
GLOBAL_CHAT_LOG = os.path.expanduser("~/.config/blender-mcp/chat_log.json")

def get_history_path():
    """Por proyecto: junto al .blend. Si no está guardado: global."""
    blend_path = bpy.data.filepath
    if blend_path:
        return blend_path + ".chat"
    return GLOBAL_CHAT_LOG

def load_history(chat):
    path = get_history_path()
    if not path:
        chat.msgs.clear()
        chat.count = 0
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
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

# ─── Model ───
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
from .properties import ChatMsg, ChatData, MCP_UL_Chat, ModelItem, ModelsData
from . import properties as _props
from . import preferences as _prefs
from .operators import connect as _conn_ops
from .operators import chat as _chat_ops
from .operators import capture as _capture_ops
from .operators import export as _export_ops
from .operators import setup as _setup_ops
from .operators import embedded as _embedded_ops
from .operators import model_ops as _model_ops
from .panels.chat import BLENDERMCP_OT_OpenWeb, BLENDERMCP_OT_InsertCommand

classes = [
    ChatMsg, ChatData, MCP_UL_Chat, ModelItem, ModelsData,
    BLENDERMCP_OT_OpenWeb, BLENDERMCP_OT_InsertCommand,
]

def register():
    _ensure_deps()
    _start_embedded()
    try:
        import importlib
        from . import auto_process as _ap
        importlib.reload(_ap)
        _ap.start()
    except Exception as e:
        print(f"[blender-mcp] auto_process: {e}")
    try:
        from . import auto_config
        auto_config.start()
    except Exception as e:
        print(f"[blender-mcp] auto_config: {e}")
    try:
        from .operators.embedded import auto_start
        auto_start()
    except Exception as e:
        print(f"[blender-mcp] auto_start: {e}")

    # ⚡ Socket server (temprano, antes de registros que puedan fallar)
    try:
        bsock.start_socket_server()
        print("[blender-mcp] ✅ Socket server on :9876")
    except Exception as e:
        print(f"[blender-mcp] ⚠️  Socket server: {e}")

    # 1. Register RNA classes FIRST (needed by PointerProperty)
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except:
            pass

    # 2. Module-level registrations (properties depends on RNA classes)
    for fn in [_props.register_properties, _prefs.register_preferences,
               _conn_ops.register_connect_operators, _chat_ops.register_chat_operators,
               _capture_ops.register_capture_operators, _export_ops.register_export_operators,
               _setup_ops.register_setup_operators, _embedded_ops.register_embedded_operators,
               _model_ops.register_model_operators]:
        try:
            fn()
        except:
            pass

    # Register modular panels
    for panel_cls in [_chat_panel.PN_PT_Chat, _config_panel.PN_PT_Config]:
        try:
            bpy.utils.register_class(panel_cls)
        except:
            pass
    for panel_cls in _integrations.PANELS:
        try:
            bpy.utils.register_class(panel_cls)
        except:
            pass


    Scene = bpy.types.Scene
    _scene_props = {
        "aimcp_chat": PointerProperty(type=ChatData),
        "aimcp_input": StringProperty(default=""),
        "aimcp_connected": BoolProperty(default=False),
        "aimcp_refreshing": BoolProperty(default=False),
        "aimcp_waiting": BoolProperty(default=False),
        "aimcp_pending_msg_id": StringProperty(default=""),
        "aimcp_chat_index": IntProperty(default=0),
        "aimcp_model": StringProperty(default=""),
        "aimcp_status": StringProperty(default=""),
        "aimcp_models": PointerProperty(type=ModelsData),
        "aimcp_ai_state": StringProperty(default="connected"),
        "aimcp_spinner_idx": IntProperty(default=0),
        "aimcp_connection_status": StringProperty(default=""),
    }
    for name, prop in _scene_props.items():
        try:
            setattr(Scene, name, prop)
        except:
            pass
    for pid in PROVIDER_ORDER:
        try:
            setattr(Scene, f"aimcp_search_{pid.replace('-','_')}", StringProperty(default=""))
            setattr(Scene, f"aimcp_show_{pid.replace('-','_')}", BoolProperty(default=False))
        except:
            pass

    try:
        from .operators.model_ops import _status_ticker
        bpy.app.timers.register(_status_ticker, first_interval=0.2)
    except:
        pass

    # ─── Timers (CRITICAL: must always register) ───
    _delayed_step = 0

    def delayed_load():
        nonlocal _delayed_step
        _delayed_step += 1

        if _delayed_step == 1:
            for s in bpy.data.scenes:
                load_history(s.aimcp_chat)
            try:
                bpy.ops.aimcp.refresh()
            except:
                pass
            return 2.0

        if _delayed_step == 2:
            model = _read_opencode_model()
            if model:
                for s in bpy.data.scenes:
                    s.aimcp_model = model
                    s.aimcp_connection_status = "🟡 Verificando..."
                    threading.Thread(
                        target=_auto_verify_model,
                        args=(model, s.name),
                        daemon=True,
                    ).start()
        return None

def _read_opencode_model():
    import json
    from .operators.model_ops import get_opencode_config_paths
    for p in get_opencode_config_paths():
        if os.path.exists(p):
            try:
                d = json.loads(open(p).read())
                if d.get("model"):
                    return _prefer_flash(d["model"])
            except:
                pass
    from .platform_utils import get_opencode_auth_path
    auth_p = get_opencode_auth_path()
    if auth_p and auth_p.exists():
        try:
            auth = json.loads(auth_p.read_text())
            for prov, entry in auth.items():
                if isinstance(entry, dict) and entry.get("model"):
                    return _prefer_flash(entry["model"])
        except:
            pass
    try:
        from .config_cache import get_last_model
        cached = get_last_model()
        if cached:
            return _prefer_flash(cached)
    except:
        pass
    return ""


def _prefer_flash(model):
    if "deepseek" in model and "pro" in model:
        flash_model = model.replace("-pro", "-flash")
        for s in bpy.data.scenes:
            md = getattr(s, "aimcp_models", None)
            if md and any(m.model_id == flash_model for m in md.items):
                print(f"[blender-mcp] Usando {flash_model} en vez de {model}")
                return flash_model
    return model

def _auto_verify_model(model_id, scene_name):
    """Auto-verify model at startup (thread-safe)."""
    try:
        from .operators.model_ops import (
            _detect_provider, _get_api_key, _PROVIDER_API,
            _queue_status,
        )
        provider = _detect_provider(model_id)
        print(f"[VERIFY] Modelo={model_id}, Provider={provider}")
        key = _get_api_key(provider)
        if not key:
            print(f"[VERIFY] No API key for {provider}")
            _queue_status(scene_name, "🔴 Sin API key para " + provider)
            return
        cfg = _PROVIDER_API.get(provider)
        if not cfg:
            print(f"[VERIFY] No config for {provider}")
            _queue_status(scene_name, "⚠️ Modelo sin verificar")
            return
        import urllib.request
        headers = {"Authorization": f"Bearer {key}", "User-Agent": "blender-mcp/0.8"}
        req = urllib.request.Request(cfg["url"], headers=headers)
        print(f"[VERIFY] Llamando a {cfg['url']}...")
        urllib.request.urlopen(req, timeout=5)
        print(f"[VERIFY] Conectado a {provider}")
        _queue_status(scene_name, "✅ Conectado: " + provider)
    except urllib.error.HTTPError as e:
        print(f"[VERIFY] HTTP Error {e.code}")
        _queue_status(scene_name, f"🔴 Key inválida ({e.code})")
    except urllib.error.URLError:
        print(f"[VERIFY] URL Error - no se pudo contactar servidor")
        _queue_status(scene_name, "🔴 No se pudo contactar servidor")
    except Exception as e:
        print(f"[VERIFY] Error: {traceback.format_exc()}")
        _queue_status(scene_name, f"🔴 Error: {str(e)[:60]}")

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


def unregister():
    try:
        from .operators.embedded import auto_stop
        auto_stop()
    except:
        pass
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
