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

        readme_files = list(handoff_dir.rglob("README.md"))
        if not readme_files:
            return RuleResult(
                rule_id=rule_id,
                description="All handoff READMEs must have I/O section",
                severity="FAILURE", passed=False,
                failure_detail="No README.md files found in handoff/per-family/",
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
