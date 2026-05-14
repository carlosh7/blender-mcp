import bpy, os, sys, subprocess, importlib, threading, traceback

bl_info = {
    "name": "AXIOM Precision Engine",
    "description": "Industrial-grade AI assembly pipeline for Blender",
    "author": "CarlosH",
    "version": (0, 8, 86),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Axiom",
    "category": "3D View",
}

def _ensure_deps():
    required = ["mcp", "fastmcp", "uvicorn", "starlette", "sse-starlette", "requests"]
    to_install = []
    for pkg in required:
        import_name = pkg.replace("-", "_")
        if pkg == "fastmcp": import_name = "mcp"
        try:
            importlib.import_module(import_name)
        except ImportError: to_install.append(pkg)
    if not to_install: return True
    for pkg in to_install:
        try:
            cmd = [sys.executable, "-m", "pip", "install", pkg, "--quiet"]
            if os.name != 'nt': cmd.append("--break-system-packages")
            subprocess.check_call(cmd, timeout=60)
        except: return False
    return True

def register():
    # IDEMPOTENCIA: Si ya estamos en medio de un registro, evitamos duplicar logs pesados
    if not _ensure_deps(): return

    from .addon import _axsock as bsock
    from .addon import properties as _props
    from .addon import preferences as _prefs
    
    # Iniciar Socket (si no está corriendo)
    try: bsock.start_socket_server()
    except: pass

    try:
        # --- ETAPA 1: TIPOS BASE ---
        from .addon.chat_types import ChatMsg, ModelItem
        for cls in [ChatMsg, ModelItem]:
            try: bpy.utils.register_class(cls)
            except: pass
            
        # --- ETAPA 2: PROPIEDADES Y PANELES ---
        from .addon.properties import ChatData, ModelsData, MCP_UL_Chat
        from .addon.panels.chat import BLENDERMCP_OT_OpenWeb
        from .addon.panels import chat, config, integrations
        
        classes = [chat.PN_PT_Chat, config.PN_PT_Config, ChatData, ModelsData, MCP_UL_Chat, BLENDERMCP_OT_OpenWeb]
        for p in integrations.PANELS: classes.append(p)
        for cls in classes:
            try: bpy.utils.register_class(cls)
            except: pass

        # --- ETAPA 3: OPERADORES Y PROPIEDADES DE ESCENA ---
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
        
        # --- ETAPA 4: SERVICIOS ---
        _start_mcp_server()
        
        try:
            from .addon.operators.model_ops import _status_ticker
            if not bpy.app.timers.is_registered(_status_ticker):
                bpy.app.timers.register(_status_ticker, first_interval=0.2)
        except: pass
        
        # --- ETAPA 5: AUTO-POBLADO ---
        def auto_refresh():
            try: bpy.ops.aimcp.refresh()
            except: pass
            return None
        bpy.app.timers.register(auto_refresh, first_interval=1.0)
        
        print("[AXIOM] ✅ Motor v0.8.86 Registrado (Modo Idempotente)")
        
    except Exception as e:
        print(f"[AXIOM] ❌ Error en registro: {e}")

def _start_mcp_server():
    def run():
        try:
            import uvicorn
            from .mcp_server import mcp
            uvicorn.run(mcp.sse_app(), host="127.0.0.1", port=9879, log_level="error")
        except: pass
    t = threading.Thread(target=run, daemon=True)
    t.start()

def unregister():
    from .addon import _axsock as bsock
    try: bsock.stop_socket_server()
    except: pass
    
    from .addon import properties as _props
    try: _props.unregister_properties()
    except: pass
    
    # Aquí se podrían desregistrar las clases, pero en 4.2 a veces es mejor dejar que el sistema lo maneje 
    # si se va a re-registrar inmediatamente. No obstante, para ser limpios:
    from .addon.chat_types import ChatMsg, ModelItem
    from .addon.properties import ChatData, ModelsData, MCP_UL_Chat
    from .addon.panels.chat import BLENDERMCP_OT_OpenWeb
    from .addon.panels import chat, config, integrations
    
    classes = [chat.PN_PT_Chat, config.PN_PT_Config, ChatData, ModelsData, MCP_UL_Chat, BLENDERMCP_OT_OpenWeb]
    for p in integrations.PANELS: classes.append(p)
    classes += [ChatMsg, ModelItem]
    
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
