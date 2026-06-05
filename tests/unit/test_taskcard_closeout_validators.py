"""
Tests for TCC and BMV validators (taskcard closeout consistency + bundle metadata verification).
Covers TCC-01..TCC-06 (6 rules, 4 tests each = 24) + BMV-01..BMV-05 (5 rules, 4 tests each = 20)
= 44 tests total + 2 aggregate tests = 46 tests.
"""
import pytest
from src.plugin_examples.fixture_factory.taskcard_closeout_validators import (
    tcc_01_no_pending_taskcards,
    tcc_02_all_taskcards_have_evidence,
    tcc_03_taskcard_count_matches_lanes,
    tcc_04_no_duplicate_taskcard_ids,
    tcc_05_taskcards_before_closeout,
    tcc_06_closeout_verdict_matches_taskcard_completion,
    bmv_01_bundle_sha_not_pending,
    bmv_02_commit_sha_not_pending,
    bmv_03_bundle_entry_count_positive,
    bmv_04_bundle_size_positive,
    bmv_05_pytest_passed_count_positive,
    run_all_tcc_validators,
    run_all_bmv_validators,
)


# ---- Fixtures ----------------------------------------------------------------

def _make_taskcards(count: int, status: str = "COMPLETE", evidence: str = "some evidence") -> list[dict]:
    return [{"id": f"TC-{i:02d}", "lane": str(i % 3), "status": status, "evidence": evidence}
            for i in range(count)]


GOOD_CLOSEOUT = {
    "sprint": "test-sprint",
    "verdict": "SPRINT_COMPLETE",
    "commit_sha": "abc123def456abc1",
    "pytest_passed": 3586,
    "pytest_failed": 0,
    "pytest_skipped": 18,
    "evidence_bundle": {
        "sha256": "a" * 64,
        "size_bytes": 101262,
        "entries": 130,
        "path": ".local/evidence-bundles/test.zip",
    },
}


# ---- TCC-01 ------------------------------------------------------------------

class TestTCC01:
    def test_pass_all_complete(self):
        tcs = _make_taskcards(5)
        result = tcc_01_no_pending_taskcards(tcs)
        assert result["status"] == "PASS"

    def test_fail_one_pending(self):
        tcs = _make_taskcards(4)
        tcs.append({"id": "TC-X", "lane": "J", "status": "PENDING", "evidence": None})
        result = tcc_01_no_pending_taskcards(tcs)
        assert result["status"] == "FAIL"
        assert "TC-X" in result["message"]

    def test_fail_all_pending(self):
        tcs = _make_taskcards(10, status="PENDING")
        result = tcc_01_no_pending_taskcards(tcs)
        assert result["status"] == "FAIL"

    def test_pass_empty_list(self):
        # Empty list — no PENDING taskcards
        result = tcc_01_no_pending_taskcards([])
        assert result["status"] == "PASS"


# ---- TCC-02 ------------------------------------------------------------------

class TestTCC02:
    def test_pass_all_have_evidence(self):
        tcs = _make_taskcards(5, evidence="coordinator/lane-ledger.json")
        result = tcc_02_all_taskcards_have_evidence(tcs)
        assert result["status"] == "PASS"

    def test_fail_missing_evidence(self):
        tcs = _make_taskcards(3)
        tcs.append({"id": "TC-X", "lane": "A", "status": "COMPLETE", "evidence": None})
        result = tcc_02_all_taskcards_have_evidence(tcs)
        assert result["status"] == "FAIL"
        assert "TC-X" in result["message"]

    def test_fail_empty_evidence(self):
        tcs = [{"id": "TC-01", "lane": "A", "status": "COMPLETE", "evidence": ""}]
        result = tcc_02_all_taskcards_have_evidence(tcs)
        assert result["status"] == "FAIL"

    def test_pass_skips_pending(self):
        # PENDING taskcards are allowed to have no evidence — TCC-02 only checks COMPLETE
        tcs = [{"id": "TC-01", "lane": "A", "status": "PENDING", "evidence": None}]
        result = tcc_02_all_taskcards_have_evidence(tcs)
        assert result["status"] == "PASS"


# ---- TCC-03 ------------------------------------------------------------------

class TestTCC03:
    def test_pass_all_lanes_covered(self):
        tcs = [{"id": f"TC-{i}", "lane": str(i), "status": "COMPLETE"} for i in range(5)]
        result = tcc_03_taskcard_count_matches_lanes(tcs, expected_lane_count=5)
        assert result["status"] == "PASS"

    def test_fail_insufficient_lanes(self):
        tcs = [{"id": f"TC-{i}", "lane": "0", "status": "COMPLETE"} for i in range(5)]
        result = tcc_03_taskcard_count_matches_lanes(tcs, expected_lane_count=5)
        assert result["status"] == "FAIL"  # only 1 unique lane, need 5

    def test_pass_more_lanes_than_required(self):
        tcs = [{"id": f"TC-{i}", "lane": str(i), "status": "COMPLETE"} for i in range(12)]
        result = tcc_03_taskcard_count_matches_lanes(tcs, expected_lane_count=5)
        assert result["status"] == "PASS"

    def test_fail_zero_taskcards_nonzero_lanes(self):
        result = tcc_03_taskcard_count_matches_lanes([], expected_lane_count=3)
        assert result["status"] == "FAIL"


