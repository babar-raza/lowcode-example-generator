"""Hardened replay support for the LowCode Example Generator pipeline.

This module provides fail-closed artifact reuse when re-entering the pipeline
at a stage after generation, validation, reviewer, or publisher, without
repeating expensive NuGet download, DLL extraction, and reflection steps.

All checks are fail-closed: a hard-fail raises ReplayIntegrityError and
writes stale-artifact-check.json before halting. Warnings are logged but
do not block execution.

Governance:
- scenario_planning is NEVER skipped (HARD_STOP stage; enforces denominator and completeness)
- Publisher replay requires reviewer evidence and gate verdict in publishable range
- Typed deserialization: ValidationResult/DotnetResult are reconstructed from JSON, not plain dicts
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

VALID_REPLAY_STEPS = frozenset({"generation", "validation", "reviewer", "publisher"})

_INFRA_STAGES = frozenset(
    {
        "nuget_fetch",
        "dependency_resolution",
        "extraction",
        "reflection",
    }
)

# Gate verdicts that are acceptable for publisher replay
_PUBLISHABLE_VERDICTS = frozenset(
    {
        "PR_DRY_RUN_READY",
        "PR_READY",
        "FULL_E2E_PASSED",
        "PARTIAL_PR_DRY_RUN_READY",
        "PARTIAL_PR_READY",
    }
)


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class ReplayIntegrityError(RuntimeError):
    """Raised when a replay integrity check fails (fail-closed)."""


# ---------------------------------------------------------------------------
# Internal check collector
# ---------------------------------------------------------------------------


class _Checks:
    """Collects integrity check results; raises only after all checks run."""

    def __init__(self):
        self.items: list[dict] = []
        self._hard_failures: list[str] = []

    def record(
        self,
        check_id: str,
        status: str,
        expected: str = "",
        actual: str = "",
        message: str = "",
    ) -> None:
        """Record a check result. status: pass | fail | warn | skipped."""
        self.items.append(
            {
                "check_id": check_id,
                "status": status,
                "expected": expected,
                "actual": actual,
                "message": message,
            }
        )
        if status == "fail":
            self._hard_failures.append(f"[{check_id}] {message}")
        elif status == "warn":
            logger.warning("Replay integrity warn [%s]: %s", check_id, message)

    def raise_if_failed(self) -> None:
        if self._hard_failures:
            msg = "; ".join(self._hard_failures)
            raise ReplayIntegrityError(f"Replay blocked by {len(self._hard_failures)} integrity failure(s): {msg}")

    @property
    def overall(self) -> str:
        if any(c["status"] == "fail" for c in self.items):
            return "fail"
        if any(c["status"] == "warn" for c in self.items):
            return "warn"
        return "pass"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _find_catalog(prior_run_dir: Path, family: str) -> Path | None:
    """Search for api-catalog.json in the canonical locations of a prior run."""
    candidates = [
        prior_run_dir / "evidence" / "latest" / "api-catalog.json",
        prior_run_dir / "evidence" / "api-catalog.json",
        prior_run_dir / "catalog" / family / "api-catalog.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _find_example_index(prior_run_dir: Path) -> Path | None:
    """Search for example-index.json in the canonical locations."""
    candidates = [
        prior_run_dir / "evidence" / "example-index.json",
        prior_run_dir / "evidence" / "latest" / "example-index.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _find_validation_results(prior_run_dir: Path) -> Path | None:
    """Search for validation-results.json."""
    candidates = [
        prior_run_dir / "evidence" / "latest" / "validation-results.json",
        prior_run_dir / "evidence" / "validation-results.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def find_prior_run(family: str, repo_root: Path) -> str | None:
    """Return the most recent pilot-{family}-YYYYMMDD-HHMMSS run ID, or None.

    Ignores discovery- and multi-family- prefixed runs.
    Sorts lexicographically (YYYYMMDD-HHMMSS sorts correctly as a string).
    """
    runs_dir = repo_root / "workspace" / "runs"
    if not runs_dir.is_dir():
        return None
    prefix = f"pilot-{family}-"
    candidates = sorted(
        [d.name for d in runs_dir.iterdir() if d.is_dir() and d.name.startswith(prefix)],
        reverse=True,
    )
    return candidates[0] if candidates else None


def stages_to_skip(replay_from: str) -> frozenset[str]:
    """Return the stage names to skip for the given replay mode.

    scenario_planning is never in the skip set — it is a HARD_STOP stage
    that enforces denominator governance and the completeness gate.
    """
    if replay_from == "generation":
        return frozenset(_INFRA_STAGES)
    if replay_from == "validation":
        return frozenset(_INFRA_STAGES | {"generation"})
    if replay_from == "reviewer":
        return frozenset(_INFRA_STAGES | {"generation", "validation"})
    if replay_from == "publisher":
        return frozenset(_INFRA_STAGES | {"generation", "validation", "reviewer"})
    raise ValueError(
        f"Unknown replay_from value: {replay_from!r}. " f"Must be one of: {', '.join(sorted(VALID_REPLAY_STEPS))}"
    )


def check_replay_integrity(
    family: str,
    replay_from: str,
    prior_run_dir: Path,
    repo_root: Path,
) -> dict:
    """Run all hash/freshness checks for the given replay mode.

    Returns a stale-artifact-check dict (also written to prior_run_dir).
    Raises ReplayIntegrityError on hard failures (after writing the check file).
    """
    checks = _Checks()

    # 1. Catalog existence (hard fail)
    catalog_file = _find_catalog(prior_run_dir, family)
    if catalog_file is None:
        checks.record(
            "catalog_exists",
            "fail",
            message=(
                f"api-catalog.json not found in prior run '{prior_run_dir.name}'. "
                f"Searched: evidence/latest/, evidence/, catalog/{family}/"
            ),
        )
        result = _build_result(family, replay_from, prior_run_dir, checks)
        _write_stale_check(prior_run_dir, result)
        checks.raise_if_failed()
        return result  # unreachable but type-checker friendly
    checks.record("catalog_exists", "pass", message=str(catalog_file.relative_to(prior_run_dir)))

    # 2. Catalog hash vs denominator
    denominator_file = repo_root / "pipeline" / "configs" / "denominators" / f"{family}.json"
    if denominator_file.exists():
        try:
            denom = json.loads(denominator_file.read_text(encoding="utf-8"))
            expected_hash = denom.get("api_catalog_sha256", "")
            if expected_hash:
                # Use canonical JSON hash (same as scenario_planner.compute_catalog_hash)
                _catalog_data = json.loads(catalog_file.read_text(encoding="utf-8"))
                actual_hash = _sha256_text(json.dumps(_catalog_data, sort_keys=True, ensure_ascii=False))
                if actual_hash != expected_hash:
                    checks.record(
                        "catalog_hash",
                        "fail",
                        expected=expected_hash[:16] + "…",
                        actual=actual_hash[:16] + "…",
                        message=(
                            "API catalog SHA256 does not match denominator. "
                            "The prior run used a different package version or the catalog was modified."
                        ),
                    )
                else:
                    checks.record(
                        "catalog_hash", "pass", expected=expected_hash[:16] + "…", actual=actual_hash[:16] + "…"
                    )
            else:
                checks.record("catalog_hash", "skipped", message="No api_catalog_sha256 field in denominator")
        except Exception as exc:
            checks.record("catalog_hash", "warn", message=f"Could not verify catalog hash: {exc}")
    else:
        checks.record("catalog_hash", "skipped", message=f"No denominator file for family '{family}'")

    # 3. Package version from catalog vs family YAML
    try:
        catalog_data = json.loads(catalog_file.read_text(encoding="utf-8"))
        catalog_version = (
            catalog_data.get("package_version")
            or catalog_data.get("nuget_version")
            or catalog_data.get("version")
            or ""
        )
        family_yml = repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
        if family_yml.exists():
            yml_text = family_yml.read_text(encoding="utf-8")
            m = re.search(r'pinned_version\s*:\s*["\']?([0-9][0-9.]+)["\']?', yml_text)
            yml_version = m.group(1) if m else ""
            if yml_version and catalog_version and yml_version != catalog_version:
                checks.record(
                    "package_version",
                    "fail",
                    expected=yml_version,
                    actual=catalog_version,
                    message=(
                        "Package version in family config differs from prior run catalog. "
                        "The NuGet package was updated; replay would use stale API definitions."
                    ),
                )
            else:
                checks.record(
                    "package_version",
                    "pass",
                    expected=yml_version,
                    actual=catalog_version,
                    message="Package version verified (or not pinned)",
                )
        else:
            checks.record("package_version", "skipped", message="Family YAML not found")
    except Exception as exc:
        checks.record("package_version", "warn", message=f"Could not verify package version: {exc}")

    # 4. Family config hash (warn only — user may intentionally update config)
    _check_stored_hash(
        checks,
        prior_run_dir,
        "load_config",
        "config_hash",
        check_id="config_hash",
        current_hash_fn=lambda: _sha256_file(repo_root / "pipeline" / "configs" / "families" / f"{family}.yml")
        if (repo_root / "pipeline" / "configs" / "families" / f"{family}.yml").exists()
        else "",
        warn_only=True,
        warn_message=(
            "Family config YAML has changed since the prior run. "
            "Constraints, allowed_types, or generation settings may differ."
        ),
    )

    # 5. Denominator hash (warn only)
    _check_stored_hash(
        checks,
        prior_run_dir,
        "scenario_planning",
        "denominator_hash",
        check_id="denominator_hash",
        current_hash_fn=lambda: _sha256_file(denominator_file) if denominator_file.exists() else "",
        warn_only=True,
        warn_message="Denominator JSON has changed. Coverage metrics may differ from prior run.",
    )

    # 6. Constraints hash — hard fail for validation+ (code generated against old constraints)
    _check_stored_hash(
        checks,
        prior_run_dir,
        "load_config",
        "constraints_hash",
        check_id="constraints_hash",
        current_hash_fn=lambda: _compute_constraints_hash(
            repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
        ),
        warn_only=(replay_from == "generation"),
        warn_message=(
            "per_type_constraints have changed. Generated code may violate new constraints. "
            "Consider running from generation instead."
        ),
    )

    # 7. Scenario contract family match
    try:
        scenario_catalog = prior_run_dir / "evidence" / "latest" / "scenario-catalog.json"
        if scenario_catalog.exists():
            sc = json.loads(scenario_catalog.read_text(encoding="utf-8"))
            if sc.get("family") and sc["family"] != family:
                checks.record(
                    "scenario_contract_family",
                    "fail",
                    expected=family,
                    actual=sc["family"],
                    message="scenario-catalog.json family does not match requested family.",
                )
            else:
                checks.record("scenario_contract_family", "pass")
        else:
            checks.record("scenario_contract_family", "skipped", message="No scenario-catalog.json in prior run")
    except Exception as exc:
        checks.record("scenario_contract_family", "warn", message=f"Could not verify scenario contract: {exc}")

    # 8. Generated projects exist (for validation/reviewer/publisher)
    if replay_from in {"validation", "reviewer", "publisher"}:
        _check_generated_projects(checks, prior_run_dir, family, repo_root)

    # 9. Validation results valid (for reviewer/publisher)
    if replay_from in {"reviewer", "publisher"}:
        _check_validation_results(checks, prior_run_dir)

    # 10. Publisher-specific evidence
    if replay_from == "publisher":
        _check_publisher_evidence(checks, prior_run_dir)

    # Build result and write
    result = _build_result(family, replay_from, prior_run_dir, checks)
    _write_stale_check(prior_run_dir, result)

    # Raise after writing (so the file always exists for diagnosis)
    checks.raise_if_failed()
    return result


# ---------------------------------------------------------------------------
# Restore functions
# ---------------------------------------------------------------------------


def restore_catalog(prior_run_dir: Path, family: str) -> tuple[dict, Path]:
    """Load and return (catalog_dict, catalog_path) from prior run.

    Raises ReplayIntegrityError if the catalog is missing or unparseable.
    """
    catalog_file = _find_catalog(prior_run_dir, family)
    if catalog_file is None:
        raise ReplayIntegrityError(f"api-catalog.json not found in prior run '{prior_run_dir.name}'")
    try:
        data = json.loads(catalog_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ReplayIntegrityError(f"Failed to parse api-catalog.json from '{prior_run_dir.name}': {exc}") from exc
    return data, catalog_file


def restore_generated_projects(
    prior_run_dir: Path,
    family: str,
    repo_root: Path,
) -> list[dict]:
    """Reconstruct ctx.generated_projects from prior run's example-index.json.

    Each project_dir is rewritten to an absolute path under repo_root.
    Raises ReplayIntegrityError if the index is missing, unparseable, or
    any project directory / Program.cs file is absent.
    """
    index_file = _find_example_index(prior_run_dir)
    if index_file is None:
        raise ReplayIntegrityError(f"example-index.json not found in prior run '{prior_run_dir.name}'")
    try:
        raw = json.loads(index_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ReplayIntegrityError(f"Failed to parse example-index.json from '{prior_run_dir.name}': {exc}") from exc

    examples = raw if isinstance(raw, list) else raw.get("examples", [])
    if not examples:
        logger.warning("replay: example-index.json in '%s' has no examples", prior_run_dir.name)
        return []

    repo_root_resolved = repo_root.resolve()
    result = []
    for proj in examples:
        proj = dict(proj)
        scenario_id = proj.get("scenario_id", "unknown")

        raw_dir = proj.get("project_dir", "")
        original_path = Path(raw_dir) if raw_dir else None

        # Safety: if the original path is absolute, check it's inside repo_root BEFORE
        # applying the fallback. This catches path injection even when the path doesn't
        # exist on disk (the check runs on the declared path, not a resolved fallback).
        if original_path and original_path.is_absolute():
            try:
                resolved_original = original_path.resolve()
            except Exception:
                resolved_original = original_path
            if not str(resolved_original).startswith(str(repo_root_resolved)):
                raise ReplayIntegrityError(
                    f"project_dir for scenario '{scenario_id}' escapes repo_root: " f"{original_path}"
                )

        # Determine actual project_dir, falling back to prior run's generated/ dir
        project_dir = original_path
        if project_dir is None or not project_dir.exists():
            project_dir = prior_run_dir / "generated" / family / scenario_id

        project_dir = project_dir.resolve()

        # Final repo_root safety check (also catches relative paths resolving outside)
        if not str(project_dir).startswith(str(repo_root_resolved)):
            raise ReplayIntegrityError(f"project_dir for scenario '{scenario_id}' escapes repo_root: " f"{project_dir}")

        if not project_dir.is_dir():
            raise ReplayIntegrityError(f"project_dir for scenario '{scenario_id}' does not exist: " f"{project_dir}")

        # Validate Program.cs
        program_path = project_dir / "Program.cs"
        if not program_path.exists():
            raise ReplayIntegrityError(f"Program.cs missing for scenario '{proj.get('scenario_id')}': {program_path}")
        if program_path.stat().st_size == 0:
            raise ReplayIntegrityError(f"Program.cs is empty for scenario '{proj.get('scenario_id')}': {program_path}")

        # Rewrite paths
        proj["project_dir"] = str(project_dir)
        proj["program_path"] = str(program_path)

        # Rewrite csproj_path if present
        raw_csproj = proj.get("csproj_path", "")
        if raw_csproj:
            csproj = Path(raw_csproj)
            if not csproj.exists():
                csproj = project_dir / csproj.name
            proj["csproj_path"] = str(csproj)

        result.append(proj)

    return result


def restore_validation_results(prior_run_dir: Path) -> list:
    """Reconstruct a list of typed ValidationResult objects from prior run.

    Imports ValidationResult / DotnetResult from the verifier_bridge and
    constructs instances from the JSON — no plain dicts, no SimpleNamespace.

    Raises ReplayIntegrityError if the file is missing or unparseable.
    """
    from plugin_examples.verifier_bridge.dotnet_runner import (  # noqa: PLC0415
        DotnetResult,
        ValidationResult,
    )

    results_file = _find_validation_results(prior_run_dir)
    if results_file is None:
        raise ReplayIntegrityError(f"validation-results.json not found in prior run '{prior_run_dir.name}'")
    try:
        raw = json.loads(results_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ReplayIntegrityError(
            f"Failed to parse validation-results.json from '{prior_run_dir.name}': {exc}"
        ) from exc

    records = raw.get("results", raw) if isinstance(raw, dict) else raw
    if not isinstance(records, list):
        raise ReplayIntegrityError(f"validation-results.json has unexpected structure in '{prior_run_dir.name}'")

    def _to_dotnet(d: dict | None) -> "DotnetResult | None":
        if not d:
            return None
        return DotnetResult(
            operation=d.get("operation", ""),
            success=bool(d.get("success", False)),
            exit_code=int(d.get("exit_code", 0)),
            stdout=d.get("stdout", ""),
            stderr=d.get("stderr", ""),
            duration_ms=float(d.get("duration_ms", 0.0)),
        )

    out = []
    for rec in records:
        if not isinstance(rec, dict):
            raise ReplayIntegrityError(f"Unexpected record type {type(rec)} in validation-results.json")
        vr = ValidationResult(
            scenario_id=rec["scenario_id"],
            passed=bool(rec.get("passed", False)),
            failure_stage=rec.get("failure_stage"),
            restore=_to_dotnet(rec.get("restore")),
            build=_to_dotnet(rec.get("build")),
            run=_to_dotnet(rec.get("run")),
        )
        out.append(vr)
    return out


def copy_reviewer_evidence(prior_run_dir: Path, evidence_dir: Path, family: str) -> None:
    """Copy prior reviewer evidence into the current run's evidence/latest/ dir.

    Required for publisher replay: the publisher stage reads reviewer results
    from the current run's evidence directory.

    Raises ReplayIntegrityError if reviewer evidence is missing or invalid.
    """
    evidence_latest = evidence_dir / "latest"
    evidence_latest.mkdir(parents=True, exist_ok=True)

    src = prior_run_dir / "evidence" / "latest" / "example-reviewer-results.json"
    if not src.exists():
        raise ReplayIntegrityError(
            f"example-reviewer-results.json not found in prior run '{prior_run_dir.name}'. "
            "Publisher replay requires reviewer evidence from the prior run."
        )

    try:
        reviewer_data = json.loads(src.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ReplayIntegrityError(f"Failed to parse example-reviewer-results.json: {exc}") from exc

    # Verify reviewer was actually available (not just a stub unavailable result)
    if not reviewer_data.get("available", False):
        raise ReplayIntegrityError(
            f"Prior run reviewer evidence shows available=false. "
            "Publisher replay requires a run where the reviewer actually executed."
        )

    dst = evidence_latest / "example-reviewer-results.json"
    shutil.copy2(src, dst)
    logger.info("replay: copied reviewer evidence from %s to %s", src, dst)

    # Also copy reviewer-preflight.json if present
    src_preflight = prior_run_dir / "evidence" / "latest" / "reviewer-preflight.json"
    if src_preflight.exists():
        shutil.copy2(src_preflight, evidence_latest / "reviewer-preflight.json")


def write_replay_manifest(
    evidence_dir: Path,
    replay_from: str,
    reuse_run_id: str,
    new_run_id: str,
    family: str,
    skipped_stages: frozenset,
    integrity_result: dict,
) -> None:
    """Write replay-manifest.json and restored-artifacts-report.json to evidence_dir/latest/."""
    evidence_latest = evidence_dir / "latest"
    evidence_latest.mkdir(parents=True, exist_ok=True)

    skipped_list = sorted(skipped_stages)

    # Determine which stages are regenerated vs executed
    _stage_order = [
        "load_config",
        "nuget_fetch",
        "dependency_resolution",
        "extraction",
        "reflection",
        "plugin_detection",
        "api_delta",
        "impact_mapping",
        "fixture_registry",
        "example_mining",
        "scenario_planning",
        "llm_preflight",
        "generation",
        "validation",
        "reviewer",
        "publisher",
    ]
    replay_idx = _stage_order.index(replay_from) if replay_from in _stage_order else len(_stage_order)
    regenerated = [s for s in _stage_order[:replay_idx] if s not in skipped_stages and s != "load_config"]
    # load_config always runs
    executed = _stage_order[replay_idx:]

    manifest = {
        "replay_from": replay_from,
        "reuse_run_id": reuse_run_id,
        "new_run_id": new_run_id,
        "family": family,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "skipped_stages": skipped_list,
        "always_run": ["load_config"],
        "regenerated_stages": regenerated,
        "executed_stages": executed,
        "hash_checks": {
            c["check_id"]: {
                "status": c["status"],
                "message": c.get("message", ""),
            }
            for c in integrity_result.get("checks", [])
        },
        "overall_integrity": integrity_result.get("overall", "unknown"),
    }

    (evidence_latest / "replay-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Restored artifacts report
    restored = []
    if replay_from in {"validation", "reviewer", "publisher"}:
        restored.append(
            {
                "stage": "generation",
                "artifact": "example-index.json",
                "status": "restored",
                "source": reuse_run_id,
            }
        )
    if replay_from in {"reviewer", "publisher"}:
        restored.append(
            {
                "stage": "validation",
                "artifact": "validation-results.json",
                "status": "restored",
                "source": reuse_run_id,
            }
        )
    if replay_from == "publisher":
        restored.append(
            {
                "stage": "reviewer",
                "artifact": "example-reviewer-results.json",
                "status": "restored",
                "source": reuse_run_id,
            }
        )
    # Catalog is always restored for any replay
    restored.append(
        {
            "stage": "reflection",
            "artifact": "api-catalog.json",
            "status": "restored",
            "source": reuse_run_id,
        }
    )

    report = {
        "reuse_run_id": reuse_run_id,
        "family": family,
        "replay_from": replay_from,
        "created_at": manifest["created_at"],
        "restored_artifacts": restored,
    }
    (evidence_latest / "restored-artifacts-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _compute_constraints_hash(family_yml: Path) -> str:
    if not family_yml.exists():
        return ""
    text = family_yml.read_text(encoding="utf-8")
    m = re.search(r"per_type_constraints\s*:(.+?)(?=\n\S|\Z)", text, re.DOTALL)
    constraints_text = m.group(1) if m else ""
    return _sha256_text(constraints_text)


def _check_stored_hash(
    checks: _Checks,
    prior_run_dir: Path,
    stage_name: str,
    artifact_key: str,
    check_id: str,
    current_hash_fn,
    warn_only: bool,
    warn_message: str,
) -> None:
    """Compare a stored hash from pilot-report.json against the current value."""
    try:
        pilot_report = prior_run_dir / "pilot-report.json"
        if not pilot_report.exists():
            checks.record(check_id, "skipped", message="No pilot-report.json in prior run")
            return
        report = json.loads(pilot_report.read_text(encoding="utf-8"))
        stored_hash = None
        for stage in report.get("stages", []):
            if stage.get("name") == stage_name:
                stored_hash = stage.get("artifacts", {}).get(artifact_key)
                break
        if not stored_hash:
            checks.record(check_id, "skipped", message=f"No stored {artifact_key!r} in prior run's {stage_name} stage")
            return
        current_hash = current_hash_fn()
        if not current_hash:
            checks.record(check_id, "skipped", message="Could not compute current hash")
            return
        if stored_hash != current_hash:
            severity = "warn" if warn_only else "fail"
            checks.record(
                check_id,
                severity,
                expected=stored_hash[:16] + "…",
                actual=current_hash[:16] + "…",
                message=warn_message,
            )
        else:
            checks.record(check_id, "pass", expected=stored_hash[:16] + "…", actual=current_hash[:16] + "…")
    except Exception as exc:
        checks.record(check_id, "warn", message=f"Could not verify {check_id}: {exc}")


def _check_generated_projects(
    checks: _Checks,
    prior_run_dir: Path,
    family: str,
    repo_root: Path,
) -> None:
    """Verify that generated project dirs and Program.cs files exist."""
    index_file = _find_example_index(prior_run_dir)
    if index_file is None:
        checks.record(
            "generated_projects_index",
            "fail",
            message=f"example-index.json not found in prior run '{prior_run_dir.name}'",
        )
        return
    try:
        raw = json.loads(index_file.read_text(encoding="utf-8"))
        examples = raw if isinstance(raw, list) else raw.get("examples", [])
    except Exception as exc:
        checks.record("generated_projects_index", "fail", message=f"Failed to parse example-index.json: {exc}")
        return

    if not examples:
        checks.record("generated_projects_index", "warn", message="example-index.json has no examples")
        return

    checks.record("generated_projects_index", "pass", message=f"{len(examples)} example(s) in index")

    repo_root_resolved = repo_root.resolve()
    missing_dirs = []
    missing_cs = []
    path_escapes = []

    for proj in examples:
        scenario_id = proj.get("scenario_id", "unknown")
        raw_dir = proj.get("project_dir", "")
        project_dir = Path(raw_dir) if raw_dir else None

        if project_dir is None or not project_dir.exists():
            project_dir = prior_run_dir / "generated" / family / scenario_id

        try:
            resolved = project_dir.resolve()
        except Exception:
            path_escapes.append(scenario_id)
            continue

        if not str(resolved).startswith(str(repo_root_resolved)):
            path_escapes.append(scenario_id)
            continue

        if not resolved.is_dir():
            missing_dirs.append(scenario_id)
            continue

        if not (resolved / "Program.cs").exists():
            missing_cs.append(scenario_id)

    if path_escapes:
        checks.record(
            "generated_project_path_safety",
            "fail",
            message=f"project_dir escapes repo_root for: {', '.join(path_escapes)}",
        )
    if missing_dirs:
        checks.record("generated_project_dirs", "fail", message=f"project_dir missing for: {', '.join(missing_dirs)}")
    if missing_cs:
        checks.record("generated_program_cs", "fail", message=f"Program.cs missing for: {', '.join(missing_cs)}")
    if not path_escapes and not missing_dirs and not missing_cs:
        checks.record(
            "generated_projects_all_present",
            "pass",
            message=f"All {len(examples)} project dirs and Program.cs files verified",
        )


def _check_validation_results(checks: _Checks, prior_run_dir: Path) -> None:
    """Verify validation-results.json is present and parseable."""
    results_file = _find_validation_results(prior_run_dir)
    if results_file is None:
        checks.record(
            "validation_results_exists",
            "fail",
            message=f"validation-results.json not found in prior run '{prior_run_dir.name}'",
        )
        return
    try:
        raw = json.loads(results_file.read_text(encoding="utf-8"))
        records = raw.get("results", raw) if isinstance(raw, dict) else raw
        if not isinstance(records, list):
            raise ValueError("'results' is not a list")
        # Check required fields
        for rec in records:
            for field in ("scenario_id", "passed"):
                if field not in rec:
                    raise ValueError(f"Missing required field '{field}' in record")
        checks.record("validation_results_valid", "pass", message=f"{len(records)} validation result(s) verified")
    except Exception as exc:
        checks.record("validation_results_valid", "fail", message=f"validation-results.json invalid: {exc}")


def _check_publisher_evidence(checks: _Checks, prior_run_dir: Path) -> None:
    """Run publisher-specific safety checks."""
    evidence_latest = prior_run_dir / "evidence" / "latest"

    # Reviewer evidence
    reviewer_file = evidence_latest / "example-reviewer-results.json"
    if not reviewer_file.exists():
        checks.record(
            "publisher_reviewer_evidence",
            "fail",
            message="example-reviewer-results.json not found. Publisher replay requires reviewer evidence.",
        )
    else:
        try:
            rd = json.loads(reviewer_file.read_text(encoding="utf-8"))
            if not rd.get("available", False):
                checks.record(
                    "publisher_reviewer_available",
                    "fail",
                    message="Reviewer evidence shows available=false. "
                    "Publisher replay requires a run where reviewer actually executed.",
                )
            else:
                checks.record("publisher_reviewer_available", "pass")
        except Exception as exc:
            checks.record("publisher_reviewer_available", "fail", message=f"Could not parse reviewer evidence: {exc}")

    # Gate results verdict
    gate_file = evidence_latest / "gate-results.json"
    if not gate_file.exists():
        checks.record(
            "publisher_gate_results",
            "fail",
            message="gate-results.json not found. Publisher replay requires prior gate evidence.",
        )
    else:
        try:
            gd = json.loads(gate_file.read_text(encoding="utf-8"))
            verdict = gd.get("verdict", "")
            if verdict not in _PUBLISHABLE_VERDICTS:
                checks.record(
                    "publisher_gate_verdict",
                    "fail",
                    expected=f"one of {sorted(_PUBLISHABLE_VERDICTS)}",
                    actual=verdict,
                    message=f"Gate verdict '{verdict}' is not in publishable range. "
                    "Publisher replay blocked on stale non-publishable gate results.",
                )
            else:
                checks.record("publisher_gate_verdict", "pass", actual=verdict)
        except Exception as exc:
            checks.record("publisher_gate_verdict", "fail", message=f"Could not parse gate-results.json: {exc}")

    # PR candidate manifest
    manifest_file = evidence_latest / "pr-candidate-manifest.json"
    if not manifest_file.exists():
        checks.record("publisher_pr_manifest", "fail", message="pr-candidate-manifest.json not found.")
    else:
        try:
            md = json.loads(manifest_file.read_text(encoding="utf-8"))
            # Use included_manifest_candidate_count (new safe field) if present,
            # otherwise fall back to publishable_candidate_count for older manifests.
            count = md.get(
                "included_manifest_candidate_count",
                md.get("publishable_candidate_count", 0),
            )
            if count == 0:
                checks.record(
                    "publisher_candidate_count",
                    "fail",
                    actual=str(count),
                    message="No candidates in prior pr-candidate-manifest.json "
                    "(included_manifest_candidate_count=0). Nothing to replay.",
                )
            else:
                checks.record("publisher_candidate_count", "pass", actual=str(count))
        except Exception as exc:
            checks.record("publisher_pr_manifest", "fail", message=f"Could not parse pr-candidate-manifest.json: {exc}")


def _build_result(
    family: str,
    replay_from: str,
    prior_run_dir: Path,
    checks: _Checks,
) -> dict:
    return {
        "family": family,
        "replay_from": replay_from,
        "reuse_run_id": prior_run_dir.name,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks.items,
        "overall": checks.overall,
    }


def _write_stale_check(prior_run_dir: Path, result: dict) -> None:
    """Write stale-artifact-check.json to prior run's evidence/latest/."""
    out_dir = prior_run_dir / "evidence" / "latest"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "stale-artifact-check.json"
    out_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.debug("replay: wrote stale-artifact-check.json to %s", out_dir)
