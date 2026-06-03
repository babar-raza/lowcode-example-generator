"""Evidence validation rules — Sprint89Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)



class Sprint89Rules:
    """Rule mixin for evidence validation."""

    def _rule_head_sha_matches_final_proof(self) -> RuleResult:
        """bundle-manifest.json head_sha must appear in final-clean-proof.txt.

        Sprint 89 (S88-D1): Sprint 88 had head_sha pointing to commit 1,
        but final-clean-proof.txt HEAD pointed to commit 2.
        """
        rule_id = "head_sha_matches_final_proof"
        description = "bundle-manifest.json head_sha must appear in final-clean-proof.txt"

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

        head_sha = data.get("head_sha", "")
        if not head_sha or not re.match(r"^[0-9a-f]{7,40}$", head_sha):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"head_sha='{head_sha}' not a valid SHA — rule not applicable",
            )

        proof_dir = self.bundle_dir / "git"
        proof_path = proof_dir / "final-clean-proof.txt" if proof_dir.exists() else self.bundle_dir / "final-clean-proof.txt"
        if not proof_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="final-clean-proof.txt not found — rule not applicable",
            )

        proof_content = proof_path.read_text(encoding="utf-8", errors="replace")
        # Check for short SHA (first 7 chars) or full SHA in proof
        short_sha = head_sha[:7]
        if head_sha in proof_content or short_sha in proof_content:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"head_sha '{short_sha}...' found in final-clean-proof.txt",
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=False,
            failure_detail=(
                f"S88-D1: bundle-manifest.json head_sha='{head_sha}' "
                f"does not appear in final-clean-proof.txt."
            ),
        )

    def _rule_active_validation_not_not_canonical(self) -> RuleResult:
        """Active *-final-validation-result.json must not have not_canonical=true.

        Sprint 89 (S88-D2): Sprint 88 had the active final validation file
        with overall_valid=false + not_canonical=true, creating ambiguity.
        """
        rule_id = "active_validation_not_not_canonical"
        description = "active final validation file must not have not_canonical=true"

        evidence_dir = self.bundle_dir / "evidence"
        if not evidence_dir.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="evidence/ directory not found — rule not applicable",
            )

        # Find *-final-validation-result.json files (not diagnostic)
        vr_files = [
            f for f in evidence_dir.iterdir()
            if f.name.endswith("-final-validation-result.json")
            and "diagnostic" not in f.name.lower()
        ]

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
            if data.get("not_canonical") is True:
                return RuleResult(
                    rule_id=rule_id, description=description,
                    severity="FAILURE", passed=False,
                    failure_detail=(
                        f"S88-D2: {vr_path.name} has not_canonical=true. "
                        f"Active final validation must be canonical."
                    ),
                )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="Active final validation file is canonical (no not_canonical=true)",
        )

    def _rule_source_proof_present_if_source_changed(self) -> RuleResult:
        """If ev_rules increased, source-diff.patch or source-proof/ must exist.

        Sprint 89 (S88-D3): Sprint 88 claimed 6 new EV rules but had no
        source proof (patch or diff) in the bundle.
        """
        rule_id = "source_proof_present_if_source_changed"
        description = "source-diff.patch must exist when EV rules are added"

        state_path = self.bundle_dir / "sprint-state.json"
        if not state_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="sprint-state.json not found — rule not applicable",
            )

        try:
            data = json.loads(state_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse sprint-state.json — rule not applicable",
            )

        new_rules = data.get("new_ev_rules_this_sprint", 0)
        if not isinstance(new_rules, int) or new_rules == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence=f"new_ev_rules_this_sprint={new_rules} — no source changes claimed",
            )

        # Check for source proof
        proof_paths = [
            self.bundle_dir / "source-diff.patch",
            self.bundle_dir / "source-proof" / "source-diff.patch",
            self.bundle_dir / "evidence" / "validator-source-proof.patch",
        ]
        has_proof = any(p.exists() and p.stat().st_size > 0 for p in proof_paths)

        if not has_proof:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"S88-D3: sprint-state.json claims new_ev_rules_this_sprint={new_rules} "
                    f"but no source-diff.patch or source proof found in bundle."
                ),
            )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=f"Source proof found for {new_rules} new EV rules",
        )

    def _rule_no_lowcode_confirmed_has_evidence(self) -> RuleResult:
        """NO_LOWCODE_CONFIRMED in candidate matrix requires scan evidence.

        Sprint 89 (S88-D5): When reclassifying a family from BLOCKED to
        NO_LOWCODE_CONFIRMED, scan evidence must exist.
        """
        rule_id = "no_lowcode_confirmed_has_evidence"
        description = "NO_LOWCODE_CONFIRMED candidates must have scan evidence"

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
            if c.get("classification") == "NO_LOWCODE_CONFIRMED":
                family = c.get("family", "unknown")
                # Must have discovery_method or lowcode_matches field
                has_evidence = (
                    "discovery_method" in c
                    or "lowcode_matches" in c
                    or c.get("lowcode_namespace_matches") is not None
                )
                if not has_evidence:
                    return RuleResult(
                        rule_id=rule_id, description=description,
                        severity="FAILURE", passed=False,
                        failure_detail=(
                            f"S88-D5: candidate '{family}' is NO_LOWCODE_CONFIRMED "
                            f"but has no discovery_method or scan match count."
                        ),
                    )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="All NO_LOWCODE_CONFIRMED candidates have scan evidence",
        )

    def _rule_candidate_classification_not_stale_after_scan(self) -> RuleResult:
        """If binary scan exists, candidates must not remain REFLECTION_BLOCKED.

        Sprint 89 (S88-D5b): Sprint 88 treated HTML/SVG as externally blocked
        when the issue was internal. If a scan result exists showing no LowCode,
        the classification must be updated.
        """
        rule_id = "candidate_classification_not_stale_after_scan"
        description = "candidates must not remain REFLECTION_BLOCKED if scan results exist"

        nf_dir = self.bundle_dir / "next-family"
        if not nf_dir.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="next-family/ directory not found — rule not applicable",
            )

        # Check for scan result files
        scan_files = [f for f in nf_dir.iterdir() if "reflection-result" in f.name]
        if not scan_files:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="No reflection-result files found — rule not applicable",
            )

        matrix_path = nf_dir / "next-family-candidate-matrix.json"
        if not matrix_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="No candidate matrix — rule not applicable",
            )

        try:
            data = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse candidate matrix — rule not applicable",
            )

        # Families with scan results
        scanned = set()
        for sf in scan_files:
            try:
                sd = json.loads(sf.read_text(encoding="utf-8", errors="replace"))
                scanned.add(sd.get("family", ""))
            except (OSError, ValueError):
                pass

        for c in data.get("candidates", []):
            family = c.get("family", "")
            classification = c.get("classification", "")
            if family in scanned and "REFLECTION_BLOCKED" in classification:
                return RuleResult(
                    rule_id=rule_id, description=description,
                    severity="FAILURE", passed=False,
                    failure_detail=(
                        f"S88-D5b: '{family}' has a scan result file but "
                        f"classification is still '{classification}'. "
                        f"Must update classification based on scan results."
                    ),
                )

        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence="No stale REFLECTION_BLOCKED classifications after scan",
        )

    def _rule_no_op_examples_eliminated(self) -> RuleResult:
        """If a no-op-detector-report exists and lists repaired examples,
        the per-example-output-proof must confirm still_no_op == 0.

        Multi-Mega-Train 20260530: 9 examples were repaired via template_first.
        This rule verifies the repair is complete (no remaining no-ops).
        """
        rule_id = "no_op_examples_eliminated"
        description = "no-op examples must be eliminated if detector report exists"

        semantic_dir = self.bundle_dir / "semantic"
        detector_path = semantic_dir / "no-op-detector-report.json"
        if not detector_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="no-op-detector-report.json not present — rule not applicable",
            )

        try:
            detector = json.loads(detector_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse no-op-detector-report.json — rule not applicable",
            )

        total_repaired = detector.get("total_repaired", 0)
        if total_repaired == 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Detector reports 0 repairs needed — no validation required",
            )

        # Repairs were needed; check the output-validation proof
        output_proof_path = self.bundle_dir / "output-validation" / "per-example-output-proof.json"
        if not output_proof_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Detector reports {total_repaired} repaired examples but "
                    f"output-validation/per-example-output-proof.json is missing. "
                    f"Output proof is required to confirm no-ops are eliminated."
                ),
            )

        try:
            proof = json.loads(output_proof_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail="Could not parse per-example-output-proof.json",
            )

        summary = proof.get("summary", {})
        still_no_op = summary.get("still_no_op", None)
        if still_no_op is None:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail="per-example-output-proof.json summary missing 'still_no_op' field",
            )

        if still_no_op != 0:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"still_no_op={still_no_op} in output proof — "
                    f"{still_no_op} no-op examples remain after repair attempt. "
                    f"All repaired examples must produce real API output."
                ),
            )

        real_output = summary.get("real_output_confirmed", 0)
        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=(
                f"still_no_op=0; {real_output}/{total_repaired} repaired examples "
                f"confirmed to produce real API output"
            ),
        )

    def _rule_all_six_family_packages_present(self) -> RuleResult:
        """All 6 publication families must have pr-dry-run packages.

        Multi-Mega-Train 20260530 (Lane F): diagram, slides, and email packages
        were missing and have been created. All 6 families are now required.
        """
        rule_id = "all_six_family_packages_present"
        description = "all 6 families must have pr-dry-run publication packages"

        # Check if publication package report exists
        pkg_report_path = self.bundle_dir / "publication" / "packages" / "package-completion-report.json"
        if not pkg_report_path.exists():
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="package-completion-report.json not present — rule not applicable",
            )

        try:
            report = json.loads(pkg_report_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=True,
                evidence="Could not parse package-completion-report.json — rule not applicable",
            )

        packages = report.get("packages", {})
        required_families = {"cells", "words", "pdf", "diagram", "slides", "email"}
        missing = required_families - set(packages.keys())
        if missing:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Package report missing families: {sorted(missing)}. "
                    f"All 6 families (cells, words, pdf, diagram, slides, email) "
                    f"must have publication packages."
                ),
            )

        # Check verdict field — must contain COMPLETE but not INCOMPLETE
        verdict = report.get("verdict", "")
        verdict_up = verdict.upper()
        if "COMPLETE" not in verdict_up or "INCOMPLETE" in verdict_up:
            return RuleResult(
                rule_id=rule_id, description=description,
                severity="FAILURE", passed=False,
                failure_detail=(
                    f"Package completion verdict is '{verdict}' — "
                    f"expected COMPLETE status. All families must have packages."
                ),
            )

        total = report.get("totals", {}).get("total_packaged_examples", 0)
        return RuleResult(
            rule_id=rule_id, description=description,
            severity="FAILURE", passed=True,
            evidence=(
                f"All 6 families present in package report; "
                f"{total} total packaged examples; verdict={verdict}"
            ),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
