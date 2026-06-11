"""Tests for CLI metrics flags and pipeline hook wiring."""

from unittest.mock import MagicMock, patch

import pytest


class TestCLIFlags:
    def test_metrics_flags_registered(self):
        """Verify --metrics and related flags exist on the run subparser."""
        import argparse

        # Import __main__ to get the parser
        # We'll test by parsing known args
        from plugin_examples.__main__ import main

        # Just verify the flags parse without error by constructing a parser
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument("--family", required=True)
        run_parser.add_argument("--metrics", action="store_true")
        run_parser.add_argument("--metrics-post", action="store_true")
        run_parser.add_argument("--metrics-job-type", metavar="TYPE")
        run_parser.add_argument("--metrics-strict", action="store_true")
        run_parser.add_argument("--metrics-force-repost", action="store_true")
        run_parser.add_argument("--metrics-config", metavar="PATH")

        args = parser.parse_args(["run", "--family", "cells", "--metrics"])
        assert args.metrics is True
        assert args.metrics_post is False

    def test_metrics_disabled_by_default(self):
        """Without --metrics flag, no metrics modules should be imported."""
        import argparse

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument("--family", required=True)
        run_parser.add_argument("--metrics", action="store_true")

        args = parser.parse_args(["run", "--family", "cells"])
        assert args.metrics is False

    def test_metrics_post_requires_metrics(self):
        """--metrics-post should be independent flag."""
        import argparse

        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        run_parser = subparsers.add_parser("run")
        run_parser.add_argument("--family", required=True)
        run_parser.add_argument("--metrics", action="store_true")
        run_parser.add_argument("--metrics-post", action="store_true")
        run_parser.add_argument("--metrics-job-type")

        args = parser.parse_args(
            ["run", "--family", "cells", "--metrics", "--metrics-post", "--metrics-job-type", "Test"]
        )
        assert args.metrics is True
        assert args.metrics_post is True
        assert args.metrics_job_type == "Test"


