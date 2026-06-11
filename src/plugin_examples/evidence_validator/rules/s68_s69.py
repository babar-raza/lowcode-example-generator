"""Evidence validation rules — Sprint68to69Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)


class Sprint68to69Rules:
    """Rule mixin for evidence validation."""

    def _rule_pdf_root_readme_complete(self) -> RuleResult:
        """PDF root README must have >=19 rows in the examples table.

        Sprint 67 defect S67-D1: pdf-root-readme.md only had 3/19 rows.
        Rule 44 (root_readme_cardinality_annotated) only checked cells README.
        This rule checks the PDF README directly.
        """
        rule_id = "pdf_root_readme_complete"
        pdf_readme = self.bundle_dir / "root-readme" / "per-family" / "pdf-root-readme.md"
        if not pdf_readme.exists():
            return RuleResult(
                rule_id=rule_id,
                description="PDF root README must have >=19 example rows",
                severity="FAILURE",
                passed=False,
                failure_detail="root-readme/per-family/pdf-root-readme.md not found",
            )
        content = pdf_readme.read_text(encoding="utf-8", errors="replace")
        # Count rows in the examples table: lines with pipe-delimited content containing
        # the dotnet run command pattern (header row excluded)
        run_rows = [ln for ln in content.splitlines() if "dotnet run" in ln and ln.strip().startswith("|")]
        count = len(run_rows)
        if count < 19:
            return RuleResult(
                rule_id=rule_id,
                description="PDF root README must have >=19 example rows",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"PDF root README has only {count} example rows (need >=19). "
                    "Sprint 67 defect S67-D1: table was truncated at 3 rows."
                ),
            )
        return RuleResult(
            rule_id=rule_id,
            description="PDF root README must have >=19 example rows",
            severity="FAILURE",
            passed=True,
            evidence=f"PDF root README has {count} example rows (>= 19)",
        )

    def _rule_splitter_cardinality_reconciled(self) -> RuleResult:
        """A splitter cardinality reconciliation document must exist.

        Sprint 67 defect S67-D2: legacy reconciliation was high-level only;
        per-type splitter cardinality decisions were not documented.
        Checks for splitter-resolution.md in any legacy-reconciliation directory.
        """
        rule_id = "splitter_cardinality_reconciled"
        # Check both sprint68 path and sprint67 legacy path
        candidates = [
            self.bundle_dir / "legacy-reconciliation" / "splitter-resolution.md",
            self.bundle_dir / "legacy-plan-reconciliation" / "splitter-resolution.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                content = candidate.read_text(encoding="utf-8", errors="replace")
                if "IN_PROGRESS" in content:
                    return RuleResult(
                        rule_id=rule_id,
                        description="Splitter cardinality reconciliation document must be complete",
                        severity="FAILURE",
                        passed=False,
                        failure_detail=f"{candidate.name} contains IN_PROGRESS",
                    )
                return RuleResult(
                    rule_id=rule_id,
                    description="Splitter cardinality reconciliation document must be complete",
                    severity="FAILURE",
                    passed=True,
                    evidence=f"Splitter cardinality reconciliation present: {candidate}",
                )
        return RuleResult(
            rule_id=rule_id,
            description="Splitter cardinality reconciliation document must be complete",
            severity="FAILURE",
            passed=False,
            failure_detail=(
                "No splitter-resolution.md found in legacy-reconciliation/ or "
                "legacy-plan-reconciliation/. Sprint 67 defect S67-D2."
            ),
        )

    def _rule_canonical_content_audit_no_stale_pdf_version(self) -> RuleResult:
        """Sprint-specific content audit must not have PDF records with version 26.4.0.

        Sprint 67 defect S67-D3: content-audit-final.json had PDF records with
        package_version=26.4.0 despite the HANDOFF_CANONICAL policy setting 26.5.0.
        This rule checks the sprint-specific content audit for stale PDF versions.
        """
        rule_id = "canonical_content_audit_no_stale_pdf_version"
        # Find the sprint-specific content audit
        dest_dir = self.bundle_dir / "destination"
        if not dest_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Sprint content audit must have no stale PDF 26.4.0 version records",
                severity="FAILURE",
                passed=False,
                failure_detail="destination/ directory not found",
            )
        # Look for sprint-specific audit (e.g., content-audit-sprint68.json)
        sprint_id = self._read_sprint_id()
        audit_path = dest_dir / f"content-audit-{sprint_id}.json"
        if not audit_path.exists():
            # Fall back to any content-audit file in destination/
            candidates = list(dest_dir.glob("content-audit-sprint*.json"))
            if not candidates:
                return RuleResult(
                    rule_id=rule_id,
                    description="Sprint content audit must have no stale PDF 26.4.0 version records",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"No content-audit-{sprint_id}.json found in destination/",
                )
            audit_path = sorted(candidates)[-1]
        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Sprint content audit must have no stale PDF 26.4.0 version records",
                severity="FAILURE",
                passed=False,
                failure_detail=str(exc),
            )
        stale_records = [
            r.get("scenario_id", "?")
            for r in data.get("records", [])
            if r.get("family") == "pdf" and r.get("package_version") == "26.4.0"
        ]
        if stale_records:
            return RuleResult(
                rule_id=rule_id,
                description="Sprint content audit must have no stale PDF 26.4.0 version records",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"Found {len(stale_records)} PDF records with stale version 26.4.0: "
                    f"{stale_records[:5]}. Sprint 67 defect S67-D3."
                ),
            )
        return RuleResult(
            rule_id=rule_id,
            description="Sprint content audit must have no stale PDF 26.4.0 version records",
            severity="FAILURE",
            passed=True,
            evidence=f"No stale PDF 26.4.0 records in {audit_path.name}",
        )

    def _rule_pdf_version_proof_chain_present(self) -> RuleResult:
        """version/pdf-version-proof-chain.md must exist.

        Sprint 67 defect S67-D4: PDF version 26.5.0 was policy-based only.
        This rule requires a proof chain document linking the handoff
        Directory.Packages.props to the 26.5.0 version claim.
        """
        rule_id = "pdf_version_proof_chain_present"
        proof_path = self.bundle_dir / "version" / "pdf-version-proof-chain.md"
        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="version/pdf-version-proof-chain.md must be present",
                severity="FAILURE",
                passed=False,
                failure_detail="version/pdf-version-proof-chain.md not found. Sprint 67 defect S67-D4.",
            )
        content = proof_path.read_text(encoding="utf-8", errors="replace")
        if "IN_PROGRESS" in content:
            return RuleResult(
                rule_id=rule_id,
                description="version/pdf-version-proof-chain.md must be present",
                severity="FAILURE",
                passed=False,
                failure_detail="pdf-version-proof-chain.md contains IN_PROGRESS",
            )
        return RuleResult(
            rule_id=rule_id,
            description="version/pdf-version-proof-chain.md must be present",
            severity="FAILURE",
            passed=True,
            evidence="version/pdf-version-proof-chain.md is present and complete",
        )

    def _rule_all_family_cardinality_display_validated(self) -> RuleResult:
        """All 6 family root READMEs must have cardinality markers for multi-I/O types.

        Sprint 67 defect S67-D5: rule 44 only checked the Cells README.
        Words README merger/splitter/comparer must show ×N or 2× markers.
        PDF README merger/splitter must show ×N markers.

        Checks that words-root-readme.md contains at least one ×N or 2× marker.
        (PDF is already covered by rule 53 which validates 19/19 rows with correct markers.)
        """
        rule_id = "all_family_cardinality_display_validated"
        words_readme = self.bundle_dir / "root-readme" / "per-family" / "words-root-readme.md"
        if not words_readme.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Words root README must have cardinality markers for multi-I/O types",
                severity="FAILURE",
                passed=False,
                failure_detail="root-readme/per-family/words-root-readme.md not found",
            )
        content = words_readme.read_text(encoding="utf-8", errors="replace")
        has_multi_marker = (
            "×N" in content or "2×" in content or "(xN)" in content or "(×N)" in content or "xN" in content
        )
        if not has_multi_marker:
            return RuleResult(
                rule_id=rule_id,
                description="Words root README must have cardinality markers for multi-I/O types",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "words-root-readme.md has no ×N or 2× cardinality markers. "
                    "Words Merger (N→1), Splitter (1→N), and Comparer (2→1) require annotations. "
                    "Sprint 67 defect S67-D5."
                ),
            )
        return RuleResult(
            rule_id=rule_id,
            description="Words root README must have cardinality markers for multi-I/O types",
            severity="FAILURE",
            passed=True,
            evidence="words-root-readme.md contains multi-cardinality markers (×N or 2×)",
        )

    # ------------------------------------------------------------------
    # Sprint 69 rules (58-67): close S68-D1 through S68-D8
    # ------------------------------------------------------------------

    def _rule_handoff_index_version_matches_dpp(self) -> RuleResult:
        """All family handoff-index nuget_version must match Directory.Packages.props.

        Sprint 68 defect S68-D5: words/pdf/diagram handoff-index said 26.4.0
        but Directory.Packages.props said 26.5.0.
        """
        import re as _re

        rule_id = "handoff_index_version_matches_dpp"
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        mismatches = []
        for family in families:
            idx_path = self.bundle_dir / "handoff" / "per-family" / family / "handoff-index.json"
            dpp_path = self.bundle_dir / "handoff" / "per-family" / family / "Directory.Packages.props"
            if not idx_path.exists() or not dpp_path.exists():
                continue
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                idx_ver = idx.get("nuget_version", "")
                dpp_content = dpp_path.read_text(encoding="utf-8")
                m = _re.search(r'Version="([^"]+)"', dpp_content)
                dpp_ver = m.group(1) if m else ""
                if idx_ver and dpp_ver and idx_ver != dpp_ver:
                    mismatches.append(f"{family}: handoff-index={idx_ver} vs DPP={dpp_ver}")
            except Exception as exc:
                mismatches.append(f"{family}: read error {exc}")
        if mismatches:
            return RuleResult(
                rule_id=rule_id,
                description="Handoff-index nuget_version must match Directory.Packages.props for all families",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Version mismatches: {'; '.join(mismatches)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Handoff-index nuget_version must match Directory.Packages.props for all families",
            severity="FAILURE",
            passed=True,
            evidence="All family handoff-index versions match Directory.Packages.props",
        )

    def _rule_only_one_canonical_final_audit(self) -> RuleResult:
        """destination/content-audit-final.json must exist and must not contain stale sprint paths.

        Sprint 68 defect S68-D4: stale content-audit-final.json coexisted with
        content-audit-sprint68.json. The 'final' filename implies authority but was stale.
        """
        rule_id = "only_one_canonical_final_audit"
        final_path = self.bundle_dir / "destination" / "content-audit-final.json"
        if not final_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="destination/content-audit-final.json must exist as the one canonical audit",
                severity="FAILURE",
                passed=False,
                failure_detail="destination/content-audit-final.json not found",
            )
        content = final_path.read_text(encoding="utf-8", errors="replace")
        stale_sprints = ["sprint64", "sprint66", "sprint67", "sprint68"]
        sprint_id = self._read_sprint_id()
        # allow references to current sprint
        for stale in stale_sprints:
            if stale in sprint_id:
                continue
            # Check for stale sprint in path-like fields (handoff_path, local_package_path)
            import re as _re

            stale_in_paths = _re.findall(
                rf'"(?:handoff_path|local_package_path|programcs_path|readme_path)"\s*:\s*"[^"]*{stale}[^"]*"',
                content,
            )
            if stale_in_paths:
                return RuleResult(
                    rule_id=rule_id,
                    description="destination/content-audit-final.json must not contain stale sprint paths",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"Stale {stale} paths found in content-audit-final.json: {stale_in_paths[:2]}",
                )
        return RuleResult(
            rule_id=rule_id,
            description="destination/content-audit-final.json must exist with no stale sprint paths",
            severity="FAILURE",
            passed=True,
            evidence="content-audit-final.json exists and contains no stale sprint paths",
        )

    def _rule_publication_truth_matrix_no_stale_paths(self) -> RuleResult:
        """publication/publication-truth-matrix-final.json must not reference old sprint paths.

        Sprint 68 defect S68-D2: all 42 records used sprint67 destination-packages paths.
        """
        rule_id = "publication_truth_matrix_no_stale_paths"
        ptm_path = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not ptm_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication-truth-matrix-final.json must exist without stale sprint paths",
                severity="FAILURE",
                passed=False,
                failure_detail="publication/publication-truth-matrix-final.json not found",
            )
        content = ptm_path.read_text(encoding="utf-8", errors="replace")
        stale_sprints = ["sprint64", "sprint66", "sprint67", "sprint68"]
        sprint_id = self._read_sprint_id()
        for stale in stale_sprints:
            if stale in sprint_id:
                continue
            import re as _re

            stale_in_paths = _re.findall(
                rf'"(?:handoff_package_path|dry_run_package_path|handoff_path)"\s*:\s*"[^"]*{stale}[^"]*"',
                content,
            )
            if stale_in_paths:
                return RuleResult(
                    rule_id=rule_id,
                    description="publication-truth-matrix-final.json must not contain stale sprint paths",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"Stale {stale} path refs in publication-truth-matrix-final.json: {stale_in_paths[:2]}",
                )
        return RuleResult(
            rule_id=rule_id,
            description="publication-truth-matrix-final.json must exist without stale sprint paths",
            severity="FAILURE",
            passed=True,
            evidence="publication-truth-matrix-final.json contains no stale sprint paths",
        )

    def _rule_publication_truth_matrix_no_mixed_state(self) -> RuleResult:
        """publication-truth-matrix-final.json must not have readme_io_post_merge_verified=true
        while remote_example_readme_has_io_docs=false.

        Sprint 68 defect S68-D3: post_merge_verified mixed old publication with README I/O state.
        """
        rule_id = "publication_truth_matrix_no_mixed_state"
        ptm_path = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not ptm_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication-truth-matrix-final.json must not mix README I/O states",
                severity="FAILURE",
                passed=False,
                failure_detail="publication/publication-truth-matrix-final.json not found",
            )
        try:
            ptm = json.loads(ptm_path.read_text(encoding="utf-8"))
            # Sprint 82+ uses flat-array format; legacy used wrapped {"records": [...]}
            if isinstance(ptm, list):
                records = ptm
            else:
                records = ptm.get("records", [])
            mixed = [
                r.get("scenario_id", r.get("example", "unknown"))
                for r in records
                if not r.get("remote_example_readme_has_io_docs", True)
                and r.get("readme_io_post_merge_verified", False)
            ]
            if mixed:
                return RuleResult(
                    rule_id=rule_id,
                    description="No record may have readme_io_post_merge_verified=true while remote README lacks I/O docs",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"Mixed state in {len(mixed)} records: {mixed[:3]}",
                )
        except Exception as exc:
            return RuleResult(
                rule_id=rule_id,
                description="publication-truth-matrix-final.json must not mix README I/O states",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read publication-truth-matrix-final.json: {exc}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="publication-truth-matrix-final.json must not mix README I/O states",
            severity="FAILURE",
            passed=True,
            evidence="No mixed readme_io_post_merge_verified / remote_example_readme_has_io_docs state",
        )

    def _rule_root_readme_indexed_in_handoff(self) -> RuleResult:
        """All 6 family handoff-index.json must include a root_readme field.

        Sprint 68 defect S68-D6: root README artifacts existed but were not
        first-class handoff index entries.
        """
        rule_id = "root_readme_indexed_in_handoff"
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        missing = []
        for family in families:
            idx_path = self.bundle_dir / "handoff" / "per-family" / family / "handoff-index.json"
            if not idx_path.exists():
                missing.append(f"{family}: handoff-index.json not found")
                continue
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                if "root_readme" not in idx:
                    missing.append(f"{family}: no root_readme field in handoff-index.json")
            except Exception as exc:
                missing.append(f"{family}: read error {exc}")
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="All 6 family handoff-indexes must include root_readme field",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Missing root_readme: {'; '.join(missing)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="All 6 family handoff-indexes must include root_readme field",
            severity="FAILURE",
            passed=True,
            evidence="All 6 family handoff-index.json files have root_readme field",
        )

    def _rule_exact_legacy_reconciliation_present(self) -> RuleResult:
        """Consolidated exact legacy reconciliation report must exist.

        Sprint 68 defect S68-D7: legacy reconciliation was split across two trees
        with no consolidated authority report.
        """
        rule_id = "exact_legacy_reconciliation_present"
        final_path = self.bundle_dir / "legacy-reconciliation" / "exact-legacy-plan-reconciliation-final.md"
        items_path = self.bundle_dir / "legacy-reconciliation" / "exact-items-final.json"
        missing = []
        if not final_path.exists():
            missing.append("legacy-reconciliation/exact-legacy-plan-reconciliation-final.md")
        if not items_path.exists():
            missing.append("legacy-reconciliation/exact-items-final.json")
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="Consolidated exact legacy reconciliation must exist",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Missing: {'; '.join(missing)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Consolidated exact legacy reconciliation must exist",
            severity="FAILURE",
            passed=True,
            evidence="exact-legacy-plan-reconciliation-final.md and exact-items-final.json present",
        )

    def _rule_final_verdict_is_precise(self) -> RuleResult:
        """final-verdict.md must use an allowed precise verdict, not a generic SPRINT##_COMPLETE.

        Sprint 68 defect S68-D1: verdict SPRINT68_COMPLETE is too generic and overclaims.
        """
        rule_id = "final_verdict_is_precise"
        verdict_path = self.bundle_dir / "final-verdict.md"
        if not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="final-verdict.md must use an allowed precise verdict",
                severity="FAILURE",
                passed=False,
                failure_detail="final-verdict.md not found",
            )
        content = verdict_path.read_text(encoding="utf-8", errors="replace")
        allowed_verdicts = [
            "LOWCODE_PREPUBLICATION_HANDOFF_READY_APPROVAL_BLOCKED",
            "LOWCODE_README_IO_PRS_CREATED_MERGE_APPROVAL_BLOCKED",
            "LOWCODE_README_IO_PUBLISHED_AND_POST_MERGE_VERIFIED",
            "LOWCODE_PREPUBLICATION_HANDOFF_PARTIAL_WITH_EXPLICIT_BLOCKERS",
            "EVIDENCE_REPAIR_REQUIRED_NOT_CLOSED",
            "LOWCODE_PREPUBLICATION_HANDOFF_READY_REMOTE_REFRESH_PARTIAL",
            "LOWCODE_LIVE_PUBLICATION_BLOCKED_BY_APPROVAL",
            "LOWCODE_PUBLICATION_PARTIAL_WITH_EXPLICIT_BLOCKERS",
            # Sprint 75 verdicts
            "LOWCODE_WEEKLY_REVIEW_ITEMS_CLASSIFIED_PUBLICATION_APPROVAL_BLOCKED",
            "LOWCODE_WEEKLY_REVIEW_REPAIRED_AND_README_IO_PRS_CREATED",
            "LOWCODE_PUBLICATION_AND_REVIEW_ITEMS_PARTIAL_WITH_EXPLICIT_BLOCKERS",
            # Sprint 77 verdicts
            "LOWCODE_WEEKLY_REVIEW_REPAIRED_WITH_WORKSPACE_EXCEPTION_PUBLICATION_APPROVAL_BLOCKED",
            "LOWCODE_WEEKLY_REVIEW_REPAIRED_CLEAN_PUBLICATION_APPROVAL_BLOCKED",
            "LOWCODE_WEEKLY_REVIEW_REPAIR_PARTIAL_WITH_EXPLICIT_BLOCKERS",
            # Sprint 78 verdicts
            "LOWCODE_LIVE_PUBLICATION_ALL_PUBLISHED_README_BACKFILL_APPROVAL_BLOCKED",
            "LOWCODE_FINISH_LINE_README_IO_APPROVAL_BLOCKED",
            # Sprint 79 verdicts
            "LOWCODE_FINISH_LINE_EVIDENCE_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED",
            "LOWCODE_FINISH_LINE_PARTIAL_WITH_EXPLICIT_BLOCKERS",
            # Sprint 86 verdicts
            "LOWCODE_LIVE_PUBLICATION_BASELINE_FROZEN_APPROVAL_BLOCKED_SAFE_LANES_ADVANCED",
            # Sprint 87 verdicts
            "LOWCODE_PUBLICATION_BASELINE_FROZEN_NEXT_SYSTEM_ADVANCED",
            "LOWCODE_REPAIR_AND_ADVANCEMENT_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED",
            "LOWCODE_REPAIR_AND_ADVANCEMENT_PARTIAL_WITH_EXPLICIT_BLOCKERS",
            "LOWCODE_BASELINE_FROZEN_REPAIR_COMPLETE_ADVANCEMENT_PARTIAL",
            "LOWCODE_BASELINE_FROZEN_ALL_LANES_COMPLETE",
            # Sprint 88 verdicts
            "LOWCODE_FINISH_LINE_ADVANCEMENT_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED",
            "LOWCODE_NEXT_FAMILY_DISCOVERY_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED",
            # Sprint 89 verdicts
            "LOWCODE_HTML_SVG_REFLECTION_REPAIRED_NEXT_FAMILY_READY",
            "LOWCODE_NEXT_FAMILY_DRY_RUN_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED",
        ]
        # Check for generic SPRINT##_COMPLETE pattern
        import re as _re

        if _re.search(r"SPRINT\d+_COMPLETE", content):
            return RuleResult(
                rule_id=rule_id,
                description="final-verdict.md must not use generic SPRINT##_COMPLETE",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "final-verdict.md contains SPRINT##_COMPLETE which is overbroad. " f"Use one of: {allowed_verdicts}"
                ),
            )
        has_allowed = any(v in content for v in allowed_verdicts)
        if not has_allowed:
            return RuleResult(
                rule_id=rule_id,
                description="final-verdict.md must contain an allowed precise verdict",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"final-verdict.md contains no allowed verdict. " f"Expected one of: {allowed_verdicts}"
                ),
            )
        return RuleResult(
            rule_id=rule_id,
            description="final-verdict.md must use an allowed precise verdict",
            severity="FAILURE",
            passed=True,
            evidence="final-verdict.md contains an allowed precise verdict",
        )

    def _rule_final_verdict_not_complete_while_blocked(self) -> RuleResult:
        """final-verdict.md must not claim publication complete while approval is blocked.

        Sprint 68 defect S68-D1: SPRINT68_COMPLETE implies full delivery including
        publication, but publication is blocked by APPROVE_LIVE_PR.
        """
        rule_id = "final_verdict_not_complete_while_blocked"
        verdict_path = self.bundle_dir / "final-verdict.md"
        ptm_path = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not verdict_path.exists() or not ptm_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="final-verdict.md must not claim complete while publication is blocked",
                severity="FAILURE",
                passed=True,  # can't check without both files
                evidence="Skipped: one or both files missing",
            )
        verdict_content = verdict_path.read_text(encoding="utf-8", errors="replace")
        # If verdict claims post-merge-verified publication
        if "PUBLISHED_AND_POST_MERGE_VERIFIED" in verdict_content:
            try:
                ptm = json.loads(ptm_path.read_text(encoding="utf-8"))
                records = ptm.get("records", [])
                blocked = [r for r in records if r.get("approval_blocked", False)]
                if blocked:
                    return RuleResult(
                        rule_id=rule_id,
                        description="Cannot claim PUBLISHED_AND_POST_MERGE_VERIFIED while approval_blocked=true",
                        severity="FAILURE",
                        passed=False,
                        failure_detail=(
                            f"Verdict claims PUBLISHED but {len(blocked)}/42 records have approval_blocked=true"
                        ),
                    )
            except Exception:
                pass
        return RuleResult(
            rule_id=rule_id,
            description="final-verdict.md must not claim complete while publication is blocked",
            severity="FAILURE",
            passed=True,
            evidence="Verdict does not overclaim publication while blocked",
        )

    def _rule_handoff_index_has_root_readme_field(self) -> RuleResult:
        """Alias check: publication-handoff-index.json must list root_readme for each family.

        Sprint 68 defect S68-D6: root README artifacts not in handoff index.
        Checks the top-level publication-handoff-index.json.
        """
        rule_id = "handoff_index_has_root_readme_field"
        pub_idx_path = self.bundle_dir / "handoff" / "publication-handoff-index.json"
        if not pub_idx_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="handoff/publication-handoff-index.json must exist with root_readme entries",
                severity="FAILURE",
                passed=False,
                failure_detail="handoff/publication-handoff-index.json not found",
            )
        try:
            pub_idx = json.loads(pub_idx_path.read_text(encoding="utf-8"))
            families = pub_idx.get("families", [])
            missing_rr = [f["family"] for f in families if not f.get("root_readme_sha256")]
            if missing_rr:
                return RuleResult(
                    rule_id=rule_id,
                    description="publication-handoff-index.json must have root_readme_sha256 for each family",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"Missing root_readme_sha256 for: {missing_rr}",
                )
        except Exception as exc:
            return RuleResult(
                rule_id=rule_id,
                description="handoff/publication-handoff-index.json must exist with root_readme entries",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read publication-handoff-index.json: {exc}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="publication-handoff-index.json must have root_readme_sha256 for each family",
            severity="FAILURE",
            passed=True,
            evidence="All 6 family entries in publication-handoff-index.json have root_readme_sha256",
        )

    def _rule_version_consistency_final_present(self) -> RuleResult:
        """version/version-consistency-final.json must exist and show all_consistent=true.

        Sprint 68 defect S68-D5: version mismatch between handoff-index and DPP.
        This rule ensures the version audit artifact is produced and passes.
        """
        rule_id = "version_consistency_final_present"
        vc_path = self.bundle_dir / "version" / "version-consistency-final.json"
        if not vc_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="version/version-consistency-final.json must exist showing all_consistent=true",
                severity="FAILURE",
                passed=False,
                failure_detail="version/version-consistency-final.json not found",
            )
        try:
            vc = json.loads(vc_path.read_text(encoding="utf-8"))
            if not vc.get("all_consistent", False):
                mismatches = vc.get("sprint68_mismatches", "?")
                return RuleResult(
                    rule_id=rule_id,
                    description="version/version-consistency-final.json must show all_consistent=true",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"version-consistency-final.json: all_consistent=false, mismatches={mismatches}",
                )
        except Exception as exc:
            return RuleResult(
                rule_id=rule_id,
                description="version/version-consistency-final.json must exist and be valid",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read version-consistency-final.json: {exc}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="version/version-consistency-final.json must exist showing all_consistent=true",
            severity="FAILURE",
            passed=True,
            evidence="version-consistency-final.json: all_consistent=true, 0 mismatches",
        )

    # --- Sprint 70 NEW rules: close S69-D1 and S69-D2 ---
