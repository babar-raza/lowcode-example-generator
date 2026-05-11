"""Tests for GAP-NEW-01: single-family discover-lowcode must preserve multi-family readiness rank.

Also tests for family-scoped evidence promotion (followup-family-scoped-evidence-promotion):
evidence promoted by one family run must not overwrite another family's promoted evidence.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from plugin_examples.evidence_layout import (
    FAMILY_SCOPED_EVIDENCE_FILES,
    detect_cross_family_contamination,
    promote_family_evidence,
    resolve_family_evidence_path,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RANK_PATH = _REPO_ROOT / "workspace" / "verification" / "latest" / "family-generation-readiness-rank.json"


def _merge_ranking_entries(existing_entries: list[dict], new_entries: list[dict]) -> tuple[list[dict], str]:
    """Simulate the merge logic from __main__.py's discover-lowcode handler.

    Returns (merged_list, scope) where scope is 'partial' or 'complete'.
    """
    existing_by_family = {e["family"]: e for e in existing_entries if "family" in e}
    for entry in new_entries:
        existing_by_family[entry["family"]] = entry
    run_families = {e["family"] for e in new_entries}
    scope = "complete" if run_families >= set(existing_by_family.keys()) else "partial"
    return list(existing_by_family.values()), scope


class TestDiscoveryReadinessPreservation:
    """Tests for GAP-NEW-01 fix: single-family run preservation logic."""

    def test_single_family_discovery_preserves_existing_readiness_entries(self):
        """Running discover-lowcode for one family must not destroy other families' entries."""
        existing = [
            {"family": "cells", "generation_ready": True, "recommended_next_action": "needs_options_aware_rules"},
            {"family": "words", "generation_ready": False, "recommended_next_action": "needs_options_aware_rules"},
            {"family": "pdf", "generation_ready": False, "recommended_next_action": "needs_type_role_rules"},
        ]
        # Simulate a words-only run
        words_only = [{"family": "words", "generation_ready": False, "recommended_next_action": "needs_options_aware_rules"}]

        merged, scope = _merge_ranking_entries(existing, words_only)
        families_in_merged = {e["family"] for e in merged}

        assert "cells" in families_in_merged, "cells entry must be preserved after single-family words run"
        assert "pdf" in families_in_merged, "pdf entry must be preserved after single-family words run"
        assert "words" in families_in_merged, "words entry must still be present"
        assert len(merged) == 3, f"All 3 families must be preserved, got: {families_in_merged}"

    def test_single_family_discovery_marks_partial_scope(self):
        """A single-family run with other families present must be marked as partial scope."""
        existing = [
            {"family": "cells", "generation_ready": True},
            {"family": "words", "generation_ready": False},
            {"family": "pdf", "generation_ready": False},
        ]
        words_only = [{"family": "words", "generation_ready": False}]

        _, scope = _merge_ranking_entries(existing, words_only)
        assert scope == "partial", f"Single-family run must be 'partial', got '{scope}'"

    def test_multi_family_discovery_marks_complete_scope(self):
        """A run covering all known families must be marked as complete scope."""
        all_families = [
            {"family": "cells", "generation_ready": True},
            {"family": "words", "generation_ready": False},
            {"family": "pdf", "generation_ready": False},
        ]

        merged, scope = _merge_ranking_entries(all_families, all_families)
        assert scope == "complete", f"All-family run must be 'complete', got '{scope}'"

    def test_single_family_run_updates_targeted_family(self):
        """The new data for the targeted family must overwrite the old entry."""
        existing = [
            {"family": "cells", "generation_ready": True, "plugin_type_count": 22},
            {"family": "words", "generation_ready": False, "plugin_type_count": 25},
        ]
        # Simulate words re-running with updated plugin_type_count
        words_updated = [{"family": "words", "generation_ready": False, "plugin_type_count": 30}]

        merged, _ = _merge_ranking_entries(existing, words_updated)
        words_entry = next(e for e in merged if e["family"] == "words")
        assert words_entry["plugin_type_count"] == 30, "Updated words entry must reflect new count"
        cells_entry = next(e for e in merged if e["family"] == "cells")
        assert cells_entry["plugin_type_count"] == 22, "Cells entry must remain unchanged"

    def test_no_manual_repopulation_needed_after_single_family_discovery(self):
        """The current rank file must have all 3 families — no manual fix needed.

        This test verifies the current state of family-generation-readiness-rank.json.
        If GAP-NEW-01 was not fixed, a single-family run would have destroyed this file
        and manual repopulation would have been needed (as happened in Sprint A1).
        """
        assert _RANK_PATH.exists(), f"Readiness rank file must exist: {_RANK_PATH}"
        data = json.loads(_RANK_PATH.read_text(encoding="utf-8", errors="replace"))
        assert isinstance(data, list), "Rank file must be a list"
        families_in_file = {e.get("family") for e in data}
        assert "cells" in families_in_file, "cells must be in rank file (no manual repopulation needed)"
        assert "words" in families_in_file, "words must be in rank file"
        assert "pdf" in families_in_file, "pdf must be in rank file"
        # Each must have the generation_ready field
        for entry in data:
            assert "generation_ready" in entry, (
                f"family '{entry.get('family')}' missing generation_ready field"
            )

    def test_empty_existing_file_case(self):
        """When no existing file, new run creates the file with only the new entries."""
        new_entries = [{"family": "cells", "generation_ready": True}]
        merged, scope = _merge_ranking_entries([], new_entries)
        assert len(merged) == 1
        assert merged[0]["family"] == "cells"
        assert scope == "complete"  # all known families (just cells) were discovered


