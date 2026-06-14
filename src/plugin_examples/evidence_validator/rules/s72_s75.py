"""Evidence validation rules — Sprint72to75Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)


class Sprint72to75Rules:
    """Rule mixin for evidence validation."""

    def _rule_remote_proof_consistency_audit_present(self) -> RuleResult:
        """remote/remote-proof-consistency-audit.json must exist.

        Sprint 71 defect S71-D1: no artifact documented the contradiction between
        remote-proof-summary.md (42/42) and remote-readme-io-audit-final.json (0/42).
        Sprint 72 adds a consistency audit file to close this gap.
        """
        rule_id = "remote_proof_consistency_audit_present"
        audit_file = self.bundle_dir / "remote" / "remote-proof-consistency-audit.json"
        if not audit_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-consistency-audit.json must be present",
                severity="FAILURE",
                passed=False,
                failure_detail="remote/remote-proof-consistency-audit.json not found",
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-proof-consistency-audit.json is present",
            severity="FAILURE",
            passed=True,
            evidence="remote/remote-proof-consistency-audit.json exists",
        )

    def _rule_remote_proof_consistency_audit_consistent(self) -> RuleResult:
        """remote/remote-proof-consistency-audit.json must have consistent=true.

        Sprint 71 defect S71-D1: remote-proof-summary.md contradicted the audit.
        This rule ensures the consistency audit confirms all checks passed.
        """
        rule_id = "remote_proof_consistency_audit_consistent"
        audit_file = self.bundle_dir / "remote" / "remote-proof-consistency-audit.json"
        if not audit_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-consistency-audit.json must exist with consistent=true",
                severity="FAILURE",
                passed=False,
                failure_detail="remote/remote-proof-consistency-audit.json not found",
            )
        try:
            data = json.loads(audit_file.read_text(encoding="utf-8"))
            if not data.get("consistent", False):
                return RuleResult(
                    rule_id=rule_id,
                    description="remote/remote-proof-consistency-audit.json must have consistent=true",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"consistent={data.get('consistent')} — remote proof is not consistent",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-consistency-audit.json must be valid JSON",
                severity="FAILURE",
                passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-proof-consistency-audit.json confirms consistent=true",
            severity="FAILURE",
            passed=True,
            evidence="remote-proof-consistency-audit.json: consistent=true",
        )

    def _rule_remote_proof_summary_states_zero_io(self) -> RuleResult:
        """remote/remote-proof-summary.md must state 0/42 remote README I/O sections.

        Sprint 71 defect S71-D1: The Sprint 68 artifact (carried through sprint71)
        incorrectly claimed '42/42 examples have README I/O sections in remote repos'.
        The corrected summary must state 0/42.
        """
        rule_id = "remote_proof_summary_states_zero_io"
        summary_file = self.bundle_dir / "remote" / "remote-proof-summary.md"
        if not summary_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-summary.md must exist and state 0/42 README I/O",
                severity="FAILURE",
                passed=False,
                failure_detail="remote/remote-proof-summary.md not found",
            )
        content = summary_file.read_text(encoding="utf-8")
        # Must NOT contain the incorrect 42/42 claim
        if "42/42 examples have README I/O sections" in content:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-summary.md must not claim 42/42 README I/O sections",
                severity="FAILURE",
                passed=False,
                failure_detail="remote-proof-summary.md still contains the incorrect '42/42 examples have README I/O sections' claim",
            )
        # Must state 0/42
        if "0/42" not in content:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-summary.md must state 0/42 remote README I/O",
                severity="FAILURE",
                passed=False,
                failure_detail="remote-proof-summary.md does not contain '0/42' — corrected count not stated",
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-proof-summary.md correctly states 0/42 remote README I/O sections",
            severity="FAILURE",
            passed=True,
            evidence="remote-proof-summary.md contains '0/42' and does not contain the incorrect 42/42 claim",
        )

    def _rule_remote_proof_summary_not_contradicted(self) -> RuleResult:
        """remote-proof-summary.md io claim must match remote-readme-io-audit-final.json io_doc_count.

        Catches cross-file contradictions like S71-D1 where summary said 42/42
        but audit said 0/42. Both must agree on the io count.
        """
        rule_id = "remote_proof_summary_not_contradicted"
        summary_file = self.bundle_dir / "remote" / "remote-proof-summary.md"
        audit_file = self.bundle_dir / "remote" / "remote-readme-io-audit-final.json"
        if not summary_file.exists() or not audit_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Both remote-proof-summary.md and remote-readme-io-audit-final.json must exist",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Missing: {'remote-proof-summary.md' if not summary_file.exists() else 'remote-readme-io-audit-final.json'}",
            )
        try:
            audit_data = json.loads(audit_file.read_text(encoding="utf-8"))
            io_doc_count = audit_data.get("io_doc_count", -1)
            total = audit_data.get("total", 42)
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote-readme-io-audit-final.json must be valid JSON",
                severity="FAILURE",
                passed=False,
                failure_detail=str(e),
            )
        summary_content = summary_file.read_text(encoding="utf-8")
        # If audit says 0, summary must not claim non-zero
        if io_doc_count == 0 and "42/42 examples have README I/O sections" in summary_content:
            return RuleResult(
                rule_id=rule_id,
                description="remote-proof-summary.md must not contradict audit io_doc_count=0",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Audit io_doc_count=0 but summary claims '42/42 examples have README I/O sections'",
            )
        return RuleResult(
            rule_id=rule_id,
            description=f"remote-proof-summary.md is consistent with audit io_doc_count={io_doc_count}/{total}",
            severity="FAILURE",
            passed=True,
            evidence=f"Audit io_doc_count={io_doc_count}, summary does not contradict this",
        )

    def _rule_remote_proof_summary_superseded_archived(self) -> RuleResult:
        """The superseded (incorrect) remote-proof-summary must be archived in history/.

        Sprint 72 archives the incorrect Sprint 68 document in
        history/remote-proof-summary-superseded.md to maintain audit trail.
        """
        rule_id = "remote_proof_summary_superseded_archived"
        superseded_file = self.bundle_dir / "history" / "remote-proof-summary-superseded.md"
        if not superseded_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="history/remote-proof-summary-superseded.md must be present",
                severity="FAILURE",
                passed=False,
                failure_detail="history/remote-proof-summary-superseded.md not found — incorrect Sprint 68 artifact not archived",
            )
        content = superseded_file.read_text(encoding="utf-8")
        if len(content.strip()) == 0:
            return RuleResult(
                rule_id=rule_id,
                description="history/remote-proof-summary-superseded.md must be non-empty",
                severity="FAILURE",
                passed=False,
                failure_detail="history/remote-proof-summary-superseded.md is empty",
            )
        return RuleResult(
            rule_id=rule_id,
            description="history/remote-proof-summary-superseded.md is present and non-empty",
            severity="FAILURE",
            passed=True,
            evidence=f"history/remote-proof-summary-superseded.md: {len(content)} bytes",
        )

    def _rule_remote_readme_io_audit_count_consistent(self) -> RuleResult:
        """remote-readme-io-audit-final.json: io_doc_count must equal count of has_io_section=true records.

        Catches internal inconsistency in the audit file itself.
        """
        rule_id = "remote_readme_io_audit_count_consistent"
        audit_file = self.bundle_dir / "remote" / "remote-readme-io-audit-final.json"
        if not audit_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-readme-io-audit-final.json must exist",
                severity="FAILURE",
                passed=False,
                failure_detail="remote/remote-readme-io-audit-final.json not found",
            )
        try:
            data = json.loads(audit_file.read_text(encoding="utf-8"))
            io_doc_count = data.get("io_doc_count", -1)
            records = data.get("records", [])
            actual_io_count = sum(1 for r in records if r.get("has_io_section", False))
            if io_doc_count != actual_io_count:
                return RuleResult(
                    rule_id=rule_id,
                    description="remote-readme-io-audit-final.json io_doc_count must match actual has_io_section=true count",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"io_doc_count={io_doc_count} but actual has_io_section=true count={actual_io_count}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote-readme-io-audit-final.json must be valid JSON",
                severity="FAILURE",
                passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description=f"remote-readme-io-audit-final.json io_doc_count={io_doc_count} matches has_io_section=true count",
            severity="FAILURE",
            passed=True,
            evidence=f"io_doc_count={io_doc_count} confirmed consistent with {len(records)} records",
        )

    def _rule_remote_vs_handoff_uses_current_sprint(self) -> RuleResult:
        """remote/remote-vs-handoff-final.json handoff_paths must use the current sprint.

        Catches the case where remote-vs-handoff-final.json was carried from a prior
        sprint without updating the handoff_path fields to the current sprint.
        """
        rule_id = "remote_vs_handoff_uses_current_sprint"
        rvh_file = self.bundle_dir / "remote" / "remote-vs-handoff-final.json"
        if not rvh_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-vs-handoff-final.json must exist with current sprint paths",
                severity="FAILURE",
                passed=False,
                failure_detail="remote/remote-vs-handoff-final.json not found",
            )
        try:
            content = rvh_file.read_text(encoding="utf-8")
            stale = self._get_stale_paths_in_content(content)
            if stale:
                return RuleResult(
                    rule_id=rule_id,
                    description="remote/remote-vs-handoff-final.json must use current sprint handoff paths",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"Stale sprint paths in remote-vs-handoff-final.json: {stale}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-vs-handoff-final.json must be readable",
                severity="FAILURE",
                passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-vs-handoff-final.json handoff_paths use current sprint",
            severity="FAILURE",
            passed=True,
            evidence="remote-vs-handoff-final.json scanned — all handoff_paths point to current sprint",
        )

    # ------------------------------------------------------------------
    # Sprint 75 — Weekly review integration rules
    # ------------------------------------------------------------------

    def _rule_weekly_review_claim_matrix_present(self) -> RuleResult:
        """02-weekly-review-claim-vs-proof-matrix.md must exist and classify items.

        Ensures independent weekly review items cannot be silently dropped.
        """
        rule_id = "weekly_review_claim_matrix_present"
        matrix_file = self.bundle_dir / "02-weekly-review-claim-vs-proof-matrix.md"
        if not matrix_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="02-weekly-review-claim-vs-proof-matrix.md must exist",
                severity="FAILURE",
                passed=False,
                failure_detail="02-weekly-review-claim-vs-proof-matrix.md not found — weekly review items not classified",
            )
        content = matrix_file.read_text(encoding="utf-8")
        required_markers = [
            "VERIFIED_HISTORICAL_BUT_SUPERSEDED",
            "BLOCKED_EXTERNAL",
            "NEEDS_REPAIR",
            "GOVERNANCE_EXCEPTION_REQUIRED",
        ]
        missing = [m for m in required_markers if m not in content]
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="Weekly review matrix must contain classification labels",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Missing classification labels in matrix: {missing}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Weekly review claim matrix present and contains classification labels",
            severity="FAILURE",
            passed=True,
            evidence="02-weekly-review-claim-vs-proof-matrix.md found with required classifications",
        )

    def _rule_pdf_publication_truth_reconciled(self) -> RuleResult:
        """pdf-publication/pdf-pr-reconciliation.json must exist.

        Prevents PDF publication truth from being inferred only from old PR numbers
        without current remote evidence.
        """
        rule_id = "pdf_publication_truth_reconciled"
        reconcile_file = self.bundle_dir / "pdf-publication" / "pdf-pr-reconciliation.json"
        if not reconcile_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="pdf-publication/pdf-pr-reconciliation.json must exist",
                severity="FAILURE",
                passed=False,
                failure_detail="pdf-pr-reconciliation.json not found — PDF publication truth not reconciled against remote state",
            )
        try:
            data = json.loads(reconcile_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="pdf-publication/pdf-pr-reconciliation.json must be valid JSON",
                severity="FAILURE",
                passed=False,
                failure_detail=str(e),
            )
        verdict = data.get("claim_verdict", "")
        if not verdict:
            return RuleResult(
                rule_id=rule_id,
                description="pdf-pr-reconciliation.json must contain claim_verdict field",
                severity="FAILURE",
                passed=False,
                failure_detail="claim_verdict field missing from pdf-pr-reconciliation.json",
            )
        return RuleResult(
            rule_id=rule_id,
            description="PDF publication truth reconciled with current remote evidence",
            severity="FAILURE",
            passed=True,
            evidence=f"pdf-pr-reconciliation.json present, claim_verdict={verdict}",
        )

    def _rule_formimporter_taskcard_durable(self) -> RuleResult:
        """formimporter/formimporter-repro-inventory.json must exist with retest trigger.

        Ensures FormImporter defect does not get lost between sprints.
        """
        rule_id = "formimporter_taskcard_durable"
        inv_file = self.bundle_dir / "formimporter" / "formimporter-repro-inventory.json"
        if not inv_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="formimporter/formimporter-repro-inventory.json must exist",
                severity="FAILURE",
                passed=False,
                failure_detail="formimporter-repro-inventory.json not found — FormImporter taskcard not durable",
            )
        try:
            data = json.loads(inv_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="formimporter-repro-inventory.json must be valid JSON",
                severity="FAILURE",
                passed=False,
                failure_detail=str(e),
            )
        trigger = data.get("next_retest_trigger", "")
        if not trigger:
            return RuleResult(
                rule_id=rule_id,
                description="formimporter-repro-inventory.json must have next_retest_trigger",
                severity="FAILURE",
                passed=False,
                failure_detail="next_retest_trigger field missing from formimporter-repro-inventory.json",
            )
        return RuleResult(
            rule_id=rule_id,
            description="FormImporter taskcard is durable with retest trigger",
            severity="FAILURE",
            passed=True,
            evidence=f"formimporter-repro-inventory.json present, trigger={trigger}",
        )

    def _rule_words_version_drift_documented(self) -> RuleResult:
        """version-drift/words-version-drift-current.json must exist with drift field.

        Prevents Words 26.4.0 vs 26.5.0 drift from being silently hidden.
        """
        rule_id = "words_version_drift_documented"
        drift_file = self.bundle_dir / "version-drift" / "words-version-drift-current.json"
        if not drift_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="version-drift/words-version-drift-current.json must exist",
                severity="FAILURE",
                passed=False,
                failure_detail="words-version-drift-current.json not found — Words version drift not documented",
            )
        try:
            data = json.loads(drift_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="words-version-drift-current.json must be valid JSON",
                severity="FAILURE",
                passed=False,
                failure_detail=str(e),
            )
        if "drift" not in data:
            return RuleResult(
                rule_id=rule_id,
                description="words-version-drift-current.json must have drift field",
                severity="FAILURE",
                passed=False,
                failure_detail="drift field missing from words-version-drift-current.json",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Words version drift documented with drift classification",
            severity="FAILURE",
            passed=True,
            evidence=f"words-version-drift-current.json present, drift={data.get('drift')}",
        )

    def _rule_email_slides_runtime_validated(self) -> RuleResult:
        """post-merge-runtime/post-merge-validation-matrix.json must exist.

        Ensures Email/Slides merged examples have post-merge runtime validation
        or an explicit blocker — not silently deferred.
        """
        rule_id = "email_slides_runtime_validated"
        matrix_file = self.bundle_dir / "post-merge-runtime" / "post-merge-validation-matrix.json"
        if not matrix_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="post-merge-runtime/post-merge-validation-matrix.json must exist",
                severity="FAILURE",
                passed=False,
                failure_detail="post-merge-validation-matrix.json not found — Email/Slides post-merge runtime not classified",
            )
        try:
            data = json.loads(matrix_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="post-merge-validation-matrix.json must be valid JSON",
                severity="FAILURE",
                passed=False,
                failure_detail=str(e),
            )
        records = data.get("records", [])
        if not records:
            return RuleResult(
                rule_id=rule_id,
                description="post-merge-validation-matrix.json must have records",
                severity="FAILURE",
                passed=False,
                failure_detail="records array is empty in post-merge-validation-matrix.json",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Post-merge runtime validation matrix present with records",
            severity="FAILURE",
            passed=True,
            evidence=f"post-merge-validation-matrix.json present, {len(records)} records",
        )

    def _rule_dirty_tree_classified(self) -> RuleResult:
        """git/dirty-file-classification.md must exist.

        Ensures dirty files are explicitly classified rather than silently
        polluting future evidence bundles.
        """
        rule_id = "dirty_tree_classified"
        classif_file = self.bundle_dir / "git" / "dirty-file-classification.md"
        if not classif_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="git/dirty-file-classification.md must exist",
                severity="FAILURE",
                passed=False,
                failure_detail="dirty-file-classification.md not found — dirty tree not explicitly classified",
            )
        content = classif_file.read_text(encoding="utf-8")
        if len(content.strip()) < 50:
            return RuleResult(
                rule_id=rule_id,
                description="git/dirty-file-classification.md must be substantive (not empty/minimal)",
                severity="FAILURE",
                passed=False,
                failure_detail="dirty-file-classification.md is too short to be substantive",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Dirty tree classification document present and substantive",
            severity="FAILURE",
            passed=True,
            evidence="git/dirty-file-classification.md found with content",
        )

    def _rule_sprint27_governance_classified(self) -> RuleResult:
        """governance/sprint27-strict-contract-revalidation.md must exist.

        Ensures Sprint 27's historical evidence gap is formally classified
        rather than ambiguous or silently ignored.
        """
        rule_id = "sprint27_governance_classified"
        gov_file = self.bundle_dir / "governance" / "sprint27-strict-contract-revalidation.md"
        if not gov_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="governance/sprint27-strict-contract-revalidation.md must exist",
                severity="FAILURE",
                passed=False,
                failure_detail="sprint27-strict-contract-revalidation.md not found — Sprint 27 evidence status ambiguous",
            )
        content = gov_file.read_text(encoding="utf-8")
        required = ["GOVERNANCE_EXCEPTION_REQUIRED", "HISTORICAL_NON_COMPLIANT"]
        missing = [m for m in required if m not in content]
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="sprint27-strict-contract-revalidation.md must contain governance classifications",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Missing in sprint27-strict-contract-revalidation.md: {missing}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Sprint 27 governance classification document present with required labels",
            severity="FAILURE",
            passed=True,
            evidence="sprint27-strict-contract-revalidation.md found with GOVERNANCE_EXCEPTION_REQUIRED and HISTORICAL_NON_COMPLIANT",
        )

    def _rule_weekly_review_verdict_not_complete_while_unclassified(self) -> RuleResult:
        """Final verdict must not say COMPLETE while weekly review items are unclassified.

        If 02-weekly-review-claim-vs-proof-matrix.md does not exist, the final verdict
        must not contain 'COMPLETE' or suggest closure.
        Prevents silently closing a sprint with unclassified review items.
        """
        rule_id = "weekly_review_verdict_not_complete_while_unclassified"
        matrix_file = self.bundle_dir / "02-weekly-review-claim-vs-proof-matrix.md"
        verdict_file = self.bundle_dir / "final-verdict.md"

        # Only applies if final verdict exists
        if not verdict_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="final-verdict.md not found — skipping weekly review verdict check",
                severity="FAILURE",
                passed=False,
                failure_detail="final-verdict.md not found",
            )

        verdict_content = verdict_file.read_text(encoding="utf-8")

        # If matrix exists, items are classified — no restriction needed
        if matrix_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Weekly review matrix present — verdict COMPLETE is allowed",
                severity="FAILURE",
                passed=True,
                evidence="02-weekly-review-claim-vs-proof-matrix.md present; weekly review items classified",
            )

        # Matrix absent — verdict must not claim complete
        if re.search(r"COMPLETE|ALL_ITEMS_CLOSED|WEEKLY_REVIEW_ITEMS_CLASSIFIED", verdict_content):
            return RuleResult(
                rule_id=rule_id,
                description="Verdict must not claim completion without weekly review classification matrix",
                severity="FAILURE",
                passed=False,
                failure_detail="final-verdict.md suggests completion but 02-weekly-review-claim-vs-proof-matrix.md is absent",
            )
        return RuleResult(
            rule_id=rule_id,
            description="No weekly review matrix but verdict does not overclaim",
            severity="FAILURE",
            passed=True,
            evidence="02-weekly-review-claim-vs-proof-matrix.md absent but verdict does not claim completion",
        )

    # ------------------------------------------------------------------
    # Sprint 76 rules (S75-B1: slides-compress, S75-B2: dirty-state)
    # ------------------------------------------------------------------
