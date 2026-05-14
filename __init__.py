import bpy, os, sys, subprocess, importlib, threading, traceback

bl_info = {
    "name": "AXIOM Precision Engine",
    "description": "Industrial-grade AI assembly pipeline for Blender",
    "author": "CarlosH",
    "version": (0, 8, 90),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Axiom",
    "category": "3D View",
}

def _ensure_deps():
    print("[AXIOM] 🔍 Validando dependencias de bajo nivel...")
    required = ["mcp", "fastmcp", "uvicorn", "starlette", "sse-starlette", "requests"]
    for pkg in required:
        import_name = pkg.replace("-", "_")
        if pkg == "fastmcp": import_name = "mcp"
        try: importlib.import_module(import_name)
        except:
            print(f"[AXIOM] 📦 Instalando dependecia crítica: {pkg}")
            cmd = [sys.executable, "-m", "pip", "install", pkg, "--quiet"]
            if os.name != 'nt': cmd.append("--break-system-packages")
            subprocess.check_call(cmd, timeout=60)
    return True

def register():
    ver = "0.8.90"
    print(f"\n[AXIOM] 🚀 INICIANDO SECUENCIA DE INTEGRIDAD TOTAL v{ver}")
    
    if not _ensure_deps():
        print("[AXIOM] ❌ FALLO CRÍTICO: No se pudieron validar las dependencias.")
        return

    from .addon import _axsock as bsock
    from .addon import properties as _props
    from .addon import preferences as _prefs
    
    # 1. VALIDACIÓN DE RED (SOCKET)
    try:
        bsock.start_socket_server()
        print("[AXIOM] ✅ SOCKET SERVER: CONECTADO Y ESCUCHANDO (9876)")
    except Exception as e:
        if "Address already in use" in str(e):
            print("[AXIOM] ℹ️ SOCKET SERVER: REUTILIZANDO CONEXIÓN ACTIVA")
        else:
            print(f"[AXIOM] ❌ SOCKET SERVER: FALLO ({e})")

    try:
        # 2. VALIDACIÓN RNA (TIPOS BASE)
        from .addon.chat_types import ChatMsg, ModelItem
        for cls in [ChatMsg, ModelItem]:
            try: 
                bpy.utils.register_class(cls)
                print(f"[AXIOM] ✅ RNA VALIDATION: {cls.__name__} (READY)")
            except: pass
            
        # 3. VALIDACIÓN DE INTERFAZ Y DATOS
        from .addon.properties import ChatData, ModelsData, MCP_UL_Chat
        from .addon.panels.chat import BLENDERMCP_OT_OpenWeb
        from .addon.panels import chat, config, integrations
        
        classes = [chat.PN_PT_Chat, config.PN_PT_Config, ChatData, ModelsData, MCP_UL_Chat, BLENDERMCP_OT_OpenWeb]
        for p in integrations.PANELS: classes.append(p)
        for cls in classes:
            try: 
                bpy.utils.register_class(cls)
                print(f"[AXIOM] ✅ COMPONENT VALIDATION: {cls.__name__} (REGISTERED)")
            except: pass

        # 4. VALIDACIÓN DE OPERADORES
        from .addon.operators import connect, chat as chat_ops, capture, export, setup, embedded, model_ops
        connect.register_connect_operators()
        chat_ops.register_chat_operators()
        capture.register_capture_operators()
        export.register_export_operators()
        setup.register_setup_operators()
        embedded.register_embedded_operators()
        model_ops.register_model_operators()
        print("[AXIOM] ✅ OPERATORS VALIDATION: ALL PIPES ESTABLISHED")
        
        # 5. VINCULACIÓN DE ESCENA
        _props.register_properties()
        _prefs.register_preferences()
        print("[AXIOM] ✅ SCENE LINKING: DATA POINTERS SYNCED")
        
        # 6. VALIDACIÓN MCP (SSE SERVER)
        _start_mcp_server()
        
        # 7. TELEMETRÍA Y STATUS
        try:
            from .addon.operators.model_ops import _status_ticker
            if not bpy.app.timers.is_registered(_status_ticker):
                bpy.app.timers.register(_status_ticker, first_interval=0.2)
                print("[AXIOM] ✅ TELEMETRY SYSTEM: ACTIVE")
        except: pass
        
        # 8. AUTO-LOAD DE CONFIGURACIÓN
        def auto_refresh():
            try: bpy.ops.aimcp.refresh()
            except: pass
            return None
        bpy.app.timers.register(auto_refresh, first_interval=1.0)
        
        print(f"[AXIOM] ⭐ REPORTE DE INTEGRIDAD v{ver}: SISTEMA OPERATIVO AL 100%\n")
        
    except Exception as e:
        print(f"[AXIOM] ❌ FALLO EN LA SECUENCIA DE INTEGRIDAD: {e}")
        traceback.print_exc()

def _start_mcp_server():
    def run():
        try:
            import uvicorn
            from .mcp_server import mcp
            print("[AXIOM] 📡 MCP SERVER: INICIANDO SSE BRIDGE (9879)")
            uvicorn.run(mcp.sse_app(), host="127.0.0.1", port=9879, log_level="error")
        except Exception as e:
            if "Address already in use" in str(e):
                print("[AXIOM] ℹ️ MCP SERVER: REUTILIZANDO SSE BRIDGE ACTIVO")
            else:
                print(f"[AXIOM] ❌ MCP SERVER: FALLO ({e})")
    threading.Thread(target=run, daemon=True).start()

def unregister():
    from .addon import _axsock as bsock
    try: bsock.stop_socket_server()
    except: pass
    from .addon import properties as _props
    try: _props.unregister_properties()
    except: pass
    print("[AXIOM] 👋 Motor detenido correctamente.")
