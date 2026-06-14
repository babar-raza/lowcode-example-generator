"""Tests for metrics integration in PipelineContext and runner wiring."""

from pathlib import Path

import pytest


class TestPipelineContextMetrics:
    def test_context_has_metrics_collector_field(self):
        from plugin_examples.runner import PipelineContext

        ctx = PipelineContext(
            family="cells",
            run_id="test-001",
            dry_run=True,
            skip_run=True,
            template_mode=True,
            require_llm=False,
            require_validation=False,
            require_reviewer=False,
            repo_root=Path("."),
            run_dir=Path("."),
            evidence_dir=Path("."),
        )
        # Default is None
        assert ctx.metrics_collector is None

    def test_context_accepts_metrics_collector(self):
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.runner import PipelineContext

        mc = MetricsCollector()
        ctx = PipelineContext(
            family="cells",
            run_id="test-002",
            dry_run=True,
            skip_run=True,
            template_mode=True,
            require_llm=False,
            require_validation=False,
            require_reviewer=False,
            repo_root=Path("."),
            run_dir=Path("."),
            evidence_dir=Path("."),
            metrics_collector=mc,
        )
        assert ctx.metrics_collector is mc
        assert ctx.metrics_collector.api_calls_count == 0

    def test_metrics_collector_none_by_default_no_overhead(self):
        """Without metrics, there should be zero overhead."""
        from plugin_examples.runner import PipelineContext

        ctx = PipelineContext(
            family="cells",
            run_id="test-003",
            dry_run=True,
            skip_run=True,
            template_mode=True,
            require_llm=False,
            require_validation=False,
            require_reviewer=False,
            repo_root=Path("."),
            run_dir=Path("."),
            evidence_dir=Path("."),
        )
        # metrics_collector is None — no MetricsCollector imported/created
        assert ctx.metrics_collector is None
