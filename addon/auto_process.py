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
import logging
from . import blender_socket as bsock

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

            # 1. Try embedded client (Ollama, OpenAI, etc.)
            try:
                from .operators.embedded import _embedded_client
                if _embedded_client is not None:
                    _process_with_client(mid, text)
                    continue
            except:
                pass

            # 2. Try auto-start client if API key available
            if elapsed > 3 and _try_auto_start_client():
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


def _process_with_client(mid, text):
    from .operators.embedded import _embedded_client

    scene = bpy.context.scene
    provider = getattr(scene, "aimcp_provider", "opencode-go")
    model = getattr(scene, "aimcp_model", getattr(_embedded_client, 'default_model', ''))
    api_key = _get_api_key(provider)

    if not api_key:
        _respond(mid, "❌ No hay API key para " + provider)
        _cleanup(mid)
        return

    _respond(mid, "⏳ Pensando...", is_status=True)

    def process():
        try:
            result = _embedded_client.send_message(
                model, api_key, [{"role": "user", "content": text}]
            )
            content = result.get("content", "")
            if content:
                _respond(mid, content)
            elif result.get("error"):
                _respond(mid, "❌ " + result["error"][:100])
            else:
                _respond(mid, "⚠️ El modelo no generó respuesta")
        except Exception as e:
            _respond(mid, f"❌ Error: {str(e)[:80]}")
        _cleanup(mid)

    threading.Thread(target=process, daemon=True).start()


def _try_auto_start_client():
    from .operators.embedded import _embedded_client, _auto_start_client
    if _embedded_client is not None:
        return True
    scene = bpy.context.scene
    provider = getattr(scene, "aimcp_provider", "opencode-go")
    api_key = _get_api_key(provider)
    if api_key:
        _auto_start_client(provider, api_key)
        return _embedded_client is not None
    return False


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
