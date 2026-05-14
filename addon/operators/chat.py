"""
blender-mcp — Chat Operators (embedded-first + fallback)
"""
import bpy
import time
import threading
import os
from bpy.types import Operator
from .. import _axsock as bsock


class OP_Send(Operator):
    bl_idname = "aimcp.send"
    bl_label = "Send"

    def execute(self, ctx):
        bsock._stop_agent = False
        txt = ctx.scene.aimcp_input.strip()
        if not txt:
            return {'CANCELLED'}

        # Check if model is configured
        model = ctx.scene.aimcp_model
        if not model:
            ctx.scene.aimcp_chat.add("system", "⚠️ No AI model configured. Go to Scene Properties → Axiom Engine Config → Refresh Models → select one.", scene=ctx.scene)
            ctx.scene.aimcp_input = ""
            if ctx.area:
                ctx.area.tag_redraw()
            return {'FINISHED'}

        ctx.scene.aimcp_chat.add("user", txt, scene=ctx.scene)
        ctx.scene.aimcp_input = ""
        ctx.scene.aimcp_waiting = True
        ctx.scene.aimcp_pending_msg_id = ""
        if ctx.area:
            ctx.area.tag_redraw()

        # ── 1. Try embedded client (inside Blender, no external process) ──
        try:
            from ..operators.embedded import _embedded_client
            if _embedded_client is not None:
                self._send_embedded(ctx, txt)
                return {'FINISHED'}
        except Exception:
            pass

        # ── 2. Queue to socket for external mcp_server.py ──
        msg_id = str(time.time())
        with bsock._chat_lock:
            bsock._chat_queue.append({"id": msg_id, "message": txt, "timestamp": time.time()})
        ctx.scene.aimcp_pending_msg_id = msg_id

        # Start polling (auto_process handles timeout messages)
        bpy.app.timers.register(self._make_poller(ctx, msg_id), first_interval=0.5)
        return {'FINISHED'}

    def _make_poller(self, ctx, msg_id):
        """Create polling function that checks for response."""
        def check():
            scene = getattr(bpy.context, "scene", None)
            if not scene:
                return 1.0
            mid = scene.aimcp_pending_msg_id
            if not mid:
                return None
            with bsock._chat_lock:
                status = bsock._chat_responses.get(mid + "_status", None)
                if status:
                    scene.aimcp_chat.add("status", status, is_update=True, scene=scene)
                resp = bsock._chat_responses.pop(mid, None)
            if resp is None:
                return 0.5
            if len(scene.aimcp_chat.msgs) > 0 and scene.aimcp_chat.msgs[-1].role == 'status' and scene.aimcp_chat.msgs[-1].text.endswith("..."):
                scene.aimcp_chat.msgs.remove(len(scene.aimcp_chat.msgs) - 1)
            scene.aimcp_chat.add("assistant", resp, scene=scene)
            scene.aimcp_status = ""
            scene.aimcp_waiting = False
            scene.aimcp_pending_msg_id = ""
            bsock._chat_responses.pop(mid + "_status", None)
            return None
        return check

    def _send_embedded(self, ctx, txt):
        """Send via embedded client inside Blender."""
        from ..operators.embedded import _embedded_client
        from ..config_cache import get_provider_config

        provider = ctx.scene.aimcp_provider or "opencode-go"
        model = ctx.scene.aimcp_model or getattr(_embedded_client, 'default_model', 'gpt-4o-mini')

        env_map = {"opencode-go": "OPENAI_API_KEY", "openai": "OPENAI_API_KEY",
                   "deepseek": "DEEPSEEK_API_KEY", "openrouter": "OPENROUTER_API_KEY",
                   "anthropic": "ANTHROPIC_API_KEY", "google": "GOOGLE_API_KEY"}
        api_key = os.environ.get(env_map.get(provider, ""))
        if not api_key:
            cfg = get_provider_config(provider)
            api_key = cfg.get("api_key", "")

        if not api_key:
            # No API key — queue for socket instead
            msg_id = str(time.time())
            with bsock._chat_lock:
                bsock._chat_queue.append({"id": msg_id, "message": txt, "timestamp": time.time()})
            ctx.scene.aimcp_pending_msg_id = msg_id
            bpy.app.timers.register(self._make_poller(ctx, msg_id), first_interval=0.5)
            return

        def process():
            try:
                result = _embedded_client.send_message(
                    model, api_key, [{"role": "user", "content": txt}]
                )
                content = result.get("content", "")
                if content:
                    def update():
                        ctx.scene.aimcp_chat.add("assistant", content, scene=ctx.scene)
                        ctx.scene.aimcp_waiting = False
                        return None
                    bpy.app.timers.register(update, first_interval=0.0)
            except Exception as e:
                def update():
                    ctx.scene.aimcp_chat.add("system", f"Error: {str(e)[:80]}", scene=ctx.scene)
                    ctx.scene.aimcp_waiting = False
                    return None
                bpy.app.timers.register(update, first_interval=0.0)

        threading.Thread(target=process, daemon=True).start()


