"""
blender-mcp — Blender Socket Connection (shared module)
Avoids circular imports by providing a single connection entry point.
"""
import json, socket, os, time, logging

logger = logging.getLogger("blender-mcp")

SOCKET_HOST = os.getenv("BLENDER_HOST", "localhost")
SOCKET_PORT = int(os.getenv("BLENDER_PORT", "9876"))

_connection = None


class BlenderConnection:
    def __init__(self, host=SOCKET_HOST, port=SOCKET_PORT):
        self.host = host
        self.port = port
        self.sock = None

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
            except:
                pass
            self.sock = None

    def send_command(self, cmd_type, params=None):
        if not self.sock and not self.connect():
            raise ConnectionError("No se pudo conectar con Blender")
        cmd = {"command": cmd_type, "args": params or {}}
        try:
            self.sock.sendall(json.dumps(cmd).encode('utf-8'))
            self.sock.settimeout(30.0 if cmd_type == "ping" else 180.0)
            buffer = b''
            while True:
                chunk = self.sock.recv(65536)
                if not chunk:
                    self.disconnect()
                    break
                buffer += chunk
                try:
                    resp = json.loads(buffer.decode('utf-8'))
                    return resp.get("result", {})
                except json.JSONDecodeError:
                    continue
            raise Exception("Sin respuesta de Blender")
        except (socket.error, ConnectionError, BrokenPipeError):
            self.disconnect()
            raise
        except socket.timeout:
            self.disconnect()
            raise Exception("Tiempo de espera agotado con Blender")


def get_blender():
    global _connection
    if _connection is None:
        _connection = BlenderConnection()
    if not _connection.sock:
        _connection.connect()
    return _connection
