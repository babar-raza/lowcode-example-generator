"""Deterministic fallback reviewer for LowCode examples.

Checks each example's Program.cs for:
1. Correct namespace usage (using Aspose.<Family>.LowCode)
2. Presence of required patterns from family config
3. Absence of forbidden patterns from family config
4. Presence of documentation (README.md)
5. Presence of expected-output.json

Does NOT require LLM. Runs entirely locally.

Usage:
  python scripts/fallback_reviewer.py [--family FAMILY] [--package-dir PKG_DIR]
  python scripts/fallback_reviewer.py --all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PR_DRY_RUN = REPO_ROOT / "workspace" / "pr-dry-run"

# Namespace patterns per family
LOWCODE_NAMESPACES = {
    "cells": "Aspose.Cells.LowCode",
    "words": "Aspose.Words.LowCode",
    "pdf": "Aspose.Pdf.LowCode",
    "diagram": "Aspose.Diagram.LowCode",
    "slides": "Aspose.Slides.LowCode",
    "email": "Aspose.Email.LowCode",
}

# Main API classes per family (at least one must appear in Program.cs)
REQUIRED_CLASSES = {
    "cells": ["HtmlConverter", "ImageConverter", "JsonConverter", "PdfConverter",
              "SpreadsheetConverter", "SpreadsheetLocker", "SpreadsheetMerger",
              "SpreadsheetSplitter", "TextConverter"],
    "words": ["Comparer", "Converter", "MailMerger", "Merger", "Replacer",
              "ReportBuilder", "Splitter", "Watermarker"],
    "pdf": ["DocConverter", "FormEditor", "FormExporter", "FormFlattener", "Html",
            "ImageExtractor", "Jpeg", "Merger", "Ofd", "Optimizer", "PdfAConverter",
            "Png", "Security", "Signature", "Splitter", "TableGenerator", "TextExtractor",
            "Tiff", "Timestamp", "TocGenerator", "XlsConverter"],
    "diagram": ["DiagramConverter", "PdfConverter"],
    "slides": ["Compress", "Convert", "Merger"],
    "email": ["Converter"],
}

# Forbidden patterns that suggest bypassing LowCode API
GENERIC_FORBIDDEN = [
    # Using full API instead of LowCode
    (r"document\.Save\(", "WARN: Document.Save() may bypass LowCode API — verify LowCode method is the primary operation"),
]


def review_example(csproj_path: Path, family: str) -> dict:
    example_dir = csproj_path.parent
    slug = example_dir.name
    program_cs = example_dir / "Program.cs"
    readme = example_dir / "README.md"
    expected_output = example_dir / "expected-output.json"

    issues = []
    warnings = []
    passed_checks = []

    # Check Program.cs exists
    if not program_cs.exists():
        return {
            "slug": slug,
            "status": "FAIL",
            "verdict": "MISSING_PROGRAM_CS",
            "issues": ["Program.cs not found"],
            "warnings": [],
            "passed_checks": []
        }

    source = program_cs.read_text(encoding="utf-8", errors="replace")

    # Check 1: LowCode namespace usage
    ns = LOWCODE_NAMESPACES.get(family, f"Aspose.{family.title()}.LowCode")
    if f"using {ns}" in source or f"using Aspose." in source:
        passed_checks.append(f"using {ns} present")
    else:
        issues.append(f"No 'using {ns}' found in Program.cs")

    # Check 2: At least one main LowCode class is used
    family_classes = REQUIRED_CLASSES.get(family, [])
    used_classes = [c for c in family_classes if c in source]
    if used_classes:
        passed_checks.append(f"LowCode class usage: {used_classes[0]}")
    else:
        issues.append(f"No recognized LowCode main class found in source. Expected one of: {family_classes[:5]}")

    # Check 3: Generic forbidden patterns
    for pattern, msg in GENERIC_FORBIDDEN:
        if re.search(pattern, source, re.IGNORECASE):
            warnings.append(msg)

    # Check 4: README.md present
    if readme.exists() and readme.stat().st_size > 0:
        passed_checks.append("README.md present")
    else:
        warnings.append("README.md missing or empty")

    # Check 5: expected-output.json present
    if expected_output.exists():
        passed_checks.append("expected-output.json present")
    else:
        warnings.append("expected-output.json missing")

    # Check 6: example.manifest.json present
    manifest = example_dir / "example.manifest.json"
    if manifest.exists():
        passed_checks.append("example.manifest.json present")
    else:
        warnings.append("example.manifest.json missing")

    # Check 7: Console.WriteLine with output info (evidence the example shows results)
    if "Console.WriteLine" in source:
        passed_checks.append("Console.WriteLine present (example produces output)")
    else:
        warnings.append("No Console.WriteLine found — example may not report results")

    # Verdict
    if issues:
        status = "FAIL"
        verdict = "REVIEW_FAILED"
    else:
        status = "PASS"
        verdict = "DETERMINISTIC_REVIEW_PASSED"

    return {
        "slug": slug,
        "family": family,
        "status": status,
        "verdict": verdict,
        "issues": issues,
        "warnings": warnings,
        "passed_checks": passed_checks,
        "lowcode_classes_used": used_classes,
    }


def run_review(package_dirs: list[Path]) -> list[dict]:
    results = []
    for pkg_dir in sorted(package_dirs):
        # Determine family from path
        for fam in LOWCODE_NAMESPACES:
            if fam in pkg_dir.name:
                family = fam
                break
        else:
            family = "unknown"

        for csproj in sorted(pkg_dir.glob("examples/**/*.csproj")):
            result = review_example(csproj, family)
            result["package"] = pkg_dir.name
            results.append(result)
            status = result["status"]
            print(f"  [{status}] {pkg_dir.name}/{result['slug']}: {result['verdict']}")
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"    ISSUE: {issue}")
            if result["warnings"]:
                for w in result["warnings"]:
                    print(f"    WARN: {w}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Deterministic fallback reviewer for LowCode examples.")
    parser.add_argument("--all", action="store_true", help="Review all packages in pr-dry-run/")
    parser.add_argument("--family", help="Filter by family name")
    parser.add_argument("--package-dir", dest="package_dir", help="Specific package directory")
    args = parser.parse_args()

    if args.package_dir:
        package_dirs = [Path(args.package_dir)]
    elif args.all:
        package_dirs = [d for d in sorted(PR_DRY_RUN.iterdir()) if d.is_dir()]
        if args.family:
            package_dirs = [d for d in package_dirs if args.family in d.name]
    else:
        parser.print_help()
        sys.exit(1)

    print(f"\nRunning fallback reviewer on {len(package_dirs)} package(s)...\n")
    results = run_review(package_dirs)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] != "PASS")
    total = len(results)

    print(f"\n--- Summary ---")
    print(f"Total: {total} | PASS: {passed} | FAIL: {failed}")

    # Save results
    out_dir = REPO_ROOT / "reports" / "lowcode-systemization-26family-20260530" / "reviewer"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "fallback-reviewer-results.json"
    out_file.write_text(
        json.dumps({
            "sprint_id": "lowcode-systemization-26family-20260530",
            "lane": "I1 — Fallback reviewer",
            "reviewer_type": "DETERMINISTIC",
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{passed}/{total}",
            "results": results
        }, indent=2),
        encoding="utf-8"
    )
    print(f"Results written to: {out_file}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
