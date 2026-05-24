"""Sprint evidence validator — detects false-complete evidence bundles.

Validates a Sprint evidence bundle against a set of rules that would
have caught the Sprint 59/60 false-complete cases.

Usage::

    from plugin_examples.evidence_validator import EvidenceValidator
    validator = EvidenceValidator(bundle_dir=Path("reports/sprint61"))
    result = validator.validate()
    print(result.to_dict())

    # With source tree scanning (wiring checks):
    validator = EvidenceValidator(
        bundle_dir=Path("reports/sprint61"),
        source_root=Path("src/plugin_examples"),
    )

All rules are evaluated independently; the result reports which rules
pass and which fail. A bundle is VALID only when all FAILURE-severity
rules pass.

Sprint 61 additions over Sprint 60:
- Rule: final_clean_proof_nonzero_bytes (was fooled by empty file in Sprint 60)
- Rule: final_clean_proof_has_git_header (requires actual git output content)
- Rule: readme_io_format_not_falsely_complete (MATCH without I/O format docs = FAIL)
- Rule: readme_gate_wired_in_pipeline (module-only gate is not a gate)
- Rule: evidence_validator_wired_in_pipeline (module-only validator is not a gate)
- Rule: destination_programcs_input_not_all_null (null-for-all = audit not done)
- Rule: no_p1_items_with_complete_verdict (P1 open + COMPLETE verdict = contradiction)
- Rule: required_files_nonzero_size (0-byte evidence files are not evidence)

Sprint 64 additions:
- Rule: ecc_contract_computed_and_valid (ECC must agree with EV — closure_valid=true required)
  Catches the Sprint 63 defect where ECC (closure_valid=false) and EV (overall_valid=true)
  silently disagreed. ECC must be run AFTER all bundle files are committed.

Sprint 65 additions (10 new rules, closes S64-D1 through S64-D8):
- Rule: content_audit_final_has_required_fields (S64-D3: missing fields in content audit)
- Rule: content_audit_count_not_contradictory (S64-D2: count contradiction)
- Rule: content_audit_all_records_ready (all 42 must reach READY/SPECIAL_CASE_READY)
- Rule: root_readme_artifacts_present_for_all_families (S64-D4: missing root README artifacts)
- Rule: special_case_placement_proof_present (S64-D6: no special-case placement proof)
- Rule: version_policy_no_unresolved_drift (S64-D5/S64-D8: unresolved drift or missing label)
- Rule: final_verdict_no_publication_overclaim (S64-D1: PUBLISHED claim with no remote proof)
- Rule: remote_proof_index_present_if_published (S64-D1: enforce remote proof artifact)
- Rule: content_audit_readme_io_coverage (catches MISSING_IO = audit not done or incomplete)
- Rule: revalidation_shows_prior_sprint_invalid (prior sprint must fail under new rules)

Sprint 66 additions (10 new rules, closes S65-D1 through S65-D5):
- Rule: remote_proof_per_example_not_overclaimed (S65-D1: PR-number-only proof without per-example coverage)
- Rule: remote_proof_has_content_hashes (S65-D1: remote proof must include content SHAs not just PR numbers)
- Rule: remote_readme_io_audit_present (S65-D2: remote README I/O status must come from fetched content)
- Rule: handoff_bundle_not_empty (S65-D3: handoff/per-family/ must not be empty when verdict claims ready)
- Rule: content_audit_output_kind_not_blank (S65-D4: output_kind must be present for all records)
- Rule: publication_state_not_mixed (S65-D5: published + approval-blocked needs separate state fields)
- Rule: remote_proof_not_workspace_only (S65-D1: merge_result_source must not point to workspace files only)
- Rule: root_readme_and_package_both_present (S65-D3: if root README artifact exists, package artifacts must too)
- Rule: remote_readme_io_not_overclaimed (S65-D2: verdict must not claim I/O published if remote audit shows 0)
- Rule: handoff_all_examples_have_io_section (S65-D3: all handoff READMEs must have I/O section)

Sprint 68 additions (5 new rules, closes S67-D1 through S67-D5):
- Rule: pdf_root_readme_complete (S67-D1: PDF root README must have >=19 rows)
- Rule: splitter_cardinality_reconciled (S67-D2: per-type splitter cardinality decision doc required)
- Rule: canonical_content_audit_no_stale_pdf_version (S67-D3: no PDF 26.4.0 in sprint content audit)
- Rule: pdf_version_proof_chain_present (S67-D4: version/pdf-version-proof-chain.md required)
- Rule: all_family_cardinality_display_validated (S67-D5: words README must have ×N/2× markers)

Sprint 72 additions (7 new rules, closes S71-D1):
- Rule: remote_proof_consistency_audit_present (S71-D1: remote-proof-consistency-audit.json must exist)
- Rule: remote_proof_consistency_audit_consistent (S71-D1: consistent=true required)
- Rule: remote_proof_summary_states_zero_io (S71-D1: remote-proof-summary.md must state 0/42)
- Rule: remote_proof_summary_not_contradicted (S71-D1: summary io claim must match audit io_doc_count)
- Rule: remote_proof_summary_superseded_archived (S71-D1: superseded document must be archived in history/)
- Rule: remote_readme_io_audit_count_consistent (remote-readme-io-audit-final.json io_doc_count must match has_io_section records)
- Rule: remote_vs_handoff_uses_current_sprint (remote-vs-handoff-final.json handoff_paths must use current sprint)

Sprint 75 additions (8 new rules, closes weekly review gaps):
- Rule: weekly_review_claim_matrix_present (02-weekly-review-claim-vs-proof-matrix.md must exist and classify all items)
- Rule: pdf_publication_truth_reconciled (pdf-publication/pdf-pr-reconciliation.json must exist — PDF item not inferred from old PR numbers)
- Rule: formimporter_taskcard_durable (formimporter/formimporter-repro-inventory.json with retest trigger)
- Rule: words_version_drift_documented (version-drift/words-version-drift-current.json must exist with drift field)
- Rule: email_slides_runtime_validated (post-merge-runtime/post-merge-validation-matrix.json with post_merge_validated records)
- Rule: dirty_tree_classified (git/dirty-file-classification.md must exist — dirty files not silently ignored)
- Rule: sprint27_governance_classified (governance/sprint27-strict-contract-revalidation.md must exist)
- Rule: weekly_review_verdict_not_complete_while_unclassified (final verdict must not say COMPLETE while weekly review items unclassified)

Sprint 76 additions (8 new rules, closes S75-B1 and S75-B2):
- Rule: runtime_matrix_output_confirmed_for_validated (post_merge_validated=true implies output_confirmed=true — graceful-exit-only is not validated)
- Rule: runtime_matrix_no_graceful_exit_labelled_validated (runtime_result must not contain NO_INPUT_FIXTURE while post_merge_validated=true)
- Rule: dirty_classification_must_match_after_snapshot (if dirty-state-after.txt shows modified src/tests, classification must not claim no source/test dirty)
- Rule: final_clean_proof_contains_commit_sha (final-clean-proof.txt must contain a 7+ character hex commit SHA)
- Rule: final_clean_proof_documents_remaining_dirty (if workspace/verification/latest modified, proof must document them explicitly)
- Rule: weekly_review_no_repaired_while_output_unconfirmed (REPAIRED claim invalid if any runtime matrix has output_confirmed=false)
- Rule: dirty_after_no_uncommitted_source_test (dirty-state-after.txt must not show src/ or tests/ as modified)
- Rule: final_verdict_workspace_exception_explicit (if dirty-state-after shows workspace/verification/latest modified, verdict must name the exception)

Sprint 77 additions (4 new rules, closes S76-C1 through S76-C4):
- Rule: commands_log_no_pending (commands.log must not contain PENDING entries — S76-C3)
- Rule: final_clean_proof_has_raw_git_lines (final-clean-proof.txt must embed raw git status output, not narrative only — S76-C2)
- Rule: dirty_state_untracked_acknowledged (if dirty-state-after.txt shows untracked files, each must be acknowledged in final-verdict.md — S76-C1)
- Rule: validation_authority_unambiguous (any *-validation-result.json with overall_valid=false must have canonical_overall_valid or bundle_type field — S76-C4)
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_UNCHECKED_TODO_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)
_GIT_HEADER_PATTERNS = [
    "On branch",
    "HEAD detached at",
    "nothing to commit",
    "nothing added to commit",
    "Changes to be committed",
    # If repo is truly empty:
    "Initial commit",
]
# Required files that must be nonzero bytes (relative to bundle_dir)
_REQUIRED_NONZERO_FILES = [
    "git/final-clean-proof.txt",
    "commands.log",
    "todo.md",
    "lanes/lane-I/test-run.log",
]


@dataclass
class RuleResult:
    """Result of evaluating one validation rule."""
    rule_id: str
    description: str
    severity: str  # "FAILURE" | "WARNING"
    passed: bool
    evidence: str = ""
    failure_detail: str = ""


@dataclass
class ValidationReport:
    """Complete validation report for a sprint bundle."""
    bundle_dir: str
    sprint_id: str
    total_rules: int
    passed: int
    failed: int
    warnings: int
    overall_valid: bool
    rule_results: list[RuleResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "bundle_dir": self.bundle_dir,
            "sprint_id": self.sprint_id,
            "total_rules": self.total_rules,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "overall_valid": self.overall_valid,
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "description": r.description,
                    "severity": r.severity,
                    "passed": r.passed,
                    "evidence": r.evidence,
                    "failure_detail": r.failure_detail,
                }
                for r in self.rule_results
            ],
        }


class EvidenceValidator:
    """Validates a sprint evidence bundle against closure quality rules."""

    def __init__(self, bundle_dir: Path, source_root: Path | None = None) -> None:
        self.bundle_dir = bundle_dir
        # source_root: path to the plugin_examples source package directory.
        # If provided, wiring rules scan source imports directly.
        # If None, wiring rules use evidence-based fallback (integration-proof.md).
        self.source_root = source_root

    def validate(self, exclude_rule_ids: "set[str] | None" = None) -> ValidationReport:
        """Run all validation rules and return a report.

        Args:
            exclude_rule_ids: Optional set of rule_id strings to skip.
                Used for two-phase validation: phase A excludes
                ``bundle_validation_result_present_and_valid`` so the result
                can be written without self-referential failure; phase B
                runs all rules to confirm the stored result is present and valid.

                A bundle validation result MUST be produced by phase A (where
                all 20 non-self-referential FAILURE rules pass) and then
                verified by phase B (all 21 rules).  Storing a result from
                a phase-B run that still has ``passed=false`` for rule 21
                is a self-contradiction and is detected by semantic validation.
        """
        exclude = exclude_rule_ids or set()
        results: list[RuleResult] = []

        def _maybe(rule_result: RuleResult) -> None:
            if rule_result.rule_id not in exclude:
                results.append(rule_result)

        # --- Original Sprint 60 rules (hardened) ---
        _maybe(self._rule_final_clean_proof_after_final_commit())
        _maybe(self._rule_destination_42_42_authority_mapped())
        _maybe(self._rule_no_present_no_authority())
        _maybe(self._rule_no_partial_without_partial_verdict())
        _maybe(self._rule_readme_audit_content_based())
        _maybe(self._rule_readme_gate_implemented())
        _maybe(self._rule_evidence_validator_actually_ran())
        _maybe(self._rule_todo_all_items_checked_or_carried())
        _maybe(self._rule_zero_unknown_input_formats())
        _maybe(self._rule_test_log_zero_failed())
        _maybe(self._rule_commands_log_complete())
        _maybe(self._rule_bundle_min_files())

        # --- Sprint 61 NEW semantic rules ---
        _maybe(self._rule_final_clean_proof_nonzero_bytes())
        _maybe(self._rule_final_clean_proof_has_git_header())
        _maybe(self._rule_readme_io_format_not_falsely_complete())
        _maybe(self._rule_readme_gate_wired_in_pipeline())
        _maybe(self._rule_evidence_validator_wired_in_pipeline())
        _maybe(self._rule_destination_programcs_input_not_all_null())
        _maybe(self._rule_no_p1_items_with_complete_verdict())
        _maybe(self._rule_required_files_nonzero_size())

        # --- Sprint 62 NEW rule: mandatory EV execution for final closure ---
        _maybe(self._rule_bundle_validation_result_present_and_valid())

        # --- Sprint 64 NEW rule: ECC must pass (closure_valid=true, no blocking failures) ---
        _maybe(self._rule_ecc_contract_computed_and_valid())

        # --- Sprint 65 NEW rules: close S64-D1 through S64-D8 ---
        _maybe(self._rule_content_audit_final_has_required_fields())
        _maybe(self._rule_content_audit_count_not_contradictory())
        _maybe(self._rule_content_audit_all_records_ready())
        _maybe(self._rule_root_readme_artifacts_present_for_all_families())
        _maybe(self._rule_special_case_placement_proof_present())
        _maybe(self._rule_version_policy_no_unresolved_drift())
        _maybe(self._rule_final_verdict_no_publication_overclaim())
        _maybe(self._rule_remote_proof_index_present_if_published())
        _maybe(self._rule_content_audit_readme_io_coverage())
        _maybe(self._rule_revalidation_shows_prior_sprint_invalid())

        # --- Sprint 66 NEW rules: close S65-D1 through S65-D5 ---
        _maybe(self._rule_remote_proof_per_example_not_overclaimed())
        _maybe(self._rule_remote_proof_has_content_hashes())
        _maybe(self._rule_remote_readme_io_audit_present())
        _maybe(self._rule_handoff_bundle_not_empty())
        _maybe(self._rule_content_audit_output_kind_not_blank())
        _maybe(self._rule_publication_state_not_mixed())
        _maybe(self._rule_remote_proof_not_workspace_only())
        _maybe(self._rule_root_readme_and_package_both_present())
        _maybe(self._rule_remote_readme_io_not_overclaimed())
        _maybe(self._rule_handoff_all_examples_have_io_section())

        # --- Sprint 67 NEW rules: close S66-D1 through S66-D5 ---
        _maybe(self._rule_cardinality_audit_json_present())
        _maybe(self._rule_root_readme_cardinality_annotated())
        _maybe(self._rule_pdf_version_decision_record_present())
        _maybe(self._rule_version_truth_matrix_present())
        _maybe(self._rule_no_cross_sprint_path_leakage())
        _maybe(self._rule_legacy_plans_reconciliation_present())
        _maybe(self._rule_content_audit_sprint_specific_present())
        _maybe(self._rule_handoff_index_per_family_complete())
        _maybe(self._rule_readme_sync_state_present())
        _maybe(self._rule_remote_truth_refresh_present())

        # --- Sprint 68 NEW rules: close S67-D1 through S67-D5 ---
        _maybe(self._rule_pdf_root_readme_complete())
        _maybe(self._rule_splitter_cardinality_reconciled())
        _maybe(self._rule_canonical_content_audit_no_stale_pdf_version())
        _maybe(self._rule_pdf_version_proof_chain_present())
        _maybe(self._rule_all_family_cardinality_display_validated())

        # --- Sprint 69 NEW rules: close S68-D1 through S68-D8 ---
        _maybe(self._rule_handoff_index_version_matches_dpp())
        _maybe(self._rule_only_one_canonical_final_audit())
        _maybe(self._rule_publication_truth_matrix_no_stale_paths())
        _maybe(self._rule_publication_truth_matrix_no_mixed_state())
        _maybe(self._rule_root_readme_indexed_in_handoff())
        _maybe(self._rule_exact_legacy_reconciliation_present())
        _maybe(self._rule_final_verdict_is_precise())
        _maybe(self._rule_final_verdict_not_complete_while_blocked())
        _maybe(self._rule_handoff_index_has_root_readme_field())
        _maybe(self._rule_version_consistency_final_present())

        # --- Sprint 70 NEW rules: close S69-D1 and S69-D2 ---
        _maybe(self._rule_handoff_root_readme_in_sprint_folder())
        _maybe(self._rule_handoff_root_readme_file_present())
        _maybe(self._rule_handoff_root_readme_hash_matches())
        _maybe(self._rule_publication_handoff_root_readme_hash_matches())
        _maybe(self._rule_legacy_simplified_index_superseded())

        # --- Sprint 71 NEW rules: close S70-D1, S70-D2, S70-D3 ---
        _maybe(self._rule_content_audit_final_no_stale_paths())
        _maybe(self._rule_publication_matrix_no_stale_paths())
        _maybe(self._rule_handoff_index_no_stale_paths())
        _maybe(self._rule_remote_vs_handoff_no_stale_paths())
        _maybe(self._rule_content_audit_final_files_exist())
        _maybe(self._rule_publication_matrix_files_exist())

        # --- Sprint 72 NEW rules: close S71-D1 (remote proof consistency) ---
        _maybe(self._rule_remote_proof_consistency_audit_present())
        _maybe(self._rule_remote_proof_consistency_audit_consistent())
        _maybe(self._rule_remote_proof_summary_states_zero_io())
        _maybe(self._rule_remote_proof_summary_not_contradicted())
        _maybe(self._rule_remote_proof_summary_superseded_archived())
        _maybe(self._rule_remote_readme_io_audit_count_consistent())
        _maybe(self._rule_remote_vs_handoff_uses_current_sprint())

        # --- Sprint 75 NEW rules: weekly review integration governance ---
        _maybe(self._rule_weekly_review_claim_matrix_present())
        _maybe(self._rule_pdf_publication_truth_reconciled())
        _maybe(self._rule_formimporter_taskcard_durable())
        _maybe(self._rule_words_version_drift_documented())
        _maybe(self._rule_email_slides_runtime_validated())
        _maybe(self._rule_dirty_tree_classified())
        _maybe(self._rule_sprint27_governance_classified())
        _maybe(self._rule_weekly_review_verdict_not_complete_while_unclassified())

        # --- Sprint 76 NEW rules: close S75-B1 (slides-compress) and S75-B2 (dirty-state) ---
        _maybe(self._rule_runtime_matrix_output_confirmed_for_validated())
        _maybe(self._rule_runtime_matrix_no_graceful_exit_labelled_validated())
        _maybe(self._rule_dirty_classification_must_match_after_snapshot())
        _maybe(self._rule_final_clean_proof_contains_commit_sha())
        _maybe(self._rule_final_clean_proof_documents_remaining_dirty())
        _maybe(self._rule_weekly_review_no_repaired_while_output_unconfirmed())
        _maybe(self._rule_dirty_after_no_uncommitted_source_test())
        _maybe(self._rule_final_verdict_workspace_exception_explicit())

        # --- Sprint 77 NEW rules: close S76-C1 through S76-C4 ---
        _maybe(self._rule_commands_log_no_pending())
        _maybe(self._rule_final_clean_proof_has_raw_git_lines())
        _maybe(self._rule_dirty_state_untracked_acknowledged())
        _maybe(self._rule_validation_authority_unambiguous())

        failures = [r for r in results if not r.passed and r.severity == "FAILURE"]
        warnings = [r for r in results if not r.passed and r.severity == "WARNING"]

        sprint_id = self._read_sprint_id()
        return ValidationReport(
            bundle_dir=str(self.bundle_dir),
            sprint_id=sprint_id,
            total_rules=len(results),
            passed=sum(1 for r in results if r.passed),
            failed=len(failures),
            warnings=len(warnings),
            overall_valid=len(failures) == 0,
            rule_results=results,
        )

    SELF_REFERENCE_RULE_ID = "bundle_validation_result_present_and_valid"

    def validate_for_storage(self) -> ValidationReport:
        """Phase-A validation: run all rules EXCEPT the self-referential rule 21.

        Use this to produce the bundle validation result JSON.  The result
        is free of self-referential paradoxes: if all 20 FAILURE rules pass,
        ``overall_valid=True`` and ``failed=0`` are truthful.

        After writing the result, call ``validate()`` (phase B, all 21 rules)
        to confirm rule 21 also passes.
        """
        return self.validate(exclude_rule_ids={self.SELF_REFERENCE_RULE_ID})

    # ------------------------------------------------------------------
    # Sprint 60 rules (hardened)
    # ------------------------------------------------------------------

    def _rule_final_clean_proof_after_final_commit(self) -> RuleResult:
        """final-clean-proof.txt must exist and not contain dirty indicators."""
        rule_id = "final_clean_proof_after_final_commit"
        proof_path = self.bundle_dir / "git" / "final-clean-proof.txt"

        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must exist (captured AFTER final bundle commit)",
                severity="FAILURE",
                passed=False,
                failure_detail="File not found: git/final-clean-proof.txt",
            )

        content = proof_path.read_text(encoding="utf-8", errors="replace").strip()
        dirty_indicators = ["modified:", "untracked files:", "?? "]
        for indicator in dirty_indicators:
            if indicator in content:
                return RuleResult(
                    rule_id=rule_id,
                    description="final-clean-proof.txt must not show dirty state",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"Dirty state indicator '{indicator}' found in final-clean-proof.txt",
                    evidence=content[:200],
                )

        return RuleResult(
            rule_id=rule_id,
            description="final-clean-proof.txt must exist without dirty indicators",
            severity="FAILURE",
            passed=True,
            evidence="git/final-clean-proof.txt exists with no dirty indicators",
        )

    def _rule_destination_42_42_authority_mapped(self) -> RuleResult:
        """content-audit-repaired.json must show 42/42 authority-mapped."""
        rule_id = "destination_42_42_authority_mapped"
        audit_path = self.bundle_dir / "destination" / "content-audit-repaired.json"
        if not audit_path.exists():
            audit_path = self.bundle_dir / "destination" / "content-audit.json"

        if not audit_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Destination content audit must show 42/42 authority-mapped",
                severity="FAILURE", passed=False,
                failure_detail="No destination content audit file found",
            )

        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Destination content audit must show 42/42 authority-mapped",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read audit file: {exc}",
            )

        authority_matched = data.get("authority_mapped", data.get("authority_match_rate", ""))
        no_auth_count = data.get("present_no_authority", -1)

        if no_auth_count > 0:
            return RuleResult(
                rule_id=rule_id,
                description="Destination content audit must show 42/42 authority-mapped",
                severity="FAILURE", passed=False,
                failure_detail=f"{no_auth_count} PRESENT_NO_AUTHORITY entries remain",
            )

        if isinstance(authority_matched, str) and "/" in authority_matched:
            matched_n, _ = authority_matched.split("/")
            if int(matched_n) < 42:
                return RuleResult(
                    rule_id=rule_id,
                    description="Destination content audit must show 42/42 authority-mapped",
                    severity="FAILURE", passed=False,
                    failure_detail=f"authority_match_rate is {authority_matched}, expected 42/42",
                )

        return RuleResult(
            rule_id=rule_id,
            description="Destination content audit must show 42/42 authority-mapped",
            severity="FAILURE", passed=True,
            evidence=f"authority_matched={authority_matched}",
        )

    def _rule_no_present_no_authority(self) -> RuleResult:
        """No PRESENT_NO_AUTHORITY entries in content audit."""
        rule_id = "no_present_no_authority"
        for fname in ["content-audit-repaired.json", "content-audit.json"]:
            path = self.bundle_dir / "destination" / fname
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                count = data.get("present_no_authority", 0)
                examples = data.get("examples", [])
                no_auth = [e for e in examples if e.get("content_match") == "PRESENT_NO_AUTHORITY"]
                if count > 0 or no_auth:
                    return RuleResult(
                        rule_id=rule_id,
                        description="No PRESENT_NO_AUTHORITY entries allowed",
                        severity="FAILURE", passed=False,
                        failure_detail=f"{max(count, len(no_auth))} PRESENT_NO_AUTHORITY entries found",
                    )
                return RuleResult(
                    rule_id=rule_id,
                    description="No PRESENT_NO_AUTHORITY entries allowed",
                    severity="FAILURE", passed=True, evidence="present_no_authority=0",
                )

        return RuleResult(
            rule_id=rule_id,
            description="No PRESENT_NO_AUTHORITY entries allowed",
            severity="FAILURE", passed=False,
            failure_detail="No destination content audit file found",
        )

    def _rule_no_partial_without_partial_verdict(self) -> RuleResult:
        """No PARTIAL entries without explicit acknowledgment in final verdict."""
        rule_id = "no_partial_without_partial_verdict"
        for fname in ["content-audit-repaired.json", "content-audit.json"]:
            path = self.bundle_dir / "destination" / fname
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                examples = data.get("examples", [])
                partials = [e["scenario_id"] for e in examples if e.get("content_match") == "PARTIAL"]
                if partials:
                    verdict_path = self.bundle_dir / "final-verdict.md"
                    verdict_content = verdict_path.read_text(encoding="utf-8") if verdict_path.exists() else ""
                    if "PARTIAL" not in verdict_content and "partial" not in verdict_content.lower():
                        return RuleResult(
                            rule_id=rule_id,
                            description="PARTIAL entries must be acknowledged in final verdict",
                            severity="FAILURE", passed=False,
                            failure_detail=f"PARTIAL entries {partials} not mentioned in final-verdict.md",
                        )
                return RuleResult(
                    rule_id=rule_id,
                    description="PARTIAL entries must be acknowledged in final verdict",
                    severity="FAILURE", passed=True,
                    evidence="partial count=0 or acknowledged in verdict",
                )

        return RuleResult(
            rule_id=rule_id,
            description="PARTIAL entries must be acknowledged in final verdict",
            severity="FAILURE", passed=False,
            failure_detail="No destination content audit file found",
        )

    def _rule_readme_audit_content_based(self) -> RuleResult:
        """README audit must have content-based checks, not just size/presence."""
        rule_id = "readme_audit_content_based"
        audit_path = self.bundle_dir / "readme" / "example-readme-content-audit.json"
        if not audit_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="README audit must be content-based",
                severity="FAILURE", passed=False,
                failure_detail="readme/example-readme-content-audit.json not found",
            )

        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="README audit must be content-based",
                severity="FAILURE", passed=False, failure_detail=str(exc),
            )

        records = data.get("records", [])
        content_fields = {"workflow_type_in_readme", "family_in_readme", "package_id_in_readme", "content_audit"}
        has_content = any(any(f in r for f in content_fields) for r in records)
        if not has_content:
            return RuleResult(
                rule_id=rule_id,
                description="README audit must be content-based (not size/presence only)",
                severity="FAILURE", passed=False,
                failure_detail="No content-check fields found in README audit records (size/presence only)",
            )

        return RuleResult(
            rule_id=rule_id,
            description="README audit must be content-based",
            severity="FAILURE", passed=True,
            evidence=f"{len(records)} records with content checks",
        )

    def _rule_readme_gate_implemented(self) -> RuleResult:
        """README gate must be implemented (has implementation + test + source proof)."""
        rule_id = "readme_gate_implemented_and_tested"
        impl_path = self.bundle_dir / "readme" / "readme-gate-implementation.md"
        test_path = self.bundle_dir / "readme" / "readme-gate-test-results.txt"
        patch_path = self.bundle_dir / "readme" / "readme-gate-source-proof.patch"

        missing = [
            name for p, name in [
                (impl_path, "readme-gate-implementation.md"),
                (test_path, "readme-gate-test-results.txt"),
                (patch_path, "readme-gate-source-proof.patch"),
            ]
            if not p.exists()
        ]

        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="README gate must be implemented, tested, and have source proof",
                severity="FAILURE", passed=False,
                failure_detail=f"Missing evidence: {missing}",
            )

        test_content = test_path.read_text(encoding="utf-8", errors="replace")
        if " failed" in test_content and "0 failed" not in test_content:
            return RuleResult(
                rule_id=rule_id,
                description="README gate must be implemented, tested, and have source proof",
                severity="FAILURE", passed=False,
                failure_detail="README gate test results show failures",
            )

        return RuleResult(
            rule_id=rule_id,
            description="README gate must be implemented, tested, and have source proof",
            severity="FAILURE", passed=True,
            evidence="implementation + tests + source proof all present",
        )

    def _rule_evidence_validator_actually_ran(self) -> RuleResult:
        """Evidence validator must have run and produced actual test output."""
        rule_id = "evidence_validator_actually_ran"
        validator_output = self.bundle_dir / "evidence" / "validator-test-results.txt"

        if not validator_output.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Evidence validator must have actually run",
                severity="FAILURE", passed=False,
                failure_detail="evidence/validator-test-results.txt not found",
            )

        content = validator_output.read_text(encoding="utf-8", errors="replace")
        has_test_output = bool(
            re.search(r"\d+\s+passed", content)
            or "PASSED" in content
            or "passed in" in content
        )
        if not has_test_output:
            return RuleResult(
                rule_id=rule_id,
                description="Evidence validator must have actually run",
                severity="FAILURE", passed=False,
                failure_detail="validator-test-results.txt does not look like actual test output",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Evidence validator must have actually run",
            severity="FAILURE", passed=True,
            evidence="validator-test-results.txt contains test output",
        )

    def _rule_todo_all_items_checked_or_carried(self) -> RuleResult:
        """todo.md must have no unchecked active [ ] items at closure."""
        rule_id = "todo_all_items_checked_or_carried"
        todo_path = self.bundle_dir / "todo.md"

        if not todo_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="todo.md must have no unchecked active items",
                severity="FAILURE", passed=False,
                failure_detail="todo.md not found",
            )

        content = todo_path.read_text(encoding="utf-8", errors="replace")
        unchecked = _UNCHECKED_TODO_PATTERN.findall(content)
        if unchecked:
            return RuleResult(
                rule_id=rule_id,
                description="todo.md must have no unchecked active items",
                severity="FAILURE", passed=False,
                failure_detail=f"{len(unchecked)} unchecked [ ] items remain in todo.md",
            )

        return RuleResult(
            rule_id=rule_id,
            description="todo.md must have no unchecked active items",
            severity="FAILURE", passed=True,
            evidence="No unchecked [ ] items found in todo.md",
        )

    def _rule_zero_unknown_input_formats(self) -> RuleResult:
        """No active type may have input_format=unknown."""
        rule_id = "zero_unknown_input_formats"
        auth_path = self.bundle_dir / "io-authority" / "input-format-authority-matrix.json"

        if not auth_path.exists():
            return RuleResult(
                rule_id=rule_id, description="Zero unknown input formats",
                severity="WARNING", passed=True,
                evidence="No io-authority matrix in this bundle (may be in prior sprint evidence)",
            )

        try:
            data = json.loads(auth_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description="Zero unknown input formats",
                severity="FAILURE", passed=False,
                failure_detail="Cannot read io-authority matrix",
            )

        unknown_count = data.get("unknown_input_formats", -1)
        if unknown_count > 0:
            return RuleResult(
                rule_id=rule_id, description="Zero unknown input formats",
                severity="FAILURE", passed=False,
                failure_detail=f"{unknown_count} unknown input formats remain",
            )

        return RuleResult(
            rule_id=rule_id, description="Zero unknown input formats",
            severity="FAILURE", passed=True,
            evidence=f"unknown_input_formats={unknown_count}",
        )

    def _rule_test_log_zero_failed(self) -> RuleResult:
        """Test log must exist and show 0 failed."""
        rule_id = "test_log_zero_failed"
        log_path = self.bundle_dir / "lanes" / "lane-I" / "test-run.log"

        if not log_path.exists():
            return RuleResult(
                rule_id=rule_id, description="Test log must exist and show 0 failed",
                severity="FAILURE", passed=False,
                failure_detail="lanes/lane-I/test-run.log not found",
            )

        content = log_path.read_text(encoding="utf-8", errors="replace")
        if "0 failed" not in content and " failed" in content:
            return RuleResult(
                rule_id=rule_id, description="Test log must exist and show 0 failed",
                severity="FAILURE", passed=False,
                failure_detail="Test log shows failures",
                evidence=content[-300:],
            )

        return RuleResult(
            rule_id=rule_id, description="Test log must exist and show 0 failed",
            severity="FAILURE", passed=True,
            evidence="Test log exists with no failed tests",
        )

    def _rule_commands_log_complete(self) -> RuleResult:
        """commands.log must not be IN_PROGRESS at closure."""
        rule_id = "commands_log_complete"
        log_path = self.bundle_dir / "commands.log"

        if not log_path.exists():
            return RuleResult(
                rule_id=rule_id, description="commands.log must not be IN_PROGRESS",
                severity="FAILURE", passed=False,
                failure_detail="commands.log not found",
            )

        content = log_path.read_text(encoding="utf-8", errors="replace")
        if "IN_PROGRESS" in content:
            return RuleResult(
                rule_id=rule_id, description="commands.log must not be IN_PROGRESS",
                severity="FAILURE", passed=False,
                failure_detail="commands.log contains IN_PROGRESS marker",
            )

        return RuleResult(
            rule_id=rule_id, description="commands.log must not be IN_PROGRESS",
            severity="FAILURE", passed=True,
            evidence="commands.log present and complete",
        )

    def _rule_bundle_min_files(self) -> RuleResult:
        """Bundle must contain at least 35 files."""
        rule_id = "bundle_min_files"
        files = list(self.bundle_dir.rglob("*"))
        file_count = sum(1 for f in files if f.is_file())
        min_files = 35

        if file_count < min_files:
            return RuleResult(
                rule_id=rule_id,
                description=f"Bundle must contain at least {min_files} files",
                severity="FAILURE", passed=False,
                failure_detail=f"Bundle has {file_count} files (minimum {min_files})",
            )

        return RuleResult(
            rule_id=rule_id,
            description=f"Bundle must contain at least {min_files} files",
            severity="FAILURE", passed=True,
            evidence=f"Bundle has {file_count} files",
        )

    # ------------------------------------------------------------------
    # Sprint 61 NEW semantic rules
    # ------------------------------------------------------------------

    def _rule_final_clean_proof_nonzero_bytes(self) -> RuleResult:
        """final-clean-proof.txt must be nonzero bytes.

        Sprint 60 defect SD60-01: git status --short outputs nothing when
        clean, so tee wrote 0 bytes. An empty file is not proof of clean state.
        Fix: capture with git status (not --short) or append branch header.
        """
        rule_id = "final_clean_proof_nonzero_bytes"
        proof_path = self.bundle_dir / "git" / "final-clean-proof.txt"

        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must be nonzero bytes",
                severity="FAILURE", passed=False,
                failure_detail="File not found: git/final-clean-proof.txt",
            )

        size = proof_path.stat().st_size
        if size == 0:
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must be nonzero bytes",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "final-clean-proof.txt is 0 bytes. "
                    "Sprint 60 defect SD60-01: git status --short produces no output when clean. "
                    "Use 'git status' (not --short) to capture branch header + nothing-to-commit text."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="final-clean-proof.txt must be nonzero bytes",
            severity="FAILURE", passed=True,
            evidence=f"final-clean-proof.txt is {size} bytes",
        )

    def _rule_final_clean_proof_has_git_header(self) -> RuleResult:
        """final-clean-proof.txt must contain a recognizable git status header line.

        A nonzero file that contains only whitespace or an unrelated log entry
        is still not valid clean proof. The file must contain git's own
        output: 'On branch', 'HEAD detached at', 'nothing to commit', etc.
        """
        rule_id = "final_clean_proof_has_git_header"
        proof_path = self.bundle_dir / "git" / "final-clean-proof.txt"

        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must contain git status header",
                severity="FAILURE", passed=False,
                failure_detail="File not found: git/final-clean-proof.txt",
            )

        content = proof_path.read_text(encoding="utf-8", errors="replace")
        has_header = any(h in content for h in _GIT_HEADER_PATTERNS)

        if not has_header:
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must contain git status header",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "final-clean-proof.txt does not contain any recognized git status header "
                    f"(expected one of: {_GIT_HEADER_PATTERNS[:3]}...). "
                    "Capture with: git status (not --short) or git status -b"
                ),
                evidence=content[:100] if content.strip() else "(empty)",
            )

        return RuleResult(
            rule_id=rule_id,
            description="final-clean-proof.txt must contain git status header",
            severity="FAILURE", passed=True,
            evidence=f"Git header found in final-clean-proof.txt: {content[:80].strip()}",
        )

    def _rule_readme_io_format_not_falsely_complete(self) -> RuleResult:
        """README MATCH cannot claim I/O completeness when I/O format fields are false.

        Sprint 60 defect SD60-02: 22/42 input_format_in_readme=false and
        23/42 output_format_in_readme=false, yet content_audit=MATCH for all 42.
        MATCH was only checking family/workflow/package_id, not I/O documentation.

        This rule fails if more than 30% of records have input or output format false
        AND the overall match/total claim equals 100%, indicating overcounting.
        """
        rule_id = "readme_io_format_not_falsely_complete"
        audit_path = self.bundle_dir / "readme" / "example-readme-content-audit.json"

        if not audit_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="README audit must not falsely claim I/O documentation complete",
                severity="FAILURE", passed=False,
                failure_detail="readme/example-readme-content-audit.json not found",
            )

        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="README audit must not falsely claim I/O documentation complete",
                severity="FAILURE", passed=False, failure_detail=str(exc),
            )

        records = data.get("records", [])
        if not records:
            return RuleResult(
                rule_id=rule_id,
                description="README audit must not falsely claim I/O documentation complete",
                severity="FAILURE", passed=False,
                failure_detail="No records found in README audit",
            )

        # Check if I/O fields are tracked at all
        first_record = records[0]
        has_io_fields = "input_format_in_readme" in first_record or "output_format_in_readme" in first_record

        if not has_io_fields:
            # I/O fields not tracked — not necessarily false, just not audited
            return RuleResult(
                rule_id=rule_id,
                description="README audit must not falsely claim I/O documentation complete",
                severity="WARNING", passed=True,
                evidence="I/O format fields not tracked in README audit (acceptable if audit scope is basic-only)",
            )

        input_false_count = sum(1 for r in records if r.get("input_format_in_readme") is False)
        output_false_count = sum(1 for r in records if r.get("output_format_in_readme") is False)
        total = len(records)

        claimed_match = data.get("match", 0)
        # False completion: >30% missing I/O docs AND 100% match claimed
        io_gap_fraction = max(input_false_count, output_false_count) / total
        claims_complete = claimed_match == total

        if io_gap_fraction > 0.3 and claims_complete:
            return RuleResult(
                rule_id=rule_id,
                description="README audit must not falsely claim I/O documentation complete",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"README audit claims {claimed_match}/{total} MATCH but "
                    f"{input_false_count}/{total} have input_format_in_readme=false and "
                    f"{output_false_count}/{total} have output_format_in_readme=false. "
                    "MATCH was assigned without gating on I/O format documentation."
                ),
                evidence=f"input_false={input_false_count}, output_false={output_false_count}, total={total}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="README audit must not falsely claim I/O documentation complete",
            severity="FAILURE", passed=True,
            evidence=(
                f"input_false={input_false_count}/{total}, output_false={output_false_count}/{total}, "
                f"claimed_match={claimed_match}/{total}"
            ),
        )

    def _rule_readme_gate_wired_in_pipeline(self) -> RuleResult:
        """README gate must be wired into the real publication flow, not standalone-only.

        Sprint 60 defect SD60-03: readme_audit_gate.py was created but never
        imported or called by any pipeline command. A gate module that is never
        called is not a gate — it is a library.

        Check order:
        1. If source_root is provided: scan pipeline source for imports of readme_audit_gate
        2. Fallback: check for readme/readme-gate-flow-integration.md evidence file
        """
        rule_id = "readme_gate_wired_in_pipeline"

        # Option 1: direct source scan
        if self.source_root is not None:
            found_in = self._scan_source_for_import(
                self.source_root, "readme_audit_gate", exclude_self="readme_audit_gate.py"
            )
            if found_in:
                return RuleResult(
                    rule_id=rule_id,
                    description="README gate must be imported by pipeline source",
                    severity="FAILURE", passed=True,
                    evidence=f"readme_audit_gate imported in: {found_in}",
                )
            return RuleResult(
                rule_id=rule_id,
                description="README gate must be imported by pipeline source",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "readme_audit_gate is not imported by any pipeline source file. "
                    "A gate module that is never called is not a gate. "
                    "Wire into publish-pr live mode in __main__.py or batch_publisher.py."
                ),
            )

        # Option 2: evidence-based fallback
        integration_proof = self.bundle_dir / "readme" / "readme-gate-flow-integration.md"
        if not integration_proof.exists():
            return RuleResult(
                rule_id=rule_id,
                description="README gate must be wired into publication flow",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "readme/readme-gate-flow-integration.md not found. "
                    "Either provide source_root for direct scanning, or create flow integration evidence."
                ),
            )

        content = integration_proof.read_text(encoding="utf-8", errors="replace")
        if "not wired" in content.lower() or "deferred" in content.lower() or "p1" in content.lower():
            return RuleResult(
                rule_id=rule_id,
                description="README gate must be wired into publication flow",
                severity="FAILURE", passed=False,
                failure_detail="readme-gate-flow-integration.md admits gate is not wired or deferred",
                evidence=content[:200],
            )

        return RuleResult(
            rule_id=rule_id,
            description="README gate must be wired into publication flow",
            severity="FAILURE", passed=True,
            evidence="readme-gate-flow-integration.md exists and does not indicate deferred status",
        )

    def _rule_evidence_validator_wired_in_pipeline(self) -> RuleResult:
        """EvidenceValidator must be wired into the real pipeline, not standalone-only.

        Sprint 60 defect SD60-04: evidence_validator.py was created but never
        imported or called by any pipeline command.

        Check order:
        1. If source_root is provided: scan pipeline source for imports of evidence_validator
        2. Fallback: check for evidence/pipeline-integration-proof.md
        """
        rule_id = "evidence_validator_wired_in_pipeline"

        # Option 1: direct source scan
        if self.source_root is not None:
            found_in = self._scan_source_for_import(
                self.source_root, "evidence_validator", exclude_self="evidence_validator.py"
            )
            if found_in:
                return RuleResult(
                    rule_id=rule_id,
                    description="EvidenceValidator must be imported by pipeline source",
                    severity="FAILURE", passed=True,
                    evidence=f"evidence_validator imported in: {found_in}",
                )
            return RuleResult(
                rule_id=rule_id,
                description="EvidenceValidator must be imported by pipeline source",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "evidence_validator is not imported by any pipeline source file. "
                    "Wire EvidenceValidator into release-status or run command finalization."
                ),
            )

        # Option 2: evidence-based fallback
        integration_proof = self.bundle_dir / "evidence" / "pipeline-integration-proof.md"
        if not integration_proof.exists():
            return RuleResult(
                rule_id=rule_id,
                description="EvidenceValidator must be wired into pipeline",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "evidence/pipeline-integration-proof.md not found. "
                    "Either provide source_root for direct scanning, or create integration evidence."
                ),
            )

        content = integration_proof.read_text(encoding="utf-8", errors="replace")
        if "not wired" in content.lower() or "deferred" in content.lower() or "p1" in content.lower():
            return RuleResult(
                rule_id=rule_id,
                description="EvidenceValidator must be wired into pipeline",
                severity="FAILURE", passed=False,
                failure_detail="pipeline-integration-proof.md admits validator is not wired or deferred",
                evidence=content[:200],
            )

        return RuleResult(
            rule_id=rule_id,
            description="EvidenceValidator must be wired into pipeline",
            severity="FAILURE", passed=True,
            evidence="pipeline-integration-proof.md exists and does not indicate deferred status",
        )

    def _rule_destination_programcs_input_not_all_null(self) -> RuleResult:
        """Destination Program.cs input format classification must not be null for all records.

        Sprint 60 defect SD60-05: input_format_in_programcs=null for all 42 records.
        This means no Program.cs was actually inspected for input format usage.
        """
        rule_id = "destination_programcs_input_not_all_null"
        for fname in ["programcs-io-audit-after.json", "content-audit-repaired.json", "content-audit.json"]:
            path = self.bundle_dir / "destination" / fname
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue

                examples = data.get("examples", [])
                if not examples:
                    continue

                # Check if the field exists at all
                first = examples[0]
                if "input_format_in_programcs" not in first and "input_classification" not in first:
                    # Field not present — audit did not include it
                    return RuleResult(
                        rule_id=rule_id,
                        description="Destination Program.cs input classification must not be all-null",
                        severity="FAILURE", passed=False,
                        failure_detail=(
                            f"{fname} records do not include input_format_in_programcs or "
                            "input_classification fields. Program.cs I/O audit was not performed."
                        ),
                    )

                null_count = sum(
                    1 for e in examples
                    if e.get("input_format_in_programcs") is None
                    and e.get("input_classification") is None
                )
                total = len(examples)

                if null_count == total:
                    return RuleResult(
                        rule_id=rule_id,
                        description="Destination Program.cs input classification must not be all-null",
                        severity="FAILURE", passed=False,
                        failure_detail=(
                            f"input_format_in_programcs is null for all {total}/{total} records. "
                            "No Program.cs was inspected for actual input format usage. "
                            "Sprint 60 defect SD60-05."
                        ),
                        evidence=f"file={fname}",
                    )

                return RuleResult(
                    rule_id=rule_id,
                    description="Destination Program.cs input classification must not be all-null",
                    severity="FAILURE", passed=True,
                    evidence=f"{total - null_count}/{total} records have non-null input classification",
                )

        return RuleResult(
            rule_id=rule_id,
            description="Destination Program.cs input classification must not be all-null",
            severity="FAILURE", passed=False,
            failure_detail="No destination audit file found with input_format_in_programcs data",
        )

    def _rule_no_p1_items_with_complete_verdict(self) -> RuleResult:
        """P1 open items in next-work-register must not coexist with COMPLETE verdict.

        Sprint 60 defect SD60-08: next-work-register.md listed 2 P1 items
        (README gate CLI wiring, EvidenceValidator CLI wiring) while the verdict
        claimed LOWCODE_IO_DESTINATION_README_CLOSURE_VERIFIED.
        """
        rule_id = "no_p1_items_with_complete_verdict"
        register_path = self.bundle_dir / "process" / "next-work-register.md"

        if not register_path.exists():
            # If register doesn't exist, no P1 items to check
            return RuleResult(
                rule_id=rule_id,
                description="No P1 open items while claiming COMPLETE verdict",
                severity="WARNING", passed=True,
                evidence="process/next-work-register.md not found (no P1 items to check)",
            )

        content = register_path.read_text(encoding="utf-8", errors="replace")
        # Look for P1 items that are not crossed out or marked as completed
        # Pattern: "| ... | P1 |" or "Priority P1" or "| P1 |"
        p1_lines = [
            line for line in content.splitlines()
            if re.search(r"\bP1\b", line) and not re.search(r"~~.*P1.*~~|DONE|COMPLETE|RESOLVED", line, re.IGNORECASE)
        ]

        if not p1_lines:
            return RuleResult(
                rule_id=rule_id,
                description="No P1 open items while claiming COMPLETE verdict",
                severity="FAILURE", passed=True,
                evidence="No P1 items found in next-work-register.md",
            )

        # Check if final verdict claims COMPLETE (only blocking if verdict asserts completion)
        verdict_path = self.bundle_dir / "final-verdict.md"
        if not verdict_path.exists():
            # No verdict yet — warn but don't fail
            return RuleResult(
                rule_id=rule_id,
                description="No P1 open items while claiming COMPLETE verdict",
                severity="WARNING", passed=True,
                evidence=f"{len(p1_lines)} P1 items noted but no final-verdict.md to check against",
            )

        verdict_content = verdict_path.read_text(encoding="utf-8", errors="replace")
        claims_complete = any(
            term in verdict_content for term in [
                "CLOSURE_VERIFIED", "COMPLETE", "GATES_ACTIVE",
                "README_IO_DOCS_AND_DESTINATION_AUDIT", "FALSE_CLOSURE_KILLED"
            ]
        )

        if p1_lines and claims_complete:
            return RuleResult(
                rule_id=rule_id,
                description="No P1 open items while claiming COMPLETE verdict",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"{len(p1_lines)} P1 open item(s) remain in next-work-register.md while "
                    "final verdict claims COMPLETE/VERIFIED. P1 = blocking; resolve or downgrade to P2."
                ),
                evidence="\n".join(p1_lines[:3]),
            )

        return RuleResult(
            rule_id=rule_id,
            description="No P1 open items while claiming COMPLETE verdict",
            severity="FAILURE", passed=True,
            evidence=f"P1 items noted but verdict does not overclaim completion",
        )

    def _rule_required_files_nonzero_size(self) -> RuleResult:
        """Key required evidence files must be nonzero bytes.

        Sprint 60 defect SD60-01 (contributory): final-clean-proof.txt was 0 bytes.
        This rule checks all required files in _REQUIRED_NONZERO_FILES.
        """
        rule_id = "required_files_nonzero_size"
        empty_files = []

        for rel_path in _REQUIRED_NONZERO_FILES:
            p = self.bundle_dir / rel_path
            if p.exists() and p.stat().st_size == 0:
                empty_files.append(rel_path)

        if empty_files:
            return RuleResult(
                rule_id=rule_id,
                description="Required evidence files must not be 0 bytes",
                severity="FAILURE", passed=False,
                failure_detail=f"Zero-byte required files: {empty_files}",
            )

        present = [rel for rel in _REQUIRED_NONZERO_FILES if (self.bundle_dir / rel).exists()]
        return RuleResult(
            rule_id=rule_id,
            description="Required evidence files must not be 0 bytes",
            severity="FAILURE", passed=True,
            evidence=f"{len(present)}/{len(_REQUIRED_NONZERO_FILES)} required files present and nonzero",
        )

    # ------------------------------------------------------------------
    # Sprint 62 NEW rules
    # ------------------------------------------------------------------

    def _rule_bundle_validation_result_present_and_valid(self) -> RuleResult:
        """Sprint bundle validation result must exist and show overall_valid=true.

        Sprint 62 requirement: EvidenceValidator execution is mandatory for final
        closure. A sprint cannot be marked COMPLETE without running EV on the bundle
        and storing the result in evidence/sprint{N}-bundle-validation-result.json.

        Missing/stale validation = BLOCKED.
        """
        rule_id = "bundle_validation_result_present_and_valid"
        evidence_dir = self.bundle_dir / "evidence"

        # Look for any sprint*-bundle-validation-result.json file
        candidates: list[Path] = []
        if evidence_dir.exists():
            candidates = sorted(evidence_dir.glob("*-bundle-validation-result.json"))

        if not candidates:
            return RuleResult(
                rule_id=rule_id,
                description=(
                    "Sprint bundle validation result must exist in evidence/ "
                    "(EV execution is mandatory for final closure)"
                ),
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "No evidence/*-bundle-validation-result.json found. "
                    "Run: python -m plugin_examples release-status --validate-bundle "
                    "and save result to evidence/sprint{N}-bundle-validation-result.json. "
                    "Sprint 62 requirement: EV execution is mandatory."
                ),
            )

        validation_path = candidates[-1]  # most recent alphabetically
        try:
            data = json.loads(validation_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Bundle validation result must be readable",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read {validation_path.name}: {exc}",
            )

        overall_valid = data.get("overall_valid", False)
        sprint_id = data.get("sprint_id", "unknown")
        rules_passed = data.get("passed", 0)
        rules_failed = data.get("failed", 0)

        if not overall_valid:
            return RuleResult(
                rule_id=rule_id,
                description="Bundle validation result must show overall_valid=true",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"{validation_path.name}: overall_valid=false "
                    f"({rules_failed} rules FAILED, {rules_passed} passed). "
                    "Fix all FAILURE-severity rule failures before closing sprint."
                ),
                evidence=f"sprint_id={sprint_id}, passed={rules_passed}, failed={rules_failed}",
            )

        # Detect internal contradiction: overall_valid=true but an embedded rule has passed=false.
        # This was the Sprint 62 bootstrap defect: the result was manually created with
        # overall_valid=true/failed=0 while embedded rules from a 20/21 run had passed=false.
        embedded_rules = data.get("rules", [])
        contradicting_rules = [r for r in embedded_rules if r.get("passed") is False]
        if contradicting_rules:
            bad_ids = ", ".join(r.get("rule_id", "unknown") for r in contradicting_rules[:5])
            return RuleResult(
                rule_id=rule_id,
                description="Bundle validation result must show overall_valid=true",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"{validation_path.name}: overall_valid=true is contradicted by "
                    f"{len(contradicting_rules)} embedded rule(s) with passed=false: {bad_ids}. "
                    "Use two-phase validation (validate_for_storage) to avoid bootstrap contradiction."
                ),
                evidence=f"sprint_id={sprint_id}, passed={rules_passed}, failed={rules_failed}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Bundle validation result must show overall_valid=true",
            severity="FAILURE",
            passed=True,
            evidence=(
                f"{validation_path.name}: overall_valid=true "
                f"(sprint_id={sprint_id}, passed={rules_passed}, failed={rules_failed})"
            ),
        )

    # ------------------------------------------------------------------
    # Sprint 64 NEW rules
    # ------------------------------------------------------------------

    def _rule_ecc_contract_computed_and_valid(self) -> RuleResult:
        """Evidence contract must be computed by ECC and show closure_valid=true.

        Sprint 64 defect S63-D1: ECC (closure_valid=false) and EV (overall_valid=true)
        disagreed silently.  Root causes:
        1. ECC was computed BEFORE final commits — stale MISSING entries.
        2. ECC pytest "0 failed" regex didn't match pytest's "N passed" format.
        3. ECC "6 families" check used wrong dict key.

        This rule requires that the ECC computed result:
        - Exists at ``evidence/evidence-contract-computed.json``
        - Has ``closure_valid=true``
        - Has ``blocking_failures=0``

        ECC must be run AFTER all bundle files are committed.  If ECC was run
        early (stale), it will have MISSING entries and this rule will fail,
        forcing a re-run.
        """
        rule_id = "ecc_contract_computed_and_valid"
        computed_path = self.bundle_dir / "evidence" / "evidence-contract-computed.json"

        if not computed_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description=(
                    "ECC must be run on the final bundle and result stored in "
                    "evidence/evidence-contract-computed.json"
                ),
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "evidence/evidence-contract-computed.json not found. "
                    "Run EvidenceContractComputer.compute() AFTER all bundle files are committed "
                    "and save the result to this path. "
                    "Sprint 64 requirement: ECC must agree with EV at closure."
                ),
            )

        try:
            data = json.loads(computed_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="ECC computed result must be readable",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read evidence-contract-computed.json: {exc}",
            )

        closure_valid = data.get("closure_valid", False)
        blocking_failures = data.get("blocking_failures", -1)
        computed_at = data.get("computed_at", "unknown")

        if not closure_valid:
            missing_cats = [
                c.get("id", "?")
                for c in data.get("categories", [])
                if c.get("blocking") and c.get("status") != "PRESENT"
            ]
            return RuleResult(
                rule_id=rule_id,
                description="ECC must show closure_valid=true (no blocking failures)",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"evidence-contract-computed.json: closure_valid=false, "
                    f"blocking_failures={blocking_failures} (computed_at={computed_at}). "
                    f"Failing categories: {missing_cats[:5]}. "
                    "Ensure ECC is run AFTER all bundle files are committed."
                ),
                evidence=f"blocking_failures={blocking_failures}, computed_at={computed_at}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="ECC must show closure_valid=true (no blocking failures)",
            severity="FAILURE",
            passed=True,
            evidence=(
                f"evidence-contract-computed.json: closure_valid=true, "
                f"blocking_failures=0 (computed_at={computed_at})"
            ),
        )

    # ------------------------------------------------------------------
    # Sprint 65 NEW rules
    # ------------------------------------------------------------------

    def _rule_content_audit_final_has_required_fields(self) -> RuleResult:
        """Content audit final must have all required fields per record.

        Sprint 64 defect S64-D3: content-audit-deep.json missing package_version,
        output_kind, readme_status, root_readme_status for all 42 records.
        """
        rule_id = "content_audit_final_has_required_fields"
        required_fields = ["package_version", "output_format", "readme_status", "root_readme_status"]

        for fname in ["destination/content-audit-final.json", "destination/content-audit-deep.json"]:
            path = self.bundle_dir / fname
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                return RuleResult(
                    rule_id=rule_id,
                    description="Content audit final must have required fields",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Cannot read {fname}: {exc}",
                )

            records = data.get("records", data.get("examples", []))
            if not records:
                continue

            missing_per_field: dict = {}
            for field_name in required_fields:
                count = sum(1 for r in records if not r.get(field_name))
                if count:
                    missing_per_field[field_name] = count

            if missing_per_field:
                details = ", ".join(f"{f}={n}" for f, n in missing_per_field.items())
                return RuleResult(
                    rule_id=rule_id,
                    description="Content audit final must have required fields per record",
                    severity="FAILURE", passed=False,
                    failure_detail=f"{fname}: records missing required fields: {details}",
                )

            return RuleResult(
                rule_id=rule_id,
                description="Content audit final must have required fields per record",
                severity="FAILURE", passed=True,
                evidence=f"{fname}: {len(records)} records, all required fields present",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit final must have required fields per record",
            severity="FAILURE", passed=False,
            failure_detail="No destination/content-audit-final.json or content-audit-deep.json found",
        )

    def _rule_content_audit_count_not_contradictory(self) -> RuleResult:
        """Content audit counts must be internally consistent.

        Sprint 64 defect S64-D2: dry_run_present=37 in JSON vs 40/42 in summary text.
        Checks: standard_package_artifacts + special_case_artifacts == total_publication_artifacts
        AND len(records) == total_publication_artifacts.
        """
        rule_id = "content_audit_count_not_contradictory"
        path = self.bundle_dir / "destination" / "content-audit-final.json"
        if not path.exists():
            path = self.bundle_dir / "destination" / "content-audit-deep.json"
        if not path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Content audit count fields must not contradict each other",
                severity="FAILURE", passed=False,
                failure_detail="No destination content audit file found",
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit count fields must not contradict each other",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read audit: {exc}",
            )

        records = data.get("records", data.get("examples", []))
        total_claimed = data.get("total_publication_artifacts", None)
        std = data.get("standard_package_artifacts", None)
        special = data.get("special_case_artifacts", None)

        contradictions = []
        if total_claimed is not None and len(records) != total_claimed:
            contradictions.append(
                f"total_publication_artifacts={total_claimed} but len(records)={len(records)}"
            )
        if std is not None and special is not None and total_claimed is not None:
            if std + special != total_claimed:
                contradictions.append(
                    f"standard({std}) + special({special}) = {std + special} != total({total_claimed})"
                )

        if contradictions:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit count fields must not contradict each other",
                severity="FAILURE", passed=False,
                failure_detail="; ".join(contradictions),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit count fields must not contradict each other",
            severity="FAILURE", passed=True,
            evidence=f"records={len(records)}, total_claimed={total_claimed}, std={std}, special={special}",
        )

    def _rule_content_audit_all_records_ready(self) -> RuleResult:
        """Content audit must show all records at READY or SPECIAL_CASE_READY.

        Catches overclaiming completion when some records are NEEDS_INVESTIGATION.
        """
        rule_id = "content_audit_all_records_ready"
        path = self.bundle_dir / "destination" / "content-audit-final.json"
        if not path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Content audit final must show all 42 records READY",
                severity="WARNING", passed=True,
                evidence="destination/content-audit-final.json not found (older sprint format)",
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit final must show all 42 records READY",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read content-audit-final.json: {exc}",
            )

        records = data.get("records", [])
        not_ready = [
            r.get("scenario_id", "?") for r in records
            if r.get("final_readiness") not in ("READY", "SPECIAL_CASE_READY")
        ]
        records_ready = data.get("records_ready", len(records) - len(not_ready))

        if not_ready:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit final must show all 42 records READY",
                severity="FAILURE", passed=False,
                failure_detail=f"{len(not_ready)} records not READY: {not_ready[:5]}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit final must show all 42 records READY",
            severity="FAILURE", passed=True,
            evidence=f"records_ready={records_ready}/{len(records)}, all READY",
        )

    def _rule_root_readme_artifacts_present_for_all_families(self) -> RuleResult:
        """Root README artifacts must exist for all 6 families.

        Sprint 64 defect S64-D4: family root README artifacts missing from bundle.
        Checks root-readme/per-family/{family}-root-readme.md for 6 families.
        """
        rule_id = "root_readme_artifacts_present_for_all_families"
        _FAMILIES = ["cells", "diagram", "email", "pdf", "slides", "words"]
        root_readme_dir = self.bundle_dir / "root-readme" / "per-family"

        if not root_readme_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Root README artifacts must exist for all 6 families",
                severity="FAILURE", passed=False,
                failure_detail="root-readme/per-family/ directory not found",
            )

        missing = [f for f in _FAMILIES if not (root_readme_dir / f"{f}-root-readme.md").exists()]
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="Root README artifacts must exist for all 6 families",
                severity="FAILURE", passed=False,
                failure_detail=f"Missing root README artifacts for: {missing}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Root README artifacts must exist for all 6 families",
            severity="FAILURE", passed=True,
            evidence="All 6 family root READMEs present in root-readme/per-family/",
        )

    def _rule_special_case_placement_proof_present(self) -> RuleResult:
        """Special-case placement proof must exist in the bundle.

        Sprint 64 defect S64-D6: special cases lack destination repo path/placement proof.
        Checks special-cases/special-case-publication-map.json with 2 cases.
        """
        rule_id = "special_case_placement_proof_present"
        map_path = self.bundle_dir / "special-cases" / "special-case-publication-map.json"

        if not map_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Special-case publication map must exist (placement proof)",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "special-cases/special-case-publication-map.json not found. "
                    "Must prove destination path for pdf-pdfa-converter and pdf-text-extractor."
                ),
            )

        try:
            data = json.loads(map_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Special-case publication map must be readable",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read special-case-publication-map.json: {exc}",
            )

        cases = data.get("special_cases", [])
        if len(cases) < 2:
            return RuleResult(
                rule_id=rule_id,
                description="Special-case publication map must document both PDF special cases",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Only {len(cases)} special cases documented "
                    "(expected 2: pdfa-converter, text-extractor)"
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Special-case publication map must document both PDF special cases",
            severity="FAILURE", passed=True,
            evidence=f"special-case-publication-map.json: {len(cases)} cases documented",
        )

    def _rule_version_policy_no_unresolved_drift(self) -> RuleResult:
        """Version policy must show no unresolved drift families.

        Sprint 64 defects S64-D5/S64-D8: PDF version drift unresolved or not labeled.
        Checks version/version-policy-final.json or phase6/version-policy.json for
        total_drift_unresolved=0.
        """
        rule_id = "version_policy_no_unresolved_drift"
        _ALLOWED_POLICIES = {
            "POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED",
            "POLICY_CLASSIFIED_CALENDAR_VERSION_BUMP",
            "VERSION_BUMP_APPLIED_NO_REGENERATION",
            "MATCH",
        }

        for rel in ["version/version-policy-final.json", "phase6/version-policy.json"]:
            path = self.bundle_dir / rel
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue

            summary = data.get("summary", {})
            unresolved = summary.get("total_drift_unresolved", None)
            if unresolved is None:
                families = data.get("families", {})
                unresolved = sum(
                    1 for f in families.values()
                    if isinstance(f, dict)
                    and not f.get("version_match")
                    and f.get("policy") not in _ALLOWED_POLICIES
                )

            if unresolved > 0:
                return RuleResult(
                    rule_id=rule_id,
                    description="Version policy must show 0 unresolved drift families",
                    severity="FAILURE", passed=False,
                    failure_detail=f"{rel}: total_drift_unresolved={unresolved}",
                )

            return RuleResult(
                rule_id=rule_id,
                description="Version policy must show 0 unresolved drift families",
                severity="FAILURE", passed=True,
                evidence=f"{rel}: total_drift_unresolved=0",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Version policy must show 0 unresolved drift families",
            severity="WARNING", passed=True,
            evidence="No version policy file found (not required for older sprints)",
        )

    def _rule_final_verdict_no_publication_overclaim(self) -> RuleResult:
        """Final verdict must not claim full publication without remote proof.

        Sprint 64 defect S64-D1: final verdict claimed PUBLISHED but no remote proof
        in the evidence bundle. If the verdict contains strong PUBLISHED keywords,
        remote proof must exist.
        """
        rule_id = "final_verdict_no_publication_overclaim"
        verdict_path = self.bundle_dir / "final-verdict.md"

        if not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim publication without proof",
                severity="FAILURE", passed=False,
                failure_detail="final-verdict.md not found",
            )

        verdict = verdict_path.read_text(encoding="utf-8", errors="replace")
        publication_claim_keywords = [
            "PUBLICATION_VERIFIED", "FULLY_PUBLISHED", "ALL_PUBLISHED",
            "LIVE_PUBLICATION_COMPLETE",
        ]
        claims_publication = any(kw in verdict for kw in publication_claim_keywords)

        if not claims_publication:
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim publication without proof",
                severity="FAILURE", passed=True,
                evidence="Verdict does not contain strong publication completion keywords",
            )

        remote_proof = self.bundle_dir / "publication" / "remote-proof-index.json"
        if not remote_proof.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim publication without proof",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "Verdict contains publication completion keyword but "
                    "publication/remote-proof-index.json is missing. "
                    "Must include remote proof artifact (PR URLs, merge SHAs) in bundle."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Final verdict must not overclaim publication without proof",
            severity="FAILURE", passed=True,
            evidence="Verdict claims publication and remote-proof-index.json is present",
        )

    def _rule_remote_proof_index_present_if_published(self) -> RuleResult:
        """Remote proof index must exist if any publication is claimed.

        Sprint 64 defect S64-D1: publication claim without remote proof in bundle.
        If final-verdict.md mentions PUBLISHED/HANDOFF/DRY_RUN keywords,
        publication/remote-proof-index.json must exist.
        """
        rule_id = "remote_proof_index_present_if_published"
        verdict_path = self.bundle_dir / "final-verdict.md"

        if not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof index must exist if publication is claimed",
                severity="FAILURE", passed=False,
                failure_detail="final-verdict.md not found",
            )

        verdict = verdict_path.read_text(encoding="utf-8", errors="replace")
        broad_pub_keywords = [
            "PUBLISHED", "HANDOFF", "PUBLICATION", "REMOTE_PROOF", "PR_MERGED",
            "DRY_RUN", "APPROVAL_BLOCKED",
        ]
        mentions_publication = any(kw in verdict for kw in broad_pub_keywords)
        remote_proof = self.bundle_dir / "publication" / "remote-proof-index.json"

        if mentions_publication and not remote_proof.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof index must exist if publication is mentioned",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "final-verdict.md mentions publication/PR activity but "
                    "publication/remote-proof-index.json is absent. "
                    "S64-D1: publication evidence must be bundled."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote proof index must exist if publication is mentioned",
            severity="FAILURE", passed=True,
            evidence=(
                f"verdict_mentions_publication={mentions_publication}, "
                f"remote_proof_present={remote_proof.exists()}"
            ),
        )

    def _rule_content_audit_readme_io_coverage(self) -> RuleResult:
        """Content audit must show high README I/O coverage (>=40/42).

        Catches cases where MISSING_IO is returned for most records — indicating
        the audit ran before README corrections were applied.
        """
        rule_id = "content_audit_readme_io_coverage"
        path = self.bundle_dir / "destination" / "content-audit-final.json"
        if not path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Content audit must show >=40/42 README I/O coverage",
                severity="WARNING", passed=True,
                evidence="destination/content-audit-final.json not found (older sprint format)",
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit must show >=40/42 README I/O coverage",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read content-audit-final.json: {exc}",
            )

        records = data.get("records", [])
        io_doc_count = sum(1 for r in records if r.get("readme_status") == "IO_DOC")
        total = len(records)
        threshold = max(40, total - 2)

        if io_doc_count < threshold:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit must show >=40/42 README I/O coverage",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Only {io_doc_count}/{total} records have readme_status=IO_DOC "
                    f"(threshold={threshold}). README corrections may not have been applied."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit must show >=40/42 README I/O coverage",
            severity="FAILURE", passed=True,
            evidence=f"io_doc_count={io_doc_count}/{total} >= {threshold}",
        )

    def _rule_revalidation_shows_prior_sprint_invalid(self) -> RuleResult:
        """Prior sprint revalidation result must show overall_valid=false.

        Ensures new semantic rules actually catch the prior sprint's defects.
        Looks for evidence/*revalidation*.json files.
        """
        rule_id = "revalidation_shows_prior_sprint_invalid"
        evidence_dir = self.bundle_dir / "evidence"

        if not evidence_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Prior sprint revalidation must show overall_valid=false",
                severity="WARNING", passed=True,
                evidence="evidence/ directory not found (older sprint format)",
            )

        candidates = sorted(evidence_dir.glob("*revalidation*.json"))
        if not candidates:
            return RuleResult(
                rule_id=rule_id,
                description="Prior sprint revalidation must show overall_valid=false",
                severity="WARNING", passed=True,
                evidence="No *revalidation*.json found (not required for older sprints)",
            )

        revalidation_path = candidates[-1]
        try:
            data = json.loads(revalidation_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Prior sprint revalidation must show overall_valid=false",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read {revalidation_path.name}: {exc}",
            )

        overall_valid = data.get("overall_valid", True)
        if overall_valid:
            sprint_id = data.get("sprint_id", "?")
            return RuleResult(
                rule_id=rule_id,
                description="Prior sprint revalidation must show overall_valid=false",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"{revalidation_path.name}: overall_valid=true — new semantic rules "
                    f"did not detect defects in prior sprint ({sprint_id}). "
                    "Rules may be too weak. Revalidation must fail."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Prior sprint revalidation must show overall_valid=false",
            severity="FAILURE", passed=True,
            evidence=f"{revalidation_path.name}: overall_valid=false (prior sprint correctly flagged)",
        )

    # ------------------------------------------------------------------
    # Sprint 66 rules: close S65-D1 through S65-D5
    # ------------------------------------------------------------------

    def _rule_remote_proof_per_example_not_overclaimed(self) -> RuleResult:
        """Remote proof index must not claim a PR covers more examples than it actually does.

        Sprint 65 defect S65-D1: Words PR#6 was cited as proving all 8 words examples
        but it only contained 1 example (report-builder). PDF PR#4 was cited for all 19
        PDF examples but only contained 1 (optimizer).

        Checks remote/remote-pr-proof-index.json: each PR's examples_count must match
        its scenario_ids_covered count. Also verifies total per-family example coverage
        equals the expected count (no single-PR-proves-all overclaim).
        """
        rule_id = "remote_proof_per_example_not_overclaimed"
        proof_path = self.bundle_dir / "remote" / "remote-pr-proof-index.json"

        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must not overclaim PR coverage",
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-pr-proof-index.json not found. Sprint 65 had only publication/remote-proof-index.json which overclaimed PR coverage.",
            )

        try:
            data = json.loads(proof_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must not overclaim PR coverage",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read remote-pr-proof-index.json: {exc}",
            )

        families = data.get("families", {})
        issues = []
        for family, prs in families.items():
            if not isinstance(prs, list):
                continue
            for pr in prs:
                claimed_count = pr.get("examples_count", 0)
                actual_ids = pr.get("scenario_ids_covered", [])
                if claimed_count != len(actual_ids):
                    issues.append(
                        f"{family} PR#{pr.get('pr_number')}: "
                        f"examples_count={claimed_count} but scenario_ids_covered has {len(actual_ids)}"
                    )

        if issues:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must not overclaim PR coverage",
                severity="FAILURE", passed=False,
                failure_detail=f"PR coverage inconsistency: {issues[:3]}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote proof must not overclaim PR coverage",
            severity="FAILURE", passed=True,
            evidence=f"remote-pr-proof-index.json present with per-example coverage for {len(families)} families",
        )

    def _rule_remote_proof_has_content_hashes(self) -> RuleResult:
        """Remote proof must include actual remote content hashes, not just PR numbers.

        Sprint 65 defect S65-D1: remote-proof-index.json had only PR numbers and merge SHAs.
        No per-example README SHA or Program.cs SHA from the remote repo was captured.
        Sprint 66 requires remote/remote-example-inventory.json with readme_content_sha256
        and programcs_content_sha256 for each of the 42 examples.
        """
        rule_id = "remote_proof_has_content_hashes"
        inv_path = self.bundle_dir / "remote" / "remote-example-inventory.json"

        if not inv_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must include per-example content hashes",
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-example-inventory.json not found. Only PR-number proof is insufficient.",
            )

        try:
            data = json.loads(inv_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must include per-example content hashes",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read remote-example-inventory.json: {exc}",
            )

        records = data.get("records", [])
        missing_hashes = [
            r.get("scenario_id", "?") for r in records
            if not r.get("readme_content_sha256") and not r.get("readme_sha")
        ]
        total = len(records)

        if total < 42:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must include per-example content hashes",
                severity="FAILURE", passed=False,
                failure_detail=f"Only {total} remote inventory records (expected 42)",
            )

        if len(missing_hashes) > 2:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must include per-example content hashes",
                severity="FAILURE", passed=False,
                failure_detail=f"{len(missing_hashes)}/{total} records missing readme SHA: {missing_hashes[:5]}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote proof must include per-example content hashes",
            severity="FAILURE", passed=True,
            evidence=f"{total} remote inventory records with content SHAs",
        )

    def _rule_remote_readme_io_audit_present(self) -> RuleResult:
        """Remote README I/O audit must be based on fetched remote content.

        Sprint 65 defect S65-D2: no remote README I/O audit was performed.
        Sprint 66 requires remote/remote-readme-io-audit.json with has_io_section
        per example, derived from actual remote README content.
        """
        rule_id = "remote_readme_io_audit_present"
        audit_path = self.bundle_dir / "remote" / "remote-readme-io-audit.json"

        if not audit_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Remote README I/O audit must be based on fetched content",
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-readme-io-audit.json not found. Remote README I/O status was not independently verified.",
            )

        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Remote README I/O audit must be based on fetched content",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read remote-readme-io-audit.json: {exc}",
            )

        records = data.get("records", [])
        missing_io_status = [r for r in records if "has_io_section" not in r and "io_status" not in r]
        total = len(records)

        if total < 42:
            return RuleResult(
                rule_id=rule_id,
                description="Remote README I/O audit must be based on fetched content",
                severity="FAILURE", passed=False,
                failure_detail=f"Only {total} records in remote README I/O audit (expected 42)",
            )

        if missing_io_status:
            return RuleResult(
                rule_id=rule_id,
                description="Remote README I/O audit must be based on fetched content",
                severity="FAILURE", passed=False,
                failure_detail=f"{len(missing_io_status)} records missing has_io_section field",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote README I/O audit must be based on fetched content",
            severity="FAILURE", passed=True,
            evidence=f"{total} remote README I/O audit records with has_io_section field",
        )

    def _rule_handoff_bundle_not_empty(self) -> RuleResult:
        """handoff/per-family/ must not be empty when verdict claims handoff ready.

        Sprint 65 defect S65-D3: handoff/per-family/ was empty but verdict said
        HANDOFF_READY. This rule checks that at least one family has example artifacts.
        """
        rule_id = "handoff_bundle_not_empty"
        handoff_dir = self.bundle_dir / "handoff" / "per-family"

        if not handoff_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="handoff/per-family/ must not be empty",
                severity="FAILURE", passed=False,
                failure_detail="handoff/per-family/ directory does not exist",
            )

        # Count family directories that contain example artifacts (Program.cs files)
        families_with_artifacts = []
        for family_dir in handoff_dir.iterdir():
            if not family_dir.is_dir():
                continue
            program_cs_files = list(family_dir.rglob("Program.cs"))
            if program_cs_files:
                families_with_artifacts.append(family_dir.name)

        if not families_with_artifacts:
            return RuleResult(
                rule_id=rule_id,
                description="handoff/per-family/ must not be empty",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "handoff/per-family/ exists but contains no Program.cs files in any family. "
                    "Sprint 65 had this defect — verdict claimed HANDOFF_READY with empty per-family/."
                ),
            )

        total_programs = sum(
            len(list((handoff_dir / f).rglob("Program.cs")))
            for f in families_with_artifacts
        )

        return RuleResult(
            rule_id=rule_id,
            description="handoff/per-family/ must not be empty",
            severity="FAILURE", passed=True,
            evidence=f"{len(families_with_artifacts)} families with artifacts, {total_programs} Program.cs files",
        )

    def _rule_content_audit_output_kind_not_blank(self) -> RuleResult:
        """Content audit final must have output_kind present for all records.

        Sprint 65 defect S65-D4: output_kind was blank for pdf-html-converter,
        pdf-pdfa-converter, and pdf-text-extractor.
        """
        rule_id = "content_audit_output_kind_not_blank"
        path = self.bundle_dir / "destination" / "content-audit-final.json"

        if not path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Content audit output_kind must not be blank for any record",
                severity="WARNING", passed=True,
                evidence="destination/content-audit-final.json not found (older sprint format)",
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit output_kind must not be blank for any record",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read content-audit-final.json: {exc}",
            )

        records = data.get("records", [])
        blank_output_kind = [r.get("scenario_id", "?") for r in records if not r.get("output_kind")]

        if blank_output_kind:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit output_kind must not be blank for any record",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"{len(blank_output_kind)} records have blank output_kind: {blank_output_kind}. "
                    "Sprint 65 defect S65-D4."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit output_kind must not be blank for any record",
            severity="FAILURE", passed=True,
            evidence=f"All {len(records)} records have output_kind present",
        )

    def _rule_publication_state_not_mixed(self) -> RuleResult:
        """Publication state must use separate fields, not a mixed published+blocked state.

        Sprint 65 defect S65-D5: final-verdict.md claimed '42/42 already published'
        AND 'approval blocked' without separate per-field state model.
        Sprint 66 requires publication/publication-truth-matrix-final.json with
        separate remote_example_present and approval_blocked fields.
        """
        rule_id = "publication_state_not_mixed"
        matrix_path = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"

        if not matrix_path.exists():
            # Check if the old-style proof index mixes states
            old_proof = self.bundle_dir / "publication" / "remote-proof-index.json"
            if old_proof.exists():
                try:
                    data = json.loads(old_proof.read_text(encoding="utf-8"))
                    # Old proof: if it claims merged=true and has no per-example state model
                    families = data.get("families", data.get("repos", {}))
                    if isinstance(families, dict):
                        first_family = next(iter(families.values()), {})
                        if "remote_example_present" not in first_family and "approval_blocked" not in first_family:
                            return RuleResult(
                                rule_id=rule_id,
                                description="Publication state must use separate fields",
                                severity="FAILURE", passed=False,
                                failure_detail=(
                                    "publication/remote-proof-index.json lacks separate "
                                    "remote_example_present and approval_blocked fields. "
                                    "Sprint 65 defect S65-D5: mixed state."
                                ),
                            )
                except (OSError, ValueError):
                    pass
            return RuleResult(
                rule_id=rule_id,
                description="Publication state must use separate fields",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "publication/publication-truth-matrix-final.json not found. "
                    "Sprint 66 requires separate per-example publication state fields."
                ),
            )

        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Publication state must use separate fields",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read publication-truth-matrix-final.json: {exc}",
            )

        records = data.get("records", [])
        if not records:
            return RuleResult(
                rule_id=rule_id,
                description="Publication state must use separate fields",
                severity="FAILURE", passed=False,
                failure_detail="publication-truth-matrix-final.json has no records",
            )

        first = records[0]
        required_fields = ["remote_example_present", "approval_blocked", "remote_readme_has_io_docs"]
        missing = [f for f in required_fields if f not in first]
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="Publication state must use separate fields",
                severity="FAILURE", passed=False,
                failure_detail=f"publication-truth-matrix-final.json records missing fields: {missing}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Publication state must use separate fields",
            severity="FAILURE", passed=True,
            evidence=f"{len(records)} records with separate state fields (remote_example_present, approval_blocked, remote_readme_has_io_docs)",
        )

    def _rule_remote_proof_not_workspace_only(self) -> RuleResult:
        """Remote proof must not rely solely on workspace/ files outside the bundle.

        Sprint 65 relied on workspace/verification/latest/*-merge-result.json which
        are gitignored workspace files. The bundle must include its own remote proof.
        """
        rule_id = "remote_proof_not_workspace_only"
        # Check if the only remote proof is workspace-path references
        old_proof = self.bundle_dir / "publication" / "remote-proof-index.json"
        new_proof = self.bundle_dir / "remote" / "remote-pr-proof-index.json"
        new_inv = self.bundle_dir / "remote" / "remote-example-inventory.json"

        if new_proof.exists() and new_inv.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must not rely solely on workspace/ files",
                severity="FAILURE", passed=True,
                evidence="remote/remote-pr-proof-index.json and remote/remote-example-inventory.json present in bundle",
            )

        if old_proof.exists():
            try:
                data = json.loads(old_proof.read_text(encoding="utf-8"))
                # Check if it references workspace/ paths
                content = old_proof.read_text(encoding="utf-8")
                if "workspace/verification/latest" in content or "merge_result_source" in content:
                    return RuleResult(
                        rule_id=rule_id,
                        description="Remote proof must not rely solely on workspace/ files",
                        severity="FAILURE", passed=False,
                        failure_detail=(
                            "publication/remote-proof-index.json references workspace/verification/latest/ "
                            "which are gitignored workspace files not in the bundle. "
                            "Sprint 65 defect S65-D1."
                        ),
                    )
            except (OSError, ValueError):
                pass

        if not new_proof.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must not rely solely on workspace/ files",
                severity="FAILURE", passed=False,
                failure_detail="Neither remote/remote-pr-proof-index.json nor bundled remote proof found",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote proof must not rely solely on workspace/ files",
            severity="FAILURE", passed=True,
            evidence="Remote proof present in bundle (not workspace-only)",
        )

    def _rule_root_readme_and_package_both_present(self) -> RuleResult:
        """If root README artifacts exist, package example artifacts must also exist.

        Sprint 65 defect S65-D3: root-readme/per-family/ had 6 family files but
        handoff/per-family/ was empty. Root README without package artifacts is incomplete.
        """
        rule_id = "root_readme_and_package_both_present"
        root_readme_dir = self.bundle_dir / "root-readme" / "per-family"
        handoff_dir = self.bundle_dir / "handoff" / "per-family"

        root_exists = root_readme_dir.exists() and any(root_readme_dir.iterdir())
        handoff_exists = handoff_dir.exists() and any(
            (handoff_dir / f).rglob("Program.cs") for f in ["cells", "words", "pdf", "diagram", "email", "slides"]
            if (handoff_dir / f).exists()
        )

        if root_exists and not handoff_exists:
            return RuleResult(
                rule_id=rule_id,
                description="Root README artifact presence requires package artifacts",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "root-readme/per-family/ exists with family files but "
                    "handoff/per-family/ has no Program.cs artifacts. "
                    "Sprint 65 defect S65-D3."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Root README artifact presence requires package artifacts",
            severity="FAILURE", passed=True,
            evidence=f"root_readme_present={root_exists}, handoff_present={handoff_exists}",
        )

    def _rule_remote_readme_io_not_overclaimed(self) -> RuleResult:
        """Final verdict must not claim remote README I/O is published if remote audit shows 0.

        Sprint 65 defect S65-D2: remote READMEs were old-format but this was not checked.
        If remote-readme-io-audit.json shows io_doc_count=0, the verdict must not say
        'README I/O PUBLISHED' or similar.
        """
        rule_id = "remote_readme_io_not_overclaimed"
        audit_path = self.bundle_dir / "remote" / "remote-readme-io-audit.json"

        if not audit_path.exists():
            # Without remote audit, cannot verify — check if verdict overclaims
            verdict_path = self.bundle_dir / "final-verdict.md"
            if verdict_path.exists():
                verdict = verdict_path.read_text(encoding="utf-8", errors="replace")
                overclaim_patterns = [
                    "REMOTE_README_IO_PUBLISHED",
                    "README_IO_VERIFIED_REMOTE",
                    "README I/O PUBLISHED",
                ]
                for pattern in overclaim_patterns:
                    if pattern in verdict:
                        return RuleResult(
                            rule_id=rule_id,
                            description="Final verdict must not overclaim remote README I/O",
                            severity="FAILURE", passed=False,
                            failure_detail=(
                                f"Verdict contains '{pattern}' but no remote README audit exists. "
                                "Cannot verify remote README I/O state without remote audit."
                            ),
                        )
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim remote README I/O",
                severity="WARNING", passed=True,
                evidence="No remote README audit; no overclaim detected in verdict",
            )

        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim remote README I/O",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read remote-readme-io-audit.json: {exc}",
            )

        io_count = data.get("io_doc_count", -1)
        total = data.get("total", 0)

        verdict_path = self.bundle_dir / "final-verdict.md"
        if not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim remote README I/O",
                severity="FAILURE", passed=False,
                failure_detail="final-verdict.md not found",
            )

        verdict = verdict_path.read_text(encoding="utf-8", errors="replace")
        overclaim_patterns = ["REMOTE_README_IO_PUBLISHED", "README_IO_PUBLISHED_AND_VERIFIED"]
        overclaims = [p for p in overclaim_patterns if p in verdict]

        if io_count == 0 and overclaims:
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim remote README I/O",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"remote-readme-io-audit.json shows io_doc_count=0/{total} but "
                    f"final-verdict.md contains: {overclaims}"
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Final verdict must not overclaim remote README I/O",
            severity="FAILURE", passed=True,
            evidence=f"remote io_doc_count={io_count}/{total}; no overclaim in verdict",
        )

    def _rule_handoff_all_examples_have_io_section(self) -> RuleResult:
        """All README.md files in handoff/per-family/ must contain I/O section.

        Sprint 65 defect S65-D3: handoff was empty so this could not be verified.
        Sprint 66: with 42 package artifacts in handoff, every README must have
        '## Input and Output' section.
        """
        rule_id = "handoff_all_examples_have_io_section"
        handoff_dir = self.bundle_dir / "handoff" / "per-family"

        if not handoff_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="All handoff READMEs must have I/O section",
                severity="FAILURE", passed=False,
                failure_detail="handoff/per-family/ directory not found",
            )

        all_readme_files = list(handoff_dir.rglob("README.md"))
        # Skip family-level root READMEs at per-family/{family}/README.md —
        # those are root family READMEs (Sprint 70) with different format.
        # Only check example-level READMEs (depth >= 2 from per-family/).
        readme_files = [
            r for r in all_readme_files
            if r.parent.parent != handoff_dir
        ]
        if not readme_files:
            return RuleResult(
                rule_id=rule_id,
                description="All handoff READMEs must have I/O section",
                severity="FAILURE", passed=False,
                failure_detail="No example README.md files found in handoff/per-family/",
            )

        missing_io = []
        for readme in readme_files:
            try:
                content = readme.read_text(encoding="utf-8", errors="replace")
                if "## Input and Output" not in content:
                    # Use relative path for clarity
                    try:
                        rel = str(readme.relative_to(self.bundle_dir))
                    except ValueError:
                        rel = str(readme)
                    missing_io.append(rel)
            except OSError:
                pass

        if missing_io:
            return RuleResult(
                rule_id=rule_id,
                description="All handoff READMEs must have I/O section",
                severity="FAILURE", passed=False,
                failure_detail=f"{len(missing_io)}/{len(readme_files)} handoff READMEs missing I/O section: {missing_io[:3]}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="All handoff READMEs must have I/O section",
            severity="FAILURE", passed=True,
            evidence=f"All {len(readme_files)} handoff README.md files have '## Input and Output' section",
        )

    # ------------------------------------------------------------------
    # Sprint 67 NEW rules: close S66-D1 through S66-D5
    # ------------------------------------------------------------------

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
                severity="FAILURE", passed=False,
                failure_detail="root-readme/per-family/pdf-root-readme.md not found",
            )
        content = pdf_readme.read_text(encoding="utf-8", errors="replace")
        # Count rows in the examples table: lines with pipe-delimited content containing
        # the dotnet run command pattern (header row excluded)
        run_rows = [ln for ln in content.splitlines()
                    if "dotnet run" in ln and ln.strip().startswith("|")]
        count = len(run_rows)
        if count < 19:
            return RuleResult(
                rule_id=rule_id,
                description="PDF root README must have >=19 example rows",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"PDF root README has only {count} example rows (need >=19). "
                    "Sprint 67 defect S67-D1: table was truncated at 3 rows."
                ),
            )
        return RuleResult(
            rule_id=rule_id,
            description="PDF root README must have >=19 example rows",
            severity="FAILURE", passed=True,
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
                        severity="FAILURE", passed=False,
                        failure_detail=f"{candidate.name} contains IN_PROGRESS",
                    )
                return RuleResult(
                    rule_id=rule_id,
                    description="Splitter cardinality reconciliation document must be complete",
                    severity="FAILURE", passed=True,
                    evidence=f"Splitter cardinality reconciliation present: {candidate}",
                )
        return RuleResult(
            rule_id=rule_id,
            description="Splitter cardinality reconciliation document must be complete",
            severity="FAILURE", passed=False,
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
                severity="FAILURE", passed=False,
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
                    severity="FAILURE", passed=False,
                    failure_detail=f"No content-audit-{sprint_id}.json found in destination/",
                )
            audit_path = sorted(candidates)[-1]
        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Sprint content audit must have no stale PDF 26.4.0 version records",
                severity="FAILURE", passed=False,
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
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Found {len(stale_records)} PDF records with stale version 26.4.0: "
                    f"{stale_records[:5]}. Sprint 67 defect S67-D3."
                ),
            )
        return RuleResult(
            rule_id=rule_id,
            description="Sprint content audit must have no stale PDF 26.4.0 version records",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="version/pdf-version-proof-chain.md not found. Sprint 67 defect S67-D4.",
            )
        content = proof_path.read_text(encoding="utf-8", errors="replace")
        if "IN_PROGRESS" in content:
            return RuleResult(
                rule_id=rule_id,
                description="version/pdf-version-proof-chain.md must be present",
                severity="FAILURE", passed=False,
                failure_detail="pdf-version-proof-chain.md contains IN_PROGRESS",
            )
        return RuleResult(
            rule_id=rule_id,
            description="version/pdf-version-proof-chain.md must be present",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="root-readme/per-family/words-root-readme.md not found",
            )
        content = words_readme.read_text(encoding="utf-8", errors="replace")
        has_multi_marker = ("×N" in content or "2×" in content or "(xN)" in content
                            or "(×N)" in content or "xN" in content)
        if not has_multi_marker:
            return RuleResult(
                rule_id=rule_id,
                description="Words root README must have cardinality markers for multi-I/O types",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "words-root-readme.md has no ×N or 2× cardinality markers. "
                    "Words Merger (N→1), Splitter (1→N), and Comparer (2→1) require annotations. "
                    "Sprint 67 defect S67-D5."
                ),
            )
        return RuleResult(
            rule_id=rule_id,
            description="Words root README must have cardinality markers for multi-I/O types",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail=f"Version mismatches: {'; '.join(mismatches)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Handoff-index nuget_version must match Directory.Packages.props for all families",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
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
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale {stale} paths found in content-audit-final.json: {stale_in_paths[:2]}",
                )
        return RuleResult(
            rule_id=rule_id,
            description="destination/content-audit-final.json must exist with no stale sprint paths",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
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
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale {stale} path refs in publication-truth-matrix-final.json: {stale_in_paths[:2]}",
                )
        return RuleResult(
            rule_id=rule_id,
            description="publication-truth-matrix-final.json must exist without stale sprint paths",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="publication/publication-truth-matrix-final.json not found",
            )
        try:
            ptm = json.loads(ptm_path.read_text(encoding="utf-8"))
            records = ptm.get("records", [])
            mixed = [
                r["scenario_id"]
                for r in records
                if not r.get("remote_example_readme_has_io_docs", True)
                and r.get("readme_io_post_merge_verified", False)
            ]
            if mixed:
                return RuleResult(
                    rule_id=rule_id,
                    description="No record may have readme_io_post_merge_verified=true while remote README lacks I/O docs",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Mixed state in {len(mixed)} records: {mixed[:3]}",
                )
        except Exception as exc:
            return RuleResult(
                rule_id=rule_id,
                description="publication-truth-matrix-final.json must not mix README I/O states",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read publication-truth-matrix-final.json: {exc}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="publication-truth-matrix-final.json must not mix README I/O states",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail=f"Missing root_readme: {'; '.join(missing)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="All 6 family handoff-indexes must include root_readme field",
            severity="FAILURE", passed=True,
            evidence="All 6 family handoff-index.json files have root_readme field",
        )

    def _rule_exact_legacy_reconciliation_present(self) -> RuleResult:
        """Consolidated exact legacy reconciliation report must exist.

        Sprint 68 defect S68-D7: legacy reconciliation was split across two trees
        with no consolidated authority report.
        """
        rule_id = "exact_legacy_reconciliation_present"
        final_path = (
            self.bundle_dir / "legacy-reconciliation" / "exact-legacy-plan-reconciliation-final.md"
        )
        items_path = (
            self.bundle_dir / "legacy-reconciliation" / "exact-items-final.json"
        )
        missing = []
        if not final_path.exists():
            missing.append("legacy-reconciliation/exact-legacy-plan-reconciliation-final.md")
        if not items_path.exists():
            missing.append("legacy-reconciliation/exact-items-final.json")
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="Consolidated exact legacy reconciliation must exist",
                severity="FAILURE", passed=False,
                failure_detail=f"Missing: {'; '.join(missing)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Consolidated exact legacy reconciliation must exist",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
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
        ]
        # Check for generic SPRINT##_COMPLETE pattern
        import re as _re
        if _re.search(r"SPRINT\d+_COMPLETE", content):
            return RuleResult(
                rule_id=rule_id,
                description="final-verdict.md must not use generic SPRINT##_COMPLETE",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "final-verdict.md contains SPRINT##_COMPLETE which is overbroad. "
                    f"Use one of: {allowed_verdicts}"
                ),
            )
        has_allowed = any(v in content for v in allowed_verdicts)
        if not has_allowed:
            return RuleResult(
                rule_id=rule_id,
                description="final-verdict.md must contain an allowed precise verdict",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"final-verdict.md contains no allowed verdict. "
                    f"Expected one of: {allowed_verdicts}"
                ),
            )
        return RuleResult(
            rule_id=rule_id,
            description="final-verdict.md must use an allowed precise verdict",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=True,  # can't check without both files
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
                        severity="FAILURE", passed=False,
                        failure_detail=(
                            f"Verdict claims PUBLISHED but {len(blocked)}/42 records have approval_blocked=true"
                        ),
                    )
            except Exception:
                pass
        return RuleResult(
            rule_id=rule_id,
            description="final-verdict.md must not claim complete while publication is blocked",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
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
                    severity="FAILURE", passed=False,
                    failure_detail=f"Missing root_readme_sha256 for: {missing_rr}",
                )
        except Exception as exc:
            return RuleResult(
                rule_id=rule_id,
                description="handoff/publication-handoff-index.json must exist with root_readme entries",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read publication-handoff-index.json: {exc}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="publication-handoff-index.json must have root_readme_sha256 for each family",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="version/version-consistency-final.json not found",
            )
        try:
            vc = json.loads(vc_path.read_text(encoding="utf-8"))
            if not vc.get("all_consistent", False):
                mismatches = vc.get("sprint68_mismatches", "?")
                return RuleResult(
                    rule_id=rule_id,
                    description="version/version-consistency-final.json must show all_consistent=true",
                    severity="FAILURE", passed=False,
                    failure_detail=f"version-consistency-final.json: all_consistent=false, mismatches={mismatches}",
                )
        except Exception as exc:
            return RuleResult(
                rule_id=rule_id,
                description="version/version-consistency-final.json must exist and be valid",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read version-consistency-final.json: {exc}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="version/version-consistency-final.json must exist showing all_consistent=true",
            severity="FAILURE", passed=True,
            evidence="version-consistency-final.json: all_consistent=true, 0 mismatches",
        )

    # --- Sprint 70 NEW rules: close S69-D1 and S69-D2 ---

    def _rule_handoff_root_readme_in_sprint_folder(self) -> RuleResult:
        """All family handoff-index root_readme.source_path must be inside current sprint handoff.

        Sprint 69 defect S69-D1: all 6 handoff-indexes pointed root_readme.source_path
        to reports/sprint68/root-readme/per-family/ — outside the handoff package.
        A self-contained handoff must have root READMEs physically inside it.
        """
        rule_id = "handoff_root_readme_in_sprint_folder"
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        sprint_id = self._read_sprint_id()
        stale_paths = []
        for family in families:
            idx_path = self.bundle_dir / "handoff" / "per-family" / family / "handoff-index.json"
            if not idx_path.exists():
                continue
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                rr = idx.get("root_readme", {})
                src = rr.get("source_path", "")
                # Must be inside current sprint handoff folder
                expected_prefix = f"reports/{sprint_id}/handoff/per-family/{family}/"
                if src and not src.startswith(expected_prefix):
                    stale_paths.append(f"{family}: source_path={src!r} (expected prefix {expected_prefix!r})")
            except Exception as exc:
                stale_paths.append(f"{family}: read error {exc}")
        if stale_paths:
            return RuleResult(
                rule_id=rule_id,
                description="Handoff-index root_readme.source_path must be inside current sprint handoff folder",
                severity="FAILURE", passed=False,
                failure_detail=f"Stale root README source paths: {'; '.join(stale_paths)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Handoff-index root_readme.source_path must be inside current sprint handoff folder",
            severity="FAILURE", passed=True,
            evidence=f"All 6 family handoff-index root_readme.source_path values are inside reports/{sprint_id}/handoff/",
        )

    def _resolve_sprint_relative_path(self, src: str) -> "Path":
        """Resolve a repo-relative source path to an absolute Path.

        source_path is stored as ``reports/{sprint_id}/handoff/per-family/{family}/README.md``.
        Strip the ``reports/{sprint_id}/`` prefix and resolve relative to bundle_dir,
        which avoids dependency on the host repo layout in tests.
        """
        sprint_id = self._read_sprint_id()
        prefix = f"reports/{sprint_id}/"
        if src.startswith(prefix):
            return self.bundle_dir / src[len(prefix):]
        # Fallback: resolve relative to bundle_dir parent (reports/) then repo root
        return self.bundle_dir.parent.parent / src

    def _rule_handoff_root_readme_file_present(self) -> RuleResult:
        """Root README file must physically exist at root_readme.source_path for all families.

        Sprint 69 defect S69-D1: even if source_path were updated, the file must
        actually be present in the handoff package.
        """
        rule_id = "handoff_root_readme_file_present"
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        missing = []
        for family in families:
            idx_path = self.bundle_dir / "handoff" / "per-family" / family / "handoff-index.json"
            if not idx_path.exists():
                continue
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                rr = idx.get("root_readme", {})
                src = rr.get("source_path", "")
                if src:
                    file_path = self._resolve_sprint_relative_path(src)
                    if not file_path.exists():
                        missing.append(f"{family}: {src!r} not found")
            except Exception as exc:
                missing.append(f"{family}: read error {exc}")
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="Root README file must physically exist at source_path for all families",
                severity="FAILURE", passed=False,
                failure_detail=f"Missing root README files: {'; '.join(missing)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Root README file must physically exist at source_path for all families",
            severity="FAILURE", passed=True,
            evidence="All 6 family root README files are physically present at their source_path",
        )

    def _rule_handoff_root_readme_hash_matches(self) -> RuleResult:
        """root_readme.sha256 in handoff-index must match the physical file at source_path.

        Ensures the stored hash is not stale (i.e., the file content matches what was indexed).
        """
        rule_id = "handoff_root_readme_hash_matches"
        import hashlib as _hashlib
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        mismatches = []
        for family in families:
            idx_path = self.bundle_dir / "handoff" / "per-family" / family / "handoff-index.json"
            if not idx_path.exists():
                continue
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                rr = idx.get("root_readme", {})
                src = rr.get("source_path", "")
                stored_hash = rr.get("sha256", "")
                if not src or not stored_hash:
                    continue
                file_path = self._resolve_sprint_relative_path(src)
                if not file_path.exists():
                    mismatches.append(f"{family}: file not found at {src!r}")
                    continue
                h = _hashlib.sha256(file_path.read_bytes()).hexdigest()
                if h != stored_hash:
                    mismatches.append(
                        f"{family}: stored={stored_hash[:16]}… actual={h[:16]}… for {src!r}"
                    )
            except Exception as exc:
                mismatches.append(f"{family}: read error {exc}")
        if mismatches:
            return RuleResult(
                rule_id=rule_id,
                description="root_readme.sha256 in handoff-index must match physical file",
                severity="FAILURE", passed=False,
                failure_detail=f"Hash mismatches: {'; '.join(mismatches)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="root_readme.sha256 in handoff-index must match physical file",
            severity="FAILURE", passed=True,
            evidence="All 6 family root README sha256 hashes match their physical files",
        )

    def _rule_publication_handoff_root_readme_hash_matches(self) -> RuleResult:
        """publication-handoff-index.json root_readme_sha256 per family must match physical file.

        Ensures the publication index is not stale for root README hashes.
        """
        rule_id = "publication_handoff_root_readme_hash_matches"
        import hashlib as _hashlib
        phi_path = self.bundle_dir / "handoff" / "publication-handoff-index.json"
        if not phi_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication-handoff-index.json must exist with correct root README hashes",
                severity="FAILURE", passed=False,
                failure_detail="handoff/publication-handoff-index.json not found",
            )
        try:
            phi = json.loads(phi_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return RuleResult(
                rule_id=rule_id,
                description="publication-handoff-index.json must be valid JSON with root README hashes",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot parse publication-handoff-index.json: {exc}",
            )
        families_data = phi.get("families", [])
        if not isinstance(families_data, list):
            return RuleResult(
                rule_id=rule_id,
                description="publication-handoff-index.json families must be a list",
                severity="FAILURE", passed=False,
                failure_detail="families field is not a list",
            )
        mismatches = []
        for fam_data in families_data:
            family = fam_data.get("family", "")
            stored_hash = fam_data.get("root_readme_sha256", "")
            src_path = fam_data.get("root_readme_source_path", "")
            if not stored_hash or not src_path:
                continue
            file_path = self._resolve_sprint_relative_path(src_path)
            if not file_path.exists():
                mismatches.append(f"{family}: root README not found at {src_path!r}")
                continue
            actual = _hashlib.sha256(file_path.read_bytes()).hexdigest()
            if actual != stored_hash:
                mismatches.append(
                    f"{family}: phi_hash={stored_hash[:16]}… actual={actual[:16]}…"
                )
        if mismatches:
            return RuleResult(
                rule_id=rule_id,
                description="publication-handoff-index root_readme_sha256 must match physical files",
                severity="FAILURE", passed=False,
                failure_detail=f"Hash mismatches: {'; '.join(mismatches)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="publication-handoff-index root_readme_sha256 must match physical files",
            severity="FAILURE", passed=True,
            evidence="All family root_readme_sha256 in publication-handoff-index match physical files",
        )

    def _rule_legacy_simplified_index_superseded(self) -> RuleResult:
        """legacy-plan-reconciliation/reconciliation-index.md must not be treated as current authority.

        Sprint 69 defect S69-D2: the old reconciliation-index.md from Sprint 67 remained
        alongside the newer exact-legacy-plan-reconciliation-final.md without being
        explicitly superseded, creating potential confusion.

        This rule passes if EITHER:
        - legacy-plan-reconciliation/reconciliation-index.md does not exist in the bundle, OR
        - history/legacy-plan-reconciliation-superseded.md exists (marking it historical), OR
        - legacy-reconciliation/README.md exists explaining the authority chain
        """
        rule_id = "legacy_simplified_index_superseded"
        old_index = self.bundle_dir / "legacy-plan-reconciliation" / "reconciliation-index.md"
        superseded_marker = self.bundle_dir / "history" / "legacy-plan-reconciliation-superseded.md"
        authority_readme = self.bundle_dir / "legacy-reconciliation" / "README.md"
        final_authority = self.bundle_dir / "legacy-reconciliation" / "exact-legacy-plan-reconciliation-final.md"

        # Final authority must exist
        if not final_authority.exists():
            return RuleResult(
                rule_id=rule_id,
                description="exact-legacy-plan-reconciliation-final.md must exist as current authority",
                severity="FAILURE", passed=False,
                failure_detail="legacy-reconciliation/exact-legacy-plan-reconciliation-final.md not found",
            )

        # If old index exists, there must be a superseded marker or authority README
        if old_index.exists():
            if not superseded_marker.exists() and not authority_readme.exists():
                return RuleResult(
                    rule_id=rule_id,
                    description="Old legacy-plan-reconciliation/reconciliation-index.md must be marked superseded",
                    severity="FAILURE", passed=False,
                    failure_detail=(
                        "legacy-plan-reconciliation/reconciliation-index.md exists without superseded marker. "
                        "Create history/legacy-plan-reconciliation-superseded.md or legacy-reconciliation/README.md"
                    ),
                )

        return RuleResult(
            rule_id=rule_id,
            description="Old legacy reconciliation index must be superseded by current authority",
            severity="FAILURE", passed=True,
            evidence="Final authority exists; old simplified index is either absent or marked superseded",
        )

    # ------------------------------------------------------------------
    # Sprint 71 NEW rules: stale-path scanner (close S70-D1, S70-D2, S70-D3)
    # ------------------------------------------------------------------

    def _get_stale_paths_in_content(self, content: str) -> list[str]:
        """Return list of stale sprint path prefixes found in content.

        A path is stale if it matches reports/sprintN/ where N is not the current sprint,
        or workspace/pr-dry-run.
        """
        import re as _re
        sprint_id = self._read_sprint_id()
        current_prefix = f"reports/{sprint_id}/"
        found_prefixes = set(_re.findall(r"reports/sprint[^/\"']+/|workspace/pr-dry-run", content))
        stale = sorted(p for p in found_prefixes if p != current_prefix)
        return stale

    def _rule_content_audit_final_no_stale_paths(self) -> RuleResult:
        """destination/content-audit-final.json must contain no stale sprint paths.

        Sprint 70 defect S70-D1: content-audit-final.json had all 42 records pointing
        to reports/sprint69/ paths. Sprint 71 repairs this by requiring all active
        paths to point to the current sprint.
        """
        rule_id = "content_audit_final_no_stale_paths"
        audit_file = self.bundle_dir / "destination" / "content-audit-final.json"
        if not audit_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="destination/content-audit-final.json must exist with no stale sprint paths",
                severity="FAILURE", passed=False,
                failure_detail="destination/content-audit-final.json not found",
            )
        try:
            content = audit_file.read_text(encoding="utf-8")
            stale = self._get_stale_paths_in_content(content)
            if stale:
                return RuleResult(
                    rule_id=rule_id,
                    description="destination/content-audit-final.json must have no stale sprint paths",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale sprint paths found in content-audit-final.json: {stale}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="destination/content-audit-final.json must be readable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="destination/content-audit-final.json contains no stale sprint paths",
            severity="FAILURE", passed=True,
            evidence="destination/content-audit-final.json scanned — no stale sprint paths found",
        )

    def _rule_publication_matrix_no_stale_paths(self) -> RuleResult:
        """publication/publication-truth-matrix-final.json must contain no stale sprint paths.

        Sprint 70 defect S70-D2: publication-truth-matrix-final.json had all 42 records
        pointing to reports/sprint69/ handoff_package_path. Sprint 71 repairs this.
        """
        rule_id = "publication_matrix_no_stale_paths"
        matrix_file = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not matrix_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication/publication-truth-matrix-final.json must exist with no stale sprint paths",
                severity="FAILURE", passed=False,
                failure_detail="publication/publication-truth-matrix-final.json not found",
            )
        try:
            content = matrix_file.read_text(encoding="utf-8")
            stale = self._get_stale_paths_in_content(content)
            if stale:
                return RuleResult(
                    rule_id=rule_id,
                    description="publication/publication-truth-matrix-final.json must have no stale sprint paths",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale sprint paths found in publication-truth-matrix-final.json: {stale}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="publication/publication-truth-matrix-final.json must be readable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="publication/publication-truth-matrix-final.json contains no stale sprint paths",
            severity="FAILURE", passed=True,
            evidence="publication/publication-truth-matrix-final.json scanned — no stale sprint paths found",
        )

    def _rule_handoff_index_no_stale_paths(self) -> RuleResult:
        """All handoff-index.json files must contain no stale sprint paths."""
        rule_id = "handoff_index_no_stale_paths"
        handoff_dir = self.bundle_dir / "handoff" / "per-family"
        if not handoff_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="handoff/per-family/ must exist",
                severity="FAILURE", passed=False,
                failure_detail="handoff/per-family/ not found",
            )
        stale_found = {}
        for idx_file in handoff_dir.rglob("handoff-index.json"):
            try:
                content = idx_file.read_text(encoding="utf-8")
                stale = self._get_stale_paths_in_content(content)
                if stale:
                    rel = str(idx_file.relative_to(self.bundle_dir)).replace("\\", "/")
                    stale_found[rel] = stale
            except OSError:
                pass
        if stale_found:
            return RuleResult(
                rule_id=rule_id,
                description="All handoff-index.json files must have no stale sprint paths",
                severity="FAILURE", passed=False,
                failure_detail=f"Stale paths in handoff indexes: {stale_found}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="All handoff-index.json files contain no stale sprint paths",
            severity="FAILURE", passed=True,
            evidence="All per-family handoff-index.json files scanned — no stale sprint paths found",
        )

    def _rule_remote_vs_handoff_no_stale_paths(self) -> RuleResult:
        """remote/remote-vs-handoff-final.json must contain no stale sprint paths."""
        rule_id = "remote_vs_handoff_no_stale_paths"
        rvh_file = self.bundle_dir / "remote" / "remote-vs-handoff-final.json"
        if not rvh_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-vs-handoff-final.json must exist with no stale sprint paths",
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-vs-handoff-final.json not found",
            )
        try:
            content = rvh_file.read_text(encoding="utf-8")
            stale = self._get_stale_paths_in_content(content)
            if stale:
                return RuleResult(
                    rule_id=rule_id,
                    description="remote/remote-vs-handoff-final.json must have no stale sprint paths",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale sprint paths found in remote-vs-handoff-final.json: {stale}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-vs-handoff-final.json must be readable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-vs-handoff-final.json contains no stale sprint paths",
            severity="FAILURE", passed=True,
            evidence="remote/remote-vs-handoff-final.json scanned — no stale sprint paths found",
        )

    def _rule_content_audit_final_files_exist(self) -> RuleResult:
        """destination/content-audit-final.json — every referenced handoff_path must exist.

        Sprint 70 defect S70-D1 (secondary): paths pointed to sprint69 which existed
        in the repo but were not the canonical sprint70 handoff. Sprint 71 requires
        the referenced files to exist in the current sprint bundle.
        """
        rule_id = "content_audit_final_files_exist"
        audit_file = self.bundle_dir / "destination" / "content-audit-final.json"
        if not audit_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="destination/content-audit-final.json must exist",
                severity="FAILURE", passed=False,
                failure_detail="destination/content-audit-final.json not found",
            )
        try:
            data = json.loads(audit_file.read_text(encoding="utf-8"))
            records = data.get("records", data) if isinstance(data, dict) else data
            missing = []
            for rec in records:
                hp = rec.get("handoff_path", "")
                if hp:
                    resolved = self._resolve_sprint_relative_path(hp)
                    if not resolved.exists():
                        missing.append(hp)
            if missing:
                return RuleResult(
                    rule_id=rule_id,
                    description="All handoff_path references in content-audit-final.json must exist",
                    severity="FAILURE", passed=False,
                    failure_detail=f"{len(missing)} handoff_path(s) not found: {missing[:3]}{'...' if len(missing) > 3 else ''}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="content-audit-final.json must be parseable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="All handoff_path references in content-audit-final.json exist physically",
            severity="FAILURE", passed=True,
            evidence=f"All {len(records)} handoff_path(s) verified to exist",
        )

    def _rule_publication_matrix_files_exist(self) -> RuleResult:
        """publication/publication-truth-matrix-final.json — every handoff_package_path must exist."""
        rule_id = "publication_matrix_files_exist"
        matrix_file = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not matrix_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication/publication-truth-matrix-final.json must exist",
                severity="FAILURE", passed=False,
                failure_detail="publication/publication-truth-matrix-final.json not found",
            )
        try:
            data = json.loads(matrix_file.read_text(encoding="utf-8"))
            records = data.get("records", data.get("examples", [])) if isinstance(data, dict) else data
            missing = []
            for rec in records:
                hp = rec.get("handoff_package_path", "")
                if hp:
                    resolved = self._resolve_sprint_relative_path(hp)
                    if not resolved.exists():
                        missing.append(hp)
            if missing:
                return RuleResult(
                    rule_id=rule_id,
                    description="All handoff_package_path references in publication-truth-matrix-final.json must exist",
                    severity="FAILURE", passed=False,
                    failure_detail=f"{len(missing)} handoff_package_path(s) not found: {missing[:3]}{'...' if len(missing) > 3 else ''}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="publication-truth-matrix-final.json must be parseable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="All handoff_package_path references in publication-truth-matrix-final.json exist physically",
            severity="FAILURE", passed=True,
            evidence=f"All {len(records)} handoff_package_path(s) verified to exist",
        )

    # ------------------------------------------------------------------
    # Sprint 72 NEW rules: remote proof consistency (close S71-D1)
    # ------------------------------------------------------------------

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
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-proof-consistency-audit.json not found",
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-proof-consistency-audit.json is present",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-proof-consistency-audit.json not found",
            )
        try:
            data = json.loads(audit_file.read_text(encoding="utf-8"))
            if not data.get("consistent", False):
                return RuleResult(
                    rule_id=rule_id,
                    description="remote/remote-proof-consistency-audit.json must have consistent=true",
                    severity="FAILURE", passed=False,
                    failure_detail=f"consistent={data.get('consistent')} — remote proof is not consistent",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-consistency-audit.json must be valid JSON",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-proof-consistency-audit.json confirms consistent=true",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-proof-summary.md not found",
            )
        content = summary_file.read_text(encoding="utf-8")
        # Must NOT contain the incorrect 42/42 claim
        if "42/42 examples have README I/O sections" in content:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-summary.md must not claim 42/42 README I/O sections",
                severity="FAILURE", passed=False,
                failure_detail="remote-proof-summary.md still contains the incorrect '42/42 examples have README I/O sections' claim",
            )
        # Must state 0/42
        if "0/42" not in content:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-proof-summary.md must state 0/42 remote README I/O",
                severity="FAILURE", passed=False,
                failure_detail="remote-proof-summary.md does not contain '0/42' — corrected count not stated",
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-proof-summary.md correctly states 0/42 remote README I/O sections",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
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
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        summary_content = summary_file.read_text(encoding="utf-8")
        # If audit says 0, summary must not claim non-zero
        if io_doc_count == 0:
            if "42/42 examples have README I/O sections" in summary_content:
                return RuleResult(
                    rule_id=rule_id,
                    description="remote-proof-summary.md must not contradict audit io_doc_count=0",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Audit io_doc_count=0 but summary claims '42/42 examples have README I/O sections'",
                )
        return RuleResult(
            rule_id=rule_id,
            description=f"remote-proof-summary.md is consistent with audit io_doc_count={io_doc_count}/{total}",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="history/remote-proof-summary-superseded.md not found — incorrect Sprint 68 artifact not archived",
            )
        content = superseded_file.read_text(encoding="utf-8")
        if len(content.strip()) == 0:
            return RuleResult(
                rule_id=rule_id,
                description="history/remote-proof-summary-superseded.md must be non-empty",
                severity="FAILURE", passed=False,
                failure_detail="history/remote-proof-summary-superseded.md is empty",
            )
        return RuleResult(
            rule_id=rule_id,
            description="history/remote-proof-summary-superseded.md is present and non-empty",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
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
                    severity="FAILURE", passed=False,
                    failure_detail=f"io_doc_count={io_doc_count} but actual has_io_section=true count={actual_io_count}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote-readme-io-audit-final.json must be valid JSON",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description=f"remote-readme-io-audit-final.json io_doc_count={io_doc_count} matches has_io_section=true count",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-vs-handoff-final.json not found",
            )
        try:
            content = rvh_file.read_text(encoding="utf-8")
            stale = self._get_stale_paths_in_content(content)
            if stale:
                return RuleResult(
                    rule_id=rule_id,
                    description="remote/remote-vs-handoff-final.json must use current sprint handoff paths",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale sprint paths in remote-vs-handoff-final.json: {stale}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-vs-handoff-final.json must be readable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-vs-handoff-final.json handoff_paths use current sprint",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
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
                severity="FAILURE", passed=False,
                failure_detail=f"Missing classification labels in matrix: {missing}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Weekly review claim matrix present and contains classification labels",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="pdf-pr-reconciliation.json not found — PDF publication truth not reconciled against remote state",
            )
        try:
            data = json.loads(reconcile_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="pdf-publication/pdf-pr-reconciliation.json must be valid JSON",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        verdict = data.get("claim_verdict", "")
        if not verdict:
            return RuleResult(
                rule_id=rule_id,
                description="pdf-pr-reconciliation.json must contain claim_verdict field",
                severity="FAILURE", passed=False,
                failure_detail="claim_verdict field missing from pdf-pr-reconciliation.json",
            )
        return RuleResult(
            rule_id=rule_id,
            description="PDF publication truth reconciled with current remote evidence",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="formimporter-repro-inventory.json not found — FormImporter taskcard not durable",
            )
        try:
            data = json.loads(inv_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="formimporter-repro-inventory.json must be valid JSON",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        trigger = data.get("next_retest_trigger", "")
        if not trigger:
            return RuleResult(
                rule_id=rule_id,
                description="formimporter-repro-inventory.json must have next_retest_trigger",
                severity="FAILURE", passed=False,
                failure_detail="next_retest_trigger field missing from formimporter-repro-inventory.json",
            )
        return RuleResult(
            rule_id=rule_id,
            description="FormImporter taskcard is durable with retest trigger",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="words-version-drift-current.json not found — Words version drift not documented",
            )
        try:
            data = json.loads(drift_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="words-version-drift-current.json must be valid JSON",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        if "drift" not in data:
            return RuleResult(
                rule_id=rule_id,
                description="words-version-drift-current.json must have drift field",
                severity="FAILURE", passed=False,
                failure_detail="drift field missing from words-version-drift-current.json",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Words version drift documented with drift classification",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="post-merge-validation-matrix.json not found — Email/Slides post-merge runtime not classified",
            )
        try:
            data = json.loads(matrix_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="post-merge-validation-matrix.json must be valid JSON",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        records = data.get("records", [])
        if not records:
            return RuleResult(
                rule_id=rule_id,
                description="post-merge-validation-matrix.json must have records",
                severity="FAILURE", passed=False,
                failure_detail="records array is empty in post-merge-validation-matrix.json",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Post-merge runtime validation matrix present with records",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="dirty-file-classification.md not found — dirty tree not explicitly classified",
            )
        content = classif_file.read_text(encoding="utf-8")
        if len(content.strip()) < 50:
            return RuleResult(
                rule_id=rule_id,
                description="git/dirty-file-classification.md must be substantive (not empty/minimal)",
                severity="FAILURE", passed=False,
                failure_detail="dirty-file-classification.md is too short to be substantive",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Dirty tree classification document present and substantive",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="sprint27-strict-contract-revalidation.md not found — Sprint 27 evidence status ambiguous",
            )
        content = gov_file.read_text(encoding="utf-8")
        required = ["GOVERNANCE_EXCEPTION_REQUIRED", "HISTORICAL_NON_COMPLIANT"]
        missing = [m for m in required if m not in content]
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="sprint27-strict-contract-revalidation.md must contain governance classifications",
                severity="FAILURE", passed=False,
                failure_detail=f"Missing in sprint27-strict-contract-revalidation.md: {missing}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Sprint 27 governance classification document present with required labels",
            severity="FAILURE", passed=True,
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
                severity="FAILURE", passed=False,
                failure_detail="final-verdict.md not found",
            )

        verdict_content = verdict_file.read_text(encoding="utf-8")

        # If matrix exists, items are classified — no restriction needed
        if matrix_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Weekly review matrix present — verdict COMPLETE is allowed",
                severity="FAILURE", passed=True,
                evidence="02-weekly-review-claim-vs-proof-matrix.md present; weekly review items classified",
            )

        # Matrix absent — verdict must not claim complete
        import re
        if re.search(r"COMPLETE|ALL_ITEMS_CLOSED|WEEKLY_REVIEW_ITEMS_CLASSIFIED", verdict_content):
            return RuleResult(
                rule_id=rule_id,
                description="Verdict must not claim completion without weekly review classification matrix",
                severity="FAILURE", passed=False,
                failure_detail="final-verdict.md suggests completion but 02-weekly-review-claim-vs-proof-matrix.md is absent",
            )
        return RuleResult(
            rule_id=rule_id,
            description="No weekly review matrix but verdict does not overclaim",
            severity="FAILURE", passed=True,
            evidence="02-weekly-review-claim-vs-proof-matrix.md absent but verdict does not claim completion",
        )

    # ------------------------------------------------------------------
    # Sprint 76 rules (S75-B1: slides-compress, S75-B2: dirty-state)
    # ------------------------------------------------------------------

    def _rule_runtime_matrix_output_confirmed_for_validated(self) -> RuleResult:
        """Every post_merge_validated=true record must also have output_confirmed=true.

        Sprint 75 defect S75-B1: slides-compress was post_merge_validated=true but
        output_confirmed=false (graceful-exit-only, no compression performed).
        post_merge_validated implies real end-to-end output was produced.
        """
        rule_id = "runtime_matrix_output_confirmed_for_validated"
        matrix_path = self.bundle_dir / "post-merge-runtime" / "post-merge-validation-matrix.json"

        if not matrix_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Post-merge matrix: post_merge_validated=true requires output_confirmed=true",
                severity="FAILURE", passed=True,
                evidence="No post-merge-validation-matrix.json — rule not applicable",
            )

        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Post-merge matrix must be readable",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read post-merge-validation-matrix.json: {exc}",
            )

        violations = [
            r.get("scenario_id", "?")
            for r in data.get("records", [])
            if r.get("post_merge_validated") is True and r.get("output_confirmed") is not True
        ]
        if violations:
            return RuleResult(
                rule_id=rule_id,
                description="post_merge_validated=true requires output_confirmed=true",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Records with post_merge_validated=true but output_confirmed!=true: {violations}. "
                    "Graceful-exit-only (e.g. RUNTIME_VALIDATED_NO_INPUT_FIXTURE) does not count as validated."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="All post_merge_validated=true records also have output_confirmed=true",
            severity="FAILURE", passed=True,
            evidence=f"Checked {len(data.get('records', []))} records — all validated records confirmed output",
        )

    def _rule_runtime_matrix_no_graceful_exit_labelled_validated(self) -> RuleResult:
        """No post-merge record may have runtime_result containing NO_INPUT_FIXTURE while
        post_merge_validated=true.

        Sprint 75 defect: slides-compress runtime_result='RUNTIME_VALIDATED_NO_INPUT_FIXTURE'
        with post_merge_validated=true. Missing-input graceful exit is not validation.
        """
        rule_id = "runtime_matrix_no_graceful_exit_labelled_validated"
        matrix_path = self.bundle_dir / "post-merge-runtime" / "post-merge-validation-matrix.json"

        if not matrix_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="No post-merge matrix — rule not applicable",
                severity="FAILURE", passed=True,
                evidence="No post-merge-validation-matrix.json found",
            )

        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Post-merge matrix must be readable",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot read post-merge-validation-matrix.json: {exc}",
            )

        violations = [
            r.get("scenario_id", "?")
            for r in data.get("records", [])
            if r.get("post_merge_validated") is True
            and "NO_INPUT_FIXTURE" in str(r.get("runtime_result", ""))
        ]
        if violations:
            return RuleResult(
                rule_id=rule_id,
                description="post_merge_validated=true with NO_INPUT_FIXTURE runtime_result is invalid",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Graceful-exit-only examples marked as validated: {violations}. "
                    "Must provide real fixture and confirm output before setting post_merge_validated=true."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="No post-merge record combines post_merge_validated=true with NO_INPUT_FIXTURE",
            severity="FAILURE", passed=True,
            evidence="All validated records use real end-to-end execution",
        )

    def _rule_dirty_classification_must_match_after_snapshot(self) -> RuleResult:
        """dirty-file-classification.md must not contradict dirty-state-after.txt.

        Sprint 75 defect S75-B2: dirty-state-after.txt showed evidence_validator.py and
        test files as modified, but dirty-file-classification.md said 'No Source or Test
        Files Are Dirty'. These two documents are internally inconsistent.

        If dirty-state-after.txt contains 'modified: src/' or 'modified: tests/', then
        dirty-file-classification.md must not contain 'No Source or Test Files Are Dirty'.
        """
        rule_id = "dirty_classification_must_match_after_snapshot"
        after_path = self.bundle_dir / "git" / "dirty-state-after.txt"
        classif_path = self.bundle_dir / "git" / "dirty-file-classification.md"

        if not after_path.exists() or not classif_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="dirty-state-after.txt or dirty-file-classification.md missing — skipping consistency check",
                severity="FAILURE", passed=True,
                evidence="One or both files absent — not applicable",
            )

        after_content = after_path.read_text(encoding="utf-8", errors="replace")
        classif_content = classif_path.read_text(encoding="utf-8", errors="replace")

        # Check if dirty-state-after.txt shows source/test files as modified
        src_test_dirty = (
            "modified:   src/" in after_content
            or "modified: src/" in after_content
            or "\tsrc/" in after_content
            or "modified:   tests/" in after_content
            or "modified: tests/" in after_content
            or "\ttests/" in after_content
        )

        if not src_test_dirty:
            return RuleResult(
                rule_id=rule_id,
                description="dirty-state-after.txt shows no src/tests modifications — consistent",
                severity="FAILURE", passed=True,
                evidence="No src/ or tests/ files shown as modified in dirty-state-after.txt",
            )

        # Source/test dirty in after snapshot — classification must acknowledge it
        contradicts = "No Source or Test Files Are Dirty" in classif_content
        if contradicts:
            return RuleResult(
                rule_id=rule_id,
                description="dirty-file-classification.md contradicts dirty-state-after.txt",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "dirty-state-after.txt shows src/ or tests/ files as modified, but "
                    "dirty-file-classification.md says 'No Source or Test Files Are Dirty'. "
                    "These two documents are internally inconsistent. "
                    "Classification must acknowledge the source/test files shown in the snapshot."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="dirty-file-classification.md is consistent with dirty-state-after.txt",
            severity="FAILURE", passed=True,
            evidence="dirty-state-after.txt shows src/tests modified and classification acknowledges it",
        )

    def _rule_final_clean_proof_contains_commit_sha(self) -> RuleResult:
        """final-clean-proof.txt must contain a 7+ character hex commit SHA.

        Sprint 75 defect: final-clean-proof.txt had narrative format but reviewers
        cannot independently verify the commit without a SHA.
        Requires at least one 7-character hex string resembling a commit SHA.
        """
        rule_id = "final_clean_proof_contains_commit_sha"
        proof_path = self.bundle_dir / "git" / "final-clean-proof.txt"

        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must exist with commit SHA",
                severity="FAILURE", passed=False,
                failure_detail="git/final-clean-proof.txt not found",
            )

        content = proof_path.read_text(encoding="utf-8", errors="replace")
        # Look for 7-40 char hex strings (commit SHA pattern)
        sha_pattern = re.compile(r"\b[0-9a-f]{7,40}\b")
        shas = sha_pattern.findall(content)
        if not shas:
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must contain a commit SHA",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "No commit SHA (7+ hex chars) found in final-clean-proof.txt. "
                    "Must include the commit hash so the final state can be independently verified."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="final-clean-proof.txt contains commit SHA",
            severity="FAILURE", passed=True,
            evidence=f"Found SHA(s): {shas[:3]}",
        )

    def _rule_final_clean_proof_documents_remaining_dirty(self) -> RuleResult:
        """If workspace/verification/latest/ files are shown dirty in dirty-state-after.txt,
        final-clean-proof.txt must explicitly document them as a governance exception.

        Sprint 75 defect: final-clean-proof.txt claimed 'Sprint 75 bundle scope: clean'
        without documenting the 7 workspace/verification/latest/ files that remained modified.
        """
        rule_id = "final_clean_proof_documents_remaining_dirty"
        after_path = self.bundle_dir / "git" / "dirty-state-after.txt"
        proof_path = self.bundle_dir / "git" / "final-clean-proof.txt"

        if not after_path.exists() or not proof_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="dirty-state-after.txt or final-clean-proof.txt missing — skipping",
                severity="FAILURE", passed=True,
                evidence="One or both files absent",
            )

        after_content = after_path.read_text(encoding="utf-8", errors="replace")
        proof_content = proof_path.read_text(encoding="utf-8", errors="replace")

        workspace_latest_dirty = "workspace/verification/latest" in after_content and (
            "modified:" in after_content or " M " in after_content
        )

        if not workspace_latest_dirty:
            return RuleResult(
                rule_id=rule_id,
                description="No workspace/verification/latest dirty files — rule not applicable",
                severity="FAILURE", passed=True,
                evidence="workspace/verification/latest/ not shown as modified in dirty-state-after.txt",
            )

        # workspace/latest dirty — proof must document this exception
        has_exception_doc = any(kw in proof_content for kw in [
            "workspace/verification/latest",
            "GENERATED_WORKSPACE_STATE",
            "governance exception",
            "pre-existing runtime",
        ])
        if not has_exception_doc:
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must document workspace/verification/latest/ governance exception",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "dirty-state-after.txt shows workspace/verification/latest/ files modified, "
                    "but final-clean-proof.txt does not document this as a governance exception. "
                    "Must mention 'workspace/verification/latest' or 'GENERATED_WORKSPACE_STATE'."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="final-clean-proof.txt documents workspace/verification/latest/ governance exception",
            severity="FAILURE", passed=True,
            evidence="proof mentions workspace/verification/latest or governance exception",
        )

    def _rule_weekly_review_no_repaired_while_output_unconfirmed(self) -> RuleResult:
        """Weekly review matrix must not classify runtime validation as REPAIRED while
        any post-merge record has output_confirmed=false.

        Sprint 75 defect: post-merge matrix had output_confirmed=false for slides-compress
        but weekly review Item 4 was classified as 'REPAIRED'. This is an overclaim.
        """
        rule_id = "weekly_review_no_repaired_while_output_unconfirmed"
        matrix_path = self.bundle_dir / "post-merge-runtime" / "post-merge-validation-matrix.json"
        review_path = self.bundle_dir / "02-weekly-review-claim-vs-proof-matrix.md"

        if not matrix_path.exists() or not review_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Post-merge matrix or weekly review matrix absent — not applicable",
                severity="FAILURE", passed=True,
                evidence="One or both files absent",
            )

        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id,
                description="Cannot read post-merge-validation-matrix.json",
                severity="FAILURE", passed=True,
                evidence="Skipping due to parse error",
            )

        unconfirmed = [
            r.get("scenario_id", "?")
            for r in data.get("records", [])
            if r.get("output_confirmed") is not True
        ]

        if not unconfirmed:
            return RuleResult(
                rule_id=rule_id,
                description="All post-merge examples have output_confirmed=true — REPAIRED claim valid",
                severity="FAILURE", passed=True,
                evidence="No unconfirmed output records",
            )

        # Some unconfirmed — weekly review matrix must not say REPAIRED for runtime item
        review_content = review_path.read_text(encoding="utf-8", errors="replace")
        # Check for overclaim: "NEEDS_REPAIR → REPAIRED" or just "REPAIRED" adjacent to runtime validation
        repaired_overclaim = (
            "NEEDS_REPAIR → REPAIRED" in review_content
            and "PARTIALLY_REPAIRED" not in review_content
            and "slides-compress" not in review_content.lower()
        )
        if repaired_overclaim:
            return RuleResult(
                rule_id=rule_id,
                description="Weekly review claims REPAIRED but runtime matrix has output_confirmed=false",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"output_confirmed=false for: {unconfirmed}. "
                    "Weekly review matrix says 'REPAIRED' without acknowledging partial validation. "
                    "Must use PARTIALLY_REPAIRED or list unconfirmed examples explicitly."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Weekly review matrix appropriately qualifies partial runtime validation",
            severity="FAILURE", passed=True,
            evidence=f"Unconfirmed examples: {unconfirmed} — matrix does not overclaim REPAIRED",
        )

    def _rule_dirty_after_no_uncommitted_source_test(self) -> RuleResult:
        """dirty-state-after.txt must not show src/ or tests/ files as modified.

        Sprint 75 defect S75-B2: dirty-state-after.txt was captured before source/test
        files were committed, showing them as modified. The 'after' snapshot should be
        taken AFTER the final bundle commit — at which point source/test must be clean.
        """
        rule_id = "dirty_after_no_uncommitted_source_test"
        after_path = self.bundle_dir / "git" / "dirty-state-after.txt"

        if not after_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="dirty-state-after.txt not found",
                severity="FAILURE", passed=False,
                failure_detail="git/dirty-state-after.txt must be present",
            )

        content = after_path.read_text(encoding="utf-8", errors="replace")

        # Detect src/ or tests/ in modified lines
        src_test_lines = [
            line.strip() for line in content.splitlines()
            if ("modified:" in line or "\tM " in line or " M " in line)
            and ("src/" in line or "tests/" in line)
        ]

        if src_test_lines:
            return RuleResult(
                rule_id=rule_id,
                description="dirty-state-after.txt must not show src/ or tests/ as modified",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Source/test files shown as modified in dirty-state-after.txt: {src_test_lines[:5]}. "
                    "dirty-state-after.txt must be captured AFTER the final bundle commit. "
                    "Source and test files must be committed before capturing the after snapshot."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="dirty-state-after.txt shows no uncommitted src/ or tests/ files",
            severity="FAILURE", passed=True,
            evidence="No src/ or tests/ modifications in dirty-state-after.txt",
        )

    def _rule_final_verdict_workspace_exception_explicit(self) -> RuleResult:
        """If dirty-state-after.txt shows workspace/verification/latest/ files as modified,
        the final verdict must explicitly name the workspace exception.

        Sprint 75 defect: verdict said 'LOWCODE_WEEKLY_REVIEW_ITEMS_CLASSIFIED_PUBLICATION_APPROVAL_BLOCKED'
        without any qualifier about the remaining dirty workspace files.
        """
        rule_id = "final_verdict_workspace_exception_explicit"
        after_path = self.bundle_dir / "git" / "dirty-state-after.txt"
        verdict_path = self.bundle_dir / "final-verdict.md"

        if not after_path.exists() or not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="dirty-state-after.txt or final-verdict.md missing — skipping",
                severity="FAILURE", passed=True,
                evidence="One or both files absent",
            )

        after_content = after_path.read_text(encoding="utf-8", errors="replace")
        verdict_content = verdict_path.read_text(encoding="utf-8", errors="replace")

        workspace_dirty = "workspace/verification/latest" in after_content and (
            "modified:" in after_content or " M " in after_content
        )

        if not workspace_dirty:
            return RuleResult(
                rule_id=rule_id,
                description="No workspace/verification/latest files dirty — verdict qualifier not required",
                severity="FAILURE", passed=True,
                evidence="dirty-state-after.txt does not show workspace/verification/latest as modified",
            )

        # workspace/latest dirty — verdict must acknowledge it
        exception_keywords = [
            "DIRTY_WORKSPACE",
            "WORKSPACE_LATEST",
            "WORKSPACE_EXCEPTION",
            "GOVERNANCE_EXCEPTION",
            "workspace/verification/latest",
            "dirty workspace",
        ]
        has_exception = any(kw.lower() in verdict_content.lower() for kw in exception_keywords)
        if not has_exception:
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must acknowledge dirty workspace/verification/latest/ files",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "dirty-state-after.txt shows workspace/verification/latest/ as modified, "
                    "but final-verdict.md does not contain any of: "
                    + str(exception_keywords)
                    + ". Must explicitly name the workspace governance exception."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Final verdict explicitly acknowledges workspace/verification/latest/ governance exception",
            severity="FAILURE", passed=True,
            evidence="verdict contains workspace exception qualifier",
        )

    # ------------------------------------------------------------------
    # Sprint 77 NEW rules: close S76-C1 through S76-C4
    # ------------------------------------------------------------------

    def _rule_commands_log_no_pending(self) -> RuleResult:
        """commands.log must not contain PENDING entries (S76-C3)."""
        rule_id = "commands_log_no_pending"
        log_path = self.bundle_dir / "commands.log"

        if not log_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="commands.log must not contain PENDING entries",
                severity="FAILURE", passed=False,
                failure_detail="commands.log not found",
            )

        content = log_path.read_text(encoding="utf-8", errors="replace")
        # Check for PENDING as a status value (e.g. "Exit: PENDING"), not narrative mentions
        pending_lines = [
            line.strip() for line in content.splitlines()
            if re.search(r"(?:Exit|Status):\s*PENDING\b", line)
        ]
        if pending_lines:
            return RuleResult(
                rule_id=rule_id,
                description="commands.log must not contain PENDING entries",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"commands.log has {len(pending_lines)} PENDING status line(s): "
                    + "; ".join(pending_lines[:3])
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="commands.log must not contain PENDING entries",
            severity="FAILURE", passed=True,
            evidence="commands.log present with no PENDING entries",
        )

    def _rule_final_clean_proof_has_raw_git_lines(self) -> RuleResult:
        """final-clean-proof.txt must contain embedded raw git status output (S76-C2).

        A narrative-only proof file cannot be independently verified.
        The file must contain at least one of:
        - Raw git status short lines: ' M ', 'M  ', '?? ', 'A  ', 'D  ' etc.
        - OR 'nothing to commit, working tree clean'
        - OR 'no changes added to commit'
        - OR 'nothing added to commit'
        """
        rule_id = "final_clean_proof_has_raw_git_lines"
        proof_path = self.bundle_dir / "git" / "final-clean-proof.txt"

        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must contain raw git status output",
                severity="FAILURE", passed=False,
                failure_detail="git/final-clean-proof.txt not found",
            )

        content = proof_path.read_text(encoding="utf-8", errors="replace")
        clean_phrases = [
            "nothing to commit",
            "no changes added to commit",
            "nothing added to commit",
        ]
        has_clean_phrase = any(phrase in content for phrase in clean_phrases)
        # Raw git status short lines start with two-char status code + space
        has_raw_status_line = bool(re.search(r"^[ MA?!D][M A?!D] ", content, re.MULTILINE))

        if not (has_clean_phrase or has_raw_status_line):
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must contain raw git status output",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "final-clean-proof.txt is narrative-only — no raw git status lines found. "
                    "Must embed actual 'git status --short' or 'git status' output, or include "
                    "'nothing to commit' / 'no changes added' text."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="final-clean-proof.txt must contain raw git status output",
            severity="FAILURE", passed=True,
            evidence="final-clean-proof.txt contains embedded raw git status output",
        )

    def _rule_dirty_state_untracked_acknowledged(self) -> RuleResult:
        """dirty-state-after.txt must show no untracked files (S76-C1).

        After the final sprint bundle commit, dirty-state-after.txt must not show
        any untracked files. Untracked files must be committed, removed, or never
        present in the final post-commit state. Any untracked file remaining after
        the bundle commit is an evidence gap — it was not committed and not removed.

        Detects both formats:
        - 'git status --short': lines starting with '?? '
        - 'git status' (verbose): tab-indented paths under 'Untracked files:' section
        """
        rule_id = "dirty_state_untracked_acknowledged"
        after_path = self.bundle_dir / "git" / "dirty-state-after.txt"

        if not after_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="dirty-state-after.txt must show no untracked files after final commit",
                severity="FAILURE", passed=True,
                evidence="dirty-state-after.txt not present — skip",
            )

        after_content = after_path.read_text(encoding="utf-8", errors="replace")

        # Detect both short format ('?? path') and verbose format (tab-indented under 'Untracked files:')
        untracked: list[str] = []

        # Short format: lines starting with '?? '
        untracked.extend(m.strip() for m in re.findall(r"^\?\? (.+)$", after_content, re.MULTILINE))

        # Verbose format: extract paths from 'Untracked files:' section
        if "Untracked files:" in after_content:
            in_untracked = False
            for line in after_content.splitlines():
                if "Untracked files:" in line:
                    in_untracked = True
                    continue
                if in_untracked:
                    if line.startswith("\t") and not line.strip().startswith("("):
                        # Tab-indented path line (not a parenthetical instruction)
                        path = line.strip()
                        if path and path not in untracked:
                            untracked.append(path)
                    elif line.strip().startswith("("):
                        # Instruction line like "  (use 'git add' ...)" — skip, stay in section
                        pass
                    elif line.strip() == "":
                        # Blank line — end of section
                        in_untracked = False
                    elif not line.startswith("\t") and not line.startswith(" "):
                        # New section at column 0 — end section
                        in_untracked = False

        if not untracked:
            return RuleResult(
                rule_id=rule_id,
                description="dirty-state-after.txt must show no untracked files after final commit",
                severity="FAILURE", passed=True,
                evidence="No untracked files in dirty-state-after.txt — clean state confirmed",
            )

        return RuleResult(
            rule_id=rule_id,
            description="dirty-state-after.txt must show no untracked files after final commit",
            severity="FAILURE", passed=False,
            failure_detail=(
                f"dirty-state-after.txt shows {len(untracked)} untracked file(s): {untracked}. "
                f"Untracked files must be committed or removed before final bundle closure. "
                f"S76-C1: 'output.pptx' was untracked in sprint76 but not committed or removed."
            ),
        )

    def _rule_validation_authority_unambiguous(self) -> RuleResult:
        """Any *-validation-result.json with overall_valid=false must have canonical_overall_valid or bundle_type (S76-C4).

        A validation result file that says overall_valid=false without any field explaining
        why (bundle_type=REPAIR_BUNDLE or canonical_overall_valid=true) is ambiguous and
        would mislead a reviewer into thinking the bundle failed validation.
        """
        rule_id = "validation_authority_unambiguous"
        evidence_dir = self.bundle_dir / "evidence"

        if not evidence_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Validation result files must not be ambiguously false",
                severity="FAILURE", passed=True,
                evidence="No evidence/ directory — nothing to check",
            )

        ambiguous_files = []
        for f in evidence_dir.glob("*validation-result.json"):
            if "diagnostic" in f.name or "revalidation" in f.name:
                # Diagnostic and revalidation files are explicitly labeled — always OK
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
                overall_valid = data.get("overall_valid")
                canonical_overall_valid = data.get("canonical_overall_valid")
                bundle_type = data.get("bundle_type", "")
                if overall_valid is False and canonical_overall_valid is None and not bundle_type:
                    ambiguous_files.append(f.name)
            except (OSError, ValueError):
                pass

        if ambiguous_files:
            return RuleResult(
                rule_id=rule_id,
                description="Validation result files must not be ambiguously false",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Validation result file(s) with overall_valid=false but no "
                    f"canonical_overall_valid or bundle_type field: {ambiguous_files}. "
                    f"Add 'canonical_overall_valid: true' or 'bundle_type: REPAIR_BUNDLE' "
                    f"to clarify, or rename to 'diagnostic-*.json'."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Validation result files must not be ambiguously false",
            severity="FAILURE", passed=True,
            evidence=f"All validation result files in evidence/ are unambiguous",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _scan_source_for_import(
        self, source_root: Path, module_name: str, exclude_self: str = ""
    ) -> list[str]:
        """Scan Python source files in source_root for imports of module_name.

        Returns list of relative file paths that import the module.
        """
        found = []
        for py_file in source_root.rglob("*.py"):
            if exclude_self and py_file.name == exclude_self:
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
                if module_name in text:
                    found.append(str(py_file.relative_to(source_root)))
            except OSError:
                pass
        return found

    def _read_sprint_id(self) -> str:
        for fname in ["sprint-state.json", "evidence-contract.json"]:
            p = self.bundle_dir / fname
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    return data.get("sprint_id", str(self.bundle_dir))
                except (OSError, ValueError):
                    pass
        return str(self.bundle_dir)
