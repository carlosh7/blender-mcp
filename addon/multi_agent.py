"""
blender-mcp — Multi-Agent System
Gestión de múltiples agentes: locks, merge, communication.

Regla de oro: COORDINAR agentes para evitar conflictos.
"""

import json
import threading
import time
from datetime import datetime

from ._paths import temp_dir as _temp_dir

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

AGENT_DIR = _temp_dir("blender_agents")
LOCKS_FILE = AGENT_DIR / "locks.json"
MESSAGES_FILE = AGENT_DIR / "messages.json"


# ═══════════════════════════════════════════════════════════════
# SISTEMA DE LOCKS
# ═══════════════════════════════════════════════════════════════

_agent_locks = {}
_lock_mutex = threading.Lock()


def _ensure_agent_dir():
    """Crear directorio de agentes."""
    AGENT_DIR.mkdir(parents=True, exist_ok=True)


def acquire_lock(agent_id, resource, timeout=30):
    """
    Adquirir un lock sobre un recurso.

    Args:
        agent_id: ID del agente
        resource: Nombre del recurso (objeto, colección, etc.)
        timeout: Tiempo máximo de espera (segundos)

    Returns:
        bool si se adquirió el lock
    """
    _ensure_agent_dir()

    start_time = time.time()

    while time.time() - start_time < timeout:
        with _lock_mutex:
            # Verificar si el recurso está libre
            if resource not in _agent_locks:
                _agent_locks[resource] = {
                    "agent": agent_id,
                    "acquired_at": datetime.now().isoformat(),
                }
                _save_locks()
                print(f"[multi] Lock adquirido: {resource} por {agent_id}")
                return True

            # Verificar si el lock expiró (más de 60 segundos)
            lock_info = _agent_locks[resource]
            lock_time = datetime.fromisoformat(lock_info["acquired_at"])
            if (datetime.now() - lock_time).seconds > 60:
                print(f"[multi] Lock expirado: {resource}")
                _agent_locks.pop(resource)
                continue

            # Otro agente tiene el lock
            print(f"[multi] Lock en uso: {resource} por {lock_info['agent']}")

        time.sleep(1)

    print(f"[multi] Timeout adquiriendo lock: {resource}")
    return False


def release_lock(agent_id, resource):
    """
    Liberar un lock.

    Args:
        agent_id: ID del agente
        resource: Nombre del recurso

    Returns:
        bool si se liberó
    """
    with _lock_mutex:
        if resource in _agent_locks:
            lock_info = _agent_locks[resource]
            if lock_info["agent"] == agent_id:
                _agent_locks.pop(resource)
                _save_locks()
                print(f"[multi] Lock liberado: {resource}")
                return True
            else:
                print(f"[multi] No puedes liberar lock de otro agente: {resource}")
                return False

    return True


def release_all_locks(agent_id):
    """Liberar todos los locks de un agente."""
    with _lock_mutex:
        to_remove = [r for r, info in _agent_locks.items() if info["agent"] == agent_id]
        for resource in to_remove:
            _agent_locks.pop(resource)

        if to_remove:
            _save_locks()
            print(f"[multi] Locks liberados: {len(to_remove)}")

    return True


def get_locks():
    """Obtener todos los locks activos."""
    return _agent_locks.copy()


def _save_locks():
    """Guardar locks a archivo."""
    _ensure_agent_dir()
    with open(LOCKS_FILE, "w") as f:
        json.dump(_agent_locks, f, indent=2)


def _load_locks():
    """Cargar locks desde archivo."""
    if LOCKS_FILE.exists():
        with open(LOCKS_FILE) as f:
            _agent_locks.update(json.load(f))


# ═══════════════════════════════════════════════════════════════
# SISTEMA DE MENSAJES
# ═══════════════════════════════════════════════════════════════

_message_queue = []


def send_message(sender_id, receiver_id, message_type, content):
    """
    Enviar un mensaje a otro agente.

    Args:
        sender_id: ID del remitente
        receiver_id: ID del destinatario (o "broadcast")
        message_type: Tipo de mensaje (task, status, request, response)
        content: Contenido del mensaje

    Returns:
        dict con el mensaje enviado
    """
    message = {
        "id": f"msg_{int(time.time() * 1000)}",
        "sender": sender_id,
        "receiver": receiver_id,
        "type": message_type,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "read": False,
    }

    _message_queue.append(message)
    _save_messages()

    print(f"[multi] Mensaje enviado: {sender_id} → {receiver_id} ({message_type})")
    return message


def get_messages(agent_id, unread_only=True):
    """
    Obtener mensajes para un agente.

    Args:
        agent_id: ID del agente
        unread_only: Solo mensajes no leídos

    Returns:
        Lista de mensajes
    """
    messages = []

    for msg in _message_queue:
        if msg["receiver"] == agent_id or msg["receiver"] == "broadcast":
            if not unread_only or not msg["read"]:
                messages.append(msg)

    return messages


def mark_message_read(message_id):
    """Marcar un mensaje como leído."""
    for msg in _message_queue:
        if msg["id"] == message_id:
            msg["read"] = True
            _save_messages()
            return True
    return False


def broadcast_message(sender_id, message_type, content):
    """Enviar mensaje a todos los agentes."""
    return send_message(sender_id, "broadcast", message_type, content)


