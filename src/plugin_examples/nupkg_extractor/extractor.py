"""NuGet package extraction: primary DLL, XML docs, and dependency DLLs."""

from __future__ import annotations

import json
import logging
import shutil
import zipfile
from pathlib import Path

from plugin_examples.nupkg_extractor.framework_selector import (
    FrameworkSelection,
    select_framework,
)

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Raised when extraction fails critically (e.g., missing DLL)."""


def extract_package(
    nupkg_path: Path,
    *,
    package_id: str,
    family: str,
    target_framework_preference: list[str],
    run_dir: Path,
    dependency_nupkgs: list[Path] | None = None,
) -> dict:
    """Extract a primary .nupkg and its dependencies.

    Args:
        nupkg_path: Path to the primary .nupkg file.
        package_id: NuGet package ID (e.g., "Aspose.Cells").
        family: Family name (e.g., "cells").
        target_framework_preference: Ordered TFM preference list.
        run_dir: Path to workspace/runs/{run_id}/.
        dependency_nupkgs: Paths to dependency .nupkg files.

    Returns:
        The extraction manifest dict.
    """
    extract_base = run_dir / "extracted" / family
    primary_dir = extract_base / "primary"
    warnings_path = extract_base / "warnings.json"
    manifest_path = extract_base / "extraction-manifest.json"

    # Extract primary .nupkg
    primary_dir.mkdir(parents=True, exist_ok=True)
    _unzip(nupkg_path, primary_dir)

    # Enumerate available frameworks from lib/ folder
    lib_dir = primary_dir / "lib"
    available_frameworks = _list_frameworks(lib_dir)

    # Select framework
    selection = select_framework(available_frameworks, target_framework_preference)
    logger.info(
        "Selected framework %s for %s: %s",
        selection.selected_framework,
        package_id,
        selection.selection_reason,
    )

    # Locate DLL and XML
    fw_dir = lib_dir / selection.selected_framework
    dll_path = _find_file(fw_dir, f"{package_id}.dll")
    xml_path = _find_file_optional(fw_dir, f"{package_id}.xml")

    if dll_path is None:
        raise ExtractionError(
            f"DLL not found: {package_id}.dll in {fw_dir}. "
            f"Available files: {list(fw_dir.iterdir()) if fw_dir.exists() else []}"
        )

    # Write warning if XML is missing
    warnings: list[dict] = []
    xml_warning = None
    if xml_path is None:
        xml_warning = (
            f"XML documentation not found: {package_id}.xml in {fw_dir}"
        )
        warnings.append({
            "type": "missing_xml_documentation",
            "package_id": package_id,
            "framework": selection.selected_framework,
            "message": xml_warning,
        })
        logger.warning(xml_warning)

    if warnings:
        _write_json(warnings_path, warnings)

    # Extract dependencies
    dep_dll_paths: list[str] = []
    extracted_dep_paths: list[str] = []

    if dependency_nupkgs:
        deps_dir = extract_base / "deps"
        resolved_libs_dir = extract_base / "resolved-libs"
        resolved_libs_dir.mkdir(parents=True, exist_ok=True)

        for dep_nupkg in dependency_nupkgs:
            dep_result = _extract_dependency(
                dep_nupkg,
                deps_dir=deps_dir,
                resolved_libs_dir=resolved_libs_dir,
                target_framework_preference=target_framework_preference,
            )
            if dep_result:
                dep_dll_paths.append(dep_result["dll_path"])
                extracted_dep_paths.append(dep_result["extracted_path"])

    # Build and write manifest
    manifest = {
        "package_id": package_id,
        "family": family,
        "selected_framework": selection.selected_framework,
        "framework_selection_reason": selection.selection_reason,
        "requires_windows_runner": selection.requires_windows_runner,
        "dll_path": str(dll_path),
        "xml_path": str(xml_path) if xml_path else None,
        "xml_warning": xml_warning,
        "dependency_dll_paths": dep_dll_paths,
        "extracted_primary_path": str(primary_dir),
        "extracted_dependency_paths": extracted_dep_paths,
    }

    _write_json(manifest_path, manifest)
    logger.info("Wrote extraction manifest: %s", manifest_path)

    return manifest


def _extract_dependency(
    dep_nupkg: Path,
    *,
    deps_dir: Path,
    resolved_libs_dir: Path,
    target_framework_preference: list[str],
) -> dict | None:
    """Extract a single dependency .nupkg and copy its DLL to resolved-libs."""
    # Derive dep_id from filename: "Dep.One.2.0.0.nupkg" → "Dep.One"
    stem = dep_nupkg.stem  # "Dep.One.2.0.0"
    parts = stem.split(".")
    # Find where the version starts (first part that's a digit)
    dep_id_parts = []
    for part in parts:
        if part.isdigit() and dep_id_parts:
            break
        dep_id_parts.append(part)
    dep_id = ".".join(dep_id_parts) if dep_id_parts else stem

    dep_extract_dir = deps_dir / dep_id
    dep_extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        _unzip(dep_nupkg, dep_extract_dir)
    except Exception as e:
        logger.warning("Failed to extract dependency %s: %s", dep_nupkg, e)
        return None

    lib_dir = dep_extract_dir / "lib"
    available = _list_frameworks(lib_dir)

    if not available:
        logger.warning("No lib/ frameworks found in dependency %s", dep_id)
        return None

    try:
        selection = select_framework(available, target_framework_preference)
    except ValueError:
        logger.warning(
            "No compatible framework for dependency %s (available: %s)",
            dep_id,
            available,
        )
        return None

    fw_dir = lib_dir / selection.selected_framework
    dll_path = _find_file(fw_dir, f"{dep_id}.dll")

    if dll_path is None:
        # Try any .dll in the framework folder
        dlls = list(fw_dir.glob("*.dll"))
        if dlls:
            dll_path = dlls[0]
        else:
            logger.warning("No DLL found for dependency %s in %s", dep_id, fw_dir)
            return None

    # Copy to resolved-libs
    resolved_dll = resolved_libs_dir / dll_path.name
    shutil.copy2(dll_path, resolved_dll)

    return {
        "dll_path": str(resolved_dll),
        "extracted_path": str(dep_extract_dir),
    }


def _unzip(zip_path: Path, dest: Path) -> None:
    """Extract a zip file to a destination directory."""
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)


def _list_frameworks(lib_dir: Path) -> list[str]:
    """List available TFM folders under lib/."""
    if not lib_dir.exists():
        return []
    return [d.name for d in lib_dir.iterdir() if d.is_dir()]


def _find_file(directory: Path, filename: str) -> Path | None:
    """Find a file by exact name (case-insensitive) in a directory."""
    if not directory.exists():
        return None
    lower = filename.lower()
    for f in directory.iterdir():
        if f.is_file() and f.name.lower() == lower:
            return f
    return None


def _find_file_optional(directory: Path, filename: str) -> Path | None:
    """Same as _find_file but expected to sometimes return None."""
    return _find_file(directory, filename)


def _write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
