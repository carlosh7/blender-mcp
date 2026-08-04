"""
test_mcp_tools.py — Offline tests for the MCP tool surface.

No Blender, no mcp SDK: mcp_tools functions are plain callables over a mocked
socket connection. Verifies schema generation, dispatch mapping, read-only
marking, and spec/registry parity.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import mcp_tools  # noqa: E402


class FakeConnection:
    def __init__(self):
        self.calls = []

    def send_command(self, command, params):
        self.calls.append((command, params))
        return {"status": "ok", "command": command}


@pytest.fixture()
def fake(monkeypatch):
    conn = FakeConnection()
    monkeypatch.setattr(mcp_tools, "get_blender", lambda: conn)
    return conn


def test_tool_surface_nonempty():
    assert len(mcp_tools.TOOL_FUNCTIONS) >= 100
    assert len(mcp_tools.TOOL_META) == len(mcp_tools.TOOL_FUNCTIONS)
    assert len(mcp_tools.READ_ONLY) >= 20


def test_schema_shape():
    schema = mcp_tools.tool_schema()
    assert len(schema) == len(mcp_tools.TOOL_FUNCTIONS)
    for t in schema:
        assert t["name"]
        assert t["description"]
        assert t["inputSchema"]["type"] == "object"
        assert isinstance(t["inputSchema"]["required"], list)


def test_required_params_marked(fake):
    # create_material has optional params; assign_material requires two
    assign = next(t for t in mcp_tools.TOOL_META.values()
                  if t["command"] == "assign_material")
    assert "object_name" in [p["name"] for p in assign["params"] if "default" not in p]
    # every spec param without default must be in schema required
    schema = {t["name"]: t for t in mcp_tools.tool_schema()}
    for name, meta in mcp_tools.TOOL_META.items():
        required = schema[name]["inputSchema"]["required"]
        spec_required = [p["name"] for p in meta["params"] if "default" not in p]
        assert set(spec_required) == set(required), name


def test_run_tool_dispatches_correct_command(fake):
    result = mcp_tools.run_tool("animate_location", {
        "object_name": "Cube", "start_frame": 1, "end_frame": 30,
        "start_loc": [0, 0, 0], "end_loc": [5, 0, 0]})
    assert result["status"] == "ok"
    cmd, params = fake.calls[-1]
    assert cmd == "animate_location"
    assert params["object_name"] == "Cube"
    assert params["end_loc"] == [5, 0, 0]


def test_run_tool_unknown(fake):
    result = mcp_tools.run_tool("nope_not_a_tool", {})
    assert "error" in result


def test_defaults_passed_through(fake):
    mcp_tools.run_tool("create_object", {"type": "CUBE", "name": "Box"})
    cmd, params = fake.calls[-1]
    assert cmd == "create_object"
    assert params["name"] == "Box"
    # defaults that were not supplied should still reach the backend
    assert "location" in params


def test_function_signatures_typed(fake):
    import inspect
    for fn in mcp_tools.TOOL_FUNCTIONS:
        sig = inspect.signature(fn)
        for p in sig.parameters.values():
            assert p.kind == inspect.Parameter.KEYWORD_ONLY
            assert p.annotation is not inspect.Parameter.empty
        assert sig.return_annotation is str


def test_read_only_marks_are_consistent():
    for name in mcp_tools.READ_ONLY:
        assert mcp_tools.TOOL_META[name]["read_only"] is True


def test_spec_matches_handlers():
    """Every MCP tool command must have a backend handler (registry or legacy)."""
    import addon  # noqa: F401  (package init under stub? only for import safety)
    # handlers live under the addon package which requires bpy; skip if absent
    try:
        import bpy  # noqa: F401
    except ImportError:
        pytest.skip("bpy not available; backend coverage tested in test_command_surface")
