#!/usr/bin/env python3
"""
blender-mcp-ultra — Security Tests
Run this script to verify all security modules work correctly.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ast_validator():
    """Test AST Validator."""
    print("Testing AST Validator...")
    from infrastructure.security.ast_validator import ASTValidator, SecurityError
    
    validator = ASTValidator()
    
    # Test safe code
    result = validator.validate("x = 1 + 2")
    assert result.is_safe, f"Safe code failed: {result.errors}"
    print("  ✓ Safe code passed")
    
    # Test blocked import
    result = validator.validate("import os")
    assert not result.is_safe, "Dangerous import should be blocked"
    assert any('os' in e for e in result.errors)
    print("  ✓ Blocked import os")
    
    # Test blocked exec
    result = validator.validate("exec('print(1)')")
    assert not result.is_safe, "exec() should be blocked"
    print("  ✓ Blocked exec()")
    
    # Test blocked open
    result = validator.validate("f = open('/etc/passwd', 'r')")
    assert not result.is_safe, "open() should be blocked"
    print("  ✓ Blocked open()")
    
    # Test validate_strict raises
    try:
        validator.validate_strict("import subprocess")
        assert False, "Should have raised SecurityError"
    except SecurityError:
        print("  ✓ validate_strict raises SecurityError")
    
    print("  ✓ AST Validator tests passed\n")


def test_sandbox():
    """Test Sandbox."""
    print("Testing Sandbox...")
    from infrastructure.security.sandbox import Sandbox
    
    sandbox = Sandbox(validate_code=True)
    
    # Test safe code
    result = sandbox.execute("x = 1 + 2")
    assert result.success, f"Safe code failed: {result.error}"
    print("  ✓ Safe code execution")
    
    # Test output capture
    result = sandbox.execute("print('hello')")
    assert result.success, f"Print failed: {result.error}"
    assert 'hello' in result.output
    print("  ✓ Output capture")
    
    # Test blocked code
    result = sandbox.execute("import os")
    assert not result.success, "Dangerous code should be blocked"
    print("  ✓ Blocked dangerous code")
    
    print("  ✓ Sandbox tests passed\n")


def test_url_validator():
    """Test URL Validator."""
    print("Testing URL Validator...")
    from infrastructure.security.url_validator import URLValidator, URLError
    
    validator = URLValidator()
    
    # Test safe URL
    result = validator.validate("https://polyhaven.com/textures")
    assert result.is_safe, f"Safe URL failed: {result.errors}"
    print("  ✓ Safe URL")
    
    # Test blocked file URL
    result = validator.validate("file:///etc/passwd")
    assert not result.is_safe, "file:// URL should be blocked"
    print("  ✓ Blocked file:// URL")
    
    # Test blocked unknown domain
    result = validator.validate("https://evil.com/steal")
    assert not result.is_safe, "Unknown domain should be blocked"
    print("  ✓ Blocked unknown domain")
    
    # Test validate_strict raises
    try:
        validator.validate_strict("file:///etc/passwd")
        assert False, "Should have raised URLError"
    except URLError:
        print("  ✓ validate_strict raises URLError")
    
    print("  ✓ URL Validator tests passed\n")


def test_rate_limiter():
    """Test Rate Limiter."""
    print("Testing Rate Limiter...")
    from infrastructure.security.rate_limiter import RateLimiter
    
    limiter = RateLimiter()
    
    # Test allows requests under limit
    assert limiter.check("user1") is True
    print("  ✓ Allows requests under limit")
    
    # Test blocks requests over limit
    for _ in range(10):
        limiter.check("user1")
    assert limiter.check("user1") is False
    print("  ✓ Blocks requests over limit")
    
    print("  ✓ Rate Limiter tests passed\n")


def test_input_validator():
    """Test Input Validator."""
    print("Testing Input Validator...")
    from infrastructure.security.input_validator import InputValidator, InputValidationError
    
    validator = InputValidator()
    
    # Test safe string
    result = validator.validate_string("hello world")
    assert result == "hello world"
    print("  ✓ Safe string")
    
    # Test SQL injection blocked
    try:
        validator.validate_string("'; DROP TABLE users; --")
        assert False, "SQL injection should be blocked"
    except InputValidationError:
        print("  ✓ Blocked SQL injection")
    
    # Test filename validation
    result = validator.validate_filename("test.png")
    assert result == "test.png"
    print("  ✓ Valid filename")
    
    # Test filename path removal
    result = validator.validate_filename("/etc/passwd")
    assert result == "passwd"
    print("  ✓ Removed path from filename")
    
    print("  ✓ Input Validator tests passed\n")


def main():
    """Run all security tests."""
    print("=" * 60)
    print("blender-mcp-ultra — Security Tests")
    print("=" * 60 + "\n")
    
    try:
        test_ast_validator()
        test_sandbox()
        test_url_validator()
        test_rate_limiter()
        test_input_validator()
        
        print("=" * 60)
        print("✓ ALL SECURITY TESTS PASSED")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
