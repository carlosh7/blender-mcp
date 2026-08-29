#!/usr/bin/env python3
"""
blender-mcp — Gateway MCP canónico.
Registra SIEMPRE el registry completo de src/ (239 tools) leyendo los
metadatos en local, sin necesidad de que Blender esté arrancado; la
ejecución va por socket (:9876) con reconexión transparente.
Compatible con opencode, Claude Desktop, Cursor, Claude Code, etc.

Modo lite (--lite o BLENDER_MCP_LITE=1): registra solo las tools núcleo +
`tools_search` + `tool_execute` (~26 en vez de 248) — reduce el coste de
contexto por petición de ~30k a ~2k tokens sin perder capacidad: el resto
del registry se descubre con tools_search y se ejecuta con tool_execute.

Transport: stdio por defecto (clientes MCP locales); `--sse` para HTTP en :9879.
"""

import json
import logging
import os
import sys
from pathlib import Path

from blender_connection import get_blender
from blender_mcp.platform import get_log_dir

_log_dir = get_log_dir()
_log_file = str(_log_dir / "server.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr), logging.FileHandler(_log_file)],
)
logger = logging.getLogger("blender-mcp")

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP("blender-mcp", log_level="INFO")


def _load_code_guard():
    """Carga code_guard: paquete blender_mcp (wheel) o addon/ local (repo)."""
    try:
        from blender_mcp import code_guard as mod

        return mod
    except Exception:
        pass
    import importlib.util

    for guard_path in (
        Path(__file__).resolve().parent / "addon" / "code_guard.py",  # repo checkout
        Path(__file__).resolve().parent / "code_guard.py",  # legacy flat
    ):
        if guard_path.exists():
            try:
                spec = importlib.util.spec_from_file_location("bmcp_code_guard", guard_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
            except Exception:
                continue
    return None


_code_guard = _load_code_guard()


def RO():
    return dict(annotations=ToolAnnotations(readOnlyHint=True))


def RW():
    return dict(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))


@mcp.tool(**RO())
def get_scene_info() -> str:
    """Get information about the current Blender scene (objects, counts, names)."""
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)


@mcp.tool(**RW())
def execute_blender_code(code: str) -> str:
    """Ejecuta código Python en Blender. Usa search_api_docs primero para encontrar la API correcta."""
    if _code_guard is not None:
        try:
            _code_guard.check_code(code)
        except _code_guard.CodeGuardError as e:
            return f"⛔ Bloqueado por seguridad: {e}"
    b = get_blender()
    result = b.send_command("execute_code", {"code": code})
    out = f"Salida:\n{result.get('output', '')}"
    if "result" in result:
        out += f"\nResultado: {result['result']}"
    return out


@mcp.tool(**RO())
def get_viewport_screenshot() -> str:
    """Captura una imagen del viewport 3D de Blender."""
    b = get_blender()
    result = b.send_command("get_viewport_screenshot")
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Captura guardada en: {result['filepath']}"


@mcp.tool(**RO())
def search_api_docs(query: str) -> str:
    """Busca en la documentación de Blender API. Siempre consulta esto ANTES de ejecutar código."""
    b = get_blender()
    result = b.send_command("search_api_docs", {"query": query})
    return json.dumps(result, indent=2)


@mcp.tool(**RO())
def get_python_api_docs(topic: str) -> str:
    """Obtiene documentación detallada de un tema específico de Blender API. Ej: 'bpy.ops.mesh.primitive_cylinder_add'."""
    b = get_blender()
    result = b.send_command("get_python_api_docs", {"topic": topic})
    return json.dumps(result, indent=2)


@mcp.tool(**RW())
def snap_and_parent(obj_move: str, obj_target: str, anchor_move: str, anchor_target: str) -> str:
    """Snap determinista y vinculación jerárquica automática (Parenting).
    Une dos objetos haciendo coincidir sus anclas (27-pt system).
    Formatos de ancla: FRONT_BOTTOM_LEFT, FRONT_BOTTOM_RIGHT, ..., TOP_CENTER,
    BOTTOM_CENTER, CENTROID (ver addon/anchor_system.py:ANCHOR_NAMES)."""
    b = get_blender()
    r = b.send_command(
        "snap_and_parent",
        {
            "obj_move": obj_move,
            "obj_target": obj_target,
            "anchor_move": anchor_move,
            "anchor_target": anchor_target,
        },
    )
    return json.dumps(r, indent=2)


@mcp.tool(**RW())
def tool_execute(tool_name: str, params: dict | None = None) -> str:
    """Ejecuta cualquier tool del registry por nombre (239 disponibles; descúbrelas con tools_search).
    Acepta `material.pbr` (registry) o `material_pbr` (nombre MCP)."""
    b = get_blender()
    return json.dumps(
        b.send_command(
            "tool", {"tool_name": _normalize_registry_name(tool_name), "params": params or {}}
        ),
        indent=2,
    )


@mcp.resource("blender://scene/info")
def resource_scene_info() -> str:
    b = get_blender()
    return json.dumps(b.send_command("get_scene_info"), indent=2)


# ── Registro dinámico: expone TODOS los tools del registry vía socket ──

_TYPE_MAP = {
    "str": str,
    "string": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": list,
    "any": object,
}

_BASE_TOOLS = {
    "ping",
    "get_scene_info",
    "execute_blender_code",
    "get_viewport_screenshot",
    "search_api_docs",
    "get_python_api_docs",
    "snap_and_parent",
}

