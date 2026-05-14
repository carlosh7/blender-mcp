"""
auto_process.py — Procesa la cola de chat dentro de Blender.
Timer que cada 0.5s revisa mensajes y los envía al LLM configurado.
Sin procesos externos. Sin mcp_server.py. Sin agent_host.py.
"""
import bpy
import json
import os
import time
import threading
import traceback
import urllib.request
import logging
from . import _axsock as bsock

logger = logging.getLogger("blender-mcp-auto")

_processed_ids = set()
_message_start = {}
_timer_registered = False


def start():
    global _timer_registered
    if _timer_registered:
        return
    bpy.app.timers.register(_tick, first_interval=0.5)
    _timer_registered = True


def _tick():
    try:
        with bsock._chat_lock:
            if not bsock._chat_queue:
                return 0.5
            messages = list(bsock._chat_queue)

        for msg in messages:
            mid = msg["id"]
            if mid in _processed_ids:
                continue
            _processed_ids.add(mid)

            if mid not in _message_start:
                _message_start[mid] = time.time()

            elapsed = time.time() - _message_start[mid]
            text = msg["message"]
            print(f"[AUTO] mid={mid[:8]} text={text[:40]} elapsed={elapsed:.1f}s")

            if _try_auto_start_client():
                _process_with_client(mid, text)
                continue

            # 3. After 30s, show specific diagnostic
            if elapsed > 30:
                msg = _diagnose()
                _respond(mid, msg)
                _cleanup(mid)

        return 0.5

    except Exception as e:
        logger.error(f"auto_process error: {e}")
        return 0.5


def _detect_provider(model_id):
    """Detect provider from model ID string."""
    PROVIDER_ORDER = ["google", "anthropic", "deepseek", "opencode-go", "openrouter"]
    _PROVIDER_API = {
        "deepseek": {"url": "https://api.deepseek.com/v1/models", "auth": True},
        "opencode-go": {"url": "https://opencode.ai/zen/go/v1/models", "auth": True},
        "openrouter": {"url": "https://openrouter.ai/api/v1/models", "auth": False},
        "google": {"url": "https://generativelanguage.googleapis.com/v1beta/models", "auth": True},
        "anthropic": {"url": "https://api.anthropic.com/v1/models", "auth": True},
    }
    for pid in PROVIDER_ORDER:
        if model_id.startswith(pid):
            return pid
    for pid in _PROVIDER_API:
        if pid in model_id:
            return pid
    return "opencode-go"


def _get_api_key(provider):
    """Busca API key en: env vars → opencode auth.json → config cache."""
    env_map = {"opencode-go": "OPENAI_API_KEY", "deepseek": "DEEPSEEK_API_KEY",
               "openrouter": "OPENROUTER_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
               "google": "GOOGLE_API_KEY"}
    key = os.environ.get(env_map.get(provider, ""), "")
    if key:
        return key
    # opencode auth.json
    try:
        from .platform_utils import get_opencode_auth_path
        p = get_opencode_auth_path()
        if p.exists():
            auth = json.loads(p.read_text())
            entry = auth.get(provider, {})
            if isinstance(entry, dict) and entry.get("key"):
                return entry["key"]
    except:
        pass
    # config cache
    try:
        from .config_cache import get_provider_config
        return get_provider_config(provider).get("api_key", "")
    except:
        pass
    return ""


_CHAT_URLS = {
    "opencode-go": "https://opencode.ai/zen/go/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
}


