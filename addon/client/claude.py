"""
blender-mcp — Anthropic Claude Provider (embedded)
Uses Anthropic's Messages API with streaming and tool use.
"""
import json
import urllib.request
import logging
from . import MCPClientBase

logger = logging.getLogger("blender-mcp-claude")


class MCPClientClaude(MCPClientBase):
    """Anthropic Claude API provider for embedded mode."""

    provider_id = "anthropic"
    provider_name = "Anthropic Claude"
    default_model = "claude-sonnet-4-20250514"
    api_base = "https://api.anthropic.com/v1"

    def __init__(self, server_url="http://localhost:45677/sse"):
        super().__init__(server_url)

    async def _call_llm(self, model, api_key, messages, stream_callback=None):
        url = f"{self.api_base}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "User-Agent": "blender-mcp-embedded/0.8",
        }

        # Convert OpenAI-style messages to Anthropic format
        system = None
        anthropic_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content_text = msg.get("content", "")
            if role == "system":
                system = content_text
            elif role == "tool":
                tc = msg.get("tool_calls", [{}])[0] if msg.get("tool_calls") else None
                anthropic_messages.append({
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": msg.get("tool_call_id", ""), "content": content_text}],
                })
            elif role == "assistant" and msg.get("tool_calls"):
                content_parts = []
                if content_text:
                    content_parts.append({"type": "text", "text": content_text})
                for tc in msg.get("tool_calls", []):
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except:
                        args = {}
                    content_parts.append({
                        "type": "tool_use",
                        "id": tc.get("id", "call_1"),
                        "name": tc["function"]["name"],
                        "input": args,
                    })
                anthropic_messages.append({"role": "assistant", "content": content_parts})
            else:
                anthropic_messages.append({"role": role, "content": content_text})

        body = {
            "model": model,
            "max_tokens": 4096,
            "messages": anthropic_messages,
            "stream": True,
        }
        if system:
            body["system"] = system

        # Add tools from embedded server
        tools_payload = []
        for t in self._tools:
            tools_payload.append({
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["schema"],
            })
        if tools_payload:
            body["tools"] = tools_payload

        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            resp = urllib.request.urlopen(req, timeout=120)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()[:500]
            return {"error": f"HTTP {e.code}: {error_body}"}
        except Exception as e:
            return {"error": str(e)[:300]}

        full_content = ""
        tool_calls = {}

        for line in resp.read().decode().split("\n"):
            if not line.startswith("data: "):
                continue
            payload = line[6:].strip()
            if payload == "[DONE]":
                break
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                continue

            etype = event.get("type", "")
            if etype == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    text = delta.get("text", "")
                    full_content += text
                    if stream_callback:
                        stream_callback(text)
            elif etype == "content_block_start":
                block = event.get("content_block", {})
                if block.get("type") == "tool_use":
                    idx = event.get("index", 0)
                    tool_calls[idx] = {
                        "id": block.get("id", f"tool_{idx}"),
                        "function": {"name": block.get("name", ""), "arguments": ""},
                    }
            elif etype == "content_block_delta" and event.get("delta", {}).get("type") == "input_json_delta":
                idx = event.get("index", 0)
                if idx in tool_calls:
                    tool_calls[idx]["function"]["arguments"] += event["delta"].get("partial_json", "")

        result = {"content": full_content}
        if tool_calls:
            result["tool_calls"] = [tc for _, tc in sorted(tool_calls.items())]
            # Parse JSON arguments
            for tc in result["tool_calls"]:
                try:
                    tc["function"]["arguments"] = json.loads(tc["function"]["arguments"])
                except:
                    pass

        return result
