"""
blender-mcp-ultra — Security Tests
InputValidator: la única pieza de infrastructure/security cableada en runtime.
"""

import pytest


class TestInputValidator:
    """Tests for Input Validator."""

    def test_safe_string(self):
        from mcp_ultra.infrastructure.security.input_validator import InputValidator

        v = InputValidator()
        result = v.validate_string("hello world")
        assert result == "hello world"

    def test_blocks_sql_injection(self):
        from mcp_ultra.infrastructure.security.input_validator import (
            InputValidationError,
            InputValidator,
        )

        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_string("'; DROP TABLE users; --")

    def test_blocks_xss(self):
        from mcp_ultra.infrastructure.security.input_validator import (
            InputValidationError,
            InputValidator,
        )

        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_string("<script>alert('xss')</script>")

    def test_validate_filename(self):
        from mcp_ultra.infrastructure.security.input_validator import InputValidator

        v = InputValidator()
        result = v.validate_filename("test.png")
        assert result == "test.png"

    def test_validate_filename_removes_path(self):
        from mcp_ultra.infrastructure.security.input_validator import InputValidator

        v = InputValidator()
        result = v.validate_filename("/etc/passwd")
        assert result == "passwd"

    def test_validate_integer(self):
        from mcp_ultra.infrastructure.security.input_validator import InputValidator

        v = InputValidator()
        result = v.validate_integer("42")
        assert result == 42

    def test_validate_integer_range(self):
        from mcp_ultra.infrastructure.security.input_validator import (
            InputValidationError,
            InputValidator,
        )

        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_integer("100", min_value=0, max_value=10)

    def test_validate_enum(self):
        from mcp_ultra.infrastructure.security.input_validator import InputValidator

        v = InputValidator()
        result = v.validate_enum("red", {"red", "blue", "green"})
        assert result == "red"

    def test_validate_enum_invalid(self):
        from mcp_ultra.infrastructure.security.input_validator import (
            InputValidationError,
            InputValidator,
        )

        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_enum("yellow", {"red", "blue", "green"})

    def test_validate_url(self):
        from mcp_ultra.infrastructure.security.input_validator import InputValidator

        v = InputValidator()
        result = v.validate_url("https://example.com")
        assert result == "https://example.com"

    def test_validate_code_safe(self):
        from mcp_ultra.infrastructure.security.input_validator import InputValidator

        v = InputValidator()
        result = v.validate_code("x = 1 + 2")
        assert result == "x = 1 + 2"

    def test_validate_code_dangerous(self):
        from mcp_ultra.infrastructure.security.input_validator import (
            InputValidationError,
            InputValidator,
        )

        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_code("import os")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
