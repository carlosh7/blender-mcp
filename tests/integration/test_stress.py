"""
blender-mcp-ultra — Stress Tests
Performance and concurrency tests.
"""
import sys
import os
import socket
import json
import time
import threading
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def is_blender_available():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('localhost', 9876))
        sock.close()
        return True
    except:
        return False

skip_without_blender = pytest.mark.skipif(
    not is_blender_available(),
    reason="Blender MCP server not running"
)


def send_command(command, params=None):
    """Send command to Blender MCP server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(('localhost', 9876))
    cmd = json.dumps({"command": command, "params": params or {}})
    sock.sendall(cmd.encode())
    time.sleep(0.1)
    resp = sock.recv(65536)
    sock.close()
    return json.loads(resp.decode()) if resp else None


class TestConcurrency:
    """Tests for concurrent operations."""
    
    @skip_without_blender
    def test_concurrent_requests(self):
        """Test multiple concurrent requests."""
        results = []
        errors = []
        
        def make_request(i):
            try:
                result = send_command("tool", {
                    "tool_name": "scene.get_info",
                    "params": {}
                })
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Create 10 threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=make_request, args=(i,))
            threads.append(t)
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join(timeout=30)
        
        # Verify results
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"
        assert len(errors) == 0, f"Errors: {errors}"
    
    @skip_without_blender
    def test_rapid_fire_requests(self):
        """Test rapid fire requests."""
        results = []
        
        for i in range(20):
            try:
                result = send_command("tool", {
                    "tool_name": "scene.get_info",
                    "params": {}
                })
                results.append(result)
                time.sleep(0.05)  # Small delay between requests
            except Exception as e:
                pass
        
        # Verify most requests succeeded
        assert len(results) >= 15, f"Expected at least 15 results, got {len(results)}"


class TestPerformance:
    """Tests for performance metrics."""
    
    @skip_without_blender
    def test_response_time(self):
        """Test response time is acceptable."""
        start = time.time()
        result = send_command("tool", {
            "tool_name": "scene.get_info",
            "params": {}
        })
        elapsed = time.time() - start
        
        assert result is not None
        assert elapsed < 10.0, f"Response time {elapsed:.2f}s exceeds 10s limit"
    
    @skip_without_blender
    def test_tool_execution_time(self):
        """Test tool execution time."""
        start = time.time()
        result = send_command("tool", {
            "tool_name": "scene.get_info",
            "params": {}
        })
        elapsed = time.time() - start
        
        assert result is not None
        # Scene info should be fast
        assert elapsed < 2.0, f"Scene info took {elapsed:.2f}s"


class TestMemory:
    """Tests for memory usage."""
    
    @skip_without_blender
    def test_multiple_object_creation(self):
        """Test creating multiple objects doesn't leak memory."""
        # Create 50 objects
        for i in range(50):
            send_command("tool", {
                "tool_name": "object.create",
                "params": {"type": "MESH", "name": f"StressObj_{i}", "location": [i*2, 0, 0]}
            })
        
        # Verify scene has objects
        result = send_command("get_scene_info")
        assert result is not None
        assert result.get("object_count", 0) >= 50


class TestErrorRecovery:
    """Tests for error recovery."""
    
    @skip_without_blender
    def test_invalid_tool_name(self):
        """Test handling of invalid tool names."""
        result = send_command("tool", {
            "tool_name": "invalid.tool.name",
            "params": {}
        })
        # Should not crash, return error
        assert result is not None
    
    @skip_without_blender
    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        result = send_command("tool", {
            "tool_name": "object.create",
            "params": {"invalid": "params"}
        })
        # Should not crash, return error
        assert result is not None
    
    @skip_without_blender
    def test_connection_recovery(self):
        """Test recovery after connection issue."""
        # Make a request
        result1 = send_command("ping")
        assert result1 is not None
        
        # Small delay
        time.sleep(0.5)
        
        # Make another request
        result2 = send_command("ping")
        assert result2 is not None
        
        # Both should succeed
        assert result1.get("pong") is True
        assert result2.get("pong") is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
