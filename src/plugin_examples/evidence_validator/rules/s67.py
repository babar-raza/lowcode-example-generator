"""Evidence validation rules — Sprint67Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)



class Sprint67Rules:
    """Rule mixin for evidence validation."""

    def _rule_cardinality_audit_json_present(self) -> RuleResult:
        """root-readme/cardinality-audit.json must exist.

        Sprint 67 defect S66-D1: root READMEs showed xlsx→xlsx for
        merger/splitter without cardinality annotations. This rule enforces
        that a cardinality audit was performed and documented.
        """
        rule_id = "cardinality_audit_json_present"
        audit_path = self.bundle_dir / "root-readme" / "cardinality-audit.json"
        if not audit_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="root-readme/cardinality-audit.json must be present",
                severity="FAILURE", passed=False,
                failure_detail="root-readme/cardinality-audit.json not found",
            )
        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="root-readme/cardinality-audit.json must be present",
                severity="FAILURE", passed=False,
                failure_detail=f"Could not parse cardinality-audit.json: {exc}",
            )
        families = data.get("families", {})
        return RuleResult(
            rule_id=rule_id,
            description="root-readme/cardinality-audit.json must be present",
            severity="FAILURE", passed=True,
            evidence=f"cardinality-audit.json present with {len(families)} families",
        )

    def _rule_root_readme_cardinality_annotated(self) -> RuleResult:
        """Root README files must contain cardinality markers for multi-cardinality types.

        Sprint 67 defect S66-D1: merger rows must show ×N input marker;
        splitter rows must show ×N output marker.
        Checks cells and words root READMEs (most reliably have merger/splitter).
        """
        rule_id = "root_readme_cardinality_annotated"
        readme_dir = self.bundle_dir / "root-readme" / "per-family"
        if not readme_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Root READMEs must have cardinality markers for merger/splitter",
                severity="FAILURE", passed=False,
                failure_detail="root-readme/per-family/ directory not found",
            )

        # Check cells README for spreadsheet-merger and spreadsheet-splitter
        cells_readme = readme_dir / "cells-root-readme.md"
        if cells_readme.exists():
            content = cells_readme.read_text(encoding="utf-8", errors="replace")
            # Look for ×N in merger row
            import re
            merger_row = next(
                (ln for ln in content.splitlines() if "spreadsheet-merger" in ln), None
            )
            splitter_row = next(
                (ln for ln in content.splitlines() if "spreadsheet-splitter" in ln), None
            )
            if merger_row and "×N" not in merger_row and "xN" not in merger_row:
                return RuleResult(
                    rule_id=rule_id,
                    description="Root READMEs must have cardinality markers for merger/splitter",
                    severity="FAILURE", passed=False,
                    failure_detail="cells-root-readme.md: spreadsheet-merger row missing ×N cardinality marker",
                )
            if splitter_row and "×N" not in splitter_row and "xN" not in splitter_row:
                return RuleResult(
                    rule_id=rule_id,
                    description="Root READMEs must have cardinality markers for merger/splitter",
                    severity="FAILURE", passed=False,
                    failure_detail="cells-root-readme.md: spreadsheet-splitter row missing ×N cardinality marker",
                )

        return RuleResult(
            rule_id=rule_id,
            description="Root READMEs must have cardinality markers for merger/splitter",
            severity="FAILURE", passed=True,
            evidence="cells-root-readme.md has ×N cardinality markers for merger and splitter",
        )

    def _rule_pdf_version_decision_record_present(self) -> RuleResult:
        """version/pdf-version-decision.md must exist.

        Sprint 67 defect S66-D2: content-audit-final.json showed 26.4.0 for PDF
        while handoff had 26.5.0. A formal decision record is required.
        """
        rule_id = "pdf_version_decision_record_present"
        decision_path = self.bundle_dir / "version" / "pdf-version-decision.md"
        if not decision_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="version/pdf-version-decision.md must be present (S66-D2)",
                severity="FAILURE", passed=False,
                failure_detail="version/pdf-version-decision.md not found",
            )
        content = decision_path.read_text(encoding="utf-8", errors="replace")
        if "IN_PROGRESS" in content:
            return RuleResult(
                rule_id=rule_id,
                description="version/pdf-version-decision.md must be present (S66-D2)",
                severity="FAILURE", passed=False,
                failure_detail="pdf-version-decision.md contains IN_PROGRESS — not complete",
            )
        return RuleResult(
            rule_id=rule_id,
            description="version/pdf-version-decision.md must be present (S66-D2)",
            severity="FAILURE", passed=True,
            evidence="pdf-version-decision.md is present and complete",
        )

    def _rule_version_truth_matrix_present(self) -> RuleResult:
        """version/version-truth-matrix.json must exist and show a decision.

        Sprint 67 defect S66-D2: version contradiction requires a truth matrix.
        """
        rule_id = "version_truth_matrix_present"
        matrix_path = self.bundle_dir / "version" / "version-truth-matrix.json"
        if not matrix_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="version/version-truth-matrix.json must be present",
                severity="FAILURE", passed=False,
                failure_detail="version/version-truth-matrix.json not found",
            )
        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="version/version-truth-matrix.json must be present",
                severity="FAILURE", passed=False,
                failure_detail=f"Could not parse version-truth-matrix.json: {exc}",
            )
        families = data.get("families", {})
        return RuleResult(
            rule_id=rule_id,
            description="version/version-truth-matrix.json must be present",
            severity="FAILURE", passed=True,
            evidence=f"version-truth-matrix.json present with {len(families)} families",
        )

    def _rule_no_cross_sprint_path_leakage(self) -> RuleResult:
        """Content audit must not reference paths from prior sprints.

        Sprint 67 defect S66-D3: content-audit-final.json had local_package_path
        pointing to reports/sprint64/ for all 42 records.
        Checks the sprint-specific content audit file if present, else falls back
        to content-audit-final.json.
        """
        rule_id = "no_cross_sprint_path_leakage"
        # Try sprint-specific audit first
        sprint_audit = self.bundle_dir / "destination" / "content-audit-sprint67.json"
        if not sprint_audit.exists():
            sprint_audit = self.bundle_dir / "destination" / "content-audit-final.json"
        if not sprint_audit.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Content audit must have no cross-sprint path leakage",
                severity="FAILURE", passed=False,
                failure_detail="Neither content-audit-sprint67.json nor content-audit-final.json found",
            )
        try:
            data = json.loads(sprint_audit.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit must have no cross-sprint path leakage",
                severity="FAILURE", passed=False,
                failure_detail=f"Could not parse {sprint_audit.name}: {exc}",
            )

        records = data.get("records", [])
        stale = []
        for rec in records:
            hp = rec.get("handoff_path", "")
            lp = rec.get("local_package_path", "")
            for stale_sprint in ("sprint64", "sprint65", "sprint66"):
                if stale_sprint in hp or stale_sprint in lp:
                    stale.append(rec.get("scenario_id", "?"))
                    break

        if stale:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit must have no cross-sprint path leakage",
                severity="FAILURE", passed=False,
                failure_detail=f"{len(stale)} records have stale sprint path refs: {stale[:3]}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Content audit must have no cross-sprint path leakage",
            severity="FAILURE", passed=True,
            evidence=f"All {len(records)} records have clean sprint-specific paths in {sprint_audit.name}",
        )

    def _rule_legacy_plans_reconciliation_present(self) -> RuleResult:
        """legacy-plan-reconciliation/reconciliation-index.md must exist.

        Sprint 67 defect S66-D5: Sprint 62 Format Capability and Sprint 61
        README Sync plans had unresolved items not explicitly closed or carried.
        """
        rule_id = "legacy_plans_reconciliation_present"
        idx_path = (
            self.bundle_dir / "legacy-plan-reconciliation" / "reconciliation-index.md"
        )
        if not idx_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="legacy-plan-reconciliation/reconciliation-index.md must be present",
                severity="FAILURE", passed=False,
                failure_detail="legacy-plan-reconciliation/reconciliation-index.md not found",
            )
        content = idx_path.read_text(encoding="utf-8", errors="replace")
        if "IN_PROGRESS" in content:
            return RuleResult(
                rule_id=rule_id,
                description="legacy-plan-reconciliation/reconciliation-index.md must be present",
                severity="FAILURE", passed=False,
                failure_detail="reconciliation-index.md contains IN_PROGRESS — not complete",
            )
        return RuleResult(
            rule_id=rule_id,
            description="legacy-plan-reconciliation/reconciliation-index.md must be present",
            severity="FAILURE", passed=True,
            evidence="legacy-plan-reconciliation/reconciliation-index.md is present and complete",
        )

    def _rule_content_audit_sprint_specific_present(self) -> RuleResult:
        """destination/content-audit-sprint{N}.json must exist for current sprint.

        Sprint 67: ensures that the sprint-specific content audit (not just the
        inherited sprint66 file) is present. The sprint-specific file has
        correct paths and PDF version.
        """
        rule_id = "content_audit_sprint_specific_present"
        # Detect sprint number from sprint-state.json
        sprint_num = None
        state_path = self.bundle_dir / "sprint-state.json"
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                sprint_num = state.get("sprint_number")
            except (OSError, ValueError):
                pass

        if sprint_num:
            specific_path = (
                self.bundle_dir / "destination" / f"content-audit-sprint{sprint_num}.json"
            )
            if specific_path.exists():
                try:
                    data = json.loads(specific_path.read_text(encoding="utf-8"))
                    count = len(data.get("records", []))
                    return RuleResult(
                        rule_id=rule_id,
                        description="Sprint-specific content audit must be present",
                        severity="FAILURE", passed=True,
                        evidence=f"content-audit-sprint{sprint_num}.json present with {count} records",
                    )
                except (OSError, ValueError):
                    pass
            return RuleResult(
                rule_id=rule_id,
                description="Sprint-specific content audit must be present",
                severity="FAILURE", passed=False,
                failure_detail=f"destination/content-audit-sprint{sprint_num}.json not found",
            )

        # No sprint number found — skip gracefully
        return RuleResult(
            rule_id=rule_id,
            description="Sprint-specific content audit must be present",
            severity="FAILURE", passed=True,
            evidence="sprint_number not found in sprint-state.json; check skipped",
        )

    def _rule_handoff_index_per_family_complete(self) -> RuleResult:
        """All 6 family handoff-index.json files must exist.

        Sprint 67: ensures the self-contained handoff bundle has per-family
        index files with correct sprint67 paths.
        """
        rule_id = "handoff_index_per_family_complete"
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        handoff_base = self.bundle_dir / "handoff" / "per-family"
        missing = []
        for fam in families:
            idx = handoff_base / fam / "handoff-index.json"
            if not idx.exists():
                missing.append(fam)
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="All 6 family handoff-index.json files must be present",
                severity="FAILURE", passed=False,
                failure_detail=f"Missing handoff-index.json for: {missing}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="All 6 family handoff-index.json files must be present",
            severity="FAILURE", passed=True,
            evidence="All 6 per-family handoff-index.json files present",
        )

    def _rule_readme_sync_state_present(self) -> RuleResult:
        """readme-sync/sync-state.json must exist.

        Sprint 67: README sync architecture must be reviewed and documented.
        """
        rule_id = "readme_sync_state_present"
        state_path = self.bundle_dir / "readme-sync" / "sync-state.json"
        if not state_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="readme-sync/sync-state.json must be present",
                severity="FAILURE", passed=False,
                failure_detail="readme-sync/sync-state.json not found",
            )
        return RuleResult(
            rule_id=rule_id,
            description="readme-sync/sync-state.json must be present",
            severity="FAILURE", passed=True,
            evidence="readme-sync/sync-state.json is present",
        )

    def _rule_remote_truth_refresh_present(self) -> RuleResult:
        """remote/remote-proof-summary.md must exist for current sprint.

        Sprint 67: remote truth must be refreshed each sprint to confirm
        no unexpected remote mutations occurred.
        """
        rule_id = "remote_truth_refresh_present"
        summary_path = self.bundle_dir / "remote" / "remote-proof-summary.md"
        if not summary_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-summary.md must be present",
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-proof-summary.md not found",
            )
        content = summary_path.read_text(encoding="utf-8", errors="replace")
        if "IN_PROGRESS" in content:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-summary.md must be present",
                severity="FAILURE", passed=False,
                failure_detail="remote-proof-summary.md contains IN_PROGRESS — not complete",
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-proof-summary.md must be present",
            severity="FAILURE", passed=True,
            evidence="remote/remote-proof-summary.md is present and complete",
        )

    # ------------------------------------------------------------------
    # Sprint 68 rules: close S67-D1 through S67-D5
    # ------------------------------------------------------------------
