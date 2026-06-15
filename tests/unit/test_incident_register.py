"""Tests for compliance/incident_register.py — TC-RH07."""

from __future__ import annotations

import json
from pathlib import Path

from plugin_examples.compliance.incident_register import (
    IncidentEntry,
    validate_incident_entry,
    validate_incident_register,
)

VALID_ENTRY = {
    "id": "INC-001",
    "severity": "HIGH",
    "timestamp": "2026-06-15T10:00:00Z",
    "title": "NuGet fetch timeout",
    "root_cause": "DNS resolution failure",
    "resolution": "Added retry logic with exponential backoff",
    "duration_minutes": 45,
    "affected_families": ["cells", "pdf"],
    "regression_test_added": True,
    "post_mortem_url": "",
}


class TestValidateIncidentEntry:
    def test_valid_entry(self):
        errors = validate_incident_entry(VALID_ENTRY)
        assert errors == []

    def test_missing_required_field(self):
        entry = dict(VALID_ENTRY)
        del entry["root_cause"]
        errors = validate_incident_entry(entry)
        assert len(errors) > 0
        assert any("root_cause" in e for e in errors)

    def test_invalid_severity(self):
        entry = {**VALID_ENTRY, "severity": "EXTREME"}
        errors = validate_incident_entry(entry)
        assert len(errors) > 0

    def test_invalid_id_pattern(self):
        entry = {**VALID_ENTRY, "id": "bad-id"}
        errors = validate_incident_entry(entry)
        assert len(errors) > 0

    def test_empty_title_rejected(self):
        entry = {**VALID_ENTRY, "title": ""}
        errors = validate_incident_entry(entry)
        assert len(errors) > 0

    def test_additional_properties_rejected(self):
        entry = {**VALID_ENTRY, "extra_field": "value"}
        errors = validate_incident_entry(entry)
        assert len(errors) > 0


class TestValidateIncidentRegister:
    def test_valid_register(self, tmp_path: Path):
        path = tmp_path / "register.json"
        path.write_text(json.dumps({"incidents": [VALID_ENTRY]}))
        total, valid, errors = validate_incident_register(path)
        assert total == 1
        assert valid == 1
        assert errors == []

    def test_missing_file(self, tmp_path: Path):
        total, valid, errors = validate_incident_register(tmp_path / "missing.json")
        assert total == 0
        assert "not found" in errors[0]

    def test_invalid_json(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text("{invalid json")
        total, valid, errors = validate_incident_register(path)
        assert total == 0
        assert len(errors) > 0

    def test_mixed_entries(self, tmp_path: Path):
        bad_entry = {"id": "bad", "severity": "LOW"}
        path = tmp_path / "register.json"
        path.write_text(json.dumps({"incidents": [VALID_ENTRY, bad_entry]}))
        total, valid, errors = validate_incident_register(path)
        assert total == 2
        assert valid == 1
        assert len(errors) > 0

    def test_list_format(self, tmp_path: Path):
        path = tmp_path / "register.json"
        path.write_text(json.dumps([VALID_ENTRY]))
        total, valid, errors = validate_incident_register(path)
        assert total == 1
        assert valid == 1


class TestIncidentEntry:
    def test_to_dict(self):
        entry = IncidentEntry(
            id="INC-001", severity="HIGH", timestamp="2026-06-15",
            title="Test", root_cause="Bug", resolution="Fix",
        )
        d = entry.to_dict()
        assert d["id"] == "INC-001"
        assert d["severity"] == "HIGH"
        assert d["affected_families"] == []
        assert d["regression_test_added"] is False
