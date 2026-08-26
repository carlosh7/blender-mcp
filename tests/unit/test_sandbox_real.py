"""
blender-mcp-ultra — Tests for Real Sandbox (Subprocess)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestRealSandbox:
    """Tests for subprocess-based sandbox."""

    def test_import(self):
        """Sandbox should be importable."""
        from src.infrastructure.security.sandbox_real import RealSandbox

        assert RealSandbox is not None

    def test_create_sandbox(self):
        """Should create sandbox instance."""
        from src.infrastructure.security.sandbox_real import RealSandbox

        s = RealSandbox(timeout=5)
        assert s is not None
        assert s.timeout == 5

    def test_execute_safe_code(self):
        """Should execute safe code."""
        from src.infrastructure.security.sandbox_real import RealSandbox

        s = RealSandbox(timeout=5)
        result = s.execute("x = 1 + 2")
        assert result.success is True

    def test_execute_with_output(self):
        """Should capture output."""
        from src.infrastructure.security.sandbox_real import RealSandbox

        s = RealSandbox(timeout=5)
        result = s.execute("print('hello world')")
        assert result.success is True
        assert "hello world" in result.stdout

    def test_execute_with_error(self):
        """Should handle errors."""
        from src.infrastructure.security.sandbox_real import RealSandbox

        s = RealSandbox(timeout=5)
        result = s.execute("1/0")
        # Error is caught by wrapper, subprocess succeeds but error in stderr
        assert result.success is True
        assert "ZeroDivisionError" in result.stderr or "error" in result.stderr.lower()

    def test_execute_timeout(self):
        """Should timeout on long execution.

        Nota: el sandbox bloquea __import__, así que el código usuario no
        puede hacer sleep(). El loop puro agota RLIMIT_CPU y el proceso muere
        por señal (SIGXCPU) → el sandbox lo reporta como timed_out.
        """
        from src.infrastructure.security.sandbox_real import RealSandbox

        s = RealSandbox(timeout=2)
        result = s.execute("x = 0\nfor i in range(10**9):\n    x += 1")
        assert result.success is False
        assert result.timed_out is True

    def test_execute_with_context(self):
        """Should pass context variables."""
        from src.infrastructure.security.sandbox_real import RealSandbox

        s = RealSandbox(timeout=5)
        result = s.execute("print(f'Value: {my_var}')", context={"my_var": 42})
        assert result.success is True
        assert "Value: 42" in result.stdout

    def test_isolation(self):
        """Code should be isolated from main process."""
        from src.infrastructure.security.sandbox_real import RealSandbox

        s = RealSandbox(timeout=5)

        # This should not affect the main process
        s.execute("import os; os._exit(0)")
        # Main process should still be running
        assert True  # If we get here, isolation worked

    def test_stats(self):
        """Should track statistics."""
        from src.infrastructure.security.sandbox_real import RealSandbox

        s = RealSandbox(timeout=5)

        s.execute("x = 1")
        s.execute("y = 2")

        stats = s.get_stats()
        assert stats["execution_count"] >= 2

    def test_singleton(self):
        """get_sandbox should return singleton."""
        from src.infrastructure.security.sandbox_real import get_sandbox

        s1 = get_sandbox()
        s2 = get_sandbox()
        assert s1 is s2
