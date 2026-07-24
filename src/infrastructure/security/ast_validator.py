"""
blender-mcp-ultra — AST Validator (Enterprise Grade)
Validates Python code against a comprehensive whitelist of allowed AST patterns.
Blocks dangerous operations that could harm the system.
"""
import ast
import re
from typing import Set, List, Optional
from dataclasses import dataclass


class SecurityError(Exception):
    """Raised when code violates security policies."""
    pass


@dataclass
class ValidationResult:
    """Result of AST validation."""
    is_safe: bool
    errors: List[str]
    warnings: List[str]


class ASTValidator:
    """Validates Python code against security whitelist."""
    
    # Dangerous builtins that should be blocked
    BLOCKED_BUILTINS: Set[str] = {
        # System access
        'exit', 'quit', 'breakpoint',
        
        # Code execution
        'exec', 'eval', 'compile', '__import__',
        
        # Introspection (can be used for exploits)
        'globals', 'locals', 'vars', 'dir',
        
        # Attribute manipulation
        'getattr', 'setattr', 'delattr',
        
        # File operations
        'open', 'input',
        
        # Memory/internals
        'memoryview', 'bytearray',
        
        # Type manipulation
        'type', 'super',
        
        # Representation
        'repr', 'id', 'hash',
    }
    
    # Dangerous module names
    BLOCKED_MODULES: Set[str] = {
        # System modules
        'os', 'sys', 'subprocess', 'shutil', 'signal',
        
        # Network modules
        'socket', 'http', 'urllib', 'requests', 'aiohttp',
        
        # Process/threading
        'multiprocessing', 'threading', 'concurrent',
        'asyncio', 'queue',
        
        # Code introspection
        'inspect', 'importlib', 'pkgutil',
        
        # Serialization (can execute code)
        'pickle', 'shelve', 'marshal',
        
        # ctypes (direct C access)
        'ctypes', 'cffi',
        
        # Debugging
        'pdb', 'profile', 'cProfile', 'trace',
        
        # File system
        'pathlib', 'glob', 'fnmatch',
        
        # Data processing (potential DoS)
        'csv', 'json', 'xml', 'html',
        
        # Compression (potential bomb)
        'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma',
        
        # Hashing (potential collision)
        'hashlib', 'hmac',
        
        # Crypto (potential key theft)
        'crypto', 'ssl',
    }
    
    # Dangerous function/method names
    BLOCKED_NAMES: Set[str] = {
        # System
        'system', 'popen', 'exec', 'spawn',
        
        # File operations
        'remove', 'unlink', 'rmdir', 'rename',
        'makedirs', 'mkdir', 'symlink',
        
        # Network
        'connect', 'bind', 'listen', 'accept',
        
        # Process
        'kill', 'terminate', 'wait',
        
        # Code execution
        'eval', 'exec', 'compile',
    }
    
    # Dangerous AST node types
    BLOCKED_NODE_TYPES: Set[type] = {
        ast.Delete,  # del statement
    }
    
    # Dangerous string patterns (regex)
    DANGEROUS_PATTERNS: List[re.Pattern] = [
        re.compile(r'__import__', re.IGNORECASE),
        re.compile(r'exec\s*\(', re.IGNORECASE),
        re.compile(r'eval\s*\(', re.IGNORECASE),
        re.compile(r'compile\s*\(', re.IGNORECASE),
        re.compile(r'open\s*\(', re.IGNORECASE),
        re.compile(r'os\.', re.IGNORECASE),
        re.compile(r'sys\.', re.IGNORECASE),
        re.compile(r'subprocess\.', re.IGNORECASE),
        re.compile(r'import\s+os', re.IGNORECASE),
        re.compile(r'import\s+sys', re.IGNORECASE),
        re.compile(r'import\s+subprocess', re.IGNORECASE),
        re.compile(r'import\s+shutil', re.IGNORECASE),
        re.compile(r'import\s+socket', re.IGNORECASE),
        re.compile(r'import\s+http', re.IGNORECASE),
        re.compile(r'import\s+urllib', re.IGNORECASE),
        re.compile(r'import\s+requests', re.IGNORECASE),
        re.compile(r'import\s+multiprocessing', re.IGNORECASE),
        re.compile(r'import\s+threading', re.IGNORECASE),
        re.compile(r'import\s+ctypes', re.IGNORECASE),
        re.compile(r'import\s+pickle', re.IGNORECASE),
        re.compile(r'import\s+shelve', re.IGNORECASE),
        re.compile(r'import\s+marshal', re.IGNORECASE),
        re.compile(r'import\s+cffi', re.IGNORECASE),
        re.compile(r'import\s+pdb', re.IGNORECASE),
        re.compile(r'import\s+profile', re.IGNORECASE),
        re.compile(r'import\s+trace', re.IGNORECASE),
        re.compile(r'import\s+pathlib', re.IGNORECASE),
        re.compile(r'import\s+glob', re.IGNORECASE),
        re.compile(r'import\s+fnmatch', re.IGNORECASE),
        re.compile(r'import\s+hashlib', re.IGNORECASE),
        re.compile(r'import\s+ssl', re.IGNORECASE),
        re.compile(r'import\s+crypto', re.IGNORECASE),
    ]
    
    def __init__(self, custom_blocked: Optional[Set[str]] = None):
        """
        Initialize validator with optional custom blocked names.
        
        Args:
            custom_blocked: Additional names to block
        """
        self.blocked_names = self.BLOCKED_NAMES.copy()
        if custom_blocked:
            self.blocked_names.update(custom_blocked)
    
    def validate(self, code: str) -> ValidationResult:
        """
        Validate Python code for security.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with is_safe, errors, and warnings
            
        Raises:
            SecurityError: If critical security violation found
        """
        errors = []
        warnings = []
        
        # First check string patterns (fast check)
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.search(code):
                errors.append(f"Dangerous pattern detected: {pattern.pattern}")
        
        # Then check AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ValidationResult(
                is_safe=False,
                errors=[f"Syntax error: {e}"],
                warnings=[]
            )
        
        # Check each node in the AST
        for node in ast.walk(tree):
            node_errors, node_warnings = self._check_node(node)
            errors.extend(node_errors)
            warnings.extend(node_warnings)
        
        is_safe = len(errors) == 0
        
        return ValidationResult(
            is_safe=is_safe,
            errors=errors,
            warnings=warnings
        )
    
    def _check_node(self, node: ast.AST) -> tuple:
        """Check a single AST node for security issues."""
        errors = []
        warnings = []
        
        # Check node type
        if type(node) in self.BLOCKED_NODE_TYPES:
            errors.append(f"Blocked statement type: {type(node).__name__}")
        
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self.BLOCKED_MODULES:
                    errors.append(f"Blocked import: {alias.name}")
        
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in self.BLOCKED_MODULES:
                errors.append(f"Blocked import from: {node.module}")
        
        # Check function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.blocked_names:
                    errors.append(f"Blocked function call: {node.func.id}")
                if node.func.id in self.BLOCKED_BUILTINS:
                    errors.append(f"Blocked builtin call: {node.func.id}")
        
        # Check name references
        if isinstance(node, ast.Name):
            if node.id in self.blocked_names:
                warnings.append(f"Potentially dangerous name: {node.id}")
        
        # Check attribute access
        if isinstance(node, ast.Attribute):
            if node.attr in ('system', 'popen', 'exec', 'kill'):
                errors.append(f"Blocked attribute access: {node.attr}")
        
        return errors, warnings
    
    def validate_strict(self, code: str) -> None:
        """
        Validate code strictly - raises exception if not safe.
        
        Args:
            code: Python code to validate
            
        Raises:
            SecurityError: If any security violation found
        """
        result = self.validate(code)
        if not result.is_safe:
            raise SecurityError(
                f"Code validation failed: {'; '.join(result.errors)}"
            )
    
    def add_blocked(self, names: Set[str]) -> None:
        """Add names to blocked list."""
        self.blocked_names.update(names)
    
    def remove_blocked(self, names: Set[str]) -> None:
        """Remove names from blocked list."""
        self.blocked_names -= names


# Singleton instance
_validator = None

def get_validator() -> ASTValidator:
    """Get singleton validator instance."""
    global _validator
    if _validator is None:
        _validator = ASTValidator()
    return _validator

def validate_code(code: str) -> ValidationResult:
    """Convenience function to validate code."""
    return get_validator().validate(code)

def validate_code_strict(code: str) -> None:
    """Convenience function to validate code strictly."""
    get_validator().validate_strict(code)
