"""
blender-mcp — Unit Tests for Execution Queue
Tests for thread-safe execution queue.
"""

import os
import sys
import time
from unittest.mock import MagicMock, patch

# Mock bpy before importing
sys.modules["bpy"] = MagicMock()
sys.modules["mathutils"] = MagicMock()

# Add addon to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "addon"))


class TestExecutionQueue:
    """Tests for ExecutionQueue class."""

    def test_queue_creation(self):
        """Test queue can be created."""
        from execution_queue import ExecutionQueue

        queue = ExecutionQueue()
        assert queue is not None
        assert queue._pending.empty()

    def test_submit_task(self):
        """Test task submission."""
        from execution_queue import ExecutionQueue

        queue = ExecutionQueue()

        def dummy_func():
            return 42

        task_id = queue.submit(dummy_func)
        assert task_id is not None
        assert task_id.startswith("task_")

    def test_submit_with_custom_id(self):
        """Test task submission with custom ID."""
        from execution_queue import ExecutionQueue

        queue = ExecutionQueue()

        def dummy_func():
            return "result"

        task_id = queue.submit(dummy_func, task_id="custom_id")
        assert task_id == "custom_id"

    def test_is_pending(self):
        """Test pending status check."""
        from execution_queue import ExecutionQueue

        queue = ExecutionQueue()

        def slow_func():
            time.sleep(0.1)
            return "done"

        task_id = queue.submit(slow_func)
        # Should be pending initially
        assert queue.is_pending(task_id)

    def test_clear_queue(self):
        """Test queue clearing."""
        from execution_queue import ExecutionQueue

        queue = ExecutionQueue()

        def dummy_func():
            return "result"

        queue.submit(dummy_func)
        queue.clear()
        assert queue._pending.empty()
        assert len(queue._results) == 0
        assert len(queue._errors) == 0


class TestSafeBpyExecute:
    """Tests for safe_bpy_execute function."""

    def test_function_execution(self):
        """Test basic function execution."""
        from execution_queue import safe_bpy_execute

        def add(a, b):
            return a + b

        # Mock the queue to test without bpy
        with patch("execution_queue.execution_queue") as mock_queue:
            mock_queue.submit.return_value = "test_id"
            mock_queue.get_result.return_value = 5

            result = safe_bpy_execute(add, 2, 3)
            assert result == 5

    def test_timeout_handling(self):
        """Test timeout handling."""
        from execution_queue import safe_bpy_execute

        def slow_func():
            time.sleep(10)
            return "done"

        with patch("execution_queue.execution_queue") as mock_queue:
            mock_queue.submit.return_value = "test_id"
            mock_queue.get_result.return_value = None

            result = safe_bpy_execute(slow_func, timeout=0.1)
            assert result is None


class TestMainThreadDecorator:
    """Tests for main_thread_only decorator."""

    def test_decorator_preserves_function_name(self):
        """Test decorator preserves function name."""
        from execution_queue import main_thread_only

        @main_thread_only
        def my_function():
            """My docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_decorator_preserves_function_behavior(self):
        """Test decorator preserves function behavior."""
        from execution_queue import main_thread_only

        @main_thread_only
        def add(a, b):
            return a + b

        with patch("execution_queue.execution_queue") as mock_queue:
            mock_queue.submit.return_value = "test_id"
            mock_queue.get_result.return_value = 5

            result = add(2, 3)
            assert result == 5
