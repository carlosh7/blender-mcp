"""
agent_host.py — Autonomous AI agent for Blender chat.
Reads the configured model, calls the LLM API, executes tools in Blender, responds to chat.
No waiting for external AI - processes messages immediately using configured provider.
"""
import json, os, sys, time, logging, urllib.request
from pathlib import Path

logger = logging.getLogger("agent-host")

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from config import PROVIDER_API_CONFIG, get_api_key
from blender_mcp.platform import get_config_dir

# Provider API base URLs for chat completions
PROVIDER_CHAT_URLS = {
    "opencode-go": "https://opencode.ai/zen/go/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
}

# Tools available to the LLM
TOOLS_DEF = [
    {
        "type": "function",
        "function": {
            "name": "execute_blender_code",
            "description": "Execute Python code in Blender. Uses bpy, C (bpy.context), D (bpy.data), ops (bpy.ops). Create objects step by step.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute in Blender"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scene_visual",
            "description": "Get a top-down ASCII visualization of the scene to understand where objects are and avoid collisions.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_to_planner",
            "description": "Export the created model to the 3D Planner. Use this when the model is finished.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Filename for the model (e.g. 'office_chair')"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_object_anchors",
            "description": "Get extreme vertices (anchors) of an object in world space (e.g., corners of a bounding box) to align with other parts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "obj_name": {"type": "string", "description": "Name of the object to inspect."}
                },
                "required": ["obj_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_geometry",
            "description": "Ejecuta un reporte técnico de ingeniería para detectar colisiones y huecos entre objetos. Úsalo para asegurar precisión 10/10.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_viewport_screenshot",
            "description": "Captura una imagen del viewport 3D de Blender. Úsala para VALIDAR visualmente tu trabajo después de ensamblar piezas.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]

SYSTEM_PROMPT = """Eres el Axiom Precision Engine, un asistente de ingeniería avanzada para Blender. 

### PROTOCOLO DE CONTROL AXIOM:
1. **SOPORTE INTELECTUAL**: Sé proactivo, ofrece planes detallados y sugiere mejoras técnicas.
2. **BLOQUEO DE EJECUCIÓN**: Nunca ejecutes una herramienta (`tool_call`) sin haber presentado el plan y recibido un "adelante", "ejecuta" o similar.
3. **PRIORIDAD 'agents.md'**: Sigue siempre el manual de usuario.

### REGLAS DE EJECUCIÓN:
- Está PROHIBIDO mover objetos usando coordenadas manuales si puedes usar un ancla.
- Tras cada fase de construcción, autoevalúate usando una captura de pantalla.
- Si detectas un error visual o técnico, corrígelo inmediatamente antes de seguir con el siguiente paso.

### MATERIALES Y ASSETS:
- Usa dimensiones reales en metros (ej: mesa de 1.5m).
- Los objetos deben estar físicamente conectados, sin huecos (salvo que el diseño lo requiera).
- Siempre confirma lo creado con un mensaje breve en español."""


def _detect_provider(model_name: str) -> str | None:
    """Detect which provider a model belongs to."""
    if "/" in model_name:
        prefix = model_name.split("/")[0]
        if prefix in PROVIDER_CHAT_URLS:
            return prefix
        if "gemini" in model_name.lower():
            return "google"
        return "openrouter"
    if "gemini" in model_name.lower():
        return "google"
    return "opencode-go"

def _load_agent_manual():
    """Load user-defined rules from agents.md."""
    path = str(get_config_dir() / "agents.md")
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return f"\n\nMANUAL DE USUARIO:\n{f.read()}"
        except: pass
    return ""

def _build_request(model: str, messages: list, api_key: str, provider: str) -> dict:
    """Build the LLM API request body."""
    full_prompt = SYSTEM_PROMPT + _load_agent_manual()
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": full_prompt},
            *messages
        ],
        "tools": TOOLS_DEF,
        "tool_choice": "auto",
        "max_tokens": 4096,
        "temperature": 0.4,
    }


def _call_llm(model: str, messages: list, provider: str, api_key: str) -> tuple[str, list | None]:
    """Call the LLM API. Returns (response_text, tool_calls_or_None)."""
    url = PROVIDER_CHAT_URLS.get(provider)
    if not url:
        return f"No chat URL for provider: {provider}", None

    body = _build_request(model, messages, api_key, provider)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "blender-mcp-agent/0.12",
    }

    try:
        req = urllib.request.Request(url,
            data=json.dumps(body).encode(),
            headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        return f"API error: {str(e)[:100]}", None

    choice = result.get("choices", [{}])[0]
    msg = choice.get("message", {})
    content = msg.get("content", "")
    tool_calls = msg.get("tool_calls")

    return content or "", tool_calls


def _execute_tool(name: str, args: dict, blender_send) -> tuple[str, str]:
    """Execute a tool in Blender and return (result_text, error_or_None)."""
    if name == "execute_blender_code":
        code = args.get("code", "")
        if not code:
            return "Error: code is required", "error"
        try:
            result = blender_send("execute_code", {"code": code})
            output = result.get("output", "")
            return output or "Code executed successfully", None
        except Exception as e:
            return f"Error: {str(e)[:200]}", "error"

    elif name == "get_scene_info":
        try:
            result = blender_send("get_scene_info")
            return json.dumps(result, indent=2), None
        except Exception as e:
            return f"Error: {str(e)[:200]}", "error"

    elif name == "get_scene_visual":
        try:
            result = blender_send("get_spatial_visual")
            return result.get("summary", "No se pudo obtener el resumen espacial."), None
        except Exception as e:
            return f"Error: {str(e)[:200]}", "error"

    elif name == "get_object_anchors":
        obj_name = args.get("obj_name", "")
        try:
            result = blender_send("get_object_anchors", {"obj_name": obj_name})
            return json.dumps(result.get("anchors", {}), indent=2), None
        except Exception as e:
            return f"Error: {str(e)[:200]}", "error"

    elif name == "validate_geometry":
        try:
            result = blender_send("validate_geometry")
            return result.get("report", "No se pudo obtener el reporte."), None
        except Exception as e:
            return f"Error: {str(e)[:200]}", "error"

    elif name == "get_viewport_screenshot":
        try:
            result = blender_send("get_viewport_screenshot")
            return f"Imagen capturada en: {result.get('filepath')}. Analiza esta ruta si tienes capacidad de visión.", None
        except Exception as e:
            return f"Error: {str(e)[:200]}", "error"

    return f"Unknown tool: {name}", "error"


def process_message(message: str, blender_send, history=None, status_callback=None, check_stop_callback=None) -> list:
    """
    Process a chat message with an autonomous loop and memory.
    Returns the updated history list.
    """
    # Read config to find model
    config_paths = [
        Path.home() / ".config" / "opencode" / "opencode.json",
        Path.home() / "Check" / "opencode.json",
        Path.cwd() / "opencode.json",
    ]
    model = "minimax-m2.7"
    for p in config_paths:
        if p.exists():
            try:
                data = json.loads(p.read_text())
                if data.get("model"):
                    model = data["model"]
                    break
            except: pass

    provider = _detect_provider(model)
    api_key = get_api_key(provider)
    if not api_key:
        err = f"Error: No API key for {provider}."
        if status_callback: status_callback(err)
        return history or []

    # Información de objetos para el prompt (con cache)
    objs_info = ""
    try:
        from blender_mcp.tool_cache import get as cache_get, set as cache_set
        scene_info = cache_get("get_scene_info")
        if scene_info is None:
            scene_info = blender_send("get_scene_info")
            cache_set("get_scene_info", scene_info)
        objs = scene_info.get("objects", [])
        if objs:
            if len(objs) == 1 and objs[0] == "Cube":
                objs_info = "\n\n[CONTEXTO: La escena solo tiene el cubo inicial. TIENES PERMISO PARA BORRARLO y empezar de cero.]"
            else:
                objs_info = f"\n\n[CONTEXTO: La escena YA TIENE estos objetos: {', '.join(objs)}. NO LOS BORRES. Trabaja alrededor de ellos.]"
    except: pass

    # Añadimos el mensaje del usuario (asegurando que no sea vacío)
    content = (message or "Continuar") + objs_info
    history.append({"role": "user", "content": content})
    
    # --- START AGENTIC LOOP ---
    MAX_TURNS = 5  # Reduced from 10 for speed (Fase 4)
    for turn in range(MAX_TURNS):
        # COMPROBACIÓN DE PARADA
        if check_stop_callback and check_stop_callback():
            logger.info("Agent execution STOPPED by user.")
            if status_callback: status_callback("🛑 Tarea cancelada por el usuario.")
            break

        if status_callback: 
            status_callback(f"IA Pensando (Turno {turn+1})...")
        
        text, tool_calls = _call_llm(model, history, provider, api_key)
        
        # Aseguramos que el contenido del asistente nunca sea vacío para evitar Error 400
        assistant_content = text or "..."
        assistant_msg = {"role": "assistant", "content": assistant_content}
        if tool_calls:
            assistant_msg["tool_calls"] = tool_calls
        history.append(assistant_msg)
        
        if text:
            logger.info(f"AI: {text[:100]}...")
            if status_callback: status_callback(text)

        if not tool_calls:
            break
            
        # Execute tools
        for tc in tool_calls:
            # OTRA COMPROBACIÓN DE PARADA ANTES DE CADA HERRAMIENTA
            if check_stop_callback and check_stop_callback():
                logger.info("Agent tool execution STOPPED by user.")
                if status_callback: status_callback("🛑 Tarea cancelada por el usuario.")
                return history

            func_name = tc["function"]["name"]
            tc_id = tc.get("id", "call_" + str(time.time()))
            try:
                func_args = json.loads(tc["function"]["arguments"])
            except:
                func_args = {}
                
            if status_callback: 
                status_callback(f"Ejecutando: {func_name}...")
                
            result_text, error = _execute_tool(func_name, func_args, blender_send)
            
            history.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "name": func_name,
                "content": result_text
            })
            
            if error and status_callback:
                status_callback(f"❌ Error en {func_name}: {result_text[:50]}...")

    return history
