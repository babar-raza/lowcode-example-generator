"""Doctor health check — TC-DOCTOR-001.

Checks Python version, packages, .NET SDK, tokens, LLM endpoint,
family configs, and format authority. Returns structured results.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class HealthCheck:
    """Result of a single health check."""
    name: str
    status: str  # PASS, WARN, FAIL, SKIP
    detail: str
    required: bool


def check_python_version() -> HealthCheck:
    """Check Python >= 3.12."""
    v = sys.version_info
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    if v >= (3, 12):
        return HealthCheck("python_version", "PASS", f"Python {version_str}", True)
    return HealthCheck("python_version", "FAIL", f"Python {version_str} < 3.12", True)


def check_required_packages() -> HealthCheck:
    """Check that required packages are importable."""
    required = ["jsonschema", "jinja2", "yaml", "requests"]
    missing = []
    for pkg in required:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if not missing:
        return HealthCheck("required_packages", "PASS", "All required packages importable", True)
    return HealthCheck("required_packages", "FAIL", f"Missing: {', '.join(missing)}", True)


def check_dotnet_sdk() -> HealthCheck:
    """Check .NET SDK availability."""
    try:
        result = subprocess.run(
            ["dotnet", "--version"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return HealthCheck("dotnet_sdk", "PASS", f"dotnet {version}", False)
        return HealthCheck("dotnet_sdk", "WARN", f"dotnet exited with code {result.returncode}", False)
    except FileNotFoundError:
        return HealthCheck("dotnet_sdk", "WARN", "dotnet not found in PATH", False)
    except subprocess.TimeoutExpired:
        return HealthCheck("dotnet_sdk", "WARN", "dotnet --version timed out", False)
    except Exception as exc:
        return HealthCheck("dotnet_sdk", "WARN", f"Error: {exc}", False)


def check_github_token() -> HealthCheck:
    """Check GITHUB_TOKEN presence (not its value)."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return HealthCheck("github_token", "PASS", "GITHUB_TOKEN or GH_TOKEN set", False)
    return HealthCheck("github_token", "WARN", "No GITHUB_TOKEN or GH_TOKEN (needed for publish only)", False)


def check_llm_endpoint() -> HealthCheck:
    """Check LLM endpoint configuration."""
    endpoint = os.environ.get("GPT_OSS_ENDPOINT", "")
    if not endpoint:
        return HealthCheck("llm_endpoint", "WARN", "GPT_OSS_ENDPOINT not set (needed for LLM generation)", False)
    if "professionalize.com" in endpoint:
        return HealthCheck("llm_endpoint", "PASS", f"Endpoint: {endpoint}", False)
    return HealthCheck("llm_endpoint", "WARN", f"Non-standard endpoint: {endpoint}", False)


def check_family_configs(repo_root: Path | None = None) -> HealthCheck:
    """Check that family config YAMLs are parseable."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    families_dir = repo_root / "pipeline" / "configs" / "families"
    if not families_dir.is_dir():
        return HealthCheck("family_configs", "FAIL", f"Directory not found: {families_dir}", True)
    import yaml
    errors = []
    count = 0
    for f in families_dir.iterdir():
        if f.suffix not in (".yml", ".yaml"):
            continue
        count += 1
        try:
            with open(f, encoding="utf-8") as fh:
                yaml.safe_load(fh)
        except Exception as exc:
            errors.append(f"{f.name}: {exc}")
    if errors:
        return HealthCheck("family_configs", "FAIL", f"{len(errors)} errors: {'; '.join(errors[:3])}", True)
    return HealthCheck("family_configs", "PASS", f"{count} configs parsed OK", True)


def check_format_authority(repo_root: Path | None = None) -> HealthCheck:
    """Check format authority manifest exists."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    manifest = repo_root / "pipeline" / "format-authority" / "manifest.json"
    if manifest.exists():
        return HealthCheck("format_authority", "PASS", f"manifest.json present ({manifest.stat().st_size} bytes)", True)
    return HealthCheck("format_authority", "FAIL", "pipeline/format-authority/manifest.json not found", True)


