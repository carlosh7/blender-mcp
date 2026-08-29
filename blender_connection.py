"""
blender-mcp — Blender Socket Connection (shared module)
Avoids circular imports by providing a single connection entry point.

Thread-safe: las llamadas concurrentes (FastMCP ejecuta handlers en un
threadpool) se serializan con un lock para no cruzar respuestas del socket.
"""

import json
import logging
import os
import socket
import threading
from pathlib import Path

logger = logging.getLogger("blender-mcp")

SOCKET_HOST = os.getenv("BLENDER_HOST", "localhost")
SOCKET_PORT = int(os.getenv("BLENDER_PORT", "9876"))

_connection = None
_connection_lock = threading.Lock()


def _token_file_path() -> Path:
    """Ruta del token compartido addon↔gateway (misma fórmula que
    addon/_axsock.py: <config>/blender-mcp/socket_token, cross-OS)."""
    import sys

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    return base / "blender-mcp" / "socket_token"


_token_cache = None


def get_socket_token() -> str:
    """Token del addon: env BLENDER_TOKEN/BLENDER_MCP_TOKEN > archivo compartido.

    El addon genera el token al arrancar si no existe; el gateway puede
    arrancar antes, así que solo cacheamos cuando la resolución tiene éxito.
    """
    global _token_cache
    if _token_cache:
        return _token_cache
    tok = os.getenv("BLENDER_TOKEN") or os.getenv("BLENDER_MCP_TOKEN") or ""
    if not tok:
        try:
            p = _token_file_path()
            if p.exists():
                tok = p.read_text(encoding="utf-8").strip()
        except Exception:
            tok = ""
    if tok:
        _token_cache = tok
    return tok


class BlenderConnection:
    def __init__(self, host=SOCKET_HOST, port=SOCKET_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self._lock = threading.Lock()

    def connect(self):
        if self.sock:
            return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10.0)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Blender: {e}")
            self.sock = None
            return False

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def send_command(self, cmd_type, params=None):
        # Serializa petición/respuesta: un socket compartido sin lock puede
        # intercalar sendall/recv entre hilos y cruzar respuestas.
        with self._lock:
            return self._send_command_locked(cmd_type, params)

    def _send_command_locked(self, cmd_type, params=None):
        if not self.sock and not self.connect():
            raise ConnectionError("No se pudo conectar con Blender")
        cmd = {"command": cmd_type, "args": params or {}}
        token = get_socket_token()
        if token:
            cmd["token"] = token
        try:
            self.sock.sendall(json.dumps(cmd).encode("utf-8"))
            self.sock.settimeout(30.0 if cmd_type == "ping" else 180.0)
            buffer = b""
            while True:
                chunk = self.sock.recv(65536)
                if not chunk:
                    self.disconnect()
                    break
                buffer += chunk
                try:
                    resp = json.loads(buffer.decode("utf-8"))
                    if isinstance(resp, dict) and resp.get("status") == "error":
                        self.disconnect()
                        raise ConnectionError(
                            f"Blender rechazó el comando: {resp.get('message', 'error desconocido')}"
                        )
                    return resp.get("result", {})
                except json.JSONDecodeError:
                    continue
            raise Exception("Sin respuesta de Blender")
        except (OSError, ConnectionError, BrokenPipeError):
            self.disconnect()
            raise
        except TimeoutError:
            self.disconnect()
            raise Exception("Tiempo de espera agotado con Blender")


def get_blender():
    global _connection
    with _connection_lock:
        if _connection is None:
            _connection = BlenderConnection()
        if not _connection.sock:
            _connection.connect()
        return _connection
