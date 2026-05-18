"""Populate Sprint 37 bundle-staging directory."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
SPRINT37_DIR = Path(__file__).parent
STAGING = SPRINT37_DIR / "bundle-staging"
SPRINT36_STAGING = ROOT / "workspace/verification/sprint36/bundle-staging"
LANES = SPRINT37_DIR / "lanes"
RUN_ID = "sprint37-all-lowcode-launch-execution-and-version-drift-20260518-195241"

STAGING.mkdir(parents=True, exist_ok=True)

# Phase 1: carry-forward from sprint36
copied = 0
for f in SPRINT36_STAGING.iterdir():
    if f.is_file():
        shutil.copy2(f, STAGING / f.name)
        copied += 1
print(f"Phase 1: copied {copied} carry-forward files from sprint36")

# Phase 2: override with sprint37 versions
overrides = {
    "final-verdict.md": SPRINT37_DIR / "final-verdict.md",
    "final-state-summary.yaml": SPRINT37_DIR / "final-state-summary.yaml",
    "sprint-identity-allocation.json": LANES / "lane-0/sprint-identity-allocation.json",
    "sprint36-final-commit-verification.json": LANES / "lane-0/sprint36-final-commit-verification.json",
    "source-state-classification.json": LANES / "lane-0/source-state-classification.json",
    "git-status-initial.txt": LANES / "lane-0/git-status-initial.txt",
    "git-status-final.txt": LANES / "lane-0/git-status-final.txt",
    "git-diff-initial.patch": LANES / "lane-0/git-diff-initial.patch",
    "git-log-proof.txt": LANES / "lane-0/git-log-proof.txt",
    "version-drift-taxonomy-verification.json": LANES / "lane-1/version-drift-taxonomy-verification.json",
    "version-drift-taxonomy-test-report.json": LANES / "lane-1/version-drift-taxonomy-test-report.json",
    "all-family-version-drift-run-report.json": LANES / "lane-1/all-family-version-drift-run-report.json",
    "publication-mode-decision.json": LANES / "lane-2/publication-mode-decision.json",
    "merge-mode-decision.json": LANES / "lane-2/merge-mode-decision.json",
    "github-token-readiness-report.json": LANES / "lane-2/github-token-readiness-report.json",
    "pdf-pr3-final-package-audit.json": LANES / "lane-3/pdf-pr3-final-package-audit.json",
    "pdf-pr3-approval-blocked.md": LANES / "lane-3/pdf-pr3-approval-blocked.md",
    "pdf-pr5-final-package-audit.json": LANES / "lane-3/pdf-pr5-final-package-audit.json",
    "pdf-pr5-approval-blocked.md": LANES / "lane-3/pdf-pr5-approval-blocked.md",
    "pdf-pr6-final-package-audit.json": LANES / "lane-3/pdf-pr6-final-package-audit.json",
    "pdf-pr6-approval-blocked.md": LANES / "lane-3/pdf-pr6-approval-blocked.md",
    "pdf-pr7-final-package-audit.json": LANES / "lane-3/pdf-pr7-final-package-audit.json",
    "pdf-pr7-approval-blocked.md": LANES / "lane-3/pdf-pr7-approval-blocked.md",
    "pdf-pr8-final-package-audit.json": LANES / "lane-3/pdf-pr8-final-package-audit.json",
    "pdf-pr8-approval-blocked.md": LANES / "lane-3/pdf-pr8-approval-blocked.md",
    "pdf-pr9-final-package-audit.json": LANES / "lane-3/pdf-pr9-final-package-audit.json",
    "pdf-pr9-approval-blocked.md": LANES / "lane-3/pdf-pr9-approval-blocked.md",
    "pdf-publication-summary.json": LANES / "lane-3/pdf-publication-summary.json",
    "post-publication-not-run-approval-blocked.md": LANES / "lane-4/post-publication-not-run-approval-blocked.md",
    "cells-version-drift-pilot-report.json": LANES / "lane-5/cells-version-drift-pilot-report.json",
    "cells-26-5-1-validation-report.json": LANES / "lane-5/cells-26-5-1-validation-report.json",
    "cells-version-drift-decision.md": LANES / "lane-5/cells-version-drift-decision.md",
    "diagram-version-drift-pilot-report.json": LANES / "lane-6/diagram-version-drift-pilot-report.json",
    "diagram-26-5-0-validation-report.json": LANES / "lane-6/diagram-26-5-0-validation-report.json",
    "diagram-version-drift-decision.md": LANES / "lane-6/diagram-version-drift-decision.md",
    "cells-target-repo-health-report.json": LANES / "lane-7/cells-target-repo-health-report.json",
    "words-target-repo-health-report.json": LANES / "lane-7/words-target-repo-health-report.json",
    "pdf-target-repo-health-report.json": LANES / "lane-7/pdf-target-repo-health-report.json",
    "diagram-target-repo-health-report.json": LANES / "lane-7/diagram-target-repo-health-report.json",
    "email-target-repo-health-report.json": LANES / "lane-7/email-target-repo-health-report.json",
    "slides-target-repo-health-report.json": LANES / "lane-7/slides-target-repo-health-report.json",
    "target-repo-health-summary.json": LANES / "lane-7/target-repo-health-summary.json",
    "readme-source-truth-run-report.json": LANES / "lane-8/readme-source-truth-run-report.json",
    "readme-source-truth-portfolio-audit.json": LANES / "lane-8/readme-source-truth-portfolio-audit.json",
    "readme-source-truth-portfolio-audit.md": LANES / "lane-8/readme-source-truth-portfolio-audit.md",
    "readme-sync-audit.json": LANES / "lane-8/readme-sync-audit.json",
    "readme-coverage-audit-before.json": LANES / "lane-8/readme-coverage-audit-before.json",
    "ocr-blocker-escalation-package-final.json": LANES / "lane-9/ocr-blocker-escalation-package-final.json",
    "ocr-blocker-escalation-issue-final.md": LANES / "lane-9/ocr-blocker-escalation-issue-final.md",
    "psd-blocker-escalation-package-final.json": LANES / "lane-9/psd-blocker-escalation-package-final.json",
    "psd-blocker-escalation-issue-final.md": LANES / "lane-9/psd-blocker-escalation-issue-final.md",
    "epub-no-package-verification-report.json": LANES / "lane-10/epub-no-package-verification-report.json",
    "other-family-lowcode-discovery-refresh.json": LANES / "lane-10/other-family-lowcode-discovery-refresh.json",
    "formimporter-version-watch-run-report.json": LANES / "lane-11/formimporter-version-watch-run-report.json",
    "formimporter-defect-status-report.md": LANES / "lane-11/formimporter-defect-status-report.md",
    "batch-publication-dry-run-report.json": LANES / "lane-12/batch-publication-dry-run-report.json",
    "batch-publication-manifest.json": LANES / "lane-12/batch-publication-manifest.json",
    "all-lowcode-launch-operator-packet-v4.md": LANES / "lane-12/all-lowcode-launch-operator-packet-v4.md",
    "all-lowcode-launch-operator-packet-v4.json": LANES / "lane-12/all-lowcode-launch-operator-packet-v4.json",
    "all-family-launch-scoreboard.json": LANES / "lane-13/all-family-launch-scoreboard.json",
    "families-needing-launch-work.json": LANES / "lane-13/families-needing-launch-work.json",
    "release-state-reconciliation-report.json": LANES / "lane-13/release-state-reconciliation-report.json",
    "portfolio-release-dashboard.json": LANES / "lane-13/portfolio-release-dashboard.json",
    "portfolio-release-dashboard.md": LANES / "lane-13/portfolio-release-dashboard.md",
    "dashboard-consistency-report.json": LANES / "lane-13/dashboard-consistency-report.json",
    "taskcard-reconciliation-report.json": LANES / "lane-14/taskcard-reconciliation-report.json",
    f"taskcard-state-after-{RUN_ID}.json": LANES / f"lane-14/taskcard-state-after-{RUN_ID}.json",
    "evidence-contract-stability-report.json": LANES / "lane-15/evidence-contract-stability-report.json",
    "evidence-contract-v7-report.json": LANES / "lane-15/evidence-contract-v7-report.json",
    "test-targeted.log": LANES / "lane-test/test-targeted.log",
    "test-full.log": LANES / "lane-test/test-full.log",
    "test-summary.json": LANES / "lane-test/test-summary.json",
    "version-drift-summary.log": LANES / "lane-test/version-drift-summary.log",
    "target-repo-health-summary.log": LANES / "lane-test/target-repo-health-summary.log",
    "readme-audit-summary.log": LANES / "lane-test/readme-audit-summary.log",
    "completeness-gate-summary.log": LANES / "lane-test/completeness-gate-summary.log",
    "package-dry-run-summary.log": LANES / "lane-test/package-dry-run-summary.log",
}

overridden = 0
missing = []
for dest_name, src_path in overrides.items():
    if src_path.exists():
        shutil.copy2(src_path, STAGING / dest_name)
        overridden += 1
    else:
        missing.append(f"  MISSING: {src_path}")
print(f"Phase 2: overrode {overridden} files with sprint37 versions")
for m in missing:
    print(m)

# Phase 3: write bundle contract definition
from plugin_examples.evidence_contract import contract_definition_v6, COMBINED_CATEGORIES_V6
import sys
sys.path.insert(0, str(ROOT / "src"))

# Use V7 if available
try:
    from plugin_examples.evidence_contract import COMBINED_CATEGORIES_V7
    categories = COMBINED_CATEGORIES_V7
    contract_version = "7.0.0"
    print("Using V7 contract (69 categories)")
except ImportError:
    categories = COMBINED_CATEGORIES_V6
    contract_version = "6.0.0"
    print("Using V6 contract (67 categories)")

defn = {
    "contract_version": contract_version,
    "sprint": "sprint37",
    "run_id": RUN_ID,
    "description": f"Evidence Contract V{contract_version[0]} for Sprint 37 bundle.",
    "total_categories": len(categories),
    "allowed_verdicts": [
        "SPRINT37_ALL_LOWCODE_FAMILIES_PUBLISHED_MERGED_AND_VERIFIED",
        "SPRINT37_PUBLICATION_DONE_MERGE_BLOCKED_PORTFOLIO_ADVANCED",
        "SPRINT37_APPROVAL_BLOCKED_PORTFOLIO_ADVANCED_VERSION_DRIFT_PILOTED",
        "SPRINT37_PARTIAL_LAUNCH_EXECUTION_WITH_EXACT_BLOCKERS",
        "SPRINT37_BLOCKED_EVIDENCE_BUNDLE_FAILED",
        "SPRINT37_BLOCKED_SOURCE_STATE",
        "SPRINT37_REJECTED_UNSAFE_TO_PUBLISH",
    ],
    "expected_verdict": "SPRINT37_APPROVAL_BLOCKED_PORTFOLIO_ADVANCED_VERSION_DRIFT_PILOTED",
}
(STAGING / "bundle-contract-definition.json").write_text(
    json.dumps(defn, indent=2), encoding="utf-8"
)

# Bootstrap validation report
bootstrap = {
    "sprint": "sprint37",
    "run_id": RUN_ID,
    "passed": False,
    "bundle_bytes": 0,
    "bundle_file": "",
    "categories_found": 0,
    "categories_missing": ["BOOTSTRAP_PLACEHOLDER"],
    "note": "Bootstrap placeholder — will be updated after ZIP is built.",
}
(STAGING / "bundle-contract-validation-report.json").write_text(
    json.dumps(bootstrap, indent=2), encoding="utf-8"
)

all_files = list(STAGING.iterdir())
print(f"\nTotal files in bundle-staging: {len(all_files)}")
