import bpy, os, sys, subprocess, importlib, threading, traceback

bl_info = {
    "name": "AXIOM Precision Engine",
    "description": "Industrial-grade AI assembly pipeline for Blender",
    "author": "CarlosH",
    "version": (0, 8, 83),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Axiom",
    "category": "3D View",
}

def _ensure_deps():
    print("[AXIOM] 🔍 Validando dependencias...")
    required = ["mcp", "fastmcp", "uvicorn", "starlette", "sse-starlette", "requests"]
    to_install = []
    for pkg in required:
        import_name = pkg.replace("-", "_")
        if pkg == "fastmcp": import_name = "mcp"
        try:
            importlib.import_module(import_name)
        except ImportError: to_install.append(pkg)
    if not to_install: return True
    print(f"[AXIOM] 📦 Instalando: {to_install}...")
    for pkg in to_install:
        try:
            cmd = [sys.executable, "-m", "pip", "install", pkg, "--quiet"]
            if os.name != 'nt': cmd.append("--break-system-packages")
            subprocess.check_call(cmd, timeout=60)
        except: return False
    return True

def register():
    print("\n[AXIOM] 🚀 INICIANDO SECUENCIA DE VALIDACIÓN V0.8.83")
    if not _ensure_deps():
        print("[AXIOM] ❌ FALLO DE DEPENDENCIAS.")
        return

    from .addon import _axsock as bsock
    from .addon import properties as _props
    from .addon import preferences as _prefs
    
    # 1. SOCKET SERVER
    try:
        bsock.start_socket_server()
        print("[AXIOM] ✅ SOCKET SERVER: LISTO (PUERTO 9876)")
    except Exception as e: print(f"[AXIOM] ❌ SOCKET ERROR: {e}")

    # 2. RNA BASE TYPES
    try:
        from .addon.chat_types import ChatMsg, ModelItem
        for cls in [ChatMsg, ModelItem]:
            bpy.utils.register_class(cls)
            print(f"[AXIOM] ✅ RNA REG: {cls.__name__}")
            
        # 3. COMPLEX PROPERTIES & PANELS
        from .addon.properties import ChatData, ModelsData, MCP_UL_Chat
        from .addon.panels.chat import BLENDERMCP_OT_OpenWeb
        from .addon.panels import chat, config, integrations
        
        classes = [chat.PN_PT_Chat, config.PN_PT_Config, ChatData, ModelsData, MCP_UL_Chat, BLENDERMCP_OT_OpenWeb]
        for p in integrations.PANELS: classes.append(p)
        for cls in classes:
            try: 
                bpy.utils.register_class(cls)
                print(f"[AXIOM] ✅ COMPONENT REG: {cls.__name__}")
            except: pass

        _props.register_properties()
        _prefs.register_preferences()
        
        # 4. OPERATORS
        from .addon.operators import connect, chat, capture, export, setup, embedded, model_ops
        connect.register_connect_operators()
        chat.register_chat_operators()
        capture.register_capture_operators()
        export.register_export_operators()
        setup.register_setup_operators()
        embedded.register_embedded_operators()
        model_ops.register_model_operators()
        print("[AXIOM] ✅ OPERADORES: REGISTRADOS")
            
        # 5. SCENE PROPERTIES
        Scene = bpy.types.Scene
        from bpy.props import PointerProperty, StringProperty, BoolProperty, IntProperty
        setattr(Scene, "aimcp_chat", PointerProperty(type=ChatData))
        setattr(Scene, "aimcp_input", StringProperty(default=""))
        setattr(Scene, "aimcp_connected", BoolProperty(default=False))
        setattr(Scene, "aimcp_ai_state", StringProperty(default="disconnected"))
        setattr(Scene, "aimcp_status", StringProperty(default=""))
        setattr(Scene, "aimcp_models", PointerProperty(type=ModelsData))
        print("[AXIOM] ✅ ESCENA: PROPIEDADES VINCULADAS")
        
        # 6. MCP SERVER
        _start_mcp_server()
        
        # 7. TIMERS
        try:
            from .addon.operators.model_ops import _status_ticker
            bpy.app.timers.register(_status_ticker, first_interval=0.2)
            print("[AXIOM] ✅ SISTEMA DE TELEMETRÍA: ACTIVO")
        except: pass
        
        print("[AXIOM] ⭐ SECUENCIA DE ARRANQUE COMPLETADA CON ÉXITO\n")
        
    except Exception as e:
        print(f"[AXIOM] ❌ ERROR CRÍTICO EN SECUENCIA: {e}")
        traceback.print_exc()

def _start_mcp_server():
    def run():
        try:
            import uvicorn
            from .mcp_server import mcp
            print("[AXIOM] 📡 MCP SERVER: INICIANDO EN PUERTO 9879...")
            uvicorn.run(mcp.sse_app(), host="127.0.0.1", port=9879, log_level="warning")
        except Exception as e: print(f"[AXIOM] ❌ MCP SERVER ERROR: {e}")
    threading.Thread(target=run, daemon=True).start()

def unregister():
    from .addon import _axsock as bsock
    bsock.stop_socket_server()
    print("[AXIOM] 👋 Motor Axiom detenido.")
