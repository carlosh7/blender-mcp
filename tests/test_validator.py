"""
blender-mcp — AST Validator Tests
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestASTValidator:
    def setup_method(self):
        from blender_mcp.utils.validator import validate
        self.validate = validate

    def test_safe_code(self):
        errors = self.validate("import bpy; bpy.ops.mesh.primitive_cube_add()")
        assert len(errors) == 0

    def test_blocked_os(self):
        errors = self.validate("import os; os.listdir('/')")
        assert len(errors) > 0
        assert "os" in str(errors[0])

    def test_blocked_subprocess(self):
        errors = self.validate("import subprocess; subprocess.run(['ls'])")
        assert len(errors) > 0
        assert "subprocess" in str(errors[0])

    def test_blocked_importlib(self):
        errors = self.validate("import importlib; importlib.import_module('os')")
        assert len(errors) > 0
        assert "importlib" in str(errors[0])

    def test_blocked_pickle(self):
        errors = self.validate("import pickle; pickle.loads(b'')")
        assert len(errors) > 0
        assert "pickle" in str(errors[0])

    def test_blocked_marshal(self):
        errors = self.validate("import marshal")
        assert len(errors) > 0
        assert "marshal" in str(errors[0])

    def test_blocked_builtins(self):
        errors = self.validate("import builtins")
        assert len(errors) > 0
        assert "builtins" in str(errors[0])

    def test_blocked_exec(self):
        errors = self.validate("exec('print(1)')")
        assert len(errors) > 0
        assert "exec" in str(errors[0])

    def test_blocked_eval(self):
        errors = self.validate("eval('1+1')")
        assert len(errors) > 0
        assert "eval" in str(errors[0])

    def test_syntax_error(self):
        errors = self.validate("bpy.ops.mesh.cube_add(")
        assert len(errors) > 0
        assert "SyntaxError" in str(errors[0])
