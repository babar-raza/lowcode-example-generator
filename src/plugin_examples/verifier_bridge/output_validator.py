"""Validate output of generated example runs.

Includes both stdout/stderr validation and semantic file output validation.
"""

from __future__ import annotations

import json
import logging
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class OutputValidation:
    """Result of output validation."""
    scenario_id: str
    passed: bool = False
    has_output: bool = False
    has_error: bool = False
    output_length: int = 0
    issues: list[str] = field(default_factory=list)


def load_expected_output(project_dir: Path) -> dict | None:
    """Load expected-output.json from a project directory."""
    path = project_dir / "expected-output.json"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def validate_output(
    scenario_id: str,
    stdout: str,
    stderr: str,
    *,
    expected_patterns: list[str] | None = None,
    expected_output: dict | None = None,
) -> OutputValidation:
    """Validate the output of a generated example run.

    Args:
        scenario_id: Scenario identifier.
        stdout: Standard output from the run.
        stderr: Standard error from the run.
        expected_patterns: Optional patterns to check in output.

    Returns:
        OutputValidation result.
    """
    result = OutputValidation(
        scenario_id=scenario_id,
        has_output=len(stdout.strip()) > 0,
        output_length=len(stdout),
    )

    # Check for error indicators in stderr
    if stderr and any(kw in stderr.lower() for kw in ["exception", "error", "fatal"]):
        result.has_error = True
        result.issues.append(f"Error output detected: {stderr[:200]}")

    # Check for unhandled exceptions in stdout
    if "Unhandled exception" in stdout:
        result.has_error = True
        result.issues.append("Unhandled exception in output")

    if not result.has_output:
        result.issues.append("No output produced")

    # Check expected patterns (legacy parameter)
    if expected_patterns:
        for pattern in expected_patterns:
            if pattern not in stdout:
                result.issues.append(f"Missing expected output: {pattern}")

    # Check expected-output.json constraints
    if expected_output:
        for must in expected_output.get("must_contain", []):
            if must not in stdout:
                result.issues.append(f"Missing required output: {must}")
        for must_not in expected_output.get("must_not_contain", []):
            if must_not in stdout:
                result.has_error = True
                result.issues.append(f"Forbidden output found: {must_not}")
        if expected_output.get("has_output", True) and not result.has_output:
            result.issues.append("Expected output but got none")

    result.passed = not result.has_error and result.has_output and len(result.issues) == 0

    return result


def write_output_validation(
    validation: OutputValidation,
    run_dir: Path,
) -> Path:
    """Write output validation result for a scenario."""
    val_dir = run_dir / "validation" / validation.scenario_id
    val_dir.mkdir(parents=True, exist_ok=True)
    path = val_dir / "output-validation.json"

    data = {
        "scenario_id": validation.scenario_id,
        "passed": validation.passed,
        "has_output": validation.has_output,
        "has_error": validation.has_error,
        "output_length": validation.output_length,
        "issues": validation.issues,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path


# ---------------------------------------------------------------------------
# Semantic output file validation
# ---------------------------------------------------------------------------

KNOWN_FIXTURE_VALUES = ("Aspose", "LowCode", "Fixture")


def validate_output_file_semantic(
    output_path: Path,
    expected_output: dict | None = None,
) -> dict:
    """Validate an output file with semantic checks.

    Args:
        output_path: Path to the output file.
        expected_output: Expected output specification from expected-output.json.

    Returns:
        Dict with validation results including per-check details.
    """
    result: dict = {
        "output_path": str(output_path),
        "file_exists": output_path.exists(),
        "checks": [],
        "passed": False,
    }

    if not output_path.exists():
        result["checks"].append({"check": "file_exists", "passed": False, "detail": "File not found"})
        return result

    size = output_path.stat().st_size
    result["file_size"] = size
    ext = output_path.suffix.lower()
    result["extension"] = ext

    min_bytes = (expected_output or {}).get("min_bytes", 1)
    result["checks"].append({
        "check": "min_bytes",
        "passed": size >= min_bytes,
        "detail": f"Size {size} bytes (min {min_bytes})",
    })

    # Extension-specific checks
    if ext in (".csv", ".txt"):
        result["checks"].extend(_validate_text_output(output_path, expected_output))
    elif ext == ".json":
        result["checks"].extend(_validate_json_output(output_path, expected_output))
    elif ext in (".html", ".htm"):
        result["checks"].extend(_validate_html_output(output_path, expected_output))
    elif ext == ".pdf":
        result["checks"].extend(_validate_pdf_output(output_path, expected_output))
    elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff"):
        result["checks"].extend(_validate_image_output(output_path))
    elif ext == ".xlsx":
        result["checks"].extend(_validate_xlsx_output(output_path, expected_output))

    result["passed"] = all(c["passed"] for c in result["checks"])
    return result


def _validate_text_output(path: Path, expected: dict | None) -> list[dict]:
    checks: list[dict] = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"check": "readable", "passed": False, "detail": str(e)}]

    checks.append({"check": "readable", "passed": True, "detail": "Text file readable"})

    if expected and expected.get("content_contains"):
        for val in expected["content_contains"]:
            checks.append({
                "check": f"contains_{val}",
                "passed": val in content,
                "detail": f"'{val}' {'found' if val in content else 'not found'}",
            })

    if expected and expected.get("content_not_contains"):
        for val in expected["content_not_contains"]:
            checks.append({
                "check": f"not_contains_{val}",
                "passed": val not in content,
                "detail": f"'{val}' {'absent' if val not in content else 'present'}",
            })

    return checks


