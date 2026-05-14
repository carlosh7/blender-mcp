"""
blender-mcp — Health Check (--doctor)
Inspired by yuri-schmaltz/mcp-blender --doctor
"""
import sys
import os
import shutil
import platform
import subprocess


def check_python():
    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 10
    print(f"  {'✅' if ok else '❌'} Python {v.major}.{v.minor}.{v.micro}")
    return ok


def check_blender():
    blender = shutil.which("blender.exe") or shutil.which("blender")
    if blender:
        try:
            r = subprocess.run([blender, "--version"], capture_output=True, text=True, timeout=10)
            ver = r.stdout.split("\n")[0].strip() if r.stdout else "unknown"
            print(f"  ✅ Blender: {ver}")
            print(f"     Path: {blender}")
            return True
        except:
            pass
    print(f"  ❌ Blender not found")
    return False


def check_mcp_sdk():
    try:
        import mcp
        print(f"  ✅ MCP SDK: {mcp.__version__}")
        return True
    except ImportError:
        print(f"  ❌ MCP SDK not installed (pip install mcp)")
        return False
    except:
        print(f"  ⚠️ MCP SDK: unknown version")
        return True


def check_socket():
    host = os.getenv("BLENDER_HOST", "localhost")
    port = int(os.getenv("BLENDER_PORT", "9876"))
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((host, port))
        print(f"  ✅ Blender socket: {host}:{port} (connected)")
        s.close()
        return True
    except:
        print(f"  ⚠️ Blender socket: {host}:{port} (not responding)")
        return False


def check_disk():
    st = os.statvfs(".")
    mb = (st.f_frsize * st.f_bavail) / (1024 * 1024)
    ok = mb > 500
    print(f"  {'✅' if ok else '⚠️'} Disk: {mb:.0f} MB free")
    return ok


def run_doctor():
    print(f"\n{'='*50}")
    print(f"  blender-mcp — Health Check")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"{'='*50}\n")
    results = [check_python(), check_blender(), check_mcp_sdk(), check_socket(), check_disk()]
    ok = sum(results)
    total = len(results)
    print(f"\n{'='*50}")
    print(f"  {ok}/{total} checks passed")
    print(f"{'='*50}\n")
    return ok == total


if __name__ == "__main__":
    sys.exit(0 if run_doctor() else 1)
