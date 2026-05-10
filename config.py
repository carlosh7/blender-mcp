import os
import sys
import shutil
import platform
import subprocess
import json

SYSTEM = platform.system()  # 'Windows' or 'Linux'

def find_blender() -> str | None:
    """Find Blender executable path across platforms."""
    if SYSTEM == "Windows":
        # 1. PATH
        blender = shutil.which("blender.exe") or shutil.which("blender")
        if blender:
            return blender

        # 2. Program Files
        common = [
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
        ]
        for base in common:
            path = os.path.join(base, "Blender Foundation")
            if os.isdir(path):
                for entry in os.listdir(path):
                    if entry.startswith("Blender"):
                        exe = os.path.join(path, entry, "blender.exe")
                        if os.path.isfile(exe):
                            return exe

        # 3. Microsoft Store
        store = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps")
        store_exe = os.path.join(store, "blender.exe")
        if os.path.isfile(store_exe):
            return store_exe

        return None

    else:  # Linux
        blender = shutil.which("blender")
        if blender:
            return blender
        # Common paths
        for path in ["/usr/bin/blender", "/snap/bin/blender"]:
            if os.path.isfile(path):
                return path
        return None


def find_python() -> str | None:
    """Find Python 3 executable."""
    if SYSTEM == "Windows":
        return shutil.which("python") or shutil.which("python3")
    return shutil.which("python3") or shutil.which("python")


def get_blender_version(blender_path: str) -> str | None:
    """Return Blender version string (e.g. '4.0.2')."""
    try:
        result = subprocess.run(
            [blender_path, "--version"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split("\n"):
            if line.strip().startswith("Blender"):
                return line.strip()
        return result.stdout.split("\n")[0].strip()
    except:
        return None


def check_disk_space(path: str = ".") -> dict:
    """Check available disk space in MB."""
    try:
        if SYSTEM == "Windows":
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(os.path.abspath(path)),
                None, None, ctypes.pointer(free_bytes)
            )
            free_mb = free_bytes.value / (1024 * 1024)
        else:
            st = os.statvfs(path)
            free_mb = (st.f_frsize * st.f_bavail) / (1024 * 1024)
        return {"free_mb": round(free_mb, 1), "enough": free_mb > 500}
    except:
        return {"free_mb": 0, "enough": False}


def get_system_info() -> dict:
    """Return all system info for diagnostics."""
    blender_path = find_blender()
    blender_ver = get_blender_version(blender_path) if blender_path else None
    python_path = find_python()
    disk = check_disk_space()

    return {
        "system": SYSTEM,
        "python": python_path,
        "python_version": sys.version.split()[0] if python_path else None,
        "blender": blender_path,
        "blender_version": blender_ver,
        "disk_free_mb": disk["free_mb"],
        "disk_ok": disk["enough"],
    }


def print_summary():
    info = get_system_info()
    print(f"\n{'='*50}")
    print(f"  blender-mcp — System Check")
    print(f"{'='*50}")
    print(f"  OS:          {info['system']}")
    print(f"  Python:      {info['python']} ({info['python_version']})")
    print(f"  Blender:     {info['blender']} ({info['blender_version']})")
    print(f"  Disk free:   {info['disk_free_mb']} MB")
    print(f"{'='*50}")
    if info['blender'] and info['python']:
        print(f"  ✅ Sistema listo para blender-mcp")
    else:
        print(f"  ❌ Faltan componentes. Revisa check.py para más detalles.")
    print(f"{'='*50}\n")
    return info


if __name__ == "__main__":
    print_summary()
