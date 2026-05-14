"""
auto_process.py — Procesa la cola de chat dentro de Blender.
Timer que cada 0.5s revisa mensajes y los envía al LLM configurado.
Sin procesos externos. Sin mcp_server.py. Sin agent_host.py.
"""
import bpy
import json
import os
import re
import time
import threading
import traceback
import urllib.request
import logging
from datetime import datetime
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

SYSTEM_PROMPT = """Eres un asistente integrado en Blender 3D.
Tienes herramientas para crear, modificar y eliminar objetos 3D en tiempo real.

REGLAS:
- USA LAS HERRAMIENTAS. No digas "puedo hacerlo", hazlo directamente.
- Cuando te pidan crear algo: usa create_object para la forma base, create_material para colores, assign_material para aplicarlos.
- Para iluminación: usa create_light o setup_three_point_lighting.
- Para cámara: usa create_camera + set_camera_target.
- Siempre verifica la escena con get_scene_info antes de empezar.
- Si algo sale mal, intenta execute_blender_code como fallback.
- No inventes nombres de herramientas que no están en la lista."""


def _exec_code(code):
    """Ejecuta código Python en Blender desde el hilo principal."""
    try:
        ns = {"bpy": bpy, "C": bpy.context, "D": bpy.data, "ops": bpy.ops}
        exec(code, ns)
    except Exception as e:
        print(f"[AUTO] exec error: {e}")


def _append_to_log(text, tag="AI"):
    """Guarda mensaje en el chat log automático."""
    try:
        log_path = os.path.expanduser("~/.config/blender-mcp/chat_log.txt")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now().strftime('%H:%M')}] {tag}: {text}\n\n")
    except:
        pass


