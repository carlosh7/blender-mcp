"""
blender-mcp — Pre-Flight AST Code Auditor
Analiza código generado por LLM antes de ejecución.
Bloquea importaciones peligrosas y llamadas inseguras.
"""
import ast

_BLOCKED_MODULES = {
    "os", "subprocess", "sys", "shutil", "socket", "pathlib",
    "requests", "ctypes", "importlib", "pickle", "marshal",
    "codecs", "builtins", "webbrowser",
    # Rutas indirectas para recuperar builtins o alcanzar objetos vivos.
    "gc", "inspect", "operator", "functools", "code", "codeop", "runpy",
    "types", "atexit", "signal", "threading", "multiprocessing", "http",
    "urllib", "ftplib", "telnetlib", "smtplib", "tempfile", "glob", "shelve",
}
_BLOCKED_CALLS = {
    "exec", "eval", "compile", "__import__", "open",
    # getattr/setattr permiten deletrear atributos prohibidos en tiempo de
    # ejecución: getattr(bpy, "ap" + "p").
    "getattr", "setattr", "delattr", "globals", "locals", "vars", "input",
    "memoryview", "breakpoint",
}
# Atributos que dan acceso al grafo de objetos de Python y, desde ahí, a
# builtins: ().__class__.__bases__[0].__subclasses__().
_BLOCKED_ATTRS = {
    "__class__", "__bases__", "__subclasses__", "__mro__", "__globals__",
    "__builtins__", "__code__", "__closure__", "__dict__", "__getattribute__",
    "__reduce__", "__reduce_ex__", "__init_subclass__", "__subclasshook__",
    "driver_namespace",
}


class SecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.name.split(".")[0]
            if name in _BLOCKED_MODULES:
                self.errors.append(SecurityError(
                    lineno=node.lineno, col_offset=node.col_offset,
                    msg=f"Import blocked: '{name}'. This module is not allowed in LLM-generated code."
                ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            name = node.module.split(".")[0]
            if name in _BLOCKED_MODULES:
                self.errors.append(SecurityError(
                    lineno=node.lineno, col_offset=node.col_offset,
                    msg=f"Import blocked: '{name}'. This module is not allowed in LLM-generated code."
                ))
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in _BLOCKED_CALLS:
            self.errors.append(SecurityError(
                lineno=node.lineno, col_offset=node.col_offset,
                msg=f"Call blocked: '{node.func.id}()'. Dynamic execution is not allowed."
            ))
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in _BLOCKED_CALLS:
                self.errors.append(SecurityError(
                    lineno=node.lineno, col_offset=node.col_offset,
                    msg=f"Call blocked: '{node.func.attr}()'. Dynamic execution is not allowed."
                ))
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # Corta el paseo por el grafo de objetos (__class__, __subclasses__…),
        # que devuelve builtins aunque el import esté bloqueado.
        if node.attr in _BLOCKED_ATTRS:
            self.errors.append(SecurityError(
                lineno=node.lineno, col_offset=node.col_offset,
                msg=f"Attribute blocked: '{node.attr}'. Introspection is not allowed."
            ))
        self.generic_visit(node)

    def visit_Name(self, node):
        # __builtins__ como nombre suelto reabre todo lo anterior.
        if node.id in _BLOCKED_ATTRS or node.id in _BLOCKED_CALLS:
            self.errors.append(SecurityError(
                lineno=node.lineno, col_offset=node.col_offset,
                msg=f"Name blocked: '{node.id}'. Introspection is not allowed."
            ))
        self.generic_visit(node)


class SecurityError(Exception):
    def __init__(self, lineno=0, col_offset=0, msg=""):
        self.lineno = lineno
        self.col_offset = col_offset
        self.msg = msg
        super().__init__(f"Line {lineno}:{col_offset} - {msg}")


def validate(code):
    """Validate LLM-generated code. Returns list of SecurityErrors (empty = safe)."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [SecurityError(lineno=e.lineno or 0, col_offset=e.offset or 0, msg=f"SyntaxError: {e.msg}")]
    visitor = SecurityVisitor()
    visitor.visit(tree)
    return visitor.errors
