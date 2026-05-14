"""
blender-mcp — Run tool-code via ``blender --background``.
Analyze .blend files without a running Blender instance.
"""
import json
import os
import subprocess
from . import platform

_BLENDER_PATH_ENV = "BLENDER_PATH"
_RESULT_PREFIX = "__BLMCP_RESULT__"
_ERROR_PREFIX = "__BLMCP_ERROR__"
_CLI_TIMEOUT = 120.0


def _get_blender_path() -> str:
    return os.environ.get(_BLENDER_PATH_ENV, "blender")


def run_blender_cli(blend_file: str, code: str, timeout: float = _CLI_TIMEOUT) -> dict:
    blender = _get_blender_path()
    wrapper = (
        "import json\n"
        "try:\n"
        "    _ns = {'result': {}}\n"
        "    exec({!r}, _ns)\n"
        "    _result = _ns['result']\n"
        "    if not isinstance(_result, dict):\n"
        "        raise TypeError('result must be a dict, not ' + type(_result).__name__)\n"
        '    print("{:s}" + json.dumps(_result, default=repr))\n'
        "except Exception as ex:\n"
        '    print("{:s}" + json.dumps(str(ex)))\n'
    ).format(code, _RESULT_PREFIX, _ERROR_PREFIX)
    try:
        proc = subprocess.run(
            [blender, "--background", blend_file, "--python-expr", wrapper],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as ex:
        raise RuntimeError(f"Blender CLI timed out after {timeout:.0f}s") from ex
    except FileNotFoundError as ex:
        raise RuntimeError(
            f"Blender not found at '{blender}'. Set {_BLENDER_PATH_ENV} env var."
        ) from ex

    for line in proc.stdout.splitlines():
        if line.startswith(_RESULT_PREFIX):
            result = json.loads(line[len(_RESULT_PREFIX):])
            if not isinstance(result, dict):
                raise TypeError(f"Expected dict from Blender CLI, got {type(result)}")
            return result
        if line.startswith(_ERROR_PREFIX):
            raise RuntimeError(f"Blender CLI error: {json.loads(line[len(_ERROR_PREFIX):])}")

    raise RuntimeError(f"No result marker in Blender CLI output.\nstdout: {proc.stdout}\nstderr: {proc.stderr}")
