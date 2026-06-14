"""Tests for plugin_examples.compliance.audit_trail."""

from __future__ import annotations

from pathlib import Path

from plugin_examples.compliance.audit_trail import AuditEntry, AuditTrail


class TestAuditEntry:
    def test_auto_timestamp(self) -> None:
        entry = AuditEntry(action_id="test", decision="EXECUTE")
        assert entry.timestamp  # auto-populated

    def test_to_dict(self) -> None:
        entry = AuditEntry(
            action_id="CONSERVATION_CHECK",
            decision="EXECUTE",
            policy_rule="gates.yml:approval_gated_types",
            goal_relevance=["build_pass_rate"],
            evidence_ref="handler-conservation-cycle01.json",
        )
        d = entry.to_dict()
        assert d["action_id"] == "CONSERVATION_CHECK"
        assert d["decision"] == "EXECUTE"
        assert d["policy_rule"] == "gates.yml:approval_gated_types"
        assert "build_pass_rate" in d["goal_relevance"]


class TestAuditTrail:
    def test_record_and_entries(self) -> None:
        trail = AuditTrail()
        trail.record(AuditEntry(action_id="a1", decision="EXECUTE"))
        trail.record(AuditEntry(action_id="a2", decision="DEFER"))
        assert len(trail.entries) == 2
        assert trail.entries[0].action_id == "a1"

    def test_to_json(self) -> None:
        trail = AuditTrail()
        trail.record(AuditEntry(action_id="a1", decision="BLOCK"))
        j = trail.to_json()
        assert '"audit_trail"' in j
        assert '"BLOCK"' in j

    def test_save_and_load(self, tmp_path: Path) -> None:
        path = tmp_path / "audit.json"
        trail = AuditTrail()
        trail.record(AuditEntry(
            action_id="a1",
            decision="EXECUTE",
            policy_rule="gates.yml:hard_stop_stages",
            goal_relevance=["evidence_completeness"],
        ))
        trail.save(path)
        assert path.exists()

        loaded = AuditTrail.load(path)
        assert len(loaded.entries) == 1
        assert loaded.entries[0].action_id == "a1"
        assert loaded.entries[0].policy_rule == "gates.yml:hard_stop_stages"

    def test_load_missing_file(self, tmp_path: Path) -> None:
        trail = AuditTrail.load(tmp_path / "nonexistent.json")
        assert len(trail.entries) == 0

    def test_load_corrupt_file(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("{{invalid json", encoding="utf-8")
        trail = AuditTrail.load(path)
        assert len(trail.entries) == 0

    def test_entries_returns_copy(self) -> None:
        trail = AuditTrail()
        trail.record(AuditEntry(action_id="a1", decision="EXECUTE"))
        entries = trail.entries
        entries.clear()
        assert len(trail.entries) == 1  # original unaffected
