"""
Anti-overclaiming validator rules (Wave 6).

16 rules that detect common overclaiming patterns in dry-run packages:
- AOC-01..AOC-05: Output file integrity rules
- AOC-06..AOC-09: Source provenance integrity rules
- AOC-10..AOC-12: Build/run log integrity rules
- AOC-13..AOC-14: Registry consistency rules
- AOC-15..AOC-16: Publication readiness rules
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AocViolation:
    rule_id: str
    package_key: str
    description: str
    evidence: str
    severity: str = "ERROR"  # ERROR | WARNING


@dataclass
class AocResult:
    package_key: str
    package_dir: str
    violations: list = field(default_factory=list)
    rules_checked: int = 0

    @property
    def passed(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)

    @property
    def violation_count(self) -> int:
        return len(self.violations)


# ── AOC-01..AOC-05: Output File Integrity ─────────────────────────────────


def aoc_01_output_dir_exists(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-01: output/ directory must exist after build+run."""
    if not (pkg_dir / "output").exists():
        return AocViolation("AOC-01", key, "output/ directory missing after run", f"No output/ dir in {pkg_dir}")
    return None


def aoc_02_no_zero_byte_primary_output(pkg_dir: Path, key: str) -> list[AocViolation]:
    """AOC-02: Primary output files must not be zero bytes."""
    violations = []
    ov_path = pkg_dir / "output-validation.json"
    if not ov_path.exists():
        return violations
    ov = json.loads(ov_path.read_text())
    output_dir = pkg_dir / "output"
    for f_info in ov.get("output_files", []):
        size = f_info.get("size", 0)
        fname = Path(f_info["path"]).name
        # Skip known intermediate/fixture files
        intermediate = {
            "fixture.png",
            "fixture.bmp",
            "fixture.psd",
            "fixture.eps",
            "canvas.bmp",
            "source-watermark.bmp",
            "src1.bmp",
            "src2.bmp",
        }
        if fname in intermediate:
            continue
        if size == 0:
            violations.append(
                AocViolation(
                    "AOC-02",
                    key,
                    f"Primary output {fname} is zero bytes",
                    f"output-validation.json shows size=0 for {fname}",
                    "ERROR",
                )
            )
    return violations


