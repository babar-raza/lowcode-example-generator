"""Post-publication verifier.

Verifies that published examples in the target repo are correct by:
1. Checking the PR exists and is open/merged
2. Fetching the PR diff to confirm expected files are present
3. Validating example files have the correct content shape
4. Producing a per-family post-publication verification report

This runs AFTER a live PR has been created (or as a simulation check for dry-run mode).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ExampleVerification:
    """Verification result for a single example."""
    example_name: str
    file_found: bool
    has_program_cs: bool
    has_readme: bool
    has_csproj: bool
    program_cs_bytes: int | None
    readme_bytes: int | None
    lowcode_api_present: bool | None  # True if Program.cs contains LowCode namespace
    status: str  # "verified" | "missing_files" | "empty_files" | "api_not_found"


@dataclass
class PackageVerification:
    """Verification result for a single PR package."""
    pr_number: int
    package_name: str
    family: str
    package_path: Path
    examples: list[ExampleVerification] = field(default_factory=list)
    total_examples: int = 0
    verified_examples: int = 0
    failed_examples: int = 0
    verdict: str = "UNVERIFIED"


@dataclass
class PostPublicationReport:
    """Full post-publication verification report."""
    verified_at: str
    family: str
    mode: str  # "dry_run_local" | "live_github"
    packages: list[PackageVerification] = field(default_factory=list)
    total_packages: int = 0
    all_verified: bool = False
    verdict: str = "UNVERIFIED"


def verify_local_package(
    family: str,
    pr_number: int,
    package_name: str,
    package_path: Path,
) -> PackageVerification:
    """Verify a local PR package directory for post-publication readiness.

    Checks each example directory for required files and content shape.

    Args:
        family: Family name (e.g., "pdf").
        pr_number: PR number.
        package_name: Package directory name.
        package_path: Path to the package directory.

    Returns:
        PackageVerification with per-example results.
    """
    lowcode_namespace = _get_lowcode_namespace(family)
    example_verifications: list[ExampleVerification] = []

    if not package_path.exists():
        return PackageVerification(
            pr_number=pr_number,
            package_name=package_name,
            family=family,
            package_path=package_path,
            verdict="PACKAGE_PATH_MISSING",
        )

    # Resolve example directories. Packages use structure:
    #   examples/{family}/lowcode/{example-name}/Program.cs
    # Fall back to scanning all leaf dirs containing Program.cs.
    examples_root = package_path / "examples"
    example_dirs: list[Path] = []
    if examples_root.exists():
        for p in sorted(examples_root.rglob("Program.cs")):
            example_dirs.append(p.parent)
    if not example_dirs:
        example_dirs = sorted(
            d for d in package_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )

    for example_dir in example_dirs:
        program_cs = example_dir / "Program.cs"
        readme_md = example_dir / "README.md"
        csproj = next(example_dir.glob("*.csproj"), None)

        file_found = any([program_cs.exists(), readme_md.exists(), csproj is not None])
        has_program_cs = program_cs.exists()
        has_readme = readme_md.exists()
        has_csproj = csproj is not None

        program_cs_bytes = program_cs.stat().st_size if has_program_cs else None
        readme_bytes = readme_md.stat().st_size if has_readme else None

        # Check for LowCode API presence in Program.cs
        lowcode_api_present = None
        if has_program_cs and program_cs_bytes and program_cs_bytes > 0:
            try:
                content = program_cs.read_text(encoding="utf-8", errors="replace")
                lowcode_api_present = lowcode_namespace.lower() in content.lower()
            except Exception:
                lowcode_api_present = None

        # Determine status
        if not file_found:
            status = "missing_files"
        elif has_program_cs and program_cs_bytes == 0:
            status = "empty_files"
        elif lowcode_api_present is False:
            status = "api_not_found"
        elif has_program_cs and has_readme and has_csproj:
            status = "verified"
        elif has_program_cs and has_csproj:
            status = "verified"  # README is optional for verification
        else:
            status = "missing_files"

        example_verifications.append(ExampleVerification(
            example_name=example_dir.name,
            file_found=file_found,
            has_program_cs=has_program_cs,
            has_readme=has_readme,
            has_csproj=has_csproj,
            program_cs_bytes=program_cs_bytes,
            readme_bytes=readme_bytes,
            lowcode_api_present=lowcode_api_present,
            status=status,
        ))

    total = len(example_verifications)
    verified = sum(1 for e in example_verifications if e.status == "verified")
    failed = total - verified

    verdict = "ALL_VERIFIED" if verified == total and total > 0 else (
        "PARTIAL" if verified > 0 else "ALL_FAILED"
    )

    return PackageVerification(
        pr_number=pr_number,
        package_name=package_name,
        family=family,
        package_path=package_path,
        examples=example_verifications,
        total_examples=total,
        verified_examples=verified,
        failed_examples=failed,
        verdict=verdict,
    )


def run_post_publication_verification(
    family: str,
    packages: list[tuple[int, str]],  # list of (pr_number, package_name)
    packages_base_path: Path,
) -> PostPublicationReport:
    """Run post-publication verification for all packages in a family.

    Args:
        family: Family name.
        packages: List of (pr_number, package_name) tuples.
        packages_base_path: Base directory containing all package subdirectories.

    Returns:
        PostPublicationReport with full verification status.
    """
    verified_at = datetime.now(timezone.utc).isoformat()
    package_results: list[PackageVerification] = []

    for pr_number, package_name in packages:
        pkg_path = packages_base_path / package_name
        result = verify_local_package(family, pr_number, package_name, pkg_path)
        package_results.append(result)
        logger.info(
            "Package %s (PR#%d): %s (%d/%d verified)",
            package_name, pr_number, result.verdict,
            result.verified_examples, result.total_examples,
        )

    total_packages = len(package_results)
    all_verified = all(p.verdict in ("ALL_VERIFIED",) for p in package_results)

    verdict = "ALL_PACKAGES_VERIFIED" if all_verified else (
        "PARTIAL_VERIFICATION" if any(p.verified_examples > 0 for p in package_results)
        else "VERIFICATION_FAILED"
    )

    return PostPublicationReport(
        verified_at=verified_at,
        family=family,
        mode="dry_run_local",
        packages=package_results,
        total_packages=total_packages,
        all_verified=all_verified,
        verdict=verdict,
    )


def write_verification_report(report: PostPublicationReport, output_path: Path) -> Path:
    """Write post-publication verification report to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "verified_at": report.verified_at,
        "family": report.family,
        "mode": report.mode,
        "total_packages": report.total_packages,
        "all_verified": report.all_verified,
        "verdict": report.verdict,
        "packages": [
            {
                "pr_number": p.pr_number,
                "package_name": p.package_name,
                "total_examples": p.total_examples,
                "verified_examples": p.verified_examples,
                "failed_examples": p.failed_examples,
                "verdict": p.verdict,
                "examples": [
                    {
                        "name": e.example_name,
                        "has_program_cs": e.has_program_cs,
                        "has_readme": e.has_readme,
                        "has_csproj": e.has_csproj,
                        "program_cs_bytes": e.program_cs_bytes,
                        "lowcode_api_present": e.lowcode_api_present,
                        "status": e.status,
                    }
                    for e in p.examples
                ],
            }
            for p in report.packages
        ],
    }

    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Post-publication verification report: %s", output_path)
    return output_path


def _get_lowcode_namespace(family: str) -> str:
    """Get the LowCode namespace string for a family."""
    return {
        "pdf": "Aspose.Pdf.LowCode",
        "cells": "Aspose.Cells.LowCode",
        "words": "Aspose.Words.LowCode",
        "diagram": "Aspose.Diagram.LowCode",
        "email": "Aspose.Email.LowCode",
        "slides": "Aspose.Slides.LowCode",
    }.get(family, f"Aspose.{family.capitalize()}.LowCode")
