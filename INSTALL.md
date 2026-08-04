# blender-mcp-ultra — Instalación y Uso

## Requisitos

| Componente | Versión mínima | Verificar |
|------------|----------------|-----------|
| Blender | 4.0.0+ | `blender --version` |
| Python | 3.10+ | `python3 --version` |
| Opcional: Ollama | Última | `ollama --version` |
| Opcional: opencode | Última | `opencode --version` |

---

## Instalación del Addon

### Opción 1: Desde disco (recomendado)

1. **Descargar o clonar el repositorio:**
```bash
git clone https://github.com/carlosh7/blender-mcp-ultra.git
cd blender-mcp-ultra
```

2. **Crear el zip del addon:**
```bash
mkdir -p /tmp/blender_addon
cp -r addon/* /tmp/blender_addon/
cd /tmp && zip -r blender_mcp_ultra.zip blender_addon/
```

3. **En Blender:**
   - Ve a **Edit → Preferences → Get Extensions** (o **Add-ons**)
   - Haz clic en **"Install from Disk..."**
   - Selecciona `/tmp/blender_mcp_ultra.zip`
   - Activa el checkbox del addon **"blender-mcp-ultra"**

4. **Verificar:**
   - En la vista 3D, presiona **N** para abrir el panel lateral
   - Busca la pestaña **"MCP"**
   - Deberías ver **"Status: Connected (auto)"** en puerto 9876

### Opción 2: Copia directa (desarrollo)

```bash
# Copiar el addon al directorio de extensiones de Blender
cp -r addon/ ~/.config/blender/4.2/extensions/user_default/blender_mcp_ultra/
```

---

## Variables de Entorno (Opcional)

Para configuración personalizada, define estas variables **antes** de abrir Blender:

```bash
# Blender Socket (puerto de comunicación)
export BLENDER_HOST=localhost      # default: localhost
export BLENDER_PORT=9876          # default: 9876

# Ollama (LLM local)
export OLLAMA_BASE_URL=http://localhost:11434

# opencode (MCP SSE)
export OPENCODE_SSE_URL=http://localhost:45677/sse
```

En **Linux/macOS**, añade al `~/.bashrc` o `~/.zshrc`:
```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OPENCODE_SSE_URL=http://localhost:45677/sse
```

En **Windows** (PowerShell):
```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OPENCODE_SSE_URL = "http://localhost:45677/sse"
```

---

## Uso Básico

### 1. Conexión con Blender

El addon inicia automáticamente un servidor TCP en el puerto **9876** al activarse.

**Verificar conexión:**
```python
import socket, json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect(('localhost', 9876))
sock.send(json.dumps({'command': 'ping', 'params': {}}).encode() + b'\n')
response = sock.recv(4096).decode()
print(response)
# → {"status": "success", "result": {"pong": true, "time": ...}}
sock.close()
```

### 2. Ejecutar código en Blender

```python
import socket, json, time

def send_command(cmd, params=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(('localhost', 9876))
    payload = json.dumps({'command': cmd, 'params': params or {}}) + '\n'
    sock.send(payload.encode())
    response = b''
    deadline = time.time() + 25
    while time.time() < deadline:
        try:
            chunk = sock.recv(65536)
            if chunk:
                response += chunk
                if b'\n' in response:
                    break
        except socket.timeout:
            continue
    sock.close()
    data = json.loads(response.decode().strip())
    return data.get('result', data)

# Crear un cubo
result = send_command('execute_code', {'code': '''
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
print("Cubo creado")
'''})
print(result)
# → {'output': 'Cubo creado\n'}
```

---

## Ejemplos de Uso

### Ejemplo 1: Escena con materiales

```python
import socket, json, time

def run(code):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect(('localhost', 9876))
    s.send(json.dumps({'command': 'execute_code', 'params': {'code': code}}).encode() + b'\n')
    r = b''
    dl = time.time() + 25
    while time.time() < dl:
        try:
            c = s.recv(65536)
            if c:
                r += c
                if b'\n' in r: break
        except: continue
    s.close()
    return json.loads(r.decode().strip()).get('result', {})

# Crear cubo rojo
run('''
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(-3, 0, 1))
cube = bpy.context.active_object
mat = bpy.data.materials.new("Rojo")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.05, 0.05, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.3
cube.data.materials.append(mat)
print(f"Cubo: {cube.name}")
''')

# Crear esfera azul metálica
run('''
import bpy
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.active_object
mat = bpy.data.materials.new("Azul")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.15, 0.8, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.9
sphere.data.materials.append(mat)
print(f"Esfera: {sphere.name}")
''')

# Crear plano suelo
run('''
import bpy
bpy.ops.mesh.primitive_plane_add(size=20)
plane = bpy.context.active_object
mat = bpy.data.materials.new("Suelo")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1)
plane.data.materials.append(mat)
print("Suelo creado")
''')
```

### Ejemplo 2: Animación

```python
run('''
import bpy, math

# Configurar escena
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
scene.render.fps = 24

# Animar cubo: saltar
cube = bpy.data.objects["Cube"]
cube.location = (-3, 0, 1)
cube.keyframe_insert("location", frame=1)

cube.location = (0, 0, 4)
cube.keyframe_insert("location", frame=15)

cube.location = (3, 0, 1)
cube.keyframe_insert("location", frame=30)

cube.location = (-3, 0, 1)
cube.keyframe_insert("location", frame=60)

print("Animación creada: 60 frames")
''')
```

