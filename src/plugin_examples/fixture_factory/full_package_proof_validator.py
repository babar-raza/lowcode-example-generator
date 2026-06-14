"""
Full Package Proof Validator

Sprint: lowcode-plugin-canonical-package-wave9-20260605

Validates that a dryrun package contains all required proof files.
A package that claims PASS verdict must not be metadata-only.

Required files for a fully-proven package:
- Program.cs
- *.csproj
- README.md
- source-provenance.json
- package-manifest.json
- restore.log (or logs/restore.log)
- build.log (or logs/build.log)
- run.log (or logs/run.log)
- output-validation.json
- output/ directory with at least one non-zero file
"""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProofViolation:
    rule: str
    severity: str  # "ERROR" | "WARNING"
    message: str
    path: str = ""


@dataclass
class ProofResult:
    package_key: str
    violations: list[ProofViolation] = field(default_factory=list)
    proof_type: str = "UNKNOWN"

    @property
    def passes(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "WARNING")

    def to_dict(self) -> dict:
        return {
            "package_key": self.package_key,
            "passes": self.passes,
            "proof_type": self.proof_type,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "violations": [
                {"rule": v.rule, "severity": v.severity, "message": v.message, "path": v.path} for v in self.violations
            ],
        }


def _find_log(pkg_dir: Path, name: str) -> Path | None:
    """Find a log file in package dir or logs/ subdir."""
    direct = pkg_dir / name
    if direct.exists():
        return direct
    nested = pkg_dir / "logs" / name
    if nested.exists():
        return nested
    return None


def _read_json(path: Path) -> dict | None:
    if path and path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def run_full_package_proof_validator(pkg_dir: Path, package_key: str) -> ProofResult:
    """
    Validate that a dryrun package has full proof files.

    FPP-01: Program.cs must exist
    FPP-02: *.csproj must exist
    FPP-03: README.md must exist
    FPP-04: source-provenance.json must exist
    FPP-05: package-manifest.json must exist
    FPP-06: restore.log must exist (direct or logs/)
    FPP-07: build.log must exist (direct or logs/)
    FPP-08: run.log must exist (direct or logs/)
    FPP-09: output-validation.json must exist
    FPP-10: output/ must contain at least one non-zero file
    FPP-11: PASS verdict must not be claimed if FPP-01..FPP-10 fail
    FPP-12: package-manifest.json must not claim METADATA_ONLY if full files present
    """
    result = ProofResult(package_key=package_key)
    ov = _read_json(pkg_dir / "output-validation.json") or {}
    verdict = ov.get("verdict", "")

    # FPP-01
    if not (pkg_dir / "Program.cs").exists():
        result.violations.append(
            ProofViolation(
                "FPP-01",
                "ERROR",
                f"{package_key}: Program.cs missing",
                str(pkg_dir / "Program.cs"),
            )
        )

    # FPP-02
    csproj = list(pkg_dir.glob("*.csproj"))
    if not csproj:
        result.violations.append(
            ProofViolation(
                "FPP-02",
                "ERROR",
                f"{package_key}: no *.csproj found",
                str(pkg_dir),
            )
        )

    # FPP-03
    if not (pkg_dir / "README.md").exists():
        result.violations.append(
            ProofViolation(
                "FPP-03",
                "WARNING",
                f"{package_key}: README.md missing",
                str(pkg_dir / "README.md"),
            )
        )

    # FPP-04
    if not (pkg_dir / "source-provenance.json").exists():
        result.violations.append(
            ProofViolation(
                "FPP-04",
                "ERROR",
                f"{package_key}: source-provenance.json missing",
                str(pkg_dir / "source-provenance.json"),
            )
        )

    # FPP-05
    if not (pkg_dir / "package-manifest.json").exists():
        result.violations.append(
            ProofViolation(
                "FPP-05",
                "WARNING",
                f"{package_key}: package-manifest.json missing",
                str(pkg_dir / "package-manifest.json"),
            )
        )

    # FPP-06
    if not _find_log(pkg_dir, "restore.log"):
        result.violations.append(
            ProofViolation(
                "FPP-06",
                "WARNING",
                f"{package_key}: restore.log missing",
                str(pkg_dir),
            )
        )

    # FPP-07
    if not _find_log(pkg_dir, "build.log"):
        result.violations.append(
            ProofViolation(
                "FPP-07",
                "WARNING",
                f"{package_key}: build.log missing",
                str(pkg_dir),
            )
        )

    # FPP-08
    if not _find_log(pkg_dir, "run.log"):
        result.violations.append(
            ProofViolation(
                "FPP-08",
                "WARNING",
                f"{package_key}: run.log missing",
                str(pkg_dir),
            )
        )

    # FPP-09
    if not (pkg_dir / "output-validation.json").exists():
        result.violations.append(
            ProofViolation(
                "FPP-09",
                "ERROR",
                f"{package_key}: output-validation.json missing",
                str(pkg_dir / "output-validation.json"),
            )
        )

    # FPP-10
    out_dir = pkg_dir / "output"
    if not out_dir.exists():
        result.violations.append(
            ProofViolation(
                "FPP-10",
                "ERROR",
                f"{package_key}: output/ directory missing",
                str(out_dir),
            )
        )
    else:
        non_zero = [f for f in out_dir.iterdir() if f.is_file() and f.stat().st_size > 0]
        if not non_zero:
            result.violations.append(
                ProofViolation(
                    "FPP-10",
                    "ERROR",
                    f"{package_key}: output/ exists but has no non-zero files",
                    str(out_dir),
                )
            )

    # FPP-11
    has_errors = any(v.severity == "ERROR" for v in result.violations)
    if verdict == "PASS" and has_errors:
        result.violations.append(
            ProofViolation(
                "FPP-11",
                "ERROR",
                f"{package_key}: verdict=PASS but package has proof errors above",
                str(pkg_dir / "output-validation.json"),
            )
        )

    # FPP-12: If package-manifest says METADATA_ONLY but full files exist
    pm = _read_json(pkg_dir / "package-manifest.json") or {}
    proof_type = pm.get("proof_type", "")
    full_files_present = (
        (pkg_dir / "Program.cs").exists()
        and bool(csproj)
        and bool(_find_log(pkg_dir, "build.log"))
        and out_dir.exists()
    )
    if proof_type == "METADATA_ONLY" and full_files_present:
        result.violations.append(
            ProofViolation(
                "FPP-12",
                "WARNING",
                f"{package_key}: package-manifest says METADATA_ONLY but full proof files are present — should be upgraded",
                str(pkg_dir / "package-manifest.json"),
            )
        )
        proof_type = "METADATA_ONLY_UPGRADE_AVAILABLE"

    # Determine proof type
    if not result.violations:
        result.proof_type = "FULL_PACKAGE_PROVEN"
    elif not has_errors:
        result.proof_type = "FULL_PACKAGE_WITH_WARNINGS"
    elif (pkg_dir / "source-provenance.json").exists() and not (pkg_dir / "Program.cs").exists():
        result.proof_type = "METADATA_ONLY"
    else:
        result.proof_type = "INCOMPLETE_PACKAGE"

    return result
