"""Tests for registry promoter (TC-PSAL-25)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from plugin_examples.probe_executor.promoter import (
    _FAILURE_NEXT_ACTION,
    promote_entry,
    promote_family,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _write_registry(path: Path, entries: list[dict]) -> Path:
    """Write a test registry YAML and return its path."""
    registry_dir = path / "pipeline" / "plugin-capability-registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_path = registry_dir / "drawing.yaml"
    registry_path.write_text(yaml.dump({"entries": entries}), encoding="utf-8")
    return registry_path


def _make_entry(slug="convert-drawing", status="REFLECTION_CANDIDATE", confidence=0.70):
    return {
        "family": "drawing",
        "plugin_slug": slug,
        "status": status,
        "confidence_score": confidence,
        "probe_evidence": None,
        "failure_taxonomy": None,
        "next_action": "PROBE_CANDIDATE_PENDING_PROBE",
        "blocker_type": None,
        "bootstrap_status": status,
    }


# ---------------------------------------------------------------------------
# Tests: promote_entry
# ---------------------------------------------------------------------------

class TestPromoteEntry:
    def test_confirmed_updates_fields(self, tmp_path):
        _write_registry(tmp_path, [_make_entry()])
        result = promote_entry(
            family="drawing",
            plugin_slug="convert-drawing",
            new_status="PROBE_CONFIRMED",
            probe_evidence_path="/evidence/probe.json",
            failure_taxonomy=None,
            repo_root=tmp_path,
        )
        assert result["status"] == "PROBE_CONFIRMED"
        assert result["probe_evidence"] == "/evidence/probe.json"
        assert result["confidence_score"] == pytest.approx(0.90)  # 0.70 + 0.20
        assert result["next_action"] == "READY_FOR_EXAMPLE_GENERATION"
        assert result["blocker_type"] is None
        assert result["failure_taxonomy"] is None
        assert result["bootstrap_status"] == "PROBE_CONFIRMED"

    def test_confirmed_caps_confidence_at_095(self, tmp_path):
        _write_registry(tmp_path, [_make_entry(confidence=0.85)])
        result = promote_entry(
            family="drawing",
            plugin_slug="convert-drawing",
            new_status="PROBE_CONFIRMED",
            probe_evidence_path="/evidence/probe.json",
            failure_taxonomy=None,
            repo_root=tmp_path,
        )
        assert result["confidence_score"] == 0.95  # min(0.95, 0.85 + 0.20)

    def test_failed_build_updates_fields(self, tmp_path):
        _write_registry(tmp_path, [_make_entry()])
        result = promote_entry(
            family="drawing",
            plugin_slug="convert-drawing",
            new_status="PROBE_FAILED_BUILD",
            probe_evidence_path="/evidence/probe.json",
            failure_taxonomy="PROBE_FAILED_BUILD",
            repo_root=tmp_path,
        )
        assert result["status"] == "PROBE_FAILED"
        assert result["failure_taxonomy"] == "PROBE_FAILED_BUILD"
        assert result["next_action"] == "NEEDS_API_MAPPING_FIX"

    def test_failed_license(self, tmp_path):
        _write_registry(tmp_path, [_make_entry()])
        result = promote_entry(
            family="drawing",
            plugin_slug="convert-drawing",
            new_status="PROBE_FAILED_LICENSE",
            probe_evidence_path="/evidence/probe.json",
            failure_taxonomy="PROBE_FAILED_LICENSE",
            repo_root=tmp_path,
        )
        assert result["next_action"] == "BLOCKED_LICENSE_RESTRICTED"

    def test_entry_not_found_raises(self, tmp_path):
        _write_registry(tmp_path, [_make_entry(slug="other-slug")])
        with pytest.raises(ValueError, match="not found"):
            promote_entry(
                family="drawing",
                plugin_slug="nonexistent",
                new_status="PROBE_CONFIRMED",
                probe_evidence_path="",
                failure_taxonomy=None,
                repo_root=tmp_path,
            )

    def test_registry_not_found_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Registry file not found"):
            promote_entry(
                family="drawing",
                plugin_slug="convert-drawing",
                new_status="PROBE_CONFIRMED",
                probe_evidence_path="",
                failure_taxonomy=None,
                repo_root=tmp_path,
            )

    def test_other_entries_not_modified(self, tmp_path):
        entries = [_make_entry(slug="convert-drawing"), _make_entry(slug="create-drawing")]
        _write_registry(tmp_path, entries)
        promote_entry(
            family="drawing",
            plugin_slug="convert-drawing",
            new_status="PROBE_CONFIRMED",
            probe_evidence_path="/evidence/probe.json",
            failure_taxonomy=None,
            repo_root=tmp_path,
        )

        # Re-read and check other entry is untouched
        registry_path = tmp_path / "pipeline" / "plugin-capability-registry" / "drawing.yaml"
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        other = next(e for e in data["entries"] if e["plugin_slug"] == "create-drawing")
        assert other["status"] == "REFLECTION_CANDIDATE"
        assert other["probe_evidence"] is None

    def test_yaml_roundtrip_preserves_structure(self, tmp_path):
        entries = [_make_entry()]
        _write_registry(tmp_path, entries)
        promote_entry(
            family="drawing",
            plugin_slug="convert-drawing",
            new_status="PROBE_CONFIRMED",
            probe_evidence_path="/evidence/probe.json",
            failure_taxonomy=None,
            repo_root=tmp_path,
        )

        # Verify YAML is valid
        registry_path = tmp_path / "pipeline" / "plugin-capability-registry" / "drawing.yaml"
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        assert "entries" in data
        assert len(data["entries"]) == 1


# ---------------------------------------------------------------------------
# Tests: promote_family
# ---------------------------------------------------------------------------

class TestPromoteFamily:
    def test_promotes_all_outcomes(self, tmp_path):
        entries = [_make_entry(slug="a"), _make_entry(slug="b")]
        _write_registry(tmp_path, entries)

        outcome_a = MagicMock(
            plugin_slug="a", new_status="PROBE_CONFIRMED",
            probe_evidence_path="/ev/a.json",
            probe_result=None, error=None,
        )
        outcome_b = MagicMock(
            plugin_slug="b", new_status="PROBE_FAILED_BUILD",
            probe_evidence_path="/ev/b.json",
            probe_result=MagicMock(failure_taxonomy="PROBE_FAILED_BUILD"),
            error=None,
        )

        summary = promote_family("drawing", [outcome_a, outcome_b], tmp_path)
        assert summary["promoted"] == 1
        assert summary["failed"] == 1
        assert summary["total"] == 2


class TestFailureNextActionMapping:
    def test_all_taxonomies_mapped(self):
        expected = {"PROBE_FAILED_BUILD", "PROBE_FAILED_API", "PROBE_FAILED_LICENSE",
                    "PROBE_FAILED_RESTORE", "PROBE_FAILED_TIMEOUT"}
        assert set(_FAILURE_NEXT_ACTION.keys()) == expected
