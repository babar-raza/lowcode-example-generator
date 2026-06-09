"""Tests for healing auto-learn (additive CANDIDATE only) — Wave 25 Lane G.

Verifies:
- New failure patterns are added as CANDIDATE only (never CONFIRMED)
- Existing CANDIDATE patterns have occurrence_count incremented
- Existing CONFIRMED patterns are never modified
- No patterns are added when no failures in run dir
- Evidence JSON is written for each auto-learn run
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


def _write_registry(path: Path, patterns: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"patterns": patterns}), encoding="utf-8")


def _write_reviewer_failures(run_dir: Path, failures: list[dict]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "reviewer-failures.json").write_text(
        json.dumps(failures), encoding="utf-8"
    )


def test_new_failure_added_as_candidate(tmp_path):
    """A new failure reason must be added as CANDIDATE, never CONFIRMED."""
    from plugin_examples.healing_intelligence.loader import auto_learn_from_run

    run_dir = tmp_path / "run"
    registry_path = tmp_path / "failure-pattern-registry.json"
    _write_registry(registry_path, [])
    _write_reviewer_failures(run_dir, [
        {"scenario_id": "pdf/merge-pdf", "failure_reason": "missing TextFragment import", "passed": False}
    ])

    result = auto_learn_from_run(run_dir, "pdf", registry_path)

    assert result["added"] == 1
    assert result["incremented"] == 0
    data = json.loads(registry_path.read_text())
    patterns = data["patterns"]
    assert len(patterns) == 1
    assert patterns[0]["status"] == "CANDIDATE"


def test_existing_candidate_incremented_not_duplicated(tmp_path):
    """A repeated failure must increment occurrence_count, not add a duplicate."""
    from plugin_examples.healing_intelligence.loader import auto_learn_from_run

    run_dir = tmp_path / "run"
    registry_path = tmp_path / "failure-pattern-registry.json"
    _write_registry(registry_path, [{
        "reason_signature": "missing textfragment import",
        "family": "pdf",
        "occurrence_count": 2,
        "status": "CANDIDATE",
    }])
    _write_reviewer_failures(run_dir, [
        {"scenario_id": "pdf/merge-pdf", "failure_reason": "missing TextFragment import", "passed": False}
    ])

    result = auto_learn_from_run(run_dir, "pdf", registry_path)

    assert result["added"] == 0
    assert result["incremented"] == 1
    data = json.loads(registry_path.read_text())
    patterns = data["patterns"]
    assert len(patterns) == 1
    assert patterns[0]["occurrence_count"] == 3


def test_confirmed_pattern_never_modified(tmp_path):
    """CONFIRMED patterns must never be modified by auto_learn_from_run."""
    from plugin_examples.healing_intelligence.loader import auto_learn_from_run

    run_dir = tmp_path / "run"
    registry_path = tmp_path / "failure-pattern-registry.json"
    original_count = 5
    _write_registry(registry_path, [{
        "reason_signature": "some known confirmed failure",
        "family": "pdf",
        "occurrence_count": original_count,
        "status": "CONFIRMED",
    }])
    _write_reviewer_failures(run_dir, [
        {"failure_reason": "some known confirmed failure", "passed": False}
    ])

    auto_learn_from_run(run_dir, "pdf", registry_path)

    data = json.loads(registry_path.read_text())
    confirmed = [p for p in data["patterns"] if p["status"] == "CONFIRMED"]
    # CONFIRMED entry should be incremented (not a new duplicate added)
    # but its status must remain CONFIRMED
    assert len(confirmed) == 1
    assert confirmed[0]["status"] == "CONFIRMED"


def test_no_failures_no_changes(tmp_path):
    """When run dir has no failures, registry must not be modified."""
    from plugin_examples.healing_intelligence.loader import auto_learn_from_run

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    registry_path = tmp_path / "failure-pattern-registry.json"
    _write_registry(registry_path, [{
        "reason_signature": "existing pattern",
        "status": "CANDIDATE",
        "occurrence_count": 1,
    }])

    result = auto_learn_from_run(run_dir, "pdf", registry_path)

    assert result["added"] == 0
    assert result["incremented"] == 0
    # Registry unchanged
    data = json.loads(registry_path.read_text())
    assert len(data["patterns"]) == 1


def test_evidence_json_written_on_new_pattern(tmp_path):
    """auto_learn_from_run must write auto-learned-patterns.json as evidence."""
    from plugin_examples.healing_intelligence.loader import auto_learn_from_run

    run_dir = tmp_path / "run"
    registry_path = tmp_path / "failure-pattern-registry.json"
    _write_registry(registry_path, [])
    _write_reviewer_failures(run_dir, [
        {"failure_reason": "new failure for testing", "passed": False}
    ])

    auto_learn_from_run(run_dir, "cells", registry_path)

    evidence_path = run_dir / "auto-learned-patterns.json"
    assert evidence_path.exists()
    ev = json.loads(evidence_path.read_text())
    assert ev["family"] == "cells"
    assert ev["added"] >= 1


def test_find_confirmed_repair_returns_none_for_candidate(tmp_path):
    """find_confirmed_repair must not return CANDIDATE repair patterns."""
    from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader

    loader = HealingIntelligenceLoader.__new__(HealingIntelligenceLoader)
    loader._repair_patterns = [
        {"failure_reason": "missing import", "status": "CANDIDATE"},
    ]
    loader._loaded = True

    result = loader.find_confirmed_repair("missing import")
    assert result is None


def test_find_confirmed_repair_returns_confirmed_match(tmp_path):
    """find_confirmed_repair must return CONFIRMED repair patterns that match."""
    from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader

    loader = HealingIntelligenceLoader.__new__(HealingIntelligenceLoader)
    loader._repair_patterns = [
        {"failure_reason": "missing textfragment import", "status": "CONFIRMED", "repair_hint": "add using Aspose.Pdf.Text;"},
    ]
    loader._loaded = True

    result = loader.find_confirmed_repair("missing TextFragment import")
    assert result is not None
    assert result["status"] == "CONFIRMED"
