"""Cross-run state persistence — tracks run outcomes for adaptive planning.

Stores a rolling history of pipeline run results so the planner loop can
deprioritize scenarios with repeated failures and adapt retry behavior.

Usage:
    from plugin_examples.state.run_history import RunHistory

    history = RunHistory.load(Path(".local/run-history.json"))
    history.record_run(RunRecord(family="cells", wave="26", ...))
    history.save()
    failures = history.recent_failures("cells", window=5)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RunRecord:
    """Single pipeline run outcome."""

    family: str
    wave: str
    timestamp: str = ""
    verdict: str = ""
    test_count: int = 0
    error_types: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    scenarios_attempted: int = 0
    scenarios_succeeded: int = 0
    scenarios_blocked: int = 0

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunRecord:
        return cls(
            family=data.get("family", ""),
            wave=data.get("wave", ""),
            timestamp=data.get("timestamp", ""),
            verdict=data.get("verdict", ""),
            test_count=data.get("test_count", 0),
            error_types=data.get("error_types", []),
            duration_seconds=data.get("duration_seconds", 0.0),
            scenarios_attempted=data.get("scenarios_attempted", 0),
            scenarios_succeeded=data.get("scenarios_succeeded", 0),
            scenarios_blocked=data.get("scenarios_blocked", 0),
        )


class RunHistory:
    """Persistent cross-run history with adaptive query support."""

    MAX_RECORDS = 500  # Rolling cap to prevent unbounded growth

    def __init__(self, path: Path, records: list[RunRecord] | None = None) -> None:
        self._path = path
        self._records: list[RunRecord] = records or []

    @classmethod
    def load(cls, path: Path) -> RunHistory:
        """Load history from JSON file. Returns empty history if file missing."""
        records: list[RunRecord] = []
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for entry in data.get("runs", []):
                    records.append(RunRecord.from_dict(entry))
            except (json.JSONDecodeError, KeyError, TypeError):
                pass  # Corrupted file — start fresh
        return cls(path, records)

    def save(self) -> None:
        """Persist history to JSON, enforcing rolling cap."""
        # Trim oldest records if over cap
        if len(self._records) > self.MAX_RECORDS:
            self._records = self._records[-self.MAX_RECORDS:]
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "updated_at": datetime.now(UTC).isoformat(),
            "record_count": len(self._records),
            "runs": [r.to_dict() for r in self._records],
        }
        self._path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def record_run(self, record: RunRecord) -> None:
        """Append a run record."""
        self._records.append(record)

    @property
    def records(self) -> list[RunRecord]:
        return list(self._records)

    def recent_failures(self, family: str, window: int = 5) -> list[RunRecord]:
        """Return recent failed runs for a family within the last *window* runs."""
        family_runs = [r for r in self._records if r.family == family]
        recent = family_runs[-window:] if family_runs else []
        return [r for r in recent if r.verdict not in ("PASS", "SPRINT_COMPLETE", "BUILD_PASS")]

    def consecutive_failure_count(self, family: str) -> int:
        """Count consecutive recent failures for a family (from most recent)."""
        family_runs = [r for r in self._records if r.family == family]
        count = 0
        for r in reversed(family_runs):
            if r.verdict in ("PASS", "SPRINT_COMPLETE", "BUILD_PASS"):
                break
            count += 1
        return count

    def failure_rate(self, family: str, window: int = 10) -> float:
        """Compute failure rate for a family over last *window* runs."""
        family_runs = [r for r in self._records if r.family == family]
        recent = family_runs[-window:] if family_runs else []
        if not recent:
            return 0.0
        failures = sum(
            1 for r in recent
            if r.verdict not in ("PASS", "SPRINT_COMPLETE", "BUILD_PASS")
        )
        return failures / len(recent)

    def should_deprioritize(self, family: str, threshold: int = 3) -> bool:
        """Return True if family has >= threshold consecutive failures."""
        return self.consecutive_failure_count(family) >= threshold

    def common_error_types(self, family: str, window: int = 10) -> dict[str, int]:
        """Return error type frequency for a family over recent runs."""
        family_runs = [r for r in self._records if r.family == family]
        recent = family_runs[-window:] if family_runs else []
        counts: dict[str, int] = {}
        for r in recent:
            for err in r.error_types:
                counts[err] = counts.get(err, 0) + 1
        return counts
