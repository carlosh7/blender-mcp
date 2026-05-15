import bpy, os, sys, subprocess, importlib, threading, traceback, time, socket

bl_info = {
    "name": "AXIOM Precision Engine",
    "description": "Industrial-grade AI assembly pipeline for Blender",
    "author": "CarlosH",
    "version": (0, 8, 98),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Axiom",
    "category": "3D View",
}

def _check_port(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except:
        return False

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
    ver = "0.8.98"
    print(f"\n[AXIOM] 🚀 INICIANDO SECUENCIA DE VERIFICACIÓN TOTAL v{ver}")
    
    if not _ensure_deps():
        print("[AXIOM] ❌ FALLO CRÍTICO: No se pudieron validar las dependencias.")
        return

    from .addon import _axsock as bsock
    from .addon import properties as _props
    from .addon import preferences as _prefs
    
    # 1. LANZAMIENTO DE SERVICIOS
    bsock.start_socket_server()
    _start_servers(__package__) # Pasar el contexto del paquete

    # Pausa técnica para permitir el binding
    time.sleep(1.0)

    try:
        # 2. AUDITORÍA FÍSICA DE PUERTOS
        s_9876 = _check_port(9876)
        s_9877 = _check_port(9877)
        s_9879 = _check_port(9879)
        
        print(f"[AXIOM] {'✅' if s_9876 else '❌'} PORT 9876 (SOCKET): {'OPERATIVO' if s_9876 else 'DESCONECTADO'}")
        print(f"[AXIOM] {'✅' if s_9877 else '❌'} PORT 9877 (HTTP): {'OPERATIVO' if s_9877 else 'DESCONECTADO'}")
        print(f"[AXIOM] {'✅' if s_9879 else '❌'} PORT 9879 (MCP): {'OPERATIVO' if s_9879 else 'DESCONECTADO'}")

        # 3. VALIDACIÓN RNA
        from .addon.chat_types import ChatMsg, ModelItem
        from .addon.properties import ChatData, ModelsData, MCP_UL_Chat
        from .addon.panels.chat import BLENDERMCP_OT_OpenWeb
        from .addon.panels import chat, config, integrations
        
        classes = [ChatMsg, ModelItem, chat.PN_PT_Chat, config.PN_PT_Config, ChatData, ModelsData, MCP_UL_Chat, BLENDERMCP_OT_OpenWeb]
        for p in integrations.PANELS: classes.append(p)
        for cls in classes:
            try: bpy.utils.register_class(cls)
            except: pass

        # 4. OPERADORES
        from .addon.operators import connect, chat as chat_ops, capture, export, setup, embedded, model_ops
        connect.register_connect_operators()
        chat_ops.register_chat_operators()
        capture.register_capture_operators()
        export.register_export_operators()
        setup.register_setup_operators()
        embedded.register_embedded_operators()
        model_ops.register_model_operators()
        _props.register_properties()
        _prefs.register_preferences()
        
        # 5. VEREDICTO
        all_ok = s_9876 and s_9877 and s_9879
        if all_ok:
            print(f"[AXIOM] ⭐ REPORTE DE INTEGRIDAD v{ver}: SISTEMA OPERATIVO AL 100%\n")
        else:
            print(f"[AXIOM] 🚨 REPORTE DE INTEGRIDAD v{ver}: SISTEMA DEGRADADO (Revisa Sockets)\n")
        
        def auto_refresh():
            try: bpy.ops.aimcp.refresh()
            except: pass
            return None
        bpy.app.timers.register(auto_refresh, first_interval=1.0)
        
    except Exception as e:
        print(f"[AXIOM] ❌ FALLO EN LA SECUENCIA: {e}")
        traceback.print_exc()

def _start_servers(pkg_name):
    try:
        # USAR IMPORTLIB CON EL NOMBRE DEL PAQUETE PARA EVITAR ERRORES DE CONTEXTO
        bridge_mod = importlib.import_module(".http_bridge", pkg_name)
        mcp_mod = importlib.import_module(".mcp_server", pkg_name)
        
        def run_mcp():
            try:
                import uvicorn
                uvicorn.run(mcp_mod.mcp.sse_app(), host="127.0.0.1", port=9879, log_level="error")
            except: pass

        def run_http():
            try:
                bridge_mod.start_http_server()
            except: pass

        threading.Thread(target=run_mcp, daemon=True).start()
        threading.Thread(target=run_http, daemon=True).start()
        
    except Exception as e:
        print(f"[AXIOM] ❌ ERROR DE INICIALIZACIÓN DE SERVIDORES: {e}")

def unregister():
    from .addon import _axsock as bsock
    try: bsock.stop_socket_server()
    except: pass
    from .addon import properties as _props
    try: _props.unregister_properties()
    except: pass
    try:
        # Intentar detener el puente usando import dinámico
        bridge_mod = importlib.import_module(".http_bridge", __package__)
        bridge_mod.stop_http_server()
    except: pass
