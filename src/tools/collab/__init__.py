"""
blender-mcp-ultra — Colaboración multi-agente
Locks por objeto, mensajería, tareas y workflows (multi_agent) + biblioteca
de assets reutilizables (asset_library) + blueprints de anclas 27-pt (akb).
"""

from ...core.entities import Tool, ToolCategory, ToolPermission

try:
    import bpy
except ImportError:  # fuera de Blender: solo definiciones
    bpy = None


def _ma():
    try:
        import addon.multi_agent as ma

        return ma
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"addon.multi_agent no disponible: {e}") from e


def _lib():
    try:
        import addon.asset_library as lib

        return lib
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"addon.asset_library no disponible: {e}") from e


def _akb():
    try:
        import addon.akb as akb

        return akb
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"addon.akb no disponible: {e}") from e


# ── Locks por objeto ──


def lock_acquire(agent_id: str, resource: str, timeout: float = 30.0) -> dict:
    return _ma().acquire_lock(agent_id, resource, timeout=float(timeout))


def lock_release(agent_id: str, resource: str) -> dict:
    return _ma().release_lock(agent_id, resource)


def lock_release_all(agent_id: str) -> dict:
    return _ma().release_all_locks(agent_id)


def locks_list() -> dict:
    return {"locks": _ma().get_locks()}


# ── Mensajería ──


def message_send(
    sender_id: str, receiver_id: str, message_type: str = "info", content: str = ""
) -> dict:
    return _ma().send_message(sender_id, receiver_id, message_type, content)


def message_get(agent_id: str, unread_only: bool = True) -> dict:
    return {"messages": _ma().get_messages(agent_id, unread_only=unread_only)}


def broadcast(sender_id: str, message_type: str = "info", content: str = "") -> dict:
    return _ma().broadcast_message(sender_id, message_type, content)


# ── Tareas y workflows ──


def task_register(task_id: str, description: str, assigned_to: str = "") -> dict:
    return _ma().register_task(task_id, description, assigned_to=assigned_to or None)


def task_assign(task_id: str, agent_id: str) -> dict:
    return _ma().assign_task(task_id, agent_id)


def task_complete(task_id: str, result: str = "") -> dict:
    return _ma().complete_task(task_id, result=result or None)


def task_pending(agent_id: str = "") -> dict:
    return {"tasks": _ma().get_pending_tasks(agent_id or None)}


def task_status() -> dict:
    return _ma().get_task_status()


# ── Asset library ──


def asset_save(name: str, object_names: list, description: str = "", tags: list = None) -> dict:
    return _lib().save_asset(name, object_names, description=description, tags=tags)


def asset_save_collection(collection_name: str, asset_name: str = "") -> dict:
    return _lib().save_collection_as_asset(collection_name, asset_name=asset_name or None)


def asset_load(name: str, location: list = None) -> dict:
    return _lib().load_asset(name, location=tuple(location or (0, 0, 0)))


def asset_search(query: str = "", tags: list = None) -> dict:
    return {"assets": _lib().search_assets(query=query or None, tags=tags)}


# ── Blueprints (akb, anclas 27-pt) ──


def blueprint_save(data: dict, category: str, name: str) -> dict:
    return _akb().save_blueprint(data, category, name)


def blueprint_search(query: str = "") -> dict:
    return {"specs": _akb().get_specs(query or "")}


def blueprint_get(name: str) -> dict:
    return _akb().get_blueprint_by_name(name)


def blueprint_categories() -> dict:
    return {"categories": _akb().list_categories()}


