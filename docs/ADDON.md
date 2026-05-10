# Addon de Blender — blender-mcp

El addon permite chatear con la IA directamente desde Blender, sin cambiar de programa.

---

## Instalación

Ver [INSTALL.md](INSTALL.md#instalación-del-addon-de-blender).

---

## Uso

### 1. Conectar

1. Abre Blender
2. En el viewport 3D, presiona `N` para abrir el sidebar
3. Ve a la pestaña `🤖 AI`
4. Click **Connect**

### 2. Chatear

Escribe en el campo de texto y presiona Enter. Ejemplos:

```
"crea una mesa redonda de 150cm"
"agrega 4 sillas alrededor"
"color roble oscuro para la mesa"
"exporta a models/mi_mesa.glb"
```

### 3. Capturar escena

Click **📷 Capture Scene** para enviar la escena actual + screenshot a la IA.

Útil cuando ya tienes un proyecto abierto y quieres modificarlo:
1. Abres tu proyecto
2. Capture Scene
3. "cambia el color de la silla a rojo"
4. La IA modifica solo lo necesario

### 4. Exportar

Click **📤 Export to GLB** para exportar la escena actual.

---

## Botones del panel

| Botón | Atajo | Función |
|-------|-------|---------|
| **Connect** | — | Conecta al MCP server |
| **Disconnect** | — | Desconecta |
| **📷 Capture Scene** | — | Envía escena + screenshot a la IA |
| **📤 Export to GLB** | — | Exporta a ~/blender-mcp/models/ |

---

## Solución de problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| No aparece el panel | Addon no activado | Preferences → Add-ons → buscar AI Assistant |
| No conecta | MCP server no running | `python server.py --mode gui` en terminal |
| Chat no responde | Server desconectado | Click Connect en el panel |
| Export falla | Permisos | Asegura que ~/blender-mcp/models/ existe |