# Modo lite: subconjunto núcleo del registry (el resto se alcanza con
# tool_execute tras descubrirlo con tools_search)
_LITE_CORE_TOOLS = {
    "scene.get_info",
    "scene.query",
    "object.create",
    "object.transform",
    "object.place_bottom",
    "material.pbr",
    "material.assign",
    "light.three_point",
    "camera.create",
    "camera.set_framing",
    "render.render",
    "render.preview",
    "render.set_engine",
    "inspect.view",
    "mesh.bevel_edges",
    "docs.scene",
    "tools.search",
    "guidance.list",
    "guidance.get",
}


def _lite_mode() -> bool:
    if "--lite" in sys.argv:
        return True
    return os.getenv("BLENDER_MCP_LITE", "").strip().lower() in ("1", "true", "yes")


def _normalize_registry_name(name: str) -> str:
    """Acepta `material.pbr` (registry) o `material_pbr` (nombre MCP)."""
    name = name.strip()
    if "." not in name and "_" in name:
        name = name.replace("_", ".", 1)
    return name


def _list_registry_tools_local():
    """Metadatos del registry de src/ construido en este proceso (sin Blender).

    Es la misma fuente que consulta el addon via `list_tools` (cmd_list_tools
    construye el mismo ToolRegistry in-process), pero sin depender de que
    Blender esté arrancado. Devuelve None si src/ no está disponible.
    """
    try:
        from mcp_ultra.presentation.mcp_server import register_all_tools
        from mcp_ultra.tools import ToolRegistry
    except Exception as e:
        logger.warning(f"Registry local (src/) no disponible: {e}")
        return None
    try:
        registry = ToolRegistry()
        register_all_tools(registry)
        return [tool.to_dict() for tool in registry.list_tools()]
    except Exception as e:
        logger.warning(f"Fallo construyendo el registry local: {e}")
        return None


def _register_dynamic_tools() -> int:
    """Exponer el registry completo (239 tools) como tools MCP reales.

    Los metadatos se leen del registry local de src/ (no requiere Blender);
    fallback: `list_tools` por socket si src/ no está importable. Los
    handlers siempre ejecutan por socket, así que una tool llamada antes de
    arrancar Blender falla con error de conexión y funciona en cuanto
    Blender esté arriba (get_blender reconecta por llamada).
    """
    import inspect
    from inspect import Parameter

    tools = _list_registry_tools_local()
    if tools is None:
        try:
            b = get_blender()
            resp = b.send_command("list_tools")
            tools = resp.get("tools", []) if isinstance(resp, dict) else []
        except Exception as e:
            logger.warning(f"Blender no disponible para tools dinámicas: {e}")
            return 0

    lite = _lite_mode()
    if lite:
        # Solo el núcleo: el resto del registry se alcanza vía tool_execute
        tools = [t for t in tools if t.get("name") in _LITE_CORE_TOOLS]

    count = 0
    for tool in tools:
        raw_name = str(tool.get("name", "")).strip()
        if not raw_name:
            continue
        name = raw_name.replace(".", "_")
        if name in _BASE_TOOLS or name.startswith("_"):
            continue
        desc = tool.get("description") or raw_name
        params = tool.get("parameters") or {}

        def _make_handler(tname: str):
            def handler(**kwargs):
                b2 = get_blender()
                return json.dumps(
                    b2.send_command("tool", {"tool_name": tname, "params": kwargs}),
                    indent=2,
                )

            return handler

        fn = _make_handler(raw_name)
        sig_params = []
        for pname, pdef in params.items():
            ann = _TYPE_MAP.get(str(pdef.get("type", "str")), str)
            if pdef.get("required"):
                sig_params.append(Parameter(pname, Parameter.KEYWORD_ONLY, annotation=ann))
            else:
                default = pdef.get("default")
                if default is None and ann is not object:
                    try:
                        default = ann()
                    except Exception:
                        default = None
                sig_params.append(
                    Parameter(pname, Parameter.KEYWORD_ONLY, default=default, annotation=ann)
                )
        try:
            fn.__signature__ = inspect.Signature(sig_params)
        except Exception:
            fn.__signature__ = inspect.Signature([Parameter("kwargs", Parameter.VAR_KEYWORD)])
        try:
            mcp.tool(name=name, description=desc)(fn)
            count += 1
        except Exception as e:
            logger.warning(f"Tool dinámica '{name}' no registrada: {e}")
    return count


def main():
    dynamic = _register_dynamic_tools()
    mode = "lite" if _lite_mode() else "full"
    logger.info(
        f"Starting MCP Server [{mode}] ({7 + dynamic} tools: 7 base + {dynamic} registry)..."
    )

    try:
        sse = "--sse" in sys.argv or os.getenv("BLENDER_MCP_MODE", "").lower() == "sse"
        if sse:
            import uvicorn

            app = mcp.sse_app()
            # 0.0.0.0 para acceso remoto (Docker/bridge); localhost por defecto
            host = os.getenv("MCP_SSE_HOST") or os.getenv("BLENDER_MCP_HOST", "127.0.0.1")
            port = int(os.getenv("MCP_SSE_PORT") or os.getenv("BLENDER_MCP_PORT", "9879"))
            logger.info("Uvicorn starting on %s:%s", host, port)
            uvicorn.run(app, host=host, port=port, log_level="info")
        else:
            logger.info("Transport: stdio")
            mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"MCP SERVER ERROR: {e}", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
