# Integración de Tablet (Lenovo Tab P12) en Blender MCP

Este documento detalla las estrategias para integrar la tablet Lenovo Tab P12 (TB370FU) con Android 15 / ZUI 17 en el flujo de trabajo de desarrollo y modelado de precisión.

## 1. Monitor Secundario/Terciario en Linux
**Objetivo:** Utilizar la pantalla de 12.7" de la tablet como un monitor inalámbrico adicional para el Asus Zenbook Duo (UX8406MA).

- **Estrategia Técnica:**
  - **Host (Linux):** Configurar **Sunshine** para transmitir una pantalla virtual o una región específica del escritorio.
  - **Cliente (Tablet):** Utilizar **Moonlight** para recibir el streaming con mínima latencia y alta tasa de refresco.
  - **Configuración de Pantalla:** Usar un controlador de pantalla virtual (como `virt-viewer` o configuraciones de X11/Wayland) para extender el escritorio a una resolución nativa de 2944 x 1840.
- **Casos de Uso:**
  - Mantener el log de `mcp_server.py` visible en tiempo real.
  - Visualizar la documentación de la API de Blender mientras se programa.
  - Dedicar la pantalla táctil exclusivamente a los paneles de propiedades de Blender.

## 2. Panel de Control Táctil para Blender MCP
**Objetivo:** Desarrollar una consola de comandos táctil que actúe como control remoto para el servidor MCP y las operaciones de ingeniería en Blender.

- **Estrategia Técnica:**
  - **Backend:** Exponer endpoints adicionales en `http_bridge.py` o crear un microservicio ligero en FastAPI/Flask.
  - **Frontend:** Interfaz web progresiva (PWA) con estética premium (modo oscuro, Electric Cyan) optimizada para la resolución de la tablet.
  - **Comunicación:** Enviar comandos JSON directamente al `agent_host.py` para disparar acciones en Blender.
- **Funcionalidades del Panel:**
  - **Scanner Control:** Iniciar el escaneo de geometría con un solo toque.
  - **Assembly Shortcuts:** Ejecutar el snap de precisión de 27 puntos sin comandos de voz o teclado.
  - **Visual Toggles:** Activar/desactivar la visualización de cajas de colisión (BVH) y anclas de montaje.
  - **Status Monitor:** Barra de progreso y logs resumidos de la ejecución de la IA.

---
*Documento generado por Antigravity para optimizar el ecosistema de hardware del usuario.*