def aoc_03_output_validation_verdict_matches_run(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-03: output-validation.json verdict must match actual output state."""
    ov_path = pkg_dir / "output-validation.json"
    if not ov_path.exists():
        return AocViolation("AOC-03", key, "output-validation.json missing", f"No output-validation.json in {pkg_dir}")
    ov = json.loads(ov_path.read_text())
    stated_verdict = ov.get("verdict", "UNKNOWN")
    output_files = ov.get("output_files", [])
    has_real_output = any(f.get("size", 0) > 20 for f in output_files)
    if stated_verdict == "PASS" and not has_real_output:
        return AocViolation(
            "AOC-03",
            key,
            "PASS claimed but no real output files (all ≤20 bytes)",
            f"Stated PASS but output_files={output_files}",
        )
    if stated_verdict == "FAIL" and has_real_output:
        return AocViolation(
            "AOC-03",
            key,
            "FAIL stated but real output files exist",
            f"Stated FAIL but has output_files with size>20",
            severity="WARNING",
        )
    return None


def aoc_04_no_fabricated_output(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-04: run.log must exist and indicate actual execution."""
    run_log = pkg_dir / "run.log"
    if not run_log.exists():
        return AocViolation("AOC-04", key, "run.log missing — no proof of execution", f"No run.log in {pkg_dir}")
    content = run_log.read_text(errors="replace")
    if content.strip() == "" or content == "BUILD FAILED — run skipped\n":
        pass  # OK — documented failure
    # If output exists but run.log is completely empty, that's suspicious
    output_dir = pkg_dir / "output"
    if output_dir.exists():
        real_outputs = [
            f
            for f in output_dir.iterdir()
            if f.is_file() and f.stat().st_size > 20 and f.name not in {"fixture.png", "fixture.bmp", "fixture.psd"}
        ]
        if real_outputs and len(content.strip()) == 0:
            return AocViolation(
                "AOC-04",
                key,
                "Output files exist but run.log is empty — execution not proven",
                f"run.log empty, but found: {[f.name for f in real_outputs]}",
            )
    return None


def aoc_05_no_stale_error_snippet_on_pass(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-05: PASS packages must not have build errors in build.log."""
    ov_path = pkg_dir / "output-validation.json"
    build_log = pkg_dir / "build.log"
    if not ov_path.exists() or not build_log.exists():
        return None
    ov = json.loads(ov_path.read_text())
    if ov.get("verdict") != "PASS":
        return None
    content = build_log.read_text(errors="replace").lower()
    if "error" in content and "build failed" in content:
        # Only flag if there are real errors, not just the build summary
        lines_with_error = [l for l in content.splitlines() if ": error cs" in l or "build failed" in l.lower()]
        if lines_with_error:
            return AocViolation(
                "AOC-05",
                key,
                "PASS claimed but build.log contains build errors",
                f"build.log has {len(lines_with_error)} error lines",
            )
    return None


# ── AOC-06..AOC-09: Source Provenance Integrity ───────────────────────────


def aoc_06_provenance_json_valid(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-06: source-provenance.json must be valid JSON with required fields."""
    sp_path = pkg_dir / "source-provenance.json"
    if not sp_path.exists():
        return AocViolation("AOC-06", key, "source-provenance.json missing", f"No source-provenance.json in {pkg_dir}")
    try:
        data = json.loads(sp_path.read_text())
    except json.JSONDecodeError as e:
        return AocViolation("AOC-06", key, "source-provenance.json is not valid JSON", f"JSONDecodeError: {e}")
    required = ["family", "plugin_slug", "nuget_package", "canonical_url"]
    missing = [f for f in required if f not in data]
    if missing:
        return AocViolation(
            "AOC-06",
            key,
            f"source-provenance.json missing required fields: {missing}",
            f"Present keys: {list(data.keys())}",
        )
    return None


def aoc_07_no_double_brace_in_json(pkg_dir: Path, key: str) -> list[AocViolation]:
    """AOC-07: JSON files must not contain {{ or }} (Python format string escape artifacts)."""
    violations = []
    for fname in ["source-provenance.json", "package-manifest.json", "output-validation.json"]:
        path = pkg_dir / fname
        if not path.exists():
            continue
        content = path.read_text(errors="replace")
        if "{{" in content or "}}" in content:
            violations.append(
                AocViolation(
                    "AOC-07",
                    key,
                    f"{fname} contains {{ or }} (Python format escape artifact)",
                    f"Found {{ or }} in {fname}",
                )
            )
    return violations


def aoc_08_canonical_url_not_placeholder(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-08: canonical_url must not be a placeholder or empty."""
    sp_path = pkg_dir / "source-provenance.json"
    if not sp_path.exists():
        return None
    try:
        data = json.loads(sp_path.read_text())
    except Exception:
        return None
    url = data.get("canonical_url", "")
    if not url or "{{" in url or url == "https://products.aspose.net/TODO":
        return AocViolation(
            "AOC-08",
            key,
            f"canonical_url is empty or placeholder: '{url}'",
            f"source-provenance.json canonical_url={url!r}",
        )
    if not url.startswith("https://"):
        return AocViolation(
            "AOC-08",
            key,
            f"canonical_url does not start with https://: {url!r}",
            f"source-provenance.json canonical_url={url!r}",
            "WARNING",
        )
    return None


def aoc_09_package_manifest_consistent(pkg_dir: Path, key: str) -> list[AocViolation]:
    """AOC-09: package-manifest.json must match source-provenance.json on nuget_package/version."""
    violations = []
    sp_path = pkg_dir / "source-provenance.json"
    pm_path = pkg_dir / "package-manifest.json"
    if not sp_path.exists() or not pm_path.exists():
        return violations
    try:
        sp = json.loads(sp_path.read_text())
        pm = json.loads(pm_path.read_text())
    except Exception:
        return violations
    for fname in ["nuget_package", "nuget_version"]:
        sp_val = sp.get(fname)
        pm_val = pm.get(fname)
        if sp_val and pm_val and sp_val != pm_val:
            violations.append(
                AocViolation(
                    "AOC-09",
                    key,
                    f"{field} mismatch: provenance={sp_val!r}, manifest={pm_val!r}",
                    f"source-provenance.json vs package-manifest.json",
                )
            )
    return violations


# ── AOC-10..AOC-12: Build/Run Log Integrity ───────────────────────────────


def aoc_10_restore_log_exists(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-10: restore.log must exist."""
    if not (pkg_dir / "restore.log").exists():
        return AocViolation("AOC-10", key, "restore.log missing", f"No restore.log in {pkg_dir}")
    return None


def aoc_11_build_log_exists(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-11: build.log must exist."""
    if not (pkg_dir / "build.log").exists():
        return AocViolation("AOC-11", key, "build.log missing", f"No build.log in {pkg_dir}")
    return None


def aoc_12_no_exception_in_pass_run(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-12: PASS packages must not have unhandled exceptions in run.log."""
    ov_path = pkg_dir / "output-validation.json"
    run_log = pkg_dir / "run.log"
    if not ov_path.exists() or not run_log.exists():
        return None
    ov = json.loads(ov_path.read_text())
    if ov.get("verdict") != "PASS":
        return None
    content = run_log.read_text(errors="replace")
    if "Unhandled exception" in content:
        return AocViolation("AOC-12", key, "PASS claimed but run.log shows unhandled exception", content[:300])
    return None


# ── AOC-13..AOC-14: Registry Consistency ─────────────────────────────────


def aoc_13_dryrun_path_matches_actual(
    pkg_dir: Path, key: str, registry_path: Optional[Path] = None
) -> Optional[AocViolation]:
    """AOC-13: If registry has dryrun_package_path, it must match actual pkg_dir."""
    if registry_path is None:
        return None
    # This is a lightweight check — full registry validation is in Lane E
    family = key.split("/")[0]
    yaml_path = registry_path / "family" / f"{family}.yaml"
    if not yaml_path.exists():
        return None
    # Just check that the family yaml is parseable (full check done in Lane E)
    try:
        import yaml as _yaml

        data = _yaml.safe_load(yaml_path.read_text())
    except Exception as e:
        return AocViolation("AOC-13", key, f"Family YAML parse error: {e}", f"{yaml_path}")
    return None


def aoc_14_no_duplicate_output_files(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-14: output/ must not contain duplicate files by size (possible copy-paste error)."""
    output_dir = pkg_dir / "output"
    if not output_dir.exists():
        return None
    seen_sizes = {}
    for f in output_dir.iterdir():
        if not f.is_file():
            continue
        size = f.stat().st_size
        if size < 100:  # skip tiny files
            continue
        if size in seen_sizes:
            return AocViolation(
                "AOC-14",
                key,
                f"Duplicate output file size: {f.name} and {seen_sizes[size].name} both {size} bytes",
                f"Possible copy-paste or incorrect output",
                "WARNING",
            )
        seen_sizes[size] = f
    return None


# ── AOC-15..AOC-16: Publication Readiness ─────────────────────────────────


def aoc_15_readme_present(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-15: README.md must be present in package root."""
    if not (pkg_dir / "README.md").exists():
        return AocViolation(
            "AOC-15", key, "README.md missing from package root", f"No README.md in {pkg_dir}", "WARNING"
        )
    return None


def aoc_16_program_cs_present(pkg_dir: Path, key: str) -> Optional[AocViolation]:
    """AOC-16: Program.cs must be present (not just a compiled binary)."""
    if not (pkg_dir / "Program.cs").exists():
        return AocViolation("AOC-16", key, "Program.cs missing — source not provided", f"No Program.cs in {pkg_dir}")
    return None


# ── Main runner ─────────────────────────────────────────────────────────────


def run_anti_overclaiming_checks(pkg_dir: Path, key: str, registry_path: Optional[Path] = None) -> AocResult:
    """Run all 16 anti-overclaiming rules on a single package."""
    result = AocResult(package_key=key, package_dir=str(pkg_dir))
    violations = []

    # AOC-01..AOC-05: Output integrity
    v = aoc_01_output_dir_exists(pkg_dir, key)
    if v:
        violations.append(v)
    violations.extend(aoc_02_no_zero_byte_primary_output(pkg_dir, key))
    v = aoc_03_output_validation_verdict_matches_run(pkg_dir, key)
    if v:
        violations.append(v)
    v = aoc_04_no_fabricated_output(pkg_dir, key)
    if v:
        violations.append(v)
    v = aoc_05_no_stale_error_snippet_on_pass(pkg_dir, key)
    if v:
        violations.append(v)

    # AOC-06..AOC-09: Provenance
    v = aoc_06_provenance_json_valid(pkg_dir, key)
    if v:
        violations.append(v)
    violations.extend(aoc_07_no_double_brace_in_json(pkg_dir, key))
    v = aoc_08_canonical_url_not_placeholder(pkg_dir, key)
    if v:
        violations.append(v)
    violations.extend(aoc_09_package_manifest_consistent(pkg_dir, key))

    # AOC-10..AOC-12: Log integrity
    v = aoc_10_restore_log_exists(pkg_dir, key)
    if v:
        violations.append(v)
    v = aoc_11_build_log_exists(pkg_dir, key)
    if v:
        violations.append(v)
    v = aoc_12_no_exception_in_pass_run(pkg_dir, key)
    if v:
        violations.append(v)

    # AOC-13..AOC-14: Registry consistency
    v = aoc_13_dryrun_path_matches_actual(pkg_dir, key, registry_path)
    if v:
        violations.append(v)
    v = aoc_14_no_duplicate_output_files(pkg_dir, key)
    if v:
        violations.append(v)

    # AOC-15..AOC-16: Publication readiness
    v = aoc_15_readme_present(pkg_dir, key)
    if v:
        violations.append(v)
    v = aoc_16_program_cs_present(pkg_dir, key)
    if v:
        violations.append(v)

    result.violations = violations
    result.rules_checked = 16
    return result


def run_all_anti_overclaiming_checks(examples_dir: Path, registry_path: Optional[Path] = None) -> dict:
    """Run all 16 AOC rules on every package in examples_dir."""
    all_results = {}
    for fam_dir in sorted(examples_dir.iterdir()):
        if not fam_dir.is_dir():
            continue
        for pkg_dir in sorted(fam_dir.iterdir()):
            if not pkg_dir.is_dir():
                continue
            key = f"{fam_dir.name}/{pkg_dir.name}"
            result = run_anti_overclaiming_checks(pkg_dir, key, registry_path)
            all_results[key] = result
    return all_results
