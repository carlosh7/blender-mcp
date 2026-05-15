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

# ─── Import helpers: fallback relativo → absoluto ───
def _import_addon(name):
    try:
        return importlib.import_module(f".{name}", __package__)
    except (ImportError, ValueError):
        return importlib.import_module(f"addon.{name}")

def _import_server(name):
    try:
        return importlib.import_module(f".{name}", __package__)
    except (ImportError, ValueError):
        return __import__(name)

# ─── Auditoría de puertos ───
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
    ver = "0.8.119"
    print(f"\n[AXIOM] 🚀 INICIANDO SECUENCIA DE VERIFICACIÓN TOTAL v{ver}")
    
    if not _ensure_deps():
        print("[AXIOM] ❌ FALLO CRÍTICO: No se pudieron validar las dependencias.")
        return

    bsock = _import_addon("_axsock")
    _props = _import_addon("properties")
    _prefs = _import_addon("preferences")
    
    # 1. LANZAMIENTO DE SERVICIOS
    bsock.start_socket_server()
    _start_servers(__package__)

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
        chat_types = _import_addon("chat_types")
        props = _import_addon("properties")
        panels_chat = _import_addon("panels.chat")
        panels_config = _import_addon("panels.config")
        panels_integrations = _import_addon("panels.integrations")
        
        classes = [
            chat_types.ChatMsg, chat_types.ModelItem,
            panels_chat.PN_PT_Chat, panels_config.PN_PT_Config,
            props.ChatData, props.ModelsData, props.MCP_UL_Chat,
            panels_chat.BLENDERMCP_OT_OpenWeb,
        ]
        for p in panels_integrations.PANELS: classes.append(p)
        for cls in classes:
            try: bpy.utils.register_class(cls)
            except: pass

        # 4. OPERADORES
        ops_connect = _import_addon("operators.connect")
        ops_chat = _import_addon("operators.chat")
        ops_capture = _import_addon("operators.capture")
        ops_export = _import_addon("operators.export")
        ops_setup = _import_addon("operators.setup")
        ops_embedded = _import_addon("operators.embedded")
        ops_model = _import_addon("operators.model_ops")
        
        ops_connect.register_connect_operators()
        ops_chat.register_chat_operators()
        ops_capture.register_capture_operators()
        ops_export.register_export_operators()
        ops_setup.register_setup_operators()
        ops_embedded.register_embedded_operators()
        ops_model.register_model_operators()
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
        mcp_mod = _import_server("mcp_server")
        
        def run_mcp():
            try:
                import uvicorn
                uvicorn.run(mcp_mod.mcp.sse_app(), host="127.0.0.1", port=9879, log_level="error")
            except: pass

        threading.Thread(target=run_mcp, daemon=True).start()
        
    except Exception as e:
        print(f"[AXIOM] ❌ ERROR DE INICIALIZACIÓN DE SERVIDORES: {e}")

def unregister():
    bsock = _import_addon("_axsock")
    try: bsock.stop_socket_server()
    except: pass
    _props = _import_addon("properties")
    try: _props.unregister_properties()
    except: pass
    pass