# ---- TCC-04 ------------------------------------------------------------------

class TestTCC04:
    def test_pass_unique_ids(self):
        tcs = _make_taskcards(10)
        result = tcc_04_no_duplicate_taskcard_ids(tcs)
        assert result["status"] == "PASS"

    def test_fail_duplicate_id(self):
        tcs = _make_taskcards(5)
        tcs.append({"id": "TC-02", "lane": "X", "status": "COMPLETE"})
        result = tcc_04_no_duplicate_taskcard_ids(tcs)
        assert result["status"] == "FAIL"
        assert "TC-02" in result["message"]

    def test_fail_multiple_duplicates(self):
        tcs = [{"id": "TC-01"}, {"id": "TC-01"}, {"id": "TC-02"}, {"id": "TC-02"}]
        result = tcc_04_no_duplicate_taskcard_ids(tcs)
        assert result["status"] == "FAIL"

    def test_pass_empty(self):
        result = tcc_04_no_duplicate_taskcard_ids([])
        assert result["status"] == "PASS"


# ---- TCC-05 ------------------------------------------------------------------

class TestTCC05:
    def test_pass_taskcards_present(self):
        tcs = _make_taskcards(5)
        result = tcc_05_taskcards_before_closeout(tcs, "2026-06-06")
        assert result["status"] == "PASS"

    def test_fail_no_taskcards(self):
        result = tcc_05_taskcards_before_closeout([], "2026-06-06")
        assert result["status"] == "FAIL"

    def test_pass_single_taskcard(self):
        result = tcc_05_taskcards_before_closeout([{"id": "TC-01"}], "2026-06-06")
        assert result["status"] == "PASS"

    def test_pass_many_taskcards(self):
        result = tcc_05_taskcards_before_closeout(_make_taskcards(50), "2026-06-06")
        assert result["status"] == "PASS"


# ---- TCC-06 ------------------------------------------------------------------

class TestTCC06:
    def test_pass_complete_verdict_all_complete(self):
        tcs = _make_taskcards(10)
        result = tcc_06_closeout_verdict_matches_taskcard_completion(tcs, "SPRINT_COMPLETE")
        assert result["status"] == "PASS"

    def test_fail_complete_verdict_pending_tasks(self):
        tcs = _make_taskcards(9)
        tcs.append({"id": "TC-X", "status": "PENDING"})
        result = tcc_06_closeout_verdict_matches_taskcard_completion(tcs, "SPRINT_COMPLETE")
        assert result["status"] == "FAIL"
        assert "TC-X" in result["message"]

    def test_pass_non_complete_verdict_ignores_pending(self):
        tcs = _make_taskcards(5, status="PENDING")
        result = tcc_06_closeout_verdict_matches_taskcard_completion(tcs, "IN_PROGRESS")
        assert result["status"] == "PASS"

    def test_pass_partial_complete_verdict_non_sprint(self):
        tcs = [{"id": "TC-01", "status": "PENDING"}]
        result = tcc_06_closeout_verdict_matches_taskcard_completion(tcs, "COORDINATOR_COMPLETE")
        assert result["status"] == "PASS"


# ---- BMV-01 ------------------------------------------------------------------

class TestBMV01:
    def test_pass_valid_sha(self):
        result = bmv_01_bundle_sha_not_pending(GOOD_CLOSEOUT)
        assert result["status"] == "PASS"

    def test_fail_pending_sha(self):
        closeout = {**GOOD_CLOSEOUT, "evidence_bundle": {"sha256": "PENDING", "size_bytes": 100, "entries": 10}}
        result = bmv_01_bundle_sha_not_pending(closeout)
        assert result["status"] == "FAIL"

    def test_fail_empty_sha(self):
        closeout = {**GOOD_CLOSEOUT, "evidence_bundle": {"sha256": "", "size_bytes": 100, "entries": 10}}
        result = bmv_01_bundle_sha_not_pending(closeout)
        assert result["status"] == "FAIL"

    def test_fail_wrong_length(self):
        closeout = {**GOOD_CLOSEOUT, "evidence_bundle": {"sha256": "abc123", "size_bytes": 100, "entries": 10}}
        result = bmv_01_bundle_sha_not_pending(closeout)
        assert result["status"] == "FAIL"


# ---- BMV-02 ------------------------------------------------------------------

