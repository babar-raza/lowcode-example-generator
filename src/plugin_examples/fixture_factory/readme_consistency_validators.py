"""README/source consistency validators RCV-01..05 — TC-RCV-001.

Validates that README claims match filesystem and source truth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RcvResult:
    """Result of a README consistency validation rule."""
    rule_id: str
    passed: bool
    detail: str


def rcv_01_active_family_count(
    readme_text: str,
    contract_dirs: list[str],
) -> RcvResult:
    """RCV-01: README active family count matches pipeline/contracts/ subdirs."""
    # Look for patterns like "N active families" or "N production families"
    match = re.search(r"(\d+)\s+(?:active|production)\s+famil", readme_text, re.IGNORECASE)
    if not match:
        return RcvResult(
            rule_id="RCV-01",
            passed=True,
            detail="No active family count claim found in README (no drift possible)",
        )
    claimed = int(match.group(1))
    actual = len(contract_dirs)
    return RcvResult(
        rule_id="RCV-01",
        passed=claimed == actual,
        detail=f"README claims {claimed} active families, contracts/ has {actual}",
    )


def rcv_02_staged_family_count(
    readme_text: str,
    staged_count: int,
) -> RcvResult:
    """RCV-02: README staged count matches config-only families."""
    match = re.search(r"(\d+)\s+(?:staged|experimental|discovery)", readme_text, re.IGNORECASE)
    if not match:
        return RcvResult(
            rule_id="RCV-02",
            passed=True,
            detail="No staged family count claim found in README",
        )
    claimed = int(match.group(1))
    return RcvResult(
        rule_id="RCV-02",
        passed=claimed == staged_count,
        detail=f"README claims {claimed} staged families, found {staged_count}",
    )


def rcv_03_cli_commands_match(
    readme_text: str,
    registered_commands: list[str],
) -> RcvResult:
    """RCV-03: README CLI commands match registered subcommands."""
    missing = []
    for cmd in registered_commands:
        if cmd not in readme_text:
            missing.append(cmd)
    return RcvResult(
        rule_id="RCV-03",
        passed=len(missing) == 0,
        detail=f"Missing from README: {sorted(missing)}" if missing else "All CLI commands referenced",
    )


def rcv_04_example_count(
    readme_text: str,
    contract_example_count: int,
) -> RcvResult:
    """RCV-04: README example count matches contract count."""
    match = re.search(r"(\d+)\s+(?:example|scenario|package)s?\b", readme_text, re.IGNORECASE)
    if not match:
        return RcvResult(
            rule_id="RCV-04",
            passed=True,
            detail="No example count claim found in README",
        )
    claimed = int(match.group(1))
    return RcvResult(
        rule_id="RCV-04",
        passed=claimed == contract_example_count,
        detail=f"README claims {claimed} examples, contracts have {contract_example_count}",
    )


def rcv_05_no_removed_family_references(
    readme_text: str,
    removed_families: list[str],
) -> RcvResult:
    """RCV-05: No references to removed families in README."""
    found = [f for f in removed_families if f.lower() in readme_text.lower()]
    return RcvResult(
        rule_id="RCV-05",
        passed=len(found) == 0,
        detail=f"Removed families still referenced: {found}" if found else "No removed family references",
    )


def validate_readme_consistency(
    readme_text: str,
    contract_dirs: list[str],
    staged_count: int,
    registered_commands: list[str],
    contract_example_count: int,
    removed_families: list[str] | None = None,
) -> list[RcvResult]:
    """Run all RCV validators against a README and source truth."""
    results = [
        rcv_01_active_family_count(readme_text, contract_dirs),
        rcv_02_staged_family_count(readme_text, staged_count),
        rcv_03_cli_commands_match(readme_text, registered_commands),
        rcv_04_example_count(readme_text, contract_example_count),
        rcv_05_no_removed_family_references(readme_text, removed_families or []),
    ]
    return results
