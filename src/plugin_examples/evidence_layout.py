"""Evidence layout utilities — family-scoped evidence promotion and path resolution.

Layout policy:
  - Run-scoped:  workspace/runs/{run_id}/evidence/latest/{file}  (canonical, never promoted)
  - Family primary:  workspace/verification/latest/families/{family}/{file}  (new, no cross-family collision)
  - Global:  workspace/verification/latest/{file}  (multi-family commands only)
  - Backward-compat alias:  workspace/verification/latest/{file}  (still written, deprecated)
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import UTC, datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Taxonomy: files written to evidence_dir/latest/ during a single family run.
# These MUST be promoted to families/{family}/ to avoid cross-family collision.
# ---------------------------------------------------------------------------
FAMILY_SCOPED_EVIDENCE_FILES: frozenset[str] = frozenset(
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

# ---------------------------------------------------------------------------
# Global aggregate files that are intentionally written to the latest/ root
# because they aggregate data across multiple families or represent pipeline-level
# (not family-level) state. These are SAFE at the top level because they are
# genuinely multi-family aggregates and their overwrite-on-new-run is expected.
#
# Files NOT in this set that are written to latest/ root should raise a WARNING
# in promote_family_evidence() — they should prefer families/{family}/ paths.
# ---------------------------------------------------------------------------
GLOBAL_AGGREGATE_ALLOWLIST: frozenset[str] = frozenset(
    {
        # Manifest files (aggregated across all families)
        "release-status.json",
        "scenario-catalog.json",
        "all-family-lowcode-discovery.json",
        "family-generation-readiness-rank.json",
        "family-publish-readiness.json",
        "family-publishing-target-audit.json",
        "family-repo-access-check.json",
        "family-repo-access-resolution.json",
        # Pipeline-level metadata
        "_last_promoted_by.json",
        "open-taskcard-closure-matrix.json",
        "example-lifecycle-records.json",
        # Denominator and contract registries (global scope)
        "remediation-execution-state.json",
    }
)

# Files that already carry a {family}- prefix in their name — safe at top level.
ALREADY_FAMILY_PREFIXED_PATTERNS: tuple[str, ...] = (
    "-source-of-truth-proof.json",
    "-live-pr-result.json",
    "-merge-result.json",
    "-post-merge-clean-checkout-validation.json",
    "-dependency-dedup-report.json",
    "-live-pr-canary-preflight.json",
    "-pr-dry-run-summary.json",
    "-live-pr-clean-checkout-validation.json",
)


def _is_already_family_prefixed(filename: str) -> bool:
    """Return True if the filename already embeds a family prefix."""
    return any(filename.endswith(suffix) for suffix in ALREADY_FAMILY_PREFIXED_PATTERNS)


def promote_family_evidence(
    src_latest: Path,
    verification_dir: Path,
    family: str,
    run_id: str,
) -> dict:
    """Promote evidence files from a run's evidence/latest/ to verification/latest/.

    Writes to two locations:
      1. PRIMARY:  verification/latest/families/{family}/  — family-isolated, no collision
      2. COMPAT:   verification/latest/  — backward-compat alias, tagged with notice

    Adds _evidence_metadata.json to the primary location.
    Adds _last_promoted_by.json to the compat location.

    Args:
        src_latest: Path to run's evidence/latest/ directory.
        verification_dir: Path to workspace/verification/.
        family: Family name (e.g. 'cells', 'words', 'pdf').
        run_id: Run identifier (e.g. 'pilot-cells-20260430-175422').

    Returns:
        Dict summarising what was promoted.
    """
    now = datetime.now(UTC).isoformat()

    # Primary: family-scoped directory
    dst_family = verification_dir / "latest" / "families" / family
    dst_family.mkdir(parents=True, exist_ok=True)

    # Backward-compat: top-level directory
    dst_top = verification_dir / "latest"
    dst_top.mkdir(parents=True, exist_ok=True)

    files_promoted: list[str] = []
    if src_latest.exists():
        for f in sorted(src_latest.iterdir()):
            if not f.is_file() or f.name == ".gitkeep":
                continue
            # Always write to primary family-scoped path
            shutil.copy2(f, dst_family / f.name)
            # Also write to top-level for backward compat
            # Warn if writing a family-scoped file to the shared latest/ root —
            # it risks cross-family contamination. Only GLOBAL_AGGREGATE_ALLOWLIST
            # files and ALREADY_FAMILY_PREFIXED_PATTERNS files are safe here.
            is_family_scoped = f.name in FAMILY_SCOPED_EVIDENCE_FILES
            is_allowlisted = f.name in GLOBAL_AGGREGATE_ALLOWLIST or _is_already_family_prefixed(f.name)
            if is_family_scoped and not is_allowlisted:
                logger.debug(
                    "Writing family-scoped file '%s' to latest/ root (backward compat). "
                    "Prefer families/%s/ path — will be overwritten by next family run.",
                    f.name,
                    family,
                )
            shutil.copy2(f, dst_top / f.name)
            files_promoted.append(f.name)

    # Promote family-scoped subdirectory files (e.g. families/{family}/*.json)
    # The completeness gate and other per-family evidence may be written to
    # evidence/latest/families/{family}/ during a run. These must be promoted
    # to workspace/verification/latest/families/{family}/ as well.
    src_family_sub = src_latest / "families" / family
    if src_family_sub.exists() and src_family_sub.is_dir():
        for f in sorted(src_family_sub.iterdir()):
            if not f.is_file() or f.name == ".gitkeep":
                continue
            shutil.copy2(f, dst_family / f.name)
            files_promoted.append(f"families/{family}/{f.name}")

    # Write metadata to family-scoped directory
    metadata: dict = {
        "scope": "family",
        "family": family,
        "run_id": run_id,
        "promoted_at": now,
        "source_run_path": str(src_latest.relative_to(src_latest.parents[4]))
        if src_latest.parents[4].exists()
        else str(src_latest),
        "files": sorted(files_promoted),
    }
    meta_path = dst_family / "_evidence_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # Write deprecation notice to top-level directory
    notice: dict = {
        "deprecated_latest_alias": True,
        "notice": (
            f"Files in this directory are a backward-compat alias. "
            f"Prefer workspace/verification/latest/families/{{family}}/ for family-specific evidence."
        ),
        "last_promoted_by_family": family,
        "last_promoted_run_id": run_id,
        "last_promoted_at": now,
        "warning": (
            "Files here may be overwritten by ANY family run. "
            "Not reliable in multi-family environments. "
            "Use families/{family}/ paths for reliable evidence isolation."
        ),
    }
    notice_path = dst_top / "_last_promoted_by.json"
    notice_path.write_text(json.dumps(notice, indent=2), encoding="utf-8")

    logger.info(
        "Evidence promoted: %d files to %s (primary) and %s (legacy alias)",
        len(files_promoted),
        dst_family,
        dst_top,
    )
    return {
        "family": family,
        "run_id": run_id,
        "files_promoted": sorted(files_promoted),
        "primary_path": str(dst_family),
        "compat_path": str(dst_top),
        "promoted_at": now,
    }


def resolve_family_evidence_path(
    verification_dir: Path,
    family: str,
    filename: str,
) -> Path:
    """Return the best available path for a family-specific evidence file.

    Checks family-scoped path first, falls back to legacy top-level with a warning.

    Args:
        verification_dir: Path to workspace/verification/.
        family: Family name (e.g. 'cells').
        filename: Evidence file name (e.g. 'validation-results.json').

    Returns:
        Path — may not exist if the file has never been promoted.
    """
    family_path = verification_dir / "latest" / "families" / family / filename
    if family_path.exists():
        return family_path

    legacy_path = verification_dir / "latest" / filename
    if legacy_path.exists():
        logger.warning(
            "Reading '%s' from deprecated top-level path. "
            "Prefer family-scoped path: verification/latest/families/%s/%s",
            filename,
            family,
            filename,
        )
        return legacy_path

    # Neither exists — return the family-scoped path for consistent missing-file handling
    return family_path


def detect_cross_family_contamination(
    verification_dir: Path,
    expected_family: str,
) -> list[str]:
    """Detect if verification/latest/ contains evidence from a different family.

    Reads _last_promoted_by.json to check if the last writer matches expected_family.

    Returns:
        List of contamination warnings. Empty if clean.
    """
    warnings: list[str] = []
    notice_path = verification_dir / "latest" / "_last_promoted_by.json"
    if not notice_path.exists():
        return warnings

    try:
        notice = json.loads(notice_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return warnings

    last_family = notice.get("last_promoted_by_family", "")
    last_run = notice.get("last_promoted_run_id", "")
    if last_family and last_family != expected_family:
        warnings.append(
            f"Cross-family contamination detected: verification/latest/ was last promoted "
            f"by '{last_family}' (run_id={last_run}), but expected '{expected_family}'. "
            f"Use verification/latest/families/{expected_family}/ for isolated evidence."
        )
    return warnings
