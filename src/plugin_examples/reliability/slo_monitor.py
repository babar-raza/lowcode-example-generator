"""Service Level Objective (SLO) monitoring.

Evaluates SLO definitions against historical run data and current loop
metrics, producing structured compliance results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SLOCheckResult:
    """Result of evaluating a single SLO."""

    slo_id: str
    metric: str
    target: float
    actual: float
    passed: bool
    severity: str
    window_runs: int
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "slo_id": self.slo_id,
            "metric": self.metric,
            "target": self.target,
            "actual": round(self.actual, 4),
            "passed": self.passed,
            "severity": self.severity,
            "window_runs": self.window_runs,
            "detail": self.detail,
        }


def _compute_metric(
    metric: str,
    history_records: list[Any],
    window: int,
    current_metrics: Any | None,
) -> float | None:
    """Compute a metric value from history records within the window.

    Returns None if the metric cannot be computed (insufficient data).
    """
    recent = history_records[-window:] if history_records else []

    if metric == "build_pass_rate":
        if not recent:
            return None
        total_attempted = sum(getattr(r, "scenarios_attempted", 0) for r in recent)
        total_succeeded = sum(getattr(r, "scenarios_succeeded", 0) for r in recent)
        return total_succeeded / total_attempted if total_attempted > 0 else 1.0

    if metric == "run_pass_rate":
        if not recent:
            return None
        success_verdicts = {"PASS", "SPRINT_COMPLETE", "BUILD_PASS"}
        successes = sum(1 for r in recent if getattr(r, "verdict", "") in success_verdicts)
        return successes / len(recent)

    if metric == "handler_error_rate":
        if current_metrics is not None:
            executed = getattr(current_metrics, "actions_executed", 0)
            errors = getattr(current_metrics, "handler_errors", 0)
            total = executed + errors
            return errors / total if total > 0 else 0.0
        return None

    if metric == "avg_cycle_duration_ms":
        if current_metrics is not None:
            total_ms = getattr(current_metrics, "total_duration_ms", 0)
            cycles = getattr(current_metrics, "total_cycles", 0)
            return total_ms / cycles if cycles > 0 else 0.0
        return None

    return None


def check_slos(
    slo_definitions: list[Any],
    history: Any | None,
    current_metrics: Any | None = None,
) -> list[SLOCheckResult]:
    """Evaluate all SLO definitions against historical + current metrics.

    Args:
        slo_definitions: List of SLODefinition instances.
        history: RunHistory instance (or None if unavailable).
        current_metrics: LoopMetrics from the current run (or None).

    Returns:
        List of SLOCheckResult for each definition.
    """
    records = getattr(history, "records", []) if history is not None else []
    results: list[SLOCheckResult] = []

    for slo in slo_definitions:
        slo_id = getattr(slo, "id", "")
        metric = getattr(slo, "metric", "")
        target = getattr(slo, "target", 0.0)
        window = getattr(slo, "window_runs", 10)
        severity = getattr(slo, "severity", "warning")

        actual = _compute_metric(metric, records, window, current_metrics)

        if actual is None:
            results.append(SLOCheckResult(
                slo_id=slo_id,
                metric=metric,
                target=target,
                actual=0.0,
                passed=True,
                severity=severity,
                window_runs=window,
                detail="insufficient data to evaluate",
            ))
            continue

        passed = actual <= target if "error" in metric or "duration" in metric else actual >= target

        results.append(SLOCheckResult(
            slo_id=slo_id,
            metric=metric,
            target=target,
            actual=actual,
            passed=passed,
            severity=severity,
            window_runs=window,
            detail=f"{'MET' if passed else 'VIOLATED'}: {actual:.4f} vs target {target}",
        ))

    return results


def slo_summary(results: list[SLOCheckResult]) -> dict[str, Any]:
    """Return aggregated SLO compliance summary."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    critical_failures = sum(1 for r in results if not r.passed and r.severity == "critical")
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "critical_failures": critical_failures,
        "all_passed": failed == 0,
        "results": [r.to_dict() for r in results],
    }
