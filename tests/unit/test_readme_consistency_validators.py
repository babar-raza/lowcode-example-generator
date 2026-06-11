"""Unit tests for README consistency validators RCV-01..05 — TC-RCV-001."""

from __future__ import annotations

import pytest

from plugin_examples.fixture_factory.readme_consistency_validators import (
    RcvResult,
    rcv_01_active_family_count,
    rcv_02_staged_family_count,
    rcv_03_cli_commands_match,
    rcv_04_example_count,
    rcv_05_no_removed_family_references,
    validate_readme_consistency,
)


class TestRcv01ActiveFamilyCount:
    def test_passes_when_count_matches(self):
        readme = "We support 3 active families in production."
        result = rcv_01_active_family_count(readme, ["cells", "pdf", "words"])
        assert result.passed

    def test_fails_when_count_mismatches(self):
        readme = "We support 5 active families in production."
        result = rcv_01_active_family_count(readme, ["cells", "pdf"])
        assert not result.passed
        assert "5" in result.detail and "2" in result.detail

    def test_passes_when_no_claim(self):
        readme = "This project generates examples."
        result = rcv_01_active_family_count(readme, ["cells"])
        assert result.passed
        assert "no drift" in result.detail.lower()


class TestRcv02StagedFamilyCount:
    def test_passes_when_count_matches(self):
        readme = "Additionally, 19 staged families are in discovery."
        result = rcv_02_staged_family_count(readme, 19)
        assert result.passed

    def test_fails_when_mismatches(self):
        readme = "We have 10 experimental families."
        result = rcv_02_staged_family_count(readme, 15)
        assert not result.passed

    def test_passes_when_no_claim(self):
        readme = "No staging info here."
        result = rcv_02_staged_family_count(readme, 5)
        assert result.passed


class TestRcv03CliCommandsMatch:
    def test_passes_when_all_present(self):
        readme = "Commands: run, status, doctor, verify-remote"
        result = rcv_03_cli_commands_match(readme, ["run", "status", "doctor"])
        assert result.passed

    def test_fails_when_missing(self):
        readme = "Commands: run, status"
        result = rcv_03_cli_commands_match(readme, ["run", "status", "doctor"])
        assert not result.passed
        assert "doctor" in result.detail


class TestRcv04ExampleCount:
    def test_passes_when_matches(self):
        readme = "The pipeline produces 38 examples."
        result = rcv_04_example_count(readme, 38)
        assert result.passed

    def test_fails_when_mismatches(self):
        readme = "We have 50 packages available."
        result = rcv_04_example_count(readme, 38)
        assert not result.passed

    def test_passes_when_no_claim(self):
        readme = "This is a tool for generating code."
        result = rcv_04_example_count(readme, 10)
        assert result.passed


class TestRcv05NoRemovedFamilyReferences:
    def test_passes_when_no_references(self):
        readme = "We support cells and pdf."
        result = rcv_05_no_removed_family_references(readme, ["obsolete_family"])
        assert result.passed

    def test_fails_when_removed_family_referenced(self):
        readme = "We also support legacy_ocr for backward compatibility."
        result = rcv_05_no_removed_family_references(readme, ["legacy_ocr"])
        assert not result.passed
        assert "legacy_ocr" in result.detail

    def test_passes_with_empty_removed_list(self):
        readme = "Any content here."
        result = rcv_05_no_removed_family_references(readme, [])
        assert result.passed


class TestValidateReadmeConsistency:
    def test_all_pass_scenario(self):
        readme = "We support 2 active families. 3 staged families in discovery. Commands: run, status. 10 examples."
        results = validate_readme_consistency(
            readme_text=readme,
            contract_dirs=["cells", "pdf"],
            staged_count=3,
            registered_commands=["run", "status"],
            contract_example_count=10,
            removed_families=[],
        )
        assert len(results) == 5
        assert all(r.passed for r in results)

    def test_mixed_results(self):
        readme = "We support 5 active families. Commands: run."
        results = validate_readme_consistency(
            readme_text=readme,
            contract_dirs=["cells"],
            staged_count=0,
            registered_commands=["run", "doctor"],
            contract_example_count=0,
        )
        assert len(results) == 5
        # RCV-01 fails (5 != 1), RCV-03 fails (doctor missing)
        assert not results[0].passed  # RCV-01
        assert not results[2].passed  # RCV-03
