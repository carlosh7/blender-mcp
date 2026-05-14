"""
blender-mcp — Embedded MCP Client Base
Manages async event loop, SSE connection to embedded MCP server,
and tool call dispatch via Blender timers.
"""
import json
import queue
import threading
import asyncio
import logging
import time
from contextlib import suppress

logger = logging.getLogger("blender-mcp-client")


class MCPClientBase:
    """Base class for embedded LLM providers inside Blender."""

    provider_id = "base"
    provider_name = "Base"
    default_model = ""
    api_base = ""

    def __init__(self, server_url="http://localhost:45677/sse"):
        self.server_url = server_url
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.running = False
        self.thread = None
        self._session = None
        self._tools = []

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()
        logger.info(f"{self.provider_name} client started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _run_async_loop(self):
        asyncio.run(self._main())

    async def _main(self):
        try:
            from mcp import ClientSession
            from mcp.client.sse import sse_client
        except ImportError:
            logger.error("MCP SDK not available for embedded client")
            return

        async with sse_client(self.server_url) as streams:
            async with ClientSession(*streams) as session:
                self._session = session
                result = await session.initialize()
                tools_result = await session.list_tools()
                self._tools = [{"name": t.name, "description": t.description, "schema": t.inputSchema} for t in tools_result.tools]
                logger.info(f"Connected to embedded MCP, {len(self._tools)} tools available")

                while self.running:
                    try:
                        command = self.command_queue.get(timeout=0.5)
                        response = await self._process_command(session, command)
                        self.response_queue.put(response)
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Client loop error: {e}")
                        self.response_queue.put({"error": str(e)})

    async def _process_command(self, session, command):
        """Process a chat command: send to LLM, execute tools loop."""
        model = command.get("model", self.default_model)
        api_key = command.get("api_key", "")
        messages = command.get("messages", [])
        stream_callback = command.get("stream_callback")

        # Call the LLM
        try:
            response = await self._call_llm(model, api_key, messages, stream_callback)
            return response
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            return {"error": str(e)}

    async def _call_llm(self, model, api_key, messages, stream_callback=None):
        """Override in subclasses. Should return a dict with 'content' and optionally 'tool_calls'."""
        raise NotImplementedError

    def send_message(self, model, api_key, messages, stream_callback=None):
        """Thread-safe: queue a message for processing and wait for response."""
        self.command_queue.put({
            "model": model,
            "api_key": api_key,
            "messages": messages,
            "stream_callback": stream_callback,
        })
        return self.response_queue.get(timeout=180)

    async def _execute_tool(self, session, tool_name, arguments):
        """Execute a tool via the MCP session."""
        result = await session.call_tool(tool_name, arguments)
        return {"tool": tool_name, "result": result.content if hasattr(result, 'content') else str(result)}
