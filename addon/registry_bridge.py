"""
registry_bridge.py — Puente entre el socket del addon y el ToolRegistry de src/.

Sin este módulo las 228 tools de `src/tools/**` son inalcanzables: el servidor MCP
real (mcp_server.py) habla con addon/_axsock.py, que solo expone métodos cmd_*
escritos a mano. Aquí se carga el registry dentro de Blender y se le da una
superficie de socket: list_tools / call_tool / describe_tool.

Se importa perezosamente para que un fallo de path no tumbe el registro del addon.
"""
import os
import sys
import threading

_registry = None
_load_error = None
_lock = threading.Lock()

# Categorías de src/tools. El registry las carga por nombre de módulo.
CATEGORIES = (
    "animation", "batch", "camera", "geometry_nodes", "geometry_nodes_extended",
    "io", "lights", "materials", "modifiers", "objects", "printing", "render",
    "rigging", "scene", "scene_utils", "shader_nodes", "shader_nodes_extended",
    "uv_texture",
)


def _src_dir():
    """Resuelve <repo>/src desde addon/registry_bridge.py."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "src")


def _ensure_path():
    src = _src_dir()
    if os.path.isdir(src) and src not in sys.path:
        sys.path.insert(0, src)
    return src


def get_registry():
    """Carga (una vez) el ToolRegistry con todas las categorías.

    Devuelve None si src/ no está disponible; el error queda en _load_error
    para que `status()` lo reporte en vez de fallar en silencio.
    """
    global _registry, _load_error
    if _registry is not None or _load_error is not None:
        return _registry

    with _lock:
        if _registry is not None or _load_error is not None:
            return _registry
        try:
            _ensure_path()
            from tools import ToolRegistry

            reg = ToolRegistry()
            for cat in CATEGORIES:
                try:
                    reg.load_category(cat)
                except Exception as exc:  # una categoría rota no invalida el resto
                    print(f"[bridge] categoría '{cat}' no cargada: {exc}")
            _registry = reg
        except Exception as exc:
            _load_error = str(exc)
            print(f"[bridge] registry no disponible: {exc}")
    return _registry


def status():
    """Estado del puente, para diagnóstico desde el cliente MCP."""
    reg = get_registry()
    if reg is None:
        return {"available": False, "error": _load_error, "src": _src_dir()}
    stats = reg.get_stats()
    return {"available": True, "src": _src_dir(), **stats}


def list_tools(category=None):
    """Lista las tools registradas, opcionalmente filtradas por categoría."""
    reg = get_registry()
    if reg is None:
        return {"tools": [], "total": 0, "error": _load_error}

    tools = reg.get_tools_by_category(category) if category else reg.list_tools()
    return {
        "tools": [t.to_dict() for t in tools],
        "total": len(tools),
    }


def describe_tool(name):
    """Devuelve la definición completa de una tool (params, ejemplos, permiso)."""
    reg = get_registry()
    if reg is None:
        return {"error": _load_error or "registry no disponible"}
    tool = reg.get_tool(name)
    if tool is None:
        return {"error": f"Tool no encontrada: {name}"}
    return tool.to_dict()


def call_tool(name, params=None):
    """Ejecuta una tool del registry y devuelve su ToolResult como dict."""
    reg = get_registry()
    if reg is None:
        return {"success": False, "error": _load_error or "registry no disponible"}
    return reg.execute_tool(name, params or {}).to_dict()
