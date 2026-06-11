"""Evidence completeness gate — verifies that all expected family-scoped evidence files exist.

This gate is NON-BLOCKING by default (mode=WARNING). It logs missing files and
returns a CompletionResult but does not halt the pipeline.

Rationale: Evidence completeness is a governance signal, not a hard gate.
Blocking runs on incomplete evidence would prevent recovery from partial failures.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Expected files per family per run.
# Mirrors FAMILY_SCOPED_EVIDENCE_FILES in evidence_layout.py.
# ---------------------------------------------------------------------------

EXPECTED_FAMILY_EVIDENCE_FILES: frozenset[str] = frozenset(
    {
        "aggregate-gate-results.json",
        "api-consumer-relationships.json",
        "api-delta-report.json",
        "blocked-scenarios.json",
        "example-gate-results.json",
        "example-impact-report.json",
        "example-reviewer-results.json",
        "fixture-strategy-plan.json",
        "gate-results.json",
        "generated-fixtures.json",
        "llm-fewshot-patterns.json",
        "llm-preflight.json",
        "plugin-type-role-classification.json",
        "publishing-report.json",
        "repair-attempts.json",
        "reviewer-preflight.json",
        "runnable-entrypoint-scores.json",
        "scenario-feedback-updates.json",
        "scenario-input-format-map.json",
        "stale-existing-examples.json",
        "validation-results.json",
        "pr-candidate-manifest.json",
    }
)

# Files that are always expected regardless of run configuration.
ALWAYS_EXPECTED: frozenset[str] = frozenset(
    {
        "aggregate-gate-results.json",
        "blocked-scenarios.json",
        "fixture-strategy-plan.json",
        "publishing-report.json",
        "validation-results.json",
    }
)


@dataclass
class CompletionResult:
    """Result of an evidence completeness check."""

    family: str
    run_id: str
    checked_at: str
    evidence_dir: str
    total_expected: int
    total_found: int
    total_missing: int
    missing_files: list[str] = field(default_factory=list)
    found_files: list[str] = field(default_factory=list)
    completeness_pct: float = 0.0
    status: str = "UNKNOWN"  # COMPLETE | INCOMPLETE | ERROR
    mode: str = "WARNING"  # WARNING | BLOCKING

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "run_id": self.run_id,
            "checked_at": self.checked_at,
            "evidence_dir": self.evidence_dir,
            "total_expected": self.total_expected,
            "total_found": self.total_found,
            "total_missing": self.total_missing,
            "missing_files": sorted(self.missing_files),
            "found_files": sorted(self.found_files),
            "completeness_pct": round(self.completeness_pct, 1),
            "status": self.status,
            "mode": self.mode,
        }


def check_completeness(
    family: str,
    evidence_dir: Path,
    run_id: str = "",
    mode: str = "WARNING",
    expected_files: frozenset[str] | None = None,
) -> CompletionResult:
    """Check evidence completeness for a family run.

    Args:
        family: Family name (e.g., 'cells').
        evidence_dir: Base evidence dir (workspace/runs/{run_id}/evidence/).
                     Checks evidence_dir/latest/ for family-scoped files.
        run_id: Run identifier for reporting.
        mode: 'WARNING' (log only) or 'BLOCKING' (raise on missing always-expected files).
        expected_files: Override the expected file set. Defaults to EXPECTED_FAMILY_EVIDENCE_FILES.

    Returns:
        CompletionResult with completeness summary.
    """
    checked_at = datetime.now(timezone.utc).isoformat()
    expected = expected_files if expected_files is not None else EXPECTED_FAMILY_EVIDENCE_FILES

    # Check evidence_dir/latest/ for files
    latest_dir = evidence_dir / "latest"
    evidence_dir_str = str(evidence_dir)

    if not latest_dir.exists():
        logger.warning(
            "Evidence completeness check: evidence_dir/latest/ does not exist at %s. "
            "Run may not have completed enough stages.",
            latest_dir,
        )
        return CompletionResult(
            family=family,
            run_id=run_id,
            checked_at=checked_at,
            evidence_dir=evidence_dir_str,
            total_expected=len(expected),
            total_found=0,
            total_missing=len(expected),
            missing_files=sorted(expected),
            found_files=[],
            completeness_pct=0.0,
            status="ERROR",
            mode=mode,
        )

    found: list[str] = []
    missing: list[str] = []

    for filename in expected:
        if (latest_dir / filename).exists():
            found.append(filename)
        else:
            missing.append(filename)

    total_expected = len(expected)
    total_found = len(found)
    total_missing = len(missing)
    completeness_pct = (total_found / total_expected * 100.0) if total_expected > 0 else 0.0
    status = "COMPLETE" if total_missing == 0 else "INCOMPLETE"

    result = CompletionResult(
        family=family,
        run_id=run_id,
        checked_at=checked_at,
        evidence_dir=evidence_dir_str,
        total_expected=total_expected,
        total_found=total_found,
        total_missing=total_missing,
        missing_files=missing,
        found_files=found,
        completeness_pct=completeness_pct,
        status=status,
        mode=mode,
    )

    if total_missing > 0:
        logger.warning(
            "Evidence completeness: %s/%s files present for family=%s run_id=%s (%.1f%%). " "Missing: %s",
            total_found,
            total_expected,
            family,
            run_id or "unknown",
            completeness_pct,
            missing[:5],  # Log first 5 to avoid log flood
        )

        if mode == "BLOCKING":
            # In blocking mode, raise on missing always-expected files
            always_missing = [f for f in missing if f in ALWAYS_EXPECTED]
            if always_missing:
                raise RuntimeError(
                    f"Evidence completeness gate FAILED for family={family}: "
                    f"always-expected files missing: {always_missing}. "
                    f"Use mode='WARNING' to downgrade to non-blocking."
                )
    else:
        logger.info(
            "Evidence completeness: all %s files present for family=%s (100%%)",
            total_expected,
            family,
        )

    return result


def write_completeness_report(result: CompletionResult, output_dir: Path) -> Path:
    """Write evidence-completeness-check.json to the given directory.

    Args:
        result: CompletionResult from check_completeness().
        output_dir: Directory to write the report (typically families/{family}/).

    Returns:
        Path of the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "evidence-completeness-check.json"
    out_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    logger.info("Evidence completeness report written to %s", out_path)
    return out_path