def _validate_json_output(path: Path, expected: dict | None) -> list[dict]:
    checks: list[dict] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        checks.append({"check": "json_parse", "passed": True, "detail": "Valid JSON"})
        if isinstance(data, list):
            checks.append({"check": "json_shape", "passed": True, "detail": f"Array with {len(data)} elements"})
        elif isinstance(data, dict):
            checks.append({"check": "json_shape", "passed": True, "detail": f"Object with {len(data)} keys"})
    except Exception as e:
        checks.append({"check": "json_parse", "passed": False, "detail": str(e)})
    return checks


def _validate_html_output(path: Path, expected: dict | None) -> list[dict]:
    checks: list[dict] = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"check": "readable", "passed": False, "detail": str(e)}]

    has_table = "<table" in content.lower()
    checks.append({"check": "html_has_table", "passed": has_table, "detail": f"Table {'found' if has_table else 'not found'}"})
    has_html = "<html" in content.lower()
    checks.append({"check": "html_structure", "passed": has_html, "detail": f"HTML tag {'found' if has_html else 'not found'}"})
    return checks


def _validate_pdf_output(path: Path, expected: dict | None) -> list[dict]:
    checks: list[dict] = []
    try:
        with open(path, "rb") as f:
            header = f.read(5)
        is_pdf = header == b"%PDF-"
        checks.append({"check": "pdf_header", "passed": is_pdf, "detail": f"PDF header {'valid' if is_pdf else 'invalid'}"})
    except Exception as e:
        return [{"check": "pdf_header", "passed": False, "detail": str(e)}]

    size = path.stat().st_size
    min_size = (expected or {}).get("min_bytes", 100)
    checks.append({"check": "pdf_min_size", "passed": size >= min_size, "detail": f"Size {size} (min {min_size})"})
    return checks


def _validate_image_output(path: Path) -> list[dict]:
    checks: list[dict] = []
    try:
        with open(path, "rb") as f:
            header = f.read(8)
    except Exception as e:
        return [{"check": "image_header", "passed": False, "detail": str(e)}]

    ext = path.suffix.lower()
    valid = False
    detail = "Unknown format"
    if ext == ".png" and header[:4] == b"\x89PNG":
        valid, detail = True, "Valid PNG header"
    elif ext in (".jpg", ".jpeg") and header[:2] == b"\xff\xd8":
        valid, detail = True, "Valid JPEG header"
    elif ext == ".bmp" and header[:2] == b"BM":
        valid, detail = True, "Valid BMP header"
    elif ext == ".tiff" and header[:2] in (b"II", b"MM"):
        valid, detail = True, "Valid TIFF header"
    else:
        valid = len(header) > 0
        detail = f"Non-empty file ({len(header)} byte header)"

    checks.append({"check": "image_header", "passed": valid, "detail": detail})
    return checks


def _validate_xlsx_output(path: Path, expected: dict | None) -> list[dict]:
    checks: list[dict] = []
    try:
        with zipfile.ZipFile(path, "r") as z:
            names = z.namelist()
            checks.append({"check": "xlsx_valid_zip", "passed": True, "detail": f"Valid ZIP with {len(names)} entries"})
            has_wb = "xl/workbook.xml" in names
            checks.append({"check": "xlsx_has_workbook", "passed": has_wb, "detail": f"workbook.xml {'found' if has_wb else 'not found'}"})
    except Exception as e:
        checks.append({"check": "xlsx_valid_zip", "passed": False, "detail": str(e)})
    return checks


def write_semantic_validation_results(
    results: list[dict],
    evidence_dir: Path,
) -> Path:
    """Write semantic output validation results."""
    latest = evidence_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "semantic-output-validation-results.json"

    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))

    data = {
        "total_validated": total,
        "total_passed": passed,
        "total_failed": total - passed,
        "results": results,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Semantic output validation results written: %s", path)
    return path