### Ejemplo 3: Geometry Nodes (Scatter)

```python
run('''
import bpy

# Crear plano para scatter
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 5, 0))
scatter = bpy.context.active_object
scatter.name = "ScatterPlane"

# Agregar Geometry Nodes
mod = scatter.modifiers.new("Scatter", "NODES")
ng = bpy.data.node_groups.new("ScatterGN", "GeometryNodeTree")
mod.node_group = ng

nodes = ng.nodes
links = ng.links

inp = nodes.new("NodeGroupInput")
inp.location = (-400, 0)

out = nodes.new("NodeGroupOutput")
out.location = (400, 0)

dist = nodes.new("GeometryNodeDistributePointsOnFaces")
dist.location = (-100, 0)
dist.inputs["Density"].default_value = 10.0

inst = nodes.new("GeometryNodeInstanceOnPoints")
inst.location = (100, 0)

# Crear objeto instancia
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1)
iso = bpy.context.active_object
iso.hide_viewport = True

oi = nodes.new("GeometryNodeObjectInfo")
oi.location = (-100, -200)
oi.inputs["Object"].default_value = iso

# Conectar nodos
links.new(inp.outputs[0], dist.inputs["Mesh"])
links.new(dist.outputs["Points"], inst.inputs["Points"])
links.new(oi.outputs["Geometry"], inst.inputs["Instance"])
links.new(inst.outputs["Instances"], out.inputs[0])

print(f"GeoNodes: {ng.name}")
''')
```

### Ejemplo 4: Shader Nodes (Material Ladrillo)

```python
run('''
import bpy

# Crear pared
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, -6, 1))
wall = bpy.context.active_object
wall.name = "BrickWall"

# Crear material
mat = bpy.data.materials.new("Brick")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Limpiar nodos
for n in nodes:
    nodes.remove(n)

# Crear nodos
output = nodes.new("ShaderNodeOutputMaterial")
output.location = (600, 0)

bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (300, 0)

brick = nodes.new("ShaderNodeTexBrick")
brick.location = (-200, 100)

# Conectar
links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

wall.data.materials.append(mat)
print(f"Material ladrillo: {mat.name}")
''')
```

### Ejemplo 5: Obtener info de la escena

```python
result = send_command('get_scene_info')
print(f"Escena: {result['name']}")
print(f"Objetos: {result['object_count']}")
for obj in result['objects']:
    print(f"  - {obj['name']} ({obj['type']})")
```

---

## Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `ping` | Verificar conexión | `{'command': 'ping'}` |
| `execute_code` | Ejecutar código Python | `{'command': 'execute_code', 'params': {'code': 'import bpy; ...'}}` |
| `get_scene_info` | Info de la escena | `{'command': 'get_scene_info'}` |
| `get_viewport_screenshot` | Captura del viewport | `{'command': 'get_viewport_screenshot'}` |
| `search_api_docs` | Buscar docs de API | `{'command': 'search_api_docs', 'params': {'query': 'mesh'}}` |

---

## Troubleshooting

### Error: "No module named 'infrastructure'"

**Causa:** El addon intenta importar módulos de `src/` que no existen dentro de Blender.

**Solución:** Asegúrate de usar el addon de `addon/` (self-contained), no el de `addon_package/`.

### Error: "Connection refused" en puerto 9876

**Causa:** El servidor socket no está activo.

**Solución:**
1. Verifica que el addon esté activo en Blender (Preferences → Add-ons)
2. En el panel MCP, haz clic en "Start Server"
3. Verifica el puerto: `ss -tlnp | grep 9876`

### Error: "AXIOM TIMEOUT"

**Causa:** La ejecución de código toma más de 10 segundos.

**Solución:**
- Divide el código en partes más pequeñas
- O aumenta el timeout en `addon/_axsock.py`: `signal.alarm(20)`

### Blender no encuentra el addon

**Solución:**
1. Ve a **Edit → Preferences → Get Extensions**
2. Haz clic en **"Install from Disk..."**
3. Selecciona el archivo `.zip` del addon
4. Activa el checkbox

### El render no funciona

**Causa:** En Blender 4.2+, el motor EEVEE se llama `BLENDER_EEVEE_NEXT`.

```python
# Correcto para Blender 4.2+
scene.render.engine = "BLENDER_EEVEE_NEXT"

# No usar (causa error)
scene.render.engine = "BLENDER_EEVEE"
```

---

## Desarrollo

### Ejecutar tests

```bash
# Suite completa
pytest

# Solo tests de handlers (sin Blender)
pytest tests/test_handlers.py tests/unit/test_tools.py -v

# Tests que requieren Blender activo
pytest tests/test_e2e_socket.py -v
```

### Crear zip del addon

```bash
mkdir -p /tmp/blender_addon
cp -r addon/* /tmp/blender_addon/
find /tmp/blender_addon -name "__pycache__" -exec rm -rf {} +
cd /tmp && zip -r blender_mcp_ultra.zip blender_addon/
```

### Variables de entorno para desarrollo

```bash
export BLENDER_HOST=localhost
export BLENDER_PORT=9876
export OLLAMA_BASE_URL=http://localhost:11434
export OPENCODE_SSE_URL=http://localhost:45677/sse
```

---

## Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.
