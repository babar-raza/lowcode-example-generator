"""Evidence validation rules — Sprint78to83Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)



class Sprint78to83Rules:
    """Rule mixin for evidence validation."""

    def _rule_publication_truth_no_stale_remote_claimed(self) -> RuleResult:
        """publication-truth-matrix-final.json with all_published=true must not list REMOTE_STALE status (S77-D1).

        If all examples are confirmed published (all_merged=true, all_published=true),
        then no family entry should claim REMOTE_STALE — that would be a contradiction.
        This rule catches the stub error where commands.log predicted REMOTE_STALE
        but the actual truth matrix shows all examples PUBLISHED.
        """
        rule_id = "publication_truth_no_stale_remote_claimed"
        ptm_path = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"

        if not ptm_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication truth matrix must not claim REMOTE_STALE when all_published=true",
                severity="FAILURE", passed=True,
                evidence="publication-truth-matrix-final.json not found — rule not applicable",
            )

        try:
            data = json.loads(ptm_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id,
                description="publication truth matrix must not claim REMOTE_STALE when all_published=true",
                severity="FAILURE", passed=True,
                evidence="Could not parse publication-truth-matrix-final.json — skipping",
            )

        # Handle both flat-array format (Sprint 82+) and wrapped-object format
        if isinstance(data, list):
            return RuleResult(
                rule_id=rule_id,
                description="publication truth matrix must not claim REMOTE_STALE when all_published=true",
                severity="FAILURE", passed=True,
                evidence="publication-truth-matrix-final.json is flat-array format — rule not applicable",
            )

        all_published = data.get("all_published", False)
        all_merged = data.get("all_merged", False)
        if not (all_published and all_merged):
            return RuleResult(
                rule_id=rule_id,
                description="publication truth matrix must not claim REMOTE_STALE when all_published=true",
                severity="FAILURE", passed=True,
                evidence="all_published=False or all_merged=False — rule not applicable",
            )

        families = data.get("families", {})
        stale_families = []
        for family_name, fdata in families.items():
            if isinstance(fdata, dict):
                status = fdata.get("status", "")
                if "REMOTE_STALE" in str(status):
                    stale_families.append(f"{family_name}={status}")

        if stale_families:
            return RuleResult(
                rule_id=rule_id,
                description="publication truth matrix must not claim REMOTE_STALE when all_published=true",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"publication-truth-matrix-final.json has all_published=true but "
                    f"{len(stale_families)} family/families claim REMOTE_STALE: {stale_families}. "
                    f"Update family status entries to reflect actual published state."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="publication truth matrix must not claim REMOTE_STALE when all_published=true",
            severity="FAILURE", passed=True,
            evidence=f"all_published=true and no REMOTE_STALE status entries found",
        )

    def _rule_handoff_validation_result_has_valid_flag(self) -> RuleResult:
        """handoff/handoff-prepublish-validation.json must exist and assert overall_handoff_valid=true (S77-D2).

        A missing or false overall_handoff_valid flag means the handoff step was either
        skipped or found a blocking issue — both require explicit documentation.
        """
        rule_id = "handoff_validation_result_has_valid_flag"
        handoff_path = self.bundle_dir / "handoff" / "handoff-prepublish-validation.json"

        if not handoff_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="handoff-prepublish-validation.json must assert overall_handoff_valid=true",
                severity="FAILURE", passed=True,
                evidence="handoff-prepublish-validation.json not found — rule not applicable",
            )

        try:
            data = json.loads(handoff_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id,
                description="handoff-prepublish-validation.json must assert overall_handoff_valid=true",
                severity="FAILURE", passed=False,
                failure_detail="handoff-prepublish-validation.json exists but is not valid JSON",
            )

        overall_handoff_valid = data.get("overall_handoff_valid")
        if overall_handoff_valid is None:
            return RuleResult(
                rule_id=rule_id,
                description="handoff-prepublish-validation.json must assert overall_handoff_valid=true",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "handoff-prepublish-validation.json is missing 'overall_handoff_valid' field. "
                    "Add overall_handoff_valid: true (or document why false)."
                ),
            )
        if overall_handoff_valid is not True:
            return RuleResult(
                rule_id=rule_id,
                description="handoff-prepublish-validation.json must assert overall_handoff_valid=true",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"handoff-prepublish-validation.json has overall_handoff_valid={overall_handoff_valid!r}. "
                    f"Must be true to proceed."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="handoff-prepublish-validation.json must assert overall_handoff_valid=true",
            severity="FAILURE", passed=True,
            evidence="overall_handoff_valid=true confirmed",
        )

    def _rule_remote_repo_state_all_accessible(self) -> RuleResult:
        """remote/remote-repo-state-before.json must exist and show all repos accessible (S77-D3).

        If any repos are inaccessible, publication cannot proceed and must be
        explicitly documented. Accessible == total_checked ensures no silent access failures.
        """
        rule_id = "remote_repo_state_all_accessible"
        remote_path = self.bundle_dir / "remote" / "remote-repo-state-before.json"

        if not remote_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote-repo-state-before.json must exist and show all repos accessible",
                severity="FAILURE", passed=True,
                evidence="remote-repo-state-before.json not found — rule not applicable",
            )

        try:
            data = json.loads(remote_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id,
                description="remote-repo-state-before.json must exist and show all repos accessible",
                severity="FAILURE", passed=False,
                failure_detail="remote-repo-state-before.json exists but is not valid JSON",
            )

        summary = data.get("summary", {})
        total_checked = summary.get("total_checked", 0)
        accessible = summary.get("accessible", 0)

        if total_checked == 0:
            return RuleResult(
                rule_id=rule_id,
                description="remote-repo-state-before.json must exist and show all repos accessible",
                severity="FAILURE", passed=False,
                failure_detail="remote-repo-state-before.json has total_checked=0 — no repos were checked",
            )

        if accessible < total_checked:
            blocked = summary.get("blocked_families", [])
            return RuleResult(
                rule_id=rule_id,
                description="remote-repo-state-before.json must exist and show all repos accessible",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"remote-repo-state-before.json shows {accessible}/{total_checked} accessible. "
                    f"Blocked: {blocked}. Publication requires all repos accessible."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="remote-repo-state-before.json must exist and show all repos accessible",
            severity="FAILURE", passed=True,
            evidence=f"All {accessible}/{total_checked} repos accessible",
        )

    # Sprint 79 NEW rules: close S78-E1 and S78-E2

    def _rule_ecc_closure_valid_only_if_no_blocking_failures(self) -> RuleResult:
        """evidence-contract-computed.json closure_valid=true is a lie if blocking_failures>0 (S78-E1).

        Sprint 78 defect: the bootstrapped ECC had closure_valid=true AND blocking_failures=1.
        These two fields are contradictory — the real ECC computer sets
        closure_valid = (blocking_failures == 0). Any hand-crafted override is invalid.
        """
        rule_id = "ecc_closure_valid_only_if_no_blocking_failures"
        ecc_path = self.bundle_dir / "evidence" / "evidence-contract-computed.json"

        if not ecc_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="ECC closure_valid=true is invalid when blocking_failures>0",
                severity="FAILURE", passed=True,
                evidence="evidence-contract-computed.json not found — rule not applicable",
            )

        try:
            data = json.loads(ecc_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id,
                description="ECC closure_valid=true is invalid when blocking_failures>0",
                severity="FAILURE", passed=False,
                failure_detail="evidence-contract-computed.json exists but is not valid JSON",
            )

        closure_valid = data.get("closure_valid", False)
        blocking_failures = data.get("blocking_failures", 0)

        if closure_valid and blocking_failures > 0:
            return RuleResult(
                rule_id=rule_id,
                description="ECC closure_valid=true is invalid when blocking_failures>0",
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"evidence-contract-computed.json has closure_valid=true "
                    f"but blocking_failures={blocking_failures}. "
                    "These are contradictory — closure_valid must be false when any blocking "
                    "category is MISSING/ZERO_BYTES/SEMANTIC_FAILED. "
                    "S78-E1: do not hand-craft closure_valid=true over a non-zero blocking count."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="ECC closure_valid=true is invalid when blocking_failures>0",
            severity="FAILURE", passed=True,
            evidence=(
                f"ECC consistent: closure_valid={closure_valid}, "
                f"blocking_failures={blocking_failures}"
            ),
        )

    def _rule_diagnostic_bundle_file_has_nonblocking_label(self) -> RuleResult:
        """Any *-bundle-validation-result.json with overall_valid=false must have
        diagnostic_rules_are_non_blocking=true (S78-E2).

        Sprint 78 defect: sprint78-bundle-validation-result.json showed overall_valid=false
        with 55 failing rules, confusing independent reviewers who could not distinguish
        diagnostic/non-applicable failures from real blocking failures.

        Every bundle-validation-result file that is diagnostic (FINISH_LINE_SPRINT,
        REPAIR_BUNDLE, etc.) must explicitly declare diagnostic_rules_are_non_blocking=true
        so future agents cannot confuse non-applicable failures with real closure blockers.
        """
        rule_id = "diagnostic_bundle_file_has_nonblocking_label"
        evidence_dir = self.bundle_dir / "evidence"

        if not evidence_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Diagnostic bundle files must have diagnostic_rules_are_non_blocking=true",
                severity="FAILURE", passed=True,
                evidence="evidence/ directory not found — rule not applicable",
            )

        bundle_files = list(evidence_dir.glob("*-bundle-validation-result.json"))
        if not bundle_files:
            return RuleResult(
                rule_id=rule_id,
                description="Diagnostic bundle files must have diagnostic_rules_are_non_blocking=true",
                severity="FAILURE", passed=True,
                evidence="No *-bundle-validation-result.json files found — rule not applicable",
            )

        offenders = []
        for bf in bundle_files:
            try:
                data = json.loads(bf.read_text(encoding="utf-8", errors="replace"))
            except (OSError, ValueError):
                offenders.append(f"{bf.name}: not valid JSON")
                continue
            overall_valid = data.get("overall_valid", True)
            if not overall_valid:
                has_label = data.get("diagnostic_rules_are_non_blocking", False)
                if not has_label:
                    offenders.append(
                        f"{bf.name}: overall_valid=false but diagnostic_rules_are_non_blocking "
                        "is missing or false"
                    )

        if offenders:
            return RuleResult(
                rule_id=rule_id,
                description="Diagnostic bundle files must have diagnostic_rules_are_non_blocking=true",
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S78-E2: bundle-validation-result file(s) with overall_valid=false are "
                    f"missing the diagnostic label: {'; '.join(offenders)}"
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Diagnostic bundle files must have diagnostic_rules_are_non_blocking=true",
            severity="FAILURE", passed=True,
            evidence=(
                f"All {len(bundle_files)} bundle-validation-result file(s) are correctly "
                "labeled (overall_valid=true or diagnostic_rules_are_non_blocking=true)"
            ),
        )

    def _rule_no_active_validation_file_with_ambiguous_false(self) -> RuleResult:
        """evidence/*-validation-result.json files must not have overall_valid=false
        without not_canonical=true (S79-B1).

        Sprint 79 defect: sprint79-final-validation-result.json had overall_valid=false
        while claiming canonical_overall_valid=true. Future agents cannot reliably
        distinguish this from a genuine validation failure.
        Any final-looking validation result with overall_valid=false must declare
        not_canonical=true to prevent misinterpretation.
        """
        rule_id = "no_active_validation_file_with_ambiguous_false"
        description = "No active validation file may have overall_valid=false without not_canonical=true"
        evidence_dir = self.bundle_dir / "evidence"

        if not evidence_dir.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="evidence/ directory not found — rule not applicable",
            )

        offenders = []
        for f in sorted(evidence_dir.glob("*-validation-result.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except (OSError, ValueError):
                continue
            if data.get("overall_valid") is False and not data.get("not_canonical"):
                offenders.append(f.name)

        if offenders:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S79-B1: *-validation-result.json file(s) with overall_valid=false "
                    f"lack not_canonical=true: {'; '.join(offenders)}. "
                    "Either remove overall_valid=false (if applicable rules all pass) "
                    "or add not_canonical=true to mark as diagnostic-only."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"All *-validation-result.json files in evidence/ have unambiguous overall_valid",
        )

    def _rule_publication_truth_matrix_has_expected_count(self) -> RuleResult:
        """publication/publication-truth-matrix-final.json must have exactly 42 records
        with correct per-family counts: cells=9, words=8, pdf=19, diagram=2, email=1, slides=3.

        Sprint 83 validator hardening (S82-F1): prevents silent denomination drift where a
        publication matrix quietly loses records without a blocking validation failure.
        """
        rule_id = "publication_truth_matrix_has_expected_count"
        description = "Publication truth matrix must have 42 records with correct per-family counts"

        matrix_path = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not matrix_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="publication/publication-truth-matrix-final.json not found — rule not applicable",
            )

        try:
            records = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=f"S82-F1: Could not parse publication-truth-matrix-final.json: {exc}",
            )

        if not isinstance(records, list):
            # Legacy/wrapped format: {"total": N, "records": [...]} — not applicable
            # This rule specifically targets the Sprint 82+ flat-array format
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=(
                    "publication-truth-matrix-final.json uses wrapped object format — "
                    "rule only applies to Sprint 82+ flat-array format"
                ),
            )

        total = len(records)
        if total != 42:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S82-F1: Expected 42 records in publication-truth-matrix-final.json, "
                    f"got {total}. Denominator drift detected."
                ),
            )

        expected_family_counts = {
            "cells": 9, "words": 8, "pdf": 19,
            "diagram": 2, "email": 1, "slides": 3,
        }
        actual_counts: dict[str, int] = {}
        for rec in records:
            fam = rec.get("family", "unknown") if isinstance(rec, dict) else "unknown"
            actual_counts[fam] = actual_counts.get(fam, 0) + 1

        mismatches = []
        for fam, expected in expected_family_counts.items():
            actual = actual_counts.get(fam, 0)
            if actual != expected:
                mismatches.append(f"{fam}: expected {expected}, got {actual}")

        if mismatches:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S82-F1: Family count mismatch in publication-truth-matrix-final.json: "
                    + "; ".join(mismatches)
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=(
                f"publication-truth-matrix-final.json has {total} records with correct "
                f"per-family counts: cells=9, words=8, pdf=19, diagram=2, email=1, slides=3"
            ),
        )

    def _rule_root_readme_conflict_strategy_documented(self) -> RuleResult:
        """If remote/remote-repo-state-before.json shows any open PRs, a conflict strategy
        document must exist: remote/remote-conflict-check.md or
        conflicts/root-readme-pr-conflict-strategy.md.

        Sprint 83 validator hardening (S82-F2): prevents Sprint 82 pattern where root README
        PR conflicts were detected but the resolution strategy was not formally documented
        in a durable conflict strategy file.
        """
        rule_id = "root_readme_conflict_strategy_documented"
        description = "Root README conflict strategy must be documented when open PRs are detected"

        remote_state_path = self.bundle_dir / "remote" / "remote-repo-state-before.json"
        if not remote_state_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="remote/remote-repo-state-before.json not found — rule not applicable",
            )

        try:
            state = json.loads(remote_state_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse remote-repo-state-before.json — rule not applicable",
            )

        if not isinstance(state, dict):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="remote-repo-state-before.json is not a dict — rule not applicable",
            )

        # Check if any family has open PRs
        families_with_open_prs = []
        for family, data in state.items():
            if isinstance(data, dict) and data.get("open_prs"):
                families_with_open_prs.append(family)

        if not families_with_open_prs:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="No open PRs detected in remote-repo-state-before.json — rule not applicable",
            )

        # Open PRs found — require conflict strategy document
        conflict_check = self.bundle_dir / "remote" / "remote-conflict-check.md"
        conflict_strategy = self.bundle_dir / "conflicts" / "root-readme-pr-conflict-strategy.md"

        if conflict_check.exists() and conflict_check.stat().st_size > 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=(
                    f"Conflict strategy documented in remote/remote-conflict-check.md "
                    f"(open PRs in: {', '.join(families_with_open_prs)})"
                ),
            )

        if conflict_strategy.exists() and conflict_strategy.stat().st_size > 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=(
                    f"Conflict strategy documented in conflicts/root-readme-pr-conflict-strategy.md "
                    f"(open PRs in: {', '.join(families_with_open_prs)})"
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=False,
            failure_detail=(
                f"S82-F2: Open PRs detected in {', '.join(families_with_open_prs)} but no conflict "
                f"strategy document found. Expected remote/remote-conflict-check.md or "
                f"conflicts/root-readme-pr-conflict-strategy.md to be non-empty."
            ),
        )

    def _rule_final_consistency_check_not_stale_after_commit(self) -> RuleResult:
        """review/final-consistency-check.json must not have overall=PASS_PENDING_COMMIT
        if git/final-clean-proof.txt contains a real commit SHA (40 hex chars).

        Sprint 83 validator hardening (S82-F3): Sprint 82's final-consistency-check.json
        retained PASS_PENDING_COMMIT after the bundle commit was made and final-clean-proof.txt
        had the real SHA. This rule catches that stale label pattern.
        """
        rule_id = "final_consistency_check_not_stale_after_commit"
        description = (
            "final-consistency-check.json must not say PASS_PENDING_COMMIT "
            "after final-clean-proof.txt has a real commit SHA"
        )

        consistency_path = self.bundle_dir / "review" / "final-consistency-check.json"
        proof_path = self.bundle_dir / "git" / "final-clean-proof.txt"

        if not consistency_path.exists() or not proof_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="final-consistency-check.json or final-clean-proof.txt not found — rule not applicable",
            )

        try:
            consistency = json.loads(consistency_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse final-consistency-check.json — rule not applicable",
            )

        if consistency.get("overall") != "PASS_PENDING_COMMIT":
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=(
                    f"final-consistency-check.json overall={consistency.get('overall')!r} — "
                    f"not PASS_PENDING_COMMIT, no stale label"
                ),
            )

        # overall IS PASS_PENDING_COMMIT — check if proof has a real SHA
        try:
            proof_text = proof_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not read final-clean-proof.txt — rule not applicable",
            )

        # A real commit SHA: 40 hex chars as a standalone token
        sha_pattern = re.compile(r"\b[0-9a-f]{40}\b")
        if not sha_pattern.search(proof_text):
            # No real SHA in proof yet — PASS_PENDING_COMMIT is legitimate
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="final-clean-proof.txt has no 40-char SHA — PASS_PENDING_COMMIT is acceptable",
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=False,
            failure_detail=(
                "S82-F3: final-consistency-check.json has stale overall=PASS_PENDING_COMMIT "
                "but final-clean-proof.txt already contains a real 40-char commit SHA. "
                "Update final-consistency-check.json overall to PASS (or the appropriate "
                "final status) after committing the bundle."
            ),
        )

    def _rule_publication_file_plan_present_if_pr_creation_claimed(self) -> RuleResult:
        """If any record in publication/publication-truth-matrix-final.json has pr_url non-null,
        then publication/publication-file-plan.json must exist.

        Sprint 83 validator hardening (S82-F4): prevents PR creation being claimed in the
        publication matrix without the corresponding file plan that documents which files
        were touched in each PR.
        """
        rule_id = "publication_file_plan_present_if_pr_creation_claimed"
        description = (
            "publication-file-plan.json must exist if any pr_url is non-null "
            "in publication-truth-matrix-final.json"
        )

        matrix_path = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not matrix_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="publication/publication-truth-matrix-final.json not found — rule not applicable",
            )

        try:
            records = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse publication-truth-matrix-final.json — rule not applicable",
            )

        if not isinstance(records, list):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="publication-truth-matrix-final.json is not a JSON array — rule not applicable",
            )

        pr_urls = [
            rec.get("pr_url") for rec in records
            if isinstance(rec, dict) and rec.get("pr_url") is not None
        ]

        if not pr_urls:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="All pr_url values are null in publication-truth-matrix-final.json — rule not applicable",
            )

        # At least one PR URL claimed — file plan must exist
        file_plan_path = self.bundle_dir / "publication" / "publication-file-plan.json"
        if not file_plan_path.exists() or file_plan_path.stat().st_size == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S82-F4: {len(pr_urls)} record(s) in publication-truth-matrix-final.json "
                    f"have non-null pr_url but publication/publication-file-plan.json is missing "
                    f"or empty. File plan must exist before PRs are created."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=(
                f"{len(pr_urls)} record(s) have pr_url set; "
                f"publication/publication-file-plan.json is present and non-empty"
            ),
        )
