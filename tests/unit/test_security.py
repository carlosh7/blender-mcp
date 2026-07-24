"""
blender-mcp-ultra — Security Tests
Comprehensive tests for security modules.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestASTValidator:
    """Tests for AST Validator."""
    
    def test_safe_code(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator()
        result = v.validate("x = 1 + 2")
        assert result.is_safe is True
    
    def test_blocked_import_os(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator()
        result = v.validate("import os")
        assert result.is_safe is False
        assert any('os' in e for e in result.errors)
    
    def test_blocked_import_subprocess(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator()
        result = v.validate("import subprocess")
        assert result.is_safe is False
    
    def test_blocked_exec(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator()
        result = v.validate("exec('print(1)')")
        assert result.is_safe is False
    
    def test_blocked_eval(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator()
        result = v.validate("eval('1+1')")
        assert result.is_safe is False
    
    def test_blocked_open(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator()
        result = v.validate("f = open('/etc/passwd', 'r')")
        assert result.is_safe is False
    
    def test_validate_strict_raises(self):
        from infrastructure.security.ast_validator import ASTValidator, SecurityError
        v = ASTValidator()
        with pytest.raises(SecurityError):
            v.validate_strict("import os")
    
    def test_syntax_error(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator()
        result = v.validate("def foo(")
        assert result.is_safe is False
    
    def test_complex_safe_code(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator()
        code = """
def calculate(a, b):
    return a + b

