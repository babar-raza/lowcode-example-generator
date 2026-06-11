"""Package self-containment validators PSC-01..08 — TC-PSC-001.

Validates that a generated .NET example package is self-contained and
suitable for publication.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PscViolation:
    """A self-containment violation."""
    rule_id: str
    detail: str


def psc_01_csproj_exists(package_dir: Path) -> PscViolation | None:
    """PSC-01: .csproj file exists in package root."""
    csproj_files = list(package_dir.glob("*.csproj"))
    if not csproj_files:
        return PscViolation("PSC-01", f"No .csproj file found in {package_dir.name}")
    return None


def psc_02_target_framework(package_dir: Path) -> PscViolation | None:
    """PSC-02: TargetFramework is net8.0 or net9.0."""
    csproj_files = list(package_dir.glob("*.csproj"))
    if not csproj_files:
        return PscViolation("PSC-02", "Cannot check TargetFramework: no .csproj")
    content = csproj_files[0].read_text(encoding="utf-8")
    match = re.search(r"<TargetFramework>(net\d+\.\d+)</TargetFramework>", content)
    if not match:
        return PscViolation("PSC-02", "TargetFramework not found in .csproj")
    tfm = match.group(1)
    if tfm not in ("net8.0", "net9.0"):
        return PscViolation("PSC-02", f"TargetFramework is {tfm}, expected net8.0 or net9.0")
    return None


def psc_03_package_reference(package_dir: Path) -> PscViolation | None:
    """PSC-03: At least one PackageReference is present."""
    csproj_files = list(package_dir.glob("*.csproj"))
    if not csproj_files:
        return PscViolation("PSC-03", "Cannot check PackageReference: no .csproj")
    content = csproj_files[0].read_text(encoding="utf-8")
    if "<PackageReference" not in content:
        return PscViolation("PSC-03", "No PackageReference found in .csproj")
    return None


def psc_04_no_absolute_paths(package_dir: Path) -> PscViolation | None:
    """PSC-04: No absolute paths in Program.cs."""
    program_cs = package_dir / "Program.cs"
    if not program_cs.exists():
        return None  # Checked by other rules
    content = program_cs.read_text(encoding="utf-8")
    abs_patterns = [r'[A-Z]:\\', r'/home/', r'/Users/', r'/tmp/']
    for pattern in abs_patterns:
        if re.search(pattern, content):
            return PscViolation("PSC-04", f"Absolute path pattern '{pattern}' found in Program.cs")
    return None


def psc_05_no_interactive_calls(package_dir: Path) -> PscViolation | None:
    """PSC-05: No Console.ReadKey()/Console.ReadLine() in Program.cs."""
    program_cs = package_dir / "Program.cs"
    if not program_cs.exists():
        return None
    content = program_cs.read_text(encoding="utf-8")
    for call in ["Console.ReadKey()", "Console.ReadLine()"]:
        if call in content:
            return PscViolation("PSC-05", f"Interactive call '{call}' found in Program.cs")
    return None


def psc_06_manifest_exists(package_dir: Path) -> PscViolation | None:
    """PSC-06: example.manifest.json exists."""
    if not (package_dir / "example.manifest.json").exists():
        return PscViolation("PSC-06", "example.manifest.json not found")
    return None


def psc_07_expected_output_exists(package_dir: Path) -> PscViolation | None:
    """PSC-07: expected-output.json or output-validation.json exists."""
    has_expected = (package_dir / "expected-output.json").exists()
    has_validation = (package_dir / "output-validation.json").exists()
    if not has_expected and not has_validation:
        return PscViolation("PSC-07", "Neither expected-output.json nor output-validation.json found")
    return None


def psc_08_readme_exists(package_dir: Path) -> PscViolation | None:
    """PSC-08: README.md exists in package."""
    if not (package_dir / "README.md").exists():
        return PscViolation("PSC-08", "README.md not found in package")
    return None


def validate_package(package_dir: Path) -> list[PscViolation]:
    """Run all PSC validators on a package directory."""
    violations = []
    for check in [
        psc_01_csproj_exists,
        psc_02_target_framework,
        psc_03_package_reference,
        psc_04_no_absolute_paths,
        psc_05_no_interactive_calls,
        psc_06_manifest_exists,
        psc_07_expected_output_exists,
        psc_08_readme_exists,
    ]:
        result = check(package_dir)
        if result is not None:
            violations.append(result)
    return violations
