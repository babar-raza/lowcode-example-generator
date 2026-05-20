"""FormatContract store — loads contracts from repo-local format authority.

The default authority path is pipeline/format-authority/manifest.json relative
to the repository root. This file MUST be present in any checkout that uses
the pipeline in production mode. Missing authority is FATAL.

No hardcoded workspace run IDs. No fallback maps.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from plugin_examples.format_authority.contracts import FormatContract

logger = logging.getLogger(__name__)

# Repo root: 3 levels up from this file (src/plugin_examples/format_authority/store.py)
_REPO_ROOT = Path(__file__).resolve().parents[3]

# Default path to the repo-local format authority manifest
_DEFAULT_MANIFEST_PATH = _REPO_ROOT / "pipeline" / "format-authority" / "manifest.json"

# Module-level store
_store: dict[tuple[str, str], FormatContract] = {}
_loaded: bool = False
_manifest_path_used: Path | None = None


class MissingFormatContractError(KeyError):
    """Raised when a FormatContract is not found for a (family, type_name) pair.

    This is a FAIL-CLOSED error. No component should fall back to stale maps
    or .out defaults when this is raised.
    """


def _normalize_from_repo_local(entry: dict) -> dict:
    """Normalize an entry from repo-local format authority to FormatContract fields."""
    # Extract canonical_output_format — may be a real extension or a kind like "directory"/"stdout"
    canonical = entry.get("canonical_output_format", "")
    output_kind = entry.get("output_kind", "file")

    # For stdout types, canonical should be empty
    if output_kind == "stdout":
        canonical = ""

    # Extract input format from input_artifacts if present, else from input_format
    input_format = entry.get("input_format", "")
    if not input_format and "input_artifacts" in entry:
        artifacts = entry["input_artifacts"]
        if artifacts:
            input_format = artifacts[0].get("format", "")

    # Extract input cardinality
    input_cardinality = entry.get("input_cardinality", "single")
    if not entry.get("input_cardinality") and "input_artifacts" in entry:
        artifacts = entry["input_artifacts"]
        if artifacts:
            input_cardinality = artifacts[0].get("cardinality", "single")

    # Extract output cardinality
    output_cardinality = entry.get("output_cardinality", "single")

    # Extract alternate formats from variants
    alt_fmts = entry.get("alternate_output_formats", [])
    if not alt_fmts and "variants" in entry:
        for v in entry["variants"]:
            if not v.get("is_canonical", False):
                vfmt = v.get("output_format", "")
                if vfmt and vfmt not in alt_fmts:
                    alt_fmts.append(vfmt)

    return {
        "family": entry["family"],
        "type_name": entry["type_name"],
        "operation_kind": entry["operation_kind"],
        "input_format": input_format,
        "input_cardinality": input_cardinality,
        "canonical_output_format": canonical,
        "output_cardinality": output_cardinality,
        "output_kind": output_kind,
        "method_signature": entry.get("method_signature", ""),
        "options_class": entry.get("options_class"),
        "alternate_output_formats": alt_fmts,
        "evidence_confidence": entry.get("evidence_confidence", "api_verified"),
        "notes": entry.get("conflict_notes", entry.get("notes", "")),
    }


def load_contracts_from_json(path: str | Path | None = None) -> int:
    """Load contracts from a format authority JSON file or manifest.

    If path points to a manifest.json, loads all referenced family files.
    If path points to a single contracts file, loads that directly.

    Returns the number of contracts loaded.
    """
    global _store, _loaded, _manifest_path_used
    if path is None:
        path = _DEFAULT_MANIFEST_PATH
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Format authority not found: {path}\n"
            f"The repo-local format authority at pipeline/format-authority/ is required. "
            f"Run the format authority builder or check your checkout."
        )

    _manifest_path_used = path

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    total_loaded = 0

    # If this is a manifest, load each family file
    if "families" in data and "types" not in data:
        manifest_dir = path.parent
        for fam_name, fam_info in data["families"].items():
            fam_file = manifest_dir / fam_info["file"]
            if not fam_file.exists():
                logger.error("Family file missing: %s", fam_file)
                continue
            with open(fam_file, encoding="utf-8") as ff:
                fam_data = json.load(ff)
            for entry in fam_data.get("types", []):
                normalized = _normalize_from_repo_local(entry)
                contract = FormatContract.from_dict(normalized)
                errors = contract.validate()
                if errors:
                    logger.warning(
                        "Skipping invalid contract %s/%s: %s",
                        entry.get("family"), entry.get("type_name"), errors,
                    )
                    continue
                _store[(contract.family, contract.type_name)] = contract
                total_loaded += 1
    # If this is a flat contracts file (legacy format from API authority)
    elif "types" in data:
        for entry in data["types"]:
            normalized = _normalize_from_repo_local(entry)
            contract = FormatContract.from_dict(normalized)
            errors = contract.validate()
            if errors:
                logger.warning(
                    "Skipping invalid contract %s/%s: %s",
                    entry.get("family"), entry.get("type_name"), errors,
                )
                continue
            _store[(contract.family, contract.type_name)] = contract
            total_loaded += 1

    _loaded = True
    logger.info("Loaded %d format contracts from %s", total_loaded, path)
    return total_loaded


def _ensure_loaded() -> None:
    """Auto-load contracts from default repo-local path on first access."""
    global _loaded
    if not _loaded:
        if _DEFAULT_MANIFEST_PATH.exists():
            load_contracts_from_json()
        else:
            _loaded = True  # prevent repeated checks
            logger.error(
                "FATAL: No repo-local format authority at %s. "
                "FormatContract store is empty. All contract lookups will fail closed.",
                _DEFAULT_MANIFEST_PATH,
            )


def get_contract(family: str, type_name: str) -> FormatContract:
    """Get the FormatContract for a (family, type_name) pair.

    Raises MissingFormatContractError if not found — this is FAIL-CLOSED.
    No fallback to stale maps or .out defaults.
    """
    _ensure_loaded()
    key = (family, type_name)
    if key not in _store:
        raise MissingFormatContractError(
            f"No FormatContract for {family}/{type_name}. "
            f"Cannot fall back to stale maps or .out defaults. "
            f"Check pipeline/format-authority/ for missing entries."
        )
    return _store[key]


def get_all_contracts() -> dict[tuple[str, str], FormatContract]:
    """Return all loaded contracts."""
    _ensure_loaded()
    return dict(_store)


def reset_store() -> None:
    """Reset the store (for testing)."""
    global _store, _loaded, _manifest_path_used
    _store = {}
    _loaded = False
    _manifest_path_used = None
