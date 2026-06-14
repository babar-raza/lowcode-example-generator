"""
Package invariant rules for dry-run example packages.

Each rule returns None (pass) or a string violation message.
Rules are numbered INV-01 through INV-16.
"""

import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

Rule = Callable[[Path], str | None]

REGISTRY: list[tuple[str, Rule]] = []


def invariant(code: str):
    def decorator(fn: Rule):
        REGISTRY.append((code, fn))
        return fn

    return decorator


@invariant("INV-01")
def check_program_cs_exists(pkg_dir: Path) -> str | None:
    if not any(pkg_dir.glob("*.cs")):
        return "INV-01: No .cs source file found in package"
    return None


@invariant("INV-02")
def check_readme_exists(pkg_dir: Path) -> str | None:
    if not (pkg_dir / "README.md").exists():
        return "INV-02: README.md missing"
    return None


@invariant("INV-03")
def check_readme_has_run_cmd(pkg_dir: Path) -> str | None:
    readme = pkg_dir / "README.md"
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="replace")
        if "dotnet run" not in content:
            return "INV-03: README.md missing 'dotnet run' command"
    return None


@invariant("INV-04")
def check_source_provenance_exists(pkg_dir: Path) -> str | None:
    if not (pkg_dir / "source-provenance.json").exists():
        return "INV-04: source-provenance.json missing"
    return None


@invariant("INV-05")
def check_source_provenance_parseable(pkg_dir: Path) -> str | None:
    p = pkg_dir / "source-provenance.json"
    if p.exists():
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            return f"INV-05: source-provenance.json parse error: {e}"
    return None


@invariant("INV-06")
def check_output_validation_exists(pkg_dir: Path) -> str | None:
    if not (pkg_dir / "output-validation.json").exists():
        return "INV-06: output-validation.json missing"
    return None


@invariant("INV-07")
def check_output_validation_parseable(pkg_dir: Path) -> str | None:
    p = pkg_dir / "output-validation.json"
    if p.exists():
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            return f"INV-07: output-validation.json parse error: {e}"
    return None


@invariant("INV-08")
def check_restore_log_exists(pkg_dir: Path) -> str | None:
    if not (pkg_dir / "restore.log").exists():
        return "INV-08: restore.log missing (build may not have been run)"
    return None


@invariant("INV-09")
def check_build_log_exists(pkg_dir: Path) -> str | None:
    if not (pkg_dir / "build.log").exists():
        return "INV-09: build.log missing"
    return None


@invariant("INV-10")
def check_run_log_exists(pkg_dir: Path) -> str | None:
    if not (pkg_dir / "run.log").exists():
        return "INV-10: run.log missing"
    return None


@invariant("INV-11")
def check_no_bin_obj(pkg_dir: Path) -> str | None:
    for d in ["bin", "obj"]:
        if (pkg_dir / d).exists():
            return f"INV-11: {d}/ directory present (should not be committed)"
    return None


@invariant("INV-12")
def check_output_dir_has_nonzero_file(pkg_dir: Path) -> str | None:
    output_dir = pkg_dir / "output"
    if not output_dir.exists():
        return "INV-12: output/ directory missing"
    files = [f for f in output_dir.iterdir() if f.is_file()]
    if not files:
        return "INV-12: output/ directory is empty (no output files)"
    if all(f.stat().st_size == 0 for f in files):
        return "INV-12: all output files are zero bytes"
    return None


@invariant("INV-13")
def check_no_hardcoded_absolute_paths(pkg_dir: Path) -> str | None:
    for cs_file in pkg_dir.glob("*.cs"):
        content = cs_file.read_text(encoding="utf-8", errors="replace")
        import re

        # Windows absolute paths like C:\Users\...
        if re.search(r"[A-Z]:\\\\Users\\\\", content) or re.search(r'"[A-Z]:\\\\', content):
            return f"INV-13: Hardcoded Windows absolute path in {cs_file.name}"
        # Unix absolute paths
        if '"/home/' in content or '"/Users/' in content:
            return f"INV-13: Hardcoded Unix absolute path in {cs_file.name}"
    return None


@invariant("INV-14")
def check_csproj_exists(pkg_dir: Path) -> str | None:
    if not any(pkg_dir.glob("*.csproj")):
        return "INV-14: No .csproj file found in package"
    return None


@invariant("INV-15")
def check_canonical_url_in_provenance(pkg_dir: Path) -> str | None:
    p = pkg_dir / "source-provenance.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            url = data.get("canonical_url", "")
            if not url or url == "null":
                return "INV-15: canonical_url missing or null in source-provenance.json"
        except (OSError, json.JSONDecodeError, KeyError):
            logger.debug("Failed to read source-provenance.json in %s", pkg_dir, exc_info=True)
    return None


@invariant("INV-16")
def check_trial_watermark_disclosed(pkg_dir: Path) -> str | None:
    """If trial watermark is detected in output, README must mention 'trial' or 'evaluation'."""
    output_dir = pkg_dir / "output"
    trial_found = False
    if output_dir.exists():
        for f in output_dir.iterdir():
            if f.is_file() and f.suffix in (".txt",):
                content = f.read_text(encoding="utf-8", errors="replace").lower()
                if "trial" in content or "evaluation" in content:
                    trial_found = True
                    break
    if trial_found:
        readme = pkg_dir / "README.md"
        if readme.exists():
            readme_content = readme.read_text(encoding="utf-8", errors="replace").lower()
            if "trial" not in readme_content and "evaluation" not in readme_content:
                return "INV-16: Trial watermark detected in output but README.md does not disclose it"
    return None


def check_package(pkg_dir: Path) -> list[str]:
    """Run all invariant checks on a package directory. Returns list of violations."""
    violations = []
    for code, rule in REGISTRY:
        try:
            violation = rule(pkg_dir)
            if violation:
                violations.append(violation)
        except Exception as e:
            violations.append(f"{code}: check raised exception: {e}")
    return violations
