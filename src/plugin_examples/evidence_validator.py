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
