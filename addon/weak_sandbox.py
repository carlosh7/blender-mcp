"""
blender-mcp — Weak sandbox for LLM-generated code execution.
Blocks dangerous operations that could crash Blender or corrupt the scene.
"""
import sys
from typing import Any

__all__ = ("WeakSandboxForLLM",)


def _blocked_exit(*args, **kwargs):
    raise RuntimeError("sys.exit() is not allowed in LLM-generated code")


_OVERRIDES = (
    (sys, "exit", _blocked_exit),
)

_BLOCKED_OPS = (
    ("wm.quit_blender", "Terminates Blender, use bpy.app.quit() if you must"),
    ("wm.read_factory_settings", "Resets all preferences and startup file"),
    ("wm.read_factory_userpref", "Resets all user preferences"),
    ("wm.read_userpref", "May disable this add-on, avoid calling"),
)

_BLOCKED_OPS_SET = frozenset(op for op, _reason in _BLOCKED_OPS)


class WeakSandboxForLLM:
    __slots__ = ("_store_attrs", "_store_ops")

    @staticmethod
    def override_store():
        saved = []
        for obj, attr, replacement in _OVERRIDES:
            saved.append((obj, attr, getattr(obj, attr)))
            setattr(obj, attr, replacement)
        return saved

    @staticmethod
    def override_restore(saved):
        for obj, attr, original in saved:
            setattr(obj, attr, original)

    @staticmethod
    def ops_blocked_store():
        import bpy.ops as _bpy_ops
        original = _bpy_ops._op_create_function

        def _filtered_op_create_function(module, func):
            key = f"{module}.{func}"
            if key in _BLOCKED_OPS_SET:
                reason = next(r for op, r in _BLOCKED_OPS if op == key)
                def _blocked(*args, **kwargs):
                    args_str = ", ".join(
                        [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
                    )
                    raise RuntimeError(
                        f"Operator 'bpy.ops.{key}({args_str})' is blocked in LLM code: {reason}"
                    )
                return _blocked
            return original(module, func)

        _bpy_ops._op_create_function = _filtered_op_create_function
        return (_bpy_ops, original)

    @staticmethod
    def ops_blocked_restore(saved):
        bpy_ops_module, original = saved
        bpy_ops_module._op_create_function = original

    def __enter__(self):
        self._store_attrs = self.override_store()
        self._store_ops = self.ops_blocked_store()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del exc_type, exc_val, exc_tb
        self.ops_blocked_restore(self._store_ops)
        self.override_restore(self._store_attrs)
