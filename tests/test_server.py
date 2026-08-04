"""
blender-mcp — Core Import Tests
Tests that the simplified system imports correctly.
Does NOT require Blender (except for addon tests).
"""
import os
import json
import sys
import pytest
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCoreImports:
    def test_blender_connection_import(self):
        from blender_connection import BlenderConnection, get_blender
        assert BlenderConnection is not None


class TestBlenderConnection:
    def test_send_command_unwraps_success_and_disconnects(self):
        from blender_connection import BlenderConnection

        sock = Mock()
        sock.recv.return_value = b'{"status":"success","result":{"pong":true}}'
        connection = BlenderConnection()
        connection.sock = sock

        assert connection.send_command("ping") == {"pong": True}
        sock.close.assert_called_once()
        assert connection.sock is None

    def test_send_command_returns_unwrapped_legacy_response(self):
        from blender_connection import BlenderConnection

        sock = Mock()
        sock.recv.return_value = b'{"pong":true}'
        connection = BlenderConnection()
        connection.sock = sock

        assert connection.send_command("ping") == {"pong": True}

    def test_send_command_raises_blender_error(self):
        from blender_connection import BlenderConnection

        sock = Mock()
        sock.recv.return_value = b'{"status":"error","message":"bad command"}'
        connection = BlenderConnection()
        connection.sock = sock

        with pytest.raises(RuntimeError, match="bad command"):
            connection.send_command("unknown")



class TestGeneratedTools:
    def test_model_from_scratch_forwards_structured_parameters(self, monkeypatch):
        pytest.importorskip("mcp")
        import mcp_tools

        connection = Mock()
        connection.send_command.return_value = {"name": "Crate"}
        monkeypatch.setattr(mcp_tools, "get_blender", lambda: connection)

        tool = next(fn for fn in mcp_tools.TOOL_FUNCTIONS
                    if fn.__name__ == "model_from_scratch")
        result = tool(name="Crate", type="CUBE", scale=[2, 3, 4], bevel_width=0.1)

        assert json.loads(result) == {"name": "Crate"}
        command, params = connection.send_command.call_args.args
        assert command == "model_from_scratch"
        assert params["scale"] == [2, 3, 4]
        assert params["bevel_width"] == 0.1

    def test_animate_from_scratch_forwards_motion(self, monkeypatch):
        pytest.importorskip("mcp")
        import mcp_tools

        connection = Mock()
        connection.send_command.return_value = {"keyframes": 2}
        monkeypatch.setattr(mcp_tools, "get_blender", lambda: connection)

        tool = next(fn for fn in mcp_tools.TOOL_FUNCTIONS
                    if fn.__name__ == "animate_from_scratch")
        result = tool(object_name="Crate", start_frame=1, end_frame=24,
                      start_loc=[0, 0, 0], end_loc=[2, 0, 1])

        assert json.loads(result) == {"keyframes": 2}
        command, params = connection.send_command.call_args.args
        assert command == "animate_from_scratch"
        assert params["start_loc"] == [0, 0, 0]
        assert params["end_loc"] == [2, 0, 1]


class TestDocumentationSearch:
    def test_rst_search_import(self):
        from blender_mcp.rst_search import search_api_docs, get_python_api_docs

        assert callable(search_api_docs)
        assert callable(get_python_api_docs)

    def test_rst_search_works(self):
        from blender_mcp.rst_search import search_api_docs

        result = search_api_docs("cylinder")
        assert "results" in result
        assert "query" in result
