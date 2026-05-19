"""Classify operation kind from type name and family."""

from __future__ import annotations

# Ordered patterns — first match wins
_PATTERNS: list[tuple[str, str]] = [
    ("textextractor", "extractor"),
    ("imageextractor", "image_extractor"),
    ("formexporter", "form_exporter"),
    ("formeditor", "form_processor"),
    ("formflattener", "form_processor"),
    ("mailmerger", "generator"),
    ("merger", "merger"),
    ("splitter", "splitter"),
    ("extractor", "extractor"),
    ("compressor", "transform"),
    ("compress", "transform"),
    ("locker", "transform"),
    ("optimizer", "transform"),
    ("pdfaconverter", "transform"),
    ("security", "transform"),
    ("signature", "transform"),
    ("watermarker", "transform"),
    ("replacer", "transform"),
    ("comparer", "transform"),
    ("tocgenerator", "generator"),
    ("tablegenerator", "generator"),
    ("reportbuilder", "generator"),
    ("converter", "converter"),
    ("convert", "converter"),
]

# Exact-match overrides for short PDF type names that lack a suffix
_EXACT_OVERRIDES: dict[str, str] = {
    "html": "converter",
    "jpeg": "converter",
    "png": "converter",
    "tiff": "converter",
}


def classify_operation_kind(type_name: str, family: str = "") -> str:
    """Classify a type into an operation kind.

    Args:
        type_name: Simple type name (e.g., "DocConverter").
        family: Optional family for disambiguation.

    Returns:
        Operation kind string.
    """
    key = type_name.lower()

    # Email Converter is special — directory output
    if family == "email" and key == "converter":
        return "directory_output"

    # Exact-match overrides for short names (Html, Jpeg, Png, Tiff)
    if key in _EXACT_OVERRIDES:
        return _EXACT_OVERRIDES[key]

    for pattern, kind in _PATTERNS:
        if pattern in key:
            return kind

    return "unknown"
