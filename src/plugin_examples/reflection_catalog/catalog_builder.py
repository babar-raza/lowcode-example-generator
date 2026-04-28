"""Build and normalize API catalogs from DllReflector output."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from plugin_examples.reflection_catalog.reflector import run_reflector
from plugin_examples.reflection_catalog.schema_validator import validate_catalog

logger = logging.getLogger(__name__)


class CatalogBuildError(Exception):
    """Raised when catalog building fails."""


def build_catalog(
    *,
    dll_path: Path,
    output_path: Path,
    xml_path: Path | None = None,
    dependency_paths: list[Path] | None = None,
    reflector_dir: Path | None = None,
    namespace_filter: list[str] | None = None,
    timeout: int = 120,
) -> dict:
    """Build a validated API catalog from a DLL.

    Args:
        dll_path: Path to the primary DLL.
        output_path: Where to write the final catalog JSON.
        xml_path: Optional XML documentation path.
        dependency_paths: Optional dependency DLL paths.
        reflector_dir: Override DllReflector location.
        namespace_filter: If provided, only include namespaces containing
            any of these substrings (case-insensitive).
        timeout: Subprocess timeout in seconds.

    Returns:
        The validated catalog dict.
    """
    # Run reflector to get raw catalog
    raw_output = output_path.parent / f"{output_path.stem}_raw.json"

    raw_catalog = run_reflector(
        dll_path=dll_path,
        output_path=raw_output,
        xml_path=xml_path,
        dependency_paths=dependency_paths,
        reflector_dir=reflector_dir,
        timeout=timeout,
    )

    # Normalize the catalog
    catalog = _normalize(raw_catalog, namespace_filter=namespace_filter)

    # Validate against schema
    errors = validate_catalog(catalog)
    if errors:
        raise CatalogBuildError(
            f"Catalog validation failed with {len(errors)} error(s):\n"
            + "\n".join(f"  - {e}" for e in errors[:10])
        )

    # Write final catalog
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(catalog, f, indent=2)

    logger.info("Validated catalog written to: %s", output_path)
    return catalog


def _normalize(
    raw: dict,
    *,
    namespace_filter: list[str] | None = None,
) -> dict:
    """Normalize raw DllReflector output.

    - Filter namespaces if filter is provided.
    - Strip obsolete types/methods if desired.
    - Ensure consistent field ordering.
    """
    catalog = {
        "assembly_name": raw.get("assembly_name"),
        "assembly_version": raw.get("assembly_version"),
        "target_framework": raw.get("target_framework"),
        "namespaces": [],
        "diagnostics": raw.get("diagnostics", {}),
    }

    namespaces = raw.get("namespaces", [])

    if namespace_filter:
        filter_lower = [f.lower() for f in namespace_filter]
        namespaces = [
            ns for ns in namespaces
            if any(f in ns.get("namespace", "").lower() for f in filter_lower)
        ]

    for ns in namespaces:
        normalized_ns = {
            "namespace": ns["namespace"],
            "types": [_normalize_type(t) for t in ns.get("types", [])],
        }
        catalog["namespaces"].append(normalized_ns)

    return catalog


def _normalize_type(type_info: dict) -> dict:
    """Normalize a single type entry."""
    result: dict = {
        "name": type_info["name"],
        "full_name": type_info["full_name"],
        "kind": type_info["kind"],
        "is_obsolete": type_info.get("is_obsolete", False),
    }

    if "xml_summary" in type_info:
        result["xml_summary"] = type_info["xml_summary"]

    if type_info["kind"] == "enum":
        result["enum_values"] = type_info.get("enum_values", [])
    else:
        result["constructors"] = type_info.get("constructors", [])
        result["methods"] = type_info.get("methods", [])
        result["properties"] = type_info.get("properties", [])

    return result
