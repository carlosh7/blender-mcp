"""
blender-mcp — Progress Reporter
Mensajes de progreso, resume, confirmación del usuario.

Regla de oro: SIEMPRE informar qué se está haciendo.
"""
import sys
import time
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# ESTADO DEL PROGRESO
# ═══════════════════════════════════════════════════════════════

_progress_state = {
    "current_task": None,
    "total_steps": 0,
    "completed_steps": 0,
    "start_time": None,
    "history": [],
    "pending_tasks": [],
}


# ═══════════════════════════════════════════════════════════════
# MENSAJES DE PROGRESO
# ═══════════════════════════════════════════════════════════════

def start_progress(task_name, total_steps=1):
    """
    Iniciar seguimiento de progreso.
    
    Args:
        task_name: Nombre de la tarea
        total_steps: Número total de pasos
    """
    _progress_state["current_task"] = task_name
    _progress_state["total_steps"] = total_steps
    _progress_state["completed_steps"] = 0
    _progress_state["start_time"] = time.time()
    
    print(f"\n🚀 Iniciando: {task_name}")
    print(f"   Pasos: {total_steps}")
    _print_progress_bar(0, total_steps)


def update_progress(step_name, step_number=None):
    """
    Actualizar progreso.
    
    Args:
        step_name: Nombre del paso actual
        step_number: Número del paso (opcional, auto-incrementa)
    """
    if step_number is None:
        _progress_state["completed_steps"] += 1
    else:
        _progress_state["completed_steps"] = step_number
    
    completed = _progress_state["completed_steps"]
    total = _progress_state["total_steps"]
    
    elapsed = time.time() - _progress_state["start_time"]
    eta = (elapsed / completed * (total - completed)) if completed > 0 else 0
    
    print(f"   [{completed}/{total}] {step_name}")
    _print_progress_bar(completed, total)
    
    if eta > 0:
        print(f"   ⏱️  ETA: {eta:.0f}s")


def complete_progress(summary=None):
    """
    Completar seguimiento de progreso.
    
    Args:
        summary: Resumen final (opcional)
    """
    elapsed = time.time() - _progress_state["start_time"]
    
    print(f"\n✅ Completado: {_progress_state['current_task']}")
    print(f"   Tiempo: {elapsed:.1f}s")
    print(f"   Pasos: {_progress_state['completed_steps']}/{_progress_state['total_steps']}")
    
    if summary:
        print(f"   Resumen: {summary}")
    
    # Guardar en historial
    _progress_state["history"].append({
        "task": _progress_state["current_task"],
        "steps": _progress_state["completed_steps"],
        "total": _progress_state["total_steps"],
        "time": elapsed,
        "timestamp": datetime.now().isoformat(),
    })
    
    # Reset
    _progress_state["current_task"] = None
    _progress_state["completed_steps"] = 0
    _progress_state["total_steps"] = 0


def _print_progress_bar(current, total, width=30):
    """Imprimir barra de progreso."""
    if total == 0:
        return
    
    progress = current / total
    filled = int(width * progress)
    bar = "█" * filled + "░" * (width - filled)
    percent = progress * 100
    
    print(f"   [{bar}] {percent:.0f}%")


# ═══════════════════════════════════════════════════════════════
# MENSAJES DE ESTADO
# ═══════════════════════════════════════════════════════════════

def info(message):
    """Mensaje informativo."""
    print(f"ℹ️  {message}")


def success(message):
    """Mensaje de éxito."""
    print(f"✅ {message}")


def warning(message):
    """Mensaje de advertencia."""
    print(f"⚠️  {message}")


def error(message):
    """Mensaje de error."""
    print(f"❌ {message}")


def step(message):
    """Mensaje de paso."""
    print(f"📌 {message}")


# ═══════════════════════════════════════════════════════════════
# CONFIRMACIÓN DEL USUARIO
# ═══════════════════════════════════════════════════════════════

