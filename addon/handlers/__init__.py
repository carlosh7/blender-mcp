"""
blender-mcp — Handler Base Class
All socket command handlers inherit from this.
Each handler module implements cmd_* methods dynamically registered by _axsock.py.
"""

from typing import Any


class BaseHandler:
    """Base class for Blender socket command handlers."""

    namespace: str = ""

    @classmethod
    def get_commands(cls) -> dict[str, str]:
        """Return {command_name: method_name} mapping for auto-registration."""
        commands = {}
        prefix = "cmd_"
        for attr_name in dir(cls):
            if attr_name.startswith(prefix):
                cmd_name = attr_name[len(prefix):]
                commands[cmd_name] = attr_name
        return commands

    @classmethod
    def help(cls) -> str:
        """Return description of what this handler module does."""
        return f"{cls.namespace or cls.__name__} — {cls.__doc__ or ''}"
