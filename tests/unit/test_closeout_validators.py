"""Unit tests for closeout consistency validators."""
import json
import tempfile
from pathlib import Path

import pytest

from plugin_examples.fixture_factory.closeout_validators import (
    check_build_results_no_stale_errors,
    check_build_results_vs_invariants,
    check_cumulative_ledger_count,
    check_no_duplicate_package_keys,
    run_all_consistency_checks,
)


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


class TestBuildResultsNoStaleErrors:
    def test_clean_results(self, tmpdir):
        data = {"results": [{"key": "a/b", "verdict": "PASS"}]}
        f = tmpdir / "results.json"
        f.write_text(json.dumps(data))
        assert check_build_results_no_stale_errors(f) == []

    def test_pass_with_no_error_snippet(self, tmpdir):
        data = {"results": [{"key": "a/b", "verdict": "PASS", "fix_note": "ok"}]}
        f = tmpdir / "results.json"
        f.write_text(json.dumps(data))
        assert check_build_results_no_stale_errors(f) == []

    def test_pass_with_stale_build_failed_snippet(self, tmpdir):
        data = {"results": [
            {"key": "a/b", "verdict": "PASS", "error_snippet": "Build FAILED.\n1 Error(s)"}
        ]}
        f = tmpdir / "results.json"
        f.write_text(json.dumps(data))
        violations = check_build_results_no_stale_errors(f)
        assert any("CV-02" in v.rule_id for v in violations)

    def test_missing_file(self, tmpdir):
        violations = check_build_results_no_stale_errors(tmpdir / "missing.json")
        assert violations == []


class TestBuildResultsVsInvariants:
    def test_matching_counts(self, tmpdir):
        build = {"total": 10, "passed": 10, "results": []}
        inv = {"total": 10, "real_violations": 0, "packages": {}}
        bf = tmpdir / "build.json"
        inf = tmpdir / "inv.json"
        bf.write_text(json.dumps(build))
        inf.write_text(json.dumps(inv))
        violations = check_build_results_vs_invariants(bf, inf)
        assert violations == []

    def test_count_mismatch(self, tmpdir):
        build = {"total": 10, "passed": 10, "results": []}
        inv = {"total": 9, "real_violations": 0, "packages": {}}
        bf = tmpdir / "build.json"
        inf = tmpdir / "inv.json"
        bf.write_text(json.dumps(build))
        inf.write_text(json.dumps(inv))
        violations = check_build_results_vs_invariants(bf, inf)
        assert any("CV-01a" in v.rule_id for v in violations)

    def test_all_pass_but_real_violations(self, tmpdir):
        build = {"total": 5, "passed": 5, "results": []}
        inv = {"total": 5, "real_violations": 3, "packages": {}}
        bf = tmpdir / "build.json"
        inf = tmpdir / "inv.json"
        bf.write_text(json.dumps(build))
        inf.write_text(json.dumps(inv))
        violations = check_build_results_vs_invariants(bf, inf)
        assert any("CV-01b" in v.rule_id for v in violations)


class TestCumulativeLedgerCount:
    def test_matching_counts(self, tmpdir):
        ledger = {
            "total_dryrun_packages": 5,
            "packages_by_wave": {
                "wave-1": ["a/b", "c/d"],
                "wave-2": ["e/f", "g/h", "i/j"],
            }
        }
        f = tmpdir / "ledger.json"
        f.write_text(json.dumps(ledger))
        violations = check_cumulative_ledger_count(f, expected_transformed=5)
        assert violations == []

    def test_count_mismatch(self, tmpdir):
        ledger = {
            "total_dryrun_packages": 10,
            "packages_by_wave": {"wave-1": ["a/b", "c/d"]}
        }
        f = tmpdir / "ledger.json"
        f.write_text(json.dumps(ledger))
        violations = check_cumulative_ledger_count(f, expected_transformed=2)
        assert any("CV-04a" in v.rule_id for v in violations)


class TestNoDuplicatePackageKeys:
    def test_no_duplicates(self, tmpdir):
        ledger = {"packages_by_wave": {"w1": ["a/b", "c/d"], "w2": ["e/f"]}}
        f = tmpdir / "ledger.json"
        f.write_text(json.dumps(ledger))
        assert check_no_duplicate_package_keys(f) == []

    def test_with_duplicate(self, tmpdir):
        ledger = {"packages_by_wave": {"w1": ["a/b", "c/d"], "w2": ["a/b", "e/f"]}}
        f = tmpdir / "ledger.json"
        f.write_text(json.dumps(ledger))
        violations = check_no_duplicate_package_keys(f)
        assert any("CV-05" in v.rule_id for v in violations)
