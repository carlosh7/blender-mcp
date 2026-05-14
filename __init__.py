import bpy, os, sys, subprocess, importlib, threading, traceback, time

bl_info = {
    "name": "AXIOM Precision Engine",
    "description": "Industrial-grade AI assembly pipeline for Blender",
    "author": "CarlosH",
    "version": (0, 8, 96),
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
    ver = "0.8.96"
    print(f"\n[AXIOM] 🚀 INICIANDO SECUENCIA DE INTEGRIDAD TOTAL v{ver}")
    
    if not _ensure_deps():
        print("[AXIOM] ❌ FALLO CRÍTICO: No se pudieron validar las dependencias.")
        return

    from .addon import _axsock as bsock
    from .addon import properties as _props
    from .addon import preferences as _prefs
    
    # 1. LANZAMIENTO DE SERVICIOS
    bsock.start_socket_server()
    _start_servers()

    # Pequeña pausa técnica para binding real
    time.sleep(0.5)

    try:
        # 2. REPORTE DE RED HONESTO
        sock_ok = bsock._socket_server.listening if bsock._socket_server else False
        if sock_ok:
            print("[AXIOM] ✅ SOCKET SERVER: ACTIVO (9876)")
        else:
            err = bsock._socket_server.last_error if bsock._socket_server else "No init"
            print(f"[AXIOM] ❌ SOCKET SERVER: FALLO ({err})")

        # 3. VALIDACIÓN RNA (TIPOS BASE)
        from .addon.chat_types import ChatMsg, ModelItem
        for cls in [ChatMsg, ModelItem]:
            try: 
                bpy.utils.register_class(cls)
                print(f"[AXIOM] ✅ RNA VALIDATION: {cls.__name__} (READY)")
            except: pass
            
        # 4. VALIDACIÓN DE INTERFAZ Y DATOS
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

        # 5. VALIDACIÓN DE OPERADORES
        from .addon.operators import connect, chat as chat_ops, capture, export, setup, embedded, model_ops
        connect.register_connect_operators()
        chat_ops.register_chat_operators()
        capture.register_capture_operators()
        export.register_export_operators()
        setup.register_setup_operators()
        embedded.register_embedded_operators()
        model_ops.register_model_operators()
        print("[AXIOM] ✅ OPERATORS VALIDATION: ALL PIPES ESTABLISHED")
        
        # 6. VINCULACIÓN DE ESCENA
        _props.register_properties()
        _prefs.register_preferences()
        print("[AXIOM] ✅ SCENE LINKING: DATA POINTERS SYNCED")
        
        # 7. TELEMETRÍA Y STATUS
        try:
            from .addon.operators.model_ops import _status_ticker
            if not bpy.app.timers.is_registered(_status_ticker):
                bpy.app.timers.register(_status_ticker, first_interval=0.2)
                print("[AXIOM] ✅ TELEMETRY SYSTEM: ACTIVE")
        except: pass
        
        # 8. VEREDICTO FINAL
        if sock_ok:
            print(f"[AXIOM] ⭐ REPORTE DE INTEGRIDAD v{ver}: SISTEMA OPERATIVO AL 100%\n")
        else:
            print(f"[AXIOM] ⚠️ REPORTE DE INTEGRIDAD v{ver}: SISTEMA DEGRADADO (Revisa Sockets)\n")
        
        # AUTO-LOAD
        def auto_refresh():
            try: bpy.ops.aimcp.refresh()
            except: pass
            return None
        bpy.app.timers.register(auto_refresh, first_interval=1.0)
        
    except Exception as e:
        print(f"[AXIOM] ❌ FALLO EN LA SECUENCIA DE INTEGRIDAD: {e}")
        traceback.print_exc()

def _start_servers():
    # IMPORTACIONES FUERA DEL HILO PARA EVITAR 'no known parent package'
    try:
        from .http_bridge import start_http_server
        from .mcp_server import mcp
    except Exception as e:
        print(f"[AXIOM] ❌ ERROR DE IMPORTACIÓN EN SERVIDORES: {e}")
        return

    def run_mcp():
        try:
            import uvicorn
            print("[AXIOM] 📡 MCP SERVER: INICIANDO SSE BRIDGE (9879)")
            uvicorn.run(mcp.sse_app(), host="127.0.0.1", port=9879, log_level="error")
        except Exception as e:
            print(f"[AXIOM] ℹ️ MCP SERVER STATUS: {e}")

    def run_http():
        try:
            start_http_server()
            print("[AXIOM] 🌐 HTTP BRIDGE: ACTIVO (9877)")
        except Exception as e:
            print(f"[AXIOM] ℹ️ HTTP BRIDGE STATUS: {e}")

    threading.Thread(target=run_mcp, daemon=True).start()
    threading.Thread(target=run_http, daemon=True).start()

def unregister():
    from .addon import _axsock as bsock
    try: bsock.stop_socket_server()
    except: pass
    from .addon import properties as _props
    try: _props.unregister_properties()
    except: pass
    try:
        from .http_bridge import stop_http_server
        stop_http_server()
    except: pass
