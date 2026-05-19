"""Tests for the example completion queue (REM-013 / B-009).

Verifies:
- Queue file exists and parses as valid JSON
- Queue covers all runnable scenarios from denominator model
- All MERGED entries have merge_sha
- State machine states are valid
- POST_MERGE_VERIFIED count matches denominator published counts
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_QUEUE_PATH = _REPO_ROOT / "workspace" / "queues" / "example-completion-queue.json"
_DENOMINATOR_DIR = _REPO_ROOT / "pipeline" / "configs" / "denominators"

_VALID_STATES = {
    "DISCOVERED", "CONTRACTED", "FIXTURE_READY", "GENERATION_READY",
    "GENERATED", "BUILT", "RAN", "REVIEWED", "PR_READY", "PR_OPEN",
    "MERGED", "POST_MERGE_VERIFIED", "BACKLOGGED", "BLOCKED",
    "PERMANENTLY_BLOCKED",
}


@pytest.fixture(scope="module")
def queue() -> dict:
    assert _QUEUE_PATH.exists(), f"Completion queue missing: {_QUEUE_PATH}"
    return json.loads(_QUEUE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def entries(queue) -> list[dict]:
    return queue.get("entries", [])


@pytest.fixture(scope="module")
def denominator(family: str) -> dict:
    path = _DENOMINATOR_DIR / f"{family}.json"
    assert path.exists(), f"Denominator missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


class TestQueueFileIntegrity:
    def test_queue_file_exists(self):
        assert _QUEUE_PATH.exists()

    def test_queue_parses_as_json(self):
        data = json.loads(_QUEUE_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_queue_has_entries(self, queue):
        assert "entries" in queue
        assert len(queue["entries"]) > 0

    def test_queue_has_total_entries(self, queue):
        assert "total_entries" in queue
        assert queue["total_entries"] == len(queue["entries"])

    def test_queue_has_state_summary(self, queue):
        assert "state_summary" in queue
        assert isinstance(queue["state_summary"], dict)

    def test_all_entries_have_required_fields(self, entries):
        required = {"scenario_id", "family", "type_name", "state"}
        for entry in entries:
            for field in required:
                assert field in entry, f"Entry {entry.get('scenario_id','?')} missing field: {field}"

    def test_all_states_are_valid(self, entries):
        for entry in entries:
            assert entry["state"] in _VALID_STATES, (
                f"Entry {entry['scenario_id']} has invalid state: {entry['state']}"
            )

    def test_scenario_ids_are_unique(self, entries):
        ids = [e["scenario_id"] for e in entries]
        assert len(ids) == len(set(ids)), f"Duplicate scenario IDs: {set(x for x in ids if ids.count(x)>1)}"

    def test_families_are_valid(self, entries):
        for entry in entries:
            assert entry["family"] in ("cells", "words", "pdf", "diagram", "email", "slides"), (
                f"Entry {entry['scenario_id']} has invalid family: {entry['family']}"
            )


class TestQueueCoversDenominator:
    def _load_denom(self, family: str) -> dict:
        path = _DENOMINATOR_DIR / f"{family}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_cells_runnable_all_in_queue(self, entries):
        denom = self._load_denom("cells")
        runnable = set(denom.get("runnable_scenario_ids", []))
        queue_ids = {e["scenario_id"] for e in entries if e["family"] == "cells"}
        missing = runnable - queue_ids
        assert len(missing) == 0, f"Cells runnable scenarios missing from queue: {missing}"

    def test_words_pilot_published_in_queue_as_post_merge_verified(self, entries):
        denom = self._load_denom("words")
        # Words pilot published entries must all be POST_MERGE_VERIFIED
        words_verified = [
            e for e in entries
            if e["family"] == "words" and e["state"] == "POST_MERGE_VERIFIED"
        ]
        assert len(words_verified) == denom["published_count"], (
            f"Words POST_MERGE_VERIFIED count ({len(words_verified)}) != "
            f"published_count ({denom['published_count']})"
        )

    def test_pdf_pilot_active_pipeline_in_queue(self, entries):
        denom = self._load_denom("pdf")
        # Active PDF entries (not BACKLOGGED or PERMANENTLY_BLOCKED)
        # should match published + pr_dry_run_ready + reviewer_passed
        _inactive = {"BACKLOGGED", "PERMANENTLY_BLOCKED"}
        queue_pdf_active = [
            e for e in entries
            if e["family"] == "pdf" and e["state"] not in _inactive
        ]
        pipeline_count = (
            denom.get("published_count", 0) +
            denom.get("pr_dry_run_ready_count", 0) +
            denom.get("reviewer_passed_awaiting_pr_count", 0)
        )
        assert len(queue_pdf_active) == pipeline_count, (
            f"PDF active queue entries ({len(queue_pdf_active)}) != pipeline scenarios ({pipeline_count})"
        )

    def test_active_pipeline_entries_match_denominator(self, entries):
        # Active (non-BACKLOGGED) entries across all families with denominators
        expected_active = 0
        for family in ("cells", "words", "pdf", "diagram", "email", "slides"):
            denom_path = _DENOMINATOR_DIR / f"{family}.json"
            if not denom_path.exists():
                continue
            denom = json.loads(denom_path.read_text(encoding="utf-8"))
            expected_active += (
                denom.get("published_count", 0) +
                denom.get("pr_ready_count", 0) +
                denom.get("pr_dry_run_ready_count", 0) +
                denom.get("reviewer_passed_awaiting_pr_count", 0)
            )
        active_entries = [
            e for e in entries
            if e["state"] not in ("BACKLOGGED", "PERMANENTLY_BLOCKED")
        ]
        assert len(active_entries) == expected_active, (
            f"Active pipeline entries ({len(active_entries)}) != expected ({expected_active})"
        )

    def test_total_queue_covers_active_plus_backlogged(self, entries):
        # Total queue = active + backlogged + permanently_blocked entries
        active = [e for e in entries if e["state"] not in ("BACKLOGGED", "PERMANENTLY_BLOCKED")]
        backlogged = [e for e in entries if e["state"] == "BACKLOGGED"]
        permanently_blocked = [e for e in entries if e["state"] == "PERMANENTLY_BLOCKED"]
        # At minimum: 42 active (cells 9 + words 8 + pdf 19 merged + diagram 2 + email 1 + slides 3)
        # + 5 backlogged (PDF deferred types: FormImporter, Ofd, PdfAValidator, FormFieldSelector, Timestamp)
        # + 4 permanently blocked (Processor: API_ACCESS_PARADOX, PdfExtractor: ABSTRACT_BASE,
        #   words-splitter-split-criteria: ENUM, PdfToImage: ABSTRACT_BASE)
        # All 19 PDF active types now have contracts and are MERGED.
        assert len(active) >= 42, f"Expected at least 42 active entries, got {len(active)}"
        assert len(backlogged) >= 5, f"Expected at least 5 backlogged entries, got {len(backlogged)}"
        assert len(permanently_blocked) >= 4, "Expected at least 4 PERMANENTLY_BLOCKED entries (Processor, PdfExtractor, SplitCriteria, PdfToImage)"
        assert len(entries) == len(active) + len(backlogged) + len(permanently_blocked)


class TestQueueStateConsistency:
    def test_merged_entries_have_merge_sha(self, entries):
        for entry in entries:
            if entry["state"] in ("MERGED", "POST_MERGE_VERIFIED"):
                assert entry.get("merge_sha") is not None, (
                    f"Entry {entry['scenario_id']} is {entry['state']} but has no merge_sha"
                )

    def test_post_merge_verified_entries_have_post_merge_validation(self, entries):
        for entry in entries:
            if entry["state"] == "POST_MERGE_VERIFIED":
                assert entry.get("post_merge_validation") == "ALL_PASS", (
                    f"Entry {entry['scenario_id']} is POST_MERGE_VERIFIED but post_merge_validation="
                    f"{entry.get('post_merge_validation')}"
                )

    def test_cells_all_post_merge_verified(self, entries):
        cells = [e for e in entries if e["family"] == "cells"]
        for entry in cells:
            assert entry["state"] == "POST_MERGE_VERIFIED", (
                f"Cells entry {entry['scenario_id']} is not POST_MERGE_VERIFIED: {entry['state']}"
            )

    def test_words_pilot_entries_post_merge_verified(self, entries):
        # Words entries may be POST_MERGE_VERIFIED (Wave 1 published), PR_READY (Wave 2 pending pub),
        # REVIEWED, BACKLOGGED (deferred/config-ready), or PERMANENTLY_BLOCKED (unreachable API)
        valid_states = ("POST_MERGE_VERIFIED", "PR_READY", "REVIEWED", "BACKLOGGED", "PERMANENTLY_BLOCKED")
        words = [e for e in entries if e["family"] == "words"]
        for entry in words:
            assert entry["state"] in valid_states, (
                f"Words entry {entry['scenario_id']} has unexpected state: {entry['state']} "
                f"(expected one of {valid_states})"
            )
        # The 4 Wave 1 pilot types specifically must be POST_MERGE_VERIFIED
        pilot_ids = {"words-converter", "words-replacer", "words-splitter", "words-watermarker"}
        queue_dict = {e["scenario_id"]: e for e in words}
        for sid in pilot_ids:
            assert sid in queue_dict, f"Words pilot entry {sid} missing from queue"
            assert queue_dict[sid]["state"] == "POST_MERGE_VERIFIED", (
                f"Words Wave 1 entry {sid} expected POST_MERGE_VERIFIED, got {queue_dict[sid]['state']}"
            )

    def test_pdf_merger_and_text_extractor_are_post_merge_verified(self, entries):
        queue_dict = {e["scenario_id"]: e for e in entries}
        for sid in ("pdf-merger", "pdf-text-extractor"):
            assert queue_dict[sid]["state"] == "POST_MERGE_VERIFIED", (
                f"{sid} expected POST_MERGE_VERIFIED, got {queue_dict[sid]['state']}"
            )

    def test_pdf_splitter_is_post_merge_verified(self, entries):
        queue_dict = {e["scenario_id"]: e for e in entries}
        assert queue_dict["pdf-splitter"]["state"] == "POST_MERGE_VERIFIED"

    def test_pdf_optimizer_is_reviewed(self, entries):
        queue_dict = {e["scenario_id"]: e for e in entries}
        assert queue_dict["pdf-optimizer"]["state"] == "POST_MERGE_VERIFIED"

    def test_state_summary_counts_match_entries(self, queue, entries):
        actual_counts: dict[str, int] = {}
        for entry in entries:
            state = entry["state"]
            actual_counts[state] = actual_counts.get(state, 0) + 1
        summary = queue.get("state_summary", {})
        for state, count in summary.items():
            assert actual_counts.get(state, 0) == count, (
                f"State summary mismatch for {state}: summary says {count}, "
                f"actual entries say {actual_counts.get(state, 0)}"
            )


class TestBackloggedEntries:
    """Verify deferred/backlogged entries have proper governance fields (R6.5 audit)."""

    def test_backlogged_entries_have_blocking_reason(self, entries):
        for entry in entries:
            if entry["state"] == "BACKLOGGED":
                assert entry.get("blocking_reason"), (
                    f"BACKLOGGED entry {entry['scenario_id']} missing blocking_reason"
                )

    def test_backlogged_entries_have_blocking_taskcard(self, entries):
        for entry in entries:
            if entry["state"] == "BACKLOGGED":
                reason = entry.get("blocking_reason") or ""
                # Non-runnable OPTIONS/RESULT/CALLBACK types don't need taskcards
                is_non_runnable = reason.startswith("OPTIONS_CLASS:") or \
                    reason.startswith("NON_RUNNABLE:")
                if not is_non_runnable:
                    assert entry.get("blocking_taskcard"), (
                        f"BACKLOGGED entry {entry['scenario_id']} missing blocking_taskcard"
                    )

    def test_pdf_deferred_workflow_roots_in_queue(self, entries):
        # 21 PDF WORKFLOW_ROOT types deferred from pilot scope must be in queue
        expected_deferred = {
            "pdf-doc-converter", "pdf-form-editor", "pdf-form-exporter", "pdf-form-flattener",
            "pdf-form-importer", "pdf-html", "pdf-image-extractor", "pdf-jpeg", "pdf-ofd",
            "pdf-pdf-a-converter", "pdf-pdf-extractor", "pdf-pdf-to-image", "pdf-png",
            "pdf-security", "pdf-select-field", "pdf-signature", "pdf-table-generator",
            "pdf-tiff", "pdf-timestamp", "pdf-toc-generator", "pdf-xls-converter",
        }
        queue_ids = {e["scenario_id"] for e in entries}
        missing = expected_deferred - queue_ids
        assert len(missing) == 0, f"PDF deferred WORKFLOW_ROOT types missing from queue: {missing}"

    def test_words_deferred_scenarios_in_queue(self, entries):
        # 5 Words deferred scenarios must be in queue as BACKLOGGED
        expected_deferred = {
            "words-comparer", "words-merger", "words-mail-merger",
            "words-splitter-split", "words-report-builder",
        }
        queue_ids = {e["scenario_id"] for e in entries}
        missing = expected_deferred - queue_ids
        assert len(missing) == 0, f"Words deferred scenarios missing from queue: {missing}"

    def test_backlogged_pdf_entries_are_not_published(self, entries):
        # No BACKLOGGED PDF entry should have a merge_sha or post_merge_validation
        for entry in entries:
            if entry["family"] == "pdf" and entry["state"] == "BACKLOGGED":
                assert entry.get("merge_sha") is None, (
                    f"BACKLOGGED PDF entry {entry['scenario_id']} has merge_sha (should be None)"
                )
                assert entry.get("post_merge_validation") is None, (
                    f"BACKLOGGED PDF entry {entry['scenario_id']} has post_merge_validation (should be None)"
                )

    def test_backlogged_words_entries_are_not_published(self, entries):
        # No BACKLOGGED Words entry should have a merge_sha
        for entry in entries:
            if entry["family"] == "words" and entry["state"] == "BACKLOGGED":
                assert entry.get("merge_sha") is None, (
                    f"BACKLOGGED Words entry {entry['scenario_id']} has merge_sha (should be None)"
                )
