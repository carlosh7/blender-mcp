"""
blender-mcp-ultra — Tests for Security Infrastructure
"""
import pytest


class TestASTValidator:
    """Tests for AST Validator."""
    
    def test_import(self):
        from infrastructure.security.ast_validator import ASTValidator, SecurityError
        assert ASTValidator is not None
    
    def test_safe_code(self):
        from infrastructure.security.ast_validator import ASTValidator
        validator = ASTValidator()
        
        safe_code = """
x = 1
y = 2
result = x + y
print(result)
"""
        result = validator.validate(safe_code)
        assert result.is_safe is True
    
    def test_blocked_import_os(self):
        from infrastructure.security.ast_validator import ASTValidator
        validator = ASTValidator()
        
        dangerous_code = "import os"
        result = validator.validate(dangerous_code)
        assert result.is_safe is False
        assert any('os' in e for e in result.errors)
    
    def test_blocked_import_subprocess(self):
        from infrastructure.security.ast_validator import ASTValidator
        validator = ASTValidator()
        
        dangerous_code = "import subprocess"
        result = validator.validate(dangerous_code)
        assert result.is_safe is False
    
    def test_blocked_exec(self):
        from infrastructure.security.ast_validator import ASTValidator
        validator = ASTValidator()
        
        dangerous_code = "exec('print(1)')"
        result = validator.validate(dangerous_code)
        assert result.is_safe is False
    
    def test_blocked_open(self):
        from infrastructure.security.ast_validator import ASTValidator
        validator = ASTValidator()
        
        dangerous_code = "f = open('/etc/passwd', 'r')"
        result = validator.validate(dangerous_code)
        assert result.is_safe is False
    
    def test_validate_strict_raises(self):
        from infrastructure.security.ast_validator import ASTValidator, SecurityError
        validator = ASTValidator()
        
        with pytest.raises(SecurityError):
            validator.validate_strict("import os")
    
    def test_syntax_error(self):
        from infrastructure.security.ast_validator import ASTValidator
        validator = ASTValidator()
        
        result = validator.validate("def foo(")
        assert result.is_safe is False


class TestSandbox:
    """Tests for Sandbox."""
    
    def test_import(self):
        from infrastructure.security.sandbox import Sandbox, execute_code
        assert Sandbox is not None
    
    def test_execute_safe_code(self):
        from infrastructure.security.sandbox import Sandbox
        sandbox = Sandbox(validate_code=True)
        
        result = sandbox.execute("x = 1 + 2")
        assert result.success is True
    
    def test_execute_with_output(self):
        from infrastructure.security.sandbox import Sandbox
        sandbox = Sandbox(validate_code=True)
        
        result = sandbox.execute("print('hello')")
        assert result.success is True
        assert 'hello' in result.output
    
    def test_execute_dangerous_code_blocked(self):
        from infrastructure.security.sandbox import Sandbox
        sandbox = Sandbox(validate_code=True)
        
        result = sandbox.execute("import os")
        assert result.success is False
        assert 'Security' in result.error or 'Security error' in result.error


class TestURLValidator:
    """Tests for URL Validator."""
    
    def test_import(self):
        from infrastructure.security.url_validator import URLValidator, validate_url
        assert URLValidator is not None
    
    def test_safe_url(self):
        from infrastructure.security.url_validator import URLValidator
        validator = URLValidator()
        
        result = validator.validate("https://polyhaven.com/textures")
        assert result.is_safe is True
    
    def test_blocked_file_url(self):
        from infrastructure.security.url_validator import URLValidator
        validator = URLValidator()
        
        result = validator.validate("file:///etc/passwd")
        assert result.is_safe is False
    
    def test_blocked_unknown_domain(self):
        from infrastructure.security.url_validator import URLValidator
        validator = URLValidator()
        
        result = validator.validate("https://evil.com/steal")
        assert result.is_safe is False
    
    def test_validate_strict_raises(self):
        from infrastructure.security.url_validator import URLValidator, URLError
        validator = URLValidator()
        
        with pytest.raises(URLError):
            validator.validate_strict("file:///etc/passwd")


class TestRateLimiter:
    """Tests for Rate Limiter."""
    
    def test_import(self):
        from infrastructure.security.rate_limiter import RateLimiter, check_rate_limit
        assert RateLimiter is not None
    
    def test_allows_requests_under_limit(self):
        from infrastructure.security.rate_limiter import RateLimiter
        limiter = RateLimiter()
        
        # Should allow first request
        assert limiter.check("user1") is True
    
    def test_blocks_requests_over_limit(self):
        from infrastructure.security.rate_limiter import RateLimiter
        limiter = RateLimiter()
        
        # Exhaust tokens
        for _ in range(10):
            limiter.check("user1")
        
        # Next request should be blocked
        assert limiter.check("user1") is False


class TestInputValidator:
    """Tests for Input Validator."""
    
    def test_import(self):
        from infrastructure.security.input_validator import InputValidator, validate_string
        assert InputValidator is not None
    
    def test_safe_string(self):
        from infrastructure.security.input_validator import InputValidator
        validator = InputValidator()
        
        result = validator.validate_string("hello world")
        assert result == "hello world"
    
    def test_blocks_sql_injection(self):
        from infrastructure.security.input_validator import InputValidator, InputValidationError
        validator = InputValidator()
        
        with pytest.raises(InputValidationError):
            validator.validate_string("'; DROP TABLE users; --")
    
    def test_validate_filename(self):
        from infrastructure.security.input_validator import InputValidator
        validator = InputValidator()
        
        result = validator.validate_filename("test.png")
        assert result == "test.png"
    
    def test_validate_filename_removes_path(self):
        from infrastructure.security.input_validator import InputValidator
        validator = InputValidator()
        
        result = validator.validate_filename("/etc/passwd")
        assert result == "passwd"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
