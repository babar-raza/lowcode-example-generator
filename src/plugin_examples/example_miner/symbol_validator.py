"""Validate mined example symbols against the reflected API catalog."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SymbolValidationResult:
    """Result of validating symbols against the catalog."""
    example_id: str
    valid_symbols: list[str] = field(default_factory=list)
    invalid_symbols: list[str] = field(default_factory=list)
    stale: bool = False
    stale_reason: str | None = None

    @property
    def is_valid(self) -> bool:
        return len(self.invalid_symbols) == 0 and len(self.valid_symbols) > 0


def validate_symbols(
    used_symbols: list[str],
    catalog: dict,
    example_id: str = "unknown",
) -> SymbolValidationResult:
    """Validate symbols against the API catalog.

    Args:
        used_symbols: List of symbol references from mined code.
        catalog: API catalog dict.
        example_id: ID of the example being validated.

    Returns:
        SymbolValidationResult with valid/invalid symbol lists.
    """
    catalog_symbols = _build_symbol_set(catalog)
    result = SymbolValidationResult(example_id=example_id)

    for symbol in used_symbols:
        if symbol in catalog_symbols:
            result.valid_symbols.append(symbol)
        else:
            result.invalid_symbols.append(symbol)

    if result.invalid_symbols:
        result.stale = True
        result.stale_reason = (
            f"Symbols not found in catalog: {', '.join(result.invalid_symbols[:5])}"
        )

    logger.debug(
        "Symbol validation for %s: %d valid, %d invalid",
        example_id, len(result.valid_symbols), len(result.invalid_symbols),
    )
    return result


def _build_symbol_set(catalog: dict) -> set[str]:
    """Build a set of all known symbols from the catalog."""
    symbols: set[str] = set()

    for ns in catalog.get("namespaces", []):
        ns_name = ns.get("namespace", "")
        symbols.add(ns_name)

        for t in ns.get("types", []):
            symbols.add(t["full_name"])
            symbols.add(t["name"])

            for m in t.get("methods", []):
                symbols.add(f"{t['full_name']}.{m['name']}")

            for p in t.get("properties", []):
                symbols.add(f"{t['full_name']}.{p['name']}")

    return symbols
