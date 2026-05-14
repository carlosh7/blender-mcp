"""
blender-mcp — Streaming Output UI
Displays streaming LLM responses in Blender's text editor.
"""
import bpy
import time


def get_or_create_text_block(name="blender-mcp-stream"):
    """Get or create a text data-block for streaming output."""
    text = bpy.data.texts.get(name)
    if text is None:
        text = bpy.data.texts.new(name)
    return text


def clear_stream():
    """Clear the streaming text block."""
    text = get_or_create_text_block()
    text.clear()


def append_stream(content):
    """Append text to the streaming output (thread-safe via timer)."""
    def _append():
        text = get_or_create_text_block()
        text.write(content)
        # Scroll to end
        text.current_line_index = len(text.lines) - 1
        return None

    if bpy.app.timers:
        bpy.app.timers.register(_append, first_interval=0.0)
    else:
        _append()


def show_stream_in_editor():
    """Open the streaming text in Blender's text editor area."""
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.spaces[0].text = get_or_create_text_block()
                return

    # If no text editor, split current area
    for area in bpy.data.screens[0].areas:
        if area.type == 'VIEW_3D':
            bpy.ops.screen.area_split(direction='VERTICAL', factor=0.7)
            for child in area.children:
                if child.type != 'VIEW_3D':
                    child.type = 'TEXT_EDITOR'
                    child.spaces[0].text = get_or_create_text_block()
            return
