"""Example lifecycle tracking — ensures no example is silently dropped."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifecycle stages (ordered)
# ---------------------------------------------------------------------------

LIFECYCLE_STAGES = (
    "planned",
    "generation_attempted",
    "generated",
    "generation_failed",
    "build_attempted",
    "build_passed",
    "build_failed",
    "build_repaired",
    "run_attempted",
    "run_passed",
    "run_failed",
    "run_repaired",
    "reviewer_attempted",
    "reviewer_passed",
    "reviewer_failed",
    "reviewer_repaired",
    "pr_candidate",
    "excluded",
    "backlogged",
)


# ---------------------------------------------------------------------------
# Core dataclass
# ---------------------------------------------------------------------------

@dataclass
class ExampleLifecycleRecord:
    """Tracks the full lifecycle of a single planned example.

    Every scenario that enters the planner's ready_scenarios gets a record.
    Examples that fail at ANY stage remain tracked — never silently dropped.
    """
    scenario_id: str
    family: str
    run_id: str

    # Current state
    current_stage: str = "planned"
    final_verdict: str = "PENDING"

    # Stage outcomes (populated as the example progresses)
    generation_status: str = "pending"  # pending, passed, failed
    generation_failure_reason: str | None = None

    build_status: str = "pending"  # pending, passed, failed, repaired
    build_failure_reason: str | None = None
    build_repair_attempts: int = 0

    run_status: str = "pending"  # pending, passed, failed, repaired, skipped
    run_failure_reason: str | None = None
    run_repair_attempts: int = 0
    run_failure_classification: str | None = None

    reviewer_status: str = "pending"  # pending, passed, failed, repaired, skipped, unavailable
    reviewer_failure_reason: str | None = None
    reviewer_repair_attempts: int = 0

    # PR candidacy
    pr_candidate: bool = False
    excluded_reason: str | None = None

    # Backlog fields
    backlogged: bool = False
    backlog_root_cause: str | None = None
    backlog_recommended_fix: str | None = None
    backlog_priority: str = "medium"  # low, medium, high, critical

    # Run-to-run comparison fields (populated only when --compare-run is used)
    prior_run_id: str | None = None
    prior_state: str | None = None
    prior_run_result: str | None = None  # UNCHANGED, IMPROVED, REGRESSED, NEW_SCENARIO
    regression_detected: bool = False
    regression_reason: str | None = None

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def update_stage(self, stage: str) -> None:
        """Update current_stage and last_updated."""
        self.current_stage = stage
        self.last_updated = datetime.now(timezone.utc).isoformat()

    def mark_generation_failed(self, reason: str) -> None:
        self.generation_status = "failed"
        self.generation_failure_reason = reason
        self.update_stage("generation_failed")
        self.final_verdict = "EXAMPLE_BLOCKED_GENERATION_FAILED"

    def mark_generated(self) -> None:
        self.generation_status = "passed"
        self.update_stage("generated")

    def mark_build_failed(self, reason: str) -> None:
        self.build_status = "failed"
        self.build_failure_reason = reason
        self.update_stage("build_failed")
        self.final_verdict = "EXAMPLE_BLOCKED_BUILD_FAILED"

    def mark_build_passed(self) -> None:
        self.build_status = "passed"
        self.update_stage("build_passed")

    def mark_build_repaired(self, attempts: int) -> None:
        self.build_status = "repaired"
        self.build_repair_attempts = attempts
        self.update_stage("build_repaired")

    def mark_run_failed(self, reason: str, classification: str | None = None) -> None:
        self.run_status = "failed"
        self.run_failure_reason = reason
        self.run_failure_classification = classification
        self.update_stage("run_failed")
        self.final_verdict = "EXAMPLE_BLOCKED_RUN_FAILED"

    def mark_run_passed(self) -> None:
        self.run_status = "passed"
        self.update_stage("run_passed")

    def mark_run_repaired(self, attempts: int) -> None:
        self.run_status = "repaired"
        self.run_repair_attempts = attempts
        self.update_stage("run_repaired")

    def mark_reviewer_passed(self) -> None:
        self.reviewer_status = "passed"
        self.update_stage("reviewer_passed")
        self.final_verdict = "EXAMPLE_READY_FOR_PR_DRY_RUN"
        self.pr_candidate = True

    def mark_reviewer_failed(self, reason: str) -> None:
        self.reviewer_status = "failed"
        self.reviewer_failure_reason = reason
        self.pr_candidate = False  # reviewer failure revokes PR candidacy
        self.update_stage("reviewer_failed")
        self.final_verdict = "EXAMPLE_BLOCKED_REVIEWER_FAILED"

    def mark_reviewer_repaired(self, attempts: int) -> None:
        self.reviewer_status = "repaired"
        self.reviewer_repair_attempts = attempts
        self.update_stage("reviewer_repaired")
        self.final_verdict = "EXAMPLE_READY_FOR_PR_DRY_RUN"
        self.pr_candidate = True

    def mark_reviewer_unavailable(self) -> None:
        self.reviewer_status = "unavailable"
        self.update_stage("reviewer_attempted")

    def mark_pr_candidate(self) -> None:
        self.pr_candidate = True
        self.update_stage("pr_candidate")
        if self.final_verdict == "PENDING":
            self.final_verdict = "EXAMPLE_READY_FOR_PR_DRY_RUN"

    def mark_excluded(self, reason: str) -> None:
        self.pr_candidate = False
        self.excluded_reason = reason
        self.update_stage("excluded")

    def mark_backlogged(self, root_cause: str, recommended_fix: str, priority: str = "medium") -> None:
        self.backlogged = True
        self.backlog_root_cause = root_cause
        self.backlog_recommended_fix = recommended_fix
        self.backlog_priority = priority
        self.update_stage("backlogged")


# ---------------------------------------------------------------------------
# Registry: per-run lifecycle tracking
# ---------------------------------------------------------------------------

@dataclass
class ExampleLifecycleRegistry:
    """Collects all lifecycle records for a single pipeline run."""
    family: str
    run_id: str
    records: list[ExampleLifecycleRecord] = field(default_factory=list)

    def create_record(self, scenario_id: str) -> ExampleLifecycleRecord:
        """Create and register a new lifecycle record for a scenario."""
        record = ExampleLifecycleRecord(
            scenario_id=scenario_id,
            family=self.family,
            run_id=self.run_id,
        )
        self.records.append(record)
        return record

    def get_record(self, scenario_id: str) -> ExampleLifecycleRecord | None:
        """Find a record by scenario_id."""
        for r in self.records:
            if r.scenario_id == scenario_id:
                return r
        return None

    @property
    def total(self) -> int:
        return len(self.records)

    @property
    def generation_failed(self) -> list[ExampleLifecycleRecord]:
        return [r for r in self.records if r.generation_status == "failed"]

    @property
    def build_failed(self) -> list[ExampleLifecycleRecord]:
        return [r for r in self.records if r.build_status == "failed"]

    @property
    def run_failed(self) -> list[ExampleLifecycleRecord]:
        return [r for r in self.records if r.run_status == "failed"]

    @property
    def pr_candidates(self) -> list[ExampleLifecycleRecord]:
        return [r for r in self.records if r.pr_candidate]

    @property
    def backlogged_records(self) -> list[ExampleLifecycleRecord]:
        return [r for r in self.records if r.backlogged]

    @property
    def excluded_records(self) -> list[ExampleLifecycleRecord]:
        return [r for r in self.records if r.excluded_reason is not None]

    def summary(self) -> dict:
        """Summary statistics."""
        return {
            "total_planned": self.total,
            "generation_passed": sum(1 for r in self.records if r.generation_status == "passed"),
            "generation_failed": len(self.generation_failed),
            "build_passed": sum(1 for r in self.records if r.build_status in ("passed", "repaired")),
            "build_failed": len(self.build_failed),
            "run_passed": sum(1 for r in self.records if r.run_status in ("passed", "repaired")),
            "run_failed": len(self.run_failed),
            "reviewer_passed": sum(1 for r in self.records if r.reviewer_status == "passed"),
            "pr_candidates": len(self.pr_candidates),
            "excluded": len(self.excluded_records),
            "backlogged": len(self.backlogged_records),
        }


# ---------------------------------------------------------------------------
# Per-family backlog
# ---------------------------------------------------------------------------

@dataclass
class FamilyBacklogEntry:
    """A persistent backlog entry for a failed example across runs."""
    scenario_id: str
    family: str
    last_run_id: str
    last_failure_stage: str  # generation, build, run, reviewer
    root_cause: str
    recommended_fix: str
    priority: str = "medium"
    attempt_count: int = 1
    first_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved: bool = False
    resolved_in_run: str | None = None


def load_family_backlog(family: str, backlog_dir: Path) -> list[FamilyBacklogEntry]:
    """Load the persistent backlog for a family."""
    path = backlog_dir / f"{family}-example-backlog.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = []
        for item in data.get("entries", []):
            entries.append(FamilyBacklogEntry(**item))
        return entries
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.warning("Failed to load backlog for %s: %s", family, e)
        return []


def save_family_backlog(family: str, entries: list[FamilyBacklogEntry], backlog_dir: Path) -> Path:
    """Save the persistent backlog for a family."""
    path = backlog_dir / f"{family}-example-backlog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "family": family,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_entries": len(entries),
        "open_entries": sum(1 for e in entries if not e.resolved),
        "resolved_entries": sum(1 for e in entries if e.resolved),
        "entries": [asdict(e) for e in entries],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def update_backlog_from_lifecycle(
    registry: ExampleLifecycleRegistry,
    backlog_dir: Path,
) -> list[FamilyBacklogEntry]:
    """Update the persistent backlog from lifecycle records.

    - Failed examples get added or updated in the backlog.
    - Passing examples that were previously backlogged get resolved.

    Returns the updated backlog entries.
    """
    entries = load_family_backlog(registry.family, backlog_dir)
    existing_map = {e.scenario_id: e for e in entries}

    for record in registry.records:
        existing = existing_map.get(record.scenario_id)

        if record.pr_candidate:
            # Example passed — resolve any existing backlog entry
            if existing and not existing.resolved:
                existing.resolved = True
                existing.resolved_in_run = registry.run_id
                existing.last_seen = datetime.now(timezone.utc).isoformat()
        elif record.backlogged:
            # Example failed — add or update backlog entry
            if existing:
                existing.last_run_id = registry.run_id
                existing.last_failure_stage = record.current_stage
                existing.root_cause = record.backlog_root_cause or existing.root_cause
                existing.recommended_fix = record.backlog_recommended_fix or existing.recommended_fix
                existing.priority = record.backlog_priority
                existing.attempt_count += 1
                existing.last_seen = datetime.now(timezone.utc).isoformat()
            else:
                new_entry = FamilyBacklogEntry(
                    scenario_id=record.scenario_id,
                    family=registry.family,
                    last_run_id=registry.run_id,
                    last_failure_stage=record.current_stage,
                    root_cause=record.backlog_root_cause or "unknown",
                    recommended_fix=record.backlog_recommended_fix or "investigate",
                    priority=record.backlog_priority,
                )
                entries.append(new_entry)

    save_family_backlog(registry.family, entries, backlog_dir)
    return entries


# ---------------------------------------------------------------------------
# Evidence writer
# ---------------------------------------------------------------------------

def write_lifecycle_evidence(
    registry: ExampleLifecycleRegistry,
    evidence_dir: Path,
) -> Path:
    """Write lifecycle registry to evidence."""
    out = evidence_dir / "latest" / "example-lifecycle-records.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "family": registry.family,
        "run_id": registry.run_id,
        "summary": registry.summary(),
        "records": [asdict(r) for r in registry.records],
    }
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Run-to-run comparison
# ---------------------------------------------------------------------------

# State strength ordering: higher index = stronger state.
# A move from a higher-index state to a lower-index state is a regression.
STATE_STRENGTH: dict[str, int] = {
    "excluded": 0,
    "backlogged": 1,
    "generation_failed": 2,
    "planned": 3,
    "generation_attempted": 4,
    "generated": 5,
    "build_attempted": 6,
    "build_failed": 7,
    "build_repaired": 8,
    "build_passed": 9,
    "run_attempted": 10,
    "run_failed": 11,
    "run_repaired": 12,
    "run_passed": 13,
    "reviewer_attempted": 14,
    "reviewer_failed": 15,
    "reviewer_repaired": 16,
    "reviewer_passed": 17,
    "pr_candidate": 18,
}


def _state_strength(stage: str) -> int:
    """Return the strength of a lifecycle stage. Unknown stages get -1."""
    return STATE_STRENGTH.get(stage, -1)


@dataclass
class ScenarioComparisonResult:
    """Comparison result for a single scenario between two runs."""
    scenario_id: str
    prior_state: str
    current_state: str
    classification: str  # UNCHANGED, IMPROVED, REGRESSED, NEW_SCENARIO, MISSING_FROM_CURRENT
    regression_reason: str | None = None


@dataclass
class RunToRunComparisonResult:
    """Aggregate comparison between a current run and a prior run."""
    current_run_id: str
    prior_run_id: str
    family: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_prior_scenarios: int = 0
    total_current_scenarios: int = 0
    unchanged_count: int = 0
    improved_count: int = 0
    regressed_count: int = 0
    missing_from_current_count: int = 0
    new_scenario_count: int = 0
    regression_detected: bool = False
    per_scenario_results: list[dict] = field(default_factory=list)
    verdict: str = "RUN_TO_RUN_COMPARISON_NOT_REQUESTED"

    def to_dict(self) -> dict:
        return asdict(self)


def _load_prior_lifecycle(
    prior_run_id: str,
    family: str,
    repo_root: Path,
) -> list[dict] | None:
    """Load prior run lifecycle records. Returns list of record dicts or None."""
    # Try run-scoped evidence first
    run_path = (
        repo_root / "workspace" / "runs" / prior_run_id
        / "evidence" / "latest" / "example-lifecycle-records.json"
    )
    if run_path.exists():
        try:
            data = json.loads(run_path.read_text(encoding="utf-8"))
            return data.get("records", [])
        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse prior lifecycle at %s", run_path)

    # Try promoted family evidence
    family_path = (
        repo_root / "workspace" / "verification" / "latest"
        / "families" / family / "example-lifecycle-records.json"
    )
    if family_path.exists():
        try:
            data = json.loads(family_path.read_text(encoding="utf-8"))
            records = data.get("records", [])
            # Only use if it matches the prior_run_id (or if caller accepts any)
            if data.get("run_id") == prior_run_id or prior_run_id == "latest":
                return records
        except (json.JSONDecodeError, KeyError):
            logger.warning("Failed to parse family lifecycle at %s", family_path)

    return None


def compare_with_prior_run(
    registry: ExampleLifecycleRegistry,
    prior_run_id: str,
    repo_root: Path,
) -> RunToRunComparisonResult:
    """Compare current lifecycle records against a prior run.

    Returns a RunToRunComparisonResult with per-scenario classifications
    and an aggregate verdict.
    """
    result = RunToRunComparisonResult(
        current_run_id=registry.run_id,
        prior_run_id=prior_run_id,
        family=registry.family,
    )

    prior_records = _load_prior_lifecycle(prior_run_id, registry.family, repo_root)
    if prior_records is None:
        result.verdict = "RUN_TO_RUN_COMPARISON_BLOCKED_PRIOR_RUN_NOT_FOUND"
        logger.error(
            "Prior run '%s' lifecycle not found for family '%s'",
            prior_run_id, registry.family,
        )
        return result

    # Build prior map
    prior_map: dict[str, dict] = {}
    for rec in prior_records:
        sid = rec.get("scenario_id")
        if sid:
            prior_map[sid] = rec

    result.total_prior_scenarios = len(prior_map)
    result.total_current_scenarios = len(registry.records)

    current_ids: set[str] = set()

    for record in registry.records:
        current_ids.add(record.scenario_id)
        prior = prior_map.get(record.scenario_id)

        if prior is None:
            # New scenario not in prior run
            scenario_result = ScenarioComparisonResult(
                scenario_id=record.scenario_id,
                prior_state="(absent)",
                current_state=record.current_stage,
                classification="NEW_SCENARIO",
            )
            result.new_scenario_count += 1
            record.prior_run_id = prior_run_id
            record.prior_state = None
            record.prior_run_result = "NEW_SCENARIO"
        else:
            prior_stage = prior.get("current_stage", "planned")
            prior_strength = _state_strength(prior_stage)
            current_strength = _state_strength(record.current_stage)

            record.prior_run_id = prior_run_id
            record.prior_state = prior_stage

            if current_strength == prior_strength:
                classification = "UNCHANGED"
                result.unchanged_count += 1
                record.prior_run_result = "UNCHANGED"
            elif current_strength > prior_strength:
                classification = "IMPROVED"
                result.improved_count += 1
                record.prior_run_result = "IMPROVED"
            else:
                classification = "REGRESSED"
                reason = (
                    f"State weakened: {prior_stage} (strength {prior_strength}) "
                    f"-> {record.current_stage} (strength {current_strength})"
                )
                result.regressed_count += 1
                result.regression_detected = True
                record.prior_run_result = "REGRESSED"
                record.regression_detected = True
                record.regression_reason = reason

            scenario_result = ScenarioComparisonResult(
                scenario_id=record.scenario_id,
                prior_state=prior_stage,
                current_state=record.current_stage,
                classification=classification,
                regression_reason=reason if classification == "REGRESSED" else None,
            )

        result.per_scenario_results.append(asdict(scenario_result))

    # Check for scenarios in prior but missing from current
    for sid, prior_rec in prior_map.items():
        if sid not in current_ids:
            prior_stage = prior_rec.get("current_stage", "planned")
            # Missing from current is a regression if the prior state was substantive
            is_regression = _state_strength(prior_stage) > _state_strength("planned")
            scenario_result = ScenarioComparisonResult(
                scenario_id=sid,
                prior_state=prior_stage,
                current_state="(missing)",
                classification="MISSING_FROM_CURRENT",
                regression_reason=(
                    f"Scenario present in prior run at stage '{prior_stage}' "
                    f"but absent from current run"
                ) if is_regression else None,
            )
            result.missing_from_current_count += 1
            if is_regression:
                result.regressed_count += 1
                result.regression_detected = True
            result.per_scenario_results.append(asdict(scenario_result))

    # Determine verdict
    if result.regression_detected:
        result.verdict = "RUN_TO_RUN_COMPARISON_REGRESSION_DETECTED"
    elif result.improved_count > 0:
        result.verdict = "RUN_TO_RUN_COMPARISON_PASS_WITH_IMPROVEMENTS"
    else:
        result.verdict = "RUN_TO_RUN_COMPARISON_PASS"

    return result


def write_comparison_evidence(
    comparison: RunToRunComparisonResult,
    evidence_dir: Path,
) -> Path:
    """Write run-to-run comparison result to evidence."""
    out = evidence_dir / "latest" / "run-to-run-comparison.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(comparison.to_dict(), indent=2), encoding="utf-8")
    return out
