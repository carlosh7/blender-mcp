"""
socket_events.py — Bus de eventos (ring buffer) para polling de agentes.
Emitido desde el hilo de red y desde timers del hilo principal: las
estructuras usadas (deque.append, int +=) son atómicas bajo el GIL.
"""

import collections
import time

_EVENT_BUFFER: collections.deque = collections.deque(maxlen=500)
_EVENT_SEQ = 0


def emit_event(kind: str, data=None) -> int:
    """Publicar un evento en el bus (poll con cmd_poll_events)."""
    global _EVENT_SEQ
    _EVENT_SEQ += 1
    _EVENT_BUFFER.append(
        {"seq": _EVENT_SEQ, "time": round(time.time(), 3), "kind": kind, "data": data or {}}
    )
    return _EVENT_SEQ


def poll_events(since: int = 0, limit: int = 100) -> dict:
    """Eventos con seq > since, hasta limit."""
    events = [e for e in _EVENT_BUFFER if e["seq"] > since]
    return {"events": events[:limit], "last_seq": _EVENT_SEQ, "count": len(events)}
