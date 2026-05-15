"""
blender-mcp — Download RST Documentation Operator
Downloads and extracts the Blender API RST documentation files.
"""
import bpy
import os
import json
import tarfile
import tempfile
import threading
import urllib.request
from bpy.types import Operator
from pathlib import Path

# URL de los RSTs comprimidos (ajustar cuando se suban al release)
RST_API_URL = "https://github.com/carlosh7/blender-mcp/releases/download/docs/api_docs.tar.gz"

def _get_docs_dir():
    return os.path.join(os.path.dirname(__file__), "..", "data")


def _docs_installed():
    api_dir = os.path.join(_get_docs_dir(), "api")
    return os.path.exists(api_dir) and len(os.listdir(api_dir)) > 10


def _check_docs_installed():
    return _docs_installed()


class OP_DownloadDocs(Operator):
    bl_idname = "aimcp.download_docs"
    bl_label = "Download RST Docs"
    bl_description = "Descarga la documentación de Blender API para búsqueda offline"

    _timer = None
    _progress = 0.0
    _status = ""
    _thread = None
    _success = False

    def _download_and_extract(self):
        try:
            docs_dir = _get_docs_dir()
            os.makedirs(docs_dir, exist_ok=True)

            api_dir = os.path.join(docs_dir, "api")
            if os.path.exists(api_dir):
                import shutil
                shutil.rmtree(api_dir)

            self._status = "Descargando documentación..."
            self._progress = 0.1

            temp_path = os.path.join(tempfile.gettempdir(), "blender_mcp_docs.tar.gz")

            def _report(block, blocksize, totalsize):
                if totalsize > 0:
                    self._progress = 0.1 + 0.6 * min(1.0, block * blocksize / totalsize)

            urllib.request.urlretrieve(RST_API_URL, temp_path, reporthook=_report)

            self._status = "Extrayendo archivos..."
            self._progress = 0.7

            with tarfile.open(temp_path, "r:gz") as tar:
                members = tar.getmembers()
                for i, m in enumerate(members):
                    tar.extract(m, docs_dir)
                    self._progress = 0.7 + 0.3 * (i + 1) / len(members)

            os.unlink(temp_path)

            total = len([f for f in os.listdir(api_dir) if f.endswith(".rst")]) if os.path.exists(api_dir) else 0
            self._status = f"✅ {total} documentos instalados"
            self._progress = 1.0
            self._success = True

        except Exception as e:
            self._status = f"❌ Error: {str(e)[:80]}"
            self._progress = 0.0
            self._success = False

    def execute(self, ctx):
        self._progress = 0.01
        self._status = "Iniciando..."
        self._success = False

        def _work():
            self._download_and_extract()
            bpy.app.timers.register(self._finish, first_interval=0.1)

        self._thread = threading.Thread(target=_work, daemon=True)
        self._thread.start()

        self._timer = bpy.app.timers.register(self._tick, first_interval=0.1)
        ctx.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _tick(self):
        ctx = bpy.context
        if ctx and ctx.area:
            ctx.area.tag_redraw()
        return 0.2

    def _finish(self):
        ctx = bpy.context
        for s in bpy.data.scenes:
            s.aimcp_docs_status = self._status
            if self._success:
                s.aimcp_use_rst = True
        if ctx and ctx.area:
            ctx.area.tag_redraw()

    def modal(self, ctx, event):
        if event.type == 'TIMER':
            ctx.area.tag_redraw()
        return {'PASS_THROUGH'}


DOWNLOAD_OPERATORS = [OP_DownloadDocs]


def register_download_operators():
    from bpy.utils import register_class
    for cls in DOWNLOAD_OPERATORS:
        try:
            register_class(cls)
        except:
            pass


def unregister_download_operators():
    from bpy.utils import unregister_class
    for cls in reversed(DOWNLOAD_OPERATORS):
        try:
            unregister_class(cls)
        except:
            pass
