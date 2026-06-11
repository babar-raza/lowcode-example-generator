"""Unit tests for LLM routing decision audit log — TC-AUDIT-LLM-001."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.llm_router.decision_audit import (
    DecisionAuditLog,
    DecisionAuditRecord,
    init_global_audit_log,
    get_global_audit_log,
    record_decision,
)


class TestDecisionAuditLog:
    def test_write_and_read_single_record(self, tmp_path: Path) -> None:
        log = DecisionAuditLog(path=tmp_path / "audit.jsonl", run_id="run-001")
        rec = log.record(
            provider="llm_professionalize",
            model="recommended",
            prompt_name="code_gen",
            stage="generate",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=300.0,
            outcome="success",
        )
        assert rec.provider == "llm_professionalize"
        assert rec.outcome == "success"

        records = log.read_all()
        assert len(records) == 1
        assert records[0].total_tokens == 150
        assert records[0].run_id == "run-001"

    def test_multiple_records_append_correctly(self, tmp_path: Path) -> None:
        log = DecisionAuditLog(path=tmp_path / "audit.jsonl", run_id="run-002")
        for i in range(5):
            log.record(
                provider="llm_professionalize",
                model="recommended",
                outcome="success",
                total_tokens=i * 10,
            )
        records = log.read_all()
        assert len(records) == 5
        token_totals = [r.total_tokens for r in records]
        assert token_totals == [0, 10, 20, 30, 40]

    def test_error_outcome_recorded(self, tmp_path: Path) -> None:
        log = DecisionAuditLog(path=tmp_path / "audit.jsonl", run_id="run-003")
        log.record(
            provider="ollama",
            model="codellama",
            outcome="error",
            error_message="Timeout",
            latency_ms=30000.0,
        )
        records = log.read_all()
        assert len(records) == 1
        assert records[0].outcome == "error"
        assert records[0].error_message == "Timeout"

    def test_read_all_returns_empty_when_no_file(self, tmp_path: Path) -> None:
        log = DecisionAuditLog(path=tmp_path / "nonexistent.jsonl", run_id="run-004")
        assert log.read_all() == []

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        nested = tmp_path / "nested" / "deep" / "audit.jsonl"
        log = DecisionAuditLog(path=nested, run_id="run-005")
        log.record(provider="ollama", model="codellama", outcome="success")
        assert nested.exists()

    def test_summary_correct_aggregation(self, tmp_path: Path) -> None:
        log = DecisionAuditLog(path=tmp_path / "audit.jsonl", run_id="run-006")
        log.record(provider="llm_professionalize", model="recommended", outcome="success", total_tokens=100, latency_ms=200.0)
        log.record(provider="llm_professionalize", model="recommended", outcome="success", total_tokens=200, latency_ms=300.0)
        log.record(provider="ollama", model="codellama", outcome="error", latency_ms=100.0)

        summary = log.summary()
        assert summary["total_calls"] == 3
        assert summary["successful_calls"] == 2
        assert summary["error_calls"] == 1
        assert summary["total_tokens"] == 300
        assert "llm_professionalize" in summary["providers_used"]
        assert "ollama" in summary["providers_used"]

    def test_audit_file_is_valid_jsonl(self, tmp_path: Path) -> None:
        log = DecisionAuditLog(path=tmp_path / "audit.jsonl", run_id="run-007")
        log.record(provider="llm_professionalize", model="gpt-4", outcome="success")
        log.record(provider="ollama", model="codellama", outcome="error")

        lines = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            data = json.loads(line)  # must be valid JSON
            assert "provider" in data
            assert "outcome" in data
            assert "timestamp" in data

    def test_path_property(self, tmp_path: Path) -> None:
        p = tmp_path / "audit.jsonl"
        log = DecisionAuditLog(path=p, run_id="run-008")
        assert log.path == p


class TestGlobalAuditLog:
    def test_global_log_roundtrip(self, tmp_path: Path) -> None:
        audit_log = init_global_audit_log(path=tmp_path / "global-audit.jsonl", run_id="global-001")
        assert get_global_audit_log() is audit_log

        record_decision(
            provider="llm_professionalize",
            model="recommended",
            outcome="success",
            total_tokens=75,
        )
        records = audit_log.read_all()
        assert len(records) == 1
        assert records[0].total_tokens == 75

    def test_record_decision_no_op_when_not_initialized(self, tmp_path: Path) -> None:
        """record_decision should not raise when no global log is initialized."""
        import plugin_examples.llm_router.decision_audit as da
        original = da._global_audit_log
        da._global_audit_log = None
        try:
            record_decision(provider="test", model="test", outcome="success")
        finally:
            da._global_audit_log = original
