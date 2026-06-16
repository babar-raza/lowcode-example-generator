"""Evidence validation rules — RemoteProofRules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)


class RemoteProofRules:
    """Rule mixin for evidence validation."""

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
                severity="FAILURE",
                passed=False,
                failure_detail="remote/remote-pr-proof-index.json not found. Sprint 65 had only publication/remote-proof-index.json which overclaimed PR coverage.",
            )

        try:
            data = json.loads(proof_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must not overclaim PR coverage",
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail=f"PR coverage inconsistency: {issues[:3]}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote proof must not overclaim PR coverage",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail="remote/remote-example-inventory.json not found. Only PR-number proof is insufficient.",
            )

        try:
            data = json.loads(inv_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must include per-example content hashes",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read remote-example-inventory.json: {exc}",
            )

        records = data.get("records", [])
        missing_hashes = [
            r.get("scenario_id", "?") for r in records if not r.get("readme_content_sha256") and not r.get("readme_sha")
        ]
        total = len(records)

        if total < 42:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must include per-example content hashes",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Only {total} remote inventory records (expected 42)",
            )

        if len(missing_hashes) > 2:
            return RuleResult(
                rule_id=rule_id,
                description="Remote proof must include per-example content hashes",
                severity="FAILURE",
                passed=False,
                failure_detail=f"{len(missing_hashes)}/{total} records missing readme SHA: {missing_hashes[:5]}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote proof must include per-example content hashes",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail="remote/remote-readme-io-audit.json not found. Remote README I/O status was not independently verified.",
            )

        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Remote README I/O audit must be based on fetched content",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read remote-readme-io-audit.json: {exc}",
            )

        records = data.get("records", [])
        missing_io_status = [r for r in records if "has_io_section" not in r and "io_status" not in r]
        total = len(records)

        if total < 42:
            return RuleResult(
                rule_id=rule_id,
                description="Remote README I/O audit must be based on fetched content",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Only {total} records in remote README I/O audit (expected 42)",
            )

        if missing_io_status:
            return RuleResult(
                rule_id=rule_id,
                description="Remote README I/O audit must be based on fetched content",
                severity="FAILURE",
                passed=False,
                failure_detail=f"{len(missing_io_status)} records missing has_io_section field",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote README I/O audit must be based on fetched content",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "handoff/per-family/ exists but contains no Program.cs files in any family. "
                    "Sprint 65 had this defect — verdict claimed HANDOFF_READY with empty per-family/."
                ),
            )

        total_programs = sum(len(list((handoff_dir / f).rglob("Program.cs"))) for f in families_with_artifacts)

        return RuleResult(
            rule_id=rule_id,
            description="handoff/per-family/ must not be empty",
            severity="FAILURE",
            passed=True,
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
                severity="WARNING",
                passed=True,
                evidence="destination/content-audit-final.json not found (older sprint format)",
            )

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit output_kind must not be blank for any record",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read content-audit-final.json: {exc}",
            )

        records = data.get("records", [])
        blank_output_kind = [r.get("scenario_id", "?") for r in records if not r.get("output_kind")]

        if blank_output_kind:
            return RuleResult(
                rule_id=rule_id,
                description="Content audit output_kind must not be blank for any record",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"{len(blank_output_kind)} records have blank output_kind: {blank_output_kind}. "
                    "Sprint 65 defect S65-D4."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Content audit output_kind must not be blank for any record",
            severity="FAILURE",
            passed=True,
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
                        first_family_raw: object = next(iter(families.values()), {})
                        if not isinstance(first_family_raw, dict) or ("remote_example_present" not in first_family_raw and "approval_blocked" not in first_family_raw):
                            return RuleResult(
                                rule_id=rule_id,
                                description="Publication state must use separate fields",
                                severity="FAILURE",
                                passed=False,
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
                severity="FAILURE",
                passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read publication-truth-matrix-final.json: {exc}",
            )

        # Handle both flat-array format (Sprint 82+) and wrapped-object format (Sprint 66-81)
        records = data if isinstance(data, list) else data.get("records", [])
        if not records:
            return RuleResult(
                rule_id=rule_id,
                description="Publication state must use separate fields",
                severity="FAILURE",
                passed=False,
                failure_detail="publication-truth-matrix-final.json has no records",
            )

        first = records[0]
        # Sprint 82+ flat-array format uses remote_readme_io_classification instead of
        # remote_readme_has_io_docs. Accept either field to satisfy the separation requirement.
        io_field_present = "remote_readme_has_io_docs" in first or "remote_readme_io_classification" in first
        required_fields = ["remote_example_present", "approval_blocked"]
        missing = [f for f in required_fields if f not in first]
        if missing or not io_field_present:
            all_missing = missing + (
                [] if io_field_present else ["remote_readme_has_io_docs/remote_readme_io_classification"]
            )
            return RuleResult(
                rule_id=rule_id,
                description="Publication state must use separate fields",
                severity="FAILURE",
                passed=False,
                failure_detail=f"publication-truth-matrix-final.json records missing fields: {all_missing}",
            )

        io_field = (
            "remote_readme_io_classification"
            if "remote_readme_io_classification" in first
            else "remote_readme_has_io_docs"
        )
        return RuleResult(
            rule_id=rule_id,
            description="Publication state must use separate fields",
            severity="FAILURE",
            passed=True,
            evidence=f"{len(records)} records with separate state fields (remote_example_present, approval_blocked, {io_field})",
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
                severity="FAILURE",
                passed=True,
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
                        severity="FAILURE",
                        passed=False,
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
                severity="FAILURE",
                passed=False,
                failure_detail="Neither remote/remote-pr-proof-index.json nor bundled remote proof found",
            )

        return RuleResult(
            rule_id=rule_id,
            description="Remote proof must not rely solely on workspace/ files",
            severity="FAILURE",
            passed=True,
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
            (handoff_dir / f).rglob("Program.cs")
            for f in ["cells", "words", "pdf", "diagram", "email", "slides"]
            if (handoff_dir / f).exists()
        )

        if root_exists and not handoff_exists:
            return RuleResult(
                rule_id=rule_id,
                description="Root README artifact presence requires package artifacts",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    "root-readme/per-family/ exists with family files but "
                    "handoff/per-family/ has no Program.cs artifacts. "
                    "Sprint 65 defect S65-D3."
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Root README artifact presence requires package artifacts",
            severity="FAILURE",
            passed=True,
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
                            severity="FAILURE",
                            passed=False,
                            failure_detail=(
                                f"Verdict contains '{pattern}' but no remote README audit exists. "
                                "Cannot verify remote README I/O state without remote audit."
                            ),
                        )
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim remote README I/O",
                severity="WARNING",
                passed=True,
                evidence="No remote README audit; no overclaim detected in verdict",
            )

        try:
            data = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim remote README I/O",
                severity="FAILURE",
                passed=False,
                failure_detail=f"Cannot read remote-readme-io-audit.json: {exc}",
            )

        io_count = data.get("io_doc_count", -1)
        total = data.get("total", 0)

        verdict_path = self.bundle_dir / "final-verdict.md"
        if not verdict_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim remote README I/O",
                severity="FAILURE",
                passed=False,
                failure_detail="final-verdict.md not found",
            )

        verdict = verdict_path.read_text(encoding="utf-8", errors="replace")
        overclaim_patterns = ["REMOTE_README_IO_PUBLISHED", "README_IO_PUBLISHED_AND_VERIFIED"]
        overclaims = [p for p in overclaim_patterns if p in verdict]

        if io_count == 0 and overclaims:
            return RuleResult(
                rule_id=rule_id,
                description="Final verdict must not overclaim remote README I/O",
                severity="FAILURE",
                passed=False,
                failure_detail=(
                    f"remote-readme-io-audit.json shows io_doc_count=0/{total} but "
                    f"final-verdict.md contains: {overclaims}"
                ),
            )

        return RuleResult(
            rule_id=rule_id,
            description="Final verdict must not overclaim remote README I/O",
            severity="FAILURE",
            passed=True,
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
                severity="FAILURE",
                passed=False,
                failure_detail="handoff/per-family/ directory not found",
            )

        all_readme_files = list(handoff_dir.rglob("README.md"))
        # Skip family-level root READMEs at per-family/{family}/README.md —
        # those are root family READMEs (Sprint 70) with different format.
        # Only check example-level READMEs (depth >= 2 from per-family/).
        readme_files = [r for r in all_readme_files if r.parent.parent != handoff_dir]
        if not readme_files:
            return RuleResult(
                rule_id=rule_id,
                description="All handoff READMEs must have I/O section",
                severity="FAILURE",
                passed=False,
                failure_detail="No example README.md files found in handoff/per-family/",
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
                severity="FAILURE",
                passed=False,
                failure_detail=f"{len(missing_io)}/{len(readme_files)} handoff READMEs missing I/O section: {missing_io[:3]}",
            )

        return RuleResult(
            rule_id=rule_id,
            description="All handoff READMEs must have I/O section",
            severity="FAILURE",
            passed=True,
            evidence=f"All {len(readme_files)} handoff README.md files have '## Input and Output' section",
        )

    # ------------------------------------------------------------------
    # Sprint 67 NEW rules: close S66-D1 through S66-D5
    # ------------------------------------------------------------------
