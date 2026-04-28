"""Invoke DllReflector .NET tool as a subprocess."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Default path relative to repository root
_DEFAULT_REFLECTOR_DIR = Path(__file__).resolve().parents[3] / "tools" / "DllReflector"


class ReflectorError(Exception):
    """Raised when DllReflector fails."""


def find_reflector_executable(reflector_dir: Path | None = None) -> Path:
    """Locate the DllReflector executable.

    Searches for the built executable under bin/Release/net8.0/.
    Falls back to bin/Debug/net8.0/ if Release not found.

    Returns:
        Path to the DllReflector executable (dll to run via dotnet).
    """
    base = reflector_dir or _DEFAULT_REFLECTOR_DIR
    for config in ("Release", "Debug"):
        candidate = base / "bin" / config / "net8.0" / "DllReflector.dll"
        if candidate.exists():
            return candidate

    raise ReflectorError(
        f"DllReflector not built. Run: dotnet build {base / 'DllReflector.csproj'} -c Release"
    )


def run_reflector(
    *,
    dll_path: Path,
    output_path: Path,
    xml_path: Path | None = None,
    dependency_paths: list[Path] | None = None,
    reflector_dir: Path | None = None,
    timeout: int = 120,
) -> dict:
    """Run DllReflector and return the parsed JSON catalog.

    Args:
        dll_path: Path to the primary DLL to reflect.
        output_path: Where to write the JSON output.
        xml_path: Optional path to XML documentation file.
        dependency_paths: Optional paths to dependency DLLs.
        reflector_dir: Override path to DllReflector project directory.
        timeout: Subprocess timeout in seconds.

    Returns:
        Parsed JSON catalog dict.

    Raises:
        ReflectorError: If DllReflector exits with non-zero or produces invalid JSON.
    """
    exe = find_reflector_executable(reflector_dir)

    cmd = ["dotnet", str(exe), "--dll", str(dll_path), "--output", str(output_path)]

    if xml_path and xml_path.exists():
        cmd.extend(["--xml", str(xml_path)])

    if dependency_paths:
        existing = [str(p) for p in dependency_paths if p.exists()]
        if existing:
            cmd.append("--deps")
            cmd.extend(existing)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Running DllReflector: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        raise ReflectorError(f"DllReflector timed out after {timeout}s") from e

    if result.returncode != 0:
        raise ReflectorError(
            f"DllReflector exited with code {result.returncode}:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    if not output_path.exists():
        raise ReflectorError(
            f"DllReflector completed but output file not found: {output_path}"
        )

    try:
        with open(output_path) as f:
            catalog = json.load(f)
    except json.JSONDecodeError as e:
        raise ReflectorError(f"DllReflector produced invalid JSON: {e}") from e

    logger.info(
        "Reflection catalog generated: %s (%d namespaces)",
        output_path,
        len(catalog.get("namespaces", [])),
    )

    return catalog
