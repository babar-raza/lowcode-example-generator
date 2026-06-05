"""
Output validation helpers for dry-run example packages.

Rules:
- Required outputs must be non-zero bytes.
- Intermediate/fixture files may be zero only if marked intermediate_optional.
- A package cannot PASS if all required outputs are zero or missing.
- Trial/evaluation watermarks are acceptable but must be disclosed.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# File signatures for format verification
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PDF_SIGNATURE = b"%PDF"
ZIP_SIGNATURE = b"PK\x03\x04"
JPEG_SIGNATURE = b"\xff\xd8\xff"
BMP_SIGNATURE = b"BM"


@dataclass
class OutputValidationResult:
    path: str
    size_bytes: int
    format_detected: str = "UNKNOWN"
    signature_valid: bool = False
    is_required: bool = True
    is_intermediate_optional: bool = False
    verdict: str = "UNKNOWN"
    notes: list = field(default_factory=list)

    @property
    def passes(self) -> bool:
        if not self.is_required:
            return True
        if self.is_intermediate_optional:
            return True
        return self.verdict == "PASS"


@dataclass
class PackageValidationResult:
    package_key: str
    package_dir: str
    restore_status: str = "UNKNOWN"
    build_status: str = "UNKNOWN"
    run_status: str = "UNKNOWN"
    output_results: list = field(default_factory=list)
    missing_required_files: list = field(default_factory=list)
    verdict: str = "UNKNOWN"
    publication_classification: str = "UNCLASSIFIED"
    notes: list = field(default_factory=list)

    @property
    def passes(self) -> bool:
        return self.verdict == "PASS"


# Required package files for a valid dry-run package
REQUIRED_PACKAGE_FILES = [
    "Program.cs",
    "README.md",
    "source-provenance.json",
    "output-validation.json",
]

# Files that are intermediate/optional (not required to be non-zero)
# These are working files created during package execution, not final outputs
INTERMEDIATE_OPTIONAL_PATTERNS = [
    "fixture.png",
    "fixture.bmp",
    "fixture.xps",
    "fixture_barcode.png",
    "canvas.bmp",           # imaging/merge-images: blank canvas before drawing
    "source-watermark.bmp", # imaging/watermark-image: source before watermark
    "src1.bmp",             # imaging/merge-images: source 1
    "src2.bmp",             # imaging/merge-images: source 2
]


def detect_format(data: bytes) -> str:
    if data[:8] == PNG_SIGNATURE:
        return "PNG"
    if data[:4] == b"%PDF":
        return "PDF"
    if data[:4] == ZIP_SIGNATURE:
        return "ZIP"
    if data[:3] == JPEG_SIGNATURE:
        return "JPEG"
    if data[:2] == BMP_SIGNATURE:
        return "BMP"
    if data[:5].lower() == b"<svg ":
        return "SVG"
    if data[:9].lower() == b"<!doctype" or data[:5].lower() == b"<html":
        return "HTML"
    if data[:1] == b"{":
        return "JSON"
    # Try UTF-8 text
    try:
        data[:200].decode("utf-8")
        return "TEXT"
    except UnicodeDecodeError:
        return "BINARY"


def validate_output_file(path: Path, is_required: bool = True) -> OutputValidationResult:
    """Validate a single output file."""
    name = path.name
    is_intermediate = any(name == pat for pat in INTERMEDIATE_OPTIONAL_PATTERNS)

    if not path.exists():
        return OutputValidationResult(
            path=str(path),
            size_bytes=0,
            verdict="MISSING",
            is_required=is_required,
            is_intermediate_optional=is_intermediate,
            notes=["File does not exist"],
        )

    size = path.stat().st_size
    if size == 0:
        if is_intermediate:
            return OutputValidationResult(
                path=str(path),
                size_bytes=0,
                verdict="PASS",
                is_required=False,
                is_intermediate_optional=True,
                notes=["Zero-byte intermediate file: acceptable"],
            )
        return OutputValidationResult(
            path=str(path),
            size_bytes=0,
            verdict="ZERO_BYTE_REQUIRED_OUTPUT",
            is_required=is_required,
            notes=["Required output file is zero bytes — FAIL"],
        )

    data = path.read_bytes()
    fmt = detect_format(data)
    sig_valid = fmt not in ("UNKNOWN", "BINARY")

    verdict = "PASS"
    notes = []

    # PDF: check it's a real PDF
    if fmt == "PDF":
        if b"%EOF" not in data and b"%%EOF" not in data and b"endobj" not in data:
            notes.append("PDF structure incomplete (no %%EOF marker)")
            # Still pass if it's non-zero PDF-like
    # PNG: basic structure check
    if fmt == "PNG" and len(data) < 32:
        verdict = "SUSPICIOUS_SMALL"
        notes.append(f"PNG only {size} bytes — may be invalid")
    # ZIP: check readable
    if fmt == "ZIP" and size < 22:
        verdict = "SUSPICIOUS_SMALL"
        notes.append(f"ZIP only {size} bytes — may be invalid")
    # Trial watermark detection (output TXT from OCR)
    if fmt == "TEXT":
        text = data.decode("utf-8", errors="replace").lower()
        if "trial" in text or "evaluation" in text:
            notes.append("TRIAL_WATERMARK_DETECTED: evaluation text present in output")

    return OutputValidationResult(
        path=str(path),
        size_bytes=size,
        format_detected=fmt,
        signature_valid=sig_valid,
        is_required=is_required,
        is_intermediate_optional=is_intermediate,
        verdict=verdict,
        notes=notes,
    )


def validate_package_outputs(pkg_dir: Path, package_key: str) -> PackageValidationResult:
    """Validate all outputs for a dry-run package."""
    result = PackageValidationResult(
        package_key=package_key,
        package_dir=str(pkg_dir),
    )

    # Check required package structure files
    for req_file in REQUIRED_PACKAGE_FILES:
        p = pkg_dir / req_file
        if not p.exists():
            result.missing_required_files.append(req_file)

    # Load output-validation.json if present
    ov_path = pkg_dir / "output-validation.json"
    if ov_path.exists():
        try:
            ov = json.loads(ov_path.read_text(encoding="utf-8"))
            result.restore_status = ov.get("restore_status", "UNKNOWN")
            result.build_status = ov.get("build_status", "UNKNOWN")
            result.run_status = ov.get("run_status", "UNKNOWN")
        except Exception:
            result.notes.append("output-validation.json parse error")

    # Validate output/ directory
    output_dir = pkg_dir / "output"
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                r = validate_output_file(f, is_required=True)
                result.output_results.append(r)

    # Determine verdict
    if result.missing_required_files:
        result.verdict = "MISSING_REQUIRED_FILES"
        result.notes.append(f"Missing: {result.missing_required_files}")
    elif result.restore_status == "FAILED":
        result.verdict = "RESTORE_FAILED"
    elif result.build_status == "FAILED":
        result.verdict = "BUILD_FAILED"
    elif result.run_status == "FAILED":
        result.verdict = "RUN_FAILED"
    elif not result.output_results:
        result.verdict = "NO_OUTPUTS"
    elif (
        any(r.verdict == "ZERO_BYTE_REQUIRED_OUTPUT" for r in result.output_results)
        and not any(r.verdict == "PASS" and r.size_bytes > 0 for r in result.output_results)
    ):
        # Only fail for zero-byte if there are NO non-zero passing output files
        result.verdict = "ZERO_BYTE_REQUIRED_OUTPUT"
    elif any(r.verdict == "MISSING" and r.is_required for r in result.output_results):
        result.verdict = "MISSING_OUTPUT"
    elif all(r.passes for r in result.output_results):
        result.verdict = "PASS"
    else:
        result.verdict = "OUTPUT_VALIDATION_FAILED"

    # Classify for publication readiness
    trial_detected = any(
        "TRIAL_WATERMARK_DETECTED" in (note for note in r.notes)
        for r in result.output_results
    )
    if result.verdict == "PASS" and not trial_detected and not result.missing_required_files:
        result.publication_classification = "PUBLICATION_CANDIDATE_LOCAL_CLEAN"
    elif result.verdict == "PASS" and trial_detected:
        result.publication_classification = "PUBLICATION_CANDIDATE_LOCAL_WITH_TRIAL_NOTICE"
    elif result.verdict in ("ZERO_BYTE_REQUIRED_OUTPUT", "MISSING_OUTPUT", "NO_OUTPUTS"):
        result.publication_classification = "NEEDS_OUTPUT_REPAIR"
    elif result.missing_required_files:
        result.publication_classification = "NEEDS_PROVENANCE_REPAIR"
    else:
        result.publication_classification = "NEEDS_API_REVIEW"

    return result
