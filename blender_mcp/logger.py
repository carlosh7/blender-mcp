"""
blender-mcp — Configurable Logging (cross-platform)
"""
import os
import sys
import logging
from pathlib import Path
from .platform import get_log_dir

LOG_LEVEL = os.getenv("BLENDER_MCP_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("BLENDER_MCP_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_HANDLER = os.getenv("BLENDER_MCP_LOG_HANDLER", "console")
LOG_FILE = os.getenv("BLENDER_MCP_LOG_FILE", str(get_log_dir() / "blender-mcp.log"))


def setup_logger(name="blender-mcp"):
    """Create and configure a logger instance."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    if LOG_HANDLER == "file":
        p = Path(LOG_FILE)
        p.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(str(p))
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger
