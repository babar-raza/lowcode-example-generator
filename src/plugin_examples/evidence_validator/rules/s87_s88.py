"""Evidence validation rules — Sprint87to88Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)



class Sprint87to88Rules:
    """Rule mixin for evidence validation."""

    def _rule_commands_log_no_result_pending(self) -> RuleResult:
        """commands.log must not have lines ending with 'result pending'.

        Sprint 87 (S86-D1): Sprint 86 commands.log had entries like
        'RUN ECC — result pending' that were never updated with real exit codes.
        """
        rule_id = "commands_log_no_result_pending"
        description = "commands.log must not contain 'result pending' entries"

        log_path = self.bundle_dir / "commands.log"
        if not log_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="commands.log not found — rule not applicable",
            )

        content = log_path.read_text(encoding="utf-8", errors="replace")
        pending_lines = [
            line.strip() for line in content.splitlines()
            if re.search(r"result\s+pending", line, re.IGNORECASE)
        ]

        if pending_lines:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S86-D1: commands.log has {len(pending_lines)} line(s) with "
                    f"'result pending': {pending_lines[:3]}"
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="No 'result pending' entries found in commands.log",
        )

    def _rule_validation_result_not_placeholder(self) -> RuleResult:
        """Validation result applicable + diagnostic must equal total_rules.

        Sprint 87 (S86-D2): Sprint 86 had a placeholder validation result
        written before the real EV run completed.
        """
        rule_id = "validation_result_not_placeholder"
        description = "validation result applicable + diagnostic must equal total_rules"

        # Find the validation result file
        evidence_dir = self.bundle_dir / "evidence"
        if not evidence_dir.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="evidence/ directory not found — rule not applicable",
            )

        vr_files = list(evidence_dir.glob("*-final-validation-result.json"))
        if not vr_files:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="No *-final-validation-result.json found — rule not applicable",
            )

        for vr_path in vr_files:
            try:
                data = json.loads(vr_path.read_text(encoding="utf-8", errors="replace"))
            except (OSError, ValueError):
                continue
            applicable = data.get("applicable", 0)
            diagnostic = data.get("diagnostic", 0)
            total = data.get("total_rules", 0)
            if total > 100 and applicable + diagnostic != total:
                return RuleResult(
                    rule_id=rule_id, description=description,
                    severity="FAILURE", passed=False,
                    failure_detail=(
                        f"S86-D2: {vr_path.name} has applicable={applicable} + "
                        f"diagnostic={diagnostic} = {applicable + diagnostic} != "
                        f"total_rules={total}. Looks like a placeholder."
                    ),
                )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="Validation result applicable + diagnostic = total_rules",
        )

    def _rule_sha_chain_reconciled_in_manifest(self) -> RuleResult:
        """bundle-manifest.json source_sha must be a valid short SHA.

        Sprint 87 (S86-D3): Sprint 86 had SHA chain inconsistency between
        bundle-manifest.json and final-clean-proof.txt.
        """
        rule_id = "sha_chain_reconciled_in_manifest"
        description = "bundle-manifest.json source_sha must be a valid git short SHA"

        manifest_path = self.bundle_dir / "bundle-manifest.json"
        if not manifest_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="bundle-manifest.json not found — rule not applicable",
            )

        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse bundle-manifest.json — rule not applicable",
            )

        source_sha = data.get("source_sha", "")
        if not source_sha or source_sha in ("TBD", "TBD_AFTER_COMMIT", "PLACEHOLDER"):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S86-D3: bundle-manifest.json source_sha is '{source_sha}' "
                    f"which is not a valid SHA."
                ),
            )

        if not re.match(r"^[0-9a-f]{7,40}$", source_sha):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S86-D3: bundle-manifest.json source_sha='{source_sha}' "
                    f"does not match [0-9a-f]{{7,40}} pattern."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"source_sha='{source_sha}' is a valid SHA",
        )

    def _rule_approval_vars_consistent_naming(self) -> RuleResult:
        """final-verdict.md must use canonical approval variable names.

        Sprint 87 (S86-D4): Sprint 86 mixed PLUGIN_EXAMPLES_README_PUSH_APPROVAL
        and PLUGIN_EXAMPLES_MERGE_PR_APPROVAL without a deprecation note.
        """
        rule_id = "approval_vars_consistent_naming"
        description = "final-verdict.md must use consistent approval variable naming"

        verdict_path = self.bundle_dir / "final-verdict.md"
        if not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="final-verdict.md not found — rule not applicable",
            )

        content = verdict_path.read_text(encoding="utf-8", errors="replace")
        has_old = "PLUGIN_EXAMPLES_README_PUSH_APPROVAL" in content
        has_new = "PLUGIN_EXAMPLES_MERGE_PR_APPROVAL" in content
        has_deprecation = "deprecat" in content.lower() or "alias" in content.lower()

        if has_old and not has_deprecation:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S86-D4: final-verdict.md uses PLUGIN_EXAMPLES_README_PUSH_APPROVAL "
                    "without a deprecation note. Use PLUGIN_EXAMPLES_MERGE_PR_APPROVAL "
                    "or add a deprecation/alias note."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="Approval variable naming is consistent or properly documented",
        )

    def _rule_words_drift_status_consistent(self) -> RuleResult:
        """sprint-state.json and words-version-drift-current.json must agree on drift.

        Sprint 87 (S86-D5): Sprint 81 MEMORY claimed drift resolved but Sprint 86
        words-version-drift-current.json showed drift=true.
        """
        rule_id = "words_drift_status_consistent"
        description = "sprint-state.json and words drift file must agree on drift status"

        drift_path = self.bundle_dir / "version-drift" / "words-version-drift-current.json"
        if not drift_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="words-version-drift-current.json not found — rule not applicable",
            )

        try:
            drift_data = json.loads(drift_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse words drift file — rule not applicable",
            )

        drift_val = drift_data.get("drift", False)
        drift_type = drift_data.get("drift_type", "")

        # Only enforce when drift is boolean True AND drift_type is present
        if not isinstance(drift_val, bool) or not drift_val:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"drift={drift_val!r} — rule applies only to boolean true drift",
            )

        # If drift=true, drift_type must not be empty or "RESOLVED"
        if drift_type.upper() in ("RESOLVED", ""):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S86-D5: words-version-drift-current.json has drift=true but "
                    f"drift_type='{drift_type}'. If drift exists, drift_type must "
                    f"reflect the actual status (e.g., NEEDS_REPAIR_APPROVAL_BLOCKED)."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"Words drift status is consistent: drift={drift_val}, drift_type={drift_type}",
        )

    def _rule_final_clean_proof_has_diff_and_log(self) -> RuleResult:
        """final-clean-proof.txt must include diff and log sections.

        Sprint 87 (S86-D6): Sprint 86 final-clean-proof.txt only had git status
        but no diff or log output.
        """
        rule_id = "final_clean_proof_has_diff_and_log"
        description = "final-clean-proof.txt must include git diff and git log output"

        proof_dir = self.bundle_dir / "git"
        if not proof_dir.exists():
            proof_path = self.bundle_dir / "final-clean-proof.txt"
        else:
            proof_path = proof_dir / "final-clean-proof.txt"

        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="final-clean-proof.txt not found — rule not applicable",
            )

        content = proof_path.read_text(encoding="utf-8", errors="replace").lower()
        has_diff = "diff" in content or "no changes" in content or "nothing to commit" in content
        has_log = "log" in content or "commit" in content

        if not has_diff or not has_log:
            missing = []
            if not has_diff:
                missing.append("diff")
            if not has_log:
                missing.append("log")
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S86-D6: final-clean-proof.txt is missing {', '.join(missing)} "
                    f"section(s). Must include git diff and git log output."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="final-clean-proof.txt includes diff and log sections",
        )

    def _rule_next_family_discovery_not_just_relisting(self) -> RuleResult:
        """advancement/next-family-discovery.md must reference pipeline configs.

        Sprint 87 (S86-A1): Next-family discovery must come from actual repo configs
        (pipeline/configs/families/), not just re-listing the current 6 families.
        """
        rule_id = "next_family_discovery_not_just_relisting"
        description = "next-family discovery must reference pipeline configs, not re-list current families"

        discovery_path = self.bundle_dir / "advancement" / "next-family-discovery.md"
        if not discovery_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="advancement/next-family-discovery.md not found — rule not applicable",
            )

        content = discovery_path.read_text(encoding="utf-8", errors="replace")
        # Must reference pipeline configs
        has_config_ref = "pipeline/configs" in content or "configs/families" in content
        # Must mention at least one non-current family
        non_current = ["ocr", "psd", "html", "svg", "barcode", "imaging", "cad"]
        has_new_family = any(f in content.lower() for f in non_current)

        if not has_config_ref:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S86-A1: next-family-discovery.md does not reference "
                    "pipeline/configs/families/. Discovery must come from repo configs."
                ),
            )

        if not has_new_family:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S86-A1: next-family-discovery.md does not mention any "
                    "non-current family. Must identify candidates beyond the current 6."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="Next-family discovery references pipeline configs and identifies new candidates",
        )

    def _rule_baseline_freeze_not_avoiding_advancement(self) -> RuleResult:
        """If baseline frozen, advancement/ dir must have real content.

        Sprint 87 (S86-A2): Baseline freeze must not be used as an excuse to
        skip product advancement. If frozen, there must be real advancement work.
        """
        rule_id = "baseline_freeze_not_avoiding_advancement"
        description = "baseline freeze must not avoid real product advancement"

        freeze_path = self.bundle_dir / "baseline-freeze" / "publication-baseline-freeze.json"
        if not freeze_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="No baseline freeze — rule not applicable",
            )

        adv_dir = self.bundle_dir / "advancement"
        if not adv_dir.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S86-A2: baseline-freeze exists but advancement/ directory "
                    "is missing. Baseline freeze must not avoid product advancement."
                ),
            )

        adv_files = list(adv_dir.iterdir())
        if len(adv_files) < 2:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S86-A2: baseline-freeze exists but advancement/ has only "
                    f"{len(adv_files)} file(s). Must have substantial advancement work."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"advancement/ has {len(adv_files)} files — real advancement present",
        )

    # ------------------------------------------------------------------
    # Sprint 88 rules (S87 defect invariants)
    # ------------------------------------------------------------------

    def _rule_bundle_manifest_has_head_sha(self) -> RuleResult:
        """bundle-manifest.json must have head_sha when source_sha is present.

        Sprint 88 (S87-D1): Sprint 87 bundle-manifest.json had source_sha
        but no head_sha field, making SHA chain verification incomplete.
        """
        rule_id = "bundle_manifest_has_head_sha"
        description = "bundle-manifest.json must have head_sha field when source_sha present"

        manifest_path = self.bundle_dir / "bundle-manifest.json"
        if not manifest_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="bundle-manifest.json not found — rule not applicable",
            )

        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse bundle-manifest.json — rule not applicable",
            )

        source_sha = data.get("source_sha", "")
        if not source_sha or source_sha in ("TBD", "TBD_AFTER_COMMIT", "PLACEHOLDER"):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="source_sha not set — head_sha rule not applicable",
            )

        head_sha = data.get("head_sha", "")
        if not head_sha or not re.match(r"^[0-9a-f]{7,40}$", head_sha):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S87-D1: bundle-manifest.json has source_sha='{source_sha}' "
                    f"but head_sha='{head_sha}' is missing or invalid. "
                    f"Both fields are required for SHA chain verification."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"head_sha='{head_sha}' present alongside source_sha='{source_sha}'",
        )

    def _rule_publication_truth_matrix_present_when_publication_claimed(self) -> RuleResult:
        """If final-verdict mentions publication, truth matrix must exist.

        Sprint 88 (S87-D3): Sprint 87 final verdict mentioned publication
        but publication-truth-matrix-final.json was initially missing.
        """
        rule_id = "publication_truth_matrix_present_when_publication_claimed"
        description = "publication truth matrix must exist when verdict mentions publication"

        verdict_path = self.bundle_dir / "final-verdict.md"
        if not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="final-verdict.md not found — rule not applicable",
            )

        content = verdict_path.read_text(encoding="utf-8", errors="replace").lower()
        mentions_publication = "publication" in content or "publish" in content

        if not mentions_publication:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="final-verdict.md does not mention publication — rule not applicable",
            )

        ptm_path = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not ptm_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S87-D3: final-verdict.md mentions publication but "
                    "publication/publication-truth-matrix-final.json is missing."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="publication truth matrix present alongside publication verdict",
        )

    def _rule_next_family_candidate_matrix_has_real_checks(self) -> RuleResult:
        """next-family-candidate-matrix.json must have real API check evidence.

        Sprint 88 (S87-D6): Sprint 87 next-family discovery was documentation-only;
        Sprint 88 requires actual NuGet API checks with HTTP status codes.
        """
        rule_id = "next_family_candidate_matrix_has_real_checks"
        description = "next-family-candidate-matrix.json must have real API check evidence"

        matrix_path = self.bundle_dir / "next-family" / "next-family-candidate-matrix.json"
        if not matrix_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="next-family-candidate-matrix.json not found — rule not applicable",
            )

        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse candidate matrix — rule not applicable",
            )

        candidates = data.get("candidates", [])
        if not candidates:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="No candidates in matrix — rule not applicable",
            )

        # Each candidate must have classification and nuget_exists fields
        for c in candidates:
            if "classification" not in c or "nuget_exists" not in c:
                return RuleResult(
                    rule_id=rule_id, description=description,
                    severity="FAILURE", passed=False,
                    failure_detail=(
                        f"S87-D6: candidate '{c.get('family', '?')}' missing "
                        f"classification or nuget_exists field. Real API checks required."
                    ),
                )

        # Must have discovery_method field
        if "discovery_method" not in data:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S87-D6: next-family-candidate-matrix.json missing "
                    "discovery_method field. Must document how discovery was performed."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"Candidate matrix has {len(candidates)} candidates with real API check fields",
        )

    def _rule_implementation_summary_present_if_advancement(self) -> RuleResult:
        """If advancement/ has discovery, implementation/ must have summary.

        Sprint 88 (S87-D7): Sprint 87 had next-family discovery but no
        implementation summary documenting what was actually executed.
        """
        rule_id = "implementation_summary_present_if_advancement"
        description = "implementation/ must have summary when advancement/ has discovery"

        adv_dir = self.bundle_dir / "advancement"
        if not adv_dir.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="advancement/ not found — rule not applicable",
            )

        discovery_path = adv_dir / "next-family-discovery.md"
        if not discovery_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="No next-family-discovery.md in advancement/ — rule not applicable",
            )

        impl_dir = self.bundle_dir / "implementation"
        summary_path = impl_dir / "implementation-summary.md"
        if not impl_dir.exists() or not summary_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    "S87-D7: advancement/next-family-discovery.md exists but "
                    "implementation/implementation-summary.md is missing. "
                    "Discovery must be paired with implementation documentation."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="implementation-summary.md present alongside next-family discovery",
        )

    def _rule_discovery_blocked_candidates_have_blocker_detail(self) -> RuleResult:
        """Each BLOCKED candidate must have a specific blocker field.

        Sprint 88 (S87-D6b): Blocked candidates must document the exact
        external dependency that blocks them, not just a generic label.
        """
        rule_id = "discovery_blocked_candidates_have_blocker_detail"
        description = "BLOCKED candidates in candidate matrix must have blocker detail"

        matrix_path = self.bundle_dir / "next-family" / "next-family-candidate-matrix.json"
        if not matrix_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="next-family-candidate-matrix.json not found — rule not applicable",
            )

        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse candidate matrix — rule not applicable",
            )

        candidates = data.get("candidates", [])
        for c in candidates:
            classification = c.get("classification", "")
            if "BLOCKED" in classification.upper():
                blocker = c.get("blocker", "")
                if not blocker or len(blocker) < 10:
                    return RuleResult(
                        rule_id=rule_id, description=description,
                        severity="FAILURE", passed=False,
                        failure_detail=(
                            f"S87-D6b: candidate '{c.get('family', '?')}' has "
                            f"classification={classification} but blocker='{blocker}' "
                            f"is missing or too vague. Must have specific blocker detail."
                        ),
                    )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="All BLOCKED candidates have detailed blocker fields",
        )

    def _rule_version_drift_reconciliation_present_if_drift_active(self) -> RuleResult:
        """If words drift is active, closure-repair must have reconciliation.

        Sprint 88 (S87-D5b): When words version drift is documented as active,
        the sprint must include a reconciliation artifact showing what was checked.
        """
        rule_id = "version_drift_reconciliation_present_if_drift_active"
        description = "closure-repair must have drift reconciliation when words drift is active"

        drift_path = self.bundle_dir / "version-drift" / "words-version-drift-current.json"
        if not drift_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="words-version-drift-current.json not found — rule not applicable",
            )

        try:
            drift_data = json.loads(drift_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse words drift file — rule not applicable",
            )

        drift_val = drift_data.get("drift", False)
        drift_type = drift_data.get("drift_type", "")

        # Only enforce when drift is boolean True with a non-resolved drift_type
        # (consistent with Rule 131 which also gates on isinstance(drift_val, bool))
        if not isinstance(drift_val, bool) or not drift_val:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"drift={drift_val!r} — rule applies only to boolean true drift",
            )

        if isinstance(drift_type, str) and drift_type.upper() == "RESOLVED":
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"drift_type={drift_type!r} — drift resolved, no reconciliation needed",
            )

        recon_path = self.bundle_dir / "closure-repair" / "words-version-drift-reconciliation.json"
        if not recon_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S87-D5b: words drift is active (drift={drift_val}, "
                    f"drift_type={drift_type}) but closure-repair/"
                    f"words-version-drift-reconciliation.json is missing."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="Version drift reconciliation present for active Words drift",
        )

    # ------------------------------------------------------------------
    # Sprint 89 rules (S88 defect invariants)
    # ------------------------------------------------------------------
