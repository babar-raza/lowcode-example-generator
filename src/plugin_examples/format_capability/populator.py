"""Populate format capability manifest from planner maps and config."""

from __future__ import annotations

from datetime import datetime, timezone

from plugin_examples.format_capability.manifest import (
    FormatCapabilityManifest,
    TypeFormatCapability,
)
from plugin_examples.format_capability.classifier import classify_operation_kind
from plugin_examples.scenario_planner.planner import (
    _infer_input_format,
    _infer_output_format,
)


# Family defaults from pipeline configs
_FAMILY_DEFAULTS: dict[str, str] = {
    "cells": ".xlsx",
    "words": ".docx",
    "pdf": ".pdf",
    "diagram": ".vsdx",
    "email": ".eml",
    "slides": ".pptx",
}

# Active types per family
_ACTIVE_TYPES: dict[str, list[str]] = {
    "cells": [
        "SpreadsheetConverter", "JsonConverter", "HtmlConverter", "TextConverter",
        "ImageConverter", "SpreadsheetMerger", "SpreadsheetSplitter",
        "SpreadsheetLocker", "PdfConverter",
    ],
    "words": [
        "Converter", "Merger", "Splitter", "Comparer",
        "MailMerger", "ReportBuilder", "Watermarker", "Replacer",
    ],
    "pdf": [
        "DocConverter", "XlsConverter", "Html", "Jpeg", "Png", "Tiff",
        "TextExtractor", "Merger", "Splitter", "Optimizer", "PdfAConverter",
        "TocGenerator", "TableGenerator", "ImageExtractor", "Security",
        "FormFlattener", "FormEditor", "FormExporter", "Signature",
    ],
    "diagram": ["DiagramConverter", "PdfConverter"],
    "email": ["Converter"],
    "slides": ["Convert", "Merger", "Compress"],
}

# Types that use template_first
_TEMPLATE_FIRST_TYPES: set[str] = {
    "DocConverter", "XlsConverter", "Html", "Jpeg", "Png", "Tiff",
    "Merger", "Splitter", "Optimizer", "PdfAConverter",
    "TocGenerator", "TableGenerator", "ImageExtractor", "Security",
    "FormFlattener", "FormEditor", "FormExporter", "Signature",
}


def _infer_cardinality(op_kind: str) -> tuple[str, str]:
    """Return (input_cardinality, output_cardinality) for an operation kind."""
    if op_kind == "merger":
        return ("multi", "single")
    if op_kind == "splitter":
        return ("single", "multi")
    if op_kind in ("extractor",):
        return ("single", "none")
    if op_kind == "image_extractor":
        return ("single", "multi")
    if op_kind == "directory_output":
        return ("single", "single")
    return ("single", "single")


def _infer_output_kind(op_kind: str) -> str:
    """Return output_kind for an operation kind."""
    if op_kind == "extractor":
        return "stdout"
    if op_kind == "directory_output":
        return "directory"
    return "file"


def populate_manifest(family: str) -> FormatCapabilityManifest:
    """Populate a FormatCapabilityManifest for a given family.

    Uses planner maps as the authoritative source for input/output formats.
    """
    if family not in _ACTIVE_TYPES:
        raise ValueError(f"Unknown family: {family}")

    family_default = _FAMILY_DEFAULTS[family]
    types: dict[str, TypeFormatCapability] = {}

    for type_name in _ACTIVE_TYPES[family]:
        op_kind = classify_operation_kind(type_name, family)
        input_fmt = _infer_input_format(type_name, family_default, family)
        output_fmt = _infer_output_format(type_name, family_default, family)
        in_card, out_card = _infer_cardinality(op_kind)
        out_kind = _infer_output_kind(op_kind)
        is_template_first = (
            family == "pdf" and type_name in _TEMPLATE_FIRST_TYPES
        )

        types[type_name] = TypeFormatCapability(
            family=family,
            type_name=type_name,
            operation_kind=op_kind,
            input_format=input_fmt,
            input_cardinality=in_card,
            primary_output_format=output_fmt,
            output_cardinality=out_card,
            output_kind=out_kind,
            template_first=is_template_first,
            evidence_confidence="verified" if not is_template_first else "inferred",
        )

    return FormatCapabilityManifest(
        family=family,
        generation_date=datetime.now(timezone.utc).isoformat(),
        types=types,
    )
