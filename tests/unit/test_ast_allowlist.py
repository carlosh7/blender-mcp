"""
blender-mcp-ultra — Tests for AST Validator (Allowlist)
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestASTValidatorAllowlist:
    """Tests for Allowlist-based AST Validator."""
    
    def test_import(self):
        """Validator should be importable."""
        from infrastructure.security.ast_validator import ASTValidator
        assert ASTValidator is not None
    
    def test_safe_code(self):
        """Safe code should pass validation."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("x = 1 + 2")
        assert result.is_safe is True
    
    def test_allowed_import_bpy(self):
        """bpy import should be allowed."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("import bpy")
        assert result.is_safe is True
    
    def test_allowed_import_math(self):
        """math import should be allowed."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("import math")
        assert result.is_safe is True
    
    def test_allowed_import_json(self):
        """json import should be allowed."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("import json")
        assert result.is_safe is True
    
    def test_blocked_import_os(self):
        """os import should be blocked."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("import os")
        assert result.is_safe is False
        assert any('os' in e for e in result.errors)
    
    def test_blocked_import_subprocess(self):
        """subprocess import should be blocked."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("import subprocess")
        assert result.is_safe is False
    
    def test_blocked_exec(self):
        """exec() should be blocked."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("exec('print(1)')")
        assert result.is_safe is False
    
    def test_blocked_eval(self):
        """eval() should be blocked."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("eval('1+1')")
        assert result.is_safe is False
    
    def test_blocked_open(self):
        """open() should be blocked."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("f = open('/etc/passwd', 'r')")
        assert result.is_safe is False
    
    def test_custom_blocked(self):
        """Custom blocked names should be blocked."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist", custom_blocked={'dangerous_func'})
        result = v.validate("dangerous_func()")
        assert result.is_safe is False
    
    def test_validate_strict_raises(self):
        """validate_strict should raise SecurityError."""
        from infrastructure.security.ast_validator import ASTValidator, SecurityError
        v = ASTValidator(mode="allowlist")
        with pytest.raises(SecurityError):
            v.validate_strict("import os")
    
    def test_syntax_error(self):
        """Syntax error should fail validation."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        result = v.validate("def foo(")
        assert result.is_safe is False
    
    def test_complex_safe_code(self):
        """Complex safe code should pass."""
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(mode="allowlist")
        code = """
import bpy
import math

def create_cube():
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.location.z = 1.0
    return obj

result = create_cube()
print(result.name)
"""
        result = v.validate(code)
        assert result.is_safe is True
    
    def test_singleton(self):
        """get_validator should return singleton."""
        from infrastructure.security.ast_validator import get_validator
        v1 = get_validator()
        v2 = get_validator()
        assert v1 is v2
