"""
transaction.py — Ejecución por lotes con rollback atómico.

El flujo real de un agente son varias operaciones encadenadas (crear, mover,
anclar, materializar). Con las tools sueltas, un gagal en el paso 4 deja la
escena a medias y sin forma limpia de volver atrás: el agente tiene que
adivinar qué revertir.

Aquí se agrupan N operaciones bajo un único `undo_push`. Si alguna falla y el
modo es atómico, se deshace el lote completo y la escena queda exactamente como
estaba. El resultado detalla paso a paso qué ocurrió.
"""
import time

import bpy


class StepError(Exception):
    """Fallo de un paso concreto del lote."""

    def __init__(self, index, op, message):
        self.index = index
        self.op = op
        self.message = message
        super().__init__(f"paso {index} ({op}): {message}")


def _run_step(server, index, step):
    """Ejecuta un paso y normaliza su resultado.

    Un paso es {"op": <nombre>, "params": {...}} donde <nombre> es un comando
    del socket (get_scene_info, snap_and_parent, ...) o una tool del registry
    (object.create, material.assign, ...).
    """
    op = step.get("op") or step.get("command") or step.get("tool")
    if not op:
        raise StepError(index, "?", "falta 'op'")
    params = step.get("params") or step.get("args") or {}
    if not isinstance(params, dict):
        raise StepError(index, op, "'params' debe ser un objeto")

    # 1) Comando nativo del socket.
    handler = getattr(server, f"cmd_{op}", None)
    if handler is not None:
        try:
            result = handler(**params)
        except Exception as exc:
            raise StepError(index, op, str(exc)) from exc
        if isinstance(result, dict) and result.get("error"):
            raise StepError(index, op, str(result["error"]))
        return result

    # 2) Tool del registry (object.create, geonodes.*, ...).
    if "." in op:
        from . import registry_bridge

        result = registry_bridge.call_tool(op, params)
        if not result.get("success"):
            raise StepError(index, op, str(result.get("error")))
        return result.get("data")

    raise StepError(index, op, "operación desconocida")


def _snapshot():
    """Estado restaurable de la escena: qué objetos hay y dónde están.

    Cubre lo que hacen estas operaciones: crear, borrar, mover, rotar,
    escalar y reemparentar.
    """
    return {
        obj.name: (
            obj.matrix_world.copy(),
            obj.parent.name if obj.parent else None,
        )
        for obj in bpy.context.scene.objects
    }


def _restore(snap):
    """Devuelve la escena al estado de `snap`.

    `bpy.ops.ed.undo()` es la vía natural, pero su poll() falla cuando no hay
    ventana (Blender en background, o llamadas desde un timer), y entonces no
    revierte nada sin avisar. Se intenta primero y se COMPRUEBA el resultado;
    si no ha surtido efecto, se restaura a mano.
    """
    try:
        bpy.ops.ed.undo()
    except Exception:
        pass

    current = {o.name for o in bpy.context.scene.objects}
    if current == set(snap):
        # El undo nativo ya dejó el censo correcto; sólo quedan transformaciones.
        for name, (matrix, parent) in snap.items():
            obj = bpy.data.objects.get(name)
            if obj is not None:
                obj.matrix_world = matrix
        bpy.context.view_layer.update()
        return True

    # Fallback: borrar lo creado y devolver lo movido a su sitio.
    for name in current - set(snap):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)

    for name, (matrix, parent) in snap.items():
        obj = bpy.data.objects.get(name)
        if obj is None:
            # Objeto borrado durante el lote: no se puede recomponer su
            # malla, así que el lote no es reversible por esta vía.
            return False
        obj.parent = bpy.data.objects.get(parent) if parent else None
        obj.matrix_world = matrix

    bpy.context.view_layer.update()
    return {o.name for o in bpy.context.scene.objects} == set(snap)


def run_batch(steps, atomic=True, label="Axiom Batch"):
    """Ejecuta `steps` en orden bajo una única transacción de undo.

    atomic=True  → un gagal revierte TODO el lote (all-or-nothing).
    atomic=False → los pasos correctos se conservan y se reporta el gagal.
    """
    if not isinstance(steps, list) or not steps:
        return {"success": False, "error": "se esperaba una lista de pasos no vacía"}

    # Punto de restauración: undo nativo + censo verificable de la escena.
    bpy.ops.ed.undo_push(message=label)
    snap = _snapshot()

    started = time.time()
    done = []

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            failure = StepError(index, "?", "cada paso debe ser un objeto")
        else:
            failure = None
            try:
                data = _run_step(_server(), index, step)
            except StepError as exc:
                failure = exc
            else:
                done.append({"index": index, "op": step.get("op"), "data": data})
                continue

        # A partir de aquí el paso ha fallado.
        rolled_back = False
        if atomic:
            try:
                rolled_back = bool(_restore(snap))
            except Exception:
                # Un rollback fallido no debe ocultar el error original.
                rolled_back = False

        return {
            "success": False,
            "error": str(failure),
            "failed_step": failure.index,
            "op": failure.op,
            "completed": done,
            "rolled_back": rolled_back,
            "atomic": atomic,
            "elapsed": round(time.time() - started, 4),
        }

    return {
        "success": True,
        "steps": len(done),
        "completed": done,
        "atomic": atomic,
        "elapsed": round(time.time() - started, 4),
    }


def _server():
    from . import _axsock

    return _axsock.get_socket_server()
