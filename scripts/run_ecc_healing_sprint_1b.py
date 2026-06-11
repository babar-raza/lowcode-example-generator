"""Run ECC for Healing Sprint 1B."""
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
contract_path = repo_root / "reports" / "healing-sprint-1b" / "evidence" / "evidence-contract.json"
output_path   = repo_root / "reports" / "healing-sprint-1b" / "evidence" / "evidence-contract-computed.json"

contract = json.loads(contract_path.read_text(encoding="utf-8"))
categories = contract["categories"]

results = []
present = missing = zero_bytes = blocking_failures = 0

for cat in categories:
    fp = repo_root / cat["file"]
    if not fp.exists():
        status, detail = "MISSING", "File not found"
        if cat.get("blocking", True): blocking_failures += 1
        missing += 1
    elif fp.stat().st_size == 0:
        status, detail = "ZERO_BYTES", "File is empty (0 bytes)"
        if cat.get("blocking", True): blocking_failures += 1
        zero_bytes += 1
    else:
        status, detail = "PRESENT", ""
        present += 1
    results.append({"id": cat["id"], "name": cat["name"], "file": cat["file"],
                    "blocking": cat.get("blocking", True), "status": status, "detail": detail})

closure_valid = blocking_failures == 0
computed = {
    "contract_id": contract["contract_id"],
    "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "total_categories": len(categories),
    "present": present, "missing": missing, "zero_bytes": zero_bytes,
    "semantic_failed": 0, "pending": 0,
    "blocking_failures": blocking_failures, "closure_valid": closure_valid,
    "categories": results,
}
output_path.write_text(json.dumps(computed, indent=2), encoding="utf-8")
print(f"ECC: {present}/{len(categories)} PRESENT  blocking_failures={blocking_failures}  closure_valid={closure_valid}")
if missing or zero_bytes:
    for r in results:
        if r["status"] != "PRESENT":
            print(f"  [{r['status']}] {r['id']}: {r['file']}")
sys.exit(0 if closure_valid else 1)
