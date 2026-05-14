#!/usr/bin/env python3
"""
blender-mcp CLI — Entry point for `uvx blender-mcp`.
Supports: stdio, sse, doctor, version, start, stop, restart
Cross-platform (Windows, Linux, Mac).
"""
import sys
import os
import time
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="blender-mcp: AI-powered Blender control via MCP")
    parser.add_argument("--mode", choices=["stdio", "sse"], default="stdio",
                        help="Transport mode (default: stdio)")
    parser.add_argument("--port", type=int, default=9879,
                        help="Port for SSE mode (default: 9879)")
    parser.add_argument("--host", type=str, default="127.0.0.1",
                        help="Host for SSE mode (default: 127.0.0.1)")
    parser.add_argument("--doctor", action="store_true",
                        help="Run health check and exit")
    parser.add_argument("--version", action="store_true",
                        help="Print version and exit")

    # Subcommands for process management
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("start", help="Start the MCP server in background")
    subparsers.add_parser("stop", help="Stop the background MCP server")
    subparsers.add_parser("restart", help="Restart the background MCP server")

    args = parser.parse_args()

    if args.command == "start":
        return _cmd_start()
    elif args.command == "stop":
        return _cmd_stop()
    elif args.command == "restart":
        _cmd_stop()
        time.sleep(1)
        return _cmd_start()

    if args.version:
        from blender_mcp import __version__
        print(f"blender-mcp v{__version__}")
        sys.exit(0)

    if args.doctor:
        from blender_mcp.doctor import run_doctor
        sys.exit(0 if run_doctor() else 1)

    if args.mode == "stdio":
        os.environ.setdefault("BLENDER_MCP_MODE", "stdio")
        from mcp_server import main as server_main
        server_main()
    elif args.mode == "sse":
        os.environ.setdefault("BLENDER_MCP_MODE", "sse")
        os.environ.setdefault("BLENDER_MCP_PORT", str(args.port))
        from mcp_server import main as server_main
        server_main()


def _cmd_start():
    """Start the MCP server as a detached process (cross-platform)."""
    from blender_mcp.platform import start_detached_process, write_pid_file, get_log_dir

    root = Path(__file__).parent.parent.parent.resolve()
    server_script = root / "mcp_server.py"
    log_dir = get_log_dir()
    log_file = str(log_dir / "server.log")

    if not server_script.exists():
        print(f"❌ Server script not found: {server_script}")
        return 1

    # Check if already running
    pid_file = str(root / ".mcp_server.pid")
    from blender_mcp.platform import read_pid_file, kill_process
    old_pid = read_pid_file(pid_file)
    if old_pid:
        try:
            kill_process(old_pid)
            time.sleep(0.5)
        except:
            pass

    process = start_detached_process(
        [sys.executable, str(server_script)],
        log_file=log_file,
    )
    write_pid_file(pid_file, process.pid)
    print(f"✅ blender-mcp server started (PID {process.pid})")
    print(f"   Log: {log_file}")
    return 0


def _cmd_stop():
    """Stop the background MCP server (cross-platform)."""
    from blender_mcp.platform import read_pid_file, kill_process

    root = Path(__file__).parent.parent.parent.resolve()
    pid_file = str(root / ".mcp_server.pid")
    pid = read_pid_file(pid_file)

    if pid:
        try:
            kill_process(pid)
            print(f"✅ Server stopped (PID {pid})")
        except Exception as e:
            print(f"⚠️ Could not stop PID {pid}: {e}")
        try:
            os.remove(pid_file)
        except:
            pass
    else:
        print("ℹ️  No server PID file found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
