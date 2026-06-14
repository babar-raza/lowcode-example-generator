"""Tests for evidence chain validators (ECV-01..04)."""

import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from plugin_examples.fixture_factory.evidence_chain_validators import (
    run_all_ecv_validators,
    validate_ecv01_non_null_evidence_paths,
    validate_ecv02_evidence_files_exist,
    validate_ecv03_timestamps_within_window,
    validate_ecv04_gate_evidence_consistency,
)


@pytest.fixture
def evidence_dir(tmp_path: Path) -> Path:
    d = tmp_path / "evidence"
    d.mkdir()
    return d


class TestECV01:
    def test_pass_with_valid_path(self):
        gates = [{"gate_id": "G1", "evidence_path": "evidence/g1.json"}]
        results = validate_ecv01_non_null_evidence_paths(gates)
        assert all(r.passed for r in results)

    def test_fail_null_path(self):
        gates = [{"gate_id": "G1", "evidence_path": None}]
        results = validate_ecv01_non_null_evidence_paths(gates)
        assert not results[0].passed
        assert "null" in results[0].message

    def test_fail_empty_path(self):
        gates = [{"gate_id": "G2", "evidence_path": ""}]
        results = validate_ecv01_non_null_evidence_paths(gates)
        assert not results[0].passed

    def test_mixed(self):
        gates = [
            {"gate_id": "G1", "evidence_path": "a.json"},
            {"gate_id": "G2", "evidence_path": None},
            {"gate_id": "G3", "evidence_path": "c.json"},
        ]
        results = validate_ecv01_non_null_evidence_paths(gates)
        assert results[0].passed
        assert not results[1].passed
        assert results[2].passed


class TestECV02:
    def test_pass_file_exists(self, evidence_dir: Path):
        (evidence_dir / "g1.json").write_text("{}", encoding="utf-8")
        gates = [{"gate_id": "G1", "evidence_path": "g1.json"}]
        results = validate_ecv02_evidence_files_exist(gates, evidence_dir)
        assert all(r.passed for r in results)

    def test_fail_file_missing(self, evidence_dir: Path):
        gates = [{"gate_id": "G1", "evidence_path": "missing.json"}]
        results = validate_ecv02_evidence_files_exist(gates, evidence_dir)
        assert not results[0].passed
        assert "missing" in results[0].message.lower()

    def test_skip_null_path(self, evidence_dir: Path):
        gates = [{"gate_id": "G1", "evidence_path": None}]
        results = validate_ecv02_evidence_files_exist(gates, evidence_dir)
        assert results == []  # skipped, ECV-01 handles this


class TestECV03:
    def test_pass_recent_timestamp(self):
        now = datetime.now(UTC).isoformat()
        gates = [{"gate_id": "G1", "timestamp": now}]
        results = validate_ecv03_timestamps_within_window(gates, max_age_hours=1.0)
        assert results[0].passed

    def test_fail_stale_timestamp(self):
        old = (datetime.now(UTC) - timedelta(hours=100)).isoformat()
        gates = [{"gate_id": "G1", "timestamp": old}]
        results = validate_ecv03_timestamps_within_window(gates, max_age_hours=72.0)
        assert not results[0].passed

    def test_fail_no_timestamp(self):
        gates = [{"gate_id": "G1"}]
        results = validate_ecv03_timestamps_within_window(gates)
        assert not results[0].passed

    def test_pass_within_run_window(self):
        start = "2026-06-10T00:00:00+00:00"
        end = "2026-06-10T23:59:59+00:00"
        gates = [{"gate_id": "G1", "timestamp": "2026-06-10T12:00:00+00:00"}]
        results = validate_ecv03_timestamps_within_window(gates, run_start=start, run_end=end)
        assert results[0].passed

    def test_fail_outside_run_window(self):
        start = "2026-06-10T00:00:00+00:00"
        end = "2026-06-10T23:59:59+00:00"
        gates = [{"gate_id": "G1", "timestamp": "2026-06-09T12:00:00+00:00"}]
        results = validate_ecv03_timestamps_within_window(gates, run_start=start, run_end=end)
        assert not results[0].passed


class TestECV04:
    def test_pass_consistent_verdict(self, evidence_dir: Path):
        evidence = {"verdict": "PASS", "family": "cells"}
        (evidence_dir / "g1.json").write_text(json.dumps(evidence), encoding="utf-8")
        gates = [{"gate_id": "G1", "evidence_path": "g1.json", "verdict": "PASS", "family": "cells"}]
        results = validate_ecv04_gate_evidence_consistency(gates, evidence_dir)
        assert all(r.passed for r in results)

    def test_fail_inconsistent_verdict(self, evidence_dir: Path):
        evidence = {"verdict": "FAIL", "family": "cells"}
        (evidence_dir / "g1.json").write_text(json.dumps(evidence), encoding="utf-8")
        gates = [{"gate_id": "G1", "evidence_path": "g1.json", "verdict": "PASS"}]
        results = validate_ecv04_gate_evidence_consistency(gates, evidence_dir)
        assert any(not r.passed for r in results)

    def test_fail_inconsistent_family(self, evidence_dir: Path):
        evidence = {"verdict": "PASS", "family": "pdf"}
        (evidence_dir / "g1.json").write_text(json.dumps(evidence), encoding="utf-8")
        gates = [{"gate_id": "G1", "evidence_path": "g1.json", "verdict": "PASS", "family": "cells"}]
        results = validate_ecv04_gate_evidence_consistency(gates, evidence_dir)
        assert any(not r.passed for r in results)

    def test_invalid_json_evidence(self, evidence_dir: Path):
        (evidence_dir / "bad.json").write_text("not json", encoding="utf-8")
        gates = [{"gate_id": "G1", "evidence_path": "bad.json", "verdict": "PASS"}]
        results = validate_ecv04_gate_evidence_consistency(gates, evidence_dir)
        assert not results[0].passed


class TestRunAll:
    def test_combined(self, evidence_dir: Path):
        evidence = {"verdict": "PASS"}
        (evidence_dir / "g1.json").write_text(json.dumps(evidence), encoding="utf-8")
        now = datetime.now(UTC).isoformat()
        gates = [{"gate_id": "G1", "evidence_path": "g1.json", "verdict": "PASS", "timestamp": now}]
        results = run_all_ecv_validators(gates, evidence_dir)
        assert len(results) >= 4  # at least one result per validator
        assert all(r.passed for r in results)
