"""
blender-mcp — Model Selection Operators (cross-platform)
"""
import bpy
import json
import sys
import os
import threading
import traceback
import urllib.request
from pathlib import Path
from bpy.types import Operator
from bpy.props import StringProperty
from .. import _axsock as bsock

from ..platform_utils import get_opencode_auth_path, get_opencode_config_paths

_PROVIDER_API = {
    "deepseek": {"url": "https://api.deepseek.com/v1/models", "auth": True},
    "opencode-go": {"url": "https://opencode.ai/zen/go/v1/models", "auth": True},
    "openrouter": {"url": "https://openrouter.ai/api/v1/models", "auth": False},
    "google": {"url": "https://generativelanguage.googleapis.com/v1beta/models", "auth": True},
    "anthropic": {"url": "https://api.anthropic.com/v1/models", "auth": True},
}

PROVIDER_ORDER = ["google", "anthropic", "deepseek", "opencode-go", "openrouter"]
PROVIDER_LABELS = {
    "google": "Google Gemini", "anthropic": "Anthropic Claude",
    "deepseek": "DeepSeek", "opencode-go": "OpenCode Go", "openrouter": "OpenRouter",
}


def _get_api_key(provider_id):
    auth_path = get_opencode_auth_path()
    if os.path.exists(auth_path):
        try:
            auth = json.loads(open(auth_path).read())
            entry = auth.get(provider_id)
            if isinstance(entry, dict) and entry.get("key"):
                return entry["key"]
        except:
            pass
    env_map = {"deepseek": "DEEPSEEK_API_KEY", "openrouter": "OPENROUTER_API_KEY",
               "google": "GOOGLE_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
    return os.environ.get(env_map.get(provider_id, ""))


class OP_Refresh(Operator):
    bl_idname = "aimcp.refresh"
    bl_label = "Refresh"

    def execute(self, ctx):
        ctx.scene.aimcp_status = "Loading..."
        if ctx.area:
            ctx.area.tag_redraw()

        model = ""
        for p in get_opencode_config_paths():
            if os.path.exists(p):
                try:
                    d = json.loads(open(p).read())
                    if d.get("model"):
                        model = d["model"]
                        break
                except:
                    pass

        auth_path = get_opencode_auth_path()
        providers = []
        if os.path.exists(auth_path):
            try:
                auth = json.loads(open(auth_path).read())
                for prov_id in auth:
                    entry = auth[prov_id]
                    if isinstance(entry, dict) and entry.get("key"):
                        providers.append(prov_id)
            except:
                pass

        def fetch_all():
            all_models = []
            for prov_id in providers:
                cfg = _PROVIDER_API.get(prov_id)
                if not cfg:
                    continue
                try:
                    headers = {"User-Agent": "blender-mcp/0.8", "Accept": "application/json"}
                    if cfg["auth"]:
                        key = _get_api_key(prov_id)
                        if not key:
                            continue
                        headers["Authorization"] = f"Bearer {key}"
                    req = urllib.request.Request(cfg["url"], headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        raw = json.loads(resp.read())
                    raw_list = raw.get("data", raw)
                    if isinstance(raw_list, list):
                        for m in raw_list:
                            mid = m.get("id", "")
                            if not mid:
                                continue
                            all_models.append({
                                "id": mid,
                                "name": m.get("name") or mid.split("/")[-1].replace("-", " ").title(),
                                "provider": prov_id,
                            })
                except:
                    pass

            def update():
                md = ctx.scene.aimcp_models
                md.clear_all()
                if model:
                    ctx.scene.aimcp_model = model
                for m in all_models:
                    md.add(m["id"], m["name"], m["provider"])
                prov_count = len(set(m["provider"] for m in all_models))
                ctx.scene.aimcp_status = f"{len(all_models)} models from {prov_count} providers"
                if ctx.area:
                    ctx.area.tag_redraw()

            bpy.app.timers.register(update, first_interval=0.01)

        threading.Thread(target=fetch_all, daemon=True).start()
        return {'FINISHED'}


def _detect_provider(model_id):
    """Detect provider from model ID string."""
    for pid in PROVIDER_ORDER:
        if model_id.startswith(pid):
            return pid
    for pid in _PROVIDER_API:
        if pid in model_id:
            return pid
    return "opencode-go"


# Thread-safe status queue (main thread picks up results)
_pending_status = []
_pending_lock = threading.Lock()

def _save_selected_model(model_id):
    """Save selected model to config_cache and opencode.json."""
    try:
        from ..config_cache import set_last_model
        set_last_model(model_id)
    except:
        pass
    # Also write to opencode.json if it exists
    try:
        from ..platform_utils import get_opencode_config_paths
        import json
        for p in get_opencode_config_paths():
            if p.exists():
                d = json.loads(p.read_text())
                d["model"] = model_id
                p.write_text(json.dumps(d, indent=2))
                break
    except:
        pass


def _queue_status(scene_name, msg):
    """Thread-safe: queue status update for main thread timer."""
    with _pending_lock:
        _pending_status.append((scene_name, msg))

def _status_ticker():
    """Timer callback: flush pending status updates to scene."""
    try:
        with _pending_lock:
            while _pending_status:
                scene_name, msg = _pending_status.pop(0)
                for s in bpy.data.scenes:
                    if s.name == scene_name:
                        s.aimcp_connection_status = msg
                        s.aimcp_status = msg
                        try:
                            if bpy.context.screen:
                                for area in bpy.context.screen.areas:
                                    area.tag_redraw()
                        except:
                            pass
                        break
    except Exception as e:
        print(f"[blender-mcp] _status_ticker error: {e}")
    return 0.2


class OP_SelectModel(Operator):
    bl_idname = "aimcp.select"
    bl_label = "Select"
    model_id: StringProperty()

    def execute(self, ctx):
        ctx.scene.aimcp_model = self.model_id
        ctx.scene.aimcp_connection_status = "🟡 Verificando..."
        ctx.scene.aimcp_status = "Verificando conexión..."
        if ctx.area:
            ctx.area.tag_redraw()
        # Save selected model to persistent cache + opencode config
        _save_selected_model(self.model_id)
        threading.Thread(target=self._verify, args=(ctx,), daemon=True).start()
        return {'FINISHED'}

    def _verify(self, ctx):
        model_id = self.model_id  # guardar antes del thread (StructRNA se elimina en thread)
        provider = _detect_provider(model_id)
        key = _get_api_key(provider)
        print(f"[VERIFY] Modelo={model_id}, Provider={provider}, Key={'✅' if key else '❌'}")
        if not key:
            _queue_status(ctx.scene.name, "🔴 Sin API key para " + provider)
            return
        cfg = _PROVIDER_API.get(provider)
        if not cfg:
            _queue_status(ctx.scene.name, "⚠️ Modelo sin verificar")
            print(f"[VERIFY] No config for {provider}")
            return
        try:
            headers = {"Authorization": f"Bearer {key}", "User-Agent": "blender-mcp/0.8"}
            req = urllib.request.Request(cfg["url"], headers=headers)
            print(f"[VERIFY] URL={cfg['url']}")
            urllib.request.urlopen(req, timeout=5)
            print(f"[VERIFY] ✅ Conectado a {provider}")
            _queue_status(ctx.scene.name, "✅ Conectado: " + provider)
        except urllib.error.HTTPError as e:
            print(f"[VERIFY] HTTP Error {e.code}")
            _queue_status(ctx.scene.name, f"🔴 Key inválida ({e.code})")
        except urllib.error.URLError:
            print(f"[VERIFY] URL Error - no se pudo contactar")
            _queue_status(ctx.scene.name, "🔴 No se pudo contactar servidor")
        except Exception as e:
            print(f"[VERIFY] Error: {traceback.format_exc()}")
            _queue_status(ctx.scene.name, f"🔴 Error: {str(e)[:60]}")

    def _queue_status(self, ctx, msg):
        """Thread-safe: queue status update for main thread timer."""
        _queue_status(ctx.scene.name, msg)


class OP_ApplyModel(Operator):
    bl_idname = "aimcp.apply_model"
    bl_label = "Apply"
    model_id: StringProperty()

    def execute(self, ctx):
        mid = self.model_id
        ctx.scene.aimcp_model = mid
        ctx.scene.aimcp_status = "Saved"
        config_paths = get_opencode_config_paths()
        for p in config_paths:
            if os.path.exists(p):
                try:
                    d = json.loads(open(p).read())
                    d["model"] = mid
                    open(p, "w").write(json.dumps(d, indent=2) + "\n")
                    ctx.scene.aimcp_status = f"Saved to {os.path.basename(p)}"
                    break
                except:
                    pass
        if ctx.area:
            ctx.area.tag_redraw()
        return {'FINISHED'}


class OP_ClearSearch(Operator):
    bl_idname = "aimcp.clear_search"
    bl_label = "Clear"
    search_prop: StringProperty()

    def execute(self, ctx):
        if self.search_prop and hasattr(ctx.scene, self.search_prop):
            setattr(ctx.scene, self.search_prop, "")
        if ctx.area:
            ctx.area.tag_redraw()
        return {'FINISHED'}


MODEL_OPERATORS = [OP_Refresh, OP_SelectModel, OP_ApplyModel, OP_ClearSearch]


def register_model_operators():
    from bpy.utils import register_class
    for cls in MODEL_OPERATORS:
        try: register_class(cls)
        except: pass


def unregister_model_operators():
    from bpy.utils import unregister_class
    for cls in reversed(MODEL_OPERATORS):
        unregister_class(cls)
