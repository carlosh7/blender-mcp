"""
blender-mcp — Deferred response handling for Blender background jobs.
When tool-code starts a background job (e.g. rendering with INVOKE_DEFAULT),
the response cannot be sent immediately. This module polls a checker
callable until the operation completes.
"""
import time
import traceback
from collections.abc import Callable

_DEFERRED_TIMEOUT = 60.0 * 60.0  # 1 hour
_POLL_INTERVAL = 1.0  # seconds between polls


class _DeferredJob:
    __slots__ = ("check_fn", "deadline", "result")
    def __init__(self, check_fn: Callable[[], dict | None]) -> None:
        self.check_fn = check_fn
        self.deadline = time.monotonic() + _DEFERRED_TIMEOUT
        self.result = None


_deferred_jobs: list[_DeferredJob] = []


def add(check_fn: Callable[[], dict | None]) -> None:
    _deferred_jobs.append(_DeferredJob(check_fn))


def poll() -> list[dict]:
    results = []
    for job in _deferred_jobs[:]:
        if time.monotonic() > job.deadline:
            results.append({"status": "error", "message": "Deferred operation timed out"})
            _deferred_jobs.remove(job)
            continue
        try:
            r = job.check_fn()
        except Exception as e:
            results.append({"status": "error", "message": traceback.format_exc()})
            _deferred_jobs.remove(job)
            continue
        if r is not None:
            results.append({"status": "ok", "result": r})
            _deferred_jobs.remove(job)
    return results


def has_pending() -> bool:
    return bool(_deferred_jobs)


def close_all() -> None:
    _deferred_jobs.clear()
