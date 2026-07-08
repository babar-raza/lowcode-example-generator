"""Regression test: bandit SAST must run in CI (GitHub Actions build-and-test)."""

from pathlib import Path

import yaml


def _load_gha_workflow() -> dict:
    wf_path = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "build-and-test.yml"
    return yaml.safe_load(wf_path.read_text(encoding="utf-8"))


def test_bandit_step_exists_in_gha():
    """Assert bandit SAST step is defined in GitHub Actions build-and-test workflow."""
    wf = _load_gha_workflow()
    test_job = wf["jobs"]["test"]
    step_names = [s.get("name", "") for s in test_job["steps"]]
    assert any("bandit" in name.lower() for name in step_names), (
        "bandit SAST step missing from .github/workflows/build-and-test.yml"
    )
