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
from config import PROVIDER_API_CONFIG, get_api_key

# Provider API base URLs for chat completions
PROVIDER_CHAT_URLS = {
    "opencode-go": "https://opencode.ai/zen/go/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
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
            "name": "get_scene_info",
            "description": "Get current Blender scene information (objects, types, locations).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]

SYSTEM_PROMPT = """You are an AI assistant controlling Blender 3D. The user sends you messages in Spanish or English.
You have the following tools:
- execute_blender_code: Execute Python code in Blender using bpy
- get_scene_info: Get current scene info

When the user asks for a 3D object, respond by calling execute_blender_code with the appropriate bpy code.
Create objects step by step. Use proper dimensions in meters. Always respond in the user's language.
If you don't understand or can't fulfill the request, respond with a helpful message explaining what you can do.
After executing code, always confirm what was created with a brief message."""


def _detect_provider(model_name: str) -> str | None:
    """Detect which provider a model belongs to."""
    if "/" in model_name:
        prefix = model_name.split("/")[0]
        if prefix in PROVIDER_CHAT_URLS:
            return prefix
        # Try openrouter for unknown prefixes
        return "openrouter"
    # Models without prefix are opencode-go
    return "opencode-go"


def _build_request(model: str, message: str, api_key: str, provider: str) -> dict:
    """Build the LLM API request body."""
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        "tools": TOOLS_DEF,
        "tool_choice": "auto",
        "max_tokens": 4096,
        "temperature": 0.7,
    }


def _call_llm(model: str, message: str, provider: str, api_key: str) -> tuple[str, list | None]:
    """Call the LLM API. Returns (response_text, tool_calls_or_None)."""
    url = PROVIDER_CHAT_URLS.get(provider)
    if not url:
        return f"No chat URL for provider: {provider}", None

    body = _build_request(model, message, api_key, provider)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "blender-mcp-agent/0.12",
    }

    try:
        req = urllib.request.Request(url,
            data=json.dumps(body).encode(),
            headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
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

    return f"Unknown tool: {name}", "error"


def process_message(message: str, blender_send) -> str:
    """Process a chat message through the LLM. Returns final response text."""
    # Read config
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
    logger.info(f"Model: {model}, Provider: {provider}")

    # Get API key
    api_key = get_api_key(provider)
    if not api_key and provider == "opencode-go":
        auth_path = Path.home() / ".local/share/opencode/auth.json"
        if auth_path.exists():
            try:
                auth_data = json.loads(auth_path.read_text())
                entry = auth_data.get("opencode-go", {})
                if isinstance(entry, dict):
                    api_key = entry.get("key")
            except: pass

    if not api_key:
        return f"No API key found for provider: {provider}. Use /connect in opencode."

    # Call LLM once. If tool calls returned, execute them and respond.
    text, tool_calls = _call_llm(model, message, provider, api_key)

    if tool_calls:
        results = []
        for tc in tool_calls:
            func_name = tc["function"]["name"]
            try:
                func_args = json.loads(tc["function"]["arguments"])
            except:
                func_args = {}
            result_text, error = _execute_tool(func_name, func_args, blender_send)
            results.append(result_text)
            logger.info(f"Tool {func_name}: {result_text[:100]}")

        # If LLM responded with text and executed tools, combine them
        if text:
            return text + "\n" + "\n".join(results)
        return "\n".join(results) if results else "Done."

    return text or "Done."
