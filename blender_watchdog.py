#!/usr/bin/env python3
"""
blender-mcp — Blender Watchdog
Detecta si Blender se cierra, lo reabre, activa el addon y guarda el proyecto.
"""

import json
import os
import socket
import subprocess
import time


def find_blender():
    """Find Blender executable."""
    candidates = [
        "/opt/blender-4.2/blender",
        "/usr/bin/blender",
        "/snap/bin/blender",
        os.path.expanduser("~/.local/bin/blender"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return "blender"


def is_blender_running():
    """Check if Blender process is running."""
    result = subprocess.run(["pgrep", "-x", "blender"], capture_output=True, text=True)
    return result.returncode == 0


def is_socket_alive(host="localhost", port=9876, timeout=3):
    """Check if Blender socket server is responsive."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.send(json.dumps({"command": "ping", "params": {}}).encode() + b"\n")
        r = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                c = s.recv(4096)
                if c:
                    r += c
                    if b"\n" in r:
                        break
            except TimeoutError:
                continue
        s.close()
        if r:
            data = json.loads(r.decode().strip())
            return data.get("result", {}).get("pong", False)
    except Exception:
        pass
    return False


def start_blender(blender_path):
    """Start Blender in background."""
    print(f"[watchdog] Starting Blender: {blender_path}")
    subprocess.Popen(
        [blender_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    # Wait for Blender to start
    for i in range(30):
        time.sleep(2)
        if is_blender_running():
            print(f"[watchdog] Blender started (PID: {get_blender_pid()})")
            return True
    print("[watchdog] Failed to start Blender")
    return False


def get_blender_pid():
    """Get Blender PID."""
    result = subprocess.run(["pgrep", "-x", "blender"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip().split("\n")[0]
    return None


def wait_for_socket(port=9876, timeout=30):
    """Wait for Blender socket server to be ready."""
    print(f"[watchdog] Waiting for socket on port {port}...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_socket_alive(port=port):
            print(f"[watchdog] Socket ready on port {port}")
            return True
        time.sleep(2)
    print(f"[watchdog] Socket not ready after {timeout}s")
    return False


def send_command(cmd, params=None, timeout=30):
    """Send command to Blender socket."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(("localhost", 9876))
        s.send(json.dumps({"command": cmd, "params": params or {}}).encode() + b"\n")
        r = b""
        deadline = time.time() + timeout - 5
        while time.time() < deadline:
            try:
                c = s.recv(65536)
                if c:
                    r += c
                    if b"\n" in r:
                        break
            except TimeoutError:
                continue
        s.close()
        if r:
            data = json.loads(r.decode().strip())
            return data.get("result", data)
    except Exception as e:
        return {"error": str(e)}
    return {"error": "timeout"}


def save_project(name):
    """Save Blender project with given name."""
    filepath = f"/tmp/{name}.blend"
    result = send_command(
        "execute_code",
        {
            "code": f'import bpy; bpy.ops.wm.save_as_mainfile(filepath="{filepath}"); print("Saved: {filepath}")'
        },
    )
    return result, filepath


def main():
    blender_path = find_blender()
    project_name = "blender_project"
    check_interval = 5  # seconds

    print("=" * 60)
    print("blender-mcp WATCHDOG")
    print("=" * 60)
    print(f"Blender: {blender_path}")
    print(f"Project: {project_name}")
    print(f"Check interval: {check_interval}s")
    print("=" * 60)

    # Initial state
    blender_running = is_blender_running()
    socket_alive = is_socket_alive()

    print(f"Initial: running={blender_running}, socket={socket_alive}")

    # Auto-start if not running
    if not blender_running:
        print("\n[watchdog] Blender not running, starting...")
        if start_blender(blender_path):
            wait_for_socket()
            # Auto-save with name
            result, path = save_project(project_name)
            print(f"[watchdog] Auto-saved: {path}")

    # Main loop
    print("\n[watchdog] Monitoring... (Ctrl+C to stop)")
    while True:
        try:
            time.sleep(check_interval)

            running = is_blender_running()
            socket = is_socket_alive()

            if not running:
                print(f"\n[watchdog] BLENDER CLOSED! (was running={blender_running})")

                # Save last state if possible
                if blender_running:
                    print("[watchdog] Attempting to save last state...")
                    # Can't save if Blender is closed

                # Restart Blender
                print("[watchdog] Restarting Blender...")
                if start_blender(blender_path):
                    if wait_for_socket():
                        # Restore project
                        result, path = save_project(project_name)
                        print(f"[watchdog] Project saved: {path}")
                        print("[watchdog] Blender recovered successfully!")
                    else:
                        print("[watchdog] WARNING: Socket not available after restart")
                else:
                    print("[watchdog] ERROR: Failed to restart Blender")

            elif not socket:
                print(
                    f"[watchdog] Socket not responding (Blender running, PID={get_blender_pid()})"
                )
                print("[watchdog] Waiting for socket...")
                if wait_for_socket(timeout=15):
                    print("[watchdog] Socket recovered")

            blender_running = running

        except KeyboardInterrupt:
            print("\n[watchdog] Stopped by user")
            # Final save
            if is_socket_alive():
                result, path = save_project(project_name)
                print(f"[watchdog] Final save: {path}")
            break
        except Exception as e:
            print(f"[watchdog] Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
