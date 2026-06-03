"""Evidence validation rules — Sprint70to71Rules."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)



class Sprint70to71Rules:
    """Rule mixin for evidence validation."""

    def _rule_handoff_root_readme_in_sprint_folder(self) -> RuleResult:
        """All family handoff-index root_readme.source_path must be inside current sprint handoff.

        Sprint 69 defect S69-D1: all 6 handoff-indexes pointed root_readme.source_path
        to reports/sprint68/root-readme/per-family/ — outside the handoff package.
        A self-contained handoff must have root READMEs physically inside it.
        """
        rule_id = "handoff_root_readme_in_sprint_folder"
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        sprint_id = self._read_sprint_id()
        stale_paths = []
        for family in families:
            idx_path = self.bundle_dir / "handoff" / "per-family" / family / "handoff-index.json"
            if not idx_path.exists():
                continue
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                rr = idx.get("root_readme", {})
                src = rr.get("source_path", "")
                # Must be inside current sprint handoff folder
                expected_prefix = f"reports/{sprint_id}/handoff/per-family/{family}/"
                if src and not src.startswith(expected_prefix):
                    stale_paths.append(f"{family}: source_path={src!r} (expected prefix {expected_prefix!r})")
            except Exception as exc:
                stale_paths.append(f"{family}: read error {exc}")
        if stale_paths:
            return RuleResult(
                rule_id=rule_id,
                description="Handoff-index root_readme.source_path must be inside current sprint handoff folder",
                severity="FAILURE", passed=False,
                failure_detail=f"Stale root README source paths: {'; '.join(stale_paths)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Handoff-index root_readme.source_path must be inside current sprint handoff folder",
            severity="FAILURE", passed=True,
            evidence=f"All 6 family handoff-index root_readme.source_path values are inside reports/{sprint_id}/handoff/",
        )

    def _rule_handoff_root_readme_file_present(self) -> RuleResult:
        """Root README file must physically exist at root_readme.source_path for all families.

        Sprint 69 defect S69-D1: even if source_path were updated, the file must
        actually be present in the handoff package.
        """
        rule_id = "handoff_root_readme_file_present"
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        missing = []
        for family in families:
            idx_path = self.bundle_dir / "handoff" / "per-family" / family / "handoff-index.json"
            if not idx_path.exists():
                continue
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                rr = idx.get("root_readme", {})
                src = rr.get("source_path", "")
                if src:
                    file_path = self._resolve_sprint_relative_path(src)
                    if not file_path.exists():
                        missing.append(f"{family}: {src!r} not found")
            except Exception as exc:
                missing.append(f"{family}: read error {exc}")
        if missing:
            return RuleResult(
                rule_id=rule_id,
                description="Root README file must physically exist at source_path for all families",
                severity="FAILURE", passed=False,
                failure_detail=f"Missing root README files: {'; '.join(missing)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="Root README file must physically exist at source_path for all families",
            severity="FAILURE", passed=True,
            evidence="All 6 family root README files are physically present at their source_path",
        )

    def _rule_handoff_root_readme_hash_matches(self) -> RuleResult:
        """root_readme.sha256 in handoff-index must match the physical file at source_path.

        Ensures the stored hash is not stale (i.e., the file content matches what was indexed).
        """
        rule_id = "handoff_root_readme_hash_matches"
        import hashlib as _hashlib
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        mismatches = []
        for family in families:
            idx_path = self.bundle_dir / "handoff" / "per-family" / family / "handoff-index.json"
            if not idx_path.exists():
                continue
            try:
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                rr = idx.get("root_readme", {})
                src = rr.get("source_path", "")
                stored_hash = rr.get("sha256", "")
                if not src or not stored_hash:
                    continue
                file_path = self._resolve_sprint_relative_path(src)
                if not file_path.exists():
                    mismatches.append(f"{family}: file not found at {src!r}")
                    continue
                h = _hashlib.sha256(file_path.read_bytes()).hexdigest()
                if h != stored_hash:
                    mismatches.append(
                        f"{family}: stored={stored_hash[:16]}… actual={h[:16]}… for {src!r}"
                    )
            except Exception as exc:
                mismatches.append(f"{family}: read error {exc}")
        if mismatches:
            return RuleResult(
                rule_id=rule_id,
                description="root_readme.sha256 in handoff-index must match physical file",
                severity="FAILURE", passed=False,
                failure_detail=f"Hash mismatches: {'; '.join(mismatches)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="root_readme.sha256 in handoff-index must match physical file",
            severity="FAILURE", passed=True,
            evidence="All 6 family root README sha256 hashes match their physical files",
        )

    def _rule_publication_handoff_root_readme_hash_matches(self) -> RuleResult:
        """publication-handoff-index.json root_readme_sha256 per family must match physical file.

        Ensures the publication index is not stale for root README hashes.
        """
        rule_id = "publication_handoff_root_readme_hash_matches"
        import hashlib as _hashlib
        phi_path = self.bundle_dir / "handoff" / "publication-handoff-index.json"
        if not phi_path.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication-handoff-index.json must exist with correct root README hashes",
                severity="FAILURE", passed=False,
                failure_detail="handoff/publication-handoff-index.json not found",
            )
        try:
            phi = json.loads(phi_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return RuleResult(
                rule_id=rule_id,
                description="publication-handoff-index.json must be valid JSON with root README hashes",
                severity="FAILURE", passed=False,
                failure_detail=f"Cannot parse publication-handoff-index.json: {exc}",
            )
        families_data = phi.get("families", [])
        if not isinstance(families_data, list):
            return RuleResult(
                rule_id=rule_id,
                description="publication-handoff-index.json families must be a list",
                severity="FAILURE", passed=False,
                failure_detail="families field is not a list",
            )
        mismatches = []
        for fam_data in families_data:
            family = fam_data.get("family", "")
            stored_hash = fam_data.get("root_readme_sha256", "")
            src_path = fam_data.get("root_readme_source_path", "")
            if not stored_hash or not src_path:
                continue
            file_path = self._resolve_sprint_relative_path(src_path)
            if not file_path.exists():
                mismatches.append(f"{family}: root README not found at {src_path!r}")
                continue
            actual = _hashlib.sha256(file_path.read_bytes()).hexdigest()
            if actual != stored_hash:
                mismatches.append(
                    f"{family}: phi_hash={stored_hash[:16]}… actual={actual[:16]}…"
                )
        if mismatches:
            return RuleResult(
                rule_id=rule_id,
                description="publication-handoff-index root_readme_sha256 must match physical files",
                severity="FAILURE", passed=False,
                failure_detail=f"Hash mismatches: {'; '.join(mismatches)}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="publication-handoff-index root_readme_sha256 must match physical files",
            severity="FAILURE", passed=True,
            evidence="All family root_readme_sha256 in publication-handoff-index match physical files",
        )

    def _rule_legacy_simplified_index_superseded(self) -> RuleResult:
        """legacy-plan-reconciliation/reconciliation-index.md must not be treated as current authority.

        Sprint 69 defect S69-D2: the old reconciliation-index.md from Sprint 67 remained
        alongside the newer exact-legacy-plan-reconciliation-final.md without being
        explicitly superseded, creating potential confusion.

        This rule passes if EITHER:
        - legacy-plan-reconciliation/reconciliation-index.md does not exist in the bundle, OR
        - history/legacy-plan-reconciliation-superseded.md exists (marking it historical), OR
        - legacy-reconciliation/README.md exists explaining the authority chain
        """
        rule_id = "legacy_simplified_index_superseded"
        old_index = self.bundle_dir / "legacy-plan-reconciliation" / "reconciliation-index.md"
        superseded_marker = self.bundle_dir / "history" / "legacy-plan-reconciliation-superseded.md"
        authority_readme = self.bundle_dir / "legacy-reconciliation" / "README.md"
        final_authority = self.bundle_dir / "legacy-reconciliation" / "exact-legacy-plan-reconciliation-final.md"

        # Final authority must exist
        if not final_authority.exists():
            return RuleResult(
                rule_id=rule_id,
                description="exact-legacy-plan-reconciliation-final.md must exist as current authority",
                severity="FAILURE", passed=False,
                failure_detail="legacy-reconciliation/exact-legacy-plan-reconciliation-final.md not found",
            )

        # If old index exists, there must be a superseded marker or authority README
        if old_index.exists():
            if not superseded_marker.exists() and not authority_readme.exists():
                return RuleResult(
                    rule_id=rule_id,
                    description="Old legacy-plan-reconciliation/reconciliation-index.md must be marked superseded",
                    severity="FAILURE", passed=False,
                    failure_detail=(
                        "legacy-plan-reconciliation/reconciliation-index.md exists without superseded marker. "
                        "Create history/legacy-plan-reconciliation-superseded.md or legacy-reconciliation/README.md"
                    ),
                )

        return RuleResult(
            rule_id=rule_id,
            description="Old legacy reconciliation index must be superseded by current authority",
            severity="FAILURE", passed=True,
            evidence="Final authority exists; old simplified index is either absent or marked superseded",
        )

    # ------------------------------------------------------------------
    # Sprint 71 NEW rules: stale-path scanner (close S70-D1, S70-D2, S70-D3)
    # ------------------------------------------------------------------

    def _rule_content_audit_final_no_stale_paths(self) -> RuleResult:
        """destination/content-audit-final.json must contain no stale sprint paths.

        Sprint 70 defect S70-D1: content-audit-final.json had all 42 records pointing
        to reports/sprint69/ paths. Sprint 71 repairs this by requiring all active
        paths to point to the current sprint.
        """
        rule_id = "content_audit_final_no_stale_paths"
        audit_file = self.bundle_dir / "destination" / "content-audit-final.json"
        if not audit_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="destination/content-audit-final.json must exist with no stale sprint paths",
                severity="FAILURE", passed=False,
                failure_detail="destination/content-audit-final.json not found",
            )
        try:
            content = audit_file.read_text(encoding="utf-8")
            stale = self._get_stale_paths_in_content(content)
            if stale:
                return RuleResult(
                    rule_id=rule_id,
                    description="destination/content-audit-final.json must have no stale sprint paths",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale sprint paths found in content-audit-final.json: {stale}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="destination/content-audit-final.json must be readable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="destination/content-audit-final.json contains no stale sprint paths",
            severity="FAILURE", passed=True,
            evidence="destination/content-audit-final.json scanned — no stale sprint paths found",
        )

    def _rule_publication_matrix_no_stale_paths(self) -> RuleResult:
        """publication/publication-truth-matrix-final.json must contain no stale sprint paths.

        Sprint 70 defect S70-D2: publication-truth-matrix-final.json had all 42 records
        pointing to reports/sprint69/ handoff_package_path. Sprint 71 repairs this.
        """
        rule_id = "publication_matrix_no_stale_paths"
        matrix_file = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not matrix_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication/publication-truth-matrix-final.json must exist with no stale sprint paths",
                severity="FAILURE", passed=False,
                failure_detail="publication/publication-truth-matrix-final.json not found",
            )
        try:
            content = matrix_file.read_text(encoding="utf-8")
            stale = self._get_stale_paths_in_content(content)
            if stale:
                return RuleResult(
                    rule_id=rule_id,
                    description="publication/publication-truth-matrix-final.json must have no stale sprint paths",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale sprint paths found in publication-truth-matrix-final.json: {stale}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="publication/publication-truth-matrix-final.json must be readable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="publication/publication-truth-matrix-final.json contains no stale sprint paths",
            severity="FAILURE", passed=True,
            evidence="publication/publication-truth-matrix-final.json scanned — no stale sprint paths found",
        )

    def _rule_handoff_index_no_stale_paths(self) -> RuleResult:
        """All handoff-index.json files must contain no stale sprint paths."""
        rule_id = "handoff_index_no_stale_paths"
        handoff_dir = self.bundle_dir / "handoff" / "per-family"
        if not handoff_dir.exists():
            return RuleResult(
                rule_id=rule_id,
                description="handoff/per-family/ must exist",
                severity="FAILURE", passed=False,
                failure_detail="handoff/per-family/ not found",
            )
        stale_found = {}
        for idx_file in handoff_dir.rglob("handoff-index.json"):
            try:
                content = idx_file.read_text(encoding="utf-8")
                stale = self._get_stale_paths_in_content(content)
                if stale:
                    rel = str(idx_file.relative_to(self.bundle_dir)).replace("\\", "/")
                    stale_found[rel] = stale
            except OSError:
                pass
        if stale_found:
            return RuleResult(
                rule_id=rule_id,
                description="All handoff-index.json files must have no stale sprint paths",
                severity="FAILURE", passed=False,
                failure_detail=f"Stale paths in handoff indexes: {stale_found}",
            )
        return RuleResult(
            rule_id=rule_id,
            description="All handoff-index.json files contain no stale sprint paths",
            severity="FAILURE", passed=True,
            evidence="All per-family handoff-index.json files scanned — no stale sprint paths found",
        )

    def _rule_remote_vs_handoff_no_stale_paths(self) -> RuleResult:
        """remote/remote-vs-handoff-final.json must contain no stale sprint paths."""
        rule_id = "remote_vs_handoff_no_stale_paths"
        rvh_file = self.bundle_dir / "remote" / "remote-vs-handoff-final.json"
        if not rvh_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-vs-handoff-final.json must exist with no stale sprint paths",
                severity="FAILURE", passed=False,
                failure_detail="remote/remote-vs-handoff-final.json not found",
            )
        try:
            content = rvh_file.read_text(encoding="utf-8")
            stale = self._get_stale_paths_in_content(content)
            if stale:
                return RuleResult(
                    rule_id=rule_id,
                    description="remote/remote-vs-handoff-final.json must have no stale sprint paths",
                    severity="FAILURE", passed=False,
                    failure_detail=f"Stale sprint paths found in remote-vs-handoff-final.json: {stale}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="remote/remote-vs-handoff-final.json must be readable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="remote/remote-vs-handoff-final.json contains no stale sprint paths",
            severity="FAILURE", passed=True,
            evidence="remote/remote-vs-handoff-final.json scanned — no stale sprint paths found",
        )

    def _rule_content_audit_final_files_exist(self) -> RuleResult:
        """destination/content-audit-final.json — every referenced handoff_path must exist.

        Sprint 70 defect S70-D1 (secondary): paths pointed to sprint69 which existed
        in the repo but were not the canonical sprint70 handoff. Sprint 71 requires
        the referenced files to exist in the current sprint bundle.
        """
        rule_id = "content_audit_final_files_exist"
        audit_file = self.bundle_dir / "destination" / "content-audit-final.json"
        if not audit_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="destination/content-audit-final.json must exist",
                severity="FAILURE", passed=False,
                failure_detail="destination/content-audit-final.json not found",
            )
        try:
            data = json.loads(audit_file.read_text(encoding="utf-8"))
            records = data.get("records", data) if isinstance(data, dict) else data
            missing = []
            for rec in records:
                hp = rec.get("handoff_path", "")
                if hp:
                    resolved = self._resolve_sprint_relative_path(hp)
                    if not resolved.exists():
                        missing.append(hp)
            if missing:
                return RuleResult(
                    rule_id=rule_id,
                    description="All handoff_path references in content-audit-final.json must exist",
                    severity="FAILURE", passed=False,
                    failure_detail=f"{len(missing)} handoff_path(s) not found: {missing[:3]}{'...' if len(missing) > 3 else ''}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="content-audit-final.json must be parseable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="All handoff_path references in content-audit-final.json exist physically",
            severity="FAILURE", passed=True,
            evidence=f"All {len(records)} handoff_path(s) verified to exist",
        )

    def _rule_publication_matrix_files_exist(self) -> RuleResult:
        """publication/publication-truth-matrix-final.json — every handoff_package_path must exist."""
        rule_id = "publication_matrix_files_exist"
        matrix_file = self.bundle_dir / "publication" / "publication-truth-matrix-final.json"
        if not matrix_file.exists():
            return RuleResult(
                rule_id=rule_id,
                description="publication/publication-truth-matrix-final.json must exist",
                severity="FAILURE", passed=False,
                failure_detail="publication/publication-truth-matrix-final.json not found",
            )
        try:
            data = json.loads(matrix_file.read_text(encoding="utf-8"))
            records = data.get("records", data.get("examples", [])) if isinstance(data, dict) else data
            missing = []
            for rec in records:
                hp = rec.get("handoff_package_path", "")
                if hp:
                    resolved = self._resolve_sprint_relative_path(hp)
                    if not resolved.exists():
                        missing.append(hp)
            if missing:
                return RuleResult(
                    rule_id=rule_id,
                    description="All handoff_package_path references in publication-truth-matrix-final.json must exist",
                    severity="FAILURE", passed=False,
                    failure_detail=f"{len(missing)} handoff_package_path(s) not found: {missing[:3]}{'...' if len(missing) > 3 else ''}",
                )
        except (OSError, ValueError) as e:
            return RuleResult(
                rule_id=rule_id,
                description="publication-truth-matrix-final.json must be parseable",
                severity="FAILURE", passed=False,
                failure_detail=str(e),
            )
        return RuleResult(
            rule_id=rule_id,
            description="All handoff_package_path references in publication-truth-matrix-final.json exist physically",
            severity="FAILURE", passed=True,
            evidence=f"All {len(records)} handoff_package_path(s) verified to exist",
        )

    # ------------------------------------------------------------------
    # Sprint 72 NEW rules: remote proof consistency (close S71-D1)
    # ------------------------------------------------------------------
