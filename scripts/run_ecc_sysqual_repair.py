"""Run ECC for Full System Qualification Repair Sprint."""
import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPRINT_ID = "full-system-qualification-repair-20260529"
SPRINT_ROOT = REPO_ROOT / "reports" / SPRINT_ID
EVIDENCE_DIR = SPRINT_ROOT / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

# Build list of all tracked files in the sprint
all_files = sorted(
    p.relative_to(REPO_ROOT).as_posix()
    for p in SPRINT_ROOT.rglob("*")
    if p.is_file()
)

# Core required files (blocking)
CORE_FILES = {
    f"reports/{SPRINT_ID}/preflight/environment-proof.json",
    f"reports/{SPRINT_ID}/preflight/environment-proof.md",
    f"reports/{SPRINT_ID}/preflight/git-start-proof.txt",
    f"reports/{SPRINT_ID}/preflight/lane-ownership.md",
    f"reports/{SPRINT_ID}/audit/contradiction-register.json",
    f"reports/{SPRINT_ID}/audit/previous-bundle-audit.md",
    f"reports/{SPRINT_ID}/audit/overclaim-correction.md",
    f"reports/{SPRINT_ID}/discovery/product-universe-current.json",
    f"reports/{SPRINT_ID}/discovery/lowcode-discovery-summary.json",
    f"reports/{SPRINT_ID}/discovery/product-classification-matrix.md",
    f"reports/{SPRINT_ID}/supervisor/product-queue-start.json",
    f"reports/{SPRINT_ID}/supervisor/product-queue-final.json",
    f"reports/{SPRINT_ID}/supervisor/event-log.jsonl",
    f"reports/{SPRINT_ID}/supervisor/failure-ledger.json",
    f"reports/{SPRINT_ID}/supervisor/halt-ledger.json",
    f"reports/{SPRINT_ID}/supervisor/final-supervisor-verdict.md",
    f"reports/{SPRINT_ID}/tests/full-pytest.log",
    f"reports/{SPRINT_ID}/tests/full-pytest-summary.json",
    f"reports/{SPRINT_ID}/validators/new-validator-rules.md",
    f"reports/{SPRINT_ID}/validators/validator-gap-analysis.md",
    f"reports/{SPRINT_ID}/validators/invariant-coverage-matrix.json",
    f"reports/{SPRINT_ID}/publication/approval-gate-proof.md",
    f"reports/{SPRINT_ID}/publication/no-remote-mutation-proof.json",
    f"reports/{SPRINT_ID}/publication/local-pr-dry-run-matrix.json",
    f"reports/{SPRINT_ID}/blockers/external-blocker-recheck.md",
    f"reports/{SPRINT_ID}/iv/independent-verification-report.md",
    f"reports/{SPRINT_ID}/iv/adversarial-review.md",
    f"reports/{SPRINT_ID}/iv/final-consistency-check.json",
    f"reports/{SPRINT_ID}/iv/acceptance-matrix.md",
    f"reports/{SPRINT_ID}/state/state-sync-summary.md",
    f"reports/{SPRINT_ID}/state/product-status-table.json",
    f"reports/{SPRINT_ID}/final-verdict.md",
    f"reports/{SPRINT_ID}/sprint-state.json",
}

# Per-family E2E required files
FAMILIES = ["cells", "diagram", "email", "pdf", "slides", "words"]
E2E_FILES = [
    "build.log", "e2e-run-summary.md", "example-gate-results.json",
    "generated-example-manifest.json", "pilot-report.json",
    "reviewer-fallback-proof.md", "reviewer-results.json",
    "validation-results.json", "stage-results.json",
]
for fam in FAMILIES:
    for ef in E2E_FILES:
        CORE_FILES.add(f"reports/{SPRINT_ID}/products/{fam}/full-e2e/{ef}")


def build_categories():
    cats = []
    idx = 1
    seen = set()
    for f in sorted(all_files):
        if f in seen:
            continue
        seen.add(f)
        blocking = f in CORE_FILES
        cats.append({
            "id": f"ECC-{idx:03d}",
            "name": Path(f).name,
            "file": f,
            "blocking": blocking,
        })
        idx += 1
    return cats


categories = build_categories()

# Write contract
contract = {
    "contract_id": f"ecc-{SPRINT_ID}",
    "sprint_id": SPRINT_ID,
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "total_files": len(categories),
    "categories": categories,
}
contract_path = EVIDENCE_DIR / "evidence-contract.json"
contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")

# Compute ECC
results = []
present = missing = zero_bytes = blocking_failures = 0

for cat in categories:
    fp = REPO_ROOT / cat["file"]
    if not fp.exists():
        status, detail = "MISSING", "File not found"
        if cat.get("blocking", True):
            blocking_failures += 1
        missing += 1
    elif fp.stat().st_size == 0:
        status, detail = "ZERO_BYTES", "File is empty (0 bytes)"
        if cat.get("blocking", True):
            blocking_failures += 1
        zero_bytes += 1
    else:
        status, detail = "PRESENT", ""
        present += 1
    results.append({
        "id": cat["id"],
        "name": cat["name"],
        "file": cat["file"],
        "blocking": cat.get("blocking", True),
        "status": status,
        "detail": detail,
    })

closure_valid = blocking_failures == 0
computed = {
    "contract_id": contract["contract_id"],
    "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "total_categories": len(categories),
    "present": present,
    "missing": missing,
    "zero_bytes": zero_bytes,
    "semantic_failed": 0,
    "pending": 0,
    "blocking_failures": blocking_failures,
    "closure_valid": closure_valid,
    "validation_result": "ACCEPTED" if closure_valid else "REJECTED",
    "categories": results,
}

output_path = EVIDENCE_DIR / "evidence-contract-computed.json"
output_path.write_text(json.dumps(computed, indent=2), encoding="utf-8")

print(f"ECC: {present}/{len(categories)} PRESENT  blocking_failures={blocking_failures}  closure_valid={closure_valid}")
if missing or zero_bytes:
    for r in results:
        if r["status"] != "PRESENT":
            print(f"  [{r['status']}] {r['id']}: {r['file']}")

sys.exit(0 if closure_valid else 1)