def _process_with_client(mid, text):
    scene = bpy.context.scene
    model = getattr(scene, "aimcp_model", "")
    provider = _detect_provider(model) if model else "opencode-go"
    print(f"[AUTO] provider={provider} model={model}")
    api_key = _get_api_key(provider)
    print(f"[AUTO] api_key={'✅' if api_key else '❌'}")

    if not api_key:
        _respond(mid, "❌ No hay API key para " + provider)
        _cleanup(mid)
        return

    _respond(mid, "⏳ Pensando...", is_status=True)

    def process():
        print(f"[AUTO] Llamando a {provider} con modelo {model}")
        try:
            # Intentar con embedded client si está disponible
            from .operators.embedded import _embedded_client
            if _embedded_client is not None:
                result = _embedded_client.send_message(
                    model, api_key, [{"role": "user", "content": text}]
                )
                content = result.get("content", "")
                print(f"[AUTO] embedded response: {'✅' if content else '❌'}")
                if content:
                    _respond(mid, content)
                elif result.get("error"):
                    _respond(mid, "❌ " + result["error"][:100])
                else:
                    _respond(mid, "⚠️ Sin respuesta")
                _cleanup(mid)
                return
        except:
            pass

        # Fallback: llamada REST directa (OpenAI-compatible)
        url = _CHAT_URLS.get(provider)
        if not url:
            _respond(mid, f"❌ Provider {provider} no soportado")
            _cleanup(mid)
            return

        try:
            body = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": text}],
                "max_tokens": 4096,
                "temperature": 0.4,
            }).encode()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "blender-mcp/0.8",
            }
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            print(f"[AUTO] REST call to {url}")
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"[AUTO] REST response: {'✅' if content else '❌'}")
            if content:
                _respond(mid, content)
            else:
                _respond(mid, "⚠️ El modelo no generó respuesta")
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:200]
            print(f"[AUTO] HTTP Error {e.code}: {err}")
            _respond(mid, f"❌ HTTP {e.code}")
        except Exception as e:
            print(f"[AUTO] Error: {traceback.format_exc()}")
            _respond(mid, f"❌ Error: {str(e)[:60]}")
        _cleanup(mid)
        _cleanup(mid)

    threading.Thread(target=process, daemon=True).start()


def _try_auto_start_client():
    """Check if API key is available (no need for embedded client, REST fallback works)."""
    scene = bpy.context.scene
    provider = getattr(scene, "aimcp_provider", "opencode-go")
    api_key = _get_api_key(provider)
    has_key = bool(api_key)
    print(f"[AUTO] _try_auto_start: provider={provider} key={'✅' if has_key else '❌'}")
    return has_key


def _respond(mid, text, is_status=False):
    def update():
        for s in bpy.data.scenes:
            for i, m in enumerate(s.aimcp_chat.msgs):
                if m.role == "status" and m.text.endswith("..."):
                    s.aimcp_chat.msgs.remove(i)
                    break
            if is_status:
                s.aimcp_chat.add("status", text, scene=s)
            else:
                with bsock._chat_lock:
                    bsock._chat_responses[mid] = text
                    bsock._chat_queue[:] = [m for m in bsock._chat_queue if m["id"] != mid]
            s.aimcp_waiting = False
        return None
    bpy.app.timers.register(update, first_interval=0.0)


def _diagnose():
    """Diagnóstico: por qué no hay respuesta del LLM."""
    lines = ["❌ No hay respuesta del agente. Diagnóstico:"]
    scene = bpy.context.scene

    # 1. Check API key
    provider = getattr(scene, "aimcp_provider", "?")
    model = getattr(scene, "aimcp_model", "?")
    api_key = _get_api_key(provider)

    if model and model != "?":
        lines.append(f"📌 Modelo: {model}")
    else:
        lines.append("📌 Ningún modelo seleccionado → Config → Refresh → selecciona uno")

    if api_key:
        lines.append(f"✅ API key presente para {provider}")
    else:
        lines.append(f"🔴 Falta API key para {provider}")
        lines.append("   • Ponla en variables de entorno")
        lines.append("   • O usa Local AI en Integrations (Ollama)")
        lines.append("   • O conecta Claude Desktop/Cursor como proxy")

    # 2. Check embedded client
    try:
        from .operators.embedded import _embedded_client
        if _embedded_client:
            lines.append("✅ Local AI activo")
        else:
            lines.append("ℹ️  Local AI no iniciado → click botón SYSTEM en el panel")
    except:
        pass

    # 3. Check Ollama
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/version")
        with urllib.request.urlopen(req, timeout=2):
            lines.append("✅ Ollama detectado (pero no activo) → Integrations → Local AI")
    except:
        pass

    return "\n".join(lines)


def _cleanup(mid):
    _processed_ids.discard(mid)
    _message_start.pop(mid, None)
