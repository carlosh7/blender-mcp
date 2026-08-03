"""
blender-mcp-ultra — Network Infrastructure
Socket server/client and connection pool.
"""
import json
import socket
import ssl
import threading
import time
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass


@dataclass
class ConnectionConfig:
    host: str = "localhost"
    port: int = 9876
    timeout: float = 30.0
    max_retries: int = 3
    use_tls: bool = False
    certfile: Optional[str] = None
    keyfile: Optional[str] = None


class ConnectionPool:
    """Thread-safe connection pool."""
    
    def __init__(self, config: ConnectionConfig, max_connections: int = 5):
        self.config = config
        self.max_connections = max_connections
        self._pool = []
        self._lock = threading.Lock()
        self._created = 0
    
    def get(self) -> 'BlenderConnection':
        with self._lock:
            if self._pool:
                return self._pool.pop()
            if self._created < self.max_connections:
                self._created += 1
                return BlenderConnection(self.config)
            raise Exception("Connection pool exhausted")
    
    def release(self, conn: 'BlenderConnection'):
        with self._lock:
            if len(self._pool) < self.max_connections and conn.is_alive():
                self._pool.append(conn)
            else:
                conn.close()
                self._created -= 1
    
    def close_all(self):
        with self._lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()
            self._created = 0


class BlenderConnection:
    """TCP connection to Blender."""
    
    def __init__(self, config: ConnectionConfig = None):
        self.config = config or ConnectionConfig()
        self._socket = None
        self._lock = threading.Lock()
    
    def connect(self) -> bool:
        try:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_socket.settimeout(self.config.timeout)
            
            # Apply TLS if configured
            if self.config.use_tls:
                context = ssl.create_default_context()
                if self.config.certfile:
                    context.load_cert_chain(self.config.certfile, self.config.keyfile)
                self._socket = context.wrap_socket(raw_socket, server_hostname=self.config.host)
            else:
                self._socket = raw_socket
            
            self._socket.connect((self.config.host, self.config.port))
            return True
        except Exception:
            self._socket = None
            return False
    
    def close(self):
        if self._socket:
            try: self._socket.close()
            except: pass
            self._socket = None
    
    def is_alive(self) -> bool:
        if not self._socket: return False
        try:
            self._socket.sendall(b'')
            return True
        except:
            return False
    
    def send_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        with self._lock:
            if not self._socket:
                if not self.connect():
                    raise ConnectionError("Cannot connect to Blender")
            
            cmd = {"command": command, "params": params or {}}
            self._socket.sendall(json.dumps(cmd).encode('utf-8'))
            
            buffer = b''
            while True:
                chunk = self._socket.recv(65536)
                if not chunk:
                    self.close()
                    raise ConnectionError("Connection closed")
                buffer += chunk
                try:
                    return json.loads(buffer.decode('utf-8'))
                except json.JSONDecodeError:
                    continue
    
    def execute_code(self, code: str) -> str:
        result = self.send_command("execute_code", {"code": code})
        return result.get("output", "")
    
    def get_scene_info(self) -> Dict[str, Any]:
        return self.send_command("get_scene_info")


class SocketServer:
    """TCP socket server."""
    
    def __init__(self, host: str = "localhost", port: int = 9876, use_tls: bool = False,
                 certfile: str = None, keyfile: str = None):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.certfile = certfile
        self.keyfile = keyfile
        self._server_socket = None
        self._running = False
        self._handlers: Dict[str, Callable] = {}
        self._thread = None
    
    def register_handler(self, command: str, handler: Callable):
        self._handlers[command] = handler
    
    def start(self) -> bool:
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Apply TLS if configured
            if self.use_tls and self.certfile:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(self.certfile, self.keyfile)
                self._server_socket = context.wrap_socket(self._server_socket, server_side=True)
            
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(5)
            self._server_socket.settimeout(1.0)
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
            return True
        except Exception:
            return False
    
    def stop(self):
        self._running = False
        if self._server_socket:
            try: self._server_socket.close()
            except: pass
    
    def _loop(self):
        while self._running:
            try:
                client, addr = self._server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()
            except socket.timeout:
                continue
            except: break
    
    def _handle_client(self, client: socket.socket):
        try:
            data = client.recv(1048576)
            if data:
                cmd = json.loads(data.decode('utf-8'))
                command = cmd.get("command", "")
                params = cmd.get("params", {})
                
                if command in self._handlers:
                    result = self._handlers[command](**params)
                else:
                    result = {"error": f"Unknown command: {command}"}
                
                client.sendall(json.dumps(result).encode('utf-8'))
        except Exception as e:
            try:
                client.sendall(json.dumps({"error": str(e)}).encode('utf-8'))
            except: pass
        finally:
            client.close()
