"""
blender-mcp-ultra — Tests para code_guard (guardián AST del addon).

El guard debe bloquear métodos peligrosos SOLO cuando el receptor no
pertenece al namespace de bpy: bpy.data.objects.remove() es legítimo;
foo.remove() no lo es.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "addon"))

from code_guard import CodeGuardError, check_code  # noqa: E402


class TestReceiverAwareMethods:
    """Métodos peligrosos: bloqueados solo con raíz de módulo peligroso.

    Los imports peligrosos (os, shutil, pathlib...) ya están bloqueados, así
    que .remove/.unlink sobre datos de bpy —directos o vía variables locales—
    es legítimo y debe pasar.
    """

    def test_bpy_objects_remove_allowed(self):
        check_code("bpy.data.objects.remove(obj, do_unlink=True)")

    def test_bpy_data_batch_remove_allowed(self):
        check_code("bpy.data.meshes.remove(mesh)")

    def test_local_bpy_struct_remove_allowed(self):
        check_code("mat.node_tree.nodes.remove(node)")

    def test_bpy_unlink_allowed(self):
        check_code("bpy.context.collection.objects.unlink(obj)")

    def test_plain_remove_allowed(self):
        # list.remove / API interna: inocuo sin imports peligrosos
        check_code("registry.remove(item)")

    def test_os_remove_blocked(self):
        with pytest.raises(CodeGuardError):
            check_code("os.remove(path)")

    def test_shutil_rmtree_blocked(self):
        with pytest.raises(CodeGuardError):
            check_code("shutil.rmtree(path)")

    def test_pathlib_unlink_blocked(self):
        with pytest.raises(CodeGuardError):
            check_code("Path(p).unlink()")

    def test_local_kill_allowed(self):
        # sin `import subprocess` (bloqueado) un .kill() local es inocuo
        check_code("proc.kill()")


class TestBlockedCore:
    """Lo peligrosamente universal sigue bloqueado."""

    @pytest.mark.parametrize(
        "code",
        [
            "import os",
            "import subprocess",
            "import importlib",
            "exec('x=1')",
            "eval('1')",
            "open('/tmp/x', 'w')",
            "__import__('os')",
            "obj.__class__",
            "f.__globals__",
        ],
    )
    def test_blocked(self, code):
        with pytest.raises(CodeGuardError):
            check_code(code)

    def test_legit_bpy_script_passes(self):
        check_code(
            """
import bpy
import math
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.mesh.primitive_cube_add(size=2)
"""
        )