TOOLS_DEF = [{"type": "function", "function": {"name": "execute_blender_code", "description": "Execute ANY Python code in Blender. Use for complex operations.", "parameters": {"type": "object", "properties": {"code": {"type": "string", "description": "Python code"}}, "required": ["code"]}}}, {"type": "function", "function": {"name": "get_scene_info", "description": "Get list of all objects in the scene.", "parameters": {"type": "object", "properties": {}}}}, {"type": "function", "function": {"name": "create_object", "description": "Create mesh: CUBE, SPHERE, CYLINDER, CONE, TORUS, PLANE, MONKEY.", "parameters": {"type": "object", "properties": {"type": {"type": "string", "enum": ["CUBE", "SPHERE", "CYLINDER", "CONE", "TORUS", "PLANE", "MONKEY"]}, "name": {"type": "string"}, "location": {"type": "array", "items": {"type": "number"}}}, "required": ["type"]}}}, {"type": "function", "function": {"name": "delete_object", "description": "Delete an object by name.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}}, {"type": "function", "function": {"name": "transform_object", "description": "Move/rotate/scale an object.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "location": {"type": "array", "items": {"type": "number"}}, "rotation": {"type": "array", "items": {"type": "number"}}, "scale": {"type": "array", "items": {"type": "number"}}}, "required": ["name"]}}}, {"type": "function", "function": {"name": "duplicate_object", "description": "Duplicate an object.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "new_name": {"type": "string"}}, "required": ["name"]}}}, {"type": "function", "function": {"name": "create_material", "description": "Create PBR material with color, roughness, metallic.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "color": {"type": "array", "items": {"type": "number"}}, "roughness": {"type": "number"}, "metallic": {"type": "number"}}, "required": ["name"]}}}, {"type": "function", "function": {"name": "assign_material", "description": "Assign material to object.", "parameters": {"type": "object", "properties": {"object_name": {"type": "string"}, "material_name": {"type": "string"}}, "required": ["object_name", "material_name"]}}}, {"type": "function", "function": {"name": "add_modifier", "description": "Add modifier: subsurf, bevel, boolean, array, mirror, solidify, screw, decimate.", "parameters": {"type": "object", "properties": {"object_name": {"type": "string"}, "modifier_type": {"type": "string", "enum": ["subsurf", "bevel", "boolean", "array", "mirror", "solidify", "screw", "decimate"]}}, "required": ["object_name", "modifier_type"]}}}, {"type": "function", "function": {"name": "create_light", "description": "Create light: point, sun, spot, area.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "light_type": {"type": "string", "enum": ["point", "sun", "spot", "area"]}, "energy": {"type": "number"}, "location": {"type": "array", "items": {"type": "number"}}}}}}, {"type": "function", "function": {"name": "setup_three_point_lighting", "description": "Auto 3-point lighting for target.", "parameters": {"type": "object", "properties": {"target_name": {"type": "string"}}}}}, {"type": "function", "function": {"name": "create_camera", "description": "Create and set active camera.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "location": {"type": "array", "items": {"type": "number"}}, "lens": {"type": "number", "description": "Focal length mm"}}}}}, {"type": "function", "function": {"name": "set_camera_target", "description": "Point camera at target.", "parameters": {"type": "object", "properties": {"camera_name": {"type": "string"}, "target_name": {"type": "string"}}, "required": ["camera_name", "target_name"]}}}, {"type": "function", "function": {"name": "insert_keyframe", "description": "Insert animation keyframe.", "parameters": {"type": "object", "properties": {"object_name": {"type": "string"}, "frame": {"type": "number"}, "property": {"type": "string", "enum": ["location", "rotation_euler", "scale"]}}, "required": ["object_name", "frame"]}}}, {"type": "function", "function": {"name": "set_render_engine", "description": "Set render engine: CYCLES, EEVEE, WORKBENCH.", "parameters": {"type": "object", "properties": {"engine": {"type": "string", "enum": ["CYCLES", "EEVEE", "WORKBENCH"]}}, "required": ["engine"]}}}, {"type": "function", "function": {"name": "render_frame", "description": "Render current frame to image.", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}}}}, {"type": "function", "function": {"name": "export_scene", "description": "Export scene: glb, gltf, fbx, obj, stl, ply, usd, dae.", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}, "format": {"type": "string", "enum": ["glb", "gltf", "fbx", "obj", "stl", "ply", "usd", "dae"]}}, "required": ["filepath", "format"]}}}, {"type": "function", "function": {"name": "get_viewport_screenshot", "description": "Capture 3D viewport.", "parameters": {"type": "object", "properties": {}}}}, {"type": "function", "function": {"name": "unwrap_object", "description": "UV unwrap mesh: smart, unwrap, cube, cylinder, sphere.", "parameters": {"type": "object", "properties": {"object_name": {"type": "string"}, "method": {"type": "string", "enum": ["smart", "unwrap", "cube", "cylinder", "sphere"]}}}}}, {"type": "function", "function": {"name": "join_objects", "description": "Join multiple objects into one mesh.", "parameters": {"type": "object", "properties": {"target_name": {"type": "string"}, "source_names": {"type": "array", "items": {"type": "string"}}}, "required": ["target_name"]}}}, {"type": "function", "function": {"name": "purge_orphans", "description": "Remove unused data blocks.", "parameters": {"type": "object", "properties": {}}}}, {"type": "function", "function": {"name": "scene_summary", "description": "Full scene summary.", "parameters": {"type": "object", "properties": {}}}}, {"type": "function", "function": {"name": "mesh_analysis", "description": "Analyze mesh topology.", "parameters": {"type": "object", "properties": {"object_name": {"type": "string"}}}}}, {"type": "function", "function": {"name": "search_polyhaven", "description": "Search Poly Haven for free HDRI/textures.", "parameters": {"type": "object", "properties": {"asset_type": {"type": "string", "enum": ["hdris", "textures", "models", "all"]}, "query": {"type": "string"}}}}}, {"type": "function", "function": {"name": "download_polyhaven_hdri", "description": "Download free HDRI for lighting.", "parameters": {"type": "object", "properties": {"asset_id": {"type": "string"}}, "required": ["asset_id"]}}}, {"type": "function", "function": {"name": "download_polyhaven_texture", "description": "Download free PBR texture and create material.", "parameters": {"type": "object", "properties": {"asset_id": {"type": "string"}}, "required": ["asset_id"]}}}]


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

    url = _CHAT_URLS.get(provider)
    if not url:
        _respond(mid, f"❌ Provider {provider} no soportado")
        _cleanup(mid)
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "blender-mcp/0.8",
    }

    _respond(mid, "⏳ Pensando...", is_status=True)

    def process():
        print(f"[AUTO] Llamando a {provider} con modelo {model}")
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        objs = [o.name for o in bpy.data.objects if hasattr(o, 'name')]
        if objs:
            messages.append({"role": "system", "content": f"Escena actual: {', '.join(objs[:10])}"})
        messages.append({"role": "user", "content": text})

        for turn in range(6):
            print(f"[AUTO] Turno {turn+1}/6")
            try:
                response = _call_llm_with_tools(url, headers, model, messages)
            except urllib.error.HTTPError as e:
                err = e.read().decode()[:200]
                print(f"[AUTO] HTTP Error {e.code}: {err}")
                _respond(mid, f"❌ HTTP {e.code}")
                break
            except Exception as e:
                print(f"[AUTO] Error: {traceback.format_exc()}")
                _respond(mid, f"❌ Error: {str(e)[:60]}")
                break

            content = response.get("content", "")
            tool_calls = response.get("tool_calls")

            if content:
                print(f"[AUTO] Respuesta: {content[:80]}...")
                if turn == 0:
                    _respond(mid, content)
                else:
                    _respond(mid, content)

            if not tool_calls:
                print(f"[AUTO] Sin tool_calls, fin del loop")
                break

            for tc in tool_calls:
                func_name = tc["function"]["name"]
                try:
                    func_args = json.loads(tc["function"]["arguments"])
                except:
                    func_args = {}
                print(f"[AUTO] Ejecutando tool: {func_name}")
                result = _execute_tool(func_name, func_args)
                print(f"[AUTO] Resultado: {result[:100]}...")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", f"call_{turn}"),
                    "name": func_name,
                    "content": result,
                })

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
            # Remove old status
            for i, m in enumerate(s.aimcp_chat.msgs):
                if m.role == "status" and m.text.endswith("..."):
                    s.aimcp_chat.msgs.remove(i)
                    break
            if is_status:
                s.aimcp_chat.add("status", text, scene=s)
            else:
                # Add response directly to chat (no polling needed)
                s.aimcp_chat.add("assistant", text, scene=s)
                with bsock._chat_lock:
                    bsock._chat_queue[:] = [m for m in bsock._chat_queue if m["id"] != mid]
            s.aimcp_waiting = False
            s.aimcp_pending_msg_id = ""
            # Force redraw ALL areas (not just active one)
            for screen in bpy.data.screens:
                for area in screen.areas:
                    area.tag_redraw()
            # Auto-save to log
            if not is_status:
                _append_to_log(text)
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
