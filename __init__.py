import bpy, os, sys, subprocess, importlib, threading, traceback

bl_info = {
    "name": "AXIOM Precision Engine",
    "description": "Industrial-grade AI assembly pipeline for Blender",
    "author": "CarlosH",
    "version": (0, 8, 84),
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
    print("\n[AXIOM] 🚀 RESTAURANDO UI V0.8.84")
    if not _ensure_deps(): return

    from .addon import _axsock as bsock
    from .addon import properties as _props
    from .addon import preferences as _prefs
    
    try: bsock.start_socket_server()
    except: pass

    try:
        from .addon.chat_types import ChatMsg, ModelItem
        for cls in [ChatMsg, ModelItem]: bpy.utils.register_class(cls)
            
        from .addon.properties import ChatData, ModelsData, MCP_UL_Chat
        from .addon.panels.chat import BLENDERMCP_OT_OpenWeb
        from .addon.panels import chat, config, integrations
        
        classes = [chat.PN_PT_Chat, config.PN_PT_Config, ChatData, ModelsData, MCP_UL_Chat, BLENDERMCP_OT_OpenWeb]
        for p in integrations.PANELS: classes.append(p)
        for cls in classes:
            try: bpy.utils.register_class(cls)
            except: pass

        _props.register_properties()
        _prefs.register_preferences()
        
        from .addon.operators import connect, chat as chat_ops, capture, export, setup, embedded, model_ops
        connect.register_connect_operators()
        chat_ops.register_chat_operators()
        capture.register_capture_operators()
        export.register_export_operators()
        setup.register_setup_operators()
        embedded.register_embedded_operators()
        model_ops.register_model_operators()
            
        # ⚡ RESTAURACIÓN TOTAL DE PROPIEDADES (CRÍTICO PARA EL PANEL)
        Scene = bpy.types.Scene
        from bpy.props import PointerProperty, StringProperty, BoolProperty, IntProperty
        
        setattr(Scene, "aimcp_chat", PointerProperty(type=ChatData))
        setattr(Scene, "aimcp_input", StringProperty(default=""))
        setattr(Scene, "aimcp_connected", BoolProperty(default=False))
        setattr(Scene, "aimcp_ai_state", StringProperty(default="disconnected"))
        setattr(Scene, "aimcp_status", StringProperty(default=""))
        setattr(Scene, "aimcp_models", PointerProperty(type=ModelsData))
        
        # Propiedades auxiliares para UI (Spinner, Waiting, Index)
        setattr(Scene, "aimcp_waiting", BoolProperty(default=False))
        setattr(Scene, "aimcp_spinner_idx", IntProperty(default=0))
        setattr(Scene, "aimcp_connection_status", StringProperty(default=""))
        setattr(Scene, "aimcp_chat_index", IntProperty(default=0))
        setattr(Scene, "aimcp_model", StringProperty(default=""))
        
        _start_mcp_server()
        
        try:
            from .addon.operators.model_ops import _status_ticker
            bpy.app.timers.register(_status_ticker, first_interval=0.2)
        except: pass
        
        print("[AXIOM] ✅ UI RESTAURADA")
        
    except Exception as e:
        print(f"[AXIOM] ❌ ERROR EN REGISTRO UI: {e}")
        traceback.print_exc()

def _start_mcp_server():
    def run():
        try:
            import uvicorn
            from .mcp_server import mcp
            uvicorn.run(mcp.sse_app(), host="127.0.0.1", port=9879, log_level="error")
        except: pass
    threading.Thread(target=run, daemon=True).start()

def unregister():
    from .addon import _axsock as bsock
    bsock.stop_socket_server()
