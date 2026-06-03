"""Evidence validation rules — CoreRules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)


_UNCHECKED_TODO_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)


class CoreRules:
    """Rule mixin for evidence validation."""

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
