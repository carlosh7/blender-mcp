"""
blender-mcp — State Manager
Persistencia, backup, historial de acciones, anti-loop.

Regla de oro: SIEMPRE guardar estado después de cada operación.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

import bpy

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

STATE_DIR = Path("/tmp/blender_mcp_state")
BACKUP_DIR = Path("/tmp/blender_mcp_backups")
LOG_FILE = STATE_DIR / "action_log.json"
STATE_FILE = STATE_DIR / "agent_state.json"
MAX_BACKUPS = 10
MAX_ACTION_HISTORY = 100
AUTO_SAVE_INTERVAL = 30  # seconds


# ═══════════════════════════════════════════════════════════════
# ESTADO DEL AGENTE
# ═══════════════════════════════════════════════════════════════

_agent_state = {
    "project_name": "blender_project",
    "created_objects": [],
    "scene_snapshot": None,
    "attempts": {},
    "max_attempts": 3,
    "action_history": [],
    "last_action": None,
    "last_save": None,
    "session_start": None,
    "total_actions": 0,
}


def _ensure_dirs():
    """Crear directorios si no existen."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def init_state(project_name=None):
    """
    Inicializar el estado del agente.

    Args:
        project_name: Nombre del proyecto (opcional)
    """
    _ensure_dirs()

    if project_name:
        _agent_state["project_name"] = project_name

    _agent_state["session_start"] = datetime.now().isoformat()
    _agent_state["created_objects"] = []
    _agent_state["action_history"] = []
    _agent_state["attempts"] = {}
    _agent_state["total_actions"] = 0

    # Tomar snapshot de la escena actual
    _agent_state["scene_snapshot"] = _take_snapshot()

    _save_state()
    print(f"[state] Inicializado: {_agent_state['project_name']}")


def _take_snapshot():
    """Tomar snapshot de la escena actual."""
    return {
        "objects": [obj.name for obj in bpy.data.objects],
        "materials": [mat.name for mat in bpy.data.materials],
        "collections": [col.name for col in bpy.data.collections],
        "timestamp": datetime.now().isoformat(),
    }


def _save_state():
    """Guardar estado a archivo."""
    _ensure_dirs()
    _agent_state["last_save"] = datetime.now().isoformat()

    with open(STATE_FILE, "w") as f:
        json.dump(_agent_state, f, indent=2)


