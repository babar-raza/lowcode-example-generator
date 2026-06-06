"""
Tests for PRV-01..PRV-04 publication readiness validators.
"""
import pytest
from src.plugin_examples.fixture_factory.publication_readiness_validators import (
    prv_01_all_pclc_have_pr_packet,
    prv_02_all_pr_branches_match_pattern,
    prv_03_no_duplicate_pr_branches,
    prv_04_pclc_total_matches_packages_length,
    run_all_prv,
)


def _make_readiness(pclc_total: int, packages: list[dict]) -> dict:
    return {"pclc_total": pclc_total, "packages": packages}


def _pkg(family: str, slug: str, pr_packet: bool = True) -> dict:
    return {
        "family": family,
        "slug": slug,
        "pr_packet_exists": pr_packet,
        "pr_branch": f"lowcode/{family}/{slug}",
    }


# --- PRV-01 ---

class TestPRV01:
    def test_pass_all_have_pr_packet(self):
        r = _make_readiness(2, [_pkg("ocr", "scanned-image-to-text"), _pkg("page", "xps-converter")])
        result = prv_01_all_pclc_have_pr_packet(r)
        assert result.passed
        assert result.rule_id == "PRV-01"

    def test_fail_one_missing_pr_packet(self):
        r = _make_readiness(2, [_pkg("ocr", "scanned-image-to-text"), _pkg("html", "convert-html-to-xps", pr_packet=False)])
        result = prv_01_all_pclc_have_pr_packet(r)
        assert not result.passed
        assert "html/convert-html-to-xps" in result.detail

    def test_fail_all_missing(self):
        r = _make_readiness(2, [_pkg("a", "b", pr_packet=False), _pkg("c", "d", pr_packet=False)])
        result = prv_01_all_pclc_have_pr_packet(r)
        assert not result.passed

    def test_pass_empty_readiness(self):
        r = _make_readiness(0, [])
        result = prv_01_all_pclc_have_pr_packet(r)
        assert result.passed

    def test_regression_w16_16_pclc_missing_2_packets(self):
        """Regression: the W16 unified-16-pclc-readiness.json had 2 entries with pr_packet_exists=false."""
        packages = [_pkg(f"fam{i}", f"slug{i}") for i in range(14)]
        packages.append(_pkg("html", "convert-html-to-xps", pr_packet=False))
        packages.append(_pkg("psd", "convert-psd-to-png", pr_packet=False))
        r = _make_readiness(16, packages)
        result = prv_01_all_pclc_have_pr_packet(r)
        assert not result.passed
        assert "html/convert-html-to-xps" in result.detail
        assert "psd/convert-psd-to-png" in result.detail


# --- PRV-02 ---

class TestPRV02:
    def test_pass_valid_branches(self):
        r = _make_readiness(2, [_pkg("ocr", "scanned-image-to-text"), _pkg("gis", "read-gis-data")])
        result = prv_02_all_pr_branches_match_pattern(r)
        assert result.passed

    def test_fail_invalid_branch(self):
        packages = [{"family": "ocr", "slug": "x", "pr_packet_exists": True, "pr_branch": "feature/ocr/x"}]
        r = _make_readiness(1, packages)
        result = prv_02_all_pr_branches_match_pattern(r)
        assert not result.passed
        assert "feature/ocr/x" in result.detail

    def test_pass_no_pr_branch_field(self):
        """Packages without pr_branch field should be skipped gracefully."""
        packages = [{"family": "ocr", "slug": "x", "pr_packet_exists": True}]
        r = _make_readiness(1, packages)
        result = prv_02_all_pr_branches_match_pattern(r)
        assert result.passed

    def test_fail_branch_with_uppercase(self):
        packages = [{"family": "OCR", "slug": "x", "pr_packet_exists": True, "pr_branch": "lowcode/OCR/x"}]
        r = _make_readiness(1, packages)
        result = prv_02_all_pr_branches_match_pattern(r)
        assert not result.passed


# --- PRV-03 ---

class TestPRV03:
    def test_pass_no_duplicates(self):
        r = _make_readiness(2, [_pkg("ocr", "a"), _pkg("ocr", "b")])
        result = prv_03_no_duplicate_pr_branches(r)
        assert result.passed

    def test_fail_duplicate_branch(self):
        packages = [
            {"family": "ocr", "slug": "a", "pr_packet_exists": True, "pr_branch": "lowcode/ocr/a"},
            {"family": "ocr", "slug": "a-copy", "pr_packet_exists": True, "pr_branch": "lowcode/ocr/a"},
        ]
        r = _make_readiness(2, packages)
        result = prv_03_no_duplicate_pr_branches(r)
        assert not result.passed
        assert "lowcode/ocr/a" in result.detail

    def test_pass_empty_list(self):
        result = prv_03_no_duplicate_pr_branches({"pclc_total": 0, "packages": []})
        assert result.passed


# --- PRV-04 ---

class TestPRV04:
    def test_pass_count_matches(self):
        r = _make_readiness(3, [_pkg("a", "b"), _pkg("c", "d"), _pkg("e", "f")])
        result = prv_04_pclc_total_matches_packages_length(r)
        assert result.passed

    def test_fail_undercounted(self):
        r = _make_readiness(5, [_pkg("a", "b"), _pkg("c", "d")])
        result = prv_04_pclc_total_matches_packages_length(r)
        assert not result.passed
        assert "5" in result.detail
        assert "2" in result.detail

    def test_fail_overcounted(self):
        r = _make_readiness(1, [_pkg("a", "b"), _pkg("c", "d")])
        result = prv_04_pclc_total_matches_packages_length(r)
        assert not result.passed

    def test_fail_missing_field(self):
        r = {"packages": [_pkg("a", "b")]}
        result = prv_04_pclc_total_matches_packages_length(r)
        assert not result.passed
        assert "missing" in result.detail.lower()

    def test_pass_zero_pclc(self):
        r = _make_readiness(0, [])
        result = prv_04_pclc_total_matches_packages_length(r)
        assert result.passed

    def test_regression_w16_20_pclc(self):
        """Regression: unified-20-pclc-readiness.json must have 20 entries."""
        packages = [_pkg(f"fam{i}", f"slug{i}") for i in range(20)]
        r = _make_readiness(20, packages)
        result = prv_04_pclc_total_matches_packages_length(r)
        assert result.passed


# --- run_all_prv ---

class TestRunAllPRV:
    def test_all_pass(self):
        r = _make_readiness(3, [_pkg("ocr", "a"), _pkg("page", "b"), _pkg("gis", "c")])
        results = run_all_prv(r)
        assert len(results) == 4
        assert all(r.passed for r in results)

    def test_mixed_results(self):
        packages = [
            _pkg("ocr", "a"),
            _pkg("html", "b", pr_packet=False),
        ]
        r = _make_readiness(3, packages)  # wrong total
        results = run_all_prv(r)
        failures = [r for r in results if not r.passed]
        assert len(failures) >= 2  # PRV-01 (missing packet) + PRV-04 (count mismatch)

    def test_returns_four_results(self):
        r = _make_readiness(0, [])
        results = run_all_prv(r)
        assert len(results) == 4
        rule_ids = {r.rule_id for r in results}
        assert rule_ids == {"PRV-01", "PRV-02", "PRV-03", "PRV-04"}
