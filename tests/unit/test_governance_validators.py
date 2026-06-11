"""Tests for src/plugin_examples/fixture_factory/governance_validators.py.

Verifies that each GOV-01..GOV-06 validator:
- Returns PASS when the expected artifact exists and is valid
- Returns FAIL/warning when the artifact is missing, empty, or stale
- Uses the correct validator_id in all findings
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from plugin_examples.fixture_factory.governance_validators import (
    ALL_GOVERNANCE_VALIDATORS,
    run_all_governance_validators,
    validate_adr_directory,
    validate_changelog,
    validate_codeowners,
    validate_incident_response,
    validate_release_process,
    validate_sla,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ctx(tmp_path: Path, *, version: str = "0.27.0") -> dict:
    return {"repo_root": str(tmp_path), "project_version": version}


def _make_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")


def _passes(results: list[dict]) -> list[dict]:
    return [r for r in results if r["status"] == "PASS"]


def _fails(results: list[dict]) -> list[dict]:
    return [r for r in results if r["status"] == "FAIL"]


# ---------------------------------------------------------------------------
# GOV-01 — CODEOWNERS
# ---------------------------------------------------------------------------

class TestValidateCodeowners:
    def test_pass_when_codeowners_has_rules(self, tmp_path):
        _make_file(tmp_path / ".github" / "CODEOWNERS", "* @org/team\n")
        results = validate_codeowners(_ctx(tmp_path))
        assert len(_passes(results)) == 1
        assert results[0]["validator_id"] == "GOV-01"

    def test_fail_when_codeowners_missing(self, tmp_path):
        results = validate_codeowners(_ctx(tmp_path))
        assert len(_fails(results)) == 1
        assert results[0]["validator_id"] == "GOV-01"
        assert "missing" in results[0]["title"].lower()

    def test_fail_when_codeowners_comment_only(self, tmp_path):
        _make_file(tmp_path / ".github" / "CODEOWNERS", "# comment only\n# another comment\n")
        results = validate_codeowners(_ctx(tmp_path))
        assert len(_fails(results)) == 1
        assert "empty" in results[0]["title"].lower() or "comment" in results[0]["title"].lower()

    def test_fail_when_codeowners_empty(self, tmp_path):
        _make_file(tmp_path / ".github" / "CODEOWNERS", "")
        results = validate_codeowners(_ctx(tmp_path))
        assert len(_fails(results)) == 1


# ---------------------------------------------------------------------------
# GOV-02 — CHANGELOG
# ---------------------------------------------------------------------------

class TestValidateChangelog:
    def test_pass_when_changelog_has_version(self, tmp_path):
        _make_file(
            tmp_path / "CHANGELOG.md",
            "# Changelog\n\n## [0.27.0] - 2026-06-10\n\n### Added\n- stuff\n",
        )
        results = validate_changelog(_ctx(tmp_path, version="0.27.0"))
        assert len(_passes(results)) == 1
        assert results[0]["validator_id"] == "GOV-02"

    def test_fail_when_changelog_missing(self, tmp_path):
        results = validate_changelog(_ctx(tmp_path))
        assert len(_fails(results)) == 1
        assert "missing" in results[0]["title"].lower()

    def test_fail_when_changelog_empty(self, tmp_path):
        _make_file(tmp_path / "CHANGELOG.md", "")
        results = validate_changelog(_ctx(tmp_path))
        assert len(_fails(results)) == 1

    def test_warning_when_version_not_in_changelog(self, tmp_path):
        _make_file(
            tmp_path / "CHANGELOG.md",
            "# Changelog\n\n## [0.26.0] - 2026-06-09\n\n### Added\n- old stuff\n",
        )
        results = validate_changelog(_ctx(tmp_path, version="0.27.0"))
        # Should be a FAIL with warning severity — version mismatch
        assert len(_fails(results)) == 1
        assert "0.27.0" in results[0]["description"]

    def test_pass_when_no_version_in_context(self, tmp_path):
        _make_file(tmp_path / "CHANGELOG.md", "# Changelog\n\n## [0.27.0] - 2026-06-10\n")
        # When project_version is empty, skip version check
        results = validate_changelog({"repo_root": str(tmp_path), "project_version": ""})
        assert len(_passes(results)) == 1


# ---------------------------------------------------------------------------
# GOV-03 — ADR directory
# ---------------------------------------------------------------------------

class TestValidateAdrDirectory:
    def test_pass_when_adr_directory_has_files(self, tmp_path):
        _make_file(
            tmp_path / "docs" / "adr" / "ADR-001-test.md",
            "# ADR-001\nStatus: Accepted\n",
        )
        results = validate_adr_directory(_ctx(tmp_path))
        assert len(_passes(results)) == 1
        assert results[0]["validator_id"] == "GOV-03"

    def test_fail_when_adr_directory_missing(self, tmp_path):
        results = validate_adr_directory(_ctx(tmp_path))
        assert len(_fails(results)) == 1
        assert "missing" in results[0]["title"].lower()

    def test_fail_when_adr_directory_empty(self, tmp_path):
        (tmp_path / "docs" / "adr").mkdir(parents=True, exist_ok=True)
        results = validate_adr_directory(_ctx(tmp_path))
        assert len(_fails(results)) == 1
        assert "empty" in results[0]["title"].lower()

    def test_pass_counts_multiple_adrs(self, tmp_path):
        for i in range(1, 4):
            _make_file(
                tmp_path / "docs" / "adr" / f"ADR-00{i}-test.md",
                "# ADR\nStatus: Accepted\n",
            )
        results = validate_adr_directory(_ctx(tmp_path))
        assert len(_passes(results)) == 1
        assert "3" in results[0]["description"] or "3" in results[0]["title"]


# ---------------------------------------------------------------------------
# GOV-04 — Incident response
# ---------------------------------------------------------------------------

class TestValidateIncidentResponse:
    def test_pass_when_doc_is_substantial(self, tmp_path):
        content = "# Incident Response\n\n" + "## Severity\n" * 20 + "Details here.\n" * 20
        _make_file(tmp_path / "docs" / "operations" / "incident-response.md", content)
        results = validate_incident_response(_ctx(tmp_path))
        assert len(_passes(results)) == 1
        assert results[0]["validator_id"] == "GOV-04"

    def test_fail_when_doc_missing(self, tmp_path):
        results = validate_incident_response(_ctx(tmp_path))
        assert len(_fails(results)) == 1

    def test_fail_when_doc_too_short(self, tmp_path):
        _make_file(
            tmp_path / "docs" / "operations" / "incident-response.md",
            "# Incident Response\nTODO\n",
        )
        results = validate_incident_response(_ctx(tmp_path))
        assert len(_fails(results)) == 1
        assert "short" in results[0]["title"].lower()


# ---------------------------------------------------------------------------
# GOV-05 — SLA
# ---------------------------------------------------------------------------

class TestValidateSla:
    def test_pass_when_sla_present(self, tmp_path):
        _make_file(tmp_path / "docs" / "operations" / "sla.md", "# SLA\n\n## Targets\n- 99%\n")
        results = validate_sla(_ctx(tmp_path))
        assert len(_passes(results)) == 1
        assert results[0]["validator_id"] == "GOV-05"

    def test_fail_when_sla_missing(self, tmp_path):
        results = validate_sla(_ctx(tmp_path))
        assert len(_fails(results)) == 1


# ---------------------------------------------------------------------------
# GOV-06 — Release process
# ---------------------------------------------------------------------------

class TestValidateReleaseProcess:
    def test_pass_when_release_process_present(self, tmp_path):
        _make_file(
            tmp_path / "docs" / "operations" / "release-process.md",
            "# Release Process\n\n## Steps\n1. Bump version\n2. Update CHANGELOG\n",
        )
        results = validate_release_process(_ctx(tmp_path))
        assert len(_passes(results)) == 1
        assert results[0]["validator_id"] == "GOV-06"

    def test_fail_when_release_process_missing(self, tmp_path):
        results = validate_release_process(_ctx(tmp_path))
        assert len(_fails(results)) == 1


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

class TestRunAllGovernanceValidators:
    def test_returns_one_result_per_validator_when_all_pass(self, tmp_path):
        # Set up a repo with all governance artifacts
        _make_file(tmp_path / ".github" / "CODEOWNERS", "* @org/team\n")
        _make_file(
            tmp_path / "CHANGELOG.md",
            "# Changelog\n\n## [0.27.0] - 2026-06-10\n\n### Added\n- stuff\n",
        )
        _make_file(
            tmp_path / "docs" / "adr" / "ADR-001-test.md",
            "# ADR-001\nStatus: Accepted\n",
        )
        ir_content = "# Incident Response\n\n" + "Details.\n" * 50
        _make_file(tmp_path / "docs" / "operations" / "incident-response.md", ir_content)
        _make_file(tmp_path / "docs" / "operations" / "sla.md", "# SLA\n\n## Targets\n")
        _make_file(
            tmp_path / "docs" / "operations" / "release-process.md",
            "# Release Process\n\n## Steps\n",
        )

        results = run_all_governance_validators(_ctx(tmp_path, version="0.27.0"))
        passed = _passes(results)
        failed = _fails(results)
        # All 6 validators should pass
        assert len(passed) == len(ALL_GOVERNANCE_VALIDATORS)
        assert len(failed) == 0

    def test_returns_fails_when_nothing_present(self, tmp_path):
        results = run_all_governance_validators(_ctx(tmp_path))
        failed = _fails(results)
        # All 6 should fail when nothing exists
        assert len(failed) == len(ALL_GOVERNANCE_VALIDATORS)

    def test_validator_ids_are_unique(self, tmp_path):
        results = run_all_governance_validators(_ctx(tmp_path))
        ids = [r["validator_id"] for r in results]
        assert len(ids) == len(set(ids)), "Duplicate validator IDs found"