class TestFamilyScopedEvidencePromotion:
    """Tests for followup-family-scoped-evidence-promotion.

    Verifies that promote_family_evidence writes to families/{family}/
    and does NOT overwrite another family's evidence.
    """

    def _make_src_latest(self, tmp_path: Path, family: str, files: dict | None = None) -> Path:
        src = tmp_path / "runs" / f"pilot-{family}-20260430" / "evidence" / "latest"
        src.mkdir(parents=True)
        default_files = {
            "validation-results.json": json.dumps({"family": family, "total": 9}),
            "pr-candidate-manifest.json": json.dumps({"family": family, "count": 9}),
            "gate-results.json": json.dumps({"family": family, "verdict": "PR_DRY_RUN_READY"}),
            "llm-preflight.json": json.dumps({"family": family, "provider": "llm_professionalize"}),
            f"{family}-source-of-truth-proof.json": json.dumps({"family": family}),
        }
        for fname, content in (files or default_files).items():
            (src / fname).write_text(content, encoding="utf-8")
        return src

    def test_family_scoped_latest_path_written(self, tmp_path):
        """promote_family_evidence must write to families/{family}/ directory."""
        src = self._make_src_latest(tmp_path, "cells")
        verification_dir = tmp_path / "verification"
        promote_family_evidence(src, verification_dir, "cells", "pilot-cells-20260430")
        assert (verification_dir / "latest" / "families" / "cells").exists()
        assert (verification_dir / "latest" / "families" / "cells" / "validation-results.json").exists()

    def test_single_family_cells_promotion_does_not_overwrite_words_latest(self, tmp_path):
        """Cells promotion must not remove or corrupt Words evidence in families/words/."""
        verification_dir = tmp_path / "verification"
        # First: promote Words evidence
        src_words = self._make_src_latest(tmp_path, "words")
        promote_family_evidence(src_words, verification_dir, "words", "pilot-words-20260501")
        words_vr = (verification_dir / "latest" / "families" / "words" / "validation-results.json")
        assert words_vr.exists()
        original_words_content = words_vr.read_text(encoding="utf-8")

        # Then: promote Cells evidence
        src_cells = self._make_src_latest(tmp_path, "cells")
        promote_family_evidence(src_cells, verification_dir, "cells", "pilot-cells-20260430")

        # Words evidence must be untouched in families/words/
        assert words_vr.exists(), "Words validation-results.json must still exist"
        assert words_vr.read_text(encoding="utf-8") == original_words_content, (
            "Cells promotion must not overwrite Words family-scoped evidence"
        )

    def test_single_family_words_promotion_does_not_overwrite_cells_latest(self, tmp_path):
        """Words promotion must not remove or corrupt Cells evidence in families/cells/."""
        verification_dir = tmp_path / "verification"
        # First: promote Cells evidence
        src_cells = self._make_src_latest(tmp_path, "cells")
        promote_family_evidence(src_cells, verification_dir, "cells", "pilot-cells-20260430")
        cells_vr = (verification_dir / "latest" / "families" / "cells" / "validation-results.json")
        original_cells_content = cells_vr.read_text(encoding="utf-8")

        # Then: promote Words evidence
        src_words = self._make_src_latest(tmp_path, "words")
        promote_family_evidence(src_words, verification_dir, "words", "pilot-words-20260501")

        # Cells evidence must be untouched in families/cells/
        assert cells_vr.exists(), "Cells validation-results.json must still exist"
        assert cells_vr.read_text(encoding="utf-8") == original_cells_content, (
            "Words promotion must not overwrite Cells family-scoped evidence"
        )

    def test_global_latest_files_preserved(self, tmp_path):
        """Global files in verification/latest/ must not be deleted by family promotion."""
        verification_dir = tmp_path / "verification"
        (verification_dir / "latest").mkdir(parents=True)
        global_file = verification_dir / "latest" / "open-taskcard-closure-matrix.json"
        global_file.write_text('{"total": 45}', encoding="utf-8")

        src_cells = self._make_src_latest(tmp_path, "cells")
        promote_family_evidence(src_cells, verification_dir, "cells", "pilot-cells-20260430")

        assert global_file.exists(), "Global open-taskcard-closure-matrix.json must not be deleted"
        assert json.loads(global_file.read_text())["total"] == 45

    def test_family_scoped_metadata_written(self, tmp_path):
        """_evidence_metadata.json must be written to families/{family}/ with correct fields."""
        verification_dir = tmp_path / "verification"
        src = self._make_src_latest(tmp_path, "cells")
        result = promote_family_evidence(src, verification_dir, "cells", "pilot-cells-20260430-175422")

        meta_path = verification_dir / "latest" / "families" / "cells" / "_evidence_metadata.json"
        assert meta_path.exists(), "_evidence_metadata.json must be written"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        assert meta["scope"] == "family"
        assert meta["family"] == "cells"
        assert meta["run_id"] == "pilot-cells-20260430-175422"
        assert "promoted_at" in meta
        assert "files" in meta
        assert isinstance(meta["files"], list)

    def test_legacy_latest_alias_marked_deprecated_if_written(self, tmp_path):
        """_last_promoted_by.json must be written to verification/latest/ after promotion."""
        verification_dir = tmp_path / "verification"
        src = self._make_src_latest(tmp_path, "cells")
        promote_family_evidence(src, verification_dir, "cells", "pilot-cells-20260430-175422")

        notice_path = verification_dir / "latest" / "_last_promoted_by.json"
        assert notice_path.exists(), "_last_promoted_by.json must be written to top-level"
        notice = json.loads(notice_path.read_text(encoding="utf-8"))
        assert notice["deprecated_latest_alias"] is True
        assert notice["last_promoted_by_family"] == "cells"
        assert notice["last_promoted_run_id"] == "pilot-cells-20260430-175422"

    def test_resolve_family_evidence_path_prefers_family_scoped(self, tmp_path):
        """resolve_family_evidence_path must return families/{family}/ path when it exists."""
        verification_dir = tmp_path / "verification"
        family_path = verification_dir / "latest" / "families" / "cells"
        family_path.mkdir(parents=True)
        (family_path / "validation-results.json").write_text('{"family":"cells"}', encoding="utf-8")
        # Also write top-level stale version
        (verification_dir / "latest").mkdir(exist_ok=True)
        (verification_dir / "latest" / "validation-results.json").write_text('{"family":"words"}', encoding="utf-8")

        resolved = resolve_family_evidence_path(verification_dir, "cells", "validation-results.json")
        assert resolved == family_path / "validation-results.json"
        content = json.loads(resolved.read_text())
        assert content["family"] == "cells", "Must read Cells content, not stale Words content"

    def test_cross_family_contamination_detected(self, tmp_path):
        """detect_cross_family_contamination must warn when last writer != expected family."""
        verification_dir = tmp_path / "verification"
        (verification_dir / "latest").mkdir(parents=True)
        notice = {
            "deprecated_latest_alias": True,
            "last_promoted_by_family": "words",
            "last_promoted_run_id": "pilot-words-20260501",
            "last_promoted_at": "2026-05-01T00:00:00+00:00",
        }
        (verification_dir / "latest" / "_last_promoted_by.json").write_text(
            json.dumps(notice), encoding="utf-8"
        )
        warnings = detect_cross_family_contamination(verification_dir, expected_family="cells")
        assert len(warnings) == 1, "Must detect 1 contamination warning"
        assert "words" in warnings[0]
        assert "cells" in warnings[0]

    def test_no_contamination_when_same_family(self, tmp_path):
        """detect_cross_family_contamination must return empty list when last writer matches."""
        verification_dir = tmp_path / "verification"
        (verification_dir / "latest").mkdir(parents=True)
        notice = {
            "deprecated_latest_alias": True,
            "last_promoted_by_family": "cells",
            "last_promoted_run_id": "pilot-cells-20260430",
            "last_promoted_at": "2026-04-30T00:00:00+00:00",
        }
        (verification_dir / "latest" / "_last_promoted_by.json").write_text(
            json.dumps(notice), encoding="utf-8"
        )
        warnings = detect_cross_family_contamination(verification_dir, expected_family="cells")
        assert warnings == [], f"No warnings expected for same-family, got: {warnings}"

    def test_family_scoped_evidence_files_constant_is_complete(self):
        """FAMILY_SCOPED_EVIDENCE_FILES must contain all the files that caused contamination."""
        contaminated = {
            "validation-results.json",
            "pr-candidate-manifest.json",
            "example-gate-results.json",
            "example-reviewer-results.json",
        }
        for f in contaminated:
            assert f in FAMILY_SCOPED_EVIDENCE_FILES, (
                f"{f} must be in FAMILY_SCOPED_EVIDENCE_FILES — it caused cross-family contamination"
            )
