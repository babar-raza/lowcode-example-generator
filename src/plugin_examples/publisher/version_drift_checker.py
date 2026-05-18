"""All-family LowCode version drift checker.

Compares the NuGet latest version of each confirmed LowCode family package
against the version recorded in the family's denominator file. Reports
any version drift that may require denominator updates or re-runs.

Usage:
    python -m plugin_examples version-drift [--family FAMILY] [--json]
"""

from __future__ import annotations

import json
import logging
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Known LowCode families and their NuGet package IDs
LOWCODE_FAMILIES: dict[str, str] = {
    "cells": "Aspose.Cells",
    "words": "Aspose.Words",
    "pdf": "Aspose.PDF",
    "diagram": "Aspose.Diagram",
    "email": "Aspose.Email",
    "slides": "Aspose.Slides.NET",
}

# Blocked families — track their blocker dependency packages
BLOCKED_FAMILY_DEPS: dict[str, str] = {
    "ocr": "Aspose.AI.LLM",
    "psd": "Aspose.JavaAttributes",
}

NUGET_INDEX_URL = "https://api.nuget.org/v3-flatcontainer/{package_lower}/index.json"


@dataclass
class FamilyDriftResult:
    """Version drift result for one family."""
    family: str
    package_id: str
    denominator_version: str | None
    latest_nuget_version: str | None
    on_nuget: bool
    drift: bool
    drift_severity: str  # NONE | PATCH | MINOR | MAJOR | UNKNOWN
    status: str  # CURRENT | DRIFT | NOT_ON_NUGET | ERROR | NO_DENOMINATOR
    error: str | None = None


@dataclass
class VersionDriftReport:
    """Full version drift report for all families."""
    generated_at: str
    families: list[FamilyDriftResult] = field(default_factory=list)
    drifted_count: int = 0
    current_count: int = 0
    error_count: int = 0
    overall_verdict: str = "UNKNOWN"

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "drifted_count": self.drifted_count,
            "current_count": self.current_count,
            "error_count": self.error_count,
            "overall_verdict": self.overall_verdict,
            "families": [
                {
                    "family": r.family,
                    "package_id": r.package_id,
                    "denominator_version": r.denominator_version,
                    "latest_nuget_version": r.latest_nuget_version,
                    "on_nuget": r.on_nuget,
                    "drift": r.drift,
                    "drift_severity": r.drift_severity,
                    "status": r.status,
                    "error": r.error,
                }
                for r in self.families
            ],
        }


def _fetch_latest_nuget_version(package_id: str) -> tuple[str | None, bool, str | None]:
    """Return (latest_version, on_nuget, error_msg)."""
    url = NUGET_INDEX_URL.format(package_lower=package_id.lower())
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
        versions = data.get("versions", [])
        if not versions:
            return None, True, "No versions listed"
        return versions[-1], True, None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, False, f"HTTP 404 — package not on NuGet"
        return None, False, f"HTTP {e.code}"
    except Exception as e:
        return None, False, str(e)[:120]


def _load_denominator_version(family: str, repo_root: Path) -> str | None:
    """Load source_version from the family's denominator JSON."""
    denom_path = repo_root / "pipeline" / "configs" / "denominators" / f"{family}.json"
    if not denom_path.exists():
        return None
    try:
        with open(denom_path) as f:
            data = json.load(f)
        return data.get("source_version")
    except Exception:
        return None


def _compare_versions(a: str, b: str) -> int:
    """Return -1, 0, or 1. a < b → -1, a > b → 1."""
    def parts(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split(".") if x.isdigit())
    pa, pb = parts(a), parts(b)
    if pa < pb:
        return -1
    if pa > pb:
        return 1
    return 0


def _drift_severity(old: str, new: str) -> str:
    """Classify version change severity."""
    try:
        op = tuple(int(x) for x in old.split("."))
        np_ = tuple(int(x) for x in new.split("."))
        if len(op) < 2 or len(np_) < 2:
            return "UNKNOWN"
        if np_[0] != op[0]:
            return "MAJOR"
        if np_[1] != op[1]:
            return "MINOR"
        if len(op) >= 3 and len(np_) >= 3 and np_[2] != op[2]:
            return "PATCH"
        return "NONE"
    except Exception:
        return "UNKNOWN"


def run_version_drift_check(
    families: list[str] | None = None,
    repo_root: Path | None = None,
) -> VersionDriftReport:
    """Run version drift check for confirmed LowCode families.

    Args:
        families: Optional list of family names to check. Defaults to all.
        repo_root: Repository root path. Defaults to current directory.

    Returns:
        VersionDriftReport with results for each family.
    """
    from datetime import datetime, timezone

    if repo_root is None:
        repo_root = Path(".")
    if families is None:
        families = list(LOWCODE_FAMILIES.keys())

    report = VersionDriftReport(
        generated_at=datetime.now(timezone.utc).isoformat()
    )

    for family in families:
        if family not in LOWCODE_FAMILIES:
            logger.warning("Unknown family '%s' — skipping", family)
            continue

        package_id = LOWCODE_FAMILIES[family]
        denom_version = _load_denominator_version(family, repo_root)
        latest, on_nuget, error = _fetch_latest_nuget_version(package_id)

        if error and not on_nuget:
            result = FamilyDriftResult(
                family=family,
                package_id=package_id,
                denominator_version=denom_version,
                latest_nuget_version=None,
                on_nuget=False,
                drift=False,
                drift_severity="NONE",
                status="ERROR",
                error=error,
            )
            report.error_count += 1
        elif denom_version is None:
            result = FamilyDriftResult(
                family=family,
                package_id=package_id,
                denominator_version=None,
                latest_nuget_version=latest,
                on_nuget=on_nuget,
                drift=False,
                drift_severity="UNKNOWN",
                status="NO_DENOMINATOR",
            )
            report.error_count += 1
        else:
            drift = (latest is not None) and (_compare_versions(denom_version, latest) != 0)
            severity = _drift_severity(denom_version, latest) if drift and latest else "NONE"
            status = "DRIFT" if drift else "CURRENT"
            result = FamilyDriftResult(
                family=family,
                package_id=package_id,
                denominator_version=denom_version,
                latest_nuget_version=latest,
                on_nuget=on_nuget,
                drift=drift,
                drift_severity=severity,
                status=status,
            )
            if drift:
                report.drifted_count += 1
            else:
                report.current_count += 1

        report.families.append(result)

    # Overall verdict
    if report.drifted_count > 0:
        report.overall_verdict = "DRIFT_DETECTED"
    elif report.error_count > 0:
        report.overall_verdict = "PARTIAL_CHECK_ERRORS"
    else:
        report.overall_verdict = "ALL_CURRENT"

    return report
