"""
blender-mcp-ultra — Blender Adapter
Implementation of IBlenderAPI using bpy.
"""
import json
import os
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from core.interfaces import IBlenderAPI
from core.entities import ToolResult, Scene, Object, Material

# Blender is optional - only available inside Blender
try:
    import bpy
    HAS_BPY = True
except ImportError:
    bpy = None
    HAS_BPY = False


class BlenderAdapter(IBlenderAPI):
    """
    Adapter for Blender API.
    
    This adapter communicates with Blender via:
    - Direct bpy access (when running inside Blender)
    - Socket connection (when running externally)
    """
    
    def __init__(self, host: str = "localhost", port: int = 9876):
        """
        Initialize Blender adapter.
        
        Args:
            host: Blender socket server host
            port: Blender socket server port
        """
        self.host = host
        self.port = port
        self._connected = False
        self._socket = None
        self._blender_version = None
    
    def connect(self) -> bool:
        """Connect to Blender instance."""
        if HAS_BPY:
            self._connected = True
            self._blender_version = bpy.app.version_string
            return True
        
        # Try socket connection
        try:
            import socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(10.0)
            self._socket.connect((self.host, self.port))
            self._connected = True
            
            # Get Blender version
            result = self._send_command("ping")
            self._blender_version = result.get("version", "unknown")
            
            return True
        except Exception as e:
            print(f"Failed to connect to Blender: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Blender."""
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
        self._connected = False
    
    def execute_code(self, code: str) -> ToolResult:
        """Execute Python code in Blender."""
        if not self._connected:
            return ToolResult(
                success=False,
                error="Not connected to Blender"
            )
        
        start_time = time.time()
        
        try:
            if HAS_BPY:
                # Execute directly in Blender
                result = self._execute_direct(code)
            else:
                # Execute via socket
                result = self._execute_via_socket(code)
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                success=True,
                data=result,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
    
    def _execute_direct(self, code: str) -> Any:
        """Execute code directly in Blender."""
        # Capture stdout
        import io
        from contextlib import redirect_stdout
        
        buf = io.StringIO()
        with redirect_stdout(buf):
            # Execute in main thread
            bpy.ops.ed.undo_push(message="blender-mcp-ultra")
            compiled = compile(code, "<blender_code>", "exec")
            exec(compiled, {"bpy": bpy, "C": bpy.context, "D": bpy.data})
        
        return buf.getvalue()
    
    def _execute_via_socket(self, code: str) -> Any:
        """Execute code via socket."""
        result = self._send_command("execute_code", {"code": code})
        return result.get("output", "")
    
    def _send_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send command to Blender socket server."""
        if not self._socket:
            raise ConnectionError("Not connected")
        
        cmd = {"command": command, "params": params or {}}
        self._socket.sendall(json.dumps(cmd).encode('utf-8'))
        
        # Receive response
        buffer = b''
        while True:
            chunk = self._socket.recv(65536)
            if not chunk:
                break
            buffer += chunk
            try:
                return json.loads(buffer.decode('utf-8'))
            except json.JSONDecodeError:
                continue
        
        raise Exception("No response from Blender")
    
    def get_scene_info(self) -> Scene:
        """Get current scene information."""
        if not self._connected:
            return Scene(name="unknown", object_count=0)
        
        if HAS_BPY:
            return self._get_scene_info_direct()
        else:
            return self._get_scene_info_via_socket()
    
    def _get_scene_info_direct(self) -> Scene:
        """Get scene info directly from Blender."""
        scene = bpy.context.scene
        objects = []
        
        for obj in scene.objects:
            objects.append(Object(
                name=obj.name,
                type=obj.type,
                location=tuple(obj.location),
                rotation=tuple(obj.rotation_euler),
                scale=tuple(obj.scale),
                dimensions=tuple(obj.dimensions),
            ))
        
        return Scene(
            name=scene.name,
            object_count=len(scene.objects),
            objects=objects,
            camera_count=sum(1 for o in scene.objects if o.type == 'CAMERA'),
            light_count=sum(1 for o in scene.objects if o.type == 'LIGHT'),
        )
    
    def _get_scene_info_via_socket(self) -> Scene:
        """Get scene info via socket."""
        result = self._send_command("get_scene_info")
        return Scene(
            name=result.get("name", "unknown"),
            object_count=result.get("object_count", 0),
            objects=[
                Object(
                    name=obj["name"],
                    type=obj["type"],
                    location=tuple(obj.get("location", [0, 0, 0])),
                )
                for obj in result.get("objects", [])
            ],
        )
    
    def get_object(self, name: str) -> Optional[Object]:
        """Get object by name."""
        if not self._connected:
            return None
        
        if HAS_BPY:
            obj = bpy.data.objects.get(name)
            if obj:
                return Object(
                    name=obj.name,
                    type=obj.type,
                    location=tuple(obj.location),
                    rotation=tuple(obj.rotation_euler),
                    scale=tuple(obj.scale),
                    dimensions=tuple(obj.dimensions),
                )
        return None
    
    def create_object(self, obj_type: str, name: str, **kwargs) -> ToolResult:
        """Create a new object."""
        code = f"""
bpy.ops.object.add(type='{obj_type}', location={kwargs.get('location', (0, 0, 0))})
obj = bpy.context.active_object
obj.name = '{name}'
"""
        return self.execute_code(code)
    
    def delete_object(self, name: str) -> ToolResult:
        """Delete an object."""
        code = f"""
obj = bpy.data.objects.get('{name}')
if obj:
    bpy.data.objects.remove(obj, do_unlink=True)
"""
        return self.execute_code(code)
    
    def create_material(self, name: str, **kwargs) -> ToolResult:
        """Create a new material."""
        color = kwargs.get('color', (0.8, 0.8, 0.8, 1.0))
        code = f"""
mat = bpy.data.materials.new(name='{name}')
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = {color}
bpy.context.object.data.materials.append(mat)
"""
        return self.execute_code(code)
    
    def apply_material(self, object_name: str, material_name: str) -> ToolResult:
        """Apply material to object."""
        code = f"""
obj = bpy.data.objects.get('{object_name}')
mat = bpy.data.materials.get('{material_name}')
if obj and mat:
    obj.data.materials.append(mat)
"""
        return self.execute_code(code)
    
    def search_api_docs(self, query: str) -> Dict[str, Any]:
        """Search Blender API documentation."""
        # Placeholder - will integrate with RST search
        return {
            'query': query,
            'results': [],
            'total': 0,
        }
    
    def get_viewport_screenshot(self) -> ToolResult:
        """Capture viewport screenshot."""
        import tempfile
        filepath = os.path.join(tempfile.gettempdir(), f"blender_mcp_screenshot_{int(time.time())}.png")
        
        code = f"""
bpy.ops.screen.screenshot_area(filepath='{filepath}')
"""
        result = self.execute_code(code)
        
        if result.success:
            result.data = {'filepath': filepath}
        
        return result
    
    def is_connected(self) -> bool:
        """Check if connected to Blender."""
        return self._connected
    
    def get_blender_version(self) -> str:
        """Get Blender version."""
        return self._blender_version or "unknown"
