"""Evidence validation rules — Sprint84to86Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)



class Sprint84to86Rules:
    """Rule mixin for evidence validation."""

    def _rule_pr_batching_strategy_present_if_pr_creation_attempted(self) -> RuleResult:
        """If pr-creation-ledger.json shows prs_created > 0, publication/pr-batching-strategy.md must exist.

        Sprint 84 validator hardening (S83-G1): prevents creating PRs without a documented
        batching strategy. Closes Sprint 83 caveat C1 (42-PR plan too noisy).
        """
        rule_id = "pr_batching_strategy_present_if_pr_creation_attempted"
        description = (
            "publication/pr-batching-strategy.md must exist if pr-creation-ledger.json "
            "shows prs_created > 0"
        )

        ledger_path = self.bundle_dir / "publication" / "pr-creation-ledger.json"
        if not ledger_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="publication/pr-creation-ledger.json not found — rule not applicable",
            )

        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse pr-creation-ledger.json — rule not applicable",
            )

        prs_created = ledger.get("prs_created", 0) if isinstance(ledger, dict) else 0
        if prs_created == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="pr-creation-ledger.json shows prs_created=0 — rule not applicable",
            )

        strategy_path = self.bundle_dir / "publication" / "pr-batching-strategy.md"
        if not strategy_path.exists() or strategy_path.stat().st_size == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S83-G1: pr-creation-ledger.json shows prs_created={prs_created} but "
                    f"publication/pr-batching-strategy.md is missing or empty. "
                    f"Document the PR batching strategy before creating PRs."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"prs_created={prs_created}; publication/pr-batching-strategy.md is present",
        )

    def _rule_pr_batching_plan_present_if_pr_creation_attempted(self) -> RuleResult:
        """If pr-creation-ledger.json shows prs_created > 0, publication/pr-batching-plan.json must exist.

        Sprint 84 validator hardening (S83-G2): pairs with S83-G1 to require both the
        strategy narrative and the structured plan JSON before PRs are created.
        """
        rule_id = "pr_batching_plan_present_if_pr_creation_attempted"
        description = (
            "publication/pr-batching-plan.json must exist if pr-creation-ledger.json "
            "shows prs_created > 0"
        )

        ledger_path = self.bundle_dir / "publication" / "pr-creation-ledger.json"
        if not ledger_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="publication/pr-creation-ledger.json not found — rule not applicable",
            )

        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse pr-creation-ledger.json — rule not applicable",
            )

        prs_created = ledger.get("prs_created", 0) if isinstance(ledger, dict) else 0
        if prs_created == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="pr-creation-ledger.json shows prs_created=0 — rule not applicable",
            )

        plan_path = self.bundle_dir / "publication" / "pr-batching-plan.json"
        if not plan_path.exists() or plan_path.stat().st_size == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S83-G2: pr-creation-ledger.json shows prs_created={prs_created} but "
                    f"publication/pr-batching-plan.json is missing or empty. "
                    f"Document the structured PR batching plan before creating PRs."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"prs_created={prs_created}; publication/pr-batching-plan.json is present",
        )

    def _rule_root_readme_file_plan_present_before_pr_creation(self) -> RuleResult:
        """If pr-creation-ledger.json shows prs_created > 0, conflicts/root-readme-file-plan.json must exist.

        Sprint 84 validator hardening (S83-G3): ensures that the per-family root README
        decision (include/exclude) is documented before any PRs are created.
        Closes Sprint 83 caveat C2 (root README ambiguity).
        """
        rule_id = "root_readme_file_plan_present_before_pr_creation"
        description = (
            "conflicts/root-readme-file-plan.json must exist if pr-creation-ledger.json "
            "shows prs_created > 0"
        )

        ledger_path = self.bundle_dir / "publication" / "pr-creation-ledger.json"
        if not ledger_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="publication/pr-creation-ledger.json not found — rule not applicable",
            )

        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse pr-creation-ledger.json — rule not applicable",
            )

        prs_created = ledger.get("prs_created", 0) if isinstance(ledger, dict) else 0
        if prs_created == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="pr-creation-ledger.json shows prs_created=0 — rule not applicable",
            )

        file_plan_path = self.bundle_dir / "conflicts" / "root-readme-file-plan.json"
        if not file_plan_path.exists() or file_plan_path.stat().st_size == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S83-G3: pr-creation-ledger.json shows prs_created={prs_created} but "
                    f"conflicts/root-readme-file-plan.json is missing or empty. "
                    f"Document per-family root README include/exclude decision before creating PRs."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"prs_created={prs_created}; conflicts/root-readme-file-plan.json is present",
        )

    def _rule_no_bulk_42pr_plan_without_justification(self) -> RuleResult:
        """If pr-batching-plan.json exists and planned_prs has 42 entries, bulk_justification must be present.

        Sprint 84 validator hardening (S83-G4): prevents the Sprint 83 S83-C1 pattern
        where 42 PRs were planned (one per example) without explicit justification.
        The default is 1 PR per family (6 PRs); creating 42 requires documented justification.
        """
        rule_id = "no_bulk_42pr_plan_without_justification"
        description = (
            "If pr-batching-plan.json has 42 planned_prs, "
            "bulk_justification field must be present"
        )

        plan_path = self.bundle_dir / "publication" / "pr-batching-plan.json"
        if not plan_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="publication/pr-batching-plan.json not found — rule not applicable",
            )

        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse pr-batching-plan.json — rule not applicable",
            )

        if not isinstance(plan, dict):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="pr-batching-plan.json is not a JSON object — rule not applicable",
            )

        planned_prs = plan.get("planned_prs", [])
        if not isinstance(planned_prs, list) or len(planned_prs) != 42:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"planned_prs count={len(planned_prs) if isinstance(planned_prs, list) else 'N/A'} (not 42) — rule not applicable",
            )

        # 42-PR plan detected — justification required
        justification = plan.get("bulk_justification")
        if not justification:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S83-G4: pr-batching-plan.json has 42 planned_prs (one per example) but "
                    "no bulk_justification field. The default is 1 PR per family (6 PRs). "
                    "Add bulk_justification to explain why 42 PRs are required."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"planned_prs=42; bulk_justification present: {str(justification)[:80]}",
        )

    # ------------------------------------------------------------------
    # Sprint 85: evidence hygiene rules (120-124)
    # ------------------------------------------------------------------

    def _rule_bundle_manifest_source_sha_not_tbd(self) -> RuleResult:
        """bundle-manifest.json source_sha must not be TBD_AFTER_COMMIT.

        Sprint 85 evidence hygiene (S84-H1): prevents the Sprint 84 pattern
        where source_sha was left as TBD_AFTER_COMMIT after the commit sequence.
        """
        rule_id = "bundle_manifest_source_sha_not_tbd"
        description = "bundle-manifest.json source_sha must not be TBD_AFTER_COMMIT"

        manifest_path = self.bundle_dir / "bundle-manifest.json"
        if not manifest_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="bundle-manifest.json not found — rule not applicable",
            )

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse bundle-manifest.json — rule not applicable",
            )

        source_sha = manifest.get("source_sha", "")
        if source_sha == "TBD_AFTER_COMMIT":
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S84-H1: bundle-manifest.json has source_sha=TBD_AFTER_COMMIT. "
                    "The source_sha must be updated to the actual commit SHA after committing."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"source_sha={source_sha!r} (not TBD)",
        )

    def _rule_no_stale_will_capture_text_in_final_consistency(self) -> RuleResult:
        """final-consistency-check.json notes must not contain 'will be captured'.

        Sprint 85 evidence hygiene (S84-H2): prevents the Sprint 84 pattern
        where the consistency check notes referenced future captures that had already occurred.
        """
        rule_id = "no_stale_will_capture_text_in_final_consistency"
        description = "final-consistency-check.json notes must not contain 'will be captured'"

        check_path = self.bundle_dir / "review" / "final-consistency-check.json"
        if not check_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="review/final-consistency-check.json not found — rule not applicable",
            )

        try:
            check = json.loads(check_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse final-consistency-check.json — rule not applicable",
            )

        notes = check.get("notes", "")
        if "will be captured" in notes.lower():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S84-H2: final-consistency-check.json notes contain 'will be captured'. "
                    "Update the notes after all captures are complete."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"notes do not contain 'will be captured'",
        )

    def _rule_no_stale_pending_lane_label_in_tracking(self) -> RuleResult:
        """taskcard-update-proof.md must not have lanes marked PENDING in lane status table.

        Sprint 85 evidence hygiene (S84-H3): prevents the Sprint 84 pattern
        where Lane J was left as PENDING after IV had completed.
        """
        rule_id = "no_stale_pending_lane_label_in_tracking"
        description = "taskcard-update-proof.md must not have lanes marked PENDING"

        taskcard_path = self.bundle_dir / "tracking" / "taskcard-update-proof.md"
        if not taskcard_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="tracking/taskcard-update-proof.md not found — rule not applicable",
            )

        content = taskcard_path.read_text(encoding="utf-8", errors="replace")
        import re
        # Match table rows like "| J | IV | PENDING ... |"
        pending_lines = re.findall(r"\|[^|]+\|[^|]+\|\s*PENDING\b[^|]*\|", content)
        if pending_lines:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S84-H3: taskcard-update-proof.md has {len(pending_lines)} lane(s) "
                    f"marked PENDING: {pending_lines[0].strip()!r}. Update to final status."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="No PENDING lane labels found in taskcard-update-proof.md",
        )

    def _rule_scoreboard_ev_applicable_not_tbd(self) -> RuleResult:
        """scoreboard-update-proof.md must not have TBD for EV applicable.

        Sprint 85 evidence hygiene (S84-H4): prevents the Sprint 84 pattern
        where the scoreboard was written before the EV run and left with TBD.
        """
        rule_id = "scoreboard_ev_applicable_not_tbd"
        description = "scoreboard-update-proof.md must not have TBD for EV applicable"

        scoreboard_path = self.bundle_dir / "tracking" / "scoreboard-update-proof.md"
        if not scoreboard_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="tracking/scoreboard-update-proof.md not found — rule not applicable",
            )

        content = scoreboard_path.read_text(encoding="utf-8", errors="replace")
        import re
        # Match rows with "EV applicable" and "TBD"
        if re.search(r"EV applicable[^|]*\|[^|]*\|\s*TBD", content, re.IGNORECASE):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S84-H4: scoreboard-update-proof.md has TBD for EV applicable. "
                    "Update with actual EV applicable count after running the validator."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="EV applicable is not TBD in scoreboard",
        )

    def _rule_bundle_manifest_source_sha_in_final_clean_proof(self) -> RuleResult:
        """When bundle-manifest.json source_sha is not TBD, it must appear in final-clean-proof.txt.

        Sprint 85 evidence hygiene (S84-H5): ensures SHA consistency between the
        bundle manifest and the git proof. Rule 120 catches TBD; this rule catches
        a non-TBD SHA that doesn't appear in the final clean proof.
        """
        rule_id = "bundle_manifest_source_sha_in_final_clean_proof"
        description = "bundle-manifest.json source_sha must appear in final-clean-proof.txt"

        manifest_path = self.bundle_dir / "bundle-manifest.json"
        proof_path = self.bundle_dir / "git" / "final-clean-proof.txt"

        if not manifest_path.exists() or not proof_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="bundle-manifest.json or final-clean-proof.txt not found — rule not applicable",
            )

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse bundle-manifest.json — rule not applicable",
            )

        source_sha = manifest.get("source_sha", "")
        if not source_sha or source_sha == "TBD_AFTER_COMMIT":
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"source_sha={source_sha!r} — rule 120 handles TBD, this rule not applicable",
            )

        proof_content = proof_path.read_text(encoding="utf-8", errors="replace")
        if source_sha not in proof_content:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S84-H5: bundle-manifest.json source_sha={source_sha!r} does not appear "
                    f"in final-clean-proof.txt. The proof must reference the bundle's commit SHA."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"source_sha={source_sha!r} found in final-clean-proof.txt",
        )

    # ------------------------------------------------------------------
    # Sprint 86: readiness-loop prevention rules (125-126)
    # ------------------------------------------------------------------

    def _rule_baseline_freeze_present_if_14_consecutive_blocked(self) -> RuleResult:
        """If sprints_approval_blocked >= 14, baseline-freeze must exist.

        Sprint 86 readiness-loop prevention (S85-I1): after 14 consecutive
        approval-blocked sprints, the pipeline must freeze the publication
        baseline rather than continuing readiness-only loops.
        """
        rule_id = "baseline_freeze_present_if_14_consecutive_blocked"
        description = "baseline-freeze/publication-baseline-freeze.json required after 14+ consecutive blocked sprints"

        state_path = self.bundle_dir / "sprint-state.json"
        if not state_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="sprint-state.json not found — rule not applicable",
            )

        try:
            state = json.loads(state_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse sprint-state.json — rule not applicable",
            )

        blocked_count = state.get("sprints_approval_blocked", 0)
        if blocked_count < 14:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"sprints_approval_blocked={blocked_count} (< 14) — freeze not required",
            )

        freeze_path = self.bundle_dir / "baseline-freeze" / "publication-baseline-freeze.json"
        if not freeze_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S85-I1: sprint-state.json shows sprints_approval_blocked={blocked_count} (>= 14) "
                    f"but baseline-freeze/publication-baseline-freeze.json does not exist. "
                    f"After 14 consecutive blocked sprints, the baseline must be frozen."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"sprints_approval_blocked={blocked_count}; baseline freeze file exists",
        )

    def _rule_no_readiness_only_verdict_after_baseline_freeze(self) -> RuleResult:
        """If baseline freeze exists, final verdict must not be a pure readiness-only pattern.

        Sprint 86 readiness-loop prevention (S85-I2): once the baseline is frozen,
        the sprint verdict must reflect the freeze (e.g., BASELINE_FROZEN) rather
        than repeating a generic BLOCKED_BY_APPROVAL readiness-only pattern.
        """
        rule_id = "no_readiness_only_verdict_after_baseline_freeze"
        description = "final verdict must not be readiness-only after baseline freeze"

        freeze_path = self.bundle_dir / "baseline-freeze" / "publication-baseline-freeze.json"
        if not freeze_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="No baseline freeze file — rule not applicable",
            )

        verdict_path = self.bundle_dir / "final-verdict.md"
        if not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="final-verdict.md not found — rule not applicable",
            )

        content = verdict_path.read_text(encoding="utf-8", errors="replace")
        # After a baseline freeze, verdict must acknowledge the freeze
        freeze_indicators = [
            "BASELINE_FROZEN",
            "FREEZE",
            "SAFE_LANES_ADVANCED",
            "FINISH_LINE",
        ]
        has_freeze_acknowledgment = any(ind in content.upper() for ind in freeze_indicators)

        if not has_freeze_acknowledgment:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S85-I2: baseline-freeze/publication-baseline-freeze.json exists but "
                    "final-verdict.md does not acknowledge the freeze. Verdict must contain "
                    "BASELINE_FROZEN, FREEZE, SAFE_LANES_ADVANCED, or FINISH_LINE."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="Baseline freeze acknowledged in final verdict",
        )

    # ------------------------------------------------------------------
    # Sprint 87: S86 defect invariant rules (127-134)
    # ------------------------------------------------------------------
