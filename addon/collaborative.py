"""
blender-mcp — Collaborative Editing
Edición colaborativa con locks, mensajes y tareas compartidas.
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# COLLABORATIVE STATE
# ═══════════════════════════════════════════════════════════════

COLLAB_STATE_FILE = Path("/tmp/blender_mcp_collab_state.json")

_collab_state = {
    "agents": {},
    "locks": {},
    "messages": [],
    "tasks": [],
    "history": [],
}


class CollaborativeManager:
    """Gestor de edición colaborativa entre agentes."""

    def __init__(self):
        self._lock = threading.Lock()
        self._load_state()

    def _load_state(self):
        """Cargar estado desde archivo."""
        if COLLAB_STATE_FILE.exists():
            try:
                with open(COLLAB_STATE_FILE) as f:
                    _collab_state.update(json.load(f))
            except Exception:
                pass

    def _save_state(self):
        """Guardar estado a archivo."""
        try:
            with open(COLLAB_STATE_FILE, "w") as f:
                json.dump(_collab_state, f, indent=2)
        except Exception as e:
            print(f"[collab] Failed to save state: {e}")

    def register_agent(self, agent_id: str, name: str) -> bool:
        """
        Registrar agente en la sesión colaborativa.

        Args:
            agent_id: ID único del agente
            name: Nombre del agente

        Returns:
            True si éxito
        """
        with self._lock:
            _collab_state["agents"][agent_id] = {
                "name": name,
                "joined_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "objects_locked": [],
            }
            self._save_state()
            print(f"[collab] Agent registered: {name} ({agent_id})")
            return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Desregistrar agente."""
        with self._lock:
            if agent_id in _collab_state["agents"]:
                # Release all locks
                for obj_name in list(_collab_state["agents"][agent_id]["objects_locked"]):
                    self.release_lock(obj_name, agent_id)

                del _collab_state["agents"][agent_id]
                self._save_state()
                return True
            return False

    def acquire_lock(self, obj_name: str, agent_id: str) -> bool:
        """
        Adquirir lock sobre un objeto.

        Args:
            obj_name: Nombre del objeto
            agent_id: ID del agente

        Returns:
            True si lock adquirido, False si ya está bloqueado
        """
        with self._lock:
            # Check if already locked
            if obj_name in _collab_state["locks"]:
                current_owner = _collab_state["locks"][obj_name]
                if current_owner != agent_id:
                    print(f"[collab] Lock denied: {obj_name} locked by {current_owner}")
                    return False

            # Acquire lock
            _collab_state["locks"][obj_name] = agent_id
            if agent_id in _collab_state["agents"]:
                _collab_state["agents"][agent_id]["objects_locked"].append(obj_name)
                _collab_state["agents"][agent_id]["last_active"] = datetime.now().isoformat()

            self._save_state()
            print(f"[collab] Lock acquired: {obj_name} by {agent_id}")
            return True

    def release_lock(self, obj_name: str, agent_id: str) -> bool:
        """Liberar lock sobre un objeto."""
        with self._lock:
            if obj_name in _collab_state["locks"]:
                if _collab_state["locks"][obj_name] == agent_id:
                    del _collab_state["locks"][obj_name]
                    if agent_id in _collab_state["agents"]:
                        if obj_name in _collab_state["agents"][agent_id]["objects_locked"]:
                            _collab_state["agents"][agent_id]["objects_locked"].remove(obj_name)
                    self._save_state()
                    return True
            return False

    def get_lock_status(self) -> dict[str, str]:
        """Obtener estado de todos los locks."""
        return dict(_collab_state["locks"])

    def send_message(self, from_agent: str, to_agent: str, message: str) -> bool:
        """
        Enviar mensaje a otro agente.

        Args:
            from_agent: ID del agente remitente
            to_agent: ID del agente destinatario
            message: Mensaje

        Returns:
            True si éxito
        """
        with self._lock:
            _collab_state["messages"].append(
                {
                    "from": from_agent,
                    "to": to_agent,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "read": False,
                }
            )
            self._save_state()
            return True

    def get_messages(self, agent_id: str) -> list[dict]:
        """Obtener mensajes para un agente."""
        messages = [m for m in _collab_state["messages"] if m["to"] == agent_id and not m["read"]]

        # Mark as read
        for m in _collab_state["messages"]:
            if m["to"] == agent_id and not m["read"]:
                m["read"] = True

        self._save_state()
        return messages

    def create_task(self, description: str, assignee: str | None = None) -> str:
        """
        Crear tarea compartida.

        Args:
            description: Descripción de la tarea
            assignee: ID del agente asignado

        Returns:
            ID de la tarea
        """
        task_id = f"task_{int(time.time())}"

        with self._lock:
            _collab_state["tasks"].append(
                {
                    "id": task_id,
                    "description": description,
                    "assignee": assignee,
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                }
            )
            self._save_state()

        return task_id

    def update_task(self, task_id: str, status: str) -> bool:
        """Actualizar estado de una tarea."""
        with self._lock:
            for task in _collab_state["tasks"]:
                if task["id"] == task_id:
                    task["status"] = status
                    self._save_state()
                    return True
            return False

    def get_tasks(self, assignee: str | None = None) -> list[dict]:
        """Obtener tareas, opcionalmente filtradas por agente."""
        if assignee:
            return [t for t in _collab_state["tasks"] if t["assignee"] == assignee]
        return list(_collab_state["tasks"])

    def log_action(self, agent_id: str, action: str, details: dict) -> bool:
        """Registrar acción en historial."""
        with self._lock:
            _collab_state["history"].append(
                {
                    "agent": agent_id,
                    "action": action,
                    "details": details,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            self._save_state()
            return True

    def get_history(self, limit: int = 50) -> list[dict]:
        """Obtener historial reciente."""
        return _collab_state["history"][-limit:]


# ═══════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL
# ═══════════════════════════════════════════════════════════════

collab_manager = CollaborativeManager()


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def get_collab_status() -> dict:
    """Obtener estado de la sesión colaborativa."""
    return {
        "agents": list(_collab_state["agents"].keys()),
        "locks": len(_collab_state["locks"]),
        "pending_messages": sum(1 for m in _collab_state["messages"] if not m["read"]),
        "pending_tasks": sum(1 for t in _collab_state["tasks"] if t["status"] == "pending"),
    }


def is_object_locked(obj_name: str) -> str | None:
    """Verificar si un objeto está bloqueado. Retorna ID del agente o None."""
    return _collab_state["locks"].get(obj_name)
