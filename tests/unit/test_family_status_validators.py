"""Unit tests for family status validators FSV-01..06 — TC-FSV-001."""

from __future__ import annotations

from pathlib import Path

import pytest

from plugin_examples.fixture_factory.family_status_validators import (
    ALLOWED_STATUSES,
    FsvResult,
    fsv_01_status_field_present,
    fsv_02_status_value_valid,
    fsv_03_active_has_contracts,
    fsv_04_discovery_not_published,
    fsv_05_active_count_matches_contracts,
    fsv_06_no_orphan_references,
    validate_all,
)


def _cfg(name: str, status: str = "active", **kwargs) -> dict:
    d = {"_filename": f"{name}.yml", "_family_name": name, "status": status}
    d.update(kwargs)
    return d


class TestFsv01StatusFieldPresent:
    def test_passes_when_present(self):
        results = fsv_01_status_field_present([_cfg("cells")])
        assert all(r.passed for r in results)

    def test_fails_when_missing(self):
        cfg = {"_filename": "bad.yml", "_family_name": "bad"}
        results = fsv_01_status_field_present([cfg])
        assert not results[0].passed


class TestFsv02StatusValueValid:
    def test_passes_for_valid_statuses(self):
        for status in ALLOWED_STATUSES:
            results = fsv_02_status_value_valid([_cfg("test", status)])
            assert results[0].passed, f"Failed for {status}"

    def test_fails_for_invalid_status(self):
        results = fsv_02_status_value_valid([_cfg("epub", "discovery_blocked")])
        assert not results[0].passed
        assert "NOT IN ENUM" in results[0].detail


class TestFsv03ActiveHasContracts:
    def test_passes_when_contract_dir_exists(self, tmp_path):
        contracts = tmp_path / "contracts"
        contracts.mkdir()
        (contracts / "cells").mkdir()
        results = fsv_03_active_has_contracts([_cfg("cells", "active")], contracts)
        assert results[0].passed

    def test_fails_when_contract_dir_missing(self, tmp_path):
        contracts = tmp_path / "contracts"
        contracts.mkdir()
        results = fsv_03_active_has_contracts([_cfg("cells", "active")], contracts)
        assert not results[0].passed

    def test_skips_non_active(self, tmp_path):
        contracts = tmp_path / "contracts"
        contracts.mkdir()
        results = fsv_03_active_has_contracts([_cfg("barcode", "discovery_only")], contracts)
        assert len(results) == 0


class TestFsv04DiscoveryNotPublished:
    def test_passes_when_not_publication(self):
        results = fsv_04_discovery_not_published([_cfg("barcode", "discovery_only")])
        assert results[0].passed

    def test_fails_when_discovery_claims_publication(self):
        results = fsv_04_discovery_not_published(
            [_cfg("barcode", "discovery_only", discovery_mode="publication")]
        )
        assert not results[0].passed


class TestFsv05ActiveCountMatchesContracts:
    def test_matches(self, tmp_path):
        contracts = tmp_path / "contracts"
        contracts.mkdir()
        (contracts / "cells").mkdir()
        results = fsv_05_active_count_matches_contracts([_cfg("cells", "active")], contracts)
        assert results[0].passed

    def test_mismatch(self, tmp_path):
        contracts = tmp_path / "contracts"
        contracts.mkdir()
        (contracts / "cells").mkdir()
        (contracts / "pdf").mkdir()
        results = fsv_05_active_count_matches_contracts([_cfg("cells", "active")], contracts)
        assert not results[0].passed


class TestFsv06NoOrphanReferences:
    def test_passes_when_contract_exists(self, tmp_path):
        contracts = tmp_path / "contracts"
        contracts.mkdir()
        (contracts / "cells").mkdir()
        results = fsv_06_no_orphan_references([_cfg("cells", "active")], contracts)
        assert results[0].passed

    def test_fails_when_contract_missing(self, tmp_path):
        contracts = tmp_path / "contracts"
        contracts.mkdir()
        results = fsv_06_no_orphan_references([_cfg("cells", "active")], contracts)
        assert not results[0].passed


class TestValidateAll:
    def test_runs_against_real_repo(self):
        """Validate against the actual repository configs."""
        repo_root = Path(__file__).resolve().parents[2]
        results = validate_all(repo_root)
        assert len(results) > 0
        # Check for the known epub issue: discovery_blocked is not in enum
        fsv02_results = [r for r in results if r.rule_id == "FSV-02"]
        epub_results = [r for r in fsv02_results if "epub" in r.detail]
        if epub_results:
            assert not epub_results[0].passed, "epub.yml has discovery_blocked which is not in schema enum"
