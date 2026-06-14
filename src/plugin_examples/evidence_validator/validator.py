"""Evidence validator — main class composing all rule mixins."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from plugin_examples.evidence_validator.helpers import ValidatorHelpers
from plugin_examples.evidence_validator.models import RuleResult, ValidationReport
from plugin_examples.evidence_validator.rules import (
    ContentAuditRules,
    CoreRules,
    RemoteProofRules,
    SemanticRules,
    Sprint67Rules,
    Sprint68to69Rules,
    Sprint70to71Rules,
    Sprint72to75Rules,
    Sprint76to77Rules,
    Sprint78to83Rules,
    Sprint84to86Rules,
    Sprint87to88Rules,
    Sprint89Rules,
)
from plugin_examples.observability import get_logger

logger = get_logger(__name__)

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


class EvidenceValidator(
    ValidatorHelpers,
    CoreRules,
    SemanticRules,
    ContentAuditRules,
    RemoteProofRules,
    Sprint67Rules,
    Sprint68to69Rules,
    Sprint70to71Rules,
    Sprint72to75Rules,
    Sprint76to77Rules,
    Sprint78to83Rules,
    Sprint84to86Rules,
    Sprint87to88Rules,
    Sprint89Rules,
):
    """Validates a sprint evidence bundle against closure quality rules."""

    def __init__(self, bundle_dir: Path, source_root: Path | None = None) -> None:
        self.bundle_dir = bundle_dir
        self.source_root = source_root

    def validate(self, exclude_rule_ids: set[str] | None = None) -> ValidationReport:
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

        # --- Sprint 78 NEW rules: close S77-D1 through S77-D3 ---
        _maybe(self._rule_publication_truth_no_stale_remote_claimed())
        _maybe(self._rule_handoff_validation_result_has_valid_flag())
        _maybe(self._rule_remote_repo_state_all_accessible())

        # --- Sprint 79 NEW rules: close S78-E1 and S78-E2 ---
        _maybe(self._rule_ecc_closure_valid_only_if_no_blocking_failures())
        _maybe(self._rule_diagnostic_bundle_file_has_nonblocking_label())

        # --- Sprint 80 NEW rules: close S79-B1 ---
        _maybe(self._rule_no_active_validation_file_with_ambiguous_false())

        # --- Sprint 83 NEW rules: close S82-F1 through S82-F4 ---
        _maybe(self._rule_publication_truth_matrix_has_expected_count())
        _maybe(self._rule_root_readme_conflict_strategy_documented())
        _maybe(self._rule_final_consistency_check_not_stale_after_commit())
        _maybe(self._rule_publication_file_plan_present_if_pr_creation_claimed())

        # --- Sprint 84 NEW rules: close S83-G1 through S83-G4 ---
        _maybe(self._rule_pr_batching_strategy_present_if_pr_creation_attempted())
        _maybe(self._rule_pr_batching_plan_present_if_pr_creation_attempted())
        _maybe(self._rule_root_readme_file_plan_present_before_pr_creation())
        _maybe(self._rule_no_bulk_42pr_plan_without_justification())

        # --- Sprint 85 NEW rules: close S84-H1 through S84-H5 ---
        _maybe(self._rule_bundle_manifest_source_sha_not_tbd())
        _maybe(self._rule_no_stale_will_capture_text_in_final_consistency())
        _maybe(self._rule_no_stale_pending_lane_label_in_tracking())
        _maybe(self._rule_scoreboard_ev_applicable_not_tbd())
        _maybe(self._rule_bundle_manifest_source_sha_in_final_clean_proof())

        # --- Sprint 86 NEW rules: readiness-loop prevention ---
        _maybe(self._rule_baseline_freeze_present_if_14_consecutive_blocked())
        _maybe(self._rule_no_readiness_only_verdict_after_baseline_freeze())

        # --- Sprint 87 NEW rules: S86 defect invariants + advancement ---
        _maybe(self._rule_commands_log_no_result_pending())
        _maybe(self._rule_validation_result_not_placeholder())
        _maybe(self._rule_sha_chain_reconciled_in_manifest())
        _maybe(self._rule_approval_vars_consistent_naming())
        _maybe(self._rule_words_drift_status_consistent())
        _maybe(self._rule_final_clean_proof_has_diff_and_log())
        _maybe(self._rule_next_family_discovery_not_just_relisting())
        _maybe(self._rule_baseline_freeze_not_avoiding_advancement())

        # --- Sprint 88 NEW rules: S87 defect invariants ---
        _maybe(self._rule_bundle_manifest_has_head_sha())
        _maybe(self._rule_publication_truth_matrix_present_when_publication_claimed())
        _maybe(self._rule_next_family_candidate_matrix_has_real_checks())
        _maybe(self._rule_implementation_summary_present_if_advancement())
        _maybe(self._rule_discovery_blocked_candidates_have_blocker_detail())
        _maybe(self._rule_version_drift_reconciliation_present_if_drift_active())

        # --- Sprint 89 NEW rules: S88 defect invariants ---
        _maybe(self._rule_head_sha_matches_final_proof())
        _maybe(self._rule_active_validation_not_not_canonical())
        _maybe(self._rule_source_proof_present_if_source_changed())
        _maybe(self._rule_no_lowcode_confirmed_has_evidence())
        _maybe(self._rule_candidate_classification_not_stale_after_scan())
        _maybe(self._rule_no_op_examples_eliminated())
        _maybe(self._rule_all_six_family_packages_present())

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