def _save_messages():
    """Guardar mensajes a archivo."""
    _ensure_agent_dir()
    with open(MESSAGES_FILE, "w") as f:
        json.dump(_message_queue[-100:], f, indent=2)  # Últimos 100


def _load_messages():
    """Cargar mensajes desde archivo."""
    global _message_queue
    if MESSAGES_FILE.exists():
        with open(MESSAGES_FILE) as f:
            _message_queue = json.load(f)


# ═══════════════════════════════════════════════════════════════
# TAREAS DISTRIBUIDAS
# ═══════════════════════════════════════════════════════════════

_task_registry = {}


def register_task(task_id, description, assigned_to=None):
    """
    Registrar una tarea.

    Args:
        task_id: ID de la tarea
        description: Descripción
        assigned_to: Agente asignado (opcional)

    Returns:
        dict con la tarea
    """
    task = {
        "id": task_id,
        "description": description,
        "assigned_to": assigned_to,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }

    _task_registry[task_id] = task
    print(f"[multi] Tarea registrada: {task_id} - {description}")
    return task


def assign_task(task_id, agent_id):
    """Asignar una tarea a un agente."""
    if task_id in _task_registry:
        _task_registry[task_id]["assigned_to"] = agent_id
        _task_registry[task_id]["status"] = "assigned"
        print(f"[multi] Tarea {task_id} asignada a {agent_id}")
        return True
    return False


def complete_task(task_id, result=None):
    """Marcar una tarea como completada."""
    if task_id in _task_registry:
        _task_registry[task_id]["status"] = "completed"
        _task_registry[task_id]["completed_at"] = datetime.now().isoformat()
        _task_registry[task_id]["result"] = result
        print(f"[multi] Tarea completada: {task_id}")
        return True
    return False


def get_pending_tasks(agent_id=None):
    """Obtener tareas pendientes."""
    tasks = []
    for task_id, task in _task_registry.items():
        if task["status"] in ("pending", "assigned"):
            if agent_id is None or task["assigned_to"] == agent_id:
                tasks.append(task)
    return tasks


def get_task_status():
    """Obtener estado de todas las tareas."""
    pending = sum(1 for t in _task_registry.values() if t["status"] == "pending")
    assigned = sum(1 for t in _task_registry.values() if t["status"] == "assigned")
    completed = sum(1 for t in _task_registry.values() if t["status"] == "completed")

    return {
        "total": len(_task_registry),
        "pending": pending,
        "assigned": assigned,
        "completed": completed,
    }


# ═══════════════════════════════════════════════════════════════
# ORQUESTACIÓN
# ═══════════════════════════════════════════════════════════════


def create_workflow(name, steps):
    """
    Crear un workflow con pasos dependentes.

    Args:
        name: Nombre del workflow
        steps: Lista de pasos [{id, description, dependencies}]

    Returns:
        dict con el workflow
    """
    workflow = {
        "name": name,
        "steps": steps,
        "status": "pending",
        "current_step": 0,
        "created_at": datetime.now().isoformat(),
    }

    print(f"[multi] Workflow creado: {name} ({len(steps)} pasos)")
    return workflow


def execute_workflow(workflow, agent_id):
    """
    Ejecutar un workflow paso a paso.

    Args:
        workflow: Workflow a ejecutar
        agent_id: ID del agente ejecutor

    Returns:
        dict con resultados
    """
    results = {"success": [], "failed": []}

    for i, step in enumerate(workflow["steps"]):
        # Verificar dependencias
        deps = step.get("dependencies", [])
        deps_met = all(
            any(r["step"] == dep and r["success"] for r in results["success"]) for dep in deps
        )

        if not deps_met:
            print(f"[multi] Saltando paso {i + 1}: dependencias no cumplidas")
            continue

        # Ejecutar paso
        print(f"[multi] Ejecutando paso {i + 1}: {step['description']}")

        # Aquí se ejecutaría la lógica específica del paso
        # Por ahora solo registramos
        results["success"].append({"step": step["id"], "result": "executed"})

    workflow["status"] = "completed"
    print(f"[multi] Workflow completado: {workflow['name']}")

    return results


# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════


def get_agent_status(agent_id):
    """Obtener estado de un agente."""
    locks = {r: info for r, info in _agent_locks.items() if info["agent"] == agent_id}
    messages = get_messages(agent_id)
    tasks = get_pending_tasks(agent_id)

    return {
        "agent_id": agent_id,
        "locks": locks,
        "unread_messages": len(messages),
        "pending_tasks": len(tasks),
    }


def print_system_status():
    """Imprimir estado del sistema multi-agente."""
    print("\n" + "=" * 60)
    print("SISTEMA MULTI-AGENTE")
    print("=" * 60)

    print(f"\n🔒 Locks activos: {len(_agent_locks)}")
    for resource, info in _agent_locks.items():
        print(f"   {resource} → {info['agent']}")

    print(f"\n📨 Cola de mensajes: {len(_message_queue)}")

    task_status = get_task_status()
    print(f"\n📋 Tareas: {task_status['total']} total")
    print(f"   Pendientes: {task_status['pending']}")
    print(f"   Asignadas: {task_status['assigned']}")
    print(f"   Completadas: {task_status['completed']}")

    print("=" * 60)


def cleanup():
    """Limpiar todos los locks y mensajes."""
    release_all_locks("all")
    _message_queue.clear()
    _task_registry.clear()
    _save_messages()
    print("[multi] Sistema limpiado")