class OP_StopAgent(Operator):
    bl_idname = "aimcp.stop_agent"
    bl_label = "Stop"

    def execute(self, ctx):
        bsock._stop_agent = True
        ctx.scene.aimcp_waiting = False
        ctx.scene.aimcp_ai_state = "connected"
        ctx.scene.aimcp_status = "STOPPED"
        if ctx.area:
            ctx.area.tag_redraw()
        return {'FINISHED'}


class OP_ClearChat(Operator):
    bl_idname = "aimcp.clear_chat"
    bl_label = "Clear"

    def execute(self, ctx):
        ctx.scene.aimcp_chat.clear_all()
        bsock._clear_memory_flag = True
        ctx.scene.aimcp_chat_index = -1
        if ctx.area:
            ctx.area.tag_redraw()
        return {'FINISHED'}


class OP_CopyChat(Operator):
    bl_idname = "blendermcp.copy_chat"
    bl_label = "Copy Chat"
    bl_description = "Copy entire chat to clipboard"

    def execute(self, context):
        lines = []
        for msg in context.scene.aimcp_chat.msgs:
            tag = "User" if msg.role == "user" else "AI" if msg.role == "assistant" else "Sys"
            lines.append(f"[{tag}] {msg.text}")
        text = "\n".join(lines)
        context.window_manager.clipboard = text
        self.report({'INFO'}, f"Chat copied ({len(lines)} messages)")
        return {'FINISHED'}


class OP_ExportLog(Operator):
    bl_idname = "blendermcp.export_log"
    bl_label = "Export Chat Log"
    bl_description = "Save chat history to a text block in Blender"

    def execute(self, context):
        scene = context.scene
        text_name = "axiom_chat_log"
        txt = bpy.data.texts.get(text_name)
        if txt:
            bpy.data.texts.remove(txt)
        txt = bpy.data.texts.new(text_name)
        txt.write("=== AXIOM Chat Log ===\n\n")
        for msg in scene.aimcp_chat.msgs:
            tag = "User" if msg.role == "user" else "AI" if msg.role == "assistant" else "System"
            txt.write(f"[{tag}] {msg.text}\n")
        # Also write to fixed log file
        import json, os
        log_path = os.path.expanduser("~/.config/blender-mcp/chat_log_export.txt")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w') as f:
            f.write("=== AXIOM Chat Log ===\n\n")
            for msg in scene.aimcp_chat.msgs:
                tag = "User" if msg.role == "user" else "AI" if msg.role == "assistant" else "System"
                f.write(f"[{tag}] {msg.text}\n")
        self.report({'INFO'}, f"Chat log saved to ~/.config/blender-mcp/chat_log_export.txt")
        # Open in Text Editor
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'TEXT_EDITOR':
                    area.spaces[0].text = txt
                    return {'FINISHED'}
        # If no text editor open, show in info
        self.report({'INFO'}, f"Log also available as text block '{text_name}'")
        return {'FINISHED'}


CHAT_OPERATORS = [OP_Send, OP_StopAgent, OP_ClearChat, OP_CopyChat, OP_ExportLog]


def register_chat_operators():
    from bpy.utils import register_class
    for cls in CHAT_OPERATORS:
        register_class(cls)


def unregister_chat_operators():
    from bpy.utils import unregister_class
    for cls in reversed(CHAT_OPERATORS):
        unregister_class(cls)