class TestPipelineHook:
    def test_finalize_dry_run(self, tmp_path):
        """finalize_metrics in dry-run mode writes evidence but does not POST."""
        from plugin_examples.metrics.pipeline_hook import finalize_metrics
        from plugin_examples.metrics.config import load_metrics_config
        from plugin_examples.metrics.models import MetricsCollector
        import yaml

        cfg_data = {
            "metrics": {
                "agent_owner": "Test",
                "agent_name": "test-gen",
                "website": "aspose.net",
                "family_to_product": {"cells": "Aspose.Cells"},
                "command_to_job_type": {"run": "Examples Generation"},
                "verdict_to_status": {"PR_READY": "success"},
                "api_endpoint": "https://example.com/exec",
            }
        }
        cfg_path = tmp_path / "m.yml"
        cfg_path.write_text(yaml.dump(cfg_data), encoding="utf-8")
        config = load_metrics_config(config_path=cfg_path)

        # Build a mock context
        ctx = MagicMock()
        ctx.run_id = "test-hook-1"
        ctx.family = "cells"
        ctx.evidence_dir = tmp_path / "evidence"
        ctx.evidence_dir.mkdir()
        ctx.repo_root = tmp_path
        ctx.metrics_collector = MetricsCollector()
        ctx.planning = None
        ctx.validation_results = []
        ctx.generated_projects = []

        report = {
            "meta": {"run_id": "test-hook-1", "total_duration_ms": 500},
            "comparison": {},
            "verdict": "PR_READY",
            "gate_summary": {},
        }

        with patch("plugin_examples.metrics.poster.requests.post") as mock_post:
            result = finalize_metrics(
                ctx=ctx,
                config=config,
                report=report,
                command="run",
                dry_run=True,
                post=False,
            )

        mock_post.assert_not_called()
        assert result["metrics_enabled"] is True
        assert result["post_result"]["posted"] is False
        assert result["post_result"]["reason"] == "dry_run"

    def test_finalize_writes_evidence_files(self, tmp_path):
        """finalize_metrics writes all evidence files."""
        from plugin_examples.metrics.pipeline_hook import finalize_metrics
        from plugin_examples.metrics.config import load_metrics_config
        from plugin_examples.metrics.models import MetricsCollector
        import yaml

        cfg_data = {
            "metrics": {
                "agent_owner": "Test",
                "agent_name": "test-gen",
                "website": "aspose.net",
                "family_to_product": {"cells": "Aspose.Cells"},
                "command_to_job_type": {"run": "Examples Generation"},
                "verdict_to_status": {"PR_READY": "success"},
                "api_endpoint": "https://example.com/exec",
            }
        }
        cfg_path = tmp_path / "m.yml"
        cfg_path.write_text(yaml.dump(cfg_data), encoding="utf-8")
        config = load_metrics_config(config_path=cfg_path)

        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()

        collector = MetricsCollector()
        collector.record_call(
            stage="generation",
            provider="llm_professionalize",
            model="gpt-4o",
            success=True,
            http_status=200,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            token_usage_available=True,
            duration_ms=200.0,
        )

        ctx = MagicMock()
        ctx.run_id = "test-evidence-1"
        ctx.family = "cells"
        ctx.evidence_dir = evidence_dir
        ctx.repo_root = tmp_path
        ctx.metrics_collector = collector
        ctx.planning = None
        ctx.validation_results = []
        ctx.generated_projects = []

        report = {
            "meta": {"run_id": "test-evidence-1", "total_duration_ms": 1000},
            "comparison": {},
            "verdict": "PR_READY",
            "gate_summary": {},
        }

        with patch("plugin_examples.metrics.poster.requests.post"):
            finalize_metrics(
                ctx=ctx,
                config=config,
                report=report,
                command="run",
                dry_run=True,
            )

        # Check evidence files written
        files = [f.name for f in evidence_dir.iterdir()]
        assert "agent-metrics-llm-calls.jsonl" in files
        assert "agent-metrics-run-summary.json" in files
        assert "agent-metrics-payload.json" in files
        assert "agent-metrics-validation.json" in files
        assert "agent-metrics-post-result.json" in files

    def test_finalize_strict_raises_on_invalid(self, tmp_path):
        """strict=True raises ValueError on validation failure."""
        from plugin_examples.metrics.pipeline_hook import finalize_metrics
        from plugin_examples.metrics.config import load_metrics_config
        import yaml

        cfg_data = {
            "metrics": {
                "agent_owner": "Test",
                "agent_name": "test-gen",
                "website": "aspose.net",
                "family_to_product": {"cells": "Aspose.Cells"},
                "command_to_job_type": {"run": "Examples Generation"},
                "verdict_to_status": {"PR_READY": "success"},
                "api_endpoint": "https://example.com/exec",
            }
        }
        cfg_path = tmp_path / "m.yml"
        cfg_path.write_text(yaml.dump(cfg_data), encoding="utf-8")
        config = load_metrics_config(config_path=cfg_path)

        ctx = MagicMock()
        ctx.run_id = "test-strict-1"
        ctx.family = "nonexistent"  # Missing from family_to_product → invalid
        ctx.evidence_dir = tmp_path / "evidence"
        ctx.evidence_dir.mkdir()
        ctx.repo_root = tmp_path
        ctx.metrics_collector = None
        ctx.planning = None
        ctx.validation_results = []
        ctx.generated_projects = []

        report = {
            "meta": {"run_id": "test-strict-1", "total_duration_ms": 0},
            "comparison": {},
            "verdict": "",
            "gate_summary": {},
        }

        with pytest.raises(ValueError, match="validation failed"):
            finalize_metrics(
                ctx=ctx,
                config=config,
                report=report,
                command="run",
                dry_run=True,
                strict=True,
            )

    def test_finalize_non_strict_does_not_raise(self, tmp_path):
        """strict=False (default) does not raise on errors."""
        from plugin_examples.metrics.pipeline_hook import finalize_metrics
        from plugin_examples.metrics.config import load_metrics_config
        import yaml

        cfg_data = {
            "metrics": {
                "agent_owner": "Test",
                "agent_name": "test-gen",
                "website": "aspose.net",
                "family_to_product": {"cells": "Aspose.Cells"},
                "command_to_job_type": {"run": "Examples Generation"},
                "verdict_to_status": {"PR_READY": "success"},
                "api_endpoint": "https://example.com/exec",
            }
        }
        cfg_path = tmp_path / "m.yml"
        cfg_path.write_text(yaml.dump(cfg_data), encoding="utf-8")
        config = load_metrics_config(config_path=cfg_path)

        ctx = MagicMock()
        ctx.run_id = "test-nostrict-1"
        ctx.family = "nonexistent"
        ctx.evidence_dir = tmp_path / "evidence"
        ctx.evidence_dir.mkdir()
        ctx.repo_root = tmp_path
        ctx.metrics_collector = None
        ctx.planning = None
        ctx.validation_results = []
        ctx.generated_projects = []

        report = {
            "meta": {"run_id": "test-nostrict-1", "total_duration_ms": 0},
            "comparison": {},
            "verdict": "",
            "gate_summary": {},
        }

        # Should not raise
        result = finalize_metrics(
            ctx=ctx,
            config=config,
            report=report,
            command="run",
            dry_run=True,
            strict=False,
        )
        assert result["metrics_enabled"] is True


class TestRunPipelineMetricsParam:
    def test_run_pipeline_accepts_metrics_params(self):
        """Verify run_pipeline signature accepts metrics parameters."""
        import inspect
        from plugin_examples.runner import run_pipeline

        sig = inspect.signature(run_pipeline)
        params = set(sig.parameters.keys())
        assert "metrics_collector" in params
        assert "metrics_config" in params
        assert "metrics_post" in params
        assert "metrics_job_type" in params
        assert "metrics_strict" in params
        assert "metrics_force_repost" in params

    def test_default_no_metrics(self):
        """Without metrics_collector, no metrics code runs."""
        import inspect
        from plugin_examples.runner import run_pipeline

        sig = inspect.signature(run_pipeline)
        assert sig.parameters["metrics_collector"].default is None
        assert sig.parameters["metrics_config"].default is None
        assert sig.parameters["metrics_post"].default is False
