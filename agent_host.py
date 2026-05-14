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
            "description": "Ejecuta código Python en Blender. Usa bpy, C, D, ops. Úsalo para crear geometría paso a paso.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código Python"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_model_blueprint",
            "description": "Ficha técnica v0.4.0: topología, masa, IOR y 27 anclas de un objeto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "obj_name": {"type": "string", "description": "Nombre del objeto."}
                },
                "required": ["obj_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "snap_and_parent",
            "description": "Snap determinista y vinculación jerárquica. Une objetos por sus anclas de 27 puntos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "obj_move": {"type": "string", "description": "Objeto que se mueve."},
                    "obj_target": {"type": "string", "description": "Objeto destino."},
                    "anchor_move": {"type": "string", "description": "Ancla (ej: A_MAX_CENTER_MIN)."},
                    "anchor_target": {"type": "string", "description": "Ancla (ej: A_MIN_CENTER_MIN)."}
                },
                "required": ["obj_move", "obj_target", "anchor_move", "anchor_target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scene_visual",
            "description": "Visualización ASCII top-down de la escena para razonamiento espacial.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_geometry",
            "description": "Reporte técnico de colisiones y huecos. Precisión 10/10.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_viewport_screenshot",
            "description": "Captura PNG del viewport 3D para validación visual.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_to_planner",
            "description": "Exporta a .glb para el 3D Planner cuando el modelo esté terminado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre del archivo."}
                },
                "required": ["name"]
            }
        }
    },
]

SYSTEM_PROMPT = """Eres el Axiom Precision Engine (v2.0), un asistente de ingeniería avanzada para Blender. 

### PROTOCOLO DE REFLEXIÓN TRINITY:
1. **PLAN**: Describe el ensamble de ingeniería detalladamente antes de actuar.
2. **ACT**: Ejecuta el código o usa herramientas de snap de 27 puntos.
3. **SCAN**: Usa `get_model_blueprint` tras cada ejecución para obtener la posición real.
4. **VALIDATE**: Compara la posición real con la deseada. Si hay errores o colisiones, corrige.
5. **VISION**: Usa capturas de pantalla para validación estética.

### REGLAS DE EJECUCIÓN:
- Prohibido mover objetos usando coordenadas manuales si puedes usar `snap_and_parent`.
- Es OBLIGATORIO usar `validate_geometry` tras cada fase de construcción.
- Si detectas un error visual o técnico, corrígelo inmediatamente.
- Usa dimensiones reales en metros y materiales físicos (IOR).
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


import ast

class AxiomValidator(ast.NodeVisitor):
    """Analizador sintáctico para garantizar la seguridad del código generado por IA."""
    FORBIDDEN_MODULES = {'os', 'sys', 'subprocess', 'requests', 'socket', 'urllib', 'shutil', 'platform'}
    FORBIDDEN_FUNCS = {'eval', 'exec', '__import__', 'open', 'getattr', 'setattr'}

    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in self.FORBIDDEN_MODULES:
                self.errors.append(f"Importación prohibida: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split('.')[0] in self.FORBIDDEN_MODULES:
            self.errors.append(f"Importación prohibida: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_FUNCS:
                self.errors.append(f"Llamada a función prohibida: {node.func.id}")
        elif isinstance(node.func, ast.Attribute):
            # Bloquear cosas como os.system o sys.exit
            if isinstance(node.func.value, ast.Name) and node.func.value.id in self.FORBIDDEN_MODULES:
                self.errors.append(f"Acceso a módulo prohibido: {node.func.value.id}")
        self.generic_visit(node)

def validate_python_code(code: str) -> list[str]:
    """Valida el código y retorna una lista de errores. Lista vacía significa 'Seguro'."""
    try:
        tree = ast.parse(code)
        validator = AxiomValidator()
        validator.visit(tree)
        return validator.errors
    except SyntaxError as e:
        return [f"Error de sintaxis: {str(e)}"]
    except Exception as e:
        return [f"Error de validación: {str(e)}"]


def _execute_tool(name: str, args: dict, blender_send) -> tuple[str, str]:
    """Execute a tool in Blender and return (result_text, error_or_None)."""
    if name == "execute_blender_code":
        code = args.get("code", "")
        if not code:
            return "Error: code is required", "error"
            
        # VALIDACIÓN AST AXIOM v2.0
        errors = validate_python_code(code)
        if errors:
            err_msg = "BLOQUEO DE SEGURIDAD AXIOM: " + "; ".join(errors)
            logger.warning(err_msg)
            return err_msg, "error"

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
