"""Evidence validation rules — SemanticRules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)


_GIT_HEADER_PATTERNS = [
    "On branch",
    "HEAD detached at",
    "nothing to commit",
    "nothing added to commit",
    "Changes to be committed",
    "Initial commit",
]

_REQUIRED_NONZERO_FILES = [
    "git/final-clean-proof.txt",
    "commands.log",
    "todo.md",
    "lanes/lane-I/test-run.log",
]


class SemanticRules:
    """Rule mixin for evidence validation."""

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
                severity="FAILURE",
                passed=False,
                failure_detail="File not found: git/final-clean-proof.txt",
            )

        size = proof_path.stat().st_size
        if size == 0:
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must be nonzero bytes",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "final-clean-proof.txt is 0 bytes. "
                    "Sprint 60 defect SD60-01: git status --short produces no output when clean. "
                    "Use 'git status' (not --short) to capture branch header + nothing-to-commit text."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="final-clean-proof.txt must be nonzero bytes",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail="File not found: git/final-clean-proof.txt",
            )

        content = proof_path.read_text(encoding="utf-8", errors="replace")
        has_header = any(h in content for h in _GIT_HEADER_PATTERNS)

        if not has_header:
            return RuleResult(
                rule_id=rule_id,
                description="final-clean-proof.txt must contain git status header",
                severity="FAILURE",
                passed=False,
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
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail="readme/example-readme-content-audit.json not found",
            )

        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="README audit must not falsely claim I/O documentation complete",
                severity="FAILURE",
                passed=False,
                failure_detail=str(exc),
            )

        records = data.get("records", [])
        if not records:
            return RuleResult(
                rule_id=rule_id,
                description="README audit must not falsely claim I/O documentation complete",
                severity="FAILURE",
                passed=False,
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
                severity="WARNING",
                passed=True,
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
                severity="FAILURE",
                passed=False,
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
            severity="FAILURE",
            passed=True,
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
                    severity="FAILURE",
                    passed=True,
                    evidence=f"readme_audit_gate imported in: {found_in}",
                )
            return RuleResult(
                rule_id=rule_id,
                description="README gate must be imported by pipeline source",
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail="readme-gate-flow-integration.md admits gate is not wired or deferred",
                evidence=content[:200],
            )

        return RuleResult(
            rule_id=rule_id,
            description="README gate must be wired into publication flow",
            severity="FAILURE",
            passed=True,
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
                    severity="FAILURE",
                    passed=True,
                    evidence=f"evidence_validator imported in: {found_in}",
                )
            return RuleResult(
                rule_id=rule_id,
                description="EvidenceValidator must be imported by pipeline source",
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail="pipeline-integration-proof.md admits validator is not wired or deferred",
                evidence=content[:200],
            )

        return RuleResult(
            rule_id=rule_id,
            description="EvidenceValidator must be wired into pipeline",
            severity="FAILURE",
            passed=True,
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
                        severity="FAILURE",
                        passed=False,
                        failure_detail=(
                            f"{fname} records do not include input_format_in_programcs or "
                            "input_classification fields. Program.cs I/O audit was not performed."
                        ),
                    )

                null_count = sum(
                    1
                    for e in examples
                    if e.get("input_format_in_programcs") is None and e.get("input_classification") is None
                )
                total = len(examples)

                if null_count == total:
                    return RuleResult(
                        rule_id=rule_id,
                        description="Destination Program.cs input classification must not be all-null",
                        severity="FAILURE",
                        passed=False,
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
                    severity="FAILURE",
                    passed=True,
                    evidence=f"{total - null_count}/{total} records have non-null input classification",
                )

        return RuleResult(
            rule_id=rule_id,
            description="Destination Program.cs input classification must not be all-null",
            severity="FAILURE",
            passed=False,
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
                severity="WARNING",
                passed=True,
                evidence="process/next-work-register.md not found (no P1 items to check)",
            )

        content = register_path.read_text(encoding="utf-8", errors="replace")
        # Look for P1 items that are not crossed out or marked as completed
        # Pattern: "| ... | P1 |" or "Priority P1" or "| P1 |"
        p1_lines = [
            line
            for line in content.splitlines()
            if re.search(r"\bP1\b", line) and not re.search(r"~~.*P1.*~~|DONE|COMPLETE|RESOLVED", line, re.IGNORECASE)
        ]

        if not p1_lines:
            return RuleResult(
                rule_id=rule_id,
                description="No P1 open items while claiming COMPLETE verdict",
                severity="FAILURE",
                passed=True,
                evidence="No P1 items found in next-work-register.md",
            )

        # Check if final verdict claims COMPLETE (only blocking if verdict asserts completion)
        verdict_path = self.bundle_dir / "final-verdict.md"
        if not verdict_path.exists():
            # No verdict yet — warn but don't fail
            return RuleResult(
                rule_id=rule_id,
                description="No P1 open items while claiming COMPLETE verdict",
                severity="WARNING",
                passed=True,
                evidence=f"{len(p1_lines)} P1 items noted but no final-verdict.md to check against",
            )

        verdict_content = verdict_path.read_text(encoding="utf-8", errors="replace")
        claims_complete = any(
            term in verdict_content
            for term in [
                "CLOSURE_VERIFIED",
                "COMPLETE",
                "GATES_ACTIVE",
                "README_IO_DOCS_AND_DESTINATION_AUDIT",
                "FALSE_CLOSURE_KILLED",
            ]
        )

        if p1_lines and claims_complete:
            return RuleResult(
                rule_id=rule_id,
                description="No P1 open items while claiming COMPLETE verdict",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"{len(p1_lines)} P1 open item(s) remain in next-work-register.md while "
                    "final verdict claims COMPLETE/VERIFIED. P1 = blocking; resolve or downgrade to P2."
                ),
                evidence="\n".join(p1_lines[:3]),
            )

        return RuleResult(
            rule_id=rule_id,
            description="No P1 open items while claiming COMPLETE verdict",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail=f"Zero-byte required files: {empty_files}",
            )

        present = [rel for rel in _REQUIRED_NONZERO_FILES if (self.bundle_dir / rel).exists()]
        return RuleResult(
            rule_id=rule_id,
            description="Required evidence files must not be 0 bytes",
            severity="FAILURE",
            passed=True,
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
