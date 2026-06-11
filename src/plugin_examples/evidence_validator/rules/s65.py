"""Evidence validation rules — ContentAuditRules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)


class ContentAuditRules:
    """Rule mixin for evidence validation."""

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
                    severity="FAILURE",
                    passed=False,
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
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"{fname}: records missing required fields: {details}",
                )

            return RuleResult(
                rule_id=rule_id,
                description="Content audit final must have required fields per record",
                severity="FAILURE",
                passed=True,
                evidence=f"{fname}: {len(records)} records, all required fields present",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit final must have required fields per record",
            severity="FAILURE",
            passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail="No destination content audit file found",
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit count fields must not contradict each other",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read audit: {exc}",
            )

        records = data.get("records", data.get("examples", []))
        total_claimed = data.get("total_publication_artifacts", None)
        std = data.get("standard_package_artifacts", None)
        special = data.get("special_case_artifacts", None)

        contradictions = []
        if total_claimed is not None and len(records) != total_claimed:
            contradictions.append(f"total_publication_artifacts={total_claimed} but len(records)={len(records)}")
        if std is not None and special is not None and total_claimed is not None:
            if std + special != total_claimed:
                contradictions.append(
                    f"standard({std}) + special({special}) = {std + special} != total({total_claimed})"
                )

        if contradictions:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit count fields must not contradict each other",
                severity="FAILURE",
                passed=False,
                failure_detail="; ".join(contradictions),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit count fields must not contradict each other",
            severity="FAILURE",
            passed=True,
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
                severity="WARNING",
                passed=True,
                evidence="destination/content-audit-final.json not found (older sprint format)",
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit final must show all 42 records READY",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read content-audit-final.json: {exc}",
            )

        records = data.get("records", [])
        not_ready = [
            r.get("scenario_id", "?")
            for r in records
            if r.get("final_readiness") not in ("READY", "SPECIAL_CASE_READY")
        ]
        records_ready = data.get("records_ready", len(records) - len(not_ready))

        if not_ready:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit final must show all 42 records READY",
                severity="FAILURE",
                passed=False,
                failure_detail=f"{len(not_ready)} records not READY: {not_ready[:5]}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit final must show all 42 records READY",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail="root-readme/per-family/ directory not found",
            )

        missing = [f for f in _FAMILIES if not (root_readme_dir / f"{f}-root-readme.md").exists()]
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="Root README artifacts must exist for all 6 families",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Missing root README artifacts for: {missing}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Root README artifacts must exist for all 6 families",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read special-case-publication-map.json: {exc}",
            )

        cases = data.get("special_cases", [])
        if len(cases) < 2:
            return RuleResult(
                rule_id=rule_id,
                description="Special-case publication map must document both PDF special cases",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"Only {len(cases)} special cases documented " "(expected 2: pdfa-converter, text-extractor)"
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Special-case publication map must document both PDF special cases",
            severity="FAILURE",
            passed=True,
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
                    1
                    for f in families.values()
                    if isinstance(f, dict) and not f.get("version_match") and f.get("policy") not in _ALLOWED_POLICIES
                )

            if unresolved > 0:
                return RuleResult(
                    rule_id=rule_id,
                    description="Version policy must show 0 unresolved drift families",
                    severity="FAILURE",
                    passed=False,
                    failure_detail=f"{rel}: total_drift_unresolved={unresolved}",
                )

            return RuleResult(
                rule_id=rule_id,
                description="Version policy must show 0 unresolved drift families",
                severity="FAILURE",
                passed=True,
                evidence=f"{rel}: total_drift_unresolved=0",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Version policy must show 0 unresolved drift families",
            severity="WARNING",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail="final-verdict.md not found",
            )

        verdict = verdict_path.read_text(encoding="utf-8", errors="replace")
        publication_claim_keywords = [
            "PUBLICATION_VERIFIED",
            "FULLY_PUBLISHED",
            "ALL_PUBLISHED",
            "LIVE_PUBLICATION_COMPLETE",
        ]
        claims_publication = any(kw in verdict for kw in publication_claim_keywords)

        if not claims_publication:
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim publication without proof",
                severity="FAILURE",
                passed=True,
                evidence="Verdict does not contain strong publication completion keywords",
            )

        remote_proof = self.bundle_dir / "publication" / "remote-proof-index.json"
        if not remote_proof.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim publication without proof",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "Verdict contains publication completion keyword but "
                    "publication/remote-proof-index.json is missing. "
                    "Must include remote proof artifact (PR URLs, merge SHAs) in bundle."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Final verdict must not overclaim publication without proof",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail="final-verdict.md not found",
            )

        verdict = verdict_path.read_text(encoding="utf-8", errors="replace")
        broad_pub_keywords = [
            "PUBLISHED",
            "HANDOFF",
            "PUBLICATION",
            "REMOTE_PROOF",
            "PR_MERGED",
            "DRY_RUN",
            "APPROVAL_BLOCKED",
        ]
        mentions_publication = any(kw in verdict for kw in broad_pub_keywords)
        remote_proof = self.bundle_dir / "publication" / "remote-proof-index.json"

        if mentions_publication and not remote_proof.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof index must exist if publication is mentioned",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "final-verdict.md mentions publication/PR activity but "
                    "publication/remote-proof-index.json is absent. "
                    "S64-D1: publication evidence must be bundled."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote proof index must exist if publication is mentioned",
            severity="FAILURE",
            passed=True,
            evidence=(
                f"verdict_mentions_publication={mentions_publication}, " f"remote_proof_present={remote_proof.exists()}"
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
                severity="WARNING",
                passed=True,
                evidence="destination/content-audit-final.json not found (older sprint format)",
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit must show >=40/42 README I/O coverage",
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"Only {io_doc_count}/{total} records have readme_status=IO_DOC "
                    f"(threshold={threshold}). README corrections may not have been applied."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit must show >=40/42 README I/O coverage",
            severity="FAILURE",
            passed=True,
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
                severity="WARNING",
                passed=True,
                evidence="evidence/ directory not found (older sprint format)",
            )

        candidates = sorted(evidence_dir.glob("*revalidation*.json"))
        if not candidates:
            return RuleResult(
                rule_id=rule_id,
                description="Prior sprint revalidation must show overall_valid=false",
                severity="WARNING",
                passed=True,
                evidence="No *revalidation*.json found (not required for older sprints)",
            )

        revalidation_path = candidates[-1]
        try:
            data = json.loads(revalidation_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Prior sprint revalidation must show overall_valid=false",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read {revalidation_path.name}: {exc}",
            )

        overall_valid = data.get("overall_valid", True)
        if overall_valid:
            sprint_id = data.get("sprint_id", "?")
            return RuleResult(
                rule_id=rule_id,
                description="Prior sprint revalidation must show overall_valid=false",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"{revalidation_path.name}: overall_valid=true — new semantic rules "
                    f"did not detect defects in prior sprint ({sprint_id}). "
                    "Rules may be too weak. Revalidation must fail."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Prior sprint revalidation must show overall_valid=false",
            severity="FAILURE",
            passed=True,
            evidence=f"{revalidation_path.name}: overall_valid=false (prior sprint correctly flagged)",
        )

    # ------------------------------------------------------------------
    # Sprint 66 rules: close S65-D1 through S65-D5
    # ------------------------------------------------------------------
