"""
Strict Evidence Contract for LowCode Sprint Bundles.

Defines required artifacts for a valid sprint evidence bundle and validates
that a given bundle (directory or ZIP) meets the contract. Thin bundles with
fewer than the required artifacts fail validation.

Usage:
    from plugin_examples.evidence_contract import StrictEvidenceContract, ContractResult
    result = StrictEvidenceContract().validate_zip(path_to_zip)
    if not result.passed:
        raise RuntimeError(f"Bundle contract failed: {result.failures}")
"""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


# ---------------------------------------------------------------------------
# Required artifact categories (filename patterns, matched against ZIP entries)
# ---------------------------------------------------------------------------

#: Required artifact categories and at least one matching filename pattern per category.
#: A category passes if ANY file in the ZIP matches its pattern list (basename match).
REQUIRED_CATEGORIES: dict[str, list[str]] = {
    "git_status_initial": ["git-status-initial.txt"],
    "git_status_final": ["git-status-final.txt"],
    "git_diff_initial": ["git-diff-initial.patch"],
    "git_diff_final": ["git-diff-final.patch"],
    "git_log_proof": ["git-log-proof.txt"],
    "changed_files": ["changed-files.txt"],
    "source_state_classification": ["source-state-classification.json"],
    "test_summary": ["test-summary.json"],
    "test_full_log": ["test-full.log", "test-full-not-run.md"],
    "final_verdict": ["final-verdict.md"],
    "final_state_summary": ["final-state-summary.yaml"],
    "bundle_contract_definition": ["bundle-contract-definition.json"],
    "bundle_contract_validation": ["bundle-contract-validation-report.json"],
    "publication_mode_decision": ["publication-mode-decision.json"],
    "github_token_readiness": ["github-token-readiness-report.json"],
    "pr3_audit_or_result": [
        "pdf-pr3-final-package-audit.json",
        "pdf-pr3-publication-result.json",
        "pdf-pr3-approval-blocked.md",
    ],
    "pr5_audit_or_result": [
        "pdf-pr5-final-package-audit.json",
        "pdf-pr5-publication-result.json",
        "pdf-pr5-approval-blocked.md",
    ],
    "pr6_audit_or_result": [
        "pdf-pr6-final-package-audit.json",
        "pdf-pr6-publication-result.json",
        "pdf-pr6-approval-blocked.md",
    ],
    "pr7_audit_or_result": [
        "pdf-pr7-final-package-audit.json",
        "pdf-pr7-publication-result.json",
        "pdf-pr7-approval-blocked.md",
    ],
    "pr8_audit_or_result": [
        "pdf-pr8-final-package-audit.json",
        "pdf-pr8-publication-result.json",
        "pdf-pr8-approval-blocked.md",
    ],
    "pr9_audit_or_result": [
        "pdf-pr9-final-package-audit.json",
        "pdf-pr9-publication-result.json",
        "pdf-pr9-approval-blocked.md",
    ],
    "post_publication": [
        "post-publication-pr-verification-report.json",
        "post-publication-not-run-approval-blocked.md",
    ],
    "formimporter_defect": [
        "pdf-formimporter-defect-package-final-report.json",
        "pdf-formimporter-upstream-issue-final.md",
    ],
    "pdf_closeout_matrix": ["pdf-final-denominator-closeout-matrix.json"],
    "pdf_max_coverage": ["pdf-maximum-achievable-coverage-report.md"],
    "email_runtime": ["email-final-runtime-status.json"],
    "slides_runtime": ["slides-final-runtime-status.json"],
    "words_guard": ["words-final-guard-report.json"],
    "cells_guard": ["cells-final-guard-report.json"],
    "diagram_guard": ["diagram-final-guard-report.json"],
    "all_family_scoreboard_json": ["all-family-launch-scoreboard.json"],
    "all_family_scoreboard_md": ["all-family-launch-scoreboard.md"],
    "families_needing_work": ["families-needing-launch-work.json"],
    "release_state": ["release-state-reconciliation-report.json"],
    "taskcard_reconciliation": ["taskcard-reconciliation-report.json"],
    "taskcard_state": ["taskcard-state-after-sprint28.json"],
}

