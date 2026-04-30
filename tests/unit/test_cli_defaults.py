"""Unit tests for CLI default behavior — ensures no hardcoded overrides."""

from __future__ import annotations

import sys
from unittest.mock import patch, MagicMock

import pytest


class TestCLIDefaults:
    """Verify CLI defaults are honest and not hardcoded."""

    def _parse_run_args(self, extra_args: list[str] | None = None):
        """Parse CLI args and capture what run_pipeline would receive."""
        from plugin_examples.__main__ import main
        args_list = ["plugin-examples", "run", "--family", "cells"]
        if extra_args:
            args_list.extend(extra_args)

        captured = {}

        def fake_run_pipeline(**kwargs):
            captured.update(kwargs)
            return {
                "gate_summary": {"passed": 10, "degraded": 0, "failed": 0,
                                  "hard_stopped": False},
                "verdict": "DATA_FLOW_PROTOTYPE_ONLY",
            }

        with patch("plugin_examples.runner.run_pipeline", side_effect=fake_run_pipeline):
            with patch.object(sys, "argv", args_list):
                main()

        return captured

    def test_default_run_not_template_mode(self):
        """Default run must NOT force template_mode=True."""
        kwargs = self._parse_run_args()
        assert kwargs["template_mode"] is False

    def test_default_run_not_skip_run(self):
        """Default run must NOT force skip_run=True."""
        kwargs = self._parse_run_args()
        assert kwargs["skip_run"] is False

    def test_default_dry_run_true(self):
        """Default run should be dry_run=True (no publishing)."""
        kwargs = self._parse_run_args()
        assert kwargs["dry_run"] is True

    def test_template_mode_flag_works(self):
        """--template-mode must set template_mode=True."""
        kwargs = self._parse_run_args(["--template-mode"])
        assert kwargs["template_mode"] is True

    def test_skip_run_flag_works(self):
        """--skip-run must set skip_run=True."""
        kwargs = self._parse_run_args(["--skip-run"])
        assert kwargs["skip_run"] is True

    def test_require_llm_flag_works(self):
        """--require-llm must set require_llm=True."""
        kwargs = self._parse_run_args(["--require-llm"])
        assert kwargs["require_llm"] is True

    def test_require_validation_flag_works(self):
        """--require-validation must set require_validation=True."""
        kwargs = self._parse_run_args(["--require-validation"])
        assert kwargs["require_validation"] is True

    def test_require_reviewer_flag_works(self):
        """--require-reviewer must set require_reviewer=True."""
        kwargs = self._parse_run_args(["--require-reviewer"])
        assert kwargs["require_reviewer"] is True

    def test_tier_flag_works(self):
        """--tier must set max_tier."""
        kwargs = self._parse_run_args(["--tier", "3"])
        assert kwargs["max_tier"] == 3

    def test_promote_latest_flag_works(self):
        """--promote-latest must set promote_latest=True."""
        kwargs = self._parse_run_args(["--promote-latest"])
        assert kwargs["promote_latest"] is True

    def test_allow_experimental_flag_works(self):
        """--allow-experimental must set allow_experimental=True."""
        kwargs = self._parse_run_args(["--allow-experimental"])
        assert kwargs["allow_experimental"] is True

    def test_publish_implies_require_validation(self):
        """--publish must force require_validation=True."""
        import os
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
            kwargs = self._parse_run_args(["--publish"])
        assert kwargs["require_validation"] is True

    def test_publish_implies_require_reviewer(self):
        """--publish must force require_reviewer=True."""
        import os
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
            kwargs = self._parse_run_args(["--publish"])
        assert kwargs["require_reviewer"] is True

    def test_publish_sets_dry_run_false(self):
        """--publish must set dry_run=False."""
        import os
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
            kwargs = self._parse_run_args(["--publish"])
        assert kwargs["dry_run"] is False

    def test_publish_without_token_fails(self):
        """--publish without GITHUB_TOKEN must exit with error."""
        import os
        with patch.dict(os.environ, {}, clear=True):
            # Remove GITHUB_TOKEN if present
            os.environ.pop("GITHUB_TOKEN", None)
            from plugin_examples.__main__ import main
            with patch.object(sys, "argv",
                              ["plugin-examples", "run", "--family", "cells", "--publish"]):
                with patch("plugin_examples.runner.run_pipeline") as mock_rp:
                    exit_code = main()
            assert exit_code == 1
            mock_rp.assert_not_called()

    def test_all_flags_parsed(self):
        """All 9 new flags must parse without error."""
        import os
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
            kwargs = self._parse_run_args([
                "--template-mode", "--skip-run", "--require-llm",
                "--require-validation", "--require-reviewer",
                "--publish", "--tier", "3", "--promote-latest",
                "--allow-experimental",
            ])
        assert kwargs["template_mode"] is True
        assert kwargs["skip_run"] is True
        assert kwargs["require_llm"] is True
        assert kwargs["require_validation"] is True
        assert kwargs["require_reviewer"] is True
        assert kwargs["dry_run"] is False
        assert kwargs["max_tier"] == 3
        assert kwargs["promote_latest"] is True
        assert kwargs["allow_experimental"] is True
