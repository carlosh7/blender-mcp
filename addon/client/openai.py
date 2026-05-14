"""
blender-mcp — OpenAI-compatible Provider (DeepSeek, OpenRouter, etc.)
Full implementation with streaming, tool calls, multi-turn conversation.
"""
import json
import urllib.request
import logging
from . import MCPClientBase

logger = logging.getLogger("blender-mcp-openai")


class MCPClientOpenAI(MCPClientBase):
    """OpenAI-compatible chat completions provider."""

    provider_id = "opencode-go"
    provider_name = "OpenAI Compatible"
    default_model = "gpt-4o-mini"
    api_base = ""

    def __init__(self, api_base="", default_model="", server_url="http://localhost:45677/sse"):
        super().__init__(server_url)
        if api_base:
            self.api_base = api_base
        if default_model:
            self.default_model = default_model

    def get_chat_url(self):
        base = self.api_base.rstrip("/")
        if "/chat/completions" not in base:
            return f"{base}/chat/completions"
        return base

    async def _call_llm(self, model, api_key, messages, stream_callback=None):
        url = self.get_chat_url()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "blender-mcp-embedded/0.8",
        }

        # Build tool descriptions from the embedded MCP server tools
        tools_payload = []
        from mcp.server.fastmcp import FastMCP as _unused
        for t in self._tools:
            tools_payload.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["schema"],
                },
            })

        body = {
            "model": model,
            "messages": messages,
            "tools": tools_payload if tools_payload else None,
            "tool_choice": "auto" if tools_payload else None,
            "stream": True,
            "max_tokens": 4096,
            "temperature": 0.4,
        }

        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        full_content = ""
        tool_calls = {}
        current_tool = None

        try:
            resp = urllib.request.urlopen(req, timeout=120)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()[:500]
            return {"error": f"HTTP {e.code}: {error_body}"}
        except Exception as e:
            return {"error": str(e)[:300]}

        try:
            for line in resp.read().decode().split("\n"):
                if not line.startswith("data: "):
                    continue
                payload = line[6:].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                except json.JSONDecodeError:
                    continue

                delta = chunk.get("choices", [{}])[0].get("delta", {})

                if delta.get("content"):
                    full_content += delta["content"]
                    if stream_callback:
                        stream_callback(delta["content"])

                if delta.get("tool_calls"):
                    for tc in delta["tool_calls"]:
                        idx = tc.get("index", 0)
                        if idx not in tool_calls:
                            tool_calls[idx] = {
                                "id": tc.get("id", f"call_{idx}"),
                                "function": {"name": "", "arguments": ""},
                            }
                        tc_data = tool_calls[idx]
                        if tc.get("id"):
                            tc_data["id"] = tc["id"]
                        if tc.get("function", {}).get("name"):
                            tc_data["function"]["name"] += tc["function"]["name"]
                        if tc.get("function", {}).get("arguments"):
                            tc_data["function"]["arguments"] += tc["function"]["arguments"]

        except Exception as e:
            logger.error(f"Stream parse error: {e}")

        result = {"content": full_content}
        if tool_calls:
            result["tool_calls"] = [tc for _, tc in sorted(tool_calls.items())]

        return result


class MCPClientDeepSeek(MCPClientOpenAI):
    provider_id = "deepseek"
    provider_name = "DeepSeek"
    default_model = "deepseek-chat"
    api_base = "https://api.deepseek.com/v1"


class MCPClientOpenRouter(MCPClientOpenAI):
    provider_id = "openrouter"
    provider_name = "OpenRouter"
    default_model = "anthropic/claude-3.5-sonnet"
    api_base = "https://openrouter.ai/api/v1"


class MCPClientGoogle(MCPClientOpenAI):
    provider_id = "google"
    provider_name = "Google Gemini"
    default_model = "gemini-2.0-flash"
    api_base = "https://generativelanguage.googleapis.com/v1beta/openai"
