# blender-mcp v0.7.0

**AI-powered 3D model generation via Blender + MCP protocol.**

Crea y edita modelos 3D desde lenguaje natural usando Blender, controlado por IA vía MCP (Model Context Protocol).

---

## ✨ Capacidades

| Capacidad | Descripción |
|-----------|-------------|
| **Generar modelos** | Describe lo que quieres y el modelo aparece |
| **Editar escenas existentes** | Abre tu proyecto en Blender y pide cambios |
| **Ver en vivo** | Blender con GUI para ver los cambios instantáneamente |
| **Exportar GLTF/GLB** | Modelos listos para web, Three.js, Unity, etc. |
| **Integración check-3d-planner** | Los modelos se copian directamente al editor de planos |
| **Multi-plataforma** | Windows y Linux |

---

## 🚀 Instalación rápida

### Requisitos

- **Blender 4.0+** ([Descargar](https://www.blender.org/download/))
- **Python 3.10+** ([Descargar](https://python.org))
- **Git** ([Descargar](https://git-scm.com/))

### Linux

```bash
# 1. Clonar
git clone https://github.com/carlosh7/blender-mcp.git
cd blender-mcp

# 2. Verificar requisitos
python3 check.py

# 3. Instalar dependencias
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Iniciar servidor
python server.py --mode standalone
```

### Windows

```powershell
# 1. Clonar
git clone https://github.com/carlosh7/blender-mcp.git
cd blender-mcp

# 2. Verificar requisitos
python check.py
# O: .\check.ps1

# 3. Instalar dependencias
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 4. Iniciar servidor
python server.py --mode standalone
```

---

## 🎮 Modos de uso

### 📦 Modo standalone (generación rápida)

```bash
python server.py --mode standalone
```

El servidor escucha comandos vía MCP. La IA puede generar modelos bajo demanda.

### 🔗 Modo check (integración con check-3d-planner)

```bash
python server.py --mode check --check-path ../check-3d-planner/public/models
```

Los modelos generados se copian automáticamente al directorio del editor 3D.

### 👁️ Modo GUI (ver en vivo)

```bash
python server.py --mode gui
```

Blender se abre con interfaz gráfica para que veas los modelos en tiempo real.

---

## 🧩 Addon de Blender

Para interactuar con la IA sin salir de Blender:

1. Copia la carpeta `addon/` a los addons de Blender:
   - **Linux:** `~/.config/blender/4.0/scripts/addons/ai_assistant/`
   - **Windows:** `%APPDATA%\Blender Foundation\Blender\4.0\scripts\addons\ai_assistant\`
2. En Blender: `Edit → Preferences → Add-ons → buscar "AI Assistant"`
3. Actívalo
4. Panel en el sidebar de Blender → pestaña `🤖 AI` (abre el sidebar con `N`) 

---

## 💬 Ejemplos de uso con IA

```
Tú: "crea una mesa redonda de 150cm con color roble oscuro"
Tú: "agrega 6 sillas alrededor de la mesa"
Tú: "el pie de la mesa es muy grueso, redúcelo a la mitad"
Tú: "exporta como .glb a la carpeta del proyecto"
```

---

## 🔧 Comandos del servidor

| Comando | Descripción |
|---------|-------------|
| `generate-model` | Genera un modelo 3D (tipo, nombre, color, material, escala) |
| `list-models` | Lista todos los tipos de modelos disponibles |
| `system-info` | Muestra información del sistema (SO, versiones, disco) |

---

## 📁 Estructura del proyecto

```
blender-mcp/
├── server.py              ← MCP Server principal
├── config.py              ← Detección automática Win/Linux
├── check.py               ← Validador de requisitos
├── check.ps1              ← Validador Windows PowerShell
├── check.sh               ← Validador Linux Bash
├── requirements.txt       ← Dependencias Python
├── opencode_example.json  ← Config para opencode
├── generators/            ← Scripts de generación por categoría
├── addon/                 ← Addon para Blender
│   └── __init__.py        ← Panel de chat + conexión MCP
├── models/                ← Modelos generados (.glb)
├── examples/              ← Ejemplos de uso
├── docs/                  ← Documentación
└── LICENSE                ← MIT
```

---

## 🤝 Integración con opencode

Para usar con [opencode](https://opencode.ai):

1. Copia `opencode_example.json` a `~/.config/opencode/mcp.json`
2. Ajusta la ruta de `args` a tu instalación de blender-mcp
3. En el chat de opencode, pide modelos directamente

---

## 📄 Licencia

MIT — Ver [LICENSE](LICENSE)
