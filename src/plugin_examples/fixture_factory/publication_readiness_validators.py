"""
Publication Readiness Validators (PRV-01..PRV-04)
Wave 16: verify that PCLC packages in readiness files have proper PR packet entries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class PRVResult:
    rule_id: str
    description: str
    passed: bool
    detail: str


def prv_01_all_pclc_have_pr_packet(readiness: dict) -> PRVResult:
    """PRV-01: Every PCLC entry must have pr_packet_exists=true."""
    packages = readiness.get("packages", [])
    missing = [f"{p.get('family')}/{p.get('slug')}" for p in packages if not p.get("pr_packet_exists", False)]
    if missing:
        return PRVResult(
            rule_id="PRV-01",
            description="Every PCLC entry must have pr_packet_exists=true",
            passed=False,
            detail=f"Missing PR packets: {missing}",
        )
    return PRVResult(
        rule_id="PRV-01",
        description="Every PCLC entry must have pr_packet_exists=true",
        passed=True,
        detail=f"All {len(packages)} PCLC packages have pr_packet_exists=true",
    )


def prv_02_all_pr_branches_match_pattern(readiness: dict) -> PRVResult:
    """PRV-02: All PR branches must match lowcode/{family}/{slug} pattern."""
    packages = readiness.get("packages", [])
    pattern = re.compile(r"^lowcode/[a-z0-9-]+/[a-z0-9-]+$")
    invalid = []
    for p in packages:
        branch = p.get("pr_branch", "")
        if branch and not pattern.match(branch):
            invalid.append(branch)
    if invalid:
        return PRVResult(
            rule_id="PRV-02",
            description="All PR branches must match lowcode/{family}/{slug} pattern",
            passed=False,
            detail=f"Invalid branches: {invalid}",
        )
    return PRVResult(
        rule_id="PRV-02",
        description="All PR branches must match lowcode/{family}/{slug} pattern",
        passed=True,
        detail=f"All {len(packages)} branches match pattern",
    )


def prv_03_no_duplicate_pr_branches(readiness: dict) -> PRVResult:
    """PRV-03: No duplicate PR branches in the readiness file."""
    packages = readiness.get("packages", [])
    branches = [p.get("pr_branch", "") for p in packages if p.get("pr_branch")]
    seen = set()
    duplicates = []
    for b in branches:
        if b in seen:
            duplicates.append(b)
        seen.add(b)
    if duplicates:
        return PRVResult(
            rule_id="PRV-03",
            description="No duplicate PR branches in readiness file",
            passed=False,
            detail=f"Duplicate branches: {duplicates}",
        )
    return PRVResult(
        rule_id="PRV-03",
        description="No duplicate PR branches in readiness file",
        passed=True,
        detail=f"No duplicates in {len(branches)} branches",
    )


def prv_04_pclc_total_matches_packages_length(readiness: dict) -> PRVResult:
    """PRV-04: pclc_total must equal the number of packages listed."""
    declared = readiness.get("pclc_total")
    actual = len(readiness.get("packages", []))
    if declared is None:
        return PRVResult(
            rule_id="PRV-04",
            description="pclc_total must match packages array length",
            passed=False,
            detail="pclc_total field missing from readiness file",
        )
    if declared != actual:
        return PRVResult(
            rule_id="PRV-04",
            description="pclc_total must match packages array length",
            passed=False,
            detail=f"pclc_total={declared} but packages list has {actual} entries",
        )
    return PRVResult(
        rule_id="PRV-04",
        description="pclc_total must match packages array length",
        passed=True,
        detail=f"pclc_total={declared} matches packages list length",
    )


def run_all_prv(readiness: dict) -> list[PRVResult]:
    """Run all PRV validators against a readiness file dict."""
    return [
        prv_01_all_pclc_have_pr_packet(readiness),
        prv_02_all_pr_branches_match_pattern(readiness),
        prv_03_no_duplicate_pr_branches(readiness),
        prv_04_pclc_total_matches_packages_length(readiness),
    ]
