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
}
_BLOCKED_CALLS = {"exec", "eval", "compile", "__import__", "open"}


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