def check_evidence_chain(repo_root: Path | None = None) -> HealthCheck:
    """Check evidence chain consistency using ECV validators.

    Scans for gate result JSON files in .local/evidence-chain/ and runs
    ECV-01..04 validators. Returns SKIP if no evidence files are found.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    evidence_dir = repo_root / ".local" / "evidence-chain"
    if not evidence_dir.is_dir():
        return HealthCheck(
            "evidence_chain",
            "SKIP",
            "No evidence-chain directory found (.local/evidence-chain/ missing)",
            False,
        )

    gate_files = list(evidence_dir.glob("*.json"))
    if not gate_files:
        return HealthCheck(
            "evidence_chain",
            "SKIP",
            "No gate result JSON files in .local/evidence-chain/",
            False,
        )

    gate_results = []
    for gf in gate_files:
        try:
            data = json.loads(gf.read_text(encoding="utf-8"))
            if isinstance(data, list):
                gate_results.extend(data)
            elif isinstance(data, dict) and ("gate_id" in data or "id" in data or "verdict" in data):
                gate_results.append(data)
        except (json.JSONDecodeError, OSError):
            pass

    if not gate_results:
        return HealthCheck(
            "evidence_chain",
            "SKIP",
            f"Found {len(gate_files)} JSON files but none match gate result schema",
            False,
        )

    from plugin_examples.fixture_factory.evidence_chain_validators import run_all_ecv_validators
    ecv_results = run_all_ecv_validators(gate_results, evidence_dir)
    total = len(ecv_results)
    passed = sum(1 for r in ecv_results if r.passed)
    failed = total - passed
    if failed == 0:
        return HealthCheck(
            "evidence_chain",
            "PASS",
            f"ECV validators: {passed}/{total} passed — {len(gate_results)} gate records validated",
            False,
        )
    failures = [r.message for r in ecv_results if not r.passed][:3]
    return HealthCheck(
        "evidence_chain",
        "WARN",
        f"ECV validators: {passed}/{total} passed, {failed} failures. First: {failures[0]}",
        False,
    )


def _ehv_result_to_health_check(ehv_result: object) -> HealthCheck:
    """Convert a single EHVResult to a HealthCheck entry."""
    status = "PASS" if ehv_result.passed else "WARN"  # type: ignore[attr-defined]
    detail = ehv_result.message  # type: ignore[attr-defined]
    if getattr(ehv_result, "detail", ""):
        detail = f"{ehv_result.message} — {ehv_result.detail}"  # type: ignore[attr-defined]
    name = f"ehv_{ehv_result.validator_id.lower().replace('-', '_')}"  # type: ignore[attr-defined]
    return HealthCheck(name=name, status=status, detail=detail, required=False)


def check_engineering_hygiene_all(repo_root: Path | None = None) -> list[HealthCheck]:
    """Run EHV-01..05 validators and return one HealthCheck per validator.

    Exposes individual validator results so each EHV check is visible in
    the doctor summary (satisfies plan acceptance criterion: ≥ 12 checks).
    """
    try:
        from plugin_examples.fixture_factory.engineering_hygiene_validators import run_all_ehv_validators
        results = run_all_ehv_validators(repo_root)
        return [_ehv_result_to_health_check(r) for r in results]
    except Exception as exc:
        return [HealthCheck("engineering_hygiene", "WARN", f"EHV validators could not run: {exc}", False)]


def check_engineering_hygiene(repo_root: Path | None = None) -> HealthCheck:
    """Aggregated engineering hygiene check (backward-compatible single entry).

    Use check_engineering_hygiene_all() to get per-validator HealthCheck entries.
    """
    checks = check_engineering_hygiene_all(repo_root)
    total = len(checks)
    passed = sum(1 for c in checks if c.status == "PASS")
    failed = total - passed
    if failed == 0:
        return HealthCheck("engineering_hygiene", "PASS", f"EHV validators: {passed}/{total} passed", False)
    failures = [c.detail for c in checks if c.status != "PASS"]
    return HealthCheck(
        "engineering_hygiene",
        "WARN",
        f"EHV validators: {passed}/{total} passed, {failed} failed. First: {failures[0]}",
        False,
    )


def run_all_checks(repo_root: Path | None = None) -> list[HealthCheck]:
    """Run all health checks and return results.

    Returns 8 core checks + 5 individual EHV checks = 13 total (≥ 12 per plan).
    """
    checks = [
        check_python_version(),
        check_required_packages(),
        check_dotnet_sdk(),
        check_github_token(),
        check_llm_endpoint(),
        check_family_configs(repo_root),
        check_format_authority(repo_root),
        check_evidence_chain(repo_root),
    ]
    checks.extend(check_engineering_hygiene_all(repo_root))
    return checks


def format_results_text(results: list[HealthCheck]) -> str:
    """Format results as human-readable text."""
    lines = ["Health Check Results", "=" * 40]
    for r in results:
        marker = {"PASS": "[OK]", "WARN": "[!!]", "FAIL": "[XX]", "SKIP": "[--]"}.get(r.status, "[??]")
        req = " (required)" if r.required else ""
        lines.append(f"  {marker} {r.name}{req}: {r.detail}")
    total_fail = sum(1 for r in results if r.status == "FAIL")
    total_warn = sum(1 for r in results if r.status == "WARN")
    lines.append("")
    lines.append(f"Summary: {len(results)} checks, {total_fail} failed, {total_warn} warnings")
    return "\n".join(lines)


def format_results_json(results: list[HealthCheck]) -> str:
    """Format results as JSON."""
    return json.dumps({
        "checks": [asdict(r) for r in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.status == "PASS"),
            "warnings": sum(1 for r in results if r.status == "WARN"),
            "failed": sum(1 for r in results if r.status == "FAIL"),
        },
    }, indent=2)
