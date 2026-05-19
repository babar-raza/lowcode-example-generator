"""Dataclasses for format capability manifest."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TypeFormatCapability:
    """Format capability for a single workflow-root type."""

    family: str
    type_name: str
    operation_kind: str  # converter|transform|merger|splitter|extractor|image_extractor|directory_output|generator|form_processor|form_exporter
    input_format: str  # e.g. ".pdf", ".xlsx"
    input_cardinality: str  # "single" | "multi"
    primary_output_format: str  # e.g. ".docx", "" for extractors
    output_cardinality: str  # "single" | "multi" | "none"
    output_kind: str  # "file" | "directory" | "stdout" | "string"
    alternate_output_formats: list[str] = field(default_factory=list)
    template_first: bool = False
    evidence_confidence: str = "inferred"  # "verified" | "inferred" | "unknown"


@dataclass
class FormatCapabilityManifest:
    """Complete format capability manifest for a family."""

    family: str
    generation_date: str = ""
    types: dict[str, TypeFormatCapability] = field(default_factory=dict)
