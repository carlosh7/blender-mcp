# Instalación — blender-mcp

Guía de instalación paso a paso para Windows y Linux.

---

## Prerrequisitos

| Componente | Linux | Windows |
|------------|-------|---------|
| **Blender 4.0+** | `sudo apt install blender` | [blender.org](https://www.blender.org/download/) |
| **Python 3.10+** | `sudo apt install python3 python3-pip` | [python.org](https://python.org) |
| **Git** | `sudo apt install git` | [git-scm.com](https://git-scm.com) |

---

## Paso 1: Verificar requisitos

```bash
# Linux
python3 check.py

# Windows
python check.py
# O PowerShell:
.\check.ps1
```

El script te dirá qué falta y cómo instalarlo.

---

## Paso 2: Clonar

```bash
git clone https://github.com/carlosh7/blender-mcp.git
cd blender-mcp
```

---

## Paso 3: Entorno virtual

```bash
# Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Paso 4: Probar

```bash
# Verificar configuración
python check.py

# Iniciar servidor
python server.py --mode standalone
```

Si ves "Ready. Connect via MCP stdio or WebSocket.", está funcionando.

---

## Paso 5: Probar generación de modelo

Desde otra terminal:

```bash
# Linux
python3 -c "
from mcp.client.stdio import stdio_client
# El cliente MCP se conecta al server y puede llamar generate-model
print('MCP client ready')
"

# O simplemente usa opencode con la configuración de ejemplo
```

---

## Instalación del addon de Blender

1. Copia la carpeta `addon/` al directorio de addons de Blender:

   **Linux:**
   ```bash
   mkdir -p ~/.config/blender/4.0/scripts/addons/ai_assistant
   cp -r addon/* ~/.config/blender/4.0/scripts/addons/ai_assistant/
   ```

   **Windows:**
   ```powershell
   mkdir "%APPDATA%\Blender Foundation\Blender\4.0\scripts\addons\ai_assistant" -Force
   copy addon\* "%APPDATA%\Blender Foundation\Blender\4.0\scripts\addons\ai_assistant\"
   ```

2. Abre Blender
3. `Edit → Preferences → Add-ons`
4. Busca "AI Assistant"
5. Activa el checkbox
6. En el viewport 3D, presiona `N` para abrir el sidebar
7. Ve a la pestaña `🤖 AI`

---

## Configurar con opencode

Para que el AI assistant (yo) pueda llamar al servidor Blender:

1. Copia `opencode_example.json` a la configuración de opencode:

   **Linux:**
   ```bash
   mkdir -p ~/.config/opencode
   cp opencode_example.json ~/.config/opencode/mcp.json
   ```

   **Windows:**
   ```powershell
   mkdir ~\.config\opencode -Force
   copy opencode_example.json ~\.config\opencode\mcp.json
   ```

2. Edita la ruta en `mcp.json` para que apunte a tu instalación de `blender-mcp/server.py`
3. Reinicia opencode
4. Ya puedes pedir modelos directamente: "crea una silla plegable"

---

## Verificar que todo funciona

```bash
python check.py
# Debe mostrar: ✅✅✅✅ (4 checks pasados)
```
