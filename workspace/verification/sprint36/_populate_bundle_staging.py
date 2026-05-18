"""Populate Sprint 36 bundle-staging directory.

Strategy:
1. Copy all 114 files from sprint35/bundle-staging as carry-forward.
2. Override with sprint36-specific files from lanes and root.
3. Add new sprint36-only artifacts.
4. Write bundle-contract-definition.json.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent  # repo root
SPRINT36_DIR = Path(__file__).parent
STAGING = SPRINT36_DIR / "bundle-staging"
SPRINT35_STAGING = ROOT / "workspace/verification/sprint35/bundle-staging"
LANES = SPRINT36_DIR / "lanes"

# Ensure staging dir exists
STAGING.mkdir(parents=True, exist_ok=True)

# --- Phase 1: Copy carry-forward from sprint35 ---
copied = 0
for f in SPRINT35_STAGING.iterdir():
    if f.is_file():
        dest = STAGING / f.name
        shutil.copy2(f, dest)
        copied += 1
print(f"Phase 1: copied {copied} carry-forward files from sprint35")

# --- Phase 2: Override with sprint36 git artifacts ---
overrides = {
    "git-status-final.txt": SPRINT36_DIR / "bundle-staging-temp-git-status-final.txt",
    "git-diff-final.patch": SPRINT36_DIR / "bundle-staging-temp-git-diff-final.patch",
    "git-log-proof.txt": SPRINT36_DIR / "bundle-staging-temp-git-log-proof.txt",
    # lane-0 overrides
    "git-status-initial.txt": LANES / "lane-0/git-status-initial.txt",
    "git-diff-initial.patch": LANES / "lane-0/git-diff-initial.patch",
    "source-state-classification.json": LANES / "lane-0/source-state-classification.json",
    # sprint36 root
    "final-verdict.md": SPRINT36_DIR / "final-verdict.md",
    "final-state-summary.yaml": SPRINT36_DIR / "final-state-summary.yaml",
    # lane-test
    "test-summary.json": LANES / "lane-test/test-summary.json",
    "test-targeted.log": LANES / "lane-test/test-targeted.log",
    "completeness-gate-summary.log": LANES / "lane-test/completeness-gate-summary.log",
    "package-dry-run-summary.log": LANES / "lane-test/package-dry-run-summary.log",
    "readme-audit-summary.log": LANES / "lane-test/readme-audit-summary.log",
    "version-drift-summary.log": LANES / "lane-test/version-drift-summary.log",
    "target-repo-health-summary.log": LANES / "lane-test/target-repo-health-summary.log",
    # lane-p0
    "publication-mode-decision.json": LANES / "lane-p0/publication-mode-decision.json",
    "github-token-readiness-report.json": LANES / "lane-p0/github-token-readiness-report.json",
    "merge-mode-decision.json": LANES / "lane-p0/merge-mode-decision.json",
    # lane-p1 through lane-p6
    "pdf-pr3-final-package-audit.json": LANES / "lane-p1/pdf-pr3-final-package-audit.json",
    "pdf-pr3-approval-blocked.md": LANES / "lane-p1/pdf-pr3-approval-blocked.md",
    "pdf-pr5-final-package-audit.json": LANES / "lane-p2/pdf-pr5-final-package-audit.json",
    "pdf-pr5-approval-blocked.md": LANES / "lane-p2/pdf-pr5-approval-blocked.md",
    "pdf-pr6-final-package-audit.json": LANES / "lane-p3/pdf-pr6-final-package-audit.json",
    "pdf-pr6-approval-blocked.md": LANES / "lane-p3/pdf-pr6-approval-blocked.md",
    "pdf-pr7-final-package-audit.json": LANES / "lane-p4/pdf-pr7-final-package-audit.json",
    "pdf-pr7-approval-blocked.md": LANES / "lane-p4/pdf-pr7-approval-blocked.md",
    "pdf-pr8-final-package-audit.json": LANES / "lane-p5/pdf-pr8-final-package-audit.json",
    "pdf-pr8-approval-blocked.md": LANES / "lane-p5/pdf-pr8-approval-blocked.md",
    "pdf-pr9-final-package-audit.json": LANES / "lane-p6/pdf-pr9-final-package-audit.json",
    "pdf-pr9-approval-blocked.md": LANES / "lane-p6/pdf-pr9-approval-blocked.md",
    # lane-p7
    "batch-publication-dry-run-report.json": LANES / "lane-p7/batch-publication-dry-run-report.json",
    # lane-p8
    "post-publication-not-run-approval-blocked.md": LANES / "lane-p8/post-publication-not-run-approval-blocked.md",
    "post-publication-pr-verification-report.json": LANES / "lane-p8/post-publication-pr-verification-report.json",
    # lane-dash (updated dashboard with reconciled counts)
    "portfolio-release-dashboard.json": LANES / "lane-dash/portfolio-release-dashboard.json",
    "portfolio-release-dashboard.md": LANES / "lane-dash/portfolio-release-dashboard.md",
    # lane-task (updated taskcard state)
    "taskcard-reconciliation-report.json": LANES / "lane-task/taskcard-reconciliation-report.json",
}

overridden = 0
for dest_name, src_path in overrides.items():
    if src_path.exists():
        shutil.copy2(src_path, STAGING / dest_name)
        overridden += 1
    else:
        print(f"  WARNING: override source missing: {src_path}")
print(f"Phase 2: overrode {overridden} sprint35 files with sprint36 versions")

# --- Phase 3: Add new sprint36-only artifacts ---
new_files = {
    # lane-0 new
    "sprint35-final-state-verification.json": LANES / "lane-0/sprint35-final-state-verification.json",
    "test-count-reconciliation-report.json": LANES / "lane-0/test-count-reconciliation-report.json",
    # lane-sys1
    "all-family-version-drift-command-report.json": LANES / "lane-sys1/all-family-version-drift-command-report.json",
    "all-family-version-drift-test-report.json": LANES / "lane-sys1/all-family-version-drift-test-report.json",
    "all-family-version-drift-run-report.json": LANES / "lane-sys1/all-family-version-drift-run-report.json",
    # lane-sys2
    "target-repo-health-command-report.json": LANES / "lane-sys2/target-repo-health-command-report.json",
    "target-repo-health-test-report.json": LANES / "lane-sys2/target-repo-health-test-report.json",
    "target-repo-health-run-report.json": LANES / "lane-sys2/target-repo-health-run-report.json",
    # lane-sys3
    "readme-source-truth-ci-report.json": LANES / "lane-sys3/readme-source-truth-ci-report.json",
    "readme-source-truth-ci-test-report.json": LANES / "lane-sys3/readme-source-truth-ci-test-report.json",
    "readme-source-truth-run-report.json": LANES / "lane-sys3/readme-source-truth-run-report.json",
    # lane-sys4
    "all-lowcode-launch-operator-packet-v3.json": LANES / "lane-sys4/all-lowcode-launch-operator-packet-v3.json",
    "all-lowcode-launch-operator-packet-v3.md": LANES / "lane-sys4/all-lowcode-launch-operator-packet-v3.md",
    # lane-dash
    "dashboard-consistency-report.json": LANES / "lane-dash/dashboard-consistency-report.json",
    # lane-task
    "taskcard-state-after-sprint36.json": LANES / "lane-task/taskcard-state-after-sprint36.json",
    # lane-p7 extra
    "batch-publication-manifest.json": LANES / "lane-p7/batch-publication-manifest.json",
    "publication-rollback-packet.json": LANES / "lane-p7/publication-rollback-packet.json",
    # lane-n-ocr
    "ocr-blocker-escalation-package.json": LANES / "lane-n-ocr/ocr-blocker-escalation-package.json",
    "ocr-blocker-escalation-issue.md": LANES / "lane-n-ocr/ocr-blocker-escalation-issue.md",
    # lane-n-psd
    "psd-blocker-escalation-package.json": LANES / "lane-n-psd/psd-blocker-escalation-package.json",
    "psd-blocker-escalation-issue.md": LANES / "lane-n-psd/psd-blocker-escalation-issue.md",
    # lane-n-epub
    "epub-no-package-verification-report.json": LANES / "lane-n-epub/epub-no-package-verification-report.json",
    # lane-n-other
    "other-family-lowcode-discovery-refresh.json": LANES / "lane-n-other/other-family-lowcode-discovery-refresh.json",
    # family lanes
    "cells-target-repo-launch-verification.json": LANES / "lane-f-cells/cells-target-repo-launch-verification.json",
    "cells-version-drift-report.json": LANES / "lane-f-cells/cells-version-drift-report.json",
    "cells-readme-integrity-report.json": LANES / "lane-f-cells/cells-readme-integrity-report.json",
    "words-target-repo-launch-verification.json": LANES / "lane-f-words/words-target-repo-launch-verification.json",
    "words-version-drift-report.json": LANES / "lane-f-words/words-version-drift-report.json",
    "words-readme-integrity-report.json": LANES / "lane-f-words/words-readme-integrity-report.json",
    "words-processor-blocker-recheck.json": LANES / "lane-f-words/words-processor-blocker-recheck.json",
    "pdf-target-repo-launch-verification.json": LANES / "lane-f-pdf/pdf-target-repo-launch-verification.json",
    "pdf-version-drift-report.json": LANES / "lane-f-pdf/pdf-version-drift-report.json",
    "pdf-readme-integrity-report.json": LANES / "lane-f-pdf/pdf-readme-integrity-report.json",
    "pdf-formimporter-recheck-report.json": LANES / "lane-f-pdf/pdf-formimporter-recheck-report.json",
    "pdf-pending-not-already-published-report.json": LANES / "lane-f-pdf/pdf-pending-not-already-published-report.json",
    "diagram-target-repo-launch-verification.json": LANES / "lane-f-diagram/diagram-target-repo-launch-verification.json",
    "diagram-version-drift-report.json": LANES / "lane-f-diagram/diagram-version-drift-report.json",
    "diagram-readme-healing-verification.json": LANES / "lane-f-diagram/diagram-readme-healing-verification.json",
    "email-target-repo-launch-verification.json": LANES / "lane-f-email/email-target-repo-launch-verification.json",
    "email-version-drift-report.json": LANES / "lane-f-email/email-version-drift-report.json",
    "email-readme-integrity-report.json": LANES / "lane-f-email/email-readme-integrity-report.json",
    "email-runtime-final-proof.json": LANES / "lane-f-email/email-runtime-final-proof.json",
    "slides-target-repo-launch-verification.json": LANES / "lane-f-slides/slides-target-repo-launch-verification.json",
    "slides-version-drift-report.json": LANES / "lane-f-slides/slides-version-drift-report.json",
    "slides-readme-integrity-report.json": LANES / "lane-f-slides/slides-readme-integrity-report.json",
    "slides-runtime-final-proof.json": LANES / "lane-f-slides/slides-runtime-final-proof.json",
}

added = 0
for dest_name, src_path in new_files.items():
    if src_path.exists():
        shutil.copy2(src_path, STAGING / dest_name)
        added += 1
    else:
        print(f"  WARNING: new file source missing: {src_path}")
print(f"Phase 3: added {added} new sprint36-only files")

# --- Phase 4: Write changed-files.txt for sprint36 ---
changed_files_content = """src/plugin_examples/__main__.py
src/plugin_examples/evidence_contract.py
src/plugin_examples/publisher/target_repo_health.py
src/plugin_examples/publisher/version_drift_checker.py
tests/unit/test_target_repo_health.py
tests/unit/test_version_drift_checker.py
workspace/verification/sprint36/ (all lane artifacts)
"""
(STAGING / "changed-files.txt").write_text(changed_files_content, encoding="utf-8")
print("Phase 4: wrote changed-files.txt")

# --- Phase 5: Write bundle-contract-definition.json ---
from plugin_examples.evidence_contract import contract_definition_v6, COMBINED_CATEGORIES_V6
import sys
sys.path.insert(0, str(ROOT / "src"))

defn = {
    "contract_version": "6.0.0",
    "sprint": "sprint36",
    "description": "Strict Evidence Contract V6 for Sprint 36 bundle.",
    "total_categories": len(COMBINED_CATEGORIES_V6),
    "allowed_verdicts": [
        "SPRINT36_ALL_LOWCODE_FAMILIES_PUBLISHED_MERGED_AND_VERIFIED",
        "SPRINT36_PUBLICATION_DONE_MERGE_BLOCKED_PORTFOLIO_HARDENED",
        "SPRINT36_APPROVAL_BLOCKED_PORTFOLIO_HARDENED_AND_OPERATOR_READY",
        "SPRINT36_PARTIAL_LAUNCH_EXECUTION_WITH_EXACT_BLOCKERS",
        "SPRINT36_BLOCKED_EVIDENCE_BUNDLE_FAILED",
        "SPRINT36_BLOCKED_SOURCE_STATE",
        "SPRINT36_REJECTED_UNSAFE_TO_PUBLISH",
    ],
    "expected_verdict": "SPRINT36_APPROVAL_BLOCKED_PORTFOLIO_HARDENED_AND_OPERATOR_READY",
}
(STAGING / "bundle-contract-definition.json").write_text(
    json.dumps(defn, indent=2), encoding="utf-8"
)
print("Phase 5: wrote bundle-contract-definition.json")

# --- Phase 6: Write bootstrap bundle-contract-validation-report.json ---
bootstrap_report = {
    "sprint": "sprint36",
    "passed": False,
    "bundle_bytes": 0,
    "bundle_file": "PENDING",
    "categories_found": 0,
    "categories_missing": ["BOOTSTRAP_PLACEHOLDER"],
    "note": "Bootstrap placeholder — will be updated after ZIP is built.",
}
(STAGING / "bundle-contract-validation-report.json").write_text(
    json.dumps(bootstrap_report, indent=2), encoding="utf-8"
)
print("Phase 6: wrote bootstrap bundle-contract-validation-report.json")

# --- Summary ---
all_files = list(STAGING.iterdir())
print(f"\nTotal files in bundle-staging: {len(all_files)}")
