# blender-mcp — Socket server for Blender (ahujasid-compatible)
# Runs inside Blender, listens on port 9876 for JSON commands via TCP socket.
import bpy, json, socket, threading, time, io, traceback
import sys, os
from contextlib import redirect_stdout

SOCKET_PORT = 9876
_socket_server = None
_chat_queue = []
_chat_responses = {}
_chat_lock = threading.Lock()
mcp_last_ping = 0  # timestamp of last ping from MCP server
mcp_connected = False  # true if ping received in last 15s

class BlenderSocketServer:
    """TCP socket server inside Blender for receiving MCP commands."""

    def __init__(self, host='localhost', port=SOCKET_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.sock = None
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            self.sock.settimeout(1.0)
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print(f"[BLENDER SOCKET] Server on port {self.port}")
        except Exception as e:
            print(f"[BLENDER SOCKET] Failed: {e}")
            self.stop()

    def stop(self):
        self.running = False
        if self.sock:
            try: self.sock.close()
            except: pass
            self.sock = None

    def _loop(self):
        while self.running:
            try:
                client, addr = self.sock.accept()
                threading.Thread(target=self._handle, args=(client,), daemon=True).start()
            except socket.timeout:
                continue
            except: pass

    def _handle(self, client):
        buffer = b''
        try:
            while self.running:
                data = client.recv(65536)
                if not data:
                    break
                buffer += data
                try:
                    cmd = json.loads(buffer.decode('utf-8'))
                    buffer = b''
                    def execute():
                        try:
                            resp = self._execute(cmd)
                            client.sendall(json.dumps(resp).encode('utf-8'))
                        except:
                            client.sendall(json.dumps({"status": "error", "message": traceback.format_exc()}).encode('utf-8'))
                        return None
                    bpy.app.timers.register(execute, first_interval=0.0)
                except json.JSONDecodeError:
                    pass
        except: pass
        finally:
            try: client.close()
            except: pass

    def _execute(self, cmd):
        cmd_type = cmd.get("type")
        params = cmd.get("params", {})
        handler = getattr(self, f"cmd_{cmd_type}", None)
        if not handler:
            return {"status": "error", "message": f"Unknown command: {cmd_type}"}
        try:
            result = handler(**params)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

    def cmd_get_scene_info(self):
        info = {"name": bpy.context.scene.name, "object_count": len(bpy.context.scene.objects), "objects": []}
        for i, obj in enumerate(bpy.context.scene.objects):
            if i >= 20: break
            info["objects"].append({
                "name": obj.name, "type": obj.type,
                "location": [round(float(obj.location.x), 2), round(float(obj.location.y), 2), round(float(obj.location.z), 2)],
            })
        return info

    def cmd_ping(self):
        global mcp_last_ping, mcp_connected
        mcp_last_ping = time.time()
        mcp_connected = True
        return {"pong": True, "time": mcp_last_ping}

    def cmd_execute_code(self, code=""):
        ns = {"bpy": bpy, "C": bpy.context, "D": bpy.data, "ops": bpy.ops}
        buf = io.StringIO()
        with redirect_stdout(buf):
            exec(code, ns)
        return {"output": buf.getvalue()}

    def cmd_chat_send(self, message="", model=""):
        with _chat_lock:
            mid = str(len(_chat_queue))
            _chat_queue.append({"id": mid, "message": message, "timestamp": time.time()})
            return {"message_id": mid}

    def cmd_read_chat(self):
        with _chat_lock:
            return {"messages": list(_chat_queue)}

    def cmd_respond_chat(self, message_id="", response=""):
        with _chat_lock:
            _chat_responses[message_id] = response
            _chat_queue[:] = [m for m in _chat_queue if m["id"] != message_id]
        return {"success": True}

    def cmd_poll_response(self, message_id=""):
        with _chat_lock:
            resp = _chat_responses.pop(message_id, None)
            if resp:
                return {"status": "done", "response": resp}
            return {"status": "pending"}


def start_socket_server():
    global _socket_server
    if _socket_server is None:
        _socket_server = BlenderSocketServer()
    if not _socket_server.running:
        _socket_server.start()
    return _socket_server

def stop_socket_server():
    global _socket_server
    if _socket_server:
        _socket_server.stop()
        _socket_server = None
