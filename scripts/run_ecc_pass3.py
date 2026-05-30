#!/usr/bin/env python3
"""ECC script for lowcode-final-closure-pass3-20260530 sprint."""

import json
import os
from pathlib import Path

SPRINT_ID = "lowcode-final-closure-pass3-20260530"
REPO_ROOT = Path(__file__).parent.parent
REPORT_DIR = REPO_ROOT / "reports" / SPRINT_ID

REQUIRED_FILES = [
    # Lane 0
    "preflight/environment-proof.json",
    "preflight/environment-proof.md",
    "preflight/git-start-proof.txt",
    "preflight/dirty-state-classification.md",
    "preflight/untracked-file-disposition.md",
    "preflight/approval-gates-proof.md",
    "preflight/run-id-selection.md",
    "commands/raw-commands.log",
    # Lane 1
    "audit/accepted-vs-not-accepted-matrix.json",
    "audit/previous-bundle-normalization.md",
    "audit/taskcard-update-proof.md",
    "audit/state-sync-proof.md",
    # Lane 2
    "generated-source/source-snapshot-manifest.json",
    "generated-source/hash-verification.json",
    "generated-source/no-manual-patch-proof.md",
    # Lane 3
    "replay-contract/replay-decision.md",
    "replay-contract/catalog-hash-proof.json",
    "replay-contract/denominator-hash-proof.json",
    "replay-contract/generator-source-hash-proof.json",
    "replay-contract/generated-output-freshness-proof.json",
    "replay-contract/cells-replay-contract.json",
    "replay-contract/diagram-replay-contract.json",
    "replay-contract/email-replay-contract.json",
    "replay-contract/pdf-replay-contract.json",
    "replay-contract/slides-replay-contract.json",
    "replay-contract/words-replay-contract.json",
    # Lane 4
    "e2e-raw/e2e-aggregate.json",
    "e2e-raw/e2e-summary.md",
    "commands/lane2-lane4-run.log",
    # Lane 5
    "tests/full-pytest.log",
    "tests/full-pytest-summary.json",
    "tests/durable-fix-tests.log",
    "tests/failure-repair-ledger.md",
    # Lane 6
    "verification-latest/before-after-state.json",
    "verification-latest/root-cause.md",
    "verification-latest/promotion-step-implementation.md",
    # Lane 7
    "reviewer/reviewer-state-model.md",
    "reviewer/fallback-review-results.json",
    "reviewer/per-family-review-summary.md",
    # Lane 8
    "denominators/validation-vs-publication-denominator.md",
    # Lane 9
    "publication/publication-dry-run-summary.json",
    # Lane 10
    "blockers/epub-raw-check.log",
    "blockers/ocr-raw-check.log",
    "blockers/psd-raw-check.log",
    "blockers/external-blocker-summary.json",
    # Lane 11
    "artifact/commit-plan.md",
    # Lane 12
    "workahead/work-ahead-deliverables.md",
    # Lane 13
    "ai/ai-accounting.json",
    # Lane 14
    "iv/iv-review.md",
    # Final verdict
    "final-verdict.md",
]

def main():
    print(f"ECC for sprint: {SPRINT_ID}")
    print(f"Report dir: {REPORT_DIR}")
    print()

    # Count total files
    total_files = list(REPORT_DIR.rglob("*"))
    total_files = [f for f in total_files if f.is_file()]
    total_count = len(total_files)

    # Check required files
    missing = []
    found = []
    for rel_path in REQUIRED_FILES:
        full_path = REPORT_DIR / rel_path
        if full_path.exists():
            found.append(rel_path)
        else:
            missing.append(rel_path)
            print(f"  MISSING: {rel_path}")

    required_count = len(REQUIRED_FILES)
    found_count = len(found)
    missing_count = len(missing)

    status = "PASS" if missing_count == 0 else "FAIL"

    print(f"\nTotal files in sprint dir: {total_count}")
    print(f"Required files checked: {required_count}")
    print(f"Found: {found_count}")
    print(f"Missing: {missing_count}")
    print(f"Status: {status}")
    print(f"ECC: {total_count}/{total_count} total, {found_count}/{required_count} required")

    result = {
        "sprint_id": SPRINT_ID,
        "status": status,
        "ecc_total": total_count,
        "ecc_required": required_count,
        "ecc_found": found_count,
        "ecc_missing": missing_count,
        "missing_files": missing,
        "summary": f"{total_count} total files, {found_count}/{required_count} required files found"
    }

    out_path = REPORT_DIR / "artifact" / "ecc-result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nECC result written: {out_path}")

    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
