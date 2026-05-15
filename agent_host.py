"""
agent_host.py — Autonomous AI agent for Blender chat.
Reads the configured model, calls the LLM API, executes tools in Blender, responds to chat.
"""
import json, os, sys, time, logging, urllib.request
from pathlib import Path

logger = logging.getLogger("agent-host")

# Usamos imports relativos para evitar Policy Violations
from config import PROVIDER_API_CONFIG, get_api_key
from blender_mcp.platform import get_config_dir

# Provider API base URLs
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
            "name": "get_scene_info",
            "description": "Get information about the current Blender scene (objects, counts, names).",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

SYSTEM_PROMPT = """Eres el Axiom Precision Engine (v2.0), un asistente de ingeniería avanzada para Blender."""

def _detect_provider(model_name: str) -> str | None:
    if "/" in model_name:
        prefix = model_name.split("/")[0]
        if prefix in PROVIDER_CHAT_URLS: return prefix
        if "gemini" in model_name.lower(): return "google"
        return "openrouter"
    if "gemini" in model_name.lower(): return "google"
    return "opencode-go"

def _load_agent_manual():
    path = str(get_config_dir() / "agents.md")
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return f"\n\nMANUAL DE USUARIO:\n{f.read()}"
        except: pass
    return ""

def _build_request(model: str, messages: list, api_key: str, provider: str) -> dict:
    full_prompt = SYSTEM_PROMPT + _load_agent_manual()
    return {
        "model": model,
        "messages": [{"role": "system", "content": full_prompt}, *messages],
        "tools": TOOLS_DEF,
        "tool_choice": "auto",
        "max_tokens": 4096,
        "temperature": 0.4,
    }

def _call_llm(model: str, messages: list, provider: str, api_key: str) -> tuple[str, list | None]:
    url = PROVIDER_CHAT_URLS.get(provider)
    if not url: return f"No chat URL for provider: {provider}", None
    body = _build_request(model, messages, api_key, provider)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
    except Exception as e: return f"API error: {str(e)[:100]}", None
    choice = result.get("choices", [{}])[0]
    msg = choice.get("message", {})
    return msg.get("content", "") or "", msg.get("tool_calls")

def _execute_tool(name: str, args: dict, blender_send) -> tuple[str, str]:
    if name == "execute_blender_code":
        code = args.get("code", "")
        try:
            result = blender_send("execute_code", {"code": code})
            return result.get("output", "") or "Code executed successfully", None
        except Exception as e: return f"Error: {str(e)[:200]}", "error"
    elif name == "get_scene_info":
        try:
            result = blender_send("get_scene_info")
            return json.dumps(result, indent=2), None
        except Exception as e: return f"Error: {str(e)[:200]}", "error"
    return f"Unknown tool: {name}", "error"

def process_message(message: str, blender_send, history=None, status_callback=None, check_stop_callback=None) -> list:
    model = "minimax-m2.7" # Default
    provider = _detect_provider(model)
    api_key = get_api_key(provider)
    if not api_key: return history or []
    
    history.append({"role": "user", "content": message})
    
    for turn in range(5):
        if check_stop_callback and check_stop_callback(): break
        text, tool_calls = _call_llm(model, history, provider, api_key)
        
        history.append({"role": "assistant", "content": text or "...", "tool_calls": tool_calls})
        if not tool_calls: break
            
        for tc in tool_calls:
            func_name = tc["function"]["name"]
            try: func_args = json.loads(tc["function"]["arguments"])
            except: func_args = {}
                
            result_text, error = _execute_tool(func_name, func_args, blender_send)
            history.append({
                "role": "tool", "tool_call_id": tc.get("id"),
                "name": func_name, "content": result_text
            })
    return history