def confirm(message, default=True):
    """
    Pedir confirmación al usuario.
    
    En modo automatizado, retorna el valor por defecto.
    
    Args:
        message: Mensaje de confirmación
        default: Valor por defecto si no hay input
    
    Returns:
        bool
    """
    print(f"\n❓ {message}")
    
    # En modo automatizado, usar default
    # En modo interactivo, preguntar
    try:
        response = input(f"   (s/n) [{'S' if default else 'N'}]: ").strip().lower()
        if not response:
            return default
        return response in ('s', 'si', 'sí', 'y', 'yes')
    except (EOFError, KeyboardInterrupt):
        return default


def confirm_destructive(message):
    """
    Confirmación para operaciones destructivas (borrar, etc.).
    
    Siempre requiere confirmación explícita.
    """
    print(f"\n🚨 OPERACIÓN DESTRUCTIVA")
    print(f"   {message}")
    
    try:
        response = input("   Escriba 'CONFIRMAR' para proceder: ").strip()
        return response == "CONFIRMAR"
    except (EOFError, KeyboardInterrupt):
        return False


# ═══════════════════════════════════════════════════════════════
# RESUMEN DE TAREA
# ═══════════════════════════════════════════════════════════════

def print_task_summary(title, items, success_count=None, failed_count=None):
    """
    Imprimir resumen de una tarea.
    
    Args:
        title: Título del resumen
        items: Lista de elementos procesados
        success_count: Número de éxitos
        failed_count: Número de fallos
    """
    print("\n" + "="*60)
    print(f"📋 {title}")
    print("="*60)
    
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    
    if success_count is not None or failed_count is not None:
        print("\n📊 Estadísticas:")
        if success_count is not None:
            print(f"   ✅ Éxitos: {success_count}")
        if failed_count is not None:
            print(f"   ❌ Fallos: {failed_count}")
    
    print("="*60)


# ═══════════════════════════════════════════════════════════════
# TAREAS PENDIENTES (RESUME)
# ═══════════════════════════════════════════════════════════════

def add_pending_task(task_name, details=None):
    """Agregar una tarea pendiente."""
    _progress_state["pending_tasks"].append({
        "name": task_name,
        "details": details,
        "added_at": datetime.now().isoformat(),
    })


def complete_pending_task(task_name):
    """Marcar una tarea pendiente como completada."""
    _progress_state["pending_tasks"] = [
        t for t in _progress_state["pending_tasks"]
        if t["name"] != task_name
    ]


def get_pending_tasks():
    """Obtener tareas pendientes."""
    return _progress_state["pending_tasks"].copy()


def print_pending_tasks():
    """Imprimir tareas pendientes."""
    pending = _progress_state["pending_tasks"]
    
    if not pending:
        print("\n✅ No hay tareas pendientes")
        return
    
    print(f"\n📋 TAREAS PENDIENTES ({len(pending)}):")
    for i, task in enumerate(pending, 1):
        details = f" - {task['details']}" if task.get('details') else ""
        print(f"  {i}. {task['name']}{details}")


# ═══════════════════════════════════════════════════════════════
# HISTORIAL
# ═══════════════════════════════════════════════════════════════

def get_progress_history(limit=10):
    """Obtener historial de progreso."""
    return _progress_state["history"][-limit:]


def print_progress_history():
    """Imprimir historial de progreso."""
    history = _progress_state["history"]
    
    if not history:
        print("\n📭 Sin historial de progreso")
        return
    
    print("\n📜 HISTORIAL DE PROGRESO:")
    for entry in history[-5:]:
        print(f"  • {entry['task']} - {entry['steps']}/{entry['total']} pasos - {entry['time']:.1f}s")


# ═══════════════════════════════════════════════════════════════
# OUTPUT PARA AGENTE
# ═══════════════════════════════════════════════════════════════

def agent_message(message, level="info"):
    """
    Enviar mensaje formateado para el agente.
    
    Args:
        message: Mensaje
        level: Nivel (info, success, warning, error)
    
    Returns:
        dict con el mensaje formateado
    """
    symbols = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "progress": "🔄",
    }
    
    symbol = symbols.get(level, "ℹ️")
    formatted = f"{symbol} {message}"
    
    print(formatted)
    
    return {
        "message": message,
        "level": level,
        "formatted": formatted,
        "timestamp": datetime.now().isoformat(),
    }