class TestBMV02:
    def test_pass_valid_commit(self):
        result = bmv_02_commit_sha_not_pending(GOOD_CLOSEOUT)
        assert result["status"] == "PASS"

    def test_fail_pending(self):
        closeout = {**GOOD_CLOSEOUT, "commit_sha": "PENDING"}
        result = bmv_02_commit_sha_not_pending(closeout)
        assert result["status"] == "FAIL"

    def test_fail_empty(self):
        closeout = {**GOOD_CLOSEOUT, "commit_sha": ""}
        result = bmv_02_commit_sha_not_pending(closeout)
        assert result["status"] == "FAIL"

    def test_fail_missing_key(self):
        closeout = {k: v for k, v in GOOD_CLOSEOUT.items() if k != "commit_sha"}
        result = bmv_02_commit_sha_not_pending(closeout)
        assert result["status"] == "FAIL"


# ---- BMV-03 ------------------------------------------------------------------

class TestBMV03:
    def test_pass_positive_count(self):
        result = bmv_03_bundle_entry_count_positive(GOOD_CLOSEOUT)
        assert result["status"] == "PASS"

    def test_fail_zero(self):
        closeout = {**GOOD_CLOSEOUT, "evidence_bundle": {**GOOD_CLOSEOUT["evidence_bundle"], "entries": 0}}
        result = bmv_03_bundle_entry_count_positive(closeout)
        assert result["status"] == "FAIL"

    def test_fail_missing(self):
        closeout = {k: v for k, v in GOOD_CLOSEOUT.items() if k != "evidence_bundle"}
        result = bmv_03_bundle_entry_count_positive(closeout)
        assert result["status"] == "FAIL"

    def test_fail_negative(self):
        closeout = {**GOOD_CLOSEOUT, "evidence_bundle": {**GOOD_CLOSEOUT["evidence_bundle"], "entries": -1}}
        result = bmv_03_bundle_entry_count_positive(closeout)
        assert result["status"] == "FAIL"


# ---- BMV-04 ------------------------------------------------------------------

class TestBMV04:
    def test_pass_positive_size(self):
        result = bmv_04_bundle_size_positive(GOOD_CLOSEOUT)
        assert result["status"] == "PASS"

    def test_fail_zero_size(self):
        closeout = {**GOOD_CLOSEOUT, "evidence_bundle": {**GOOD_CLOSEOUT["evidence_bundle"], "size_bytes": 0}}
        result = bmv_04_bundle_size_positive(closeout)
        assert result["status"] == "FAIL"

    def test_fail_missing(self):
        result = bmv_04_bundle_size_positive({})
        assert result["status"] == "FAIL"

    def test_fail_negative(self):
        closeout = {**GOOD_CLOSEOUT, "evidence_bundle": {**GOOD_CLOSEOUT["evidence_bundle"], "size_bytes": -100}}
        result = bmv_04_bundle_size_positive(closeout)
        assert result["status"] == "FAIL"


# ---- BMV-05 ------------------------------------------------------------------

class TestBMV05:
    def test_pass_good_counts(self):
        result = bmv_05_pytest_passed_count_positive(GOOD_CLOSEOUT)
        assert result["status"] == "PASS"

    def test_fail_zero_passed(self):
        closeout = {**GOOD_CLOSEOUT, "pytest_passed": 0}
        result = bmv_05_pytest_passed_count_positive(closeout)
        assert result["status"] == "FAIL"

    def test_fail_nonzero_failed(self):
        closeout = {**GOOD_CLOSEOUT, "pytest_failed": 5}
        result = bmv_05_pytest_passed_count_positive(closeout)
        assert result["status"] == "FAIL"

    def test_fail_missing_counts(self):
        result = bmv_05_pytest_passed_count_positive({})
        assert result["status"] == "FAIL"


# ---- Aggregate TCC -----------------------------------------------------------

class TestRunAllTCC:
    def test_pass_all_conditions_met(self):
        tcs = _make_taskcards(12, evidence="some evidence")
        # Give each a unique lane
        for i, tc in enumerate(tcs):
            tc["lane"] = str(i % 6)
        result = run_all_tcc_validators(tcs, expected_lane_count=6, closeout_date="2026-06-06", closeout_verdict="SPRINT_COMPLETE")
        assert result["verdict"] == "ALL_PASS"
        assert result["fail"] == 0

    def test_fail_pending_taskcards(self):
        tcs = _make_taskcards(5, status="PENDING")
        result = run_all_tcc_validators(tcs, expected_lane_count=1, closeout_date="2026-06-06", closeout_verdict="SPRINT_COMPLETE")
        assert result["verdict"] == "FAIL"
        assert result["fail"] > 0


# ---- Aggregate BMV -----------------------------------------------------------

class TestRunAllBMV:
    def test_pass_all_conditions_met(self):
        result = run_all_bmv_validators(GOOD_CLOSEOUT)
        assert result["verdict"] == "ALL_PASS"
        assert result["fail"] == 0

    def test_fail_pending_sha(self):
        closeout = {**GOOD_CLOSEOUT, "evidence_bundle": {"sha256": "PENDING", "size_bytes": 0, "entries": 0}}
        result = run_all_bmv_validators(closeout)
        assert result["verdict"] == "FAIL"
        assert result["fail"] > 0
