"""Integration test: LLM decision audit log end-to-end — TC-AUDIT-LLM-INT-001.

Verifies that:
1. The audit log is written when LLM calls are made (success and error paths)
2. Audit records survive a full router generate() cycle
3. Multiple calls append correctly (not overwrite)
4. Summary statistics are correct after a session
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.llm_router.decision_audit import (
    DecisionAuditLog,
    get_global_audit_log,
    init_global_audit_log,
    record_decision,
)
from plugin_examples.llm_router.router import LLMRouter


class TestDecisionAuditIntegration:
    """End-to-end audit log behavior through the router generate() path."""

    def test_audit_captures_successful_generate(self, tmp_path: Path) -> None:
        """Router.generate() success path records an audit entry."""
        audit_log = DecisionAuditLog(path=tmp_path / "audit.jsonl", run_id="int-001")

        # Initialize as global
        import plugin_examples.llm_router.decision_audit as da
        original = da._global_audit_log
        da._global_audit_log = audit_log

        try:
            router = LLMRouter(provider_order=["llm_professionalize"])
            router.selected_provider = "llm_professionalize"

            fake_response = MagicMock()
            fake_response.status_code = 200
            fake_response.raise_for_status = MagicMock()
            fake_response.json.return_value = {
                "choices": [{"message": {"content": "Hello from LLM"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            }

            with patch("plugin_examples.llm_router.router.requests.post", return_value=fake_response):
                result = router.generate("Test prompt")

            assert result == "Hello from LLM"

            records = audit_log.read_all()
            assert len(records) == 1
            assert records[0].outcome == "success"
            assert records[0].provider == "llm_professionalize"
            assert records[0].latency_ms >= 0
        finally:
            da._global_audit_log = original

    def test_audit_captures_error_generate(self, tmp_path: Path) -> None:
        """Router.generate() error path records an error audit entry."""
        audit_log = DecisionAuditLog(path=tmp_path / "audit.jsonl", run_id="int-002")

        import plugin_examples.llm_router.decision_audit as da
        original = da._global_audit_log
        da._global_audit_log = audit_log

        try:
            router = LLMRouter(provider_order=["llm_professionalize"])
            router.selected_provider = "llm_professionalize"

            with patch("plugin_examples.llm_router.router.requests.post", side_effect=ConnectionError("refused")), pytest.raises(Exception):
                    router.generate("Test prompt")

            records = audit_log.read_all()
            assert len(records) == 1
            assert records[0].outcome == "error"
            assert records[0].provider == "llm_professionalize"
        finally:
            da._global_audit_log = original

    def test_multiple_calls_accumulate(self, tmp_path: Path) -> None:
        """Multiple generate() calls accumulate in audit log."""
        audit_log = DecisionAuditLog(path=tmp_path / "audit.jsonl", run_id="int-003")

        import plugin_examples.llm_router.decision_audit as da
        original = da._global_audit_log
        da._global_audit_log = audit_log

        try:
            router = LLMRouter(provider_order=["llm_professionalize"])
            router.selected_provider = "llm_professionalize"

            fake_response = MagicMock()
            fake_response.status_code = 200
            fake_response.raise_for_status = MagicMock()
            fake_response.json.return_value = {
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
            }

            with patch("plugin_examples.llm_router.router.requests.post", return_value=fake_response):
                for _ in range(3):
                    router.generate("prompt")

            records = audit_log.read_all()
            assert len(records) == 3
            assert all(r.outcome == "success" for r in records)

            summary = audit_log.summary()
            assert summary["total_calls"] == 3
            assert summary["successful_calls"] == 3
        finally:
            da._global_audit_log = original

    def test_audit_jsonl_survives_process_restart(self, tmp_path: Path) -> None:
        """Audit log written in one session can be read in a new session."""
        path = tmp_path / "audit.jsonl"

        # Session 1: write records
        log1 = DecisionAuditLog(path=path, run_id="session-1")
        for i in range(3):
            log1.record(provider="llm_professionalize", model="recommended", outcome="success", total_tokens=i * 10)

        # Session 2: new instance reads same file
        log2 = DecisionAuditLog(path=path, run_id="session-2")
        records = log2.read_all()
        assert len(records) == 3
        assert [r.total_tokens for r in records] == [0, 10, 20]

    def test_audit_does_not_fail_when_not_initialized(self) -> None:
        """record_decision() is a no-op when no global log is initialized."""
        import plugin_examples.llm_router.decision_audit as da
        original = da._global_audit_log
        da._global_audit_log = None
        try:
            record_decision(provider="test", model="test", outcome="success")
            # Should not raise
        finally:
            da._global_audit_log = original
