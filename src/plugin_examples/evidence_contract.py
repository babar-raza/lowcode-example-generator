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


# ---------------------------------------------------------------------------
# Contract v4 — PR count consistency, Security inventory, staged-package
#               deletion check, Sprint 31 verdicts (Sprint 31+)
# ---------------------------------------------------------------------------

#: Categories removed from v3 (renamed to reflect sprint30 content).
_REQUIRED_CATEGORIES_V4_REMOVED: frozenset[str] = frozenset({
    "sprint29_commit_proof",
    "sprint29_reconciliation",
})

#: Pattern updates for v4 (key kept, patterns updated).
_REQUIRED_CATEGORIES_V4_UPDATES: dict[str, list[str]] = {
    "taskcard_state": ["taskcard-state-after-sprint31.json"],
}

#: New categories in v4: Sprint 30 commit proof, Security inventory,
#: PR package count reconciliation, PR#8/PR#9 clean audits.
_REQUIRED_CATEGORIES_V4_NEW: dict[str, list[str]] = {
    "sprint30_commit_proof": ["sprint30-commit-proof.json"],
    "sprint30_reconciliation": ["sprint30-bundle-vs-commit-reconciliation.md"],
    "security_inventory": ["pdf-security-inventory-reconciliation.json"],
    "pr_package_count_reconciliation": ["pdf-pr-package-count-reconciliation.json"],
    "pr8_clean_audit": ["pdf-pr8-clean-final-audit.json"],
    "pr9_clean_audit": ["pdf-pr9-clean-final-audit.json"],
}

#: Combined v4 categories: v3 (minus removed, with updates) + new.
#: v3 had 45 categories; v4 removes 2 (renamed) and adds 6 → 49 total.
COMBINED_CATEGORIES_V4: dict[str, list[str]] = {
    **{
        k: _REQUIRED_CATEGORIES_V4_UPDATES.get(k, v)
        for k, v in COMBINED_CATEGORIES_V3.items()
        if k not in _REQUIRED_CATEGORIES_V4_REMOVED
    },
    **_REQUIRED_CATEGORIES_V4_NEW,
}

MIN_CATEGORIES_REQUIRED_V4: int = len(COMBINED_CATEGORIES_V4)

#: Allowed final verdicts for Sprint 31 bundles.
ALLOWED_VERDICTS_V4: frozenset[str] = frozenset({
    "SPRINT31_ALL_PRS_PUBLISHED_EVIDENCE_V4_COMPLETE",
    "SPRINT31_PARTIAL_PUBLICATION_EVIDENCE_V4_COMPLETE",
    "SPRINT31_APPROVAL_BLOCKED_SECURITY_RECONCILED_EVIDENCE_V4_COMPLETE",
    "SPRINT31_BLOCKED_PR_COUNT_INCONSISTENCY",
    "SPRINT31_BLOCKED_SECURITY_INVENTORY_UNRESOLVED",
    "SPRINT31_BLOCKED_EVIDENCE_CONTRACT_V4_FAILED",
    "SPRINT31_REJECTED_UNSAFE_TO_PUBLISH",
})

#: Sprint 30 HEAD commit SHA (short) — must appear in git-log-proof.txt for Sprint 31.
_SPRINT30_HEAD_COMMIT = "e379cdf"

#: Pattern to detect staged workspace/pr-dry-run/ package deletions in git-status-final.txt.
#: Matches lines like 'D  workspace/pr-dry-run/pdf-controlled-pilot-pr7/...'
_STAGED_PACKAGE_DELETION_PATTERN = re.compile(
    r"^[AMDRC][AMDRC?! ]\s+workspace/pr-dry-run/",
    re.MULTILINE,
)