def load_state():
    """Cargar estado desde archivo."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            loaded = json.load(f)
            _agent_state.update(loaded)
            print(f"[state] Cargado: {_agent_state['project_name']}")
            return True
    return False


def get_state():
    """Obtener estado actual."""
    return _agent_state.copy()


# ═══════════════════════════════════════════════════════════════
# HISTORIAL DE ACCIONES
# ═══════════════════════════════════════════════════════════════


def log_action(action_type, details=None, success=True):
    """
    Registrar una acción en el historial.

    Args:
        action_type: Tipo de acción (create, modify, delete, save, etc.)
        details: Detalles adicionales (diccionario)
        success: Si la acción fue exitosa
    """
    entry = {
        "action": action_type,
        "details": details or {},
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "objects_before": len(bpy.data.objects),
    }

    _agent_state["action_history"].append(entry)
    _agent_state["last_action"] = action_type
    _agent_state["total_actions"] += 1

    # Limitar historial
    if len(_agent_state["action_history"]) > MAX_ACTION_HISTORY:
        _agent_state["action_history"] = _agent_state["action_history"][-MAX_ACTION_HISTORY:]

    _save_state()

    # También log a archivo
    _log_to_file(entry)


def _log_to_file(entry):
    """Agregar entrada al archivo de log."""
    _ensure_dirs()

    logs = []
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            logs = json.load(f)

    logs.append(entry)

    # Mantener solo los últimos 1000
    if len(logs) > 1000:
        logs = logs[-1000:]

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def get_action_history(limit=20):
    """Obtener las últimas N acciones."""
    return _agent_state["action_history"][-limit:]


def get_actions_by_type(action_type):
    """Obtener acciones filtradas por tipo."""
    return [a for a in _agent_state["action_history"] if a["action"] == action_type]


# ═══════════════════════════════════════════════════════════════
# ANTI-LOOP SYSTEM
# ═══════════════════════════════════════════════════════════════


def check_loop(action_name):
    """
    Verificar si una acción está en loop.

    Args:
        action_name: Nombre de la acción a verificar

    Returns:
        dict con {is_loop: bool, count: int, message: str}
    """
    # Contar acciones recientes del mismo tipo
    recent = _agent_state["action_history"][-5:]
    same_action = [a for a in recent if a["action"] == action_name]
    count = len(same_action)

    is_loop = count >= _agent_state["max_attempts"]

    if is_loop:
        _agent_state["attempts"][action_name] = _agent_state["attempts"].get(action_name, 0) + 1
        _save_state()

        return {
            "is_loop": True,
            "count": count,
            "total_attempts": _agent_state["attempts"][action_name],
            "message": f"LOOP DETECTADO: '{action_name}' ejecutada {count} veces seguidas",
        }

    return {
        "is_loop": False,
        "count": count,
        "total_attempts": _agent_state["attempts"].get(action_name, 0),
        "message": f"OK: '{action_name}' ejecutada {count} veces",
    }


def reset_attempts(action_name=None):
    """Reiniciar contador de intentos."""
    if action_name:
        _agent_state["attempts"].pop(action_name, None)
    else:
        _agent_state["attempts"] = {}
    _save_state()


def register_object(obj_name):
    """Registrar un objeto creado."""
    if obj_name not in _agent_state["created_objects"]:
        _agent_state["created_objects"].append(obj_name)
        _save_state()


def unregister_object(obj_name):
    """Des-registrar un objeto eliminado."""
    if obj_name in _agent_state["created_objects"]:
        _agent_state["created_objects"].remove(obj_name)
        _save_state()


# ═══════════════════════════════════════════════════════════════
# BACKUP SYSTEM
# ═══════════════════════════════════════════════════════════════


def create_backup(label=None):
    """
    Crear backup del archivo .blend actual.

    Args:
        label: Etiqueta opcional para el backup

    Returns:
        Ruta del backup creado
    """
    _ensure_dirs()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    if label:
        backup_name += f"_{label}"

    backup_path = BACKUP_DIR / f"{backup_name}.blend"

    # Guardar archivo actual
    filepath = bpy.data.filepath
    if filepath:
        shutil.copy2(filepath, backup_path)
        print(f"[state] Backup creado: {backup_path}")
    else:
        # Si no hay archivo guardado, guardar uno nuevo
        bpy.ops.wm.save_as_mainfile(filepath=str(backup_path))
        print(f"[state] Backup creado (nuevo): {backup_path}")

    # Limpiar backups antiguos
    _cleanup_old_backups()

    return str(backup_path)


def _cleanup_old_backups():
    """Eliminar backups antiguos manteniendo solo los últimos MAX_BACKUPS."""
    backups = sorted(BACKUP_DIR.glob("backup_*.blend"), key=os.path.getmtime)

    while len(backups) > MAX_BACKUPS:
        oldest = backups.pop(0)
        oldest.unlink()
        print(f"[state] Backup eliminado: {oldest.name}")


def list_backups():
    """Listar backups disponibles."""
    backups = sorted(BACKUP_DIR.glob("backup_*.blend"), key=os.path.getmtime, reverse=True)

    print("\n📋 Backups disponibles:")
    for i, backup in enumerate(backups):
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        size = backup.stat().st_size / 1024  # KB
        print(f"  {i + 1}. {backup.name} ({size:.1f} KB) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

    return backups


def restore_backup(backup_path=None, index=0):
    """
    Restaurar desde backup.

    Args:
        backup_path: Ruta del backup (opcional)
        index: Índice del backup a restaurar (si no se especifica path)
    """
    if backup_path:
        path = Path(backup_path)
    else:
        backups = list_backups()
        if not backups:
            print("[state] No hay backups disponibles")
            return False
        path = backups[index]

    if not path.exists():
        print(f"[state] Backup no encontrado: {path}")
        return False

    # Cargar el backup
    bpy.ops.wm.open_mainfile(filepath=str(path))
    print(f"[state] Backup restaurado: {path.name}")
    return True


# ═══════════════════════════════════════════════════════════════
# AUTO-SAVE
# ═══════════════════════════════════════════════════════════════


def auto_save():
    """
    Guardar automáticamente el archivo actual.

    Returns:
        Ruta del archivo guardado o None
    """
    project_name = _agent_state["project_name"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if bpy.data.filepath:
        # Archivo ya existe, guardar
        bpy.ops.wm.save_mainfile()
        filepath = bpy.data.filepath
        print(f"[state] Auto-guardado: {filepath}")
    else:
        # Archivo nuevo, guardar con nombre
        filepath = f"/tmp/{project_name}_{timestamp}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
        print(f"[state] Auto-guardado (nuevo): {filepath}")

    _agent_state["last_save"] = datetime.now().isoformat()
    _save_state()

    return filepath


def save_project(name=None):
    """
    Guardar proyecto con nombre específico.

    Args:
        name: Nombre del proyecto (sin extensión)

    Returns:
        Ruta del archivo guardado
    """
    if name:
        _agent_state["project_name"] = name

    project_name = _agent_state["project_name"]
    filepath = f"/tmp/{project_name}.blend"

    bpy.ops.wm.save_as_mainfile(filepath=filepath)

    _agent_state["last_save"] = datetime.now().isoformat()
    _save_state()

    print(f"[state] Proyecto guardado: {filepath}")
    return filepath


def get_file_status():
    """Obtener estado del archivo."""
    return {
        "filepath": bpy.data.filepath or None,
        "is_saved": bool(bpy.data.filepath),
        "has_unsaved": bpy.data.is_dirty,
        "project_name": _agent_state["project_name"],
        "last_save": _agent_state.get("last_save"),
    }


# ═══════════════════════════════════════════════════════════════
# SCENE SNAPSHOT
# ═══════════════════════════════════════════════════════════════


def update_snapshot():
    """Actualizar snapshot de la escena."""
    _agent_state["scene_snapshot"] = _take_snapshot()
    _save_state()


def compare_with_snapshot():
    """
    Comparar escena actual con el último snapshot.

    Returns:
        dict con diferencias encontradas
    """
    current = _take_snapshot()
    previous = _agent_state.get("scene_snapshot", {})

    if not previous:
        return {"changed": False, "message": "No hay snapshot previo"}

    old_objects = set(previous.get("objects", []))
    new_objects = set(current.get("objects", []))

    added = new_objects - old_objects
    removed = old_objects - new_objects

    return {
        "changed": bool(added or removed),
        "added": list(added),
        "removed": list(removed),
        "message": f"Agregados: {len(added)}, Eliminados: {len(removed)}",
    }


# ═══════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════


def print_state_summary():
    """Imprimir resumen del estado actual."""
    print("\n" + "=" * 60)
    print("ESTADO DEL AGENTE")
    print("=" * 60)
    print(f"Proyecto: {_agent_state['project_name']}")
    print(f"Sesión: {_agent_state.get('session_start', 'N/A')}")
    print(f"Acciones totales: {_agent_state['total_actions']}")
    print(f"Objetos creados: {len(_agent_state['created_objects'])}")
    print(f"Última acción: {_agent_state.get('last_action', 'N/A')}")
    print(f"Último save: {_agent_state.get('last_save', 'N/A')}")

    file_status = get_file_status()
    print(f"\nArchivo: {file_status['filepath'] or 'UNSAVED'}")
    print(f"Guardado: {'Sí' if file_status['is_saved'] else 'No'}")
    print(f"Sin guardar: {'Sí' if file_status['has_unsaved'] else 'No'}")

    if _agent_state["action_history"]:
        print("\nÚltimas 5 acciones:")
        for action in _agent_state["action_history"][-5:]:
            status = "✅" if action["success"] else "❌"
            print(f"  {status} {action['action']} - {action['timestamp']}")

    print("=" * 60)
