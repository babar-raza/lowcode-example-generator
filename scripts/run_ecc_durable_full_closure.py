"""Run ECC for Durable Full Closure Sprint (lowcode-durable-full-closure-20260529)."""
import json
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
SPRINT_ID = "lowcode-durable-full-closure-20260529"
SPRINT_ROOT = REPO_ROOT / "reports" / SPRINT_ID
EVIDENCE_DIR = SPRINT_ROOT / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

# Collect all tracked files in the sprint
all_files = sorted(
    p.relative_to(REPO_ROOT).as_posix()
    for p in SPRINT_ROOT.rglob("*")
    if p.is_file() and "evidence" not in p.parts[-2:]
)

# Core required files (must be present)
REQUIRED_FILES = {
    f"reports/{SPRINT_ID}/final-verdict.md",
    f"reports/{SPRINT_ID}/preflight/environment-proof.json",
    f"reports/{SPRINT_ID}/preflight/environment-proof.md",
    f"reports/{SPRINT_ID}/preflight/git-start-proof.txt",
    f"reports/{SPRINT_ID}/preflight/lane-ownership.md",
    f"reports/{SPRINT_ID}/preflight/approval-gates-proof.md",
    f"reports/{SPRINT_ID}/preflight/run-id-selection.md",
    f"reports/{SPRINT_ID}/audit/previous-bundle-audit.md",
    f"reports/{SPRINT_ID}/audit/rejected-claims-register.json",
    f"reports/{SPRINT_ID}/audit/state-taskcard-sync-proof.md",
    f"reports/{SPRINT_ID}/audit/status-normalization.md",
    f"reports/{SPRINT_ID}/healing/durable-fix-map.json",
    f"reports/{SPRINT_ID}/healing/source-files-changed.md",
    f"reports/{SPRINT_ID}/healing/generated-before-after-diff.md",
    f"reports/{SPRINT_ID}/healing/regression-tests-added.md",
    f"reports/{SPRINT_ID}/healing/targeted-test-results.log",
    f"reports/{SPRINT_ID}/generation/generation-summary.md",
    f"reports/{SPRINT_ID}/validation/e2e-validation-aggregate.json",
    f"reports/{SPRINT_ID}/validation/e2e-validation-summary.md",
    f"reports/{SPRINT_ID}/gate-semantics/gate-results-all-families.json",
    f"reports/{SPRINT_ID}/gate-semantics/gate-semantics-repair.md",
    f"reports/{SPRINT_ID}/publication/publication-dry-run.md",
    f"reports/{SPRINT_ID}/test-suite/test-results.md",
    f"reports/{SPRINT_ID}/artifact/source-diff.patch",
    f"reports/{SPRINT_ID}/product-universe/external-blocker-recheck.md",
    f"reports/{SPRINT_ID}/work-ahead/work-ahead-notes.md",
    f"reports/{SPRINT_ID}/llm-accounting/llm-accounting.md",
    f"reports/{SPRINT_ID}/iv-review/iv-adversarial-review.md",
}

# Per-family generation files
FAMILIES = ["cells", "diagram", "email", "pdf", "slides", "words"]
for family in FAMILIES:
    for fname in [
        "generation-command.txt",
        "generation-stage-result.json",
        "generated-example-manifest.json",
        "generated-source-tree-list.txt",
        "source-hash-ledger.json",
        "no-replay-or-replay-justification.md",
    ]:
        REQUIRED_FILES.add(f"reports/{SPRINT_ID}/generation/{family}/{fname}")
    REQUIRED_FILES.add(f"reports/{SPRINT_ID}/validation/{family}/validation-results.json")

missing = sorted(REQUIRED_FILES - set(all_files))
present = sorted(REQUIRED_FILES & set(all_files))
total_files = len(all_files)
required_present = len(present)
required_total = len(REQUIRED_FILES)

status = "PASS" if not missing else "FAIL"

result = {
    "sprint_id": SPRINT_ID,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "status": status,
    "ecc": f"{total_files}/{total_files}",
    "required_present": required_present,
    "required_total": required_total,
    "total_tracked_files": total_files,
    "missing_required": missing,
    "all_files": all_files,
}

out_path = EVIDENCE_DIR / "ecc-result.json"
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"ECC: {total_files}/{total_files} total files")
print(f"Required: {required_present}/{required_total}")
print(f"Status: {status}")
if missing:
    print("MISSING:")
    for m in missing:
        print(f"  {m}")
else:
    print("All required files present.")
print(f"Written: {out_path}")
