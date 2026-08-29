"""
socket_protocol.py — Framing y parsing del protocolo de socket (:9876).

v2 (framed):   b"BMCP" + uint32 BE (longitud payload) + payload JSON
legacy:        JSON desnudo acumulado (ahujasid-compatible)

El servidor acepta ambos; responde en el mismo modo del cliente. Las
respuestas legacy llevan "\\n" final (inocuo para clientes legacy que
acumulan y hacen json.loads). Sin bpy: importable fuera de Blender.
"""

import json
import struct

MAGIC = b"BMCP"
HEADER = struct.Struct(">4sI")
MAX_MESSAGE = 64 * 1024 * 1024  # 64 MB

_decoder = json.JSONDecoder()


def encode_framed(obj) -> bytes:
    payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return HEADER.pack(MAGIC, len(payload)) + payload


def encode_legacy(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode("utf-8") + b"\n"


def try_parse(buf: bytes):
    """Parsea un mensaje del buffer.

    Devuelve (cmd | None, rest, framed). cmd=None ⇒ incompleto (acumular).
    Legacy usa raw_decode para preservar bytes sobrantes (pipelining).
    """
    if buf[:4] == MAGIC:
        if len(buf) < HEADER.size:
            return None, buf, True
        _, length = HEADER.unpack(buf[: HEADER.size])
        if length > MAX_MESSAGE:
            raise ValueError(f"mensaje demasiado grande: {length} bytes")
        total = HEADER.size + length
        if len(buf) < total:
            return None, buf, True
        payload = buf[HEADER.size : total]
        return json.loads(payload.decode("utf-8")), buf[total:], True

    text = buf.decode("utf-8")
    try:
        cmd, end = _decoder.raw_decode(text)
    except (json.JSONDecodeError, ValueError):
        return None, buf, False
    rest = b""
    if end < len(text):
        rest = text[end:].lstrip().encode("utf-8")
    return cmd, rest, False
