"""Evidence validation rules — Sprint76to77Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)



class Sprint76to77Rules:
    """Rule mixin for evidence validation."""

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
    # Sprint 78 NEW rules: close S77-D1 through S77-D3
    # ------------------------------------------------------------------
