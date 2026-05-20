"""FormatContract store — loads and provides contracts from API authority evidence."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from plugin_examples.format_authority.contracts import FormatContract

logger = logging.getLogger(__name__)

# Default path to the API-backed contracts produced by discover-lowcode
_DEFAULT_CONTRACTS_PATH = (
    Path(__file__).resolve().parents[3]
    / "workspace"
    / "verification"
    / "lowcode-api-format-authority-20260519-153439"
    / "reports"
    / "api-backed-format-contracts.json"
)

# Module-level store: populated on first access or explicitly via load_contracts_from_json()
_store: dict[tuple[str, str], FormatContract] = {}
_loaded: bool = False


class MissingFormatContractError(KeyError):
    """Raised when a FormatContract is not found for a (family, type_name) pair.

    This is a FAIL-CLOSED error. No component should fall back to stale maps
    or .out defaults when this is raised.
    """


def _normalize_from_api_authority(entry: dict) -> dict:
    """Normalize an entry from api-backed-format-contracts.json to FormatContract fields."""
    return {
        "family": entry["family"],
        "type_name": entry["type_name"],
        "operation_kind": entry["operation_kind"],
        "input_format": entry["input_format"],
        "input_cardinality": entry["input_cardinality"],
        "canonical_output_format": entry.get("canonical_output_format", ""),
        "output_cardinality": entry["output_cardinality"],
        "output_kind": entry.get("output_kind", "file"),
        "method_signature": entry.get("method_signature", ""),
        "options_class": entry.get("options_class"),
        "alternate_output_formats": entry.get("alternate_output_formats", []),
        "evidence_confidence": entry.get("evidence_confidence", "api_verified"),
        "notes": entry.get("notes", ""),
    }


def load_contracts_from_json(path: str | Path | None = None) -> int:
    """Load contracts from an API authority JSON file.

    Returns the number of contracts loaded.
    """
    global _store, _loaded
    if path is None:
        path = _DEFAULT_CONTRACTS_PATH
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Format contract authority file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("types", [])
    loaded = 0
    for entry in entries:
        normalized = _normalize_from_api_authority(entry)
        contract = FormatContract.from_dict(normalized)
        errors = contract.validate()
        if errors:
            logger.warning(
                "Skipping invalid contract %s/%s: %s",
                entry.get("family"), entry.get("type_name"), errors,
            )
            continue
        _store[(contract.family, contract.type_name)] = contract
        loaded += 1

    _loaded = True
    logger.info("Loaded %d format contracts from %s", loaded, path)
    return loaded


def _ensure_loaded() -> None:
    """Auto-load contracts from default path on first access."""
    global _loaded
    if not _loaded:
        if _DEFAULT_CONTRACTS_PATH.exists():
            load_contracts_from_json()
        else:
            _loaded = True  # mark loaded to avoid repeated file checks
            logger.warning("No default contract file at %s", _DEFAULT_CONTRACTS_PATH)


def get_contract(family: str, type_name: str) -> FormatContract:
    """Get the FormatContract for a (family, type_name) pair.

    Raises MissingFormatContractError if not found — this is FAIL-CLOSED.
    """
    _ensure_loaded()
    key = (family, type_name)
    if key not in _store:
        raise MissingFormatContractError(
            f"No FormatContract for {family}/{type_name}. "
            f"Cannot fall back to stale maps or .out defaults."
        )
    return _store[key]


def get_all_contracts() -> dict[tuple[str, str], FormatContract]:
    """Return all loaded contracts."""
    _ensure_loaded()
    return dict(_store)


def reset_store() -> None:
    """Reset the store (for testing)."""
    global _store, _loaded
    _store = {}
    _loaded = False
