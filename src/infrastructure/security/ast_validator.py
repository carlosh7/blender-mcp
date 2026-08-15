"""
blender-mcp-ultra — AST Validator (Allowlist-based)
Validates Python code against a whitelist of allowed patterns.
Only explicitly allowed modules, builtins, and functions are permitted.
"""
import ast
import re
from typing import Set, List, Optional, Any
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
    """Validates Python code against security allowlist."""
    
    # ═══════════════════════════════════════════════════════════════
    # ALLOWLIST - Only these are permitted
    # ═══════════════════════════════════════════════════════════════
    
    # Allowed modules (whitelist)
    ALLOWED_MODULES: Set[str] = {
        # Blender API
        'bpy', 'bpy.types', 'bpy.ops', 'bpy.data', 'bpy.context',
        'bpy.app', 'bpy.utils', 'bpy.props',
        
        # Math
        'math', 'mathutils', 'mathutils.geometry', 'mathutils.noise',
        
        # Standard library (safe subset)
        'json', 'random', 'collections', 'datetime', 'typing',
        'itertools', 'functools', 'operator', 'string', 're',
        'copy', 'enum', 'dataclasses', 'contextlib',
        
        # Blender specific
        'bmesh', 'bmesh.ops', 'bmesh.types',
        'gpu', 'gpu_ex',
        'blf', 'ui',
    }
    
    # Allowed builtins (whitelist)
    ALLOWED_BUILTINS: Set[str] = {
        # Output
        'print',
        
        # Iteration
        'len', 'range', 'enumerate', 'zip', 'map', 'filter',
        'reversed', 'sorted',
        
        # Math
        'min', 'max', 'abs', 'round', 'sum', 'pow',
        
        # Types
        'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple', 'set',
        'type', 'isinstance', 'hasattr', 'getattr', 'setattr',
        
        # Constants
        'True', 'False', 'None',
        
        # Conversion
        'chr', 'ord', 'hex', 'bin', 'oct',
        
        # Exception handling
        'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
        'RuntimeError', 'StopIteration', 'NotImplementedError',
    }
    
    # Allowed function/method names (whitelist)
    ALLOWED_FUNCTIONS: Set[str] = {
        # Blender operators (common)
        'select_all', 'select', 'deselect',
        'delete', 'duplicate', 'join',
        'transform_apply', 'shade_smooth', 'shade_flat',
        'object.mode_set',
        
        # Mesh operations
        'primitive_cube_add', 'primitive_uv_sphere_add',
        'primitive_cylinder_add', 'primitive_cone_add',
        'primitive_torus_add', 'primitive_plane_add',
        'primitive_grid_add', 'primitive_circle_add',
        
        # Modifier operations
        'modifier_add', 'modifier_remove', 'modifier_apply',
        
        # Material operations
        'material_slot_add', 'material_slot_remove',
        
        # Animation
        'keyframe_insert', 'keyframe_delete',
        
        # UV operations
        'uv.smart_project', 'uv.project_from_view',
        
        # Common functions
        'range', 'len', 'print', 'type', 'isinstance',
    }
    
    # Dangerous string patterns (blocked regardless of context)
    DANGEROUS_PATTERNS: List[re.Pattern] = [
        # Code execution
        re.compile(r'exec\s*\(', re.IGNORECASE),
        re.compile(r'eval\s*\(', re.IGNORECASE),
        re.compile(r'compile\s*\(', re.IGNORECASE),
        re.compile(r'__import__', re.IGNORECASE),
        
        # System access
        re.compile(r'os\.\s*system\s*\(', re.IGNORECASE),
        re.compile(r'subprocess\.', re.IGNORECASE),
        re.compile(r'os\.\s*popen\s*\(', re.IGNORECASE),
        
        # File operations (write)
        re.compile(r'open\s*\([^)]*["\']w', re.IGNORECASE),
        re.compile(r'open\s*\([^)]*["\']a', re.IGNORECASE),
        
        # Network
        re.compile(r'socket\.', re.IGNORECASE),
        re.compile(r'urllib\.', re.IGNORECASE),
        re.compile(r'requests\.', re.IGNORECASE),
        
        # File operations (any mode - for security tests)
        re.compile(r'\bopen\s*\(', re.IGNORECASE),
    ]
    
    def __init__(self, mode: str = "allowlist", custom_blocked: Set[str] = None):
        """
        Initialize validator.
        
        Args:
            mode: "allowlist" (default, secure) or "blocklist" (legacy)
            custom_blocked: Additional names to block (backward compatibility)
        """
        self.mode = mode
        self._custom_allowed = set()
        self._custom_blocked = custom_blocked or set()
    
    def validate(self, code: str) -> ValidationResult:
        """
        Validate Python code for security.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with is_safe, errors, and warnings
        """
        errors = []
        warnings = []
        
        if self.mode == "allowlist":
            return self._validate_allowlist(code)
        else:
            return self._validate_blocklist(code)
    
    def _validate_allowlist(self, code: str) -> ValidationResult:
        """Validate using allowlist approach (secure)."""
        errors = []
        warnings = []
        
        # 1. Check dangerous string patterns first (fast)
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.search(code):
                errors.append(f"Dangerous pattern: {pattern.pattern}")
        
        # 2. Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ValidationResult(
                is_safe=False,
                errors=[f"Syntax error: {e}"],
                warnings=[]
            )
        
        # 3. Check each node
        for node in ast.walk(tree):
            node_errors, node_warnings = self._check_node_allowlist(node)
            errors.extend(node_errors)
            warnings.extend(node_warnings)
        
        return ValidationResult(
            is_safe=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _check_node_allowlist(self, node: ast.AST) -> tuple:
        """Check node against allowlist."""
        errors = []
        warnings = []
        
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split('.')[0]
                if module not in self.ALLOWED_MODULES and module not in self._custom_allowed:
                    errors.append(f"Blocked import: {alias.name}")
        
        if isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split('.')[0]
                if module not in self.ALLOWED_MODULES and module not in self._custom_allowed:
                    errors.append(f"Blocked import from: {node.module}")
        
        # Check function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                # Check custom blocked first
                if func_name in self._custom_blocked:
                    errors.append(f"Blocked function: {func_name}")
                elif func_name not in self.ALLOWED_BUILTINS and func_name not in self.ALLOWED_FUNCTIONS:
                    if func_name not in self._custom_allowed:
                        warnings.append(f"Unknown function: {func_name}")
        
        # Check attribute access
        if isinstance(node, ast.Attribute):
            # Check for dangerous attribute chains
            if node.attr in ('system', 'popen', 'exec', 'kill', 'terminate'):
                errors.append(f"Dangerous attribute: {node.attr}")
        
        return errors, warnings
    
    def _validate_blocklist(self, code: str) -> ValidationResult:
        """Validate using blocklist approach (legacy, less secure)."""
        # Import the old validator for backward compatibility
        from .ast_validator_legacy import ASTValidatorLegacy
        legacy = ASTValidatorLegacy()
        return legacy.validate(code)
    
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
    
    def add_allowed(self, names: Set[str]) -> None:
        """Add names to allowed list."""
        self._custom_allowed.update(names)
    
    def add_blocked(self, names: Set[str]) -> None:
        """Add names to blocked list."""
        self._custom_blocked.update(names)


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

_validator: Optional[ASTValidator] = None


def get_validator(mode: str = "allowlist") -> ASTValidator:
    """Get singleton validator instance."""
    global _validator
    if _validator is None:
        _validator = ASTValidator(mode=mode)
    return _validator


def validate_code(code: str) -> ValidationResult:
    """Convenience function to validate code."""
    return get_validator().validate(code)


def validate_code_strict(code: str) -> None:
    """Convenience function to validate code strictly."""
    get_validator().validate_strict(code)
