"""
blender-mcp-ultra — Input Validator
Validates and sanitizes user inputs to prevent injection attacks.
"""
import os
import re
import html
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass


class InputValidationError(Exception):
    """Raised when input validation fails."""
    pass


@dataclass
class ValidationRule:
    """Validation rule for input fields."""
    name: str
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_chars: Optional[str] = None
    blocked_chars: Optional[str] = None
    custom_validator: Optional[callable] = None


class InputValidator:
    """
    Validates and sanitizes user inputs.
    
    Features:
    - Pattern matching
    - Length validation
    - Character whitelisting/blacklisting
    - SQL injection prevention
    - XSS prevention
    - Path traversal prevention
    """
    
    # Common injection patterns
    INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|alter|create|exec|execute)\b)",
        r"(--|;|'|\")",
        r"(\b(or|and)\b\s+\d+\s*=\s*\d+)",
        r"(\/\*|\*\/)",
        r"(\bexec\b\s*\()",
        r"(\beval\b\s*\()",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\.',
        r'\\',
    ]
    
    # Allowed path prefixes (these directories are safe)
    ALLOWED_PATH_PREFIXES = [
        '/tmp/',
        '/home/',
        os.path.expanduser('~'),
    ]
    
    # Dangerous characters
    DANGEROUS_CHARS = set('<>{}[]|\\^~[]`')
    
    def __init__(self):
        """Initialize input validator."""
        self.injection_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS
        ]
        self.path_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS
        ]
    
    def validate_string(
        self,
        value: str,
        field_name: str = "input",
        rules: Optional[List[ValidationRule]] = None
    ) -> str:
        """
        Validate and sanitize string input.
        
        Args:
            value: Input string to validate
            field_name: Name of field for error messages
            rules: Additional validation rules
            
        Returns:
            Sanitized string
            
        Raises:
            InputValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise InputValidationError(
                f"{field_name}: Expected string, got {type(value).__name__}"
            )
        
        # Basic sanitization
        sanitized = self._sanitize_string(value)
        
        # Check for injection attempts
        self._check_injection(sanitized, field_name)
        
        # Check for path traversal
        self._check_path_traversal(sanitized, field_name)
        
        # Apply custom rules
        if rules:
            for rule in rules:
                self._apply_rule(sanitized, field_name, rule)
        
        return sanitized
    
    def validate_filename(
        self,
        filename: str,
        field_name: str = "filename"
    ) -> str:
        """
        Validate filename.
        
        Args:
            filename: Filename to validate
            field_name: Field name for errors
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Check length
        if len(filename) > 255:
            raise InputValidationError(
                f"{field_name}: Filename too long (max 255 chars)"
            )
        
        # Check for reserved names (Windows)
        reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3',
                    'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6',
                    'LPT7', 'LPT8', 'LPT9'}
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved:
            raise InputValidationError(
                f"{field_name}: Reserved filename: {filename}"
            )
        
        return filename
    
    def validate_url(
        self,
        url: str,
        field_name: str = "url"
    ) -> str:
        """
        Validate URL.
        
        Args:
            url: URL to validate
            field_name: Field name for errors
            
        Returns:
            Sanitized URL
        """
        # Basic URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            raise InputValidationError(
                f"{field_name}: Invalid URL format"
            )
        
        return url
    
    def validate_code(
        self,
        code: str,
        field_name: str = "code"
    ) -> str:
        """
        Validate code input.
        
        Args:
            code: Code to validate
            field_name: Field name for errors
            
        Returns:
            Sanitized code
        """
        # Check for common injection patterns
        dangerous_patterns = [
            (r'__import__', "Dynamic imports not allowed"),
            (r'exec\s*\(', "exec() not allowed"),
            (r'eval\s*\(', "eval() not allowed"),
            (r'compile\s*\(', "compile() not allowed"),
            (r'open\s*\(', "Direct file access not allowed"),
            (r'import\s+os', "os module not allowed"),
            (r'import\s+sys', "sys module not allowed"),
            (r'import\s+subprocess', "subprocess not allowed"),
            (r'os\.', "os module not allowed"),
            (r'sys\.', "sys module not allowed"),
            (r'subprocess\.', "subprocess not allowed"),
        ]
        
        for pattern, message in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise InputValidationError(
                    f"{field_name}: {message}"
                )
        
        return code
    
    def validate_integer(
        self,
        value: Any,
        field_name: str = "input",
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> int:
        """
        Validate integer input.
        
        Args:
            value: Value to validate
            field_name: Field name for errors
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated integer
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise InputValidationError(
                f"{field_name}: Expected integer, got {type(value).__name__}"
            )
        
        if min_value is not None and int_value < min_value:
            raise InputValidationError(
                f"{field_name}: Value {int_value} below minimum {min_value}"
            )
        
        if max_value is not None and int_value > max_value:
            raise InputValidationError(
                f"{field_name}: Value {int_value} above maximum {max_value}"
            )
        
        return int_value
    
    def validate_float(
        self,
        value: Any,
        field_name: str = "input",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> float:
        """
        Validate float input.
        
        Args:
            value: Value to validate
            field_name: Field name for errors
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated float
        """
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise InputValidationError(
                f"{field_name}: Expected float, got {type(value).__name__}"
            )
        
        if min_value is not None and float_value < min_value:
            raise InputValidationError(
                f"{field_name}: Value {float_value} below minimum {min_value}"
            )
        
        if max_value is not None and float_value > max_value:
            raise InputValidationError(
                f"{field_name}: Value {float_value} above maximum {max_value}"
            )
        
        return float_value
    
    def validate_enum(
        self,
        value: Any,
        allowed_values: Set[Any],
        field_name: str = "input"
    ) -> Any:
        """
        Validate enum input.
        
        Args:
            value: Value to validate
            allowed_values: Set of allowed values
            field_name: Field name for errors
            
        Returns:
            Validated value
        """
        if value not in allowed_values:
            raise InputValidationError(
                f"{field_name}: Value '{value}' not in allowed values: {allowed_values}"
            )
        return value
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string value."""
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Escape HTML entities
        value = html.escape(value)
        
        # Remove control characters (except newline and tab)
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        return value.strip()
    
    def _check_injection(self, value: str, field_name: str) -> None:
        """Check for SQL/command injection attempts."""
        for pattern in self.injection_patterns:
            if pattern.search(value):
                raise InputValidationError(
                    f"{field_name}: Potential injection attempt detected"
                )
    
    def _check_path_traversal(self, value: str, field_name: str) -> None:
        """Check for path traversal attempts."""
        # Allow paths that start with known safe prefixes
        for prefix in self.ALLOWED_PATH_PREFIXES:
            if value.startswith(prefix):
                return
        for pattern in self.path_patterns:
            if pattern.search(value):
                raise InputValidationError(
                    f"{field_name}: Potential path traversal detected"
                )
    
    def _apply_rule(self, value: str, field_name: str, rule: ValidationRule) -> None:
        """Apply validation rule."""
        if rule.pattern and not re.match(rule.pattern, value):
            raise InputValidationError(
                f"{field_name}: {rule.name} validation failed"
            )
        
        if rule.min_length and len(value) < rule.min_length:
            raise InputValidationError(
                f"{field_name}: Minimum length {rule.min_length} not met"
            )
        
        if rule.max_length and len(value) > rule.max_length:
            raise InputValidationError(
                f"{field_name}: Maximum length {rule.max_length} exceeded"
            )
        
        if rule.blocked_chars:
            for char in rule.blocked_chars:
                if char in value:
                    raise InputValidationError(
                        f"{field_name}: Blocked character '{char}' found"
                    )
        
        if rule.custom_validator and not rule.custom_validator(value):
            raise InputValidationError(
                f"{field_name}: Custom validation failed"
            )


# Singleton instance
_validator = None

def get_validator() -> InputValidator:
    """Get singleton validator instance."""
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator

def validate_string(value: str, **kwargs) -> str:
    """Convenience function to validate string."""
    return get_validator().validate_string(value, **kwargs)

def validate_filename(filename: str, **kwargs) -> str:
    """Convenience function to validate filename."""
    return get_validator().validate_filename(filename, **kwargs)

def validate_url(url: str, **kwargs) -> str:
    """Convenience function to validate URL."""
    return get_validator().validate_url(url, **kwargs)
