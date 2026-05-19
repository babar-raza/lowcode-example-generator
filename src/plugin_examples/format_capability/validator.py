"""Validate format capability manifest for consistency."""

from __future__ import annotations

from dataclasses import dataclass, field

from plugin_examples.format_capability.manifest import FormatCapabilityManifest


@dataclass
class ValidationIssue:
    """A single validation issue."""

    type_name: str
    severity: str  # "error" | "warning"
    message: str


@dataclass
class ValidationResult:
    """Result of manifest validation."""

    valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)


def validate_manifest(manifest: FormatCapabilityManifest) -> ValidationResult:
    """Validate a FormatCapabilityManifest for internal consistency.

    Checks:
    - Converters should have different input and output formats
    - Transforms should have same input and output
    - Extractors should have empty output format
    - All types should have non-empty input format
    - No .out fallback formats
    """
    result = ValidationResult()

    for type_name, cap in manifest.types.items():
        # No .out fallback
        if cap.primary_output_format == ".out":
            result.valid = False
            result.issues.append(ValidationIssue(
                type_name=type_name,
                severity="error",
                message=f"Output format is .out (fallback) — missing planner map entry",
            ))

        # Converter should have different input/output
        if cap.operation_kind == "converter" and cap.input_format == cap.primary_output_format:
            result.issues.append(ValidationIssue(
                type_name=type_name,
                severity="warning",
                message=f"Converter has same input ({cap.input_format}) and output format",
            ))

        # Extractor should have empty output
        if cap.operation_kind == "extractor" and cap.primary_output_format:
            result.issues.append(ValidationIssue(
                type_name=type_name,
                severity="warning",
                message=f"Extractor has non-empty output format: {cap.primary_output_format}",
            ))

        # Must have input format
        if not cap.input_format:
            result.valid = False
            result.issues.append(ValidationIssue(
                type_name=type_name,
                severity="error",
                message="Missing input format",
            ))

        # Family must match manifest
        if cap.family != manifest.family:
            result.valid = False
            result.issues.append(ValidationIssue(
                type_name=type_name,
                severity="error",
                message=f"Type family ({cap.family}) doesn't match manifest family ({manifest.family})",
            ))

    return result