#: Patterns indicating raw secrets present in a file (lines matching these must not appear).
SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ghp_[A-Za-z0-9]{36}", re.IGNORECASE),  # GitHub classic PAT
    re.compile(r"github_pat_[A-Za-z0-9_]{82}", re.IGNORECASE),  # GitHub fine-grained PAT
    re.compile(r"sk-[A-Za-z0-9]{48}", re.IGNORECASE),  # OpenAI key
    re.compile(r"Bearer [A-Za-z0-9\-_\.]{20,}", re.IGNORECASE),  # Generic Bearer token
]

#: Minimum number of unique categories that must pass (all of REQUIRED_CATEGORIES).
MIN_CATEGORIES_REQUIRED = len(REQUIRED_CATEGORIES)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ContractResult:
    passed: bool
    categories_found: list[str] = field(default_factory=list)
    categories_missing: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    secret_violations: list[str] = field(default_factory=list)
    file_count: int = 0
    verdict: str = ""

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"ContractResult[{status}] files={self.file_count} "
            f"categories={len(self.categories_found)}/{MIN_CATEGORIES_REQUIRED} "
            f"failures={len(self.failures)}"
        )


# ---------------------------------------------------------------------------
# Contract validator
# ---------------------------------------------------------------------------

class StrictEvidenceContract:
    """
    Validates that a sprint evidence ZIP meets the strict evidence contract.

    The contract requires every category in REQUIRED_CATEGORIES to be satisfied
    by at least one file in the ZIP. It also scans text files for raw secrets.
    """

    def validate_zip(self, zip_path: str | Path) -> ContractResult:
        """
        Validate a ZIP file against the strict evidence contract.

        Parameters
        ----------
        zip_path:
            Absolute or relative path to the ZIP file.

        Returns
        -------
        ContractResult
            Result object with passed/failed status and details.
        """
        zip_path = Path(zip_path)
        result = ContractResult(passed=False)

        if not zip_path.exists():
            result.failures.append(f"ZIP file not found: {zip_path}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        if not zip_path.is_absolute():
            result.warnings.append(
                "ZIP path is relative; contract requires absolute path in final response."
            )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                result.file_count = len(names)
                basenames = {Path(n).name for n in names}

                # Check categories
                for category, patterns in REQUIRED_CATEGORIES.items():
                    if any(p in basenames for p in patterns):
                        result.categories_found.append(category)
                    else:
                        result.categories_missing.append(category)
                        result.failures.append(
                            f"Missing category '{category}' — "
                            f"expected one of: {patterns}"
                        )

                # Scan text files for secrets
                for name in names:
                    if name.endswith((".json", ".md", ".txt", ".yaml", ".yml", ".patch", ".log")):
                        try:
                            content = zf.read(name).decode("utf-8", errors="replace")
                            for pattern in SECRET_PATTERNS:
                                if pattern.search(content):
                                    violation = f"Possible secret in {name}: pattern {pattern.pattern}"
                                    result.secret_violations.append(violation)
                                    result.failures.append(violation)
                        except Exception:
                            pass  # Binary file — skip

        except zipfile.BadZipFile as e:
            result.failures.append(f"ZIP is invalid/corrupt: {e}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        # Final pass/fail
        if result.failures:
            result.passed = False
            result.verdict = "BUNDLE_CONTRACT_FAILED"
        else:
            result.passed = True
            result.verdict = "BUNDLE_CONTRACT_PASSED"

        return result

    def validate_directory(self, dir_path: str | Path) -> ContractResult:
        """
        Validate an unpacked directory of evidence artifacts against the contract.

        Parameters
        ----------
        dir_path:
            Path to a directory containing evidence files (searched recursively).
        """
        dir_path = Path(dir_path)
        result = ContractResult(passed=False)

        if not dir_path.exists() or not dir_path.is_dir():
            result.failures.append(f"Directory not found: {dir_path}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        all_files = list(dir_path.rglob("*"))
        basenames = {f.name for f in all_files if f.is_file()}
        result.file_count = len(basenames)

        for category, patterns in REQUIRED_CATEGORIES.items():
            if any(p in basenames for p in patterns):
                result.categories_found.append(category)
            else:
                result.categories_missing.append(category)
                result.failures.append(
                    f"Missing category '{category}' — expected one of: {patterns}"
                )

        result.passed = not result.failures
        result.verdict = "BUNDLE_CONTRACT_PASSED" if result.passed else "BUNDLE_CONTRACT_FAILED"
        return result


def contract_definition() -> dict:
    """Return the bundle contract definition as a serialisable dict."""
    return {
        "contract_version": "1.0.0",
        "sprint": "sprint28+",
        "description": "Strict evidence contract for LowCode sprint bundles. Every category must be satisfied.",
        "required_categories": {
            cat: patterns for cat, patterns in REQUIRED_CATEGORIES.items()
        },
        "min_categories_required": MIN_CATEGORIES_REQUIRED,
        "secret_scanning_enabled": True,
        "secret_patterns": [p.pattern for p in SECRET_PATTERNS],
        "failure_verdict": "BUNDLE_CONTRACT_FAILED",
        "pass_verdict": "BUNDLE_CONTRACT_PASSED",
    }


# ---------------------------------------------------------------------------
# Contract v2 — state-correctness, not just category presence (Sprint 29+)
# ---------------------------------------------------------------------------

#: Category overrides for v2 (updated patterns replacing v1 entries).
_REQUIRED_CATEGORIES_V2_UPDATES: dict[str, list[str]] = {
    # Updated: sprint29 taskcard state replaces sprint28
    "taskcard_state": ["taskcard-state-after-sprint29.json"],
    # Updated: formimporter check file replaces final-report
    "formimporter_defect": [
        "pdf-formimporter-defect-package-final-check.json",
        "pdf-formimporter-defect-package-final-report.json",
        "pdf-formimporter-upstream-issue-final.md",
    ],
}

#: Categories removed from v1 (sprint28-specific; not required in Sprint 29).
_REQUIRED_CATEGORIES_V2_REMOVED: frozenset[str] = frozenset({"pdf_max_coverage"})

#: New categories required in Sprint 29 (not present in v1).
_REQUIRED_CATEGORIES_V2_NEW: dict[str, list[str]] = {
    "sprint28_commit_proof": ["sprint28-commit-proof.json"],
    "sprint28_reconciliation": ["sprint28-bundle-vs-commit-reconciliation.md"],
    "evidence_contract_v2_impl": ["evidence-contract-v2-implementation-report.json"],
    "evidence_contract_v2_tests": ["evidence-contract-v2-test-report.json"],
    "pr3_version_policy": ["pdf-pr3-version-policy-report.json"],
    "pr5_version_policy": ["pdf-pr5-version-policy-report.json"],
    "pr6_version_policy": ["pdf-pr6-version-policy-report.json"],
    "formimporter_defect_check": ["pdf-formimporter-defect-package-final-check.json"],
    "test_targeted_log": ["test-targeted.log"],
}

#: Combined v2 categories: v1 (minus removed, with updates) + new.
COMBINED_CATEGORIES_V2: dict[str, list[str]] = {
    **{
        k: _REQUIRED_CATEGORIES_V2_UPDATES.get(k, v)
        for k, v in REQUIRED_CATEGORIES.items()
        if k not in _REQUIRED_CATEGORIES_V2_REMOVED
    },
    **_REQUIRED_CATEGORIES_V2_NEW,
}

MIN_CATEGORIES_REQUIRED_V2: int = len(COMBINED_CATEGORIES_V2)

#: Allowed final verdicts for Sprint 29 bundles.
ALLOWED_VERDICTS_V2: frozenset[str] = frozenset({
    "SPRINT29_PUBLISHED_AND_EVIDENCE_CONTRACT_V2_COMPLETE",
    "SPRINT29_APPROVAL_BLOCKED_EVIDENCE_CONTRACT_V2_COMPLETE",
    "SPRINT29_PUBLICATION_PARTIAL_CONTRACT_V2_COMPLETE",
    "SPRINT29_BLOCKED_EVIDENCE_CONTRACT_V2_FAILED",
    "SPRINT29_BLOCKED_SOURCE_STATE",
    "SPRINT29_REJECTED_UNSAFE_TO_PUBLISH",
})

#: git status line prefixes indicating STAGED source/test/config files (must not appear post-commit).
_STAGED_SOURCE_PATTERN = re.compile(
    r"^[AMDRC][AMDRC?! ]\s+(src/|tests/|pipeline/)",
    re.MULTILINE,
)

#: Sprint 28 commit SHA (short) — must appear in git-log-proof.txt.
_SPRINT28_COMMIT = "20686d3"


class StrictEvidenceContractV2(StrictEvidenceContract):
    """
    v2 of the strict evidence contract (Sprint 29+).

    Extends v1 with:
    - 45 required categories (vs 37 in v1).
    - Absolute ZIP path required.
    - Content-level checks on key artifacts:
      * git-status-final.txt must not contain staged source/test/config files.
      * git-log-proof.txt must contain Sprint 28 commit 20686d3.
      * final-verdict.md must contain an allowed Sprint 29 verdict.
      * test-summary.json must report failed==0 and passed>0.
      * bundle-contract-validation-report.json must report passed=true.
    """

    def validate_zip(self, zip_path: str | Path) -> ContractResult:
        zip_path = Path(zip_path)
        result = ContractResult(passed=False)

        if not zip_path.exists():
            result.failures.append(f"ZIP file not found: {zip_path}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        if not zip_path.is_absolute():
            result.failures.append(
                f"v2: ZIP path must be absolute for evidence completeness, got: {zip_path}"
            )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                result.file_count = len(names)
                basenames = {Path(n).name for n in names}

                # Presence checks — v2 categories (45 total)
                for category, patterns in COMBINED_CATEGORIES_V2.items():
                    if any(p in basenames for p in patterns):
                        result.categories_found.append(category)
                    else:
                        result.categories_missing.append(category)
                        result.failures.append(
                            f"Missing category '{category}' — "
                            f"expected one of: {patterns}"
                        )

                # Secret scan (all text files)
                for name in names:
                    if name.endswith((".json", ".md", ".txt", ".yaml", ".yml", ".patch", ".log")):
                        try:
                            content = zf.read(name).decode("utf-8", errors="replace")
                            for pattern in SECRET_PATTERNS:
                                if pattern.search(content):
                                    violation = (
                                        f"v2: Possible secret in {name}: "
                                        f"pattern {pattern.pattern}"
                                    )
                                    result.secret_violations.append(violation)
                                    result.failures.append(violation)
                        except Exception:
                            pass

                # v2 content-level checks
                self._validate_content_v2(zf, names, result)

        except zipfile.BadZipFile as e:
            result.failures.append(f"ZIP is invalid/corrupt: {e}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        result.passed = not result.failures
        result.verdict = "BUNDLE_CONTRACT_PASSED" if result.passed else "BUNDLE_CONTRACT_FAILED"
        return result

    # ------------------------------------------------------------------
    # Content-level validation helpers
    # ------------------------------------------------------------------

    def _validate_content_v2(
        self,
        zf: zipfile.ZipFile,
        names: list[str],
        result: ContractResult,
    ) -> None:
        name_map: dict[str, str] = {Path(n).name: n for n in names}
        self._check_git_status_final(zf, name_map, result)
        self._check_git_log_proof(zf, name_map, result)
        self._check_final_verdict(zf, name_map, result)
        self._check_test_summary(zf, name_map, result)
        self._check_bundle_contract_report(zf, name_map, result)

    def _read_text(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        basename: str,
    ) -> str | None:
        if basename not in name_map:
            return None
        try:
            return zf.read(name_map[basename]).decode("utf-8", errors="replace")
        except Exception:
            return None

    def _check_git_status_final(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        content = self._read_text(zf, name_map, "git-status-final.txt")
        if content is None:
            return  # Missing category already reported by presence check
        staged = _STAGED_SOURCE_PATTERN.findall(content)
        if staged:
            result.failures.append(
                f"v2: git-status-final.txt contains staged/dirty source-tree files: "
                f"{staged[:5]}. Sprint work must be committed before the final status is captured."
            )

    def _check_git_log_proof(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        content = self._read_text(zf, name_map, "git-log-proof.txt")
        if content is None:
            return
        if not content.strip():
            result.failures.append("v2: git-log-proof.txt is empty — no commits recorded.")
            return
        if _SPRINT28_COMMIT not in content:
            result.failures.append(
                f"v2: git-log-proof.txt does not contain Sprint 28 commit {_SPRINT28_COMMIT}. "
                "Sprint 28 must be committed before Sprint 29 bundle is created."
            )

    def _check_final_verdict(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        content = self._read_text(zf, name_map, "final-verdict.md")
        if content is None:
            return
        if "IN_PROGRESS" in content.upper():
            result.failures.append(
                "v2: final-verdict.md contains 'IN_PROGRESS' — sprint is not complete."
            )
            return
        if not any(v in content for v in ALLOWED_VERDICTS_V2):
            result.failures.append(
                f"v2: final-verdict.md does not contain any allowed Sprint 29 verdict. "
                f"Allowed: {sorted(ALLOWED_VERDICTS_V2)}"
            )

    def _check_test_summary(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        content = self._read_text(zf, name_map, "test-summary.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append("v2: test-summary.json is not valid JSON.")
            return
        if isinstance(data, dict):
            failed = int(data.get("failed", data.get("errors", 0)))
            passed = int(data.get("passed", data.get("total", 0)))
            if failed > 0:
                result.failures.append(
                    f"v2: test-summary.json reports {failed} failed tests — must be 0."
                )
            if passed == 0:
                result.failures.append(
                    "v2: test-summary.json reports 0 passed tests — test suite did not run."
                )

    def _check_bundle_contract_report(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        content = self._read_text(zf, name_map, "bundle-contract-validation-report.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append(
                "v2: bundle-contract-validation-report.json is not valid JSON."
            )
            return
        if not data.get("passed", False):
            result.failures.append(
                "v2: bundle-contract-validation-report.json has passed=false — "
                "bundle failed its own contract validation."
            )
        missing = data.get("categories_missing", [])
        if missing:
            result.failures.append(
                f"v2: bundle-contract-validation-report.json reports categories_missing: {missing}"
            )


def contract_definition_v2() -> dict:
    """Return the v2 bundle contract definition as a serialisable dict."""
    return {
        "contract_version": "2.0.0",
        "sprint": "sprint29+",
        "description": (
            "Strict evidence contract v2 for LowCode sprint bundles. "
            "Validates category presence AND state correctness. "
            "Requires post-commit git status (no staged source files), "
            "prior sprint commit in git log, and valid final verdict."
        ),
        "required_categories": {
            cat: patterns for cat, patterns in COMBINED_CATEGORIES_V2.items()
        },
        "min_categories_required": MIN_CATEGORIES_REQUIRED_V2,
        "content_checks_enabled": True,
        "content_checks": [
            "git-status-final.txt: no staged source/test/config files",
            f"git-log-proof.txt: must contain {_SPRINT28_COMMIT}",
            "final-verdict.md: must contain an allowed Sprint 29 verdict",
            "test-summary.json: failed==0 and passed>0",
            "bundle-contract-validation-report.json: passed=true",
        ],
        "secret_scanning_enabled": True,
        "secret_patterns": [p.pattern for p in SECRET_PATTERNS],
        "allowed_verdicts": sorted(ALLOWED_VERDICTS_V2),
        "failure_verdict": "BUNDLE_CONTRACT_FAILED",
        "pass_verdict": "BUNDLE_CONTRACT_PASSED",
    }


# ---------------------------------------------------------------------------
# Contract v3 — package-audit blocking flags, source-state classification,
#               Sprint 30 verdicts, and 45-category reconciliation (Sprint 30+)
# ---------------------------------------------------------------------------

#: Categories removed from v2 (renamed to reflect sprint29 content).
_REQUIRED_CATEGORIES_V3_REMOVED: frozenset[str] = frozenset({
    "sprint28_commit_proof",
    "sprint28_reconciliation",
})

#: Pattern updates for v3 (key kept, patterns updated).
_REQUIRED_CATEGORIES_V3_UPDATES: dict[str, list[str]] = {
    "taskcard_state": ["taskcard-state-after-sprint30.json"],
}

#: New categories in v3: Sprint 29 commit proof + bin/obj cleanup audit.
_REQUIRED_CATEGORIES_V3_NEW: dict[str, list[str]] = {
    "sprint29_commit_proof": ["sprint29-commit-proof.json"],
    "sprint29_reconciliation": ["sprint29-bundle-vs-commit-reconciliation.md"],
    "bin_obj_cleanup": ["all-pr-packages-audit-post-cleanup.json"],
}

#: Combined v3 categories: v2 (minus removed, with updates) + new.
#: v2 had 44 categories; v3 removes 2 (renamed) and adds 3 → 45 total.
COMBINED_CATEGORIES_V3: dict[str, list[str]] = {
    **{
        k: _REQUIRED_CATEGORIES_V3_UPDATES.get(k, v)
        for k, v in COMBINED_CATEGORIES_V2.items()
        if k not in _REQUIRED_CATEGORIES_V3_REMOVED
    },
    **_REQUIRED_CATEGORIES_V3_NEW,
}

MIN_CATEGORIES_REQUIRED_V3: int = len(COMBINED_CATEGORIES_V3)

#: Allowed final verdicts for Sprint 30 bundles.
ALLOWED_VERDICTS_V3: frozenset[str] = frozenset({
    "SPRINT30_ALL_PRS_PUBLISHED_EVIDENCE_V3_COMPLETE",
    "SPRINT30_PARTIAL_PUBLICATION_EVIDENCE_V3_COMPLETE",
    "SPRINT30_APPROVAL_BLOCKED_PACKAGES_CLEAN_EVIDENCE_V3_COMPLETE",
    "SPRINT30_BLOCKED_PACKAGE_AUDIT_FAILURES",
    "SPRINT30_BLOCKED_SOURCE_STATE",
    "SPRINT30_BLOCKED_EVIDENCE_CONTRACT_V3_FAILED",
    "SPRINT30_REJECTED_UNSAFE_TO_PUBLISH",
})

#: Sprint 29 HEAD commit SHA (short) — must appear in git-log-proof.txt for Sprint 30.
_SPRINT29_HEAD_COMMIT = "ef74d9b"


class StrictEvidenceContractV3(StrictEvidenceContractV2):
    """
    v3 of the strict evidence contract (Sprint 30+).

    Extends v2 with:
    - 45 required categories (vs 44 in v2; reconciles the 44-vs-45 discrepancy).
    - Sprint 29 commit ef74d9b must appear in git-log-proof.txt (replaces Sprint 28 check).
    - Sprint 30 verdicts required in final-verdict.md (replaces Sprint 29 set).
    - source-state-classification.json sprint30_start_state must be CLEAN_FOR_SPRINT_EXECUTION.
    - all-pr-packages-audit-post-cleanup.json packages_with_blocking_flags must be 0.
    """

    def validate_zip(self, zip_path: str | Path) -> ContractResult:
        zip_path = Path(zip_path)
        result = ContractResult(passed=False)

        if not zip_path.exists():
            result.failures.append(f"ZIP file not found: {zip_path}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        if not zip_path.is_absolute():
            result.failures.append(
                f"v3: ZIP path must be absolute for evidence completeness, got: {zip_path}"
            )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                result.file_count = len(names)
                basenames = {Path(n).name for n in names}

                # Presence checks — v3 categories (45 total)
                for category, patterns in COMBINED_CATEGORIES_V3.items():
                    if any(p in basenames for p in patterns):
                        result.categories_found.append(category)
                    else:
                        result.categories_missing.append(category)
                        result.failures.append(
                            f"Missing category '{category}' — "
                            f"expected one of: {patterns}"
                        )

                # Secret scan (all text files)
                for name in names:
                    if name.endswith((".json", ".md", ".txt", ".yaml", ".yml", ".patch", ".log")):
                        try:
                            content = zf.read(name).decode("utf-8", errors="replace")
                            for pattern in SECRET_PATTERNS:
                                if pattern.search(content):
                                    violation = (
                                        f"v3: Possible secret in {name}: "
                                        f"pattern {pattern.pattern}"
                                    )
                                    result.secret_violations.append(violation)
                                    result.failures.append(violation)
                        except Exception:
                            pass

                # v3 content-level checks
                self._validate_content_v3(zf, names, result)

        except zipfile.BadZipFile as e:
            result.failures.append(f"ZIP is invalid/corrupt: {e}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        result.passed = not result.failures
        result.verdict = "BUNDLE_CONTRACT_PASSED" if result.passed else "BUNDLE_CONTRACT_FAILED"
        return result

    # ------------------------------------------------------------------
    # v3 content validation (calls overridden v2 helpers + new v3 checks)
    # ------------------------------------------------------------------

    def _validate_content_v3(
        self,
        zf: zipfile.ZipFile,
        names: list[str],
        result: ContractResult,
    ) -> None:
        name_map: dict[str, str] = {Path(n).name: n for n in names}
        self._check_git_status_final(zf, name_map, result)      # from v2 (unchanged)
        self._check_git_log_proof(zf, name_map, result)          # overridden below
        self._check_final_verdict(zf, name_map, result)          # overridden below
        self._check_test_summary(zf, name_map, result)           # from v2 (unchanged)
        self._check_bundle_contract_report(zf, name_map, result) # from v2 (unchanged)
        self._check_source_state_sprint30_clean(zf, name_map, result)
        self._check_package_audit_no_blocking_flags(zf, name_map, result)

    def _check_git_log_proof(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """Override: v3 requires Sprint 29 HEAD commit ef74d9b in git-log-proof.txt."""
        content = self._read_text(zf, name_map, "git-log-proof.txt")
        if content is None:
            return
        if not content.strip():
            result.failures.append("v3: git-log-proof.txt is empty — no commits recorded.")
            return
        if _SPRINT29_HEAD_COMMIT not in content:
            result.failures.append(
                f"v3: git-log-proof.txt does not contain Sprint 29 HEAD commit "
                f"{_SPRINT29_HEAD_COMMIT}. "
                "Sprint 29 must be committed before Sprint 30 bundle is created."
            )

    def _check_final_verdict(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """Override: v3 uses Sprint 30 allowed verdicts."""
        content = self._read_text(zf, name_map, "final-verdict.md")
        if content is None:
            return
        if "IN_PROGRESS" in content.upper():
            result.failures.append(
                "v3: final-verdict.md contains 'IN_PROGRESS' — sprint is not complete."
            )
            return
        if not any(v in content for v in ALLOWED_VERDICTS_V3):
            result.failures.append(
                f"v3: final-verdict.md does not contain any allowed Sprint 30 verdict. "
                f"Allowed: {sorted(ALLOWED_VERDICTS_V3)}"
            )

    def _check_source_state_sprint30_clean(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v3: source-state-classification.json must confirm clean sprint start."""
        content = self._read_text(zf, name_map, "source-state-classification.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append("v3: source-state-classification.json is not valid JSON.")
            return
        state = data.get("sprint30_start_state", "")
        if state != "CLEAN_FOR_SPRINT_EXECUTION":
            result.failures.append(
                f"v3: source-state-classification.json sprint30_start_state is '{state}' — "
                "must be 'CLEAN_FOR_SPRINT_EXECUTION' to confirm no source modifications at sprint start."
            )

    def _check_package_audit_no_blocking_flags(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v3: all-pr-packages-audit-post-cleanup.json must report 0 packages with blocking flags."""
        content = self._read_text(zf, name_map, "all-pr-packages-audit-post-cleanup.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append(
                "v3: all-pr-packages-audit-post-cleanup.json is not valid JSON."
            )
            return
        blocking = data.get("summary", {}).get("packages_with_blocking_flags", -1)
        if blocking != 0:
            result.failures.append(
                f"v3: all-pr-packages-audit-post-cleanup.json packages_with_blocking_flags={blocking} — "
                "must be 0 before publication. Clean all bin/obj artifacts first."
            )


def contract_definition_v3() -> dict:
    """Return the v3 bundle contract definition as a serialisable dict."""
    return {
        "contract_version": "3.0.0",
        "sprint": "sprint30+",
        "description": (
            "Strict evidence contract v3 for LowCode sprint bundles. "
            "Validates category presence, state correctness, package audit cleanliness, "
            "and source-state classification. "
            "45 categories (reconciles 44-vs-45 discrepancy from v2). "
            "Sprint 30 verdicts required."
        ),
        "required_categories": {
            cat: patterns for cat, patterns in COMBINED_CATEGORIES_V3.items()
        },
        "min_categories_required": MIN_CATEGORIES_REQUIRED_V3,
        "content_checks_enabled": True,
        "content_checks": [
            "git-status-final.txt: no staged source/test/config files",
            f"git-log-proof.txt: must contain Sprint 29 HEAD {_SPRINT29_HEAD_COMMIT}",
            "final-verdict.md: must contain an allowed Sprint 30 verdict",
            "test-summary.json: failed==0 and passed>0",
            "bundle-contract-validation-report.json: passed=true",
            "source-state-classification.json: sprint30_start_state==CLEAN_FOR_SPRINT_EXECUTION",
            "all-pr-packages-audit-post-cleanup.json: packages_with_blocking_flags==0",
        ],
        "category_count_reconciliation": {
            "v2_categories": MIN_CATEGORIES_REQUIRED_V2,
            "v3_categories": MIN_CATEGORIES_REQUIRED_V3,
            "categories_removed_from_v2": sorted(_REQUIRED_CATEGORIES_V3_REMOVED),
            "categories_added_in_v3": sorted(_REQUIRED_CATEGORIES_V3_NEW.keys()),
            "note": "v2 had 44 categories (docstring said 45 — that was wrong). v3 has 45.",
        },
        "secret_scanning_enabled": True,
        "secret_patterns": [p.pattern for p in SECRET_PATTERNS],
        "allowed_verdicts": sorted(ALLOWED_VERDICTS_V3),
        "failure_verdict": "BUNDLE_CONTRACT_FAILED",
        "pass_verdict": "BUNDLE_CONTRACT_PASSED",
    }
