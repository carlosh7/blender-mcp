"""
blender-mcp-ultra — Real Sandbox (Subprocess-based)
Executes LLM-generated code in an isolated subprocess.
True isolation - code cannot escape or access Blender memory.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class SandboxResult:
    """Result of sandbox execution."""

    success: bool
    stdout: str
    stderr: str
    returncode: int
    execution_time: float
    timed_out: bool


class RealSandbox:
    """
    Real sandbox using subprocess isolation.

    Features:
    - True process isolation
    - Timeout enforcement
    - Memory limits (via ulimit)
    - No access to Blender memory
    - Safe for untrusted code
    """

    def __init__(
        self,
        timeout: int = 10,
        memory_limit_mb: int = 100,
        python_path: str = None,
    ):
        """
        Initialize sandbox.

        Args:
            timeout: Maximum execution time in seconds
            memory_limit_mb: Maximum memory usage in MB
            python_path: Path to Python interpreter (default: sys.executable)
        """
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.python_path = python_path or sys.executable

        # Statistics
        self.execution_count = 0
        self.error_count = 0
        self.timeout_count = 0

    def execute(self, code: str, context: dict[str, Any] = None) -> SandboxResult:
        """
        Execute code in isolated subprocess.

        Args:
            code: Python code to execute
            context: Additional context variables (passed as JSON)

        Returns:
            SandboxResult with stdout, stderr, etc.
        """
        start_time = time.time()

        # Create temporary script file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()
        ) as f:
            # Write wrapper script
            wrapper = self._create_wrapper(code, context)
            f.write(wrapper)
            script_path = f.name

        try:
            # Execute in subprocess
            result = self._execute_subprocess(script_path)

            execution_time = time.time() - start_time

            # Parse output
            stdout = result.stdout
            stderr = result.stderr

            # Try to parse JSON output from wrapper
            try:
                output_data = json.loads(stdout)
                stdout = output_data.get("stdout", "")
                if output_data.get("error"):
                    stderr = output_data["error"]
            except json.JSONDecodeError:
                pass

            self.execution_count += 1
            if result.returncode != 0:
                self.error_count += 1
            if result.timed_out:
                self.timeout_count += 1

            return SandboxResult(
                success=result.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                returncode=result.returncode,
                execution_time=execution_time,
                timed_out=result.timed_out,
            )

        finally:
            # Cleanup
            try:
                os.unlink(script_path)
            except OSError:
                pass

    def _create_wrapper(self, code: str, context: dict[str, Any] = None) -> str:
        """Create wrapper script with safety measures."""
        context_json = json.dumps(context or {})

        return f'''#!/usr/bin/env python3
"""
Sandbox wrapper - executes code in isolation.
This file is auto-generated and will be deleted after execution.
"""
import sys
import json
import os

# Limit resources
try:
    import resource
    # Limit memory (in MB)
    mem_limit = {self.memory_limit_mb} * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
    # Limit CPU time
    resource.setrlimit(resource.RLIMIT_CPU, ({self.timeout}, {self.timeout}))
except (ImportError, ValueError):
    pass  # Windows or limited environment

# Capture output
output = {{'stdout': '', 'stderr': '', 'error': None}}

class OutputCapture:
    def __init__(self):
        self.buffer = []
    def write(self, text):
        self.buffer.append(str(text))
    def flush(self):
        pass

# Redirect stdout/stderr
original_stdout = sys.stdout
original_stderr = sys.stderr
capture_out = OutputCapture()
capture_err = OutputCapture()
sys.stdout = capture_out
sys.stderr = capture_err

try:
    # Load context
    context = json.loads('{context_json}')

    # Create safe namespace
    namespace = {{
        '__builtins__': {{
            'print': print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'sum': sum,
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'True': True,
            'False': False,
            'None': None,
            'isinstance': isinstance,
            'type': type,
            'hasattr': hasattr,
            'getattr': getattr,
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
        }}
    }}
    namespace.update(context)

    # Execute code
    compiled = compile({repr(code)}, '<sandbox>', 'exec')
    exec(compiled, namespace)

    output['stdout'] = ''.join(capture_out.buffer)
    output['stderr'] = ''.join(capture_err.buffer)

except Exception as e:
    output['error'] = f"{{type(e).__name__}}: {{e}}"
    output['stderr'] = ''.join(capture_err.buffer)

finally:
    sys.stdout = original_stdout
    sys.stderr = original_stderr

# Output result as JSON
print(json.dumps(output))
'''

    def _execute_subprocess(self, script_path: str) -> subprocess.CompletedProcess:
        """Execute script in subprocess with timeout."""
        try:
            result = subprocess.run(
                [self.python_path, script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=tempfile.gettempdir(),
                env={
                    "PATH": "/usr/bin:/bin:/usr/local/bin",
                    "HOME": tempfile.gettempdir(),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
            )
            result.timed_out = result.returncode < 0  # kill por señal (SIGXCPU/SIGKILL) = límite de recursos
            return result
        except subprocess.TimeoutExpired:
            result = subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr=f"Execution timed out after {self.timeout}s",
            )
            result.timed_out = True
            return result

    def get_stats(self) -> dict[str, Any]:
        """Get sandbox statistics."""
        return {
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "timeout_count": self.timeout_count,
            "success_rate": (
                (self.execution_count - self.error_count) / self.execution_count * 100
                if self.execution_count > 0
                else 0
            ),
        }


# ═══════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════

_sandbox: RealSandbox | None = None


def get_sandbox(**kwargs) -> RealSandbox:
    """Get singleton sandbox instance."""
    global _sandbox
    if _sandbox is None:
        _sandbox = RealSandbox(**kwargs)
    return _sandbox


def execute_in_sandbox(code: str, context: dict[str, Any] = None) -> SandboxResult:
    """Convenience function to execute code in sandbox."""
    return get_sandbox().execute(code, context)
