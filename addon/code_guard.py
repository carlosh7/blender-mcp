"""
code_guard.py — Guardián AST para código ejecutado vía MCP/HTTP.
Bloquea construcciones peligrosas antes de exec() dentro de Blender.
Autónomo (sin dependencias de src/) para poder usarse desde el addon.
"""

import ast

BLOCKED_IMPORTS = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "importlib",
    "ctypes",
    "pickle",
    "marshal",
    "builtins",
    "webbrowser",
    "http",
    "urllib",
    "requests",
    "asyncio",
    "threading",
    "multiprocessing",
    "signal",
    "resource",
    "mmap",
    "code",
    "codeop",
    "runpy",
    "site",
}

BLOCKED_CALLS = {
    "exec",
    "eval",
    "compile",
    "open",
    "__import__",
    "input",
    "breakpoint",
    "globals",
    "locals",
    "vars",
    "delattr",
    "setattr",
    "getattr",
    "exit",
    "quit",
    "system",
    "popen",
}

# Métodos peligrosos SOLO cuando el receptor no pertenece al namespace de bpy
# (p. ej. os.remove, Path.unlink); bpy.data.objects.remove() es legítimo.
BLOCKED_METHODS = {"remove", "unlink", "rmdir", "makedirs", "rmtree", "kill"}

ALLOWED_ROOTS = {"bpy", "C", "D", "ops"}

BLOCKED_DUNDERS = {
    "__class__",
    "__subclasses__",
    "__bases__",
    "__mro__",
    "__globals__",
    "__locals__",
    "__code__",
    "__func__",
    "__closure__",
    "__builtins__",
    "__import__",
    "__dict__",
    "__getattribute__",
    "__reduce__",
    "__reduce_ex__",
    "__init_subclass__",
}


class CodeGuardError(ValueError):
    """Raised when code contains blocked constructs."""


def _root_allowed(node) -> bool:
    """True si la cadena de atributos arranca en un nombre permitido (bpy, C, D, ops)."""
    while isinstance(node, ast.Attribute):
        node = node.value
    return isinstance(node, ast.Name) and node.id in ALLOWED_ROOTS


def check_code(code: str) -> None:
    """Lanza CodeGuardError si el código contiene construcciones bloqueadas."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return  # syntax errors surface naturally at exec time

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in BLOCKED_IMPORTS:
                    raise CodeGuardError(f"Import bloqueado: '{alias.name}'")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in BLOCKED_IMPORTS:
                raise CodeGuardError(f"Import bloqueado: '{node.module}'")
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in BLOCKED_CALLS:
                raise CodeGuardError(f"Llamada bloqueada: '{func.id}()'")
            if isinstance(func, ast.Attribute) and func.attr in BLOCKED_METHODS:
                if not _root_allowed(func.value):
                    raise CodeGuardError(f"Llamada bloqueada: '.{func.attr}()'")
            if isinstance(func, ast.Attribute) and func.attr in BLOCKED_CALLS:
                raise CodeGuardError(f"Llamada bloqueada: '.{func.attr}()'")
        elif isinstance(node, ast.Attribute):
            if node.attr in BLOCKED_DUNDERS:
                raise CodeGuardError(f"Atributo bloqueado: '{node.attr}'")
