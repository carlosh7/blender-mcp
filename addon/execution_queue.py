"""
blender-mcp — Execution Queue
Cola de ejecución segura para bpy (thread-safe).

Problema: bpy NO es thread-safe. Ejecutar bpy.ops desde hilos secundarios
causa Segmentation Fault.

Solución: Usar bpy.app.timers para ejecutar código en el hilo principal.
"""

import queue
import threading
import time
import traceback
from collections.abc import Callable
from typing import Any

import bpy

# ═══════════════════════════════════════════════════════════════
# COLA DE EJECUCIÓN SEGURA
# ═══════════════════════════════════════════════════════════════


class ExecutionQueue:
    """
    Cola thread-safe para ejecutar código bpy en el hilo principal.

    Uso:
        queue = ExecutionQueue()
        queue.submit(my_function, arg1, arg2)
        result = queue.get_result(timeout=10.0)
    """

    def __init__(self):
        self._pending: queue.Queue = queue.Queue()
        self._results: dict[str, Any] = {}
        self._errors: dict[str, str] = {}
        self._lock = threading.Lock()
        self._counter = 0
        self._registered = False

    def _ensure_registered(self):
        """Registrar timer si no está registrado."""
        if not self._registered:
            bpy.app.timers.register(self._process_queue, first_interval=0.1, persistent=True)
            self._registered = True

    def _process_queue(self) -> float:
        """
        Procesar elementos pendientes en el hilo principal de Blender.
        Se ejecuta periódicamente via bpy.app.timers.
        """
        processed = 0

        while not self._pending.empty() and processed < 10:  # Max 10 por tick
            try:
                task_id, func, args, kwargs = self._pending.get_nowait()

                try:
                    result = func(*args, **kwargs)
                    with self._lock:
                        self._results[task_id] = result
                except Exception as e:
                    with self._lock:
                        self._errors[task_id] = (
                            f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                        )

                processed += 1
            except queue.Empty:
                break

        return 0.1  # Re-ejecutar en 0.1 segundos

    def submit(self, func: Callable, *args, task_id: str | None = None, **kwargs) -> str:
        """
        Enviar función a la cola de ejecución.

        Args:
            func: Función a ejecutar en el hilo principal
            *args: Argumentos posicionales
            task_id: ID personalizado (opcional)
            **kwargs: Argumentos con nombre

        Returns:
            ID de la tarea para obtener el resultado
        """
        self._ensure_registered()

        if task_id is None:
            with self._lock:
                self._counter += 1
                task_id = f"task_{self._counter}_{int(time.time())}"

        self._pending.put((task_id, func, args, kwargs))
        return task_id

    def get_result(self, task_id: str, timeout: float = 10.0) -> Any | None:
        """
        Obtener resultado de una tarea.

        Args:
            task_id: ID de la tarea
            timeout: Tiempo máximo de espera (segundos)

        Returns:
            Resultado de la función o None si no está listo
        """
        start = time.time()

        while time.time() - start < timeout:
            with self._lock:
                if task_id in self._results:
                    return self._results.pop(task_id)
                if task_id in self._errors:
                    error = self._errors.pop(task_id)
                    raise RuntimeError(f"Execution failed: {error}")
            time.sleep(0.05)

        return None

    def is_pending(self, task_id: str) -> bool:
        """Verificar si una tarea está pendiente."""
        with self._lock:
            return task_id not in self._results and task_id not in self._errors

    def clear(self):
        """Limpiar cola y resultados pendientes."""
        while not self._pending.empty():
            try:
                self._pending.get_nowait()
            except queue.Empty:
                break
        with self._lock:
            self._results.clear()
            self._errors.clear()


# ═══════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL
# ═══════════════════════════════════════════════════════════════

execution_queue = ExecutionQueue()


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE CONVENIENCIA
# ═══════════════════════════════════════════════════════════════


def safe_bpy_execute(func: Callable, *args, **kwargs) -> Any | None:
    """
    Ejecutar función bpy de forma segura en el hilo principal.

    Args:
        func: Función que usa bpy
        *args: Argumentos
        **kwargs: Argumentos con nombre

    Returns:
        Resultado de la función
    """
    task_id = execution_queue.submit(func, *args, **kwargs)
    return execution_queue.get_result(task_id, timeout=30.0)


def safe_bpy_call(operator_call: Callable, *args, **kwargs) -> dict[str, Any]:
    """
    Llamar a un operador bpy de forma segura.

    Args:
        operator_call: Función del operador (ej: bpy.ops.mesh.primitive_cube_add)
        *args: Argumentos
        **kwargs: Argumentos con nombre

    Returns:
        dict con {success, result, error}
    """

    def _wrapper():
        try:
            result = operator_call(*args, **kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    task_id = execution_queue.submit(_wrapper)
    return execution_queue.get_result(task_id, timeout=30.0)


# ═══════════════════════════════════════════════════════════════
# DECORADOR
# ═══════════════════════════════════════════════════════════════


def main_thread_only(func: Callable) -> Callable:
    """
    Decorador para asegurar que una función se ejecute en el hilo principal.

    Uso:
        @main_thread_only
        def my_blender_function():
            bpy.ops.mesh.primitive_cube_add()
    """

    def wrapper(*args, **kwargs):
        return safe_bpy_execute(func, *args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