class StrictEvidenceContractV4(StrictEvidenceContractV3):
    """
    v4 of the strict evidence contract (Sprint 31+).

    Extends v3 with:
    - 49 required categories (vs 45 in v3; removes sprint29 entries, adds 6 sprint31 entries).
    - Sprint 30 HEAD commit e379cdf must appear in git-log-proof.txt (replaces Sprint 29 check).
    - Sprint 31 verdicts required in final-verdict.md (replaces Sprint 30 set).
    - source-state-classification.json sprint31_start_state must be CLEAN_FOR_SPRINT_EXECUTION.
    - pdf-pr-package-count-reconciliation.json total_pr_ready must equal 14.
    - git-status-final.txt must not contain staged workspace/pr-dry-run/ deletions.
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
                f"v4: ZIP path must be absolute for evidence completeness, got: {zip_path}"
            )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                result.file_count = len(names)
                basenames = {Path(n).name for n in names}

                # Presence checks — v4 categories (49 total)
                for category, patterns in COMBINED_CATEGORIES_V4.items():
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
                                        f"v4: Possible secret in {name}: "
                                        f"pattern {pattern.pattern}"
                                    )
                                    result.secret_violations.append(violation)
                                    result.failures.append(violation)
                        except Exception:
                            pass

                # v4 content-level checks
                self._validate_content_v4(zf, names, result)

        except zipfile.BadZipFile as e:
            result.failures.append(f"ZIP is invalid/corrupt: {e}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        result.passed = not result.failures
        result.verdict = "BUNDLE_CONTRACT_PASSED" if result.passed else "BUNDLE_CONTRACT_FAILED"
        return result

    # ------------------------------------------------------------------
    # v4 content validation (calls overridden helpers + new v4 checks)
    # ------------------------------------------------------------------

    def _validate_content_v4(
        self,
        zf: zipfile.ZipFile,
        names: list[str],
        result: ContractResult,
    ) -> None:
        name_map: dict[str, str] = {Path(n).name: n for n in names}
        self._check_git_status_final(zf, name_map, result)            # from v2 (unchanged)
        self._check_staged_package_deletions(zf, name_map, result)    # new v4
        self._check_git_log_proof(zf, name_map, result)                # overridden below
        self._check_final_verdict(zf, name_map, result)                # overridden below
        self._check_test_summary(zf, name_map, result)                 # from v2 (unchanged)
        self._check_bundle_contract_report(zf, name_map, result)       # from v2 (unchanged)
        self._check_source_state_sprint31_clean(zf, name_map, result)  # new v4
        self._check_package_audit_no_blocking_flags(zf, name_map, result)   # from v3 (unchanged)
        self._check_pr_package_count_consistency(zf, name_map, result)      # new v4

    def _check_git_log_proof(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """Override: v4 requires Sprint 30 HEAD commit e379cdf in git-log-proof.txt."""
        content = self._read_text(zf, name_map, "git-log-proof.txt")
        if content is None:
            return
        if not content.strip():
            result.failures.append("v4: git-log-proof.txt is empty — no commits recorded.")
            return
        if _SPRINT30_HEAD_COMMIT not in content:
            result.failures.append(
                f"v4: git-log-proof.txt does not contain Sprint 30 HEAD commit "
                f"{_SPRINT30_HEAD_COMMIT}. "
                "Sprint 30 must be committed before Sprint 31 bundle is created."
            )

    def _check_final_verdict(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """Override: v4 uses Sprint 31 allowed verdicts."""
        content = self._read_text(zf, name_map, "final-verdict.md")
        if content is None:
            return
        if "IN_PROGRESS" in content.upper():
            result.failures.append(
                "v4: final-verdict.md contains 'IN_PROGRESS' — sprint is not complete."
            )
            return
        if not any(v in content for v in ALLOWED_VERDICTS_V4):
            result.failures.append(
                f"v4: final-verdict.md does not contain any allowed Sprint 31 verdict. "
                f"Allowed: {sorted(ALLOWED_VERDICTS_V4)}"
            )

    def _check_source_state_sprint31_clean(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v4: source-state-classification.json must confirm clean sprint 31 start."""
        content = self._read_text(zf, name_map, "source-state-classification.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append("v4: source-state-classification.json is not valid JSON.")
            return
        state = data.get("sprint31_start_state", "")
        if state != "CLEAN_FOR_SPRINT_EXECUTION":
            result.failures.append(
                f"v4: source-state-classification.json sprint31_start_state is '{state}' — "
                "must be 'CLEAN_FOR_SPRINT_EXECUTION' to confirm no source modifications at sprint start."
            )

    def _check_pr_package_count_consistency(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v4: pdf-pr-package-count-reconciliation.json must confirm total_pr_ready==14."""
        content = self._read_text(zf, name_map, "pdf-pr-package-count-reconciliation.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append(
                "v4: pdf-pr-package-count-reconciliation.json is not valid JSON."
            )
            return
        count = data.get(
            "total_pr_ready",
            data.get("pr_ready_count",
            data.get("totals", {}).get("total_examples", -1))
        )
        if count != 14:
            result.failures.append(
                f"v4: pdf-pr-package-count-reconciliation.json total_pr_ready={count} — "
                "must be 14 (PR#3:3 + PR#5:3 + PR#6:3 + PR#7:2 + PR#8:2 + PR#9:1). "
                "PR count contradiction must be resolved before publication."
            )

    def _check_staged_package_deletions(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v4: git-status-final.txt must not contain staged workspace/pr-dry-run/ deletions."""
        content = self._read_text(zf, name_map, "git-status-final.txt")
        if content is None:
            return
        if _STAGED_PACKAGE_DELETION_PATTERN.search(content):
            result.failures.append(
                "v4: git-status-final.txt contains staged workspace/pr-dry-run/ deletions. "
                "PR packages must not be deleted from workspace before publication."
            )


def contract_definition_v4() -> dict:
    """Return the v4 bundle contract definition as a serialisable dict."""
    return {
        "contract_version": "4.0.0",
        "sprint": "sprint31+",
        "description": (
            "Strict evidence contract v4 for LowCode sprint bundles. "
            "Validates category presence, PR count consistency, Security inventory, "
            "staged-package deletion check, and source-state classification. "
            "49 categories (v3 had 45: removes 2 sprint29 entries, adds 6 sprint31 entries). "
            "Sprint 31 verdicts required."
        ),
        "required_categories": {
            cat: patterns for cat, patterns in COMBINED_CATEGORIES_V4.items()
        },
        "min_categories_required": MIN_CATEGORIES_REQUIRED_V4,
        "content_checks_enabled": True,
        "content_checks": [
            "git-status-final.txt: no staged source/test/config files",
            "git-status-final.txt: no staged workspace/pr-dry-run/ deletions",
            f"git-log-proof.txt: must contain Sprint 30 HEAD {_SPRINT30_HEAD_COMMIT}",
            "final-verdict.md: must contain an allowed Sprint 31 verdict",
            "test-summary.json: failed==0 and passed>0",
            "bundle-contract-validation-report.json: passed=true",
            "source-state-classification.json: sprint31_start_state==CLEAN_FOR_SPRINT_EXECUTION",
            "all-pr-packages-audit-post-cleanup.json: packages_with_blocking_flags==0",
            "pdf-pr-package-count-reconciliation.json: total_pr_ready==14",
        ],
        "category_count_reconciliation": {
            "v3_categories": MIN_CATEGORIES_REQUIRED_V3,
            "v4_categories": MIN_CATEGORIES_REQUIRED_V4,
            "categories_removed_from_v3": sorted(_REQUIRED_CATEGORIES_V4_REMOVED),
            "categories_added_in_v4": sorted(_REQUIRED_CATEGORIES_V4_NEW.keys()),
            "note": "v3 had 45 categories. v4 removes 2 (sprint29 entries) and adds 6 (sprint31 entries) → 49.",
        },
        "secret_scanning_enabled": True,
        "secret_patterns": [p.pattern for p in SECRET_PATTERNS],
        "allowed_verdicts": sorted(ALLOWED_VERDICTS_V4),
        "failure_verdict": "BUNDLE_CONTRACT_FAILED",
        "pass_verdict": "BUNDLE_CONTRACT_PASSED",
    }


# ---------------------------------------------------------------------------
# Contract v5 — modified (not only staged) source/test/config enforcement,
#               Sprint 32 release-candidate evidence, target runtime proofs
#               (Sprint 32+)
# ---------------------------------------------------------------------------

#: Categories removed from v4 (renamed to reflect sprint31 content).
_REQUIRED_CATEGORIES_V5_REMOVED: frozenset[str] = frozenset({
    "sprint30_commit_proof",
    "sprint30_reconciliation",
})

#: Pattern updates for v5 (key kept, patterns updated).
_REQUIRED_CATEGORIES_V5_UPDATES: dict[str, list[str]] = {
    "taskcard_state": ["taskcard-state-after-sprint32.json"],
}

#: New categories in v5: Sprint 31 state reconciliation, target runtime proofs,
#: FormImporter version retest, release candidate packet.
_REQUIRED_CATEGORIES_V5_NEW: dict[str, list[str]] = {
    "sprint31_state_reconciliation": ["sprint31-final-state-reconciliation.json"],
    "email_target_runtime_report": ["email-target-runtime-verification-report.json"],
    "slides_target_runtime_report": ["slides-target-runtime-verification-report.json"],
    "formimporter_version_retest": ["pdf-formimporter-latest-version-retest-report.json"],
    "release_candidate_packet_json": ["pdf-release-candidate-publication-packet.json"],
    "release_candidate_packet_md": ["pdf-release-candidate-publication-packet.md"],
}

#: Combined v5 categories: v4 (minus removed, with updates) + new.
#: v4 had 49 categories; v5 removes 2 (sprint30 entries) and adds 6 → 53 total.
COMBINED_CATEGORIES_V5: dict[str, list[str]] = {
    **{
        k: _REQUIRED_CATEGORIES_V5_UPDATES.get(k, v)
        for k, v in COMBINED_CATEGORIES_V4.items()
        if k not in _REQUIRED_CATEGORIES_V5_REMOVED
    },
    **_REQUIRED_CATEGORIES_V5_NEW,
}

MIN_CATEGORIES_REQUIRED_V5: int = len(COMBINED_CATEGORIES_V5)

#: Allowed final verdicts for Sprint 32 bundles.
ALLOWED_VERDICTS_V5: frozenset[str] = frozenset({
    "SPRINT32_PUBLISHED_RELEASE_CANDIDATE_AND_CONTRACT_V5_COMPLETE",
    "SPRINT32_APPROVAL_BLOCKED_RELEASE_CANDIDATE_AND_CONTRACT_V5_COMPLETE",
    "SPRINT32_PARTIAL_PUBLICATION_RELEASE_CANDIDATE_COMPLETE",
    "SPRINT32_BLOCKED_EVIDENCE_CONTRACT_V5_FAILED",
    "SPRINT32_BLOCKED_SOURCE_STATE",
    "SPRINT32_REJECTED_UNSAFE_TO_PUBLISH",
})

#: Sprint 31 HEAD commit SHA (short) — must appear in git-log-proof.txt for Sprint 32.
_SPRINT31_HEAD_COMMIT = "0f44886"

#: Pattern matching any modification (staged or unstaged) to source/test/config files.
#: In `git status --short`, lines are:
#:   'XY path' where X is index status, Y is worktree status.
#:   ' M src/foo.py'  → unstaged modification (Y=M, X=space)
#:   'M  src/foo.py'  → staged modification (X=M, Y=space)
#: V5 rejects BOTH for complete verdicts.
_MODIFIED_SOURCE_PATTERN_V5 = re.compile(
    r"^..\s+(src/|tests/|pipeline/|\.gitignore)",
    re.MULTILINE,
)


class StrictEvidenceContractV5(StrictEvidenceContractV4):
    """
    v5 of the strict evidence contract (Sprint 32+).

    Extends v4 with:
    - 53 required categories (vs 49 in v4; removes sprint30 entries, adds 6 sprint32 entries).
    - Sprint 31 HEAD commit 0f44886 must appear in git-log-proof.txt.
    - Sprint 32 verdicts required in final-verdict.md.
    - source-state-classification.json sprint32_start_state must be CLEAN_FOR_SPRINT_EXECUTION.
    - git-status-final.txt must have NO modified (staged OR unstaged) src/tests/pipeline/.gitignore.
      This closes the Sprint 31 v4 weakness where unstaged source changes passed validation.
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
                f"v5: ZIP path must be absolute for evidence completeness, got: {zip_path}"
            )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                result.file_count = len(names)
                basenames = {Path(n).name for n in names}

                # Presence checks — v5 categories (53 total)
                for category, patterns in COMBINED_CATEGORIES_V5.items():
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
                                        f"v5: Possible secret in {name}: "
                                        f"pattern {pattern.pattern}"
                                    )
                                    result.secret_violations.append(violation)
                                    result.failures.append(violation)
                        except Exception:
                            pass

                # v5 content-level checks
                self._validate_content_v5(zf, names, result)

        except zipfile.BadZipFile as e:
            result.failures.append(f"ZIP is invalid/corrupt: {e}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        result.passed = not result.failures
        result.verdict = "BUNDLE_CONTRACT_PASSED" if result.passed else "BUNDLE_CONTRACT_FAILED"
        return result

    # ------------------------------------------------------------------
    # v5 content validation
    # ------------------------------------------------------------------

    def _validate_content_v5(
        self,
        zf: zipfile.ZipFile,
        names: list[str],
        result: ContractResult,
    ) -> None:
        name_map: dict[str, str] = {Path(n).name: n for n in names}
        self._check_git_status_no_modified_source(zf, name_map, result)   # new v5 (replaces v4 staged check)
        self._check_staged_package_deletions(zf, name_map, result)         # from v4 (unchanged)
        self._check_git_log_proof(zf, name_map, result)                     # overridden below
        self._check_final_verdict(zf, name_map, result)                     # overridden below
        self._check_test_summary(zf, name_map, result)                      # from v2 (unchanged)
        self._check_bundle_contract_report(zf, name_map, result)            # from v2 (unchanged)
        self._check_source_state_sprint32_clean(zf, name_map, result)       # new v5
        self._check_package_audit_no_blocking_flags(zf, name_map, result)   # from v3 (unchanged)
        self._check_pr_package_count_consistency(zf, name_map, result)      # from v4 (unchanged)

    def _check_git_status_no_modified_source(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v5: git-status-final.txt must have NO modified src/tests/pipeline/.gitignore.

        This closes the Sprint 31 V4 weakness: V4 only checked for STAGED source files
        (first-column modification). V5 rejects any modification — staged or unstaged.
        """
        content = self._read_text(zf, name_map, "git-status-final.txt")
        if content is None:
            return
        match = _MODIFIED_SOURCE_PATTERN_V5.search(content)
        if match:
            result.failures.append(
                f"v5: git-status-final.txt contains modified source/test/config file: "
                f"'{match.group(0).strip()}'. "
                "Complete verdicts require all src/, tests/, pipeline/, and .gitignore "
                "changes to be committed before bundle creation. "
                "(Sprint 31 V4 weakness: V4 only blocked STAGED changes; "
                "V5 blocks any modification.)"
            )

    def _check_git_log_proof(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """Override: v5 requires Sprint 31 HEAD commit 0f44886 in git-log-proof.txt."""
        content = self._read_text(zf, name_map, "git-log-proof.txt")
        if content is None:
            return
        if not content.strip():
            result.failures.append("v5: git-log-proof.txt is empty — no commits recorded.")
            return
        if _SPRINT31_HEAD_COMMIT not in content:
            result.failures.append(
                f"v5: git-log-proof.txt does not contain Sprint 31 HEAD commit "
                f"{_SPRINT31_HEAD_COMMIT}. "
                "Sprint 31 must be committed before Sprint 32 bundle is created."
            )

    def _check_final_verdict(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """Override: v5 uses Sprint 32 allowed verdicts."""
        content = self._read_text(zf, name_map, "final-verdict.md")
        if content is None:
            return
        if "IN_PROGRESS" in content.upper():
            result.failures.append(
                "v5: final-verdict.md contains 'IN_PROGRESS' — sprint is not complete."
            )
            return
        if not any(v in content for v in ALLOWED_VERDICTS_V5):
            result.failures.append(
                f"v5: final-verdict.md does not contain any allowed Sprint 32 verdict. "
                f"Allowed: {sorted(ALLOWED_VERDICTS_V5)}"
            )

    def _check_source_state_sprint32_clean(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v5: source-state-classification.json must confirm clean sprint 32 start."""
        content = self._read_text(zf, name_map, "source-state-classification.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append("v5: source-state-classification.json is not valid JSON.")
            return
        state = data.get("sprint32_start_state", "")
        if state != "CLEAN_FOR_SPRINT_EXECUTION":
            result.failures.append(
                f"v5: source-state-classification.json sprint32_start_state is '{state}' — "
                "must be 'CLEAN_FOR_SPRINT_EXECUTION'."
            )


def contract_definition_v5() -> dict:
    """Return the v5 bundle contract definition as a serialisable dict."""
    return {
        "contract_version": "5.0.0",
        "sprint": "sprint32+",
        "description": (
            "Strict evidence contract v5 for LowCode sprint bundles. "
            "Closes Sprint 31 V4 weakness: rejects bundles where src/tests/pipeline/.gitignore "
            "are modified (staged OR unstaged) in git-status-final.txt. "
            "53 categories (v4 had 49: removes 2 sprint30 entries, adds 6 sprint32 entries). "
            "Sprint 32 verdicts required."
        ),
        "required_categories": {
            cat: patterns for cat, patterns in COMBINED_CATEGORIES_V5.items()
        },
        "min_categories_required": MIN_CATEGORIES_REQUIRED_V5,
        "content_checks_enabled": True,
        "content_checks": [
            "git-status-final.txt: no modified (staged OR unstaged) src/tests/pipeline/.gitignore (V5 new — closes V4 weakness)",
            "git-status-final.txt: no staged workspace/pr-dry-run/ deletions",
            f"git-log-proof.txt: must contain Sprint 31 HEAD {_SPRINT31_HEAD_COMMIT}",
            "final-verdict.md: must contain an allowed Sprint 32 verdict",
            "test-summary.json: failed==0 and passed>0",
            "bundle-contract-validation-report.json: passed=true",
            "source-state-classification.json: sprint32_start_state==CLEAN_FOR_SPRINT_EXECUTION",
            "all-pr-packages-audit-post-cleanup.json: packages_with_blocking_flags==0",
            "pdf-pr-package-count-reconciliation.json: total_pr_ready==14",
        ],
        "category_count_reconciliation": {
            "v4_categories": MIN_CATEGORIES_REQUIRED_V4,
            "v5_categories": MIN_CATEGORIES_REQUIRED_V5,
            "categories_removed_from_v4": sorted(_REQUIRED_CATEGORIES_V5_REMOVED),
            "categories_added_in_v5": sorted(_REQUIRED_CATEGORIES_V5_NEW.keys()),
            "note": "v4 had 49. v5 removes 2 (sprint30 entries) and adds 6 (sprint32 entries) → 53.",
        },
        "secret_scanning_enabled": True,
        "secret_patterns": [p.pattern for p in SECRET_PATTERNS],
        "allowed_verdicts": sorted(ALLOWED_VERDICTS_V5),
        "failure_verdict": "BUNDLE_CONTRACT_FAILED",
        "pass_verdict": "BUNDLE_CONTRACT_PASSED",
    }


# ---------------------------------------------------------------------------
# Contract v6 — cross-file verdict consistency, bundle identity validation,
#               families-needing-work accuracy, Words SOT classification,
#               dirty-artifact policy formalization, scoreboard consistency
#               (Sprint 33+)
# ---------------------------------------------------------------------------

#: Categories removed from v5 (sprint31 reconciliation replaced by sprint32 reconciliation).
_REQUIRED_CATEGORIES_V6_REMOVED: frozenset[str] = frozenset({
    "sprint31_state_reconciliation",
})

#: Pattern updates for v6 (key kept, patterns updated).
_REQUIRED_CATEGORIES_V6_UPDATES: dict[str, list[str]] = {
    "taskcard_state": ["taskcard-state-after-sprint33.json"],
}

#: New categories in v6: Sprint 32 state reconciliation, dirty-artifact policy,
#: merge-mode decision/result, Words SOT, Email/Slides scoreboard cleanup,
#: FormImporter version watch, new family discovery, RC packet v2, V6 impl report.
_REQUIRED_CATEGORIES_V6_NEW: dict[str, list[str]] = {
    "sprint32_state_reconciliation": ["sprint32-final-state-reconciliation.json"],
    "dirty_artifact_policy": ["dirty-artifact-policy-report.json"],
    "merge_mode_decision": ["merge-mode-decision.json"],
    "merge_mode_result": ["merge-mode-result.json"],
    "words_sot_classification": ["words-full-sot-classification-report.json"],
    "words_denominator_update": ["words-denominator-update-report.json"],
    "words_backlog_closeout": ["words-backlog-closeout-plan.md"],
    "email_scoreboard_cleanup": ["email-scoreboard-cleanup-report.json"],
    "slides_scoreboard_cleanup": ["slides-scoreboard-cleanup-report.json"],
    "formimporter_version_watch": ["pdf-formimporter-version-watch-report.json"],
    "new_family_discovery": ["new-lowcode-family-discovery-report.json"],
    "next_family_plan": ["next-family-launch-candidate-plan.md"],
    "release_candidate_packet_v2_md": ["pdf-release-candidate-publication-packet-v2.md"],
    "release_candidate_packet_v2_json": ["pdf-release-candidate-publication-packet-v2.json"],
    "evidence_contract_v6_impl": ["evidence-contract-v6-implementation-report.json"],
}

#: Combined v6 categories: v5 (minus removed, with updates) + new.
#: v5 had 53 categories; v6 removes 1 (sprint31 entry) and adds 15 → 67 total.
COMBINED_CATEGORIES_V6: dict[str, list[str]] = {
    **{
        k: _REQUIRED_CATEGORIES_V6_UPDATES.get(k, v)
        for k, v in COMBINED_CATEGORIES_V5.items()
        if k not in _REQUIRED_CATEGORIES_V6_REMOVED
    },
    **_REQUIRED_CATEGORIES_V6_NEW,
}

MIN_CATEGORIES_REQUIRED_V6: int = len(COMBINED_CATEGORIES_V6)

#: Allowed final verdicts for Sprint 33 bundles.
ALLOWED_VERDICTS_V6: frozenset[str] = frozenset({
    # Sprint 33 verdicts
    "SPRINT33_PUBLISHED_MERGED_AND_PORTFOLIO_RELEASE_CANDIDATE_COMPLETE",
    "SPRINT33_PUBLISHED_RELEASE_CANDIDATE_COMPLETE_MERGE_BLOCKED",
    "SPRINT33_APPROVAL_BLOCKED_BUT_PORTFOLIO_RELEASE_CANDIDATE_ADVANCED",
    "SPRINT33_PARTIAL_PUBLICATION_AND_PORTFOLIO_ADVANCED",
    "SPRINT33_BLOCKED_EVIDENCE_CONTRACT_V6_FAILED",
    "SPRINT33_BLOCKED_SOURCE_STATE",
    "SPRINT33_REJECTED_UNSAFE_TO_PUBLISH",
    # Sprint 34 verdicts (V6 contract extended to cover Sprint 34 bundles)
    "SPRINT34_APPROVAL_BLOCKED_MEGA_SWARM_SYSTEM_BACKLOG_RESOLVED_NEW_FAMILY_DISCOVERY_COMPLETE",
    "SPRINT34_PUBLISHED_MERGED_AND_PORTFOLIO_RELEASE_CANDIDATE_COMPLETE",
    "SPRINT34_APPROVAL_BLOCKED_ALL_PACKAGES_VERIFIED",
    "SPRINT34_BLOCKED_EVIDENCE_CONTRACT_V6_FAILED",
    "SPRINT34_BLOCKED_SOURCE_STATE",
})

#: Sprint 32 HEAD commit SHA (short) — must appear in git-log-proof.txt for Sprint 33.
_SPRINT32_HEAD_COMMIT = "b7665d4"


class StrictEvidenceContractV6(StrictEvidenceContractV5):
    """
    v6 of the strict evidence contract (Sprint 33+).

    Extends v5 with:
    - 67 required categories (vs 53 in v5; removes 1 sprint31 entry, adds 15 sprint33 entries).
    - Sprint 32 HEAD commit b7665d4 must appear in git-log-proof.txt.
    - Sprint 33 verdicts required in final-verdict.md.
    - Cross-file verdict consistency: final-verdict.md must match final-state-summary.yaml.
    - Bundle identity: bundle-contract-validation-report.json bundle_bytes > 0 and
      bundle_file must match the actual ZIP filename.
    - families-needing-launch-work.json must not list Email/Slides as needing work
      (Sprint 32 verified them; stale entries are a contract violation).
    - Words SOT: words-full-sot-classification-report.json must set workflow_root_count > 0.
    - Scoreboard published total must be consistent across scoreboard and release-state.
    - PR#7 package must declare Security and FormFlattener examples.
    - dirty-artifact-policy-report.json verdict must be DIRTY_ARTIFACT_POLICY_FORMALIZED
      or DIRTY_ARTIFACT_POLICY_CLEAN.
    - source-state-classification.json sprint33_start_state must be
      CLEAN_FOR_SPRINT_EXECUTION.
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
                f"v6: ZIP path must be absolute for evidence completeness, got: {zip_path}"
            )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                result.file_count = len(names)
                basenames = {Path(n).name for n in names}

                # Presence checks — v6 categories (67 total)
                for category, patterns in COMBINED_CATEGORIES_V6.items():
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
                                        f"v6: Possible secret in {name}: "
                                        f"pattern {pattern.pattern}"
                                    )
                                    result.secret_violations.append(violation)
                                    result.failures.append(violation)
                        except Exception:
                            pass

                # v6 content-level checks
                self._validate_content_v6(zf, names, result, zip_path)

        except zipfile.BadZipFile as e:
            result.failures.append(f"ZIP is invalid/corrupt: {e}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        result.passed = not result.failures
        result.verdict = "BUNDLE_CONTRACT_PASSED" if result.passed else "BUNDLE_CONTRACT_FAILED"
        return result

    # ------------------------------------------------------------------
    # v6 content validation
    # ------------------------------------------------------------------

    def _validate_content_v6(
        self,
        zf: zipfile.ZipFile,
        names: list[str],
        result: ContractResult,
        zip_path: Path,
    ) -> None:
        name_map: dict[str, str] = {Path(n).name: n for n in names}
        self._check_git_status_no_modified_source(zf, name_map, result)   # from v5
        self._check_staged_package_deletions(zf, name_map, result)         # from v4
        self._check_git_log_proof(zf, name_map, result)                     # overridden below
        self._check_final_verdict(zf, name_map, result)                     # overridden below
        self._check_test_summary(zf, name_map, result)                      # from v2
        self._check_bundle_contract_report(zf, name_map, result)            # from v2
        self._check_source_state_sprint33_clean(zf, name_map, result)       # new v6
        self._check_package_audit_no_blocking_flags(zf, name_map, result)   # from v3
        self._check_pr_package_count_consistency(zf, name_map, result)      # from v4
        # V6 new checks
        self._check_v6_bundle_identity(zf, name_map, result, zip_path)
        self._check_v6_cross_file_verdict(zf, name_map, result)
        self._check_v6_families_needing_work_accuracy(zf, name_map, result)
        self._check_v6_words_sot(zf, name_map, result)
        self._check_v6_scoreboard_consistency(zf, name_map, result)
        self._check_v6_pr7_has_security(zf, name_map, result)
        self._check_v6_dirty_artifact_policy(zf, name_map, result)

    def _check_git_log_proof(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """Override: v6 requires Sprint 32 HEAD commit b7665d4 in git-log-proof.txt."""
        content = self._read_text(zf, name_map, "git-log-proof.txt")
        if content is None:
            return
        if not content.strip():
            result.failures.append("v6: git-log-proof.txt is empty — no commits recorded.")
            return
        if _SPRINT32_HEAD_COMMIT not in content:
            result.failures.append(
                f"v6: git-log-proof.txt does not contain Sprint 32 HEAD commit "
                f"{_SPRINT32_HEAD_COMMIT}. "
                "Sprint 32 must be committed before Sprint 33 bundle is created."
            )

    def _check_final_verdict(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """Override: v6 uses Sprint 33 allowed verdicts."""
        content = self._read_text(zf, name_map, "final-verdict.md")
        if content is None:
            return
        if "IN_PROGRESS" in content.upper():
            result.failures.append(
                "v6: final-verdict.md contains 'IN_PROGRESS' — sprint is not complete."
            )
            return
        if not any(v in content for v in ALLOWED_VERDICTS_V6):
            result.failures.append(
                f"v6: final-verdict.md does not contain any allowed Sprint 33 verdict. "
                f"Allowed: {sorted(ALLOWED_VERDICTS_V6)}"
            )

    def _check_source_state_sprint33_clean(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v6: source-state-classification.json must confirm clean sprint 33 start."""
        content = self._read_text(zf, name_map, "source-state-classification.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append("v6: source-state-classification.json is not valid JSON.")
            return
        state = data.get("sprint33_start_state", "")
        if state != "CLEAN_FOR_SPRINT_EXECUTION":
            result.failures.append(
                f"v6: source-state-classification.json sprint33_start_state is '{state}' — "
                "must be 'CLEAN_FOR_SPRINT_EXECUTION'."
            )

    def _check_v6_bundle_identity(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
        zip_path: Path,
    ) -> None:
        """v6: bundle-contract-validation-report.json must have bundle_bytes > 0
        and bundle_file must match the actual ZIP filename being validated."""
        content = self._read_text(zf, name_map, "bundle-contract-validation-report.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append(
                "v6: bundle-contract-validation-report.json is not valid JSON."
            )
            return
        bundle_bytes = data.get("bundle_bytes", 0)
        if not isinstance(bundle_bytes, (int, float)) or bundle_bytes <= 0:
            result.failures.append(
                f"v6: bundle-contract-validation-report.json bundle_bytes={bundle_bytes!r} — "
                "must be > 0. Bootstrap report generated before bundle was built."
            )
        bundle_file = data.get("bundle_file", "")
        actual_name = zip_path.name
        if bundle_file and bundle_file != actual_name:
            result.failures.append(
                f"v6: bundle-contract-validation-report.json bundle_file='{bundle_file}' "
                f"does not match actual ZIP filename '{actual_name}'. "
                "Report must reference the bundle it describes."
            )

    def _check_v6_cross_file_verdict(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v6: final-verdict.md and final-state-summary.yaml must agree on the sprint verdict."""
        md_content = self._read_text(zf, name_map, "final-verdict.md")
        yaml_content = self._read_text(zf, name_map, "final-state-summary.yaml")
        if md_content is None or yaml_content is None:
            return
        # Extract verdict from md: look for the first SPRINT33_ token
        md_verdict = None
        for v in ALLOWED_VERDICTS_V6:
            if v in md_content:
                md_verdict = v
                break
        # Extract verdict from yaml: look for verdict: field
        yaml_verdict = None
        for line in yaml_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("verdict:"):
                yaml_verdict = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                break
        if md_verdict is None or yaml_verdict is None:
            return  # already caught by other checks
        if md_verdict != yaml_verdict:
            result.failures.append(
                f"v6: Cross-file verdict mismatch — "
                f"final-verdict.md='{md_verdict}' but "
                f"final-state-summary.yaml verdict='{yaml_verdict}'. "
                "Both files must record the same sprint verdict."
            )

    def _check_v6_families_needing_work_accuracy(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v6: families-needing-launch-work.json must not list Email or Slides
        as needing work — Sprint 32 runtime-verified them as PILOT_COMPLETE."""
        content = self._read_text(zf, name_map, "families-needing-launch-work.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append(
                "v6: families-needing-launch-work.json is not valid JSON."
            )
            return
        # Accept list or dict with families_needing_work key
        if isinstance(data, list):
            families = [str(f).lower() for f in data]
        elif isinstance(data, dict):
            families = [
                str(f).lower()
                for f in data.get("families_needing_work", data.get("families", []))
            ]
        else:
            families = []
        stale = [f for f in families if f in ("email", "slides")]
        if stale:
            result.failures.append(
                f"v6: families-needing-launch-work.json stale — lists {stale} as needing work. "
                "Sprint 32 runtime-verified Email (BUILD+RUN PASS, HTML 2002 bytes) and "
                "Slides (all 3 examples BUILD+RUN PASS). Update to reflect PILOT_COMPLETE status."
            )

    def _check_v6_words_sot(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v6: words-full-sot-classification-report.json must have workflow_root_count > 0."""
        content = self._read_text(zf, name_map, "words-full-sot-classification-report.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append(
                "v6: words-full-sot-classification-report.json is not valid JSON."
            )
            return
        wrc = data.get("workflow_root_count")
        if wrc is None:
            result.failures.append(
                "v6: words-full-sot-classification-report.json workflow_root_count is null. "
                "TC-WORDS-01 must complete: classify all 25 Words LowCode types and set "
                "workflow_root_count to a positive integer."
            )
        elif not isinstance(wrc, int) or wrc <= 0:
            result.failures.append(
                f"v6: words-full-sot-classification-report.json workflow_root_count={wrc!r} — "
                "must be a positive integer."
            )

    def _check_v6_scoreboard_consistency(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v6: all-family-launch-scoreboard.json total_published_examples must match
        release-state-reconciliation-report.json published total."""
        scoreboard_content = self._read_text(
            zf, name_map, "all-family-launch-scoreboard.json"
        )
        release_content = self._read_text(
            zf, name_map, "release-state-reconciliation-report.json"
        )
        if scoreboard_content is None or release_content is None:
            return
        try:
            scoreboard = json.loads(scoreboard_content)
            release = json.loads(release_content)
        except Exception:
            return
        sb_total = (
            scoreboard.get("portfolio_summary", {}).get("total_published_examples")
        )
        rc_total = (
            release.get("published_count_reconciliation", {}).get("total")
        )
        if sb_total is None or rc_total is None:
            return
        if sb_total != rc_total:
            result.failures.append(
                f"v6: Scoreboard consistency failure — "
                f"all-family-launch-scoreboard.json total_published_examples={sb_total} "
                f"but release-state-reconciliation-report.json total={rc_total}. "
                "Both files must report the same published count."
            )

    def _check_v6_pr7_has_security(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v6: pdf-release-candidate-publication-packet-v2.json PR#7 must declare
        Security and FormFlattener examples."""
        content = self._read_text(
            zf, name_map, "pdf-release-candidate-publication-packet-v2.json"
        )
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append(
                "v6: pdf-release-candidate-publication-packet-v2.json is not valid JSON."
            )
            return
        pr_packages = data.get("pr_packages", [])
        pr7 = next((p for p in pr_packages if p.get("pr_number") == 7), None)
        if pr7 is None:
            result.failures.append(
                "v6: pdf-release-candidate-publication-packet-v2.json has no PR#7 entry."
            )
            return
        examples = [str(e).lower() for e in pr7.get("examples", [])]
        missing = []
        if not any("security" in e for e in examples):
            missing.append("security")
        if not any("formflattener" in e or "form-flattener" in e for e in examples):
            missing.append("form-flattener")
        if missing:
            result.failures.append(
                f"v6: PR#7 in pdf-release-candidate-publication-packet-v2.json is missing "
                f"required examples: {missing}. PR#7 must include Security and FormFlattener."
            )

    def _check_v6_dirty_artifact_policy(
        self,
        zf: zipfile.ZipFile,
        name_map: dict[str, str],
        result: ContractResult,
    ) -> None:
        """v6: dirty-artifact-policy-report.json verdict must be
        DIRTY_ARTIFACT_POLICY_FORMALIZED or DIRTY_ARTIFACT_POLICY_CLEAN."""
        content = self._read_text(zf, name_map, "dirty-artifact-policy-report.json")
        if content is None:
            return
        try:
            data = json.loads(content)
        except Exception:
            result.failures.append(
                "v6: dirty-artifact-policy-report.json is not valid JSON."
            )
            return
        verdict = data.get("verdict", "")
        allowed = {"DIRTY_ARTIFACT_POLICY_FORMALIZED", "DIRTY_ARTIFACT_POLICY_CLEAN"}
        if verdict not in allowed:
            result.failures.append(
                f"v6: dirty-artifact-policy-report.json verdict='{verdict}' — "
                f"must be one of {sorted(allowed)}."
            )


def contract_definition_v6() -> dict:
    """Return the v6 bundle contract definition as a serialisable dict."""
    return {
        "contract_version": "6.0.0",
        "sprint": "sprint33+",
        "description": (
            "Strict evidence contract v6 for LowCode sprint bundles. "
            "Closes Sprint 32 V5 weaknesses: cross-file verdict consistency, "
            "bundle identity (bundle_bytes > 0, bundle_file matches ZIP), "
            "families-needing-launch-work staleness detection, Words SOT null guard, "
            "scoreboard count consistency, PR#7 content enforcement, "
            "and dirty-artifact policy formalization. "
            "67 categories (v5 had 53: removes 1 sprint31 entry, adds 15 sprint33 entries). "
            "Sprint 33 verdicts required."
        ),
        "required_categories": {
            cat: patterns for cat, patterns in COMBINED_CATEGORIES_V6.items()
        },
        "min_categories_required": MIN_CATEGORIES_REQUIRED_V6,
        "content_checks_enabled": True,
        "content_checks": [
            "git-status-final.txt: no modified (staged OR unstaged) src/tests/pipeline/.gitignore",
            "git-status-final.txt: no staged workspace/pr-dry-run/ deletions",
            f"git-log-proof.txt: must contain Sprint 32 HEAD {_SPRINT32_HEAD_COMMIT}",
            "final-verdict.md: must contain an allowed Sprint 33 verdict",
            "test-summary.json: failed==0 and passed>0",
            "bundle-contract-validation-report.json: passed=true AND bundle_bytes > 0 (V6 new)",
            "bundle-contract-validation-report.json: bundle_file matches actual ZIP (V6 new)",
            "source-state-classification.json: sprint33_start_state==CLEAN_FOR_SPRINT_EXECUTION",
            "all-pr-packages-audit-post-cleanup.json: packages_with_blocking_flags==0",
            "pdf-pr-package-count-reconciliation.json: total_pr_ready==14",
            "final-verdict.md vs final-state-summary.yaml: verdict must match (V6 new)",
            "families-needing-launch-work.json: Email/Slides not listed as needing work (V6 new)",
            "words-full-sot-classification-report.json: workflow_root_count > 0 (V6 new)",
            "scoreboard total_published == release-state total (V6 new)",
            "PR#7 must contain Security + FormFlattener (V6 new)",
            "dirty-artifact-policy-report.json: verdict FORMALIZED or CLEAN (V6 new)",
            "dirty-artifact-policy-report.json: present in bundle (V6 new)",
            "source-state-classification.json: sprint33_start_state present (V6 new)",
        ],
        "category_count_reconciliation": {
            "v5_categories": MIN_CATEGORIES_REQUIRED_V5,
            "v6_categories": MIN_CATEGORIES_REQUIRED_V6,
            "categories_removed_from_v5": sorted(_REQUIRED_CATEGORIES_V6_REMOVED),
            "categories_added_in_v6": sorted(_REQUIRED_CATEGORIES_V6_NEW.keys()),
            "note": "v5 had 53. v6 removes 1 (sprint31 entry) and adds 15 (sprint33 entries) → 67.",
        },
        "secret_scanning_enabled": True,
        "secret_patterns": [p.pattern for p in SECRET_PATTERNS],
        "allowed_verdicts": sorted(ALLOWED_VERDICTS_V6),
        "failure_verdict": "BUNDLE_CONTRACT_FAILED",
        "pass_verdict": "BUNDLE_CONTRACT_PASSED",
    }
