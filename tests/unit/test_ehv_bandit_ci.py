"""Regression test: bandit-sast CI job must exist as a blocking gate."""

from pathlib import Path

import yaml


def _load_ci_config() -> dict:
    ci_path = Path(__file__).resolve().parents[2] / ".gitlab-ci.yml"
    return yaml.safe_load(ci_path.read_text(encoding="utf-8"))


def test_bandit_sast_job_exists():
    """Assert bandit-sast job is defined in .gitlab-ci.yml."""
    ci = _load_ci_config()
    assert "bandit-sast" in ci, "bandit-sast job missing from .gitlab-ci.yml"


def test_bandit_sast_is_blocking():
    """Assert bandit-sast does NOT have allow_failure: true."""
    ci = _load_ci_config()
    job = ci["bandit-sast"]
    assert job.get("allow_failure") is not True, "bandit-sast must be a blocking gate (allow_failure must not be true)"


def test_bandit_sast_in_lint_stage():
    """Assert bandit-sast runs in lint stage."""
    ci = _load_ci_config()
    job = ci["bandit-sast"]
    assert job.get("stage") == "lint", "bandit-sast should run in lint stage"
