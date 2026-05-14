"""
blender-mcp — Ollama Provider (local LLM)
Runs fully offline using local models via Ollama API.
"""
import json
import urllib.request
import logging
from . import MCPClientBase

logger = logging.getLogger("blender-mcp-ollama")


class MCPClientOllama(MCPClientBase):
    """Ollama local LLM provider — no internet required."""

    provider_id = "ollama"
    provider_name = "Ollama (Local)"
    default_model = "llama3.2"
    api_base = "http://localhost:11434"

    def __init__(self, server_url="http://localhost:45677/sse"):
        super().__init__(server_url)

    async def _call_llm(self, model, api_key, messages, stream_callback=None):
        url = f"{self.api_base}/api/chat"
        headers = {"Content-Type": "application/json", "User-Agent": "blender-mcp-embedded/0.8"}

        # Convert to Ollama format
        ollama_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls")
            if role == "tool":
                role = "tool"
            ollama_messages.append({"role": role, "content": content})

        body = {
            "model": model,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": 0.4,
                "num_predict": 4096,
            },
        }

        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            resp = urllib.request.urlopen(req, timeout=180)
        except urllib.error.HTTPError as e:
            return {"error": f"Ollama HTTP {e.code}: {e.read().decode()[:200]}"}
        except Exception as e:
            return {"error": f"Ollama error: {str(e)[:200]}"}

        full_content = ""
        for line in resp.read().decode().split("\n"):
            if not line.strip():
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            if chunk.get("done"):
                break
            if chunk.get("message", {}).get("content"):
                text = chunk["message"]["content"]
                full_content += text
                if stream_callback:
                    stream_callback(text)

        return {"content": full_content}
