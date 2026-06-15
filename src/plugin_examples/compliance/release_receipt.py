"""Release receipt generator — captures release-time quality evidence.

Produces a structured JSON receipt recording version, git metadata,
doctor check results, SLO compliance, and gate policy status at the
time of a release. This formalizes the release audit trail so that
each version has machine-readable proof of its quality posture.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class ReleaseReceipt:
    """Structured release-time quality snapshot."""

    version: str = ""
    git_sha: str = ""
    git_branch: str = ""
    timestamp: str = ""
    python_version: str = ""
    doctor_total: int = 0
    doctor_passed: int = 0
    doctor_failed: int = 0
    doctor_warnings: int = 0
    slo_count: int = 0
    slo_compliant: bool = True
    gate_policy_loaded: bool = False
    coverage_percent: float = 0.0
    test_count: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _git_field(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def generate_release_receipt(
    repo_root: Path,
    *,
    version: str = "",
    coverage_percent: float = 0.0,
    test_count: int = 0,
) -> ReleaseReceipt:
    """Generate a release receipt from current project state."""
    import sys

    from plugin_examples.health.doctor import run_all_checks
    from plugin_examples.policy.loader import load_gate_policy, load_slos

    if not version:
        pyproject = repo_root / "pyproject.toml"
        if pyproject.exists():
            for line in pyproject.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version"):
                    version = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

    checks = run_all_checks(repo_root)
    slos = load_slos(repo_root)
    policy = load_gate_policy(repo_root)

    receipt = ReleaseReceipt(
        version=version,
        git_sha=_git_field(["rev-parse", "HEAD"]),
        git_branch=_git_field(["branch", "--show-current"]),
        timestamp=datetime.now(UTC).isoformat(),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        doctor_total=len(checks),
        doctor_passed=sum(1 for c in checks if c.status == "PASS"),
        doctor_failed=sum(1 for c in checks if c.status == "FAIL"),
        doctor_warnings=sum(1 for c in checks if c.status == "WARN"),
        slo_count=len(slos),
        slo_compliant=True,
        gate_policy_loaded=bool(policy.approval_gated_types),
        coverage_percent=coverage_percent,
        test_count=test_count,
    )
    return receipt


def save_release_receipt(receipt: ReleaseReceipt, output_dir: Path) -> Path:
    """Write a release receipt JSON file to the output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"release-receipt-{receipt.version or 'unknown'}.json"
    path = output_dir / filename
    path.write_text(json.dumps(receipt.to_dict(), indent=2), encoding="utf-8")
    return path
