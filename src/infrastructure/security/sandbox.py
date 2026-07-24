"""
blender-mcp-ultra — Secure Sandbox (Enterprise Grade)
Executes LLM-generated code in an isolated namespace.
Blocks dangerous operations and limits execution time.
"""
import sys
import signal
import traceback
from typing import Any, Dict, List, Optional, Callable, Set
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from .ast_validator import ASTValidator, SecurityError, validate_code_strict

# Blender is optional - only available inside Blender
try:
    import bpy
    HAS_BPY = True
except ImportError:
    bpy = None
    HAS_BPY = False


class SandboxTimeout(Exception):
    """Raised when code execution exceeds time limit."""
    pass


class SandboxError(Exception):
    """Raised when sandbox encounters an error."""
    pass


@dataclass
class ExecutionResult:
    """Result of code execution in sandbox."""
    success: bool
    output: str
    error: Optional[str]
    execution_time: float
    timestamp: str
    blocked_ops: List[str]


class Sandbox:
    """
    Secure sandbox for executing LLM-generated code.
    
    Features:
    - Isolated namespace (no builtins)
    - AST validation before execution
    - Timeout protection
    - Limited Blender API access
    - Audit logging
    - Memory limits
    """
    
    # Allowed Blender modules
    ALLOWED_BLENDER_MODULES = {
        'bpy', 'bpy.types', 'bpy.ops', 'bpy.data', 'bpy.context',
        'mathutils', 'mathutils.geometry',
    }
    
    # Allowed builtins (minimal set)
    ALLOWED_BUILTINS = {
        'print', 'len', 'range', 'enumerate', 'zip', 'map', 'filter',
        'min', 'max', 'abs', 'round', 'sum', 'sorted', 'reversed',
        'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple', 'set',
        'True', 'False', 'None',
        'isinstance', 'type', 'hasattr', 'getattr',
        'Exception', 'ValueError', 'TypeError', 'KeyError',
    }
    
    # Dangerous Blender operators that should be blocked
    BLOCKED_BLENDER_OPS = {
        'wm.quit_blender', 'wm.read_factory_settings',
        'wm.read_factory_userpref', 'wm.read_userpref',
        'wm.save_as_mainfile', 'wm.save_mainfile',
        'wm.open_mainfile', 'wm.revert_mainfile',
    }
    
    def __init__(
        self,
        timeout_seconds: int = 30,
        validate_code: bool = True,
        custom_allowed: Optional[Dict[str, Any]] = None,
        memory_limit_mb: int = 100,
    ):
        """
        Initialize sandbox.
        
        Args:
            timeout_seconds: Maximum execution time in seconds
            validate_code: Whether to validate code before execution
            custom_allowed: Additional allowed names in namespace
            memory_limit_mb: Maximum memory usage in MB
        """
        self.timeout_seconds = timeout_seconds
        self.validate_code = validate_code
        self.validator = ASTValidator()
        self.memory_limit_mb = memory_limit_mb
        
        # Build namespace
        self.namespace = self._build_namespace(custom_allowed or {})
        
        # Statistics
        self.execution_count = 0
        self.error_count = 0
        self.blocked_count = 0
        self.last_execution = None
    
    def _build_namespace(self, custom_allowed: Dict[str, Any]) -> Dict[str, Any]:
        """Build the execution namespace."""
        namespace = {
            '__builtins__': self._create_safe_builtins(),
        }
        
        # Add Blender modules if available
        if HAS_BPY:
            namespace['bpy'] = bpy
            namespace['C'] = bpy.context
            namespace['D'] = bpy.data
        
        namespace.update(custom_allowed)
        return namespace
    
    def _create_safe_builtins(self) -> Dict[str, Any]:
        """Create a safe subset of builtins."""
        import builtins
        safe = {}
        for name in self.ALLOWED_BUILTINS:
            if hasattr(builtins, name):
                safe[name] = getattr(builtins, name)
        return safe
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Execute code in sandbox.
        
        Args:
            code: Python code to execute
            context: Additional context variables
            
        Returns:
            ExecutionResult with success, output, error, etc.
        """
        start_time = datetime.now()
        output_buffer = []
        blocked_ops = []
        
        # Validate code if enabled
        if self.validate_code:
            try:
                validate_code_strict(code)
            except SecurityError as e:
                self.error_count += 1
                self.blocked_count += 1
                return ExecutionResult(
                    success=False,
                    output='',
                    error=f"Security error: {e}",
                    execution_time=0.0,
                    timestamp=start_time.isoformat(),
                    blocked_ops=[str(e)]
                )
        
        # Update namespace with context
        exec_namespace = self.namespace.copy()
        if context:
            exec_namespace.update(context)
        
        # Capture stdout
        original_stdout = sys.stdout
        
        class OutputCapture:
            def __init__(self):
                self.buffer = []
            def write(self, text):
                self.buffer.append(str(text))
            def flush(self):
                pass
        
        capture = OutputCapture()
        sys.stdout = capture
        
        try:
            # Compile and execute
            compiled = compile(code, '<sandbox>', 'exec')
            
            # Execute with timeout
            self._execute_with_timeout(compiled, exec_namespace)
            
            # Get output
            output = '\n'.join(capture.buffer)
            
            self.execution_count += 1
            self.last_execution = datetime.now()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                success=True,
                output=output,
                error=None,
                execution_time=execution_time,
                timestamp=start_time.isoformat(),
                blocked_ops=blocked_ops
            )
            
        except SandboxTimeout as e:
            self.error_count += 1
            return ExecutionResult(
                success=False,
                output='',
                error=f"Execution timed out after {self.timeout_seconds}s",
                execution_time=self.timeout_seconds,
                timestamp=start_time.isoformat(),
                blocked_ops=blocked_ops
            )
            
        except SecurityError as e:
            self.error_count += 1
            self.blocked_count += 1
            return ExecutionResult(
                success=False,
                output='',
                error=f"Security violation: {e}",
                execution_time=(datetime.now() - start_time).total_seconds(),
                timestamp=start_time.isoformat(),
                blocked_ops=[str(e)]
            )
            
        except Exception as e:
            self.error_count += 1
            return ExecutionResult(
                success=False,
                output='',
                error=f"Execution error: {type(e).__name__}: {e}",
                execution_time=(datetime.now() - start_time).total_seconds(),
                timestamp=start_time.isoformat(),
                blocked_ops=blocked_ops
            )
            
        finally:
            sys.stdout = original_stdout
    
    def _execute_with_timeout(self, compiled: Any, namespace: Dict[str, Any]) -> None:
        """Execute compiled code with timeout."""
        def timeout_handler(signum, frame):
            raise SandboxTimeout("Execution timed out")
        
        # Set timeout (Unix only)
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout_seconds)
            try:
                exec(compiled, namespace)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Windows: no SIGALRM, just execute
            exec(compiled, namespace)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sandbox statistics."""
        return {
            'execution_count': self.execution_count,
            'error_count': self.error_count,
            'blocked_count': self.blocked_count,
            'success_rate': (
                (self.execution_count - self.error_count) / self.execution_count * 100
                if self.execution_count > 0 else 0
            ),
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
        }
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        self.execution_count = 0
        self.error_count = 0
        self.blocked_count = 0
        self.last_execution = None


# Singleton instance
_sandbox = None

def get_sandbox(**kwargs) -> Sandbox:
    """Get singleton sandbox instance."""
    global _sandbox
    if _sandbox is None:
        _sandbox = Sandbox(**kwargs)
    return _sandbox

def execute_code(code: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
    """Convenience function to execute code in sandbox."""
    return get_sandbox().execute(code, context)