result = calculate(1, 2)
print(result)
"""
        result = v.validate(code)
        assert result.is_safe is True
    
    def test_custom_blocked_names(self):
        from infrastructure.security.ast_validator import ASTValidator
        v = ASTValidator(custom_blocked={'dangerous_func'})
        result = v.validate("dangerous_func()")
        assert result.is_safe is False


class TestSandbox:
    """Tests for Sandbox."""
    
    def test_execute_safe_code(self):
        from infrastructure.security.sandbox import Sandbox
        s = Sandbox(validate_code=True)
        result = s.execute("x = 1 + 2")
        assert result.success is True
    
    def test_execute_with_output(self):
        from infrastructure.security.sandbox import Sandbox
        s = Sandbox(validate_code=True)
        result = s.execute("print('hello')")
        assert result.success is True
        assert 'hello' in result.output
    
    def test_execute_dangerous_code_blocked(self):
        from infrastructure.security.sandbox import Sandbox
        s = Sandbox(validate_code=True)
        result = s.execute("import os")
        assert result.success is False
        assert 'Security' in result.error or 'error' in result.error.lower()
    
    def test_sandbox_stats(self):
        from infrastructure.security.sandbox import Sandbox
        s = Sandbox(validate_code=True)
        s.execute("print(1)")
        stats = s.get_stats()
        assert stats['execution_count'] == 1
    
    def test_sandbox_reset_stats(self):
        from infrastructure.security.sandbox import Sandbox
        s = Sandbox(validate_code=True)
        s.execute("print(1)")
        s.reset_stats()
        assert s.get_stats()['execution_count'] == 0


class TestURLValidator:
    """Tests for URL Validator."""
    
    def test_safe_url(self):
        from infrastructure.security.url_validator import URLValidator
        v = URLValidator()
        result = v.validate("https://polyhaven.com/textures")
        assert result.is_safe is True
    
    def test_blocked_file_url(self):
        from infrastructure.security.url_validator import URLValidator
        v = URLValidator()
        result = v.validate("file:///etc/passwd")
        assert result.is_safe is False
    
    def test_blocked_unknown_domain(self):
        from infrastructure.security.url_validator import URLValidator
        v = URLValidator()
        result = v.validate("https://evil.com/steal")
        assert result.is_safe is False
    
    def test_allowed_domain(self):
        from infrastructure.security.url_validator import URLValidator
        v = URLValidator()
        result = v.validate("https://sketchfab.com/models")
        assert result.is_safe is True
    
    def test_validate_strict_raises(self):
        from infrastructure.security.url_validator import URLValidator, URLError
        v = URLValidator()
        with pytest.raises(URLError):
            v.validate_strict("file:///etc/passwd")
    
    def test_custom_allowed_domains(self):
        from infrastructure.security.url_validator import URLValidator
        v = URLValidator(custom_allowed={'mydomain.com'})
        result = v.validate("https://mydomain.com/data")
        assert result.is_safe is True


class TestRateLimiter:
    """Tests for Rate Limiter."""
    
    def test_allows_first_request(self):
        from infrastructure.security.rate_limiter import RateLimiter
        r = RateLimiter()
        assert r.check("user1") is True
    
    def test_blocks_requests_over_limit(self):
        from infrastructure.security.rate_limiter import RateLimiter
        r = RateLimiter()
        for _ in range(10):
            r.check("user1")
        assert r.check("user1") is False
    
    def test_different_users(self):
        from infrastructure.security.rate_limiter import RateLimiter
        r = RateLimiter()
        for _ in range(10):
            r.check("user1")
        assert r.check("user2") is True
    
    def test_reset(self):
        from infrastructure.security.rate_limiter import RateLimiter
        r = RateLimiter()
        for _ in range(10):
            r.check("user1")
        r.reset("user1")
        assert r.check("user1") is True
    
    def test_stats(self):
        from infrastructure.security.rate_limiter import RateLimiter
        r = RateLimiter()
        r.check("user1")
        stats = r.get_stats()
        assert stats['total_requests'] == 1


class TestInputValidator:
    """Tests for Input Validator."""
    
    def test_safe_string(self):
        from infrastructure.security.input_validator import InputValidator
        v = InputValidator()
        result = v.validate_string("hello world")
        assert result == "hello world"
    
    def test_blocks_sql_injection(self):
        from infrastructure.security.input_validator import InputValidator, InputValidationError
        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_string("'; DROP TABLE users; --")
    
    def test_blocks_xss(self):
        from infrastructure.security.input_validator import InputValidator, InputValidationError
        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_string("<script>alert('xss')</script>")
    
    def test_validate_filename(self):
        from infrastructure.security.input_validator import InputValidator
        v = InputValidator()
        result = v.validate_filename("test.png")
        assert result == "test.png"
    
    def test_validate_filename_removes_path(self):
        from infrastructure.security.input_validator import InputValidator
        v = InputValidator()
        result = v.validate_filename("/etc/passwd")
        assert result == "passwd"
    
    def test_validate_integer(self):
        from infrastructure.security.input_validator import InputValidator
        v = InputValidator()
        result = v.validate_integer("42")
        assert result == 42
    
    def test_validate_integer_range(self):
        from infrastructure.security.input_validator import InputValidator, InputValidationError
        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_integer("100", min_value=0, max_value=10)
    
    def test_validate_enum(self):
        from infrastructure.security.input_validator import InputValidator
        v = InputValidator()
        result = v.validate_enum("red", {"red", "blue", "green"})
        assert result == "red"
    
    def test_validate_enum_invalid(self):
        from infrastructure.security.input_validator import InputValidator, InputValidationError
        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_enum("yellow", {"red", "blue", "green"})
    
    def test_validate_url(self):
        from infrastructure.security.input_validator import InputValidator
        v = InputValidator()
        result = v.validate_url("https://example.com")
        assert result == "https://example.com"
    
    def test_validate_code_safe(self):
        from infrastructure.security.input_validator import InputValidator
        v = InputValidator()
        result = v.validate_code("x = 1 + 2")
        assert result == "x = 1 + 2"
    
    def test_validate_code_dangerous(self):
        from infrastructure.security.input_validator import InputValidator, InputValidationError
        v = InputValidator()
        with pytest.raises(InputValidationError):
            v.validate_code("import os")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
