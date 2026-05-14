# AXIOM Precision Engine v0.8.75
# Automatic Installation & Bootstrapper (GitHub ZIP Compatible)
import bpy, os, sys, subprocess, threading, time, importlib, traceback

bl_info = {
    "name": "AXIOM Precision Engine",
    "description": "Industrial-grade AI assembly pipeline for Blender",
    "author": "CarlosH",
    "version": (0, 8, 78),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Axiom",
    "category": "3D View",
}

# 1. AUTO-INSTALLER (SILENT)
def _ensure_deps():
    required = ["mcp", "fastmcp", "uvicorn", "starlette", "sse-starlette", "requests"]
    to_install = []
    for pkg in required:
        import_name = pkg.replace("-", "_")
        if pkg == "fastmcp": import_name = "mcp"
        try:
            importlib.import_module(import_name)
        except ImportError:
            to_install.append(pkg)
            
    if not to_install: return True

    print(f"[AXIOM] Instalando dependencias: {to_install}...")
    for pkg in to_install:
        try:
            cmd = [sys.executable, "-m", "pip", "install", pkg, "--quiet"]
            if os.name != 'nt': cmd.append("--break-system-packages")
            subprocess.check_call(cmd, timeout=60)
        except: return False
    return True

# 2. PATH CONFIGURATION
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path: sys.path.insert(0, ROOT)
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path: sys.path.insert(0, SRC_PATH)

# 3. MODULAR REGISTRATION
def register():
    if not _ensure_deps():
        print("[AXIOM] ❌ Error de dependencias. Revisa la consola.")
        return

    from .addon import _axsock as bsock
    from .addon import properties as _props
    from .addon import preferences as _prefs
    from .addon import operators as _ops
    from .addon import panels as _panels
    
    # Iniciar Socket Server (9876)
    try:
        bsock.start_socket_server()
        print("[AXIOM] ✅ Precisión Socket listo (:9876)")
    except Exception as e: print(f"[AXIOM] Socket Error: {e}")

    # --- REGISTRO DE CLASES (PRIMERO) ---
    try:
        from .addon.properties import ChatMsg, ChatData, ModelsData, ModelItem, MCP_UL_Chat
        from .addon.panels.chat import BLENDERMCP_OT_OpenWeb
        
        # Paneles
        from .addon.panels import chat as _chat_panel, config as _config_panel, integrations as _int_panel
        classes = [
            _chat_panel.PN_PT_Chat, _config_panel.PN_PT_Config,
            ChatMsg, ChatData, ModelsData, ModelItem, MCP_UL_Chat, 
            BLENDERMCP_OT_OpenWeb
        ]
        for p in _int_panel.PANELS: classes.append(p)
        
        for cls in classes:
            try: bpy.utils.register_class(cls)
            except: pass

        # --- REGISTRO DE PROPIEDADES Y PREFERENCIAS (DESPUÉS) ---
        _props.register_properties()
        _prefs.register_preferences()
        
        # Registro de operadores
        from .addon.operators import connect, chat, capture, export, setup, embedded, model_ops
        connect.register_connect_operators()
        chat.register_chat_operators()
        capture.register_capture_operators()
        export.register_export_operators()
        setup.register_setup_operators()
        embedded.register_embedded_operators()
        model_ops.register_model_operators()
            
        # ⚡ PROPIEDADES DE ESCENA (Vinculadas a las clases ya registradas)
        Scene = bpy.types.Scene
        from bpy.props import PointerProperty, StringProperty, BoolProperty, IntProperty
        
        setattr(Scene, "aimcp_chat", PointerProperty(type=ChatData))
        setattr(Scene, "aimcp_input", StringProperty(default=""))
        setattr(Scene, "aimcp_connected", BoolProperty(default=False))
        setattr(Scene, "aimcp_ai_state", StringProperty(default="disconnected"))
        setattr(Scene, "aimcp_model", StringProperty(default=""))
        setattr(Scene, "aimcp_status", StringProperty(default=""))
        setattr(Scene, "aimcp_models", PointerProperty(type=ModelsData))
        setattr(Scene, "aimcp_waiting", BoolProperty(default=False))
        setattr(Scene, "aimcp_spinner_idx", IntProperty(default=0))
        setattr(Scene, "aimcp_connection_status", StringProperty(default=""))
        setattr(Scene, "aimcp_chat_index", IntProperty(default=0))
            
        # Iniciar Ticker de Status y Timers
        try:
            from .addon.operators.model_ops import _status_ticker
            bpy.app.timers.register(_status_ticker, first_interval=0.2)
        except: pass
        
    except Exception as e:
        print(f"[AXIOM] ❌ Error de registro modular: {e}")
        traceback.print_exc()

    # Iniciar Servidor MCP (9879)
    _start_mcp_server()

def _start_mcp_server():
    def run():
        try:
            import uvicorn
            from mcp_server import mcp
            app = mcp.sse_app()
            uvicorn.run(app, host="127.0.0.1", port=9879, log_level="error")
        except Exception as e: print(f"[AXIOM] MCP Server Error: {e}")

    threading.Thread(target=run, daemon=True).start()

def unregister():
    # Lógica de limpieza inversa
    from .addon import _axsock as bsock
    bsock.stop_socket_server()
    # (Unregister de clases omitido para brevedad, pero debe incluirse en producción)

if __name__ == "__main__":
    register()
