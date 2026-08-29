"""
socket_protocol — tests unitarios (sin bpy).
Framing v2 (BMCP + uint32 BE + JSON) y legacy (JSON desnudo acumulado).
"""

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "addon"))

import socket_protocol as proto  # noqa: E402


class TestFramed:
    def test_round_trip(self):
        cmd = {"command": "ping", "args": {"x": 1}}
        buf = proto.encode_framed(cmd)
        parsed, rest, framed = proto.try_parse(buf)
        assert parsed == cmd
        assert rest == b""
        assert framed is True

    def test_incomplete_header(self):
        parsed, rest, framed = proto.try_parse(b"BMCP")
        assert parsed is None and framed is True and rest == b"BMCP"

    def test_incomplete_payload(self):
        buf = proto.encode_framed({"command": "ping"})[:-4]
        parsed, rest, framed = proto.try_parse(buf)
        assert parsed is None and framed is True and rest == buf

    def test_oversize_rejected(self):
        buf = proto.HEADER.pack(proto.MAGIC, proto.MAX_MESSAGE + 1)
        with pytest.raises(ValueError):
            proto.try_parse(buf)


class TestLegacy:
    def test_single_json(self):
        cmd = {"command": "ping"}
        parsed, rest, framed = proto.try_parse(json.dumps(cmd).encode())
        assert parsed == cmd and rest == b"" and framed is False

    def test_pipelined_preserves_rest(self):
        buf = (
            json.dumps({"command": "ping"}).encode()
            + b" "
            + json.dumps({"command": "pong"}).encode()
        )
        cmd1, rest, _ = proto.try_parse(buf)
        assert cmd1 == {"command": "ping"}
        cmd2, rest, _ = proto.try_parse(rest)
        assert cmd2 == {"command": "pong"} and rest == b""

    def test_trailing_newline_harmless(self):
        parsed, rest, _ = proto.try_parse(json.dumps({"a": 1}).encode() + b"\n")
        assert parsed == {"a": 1} and rest == b""

    def test_incomplete_waits(self):
        parsed, rest, framed = proto.try_parse(b'{"command": "pi')
        assert parsed is None and framed is False and rest == b'{"command": "pi'


class TestResponses:
    def test_legacy_suffix_is_newline_json(self):
        out = proto.encode_legacy({"ok": True})
        assert out.endswith(b"\n") and json.loads(out.decode()) == {"ok": True}

    def test_legacy_client_tolerates_newline_suffix(self):
        import json as _json

        out = proto.encode_legacy({"status": "success", "result": {"pong": True}})
        assert _json.loads(out.decode("utf-8"))["status"] == "success"