TOOLS = [
    Tool(
        "collab.lock_acquire",
        ToolCategory.SCENE_UTILS,
        "Lock por recurso/objeto para un agente (multi-agente fino)",
        ToolPermission.WRITE,
        {
            "agent_id": {"type": "str", "required": True},
            "resource": {"type": "str", "required": True},
            "timeout": {"type": "float"},
        },
    ),
    Tool(
        "collab.lock_release",
        ToolCategory.SCENE_UTILS,
        "Liberar lock de un recurso",
        ToolPermission.WRITE,
        {
            "agent_id": {"type": "str", "required": True},
            "resource": {"type": "str", "required": True},
        },
    ),
    Tool(
        "collab.lock_release_all",
        ToolCategory.SCENE_UTILS,
        "Liberar todos los locks de un agente",
        ToolPermission.WRITE,
        {"agent_id": {"type": "str", "required": True}},
    ),
    Tool(
        "collab.locks_list",
        ToolCategory.SCENE_UTILS,
        "Listar locks activos",
        ToolPermission.READ_ONLY,
        {},
    ),
    Tool(
        "collab.message_send",
        ToolCategory.SCENE_UTILS,
        "Mensaje directo entre agentes",
        ToolPermission.WRITE,
        {
            "sender_id": {"type": "str", "required": True},
            "receiver_id": {"type": "str", "required": True},
            "message_type": {"type": "str"},
            "content": {"type": "str"},
        },
    ),
    Tool(
        "collab.message_get",
        ToolCategory.SCENE_UTILS,
        "Bandeja de un agente",
        ToolPermission.READ_ONLY,
        {"agent_id": {"type": "str", "required": True}, "unread_only": {"type": "bool"}},
    ),
    Tool(
        "collab.broadcast",
        ToolCategory.SCENE_UTILS,
        "Broadcast a todos los agentes",
        ToolPermission.WRITE,
        {
            "sender_id": {"type": "str", "required": True},
            "message_type": {"type": "str"},
            "content": {"type": "str"},
        },
    ),
    Tool(
        "collab.task_register",
        ToolCategory.SCENE_UTILS,
        "Registrar tarea en el tablero",
        ToolPermission.WRITE,
        {
            "task_id": {"type": "str", "required": True},
            "description": {"type": "str", "required": True},
            "assigned_to": {"type": "str"},
        },
    ),
    Tool(
        "collab.task_assign",
        ToolCategory.SCENE_UTILS,
        "Asignar tarea a un agente",
        ToolPermission.WRITE,
        {
            "task_id": {"type": "str", "required": True},
            "agent_id": {"type": "str", "required": True},
        },
    ),
    Tool(
        "collab.task_complete",
        ToolCategory.SCENE_UTILS,
        "Marcar tarea completada",
        ToolPermission.WRITE,
        {"task_id": {"type": "str", "required": True}, "result": {"type": "str"}},
    ),
    Tool(
        "collab.task_pending",
        ToolCategory.SCENE_UTILS,
        "Tareas pendientes (de un agente o todas)",
        ToolPermission.READ_ONLY,
        {"agent_id": {"type": "str"}},
    ),
    Tool(
        "collab.task_status",
        ToolCategory.SCENE_UTILS,
        "Estado global del tablero",
        ToolPermission.READ_ONLY,
        {},
    ),
    Tool(
        "asset.save",
        ToolCategory.IO,
        "Guardar objetos como asset reutilizable",
        ToolPermission.WRITE,
        {
            "name": {"type": "str", "required": True},
            "object_names": {"type": "list", "required": True},
            "description": {"type": "str"},
            "tags": {"type": "list"},
        },
    ),
    Tool(
        "asset.save_collection",
        ToolCategory.IO,
        "Guardar una colección como asset",
        ToolPermission.WRITE,
        {"collection_name": {"type": "str", "required": True}, "asset_name": {"type": "str"}},
    ),
    Tool(
        "asset.load",
        ToolCategory.IO,
        "Cargar un asset de la biblioteca",
        ToolPermission.WRITE,
        {"name": {"type": "str", "required": True}, "location": {"type": "list"}},
    ),
    Tool(
        "asset.search",
        ToolCategory.IO,
        "Buscar assets por texto/tags",
        ToolPermission.READ_ONLY,
        {"query": {"type": "str"}, "tags": {"type": "list"}},
    ),
    Tool(
        "blueprint.save",
        ToolCategory.IO,
        "Guardar blueprint con anclas 27-pt (data: {name, objects:[...], dims})",
        ToolPermission.WRITE,
        {
            "data": {"type": "dict", "required": True},
            "category": {"type": "str", "required": True},
            "name": {"type": "str", "required": True},
        },
    ),
    Tool(
        "blueprint.search",
        ToolCategory.IO,
        "Buscar blueprints por query",
        ToolPermission.READ_ONLY,
        {"query": {"type": "str"}},
    ),
    Tool(
        "blueprint.get",
        ToolCategory.IO,
        "Obtener blueprint por nombre",
        ToolPermission.READ_ONLY,
        {"name": {"type": "str", "required": True}},
    ),
    Tool(
        "blueprint.categories",
        ToolCategory.IO,
        "Listar categorías de blueprints",
        ToolPermission.READ_ONLY,
        {},
    ),
]

HANDLERS = {
    "collab.lock_acquire": lock_acquire,
    "collab.lock_release": lock_release,
    "collab.lock_release_all": lock_release_all,
    "collab.locks_list": locks_list,
    "collab.message_send": message_send,
    "collab.message_get": message_get,
    "collab.broadcast": broadcast,
    "collab.task_register": task_register,
    "collab.task_assign": task_assign,
    "collab.task_complete": task_complete,
    "collab.task_pending": task_pending,
    "collab.task_status": task_status,
    "asset.save": asset_save,
    "asset.save_collection": asset_save_collection,
    "asset.load": asset_load,
    "asset.search": asset_search,
    "blueprint.save": blueprint_save,
    "blueprint.search": blueprint_search,
    "blueprint.get": blueprint_get,
    "blueprint.categories": blueprint_categories,
}
