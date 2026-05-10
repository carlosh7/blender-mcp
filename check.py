#!/usr/bin/env python3
"""
blender-mcp — Environment Checker
Validates that all dependencies are installed and provides installation help.
Works on Windows and Linux.
"""

import subprocess
import sys
import os
import shutil
import platform

SYSTEM = platform.system()
PASS = "✅"
FAIL = "❌"
WARN = "⚠️"
checks = []

def log(icon, msg):
    checks.append((icon, msg))
    print(f"  {icon}  {msg}")

def check_python():
    v = sys.version_info
    if v.major >= 3 and v.minor >= 10:
        log(PASS, f"Python {v.major}.{v.minor}.{v.micro} (3.10+ required)")
        return True
    else:
        log(FAIL, f"Python {v.major}.{v.minor}.{v.micro} (need 3.10+). Download: https://python.org")
        return False

def check_pip():
    if shutil.which("pip") or shutil.which("pip3"):
        log(PASS, "pip installed")
        return True
    log(WARN, "pip not found. Run: python -m ensurepip")
    return False

def check_blender():
    blender = shutil.which("blender.exe") or shutil.which("blender")
    if blender:
        try:
            r = subprocess.run([blender, "--version"], capture_output=True, text=True, timeout=10)
            ver = r.stdout.split("\n")[0].strip() if r.stdout else "unknown"
            log(PASS, f"Blender: {ver}")
            return True
        except:
            pass
    msg = "Blender not found."
    if SYSTEM == "Windows":
        msg += " Download from: https://www.blender.org/download/"
    else:
        msg += " Install: sudo apt install blender"
    log(FAIL, msg)
    return False

def check_mcp():
    try:
        import mcp
        log(PASS, "MCP SDK installed")
        return True
    except ImportError:
        log(WARN, "MCP SDK not installed. Run: pip install mcp")
        return False

def check_disk():
    try:
        if SYSTEM == "Windows":
            import ctypes
            free = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p("."), None, None, ctypes.pointer(free))
            mb = free.value / (1024 * 1024)
        else:
            st = os.statvfs(".")
            mb = (st.f_frsize * st.f_bavail) / (1024 * 1024)
        if mb > 500:
            log(PASS, f"Disk space: {mb:.0f} MB free")
        else:
            log(WARN, f"Low disk: {mb:.0f} MB free (need >500)")
    except:
        log(WARN, "Could not check disk space")

def print_summary():
    print(f"\n{'='*50}")
    print(f"  blender-mcp — Environment Check")
    print(f"  OS: {SYSTEM}")
    print(f"{'='*50}\n")

    py_ok = check_python()
    check_pip()
    check_blender()
    check_mcp()
    check_disk()

    ok = sum(1 for c in checks if c[0] == PASS)
    total = len(checks)
    print(f"\n{'='*50}")
    print(f"  {ok}/{total} checks passed")
    if ok == total:
        print(f"  ✅ Everything looks good!")
    else:
        print(f"  Fix the issues above, then run: python check.py")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    print_summary()
