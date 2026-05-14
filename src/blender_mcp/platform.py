"""
blender-mcp — Cross-platform utilities
Centralizes OS-specific paths, detection, and process management.
"""
import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

SYSTEM = platform.system()  # 'Windows', 'Darwin', 'Linux'


def get_config_dir() -> Path:
    """Cross-platform config directory (stores logs, memory, cache)."""
    if SYSTEM == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif SYSTEM == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    return base / "blender-mcp"


def get_log_dir() -> Path:
    """Cross-platform log directory."""
    cfg = get_config_dir()
    log_dir = cfg / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_opencode_auth_path() -> Path:
    """Cross-platform path to opencode auth.json."""
    if SYSTEM == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif SYSTEM == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux
        base = Path.home() / ".local" / "share"
    return base / "opencode" / "auth.json"


def get_opencode_config_paths() -> list[Path]:
    """Cross-platform paths to opencode config files."""
    paths = []
    if SYSTEM == "Windows":
        appdata = Path(os.environ.get("APPDATA", ""))
        if appdata:
            paths.append(appdata / "opencode" / "opencode.json")
    elif SYSTEM == "Darwin":
        paths.append(Path.home() / "Library" / "Application Support" / "opencode" / "opencode.json")
    else:
        paths.append(Path.home() / ".config" / "opencode" / "opencode.json")
        paths.append(Path.home() / "Check" / "opencode.json")
    paths.append(Path.cwd() / "opencode.json")
    return paths


def find_blender() -> str | None:
    """Find Blender executable across platforms."""
    # 1. Check PATH first
    blender = shutil.which("blender.exe") or shutil.which("blender")
    if blender:
        return blender

    if SYSTEM == "Windows":
        # Program Files
        for base in [os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                     os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")]:
            path = os.path.join(base, "Blender Foundation")
            if os.path.isdir(path):
                for entry in os.listdir(path):
                    if entry.startswith("Blender"):
                        exe = os.path.join(path, entry, "blender.exe")
                        if os.path.isfile(exe):
                            return exe
        # Microsoft Store
        store = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps")
        store_exe = os.path.join(store, "blender.exe")
        if os.path.isfile(store_exe):
            return store_exe
        return None

    elif SYSTEM == "Darwin":
        # Mac: /Applications/Blender.app/Contents/MacOS/Blender
        mac_path = "/Applications/Blender.app/Contents/MacOS/Blender"
        if os.path.isfile(mac_path):
            return mac_path
        # Also check ~/Applications
        user_path = os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender")
        if os.path.isfile(user_path):
            return user_path
        # Also check blender.org DMG installs
        for ver in range(42, 60):
            path = f"/Applications/Blender {ver}.app/Contents/MacOS/Blender"
            if os.path.isfile(path):
                return path
        return None

    else:  # Linux
        for path in ["/usr/bin/blender", "/snap/bin/blender", "/usr/local/bin/blender"]:
            if os.path.isfile(path):
                return path
        return None


def find_python() -> str:
    """Get the system Python executable."""
    if SYSTEM == "Windows":
        return shutil.which("python") or sys.executable
    return shutil.which("python3") or shutil.which("python") or sys.executable


def get_python() -> str:
    """Get the Python executable to use for subprocesses."""
    return sys.executable


def start_detached_process(args: list[str], log_file: str | None = None):
    """Start a detached process (works on Windows, Linux, Mac)."""
    if SYSTEM == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            args,
            stdout=open(log_file, "w") if log_file else subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
            startupinfo=startupinfo,
        )
    else:
        process = subprocess.Popen(
            args,
            stdout=open(log_file, "w") if log_file else subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return process


def read_pid_file(pid_file: str) -> int | None:
    """Read PID from file (cross-platform)."""
    try:
        with open(pid_file) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def write_pid_file(pid_file: str, pid: int):
    """Write PID to file."""
    os.makedirs(os.path.dirname(pid_file) or ".", exist_ok=True)
    with open(pid_file, "w") as f:
        f.write(str(pid))


def kill_process(pid: int):
    """Kill a process by PID (cross-platform)."""
    if SYSTEM == "Windows":
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    else:
        try:
            os.kill(pid, 15)  # SIGTERM
        except ProcessLookupError:
            pass
