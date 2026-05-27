"""Run ECC for Healing Sprint 1."""
import sys
import json
import os
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plugin_examples.evidence_contract_computer import EvidenceContractComputer

repo_root = Path(__file__).resolve().parents[1]
contract_path = repo_root / "reports" / "healing-sprint-1" / "evidence" / "evidence-contract.json"
output_path = repo_root / "reports" / "healing-sprint-1" / "evidence" / "evidence-contract-computed.json"

with open(contract_path, encoding="utf-8") as f:
    contract = json.load(f)

categories = contract["categories"]

results = []
present = 0
missing = 0
zero_bytes = 0
semantic_failed = 0
blocking_failures = 0

for cat in categories:
    file_path = repo_root / cat["file"]
    if not file_path.exists():
        status = "MISSING"
        detail = "File not found"
        if cat.get("blocking", True):
            blocking_failures += 1
        missing += 1
    elif file_path.stat().st_size == 0:
        status = "ZERO_BYTES"
        detail = "File is empty (0 bytes)"
        if cat.get("blocking", True):
            blocking_failures += 1
        zero_bytes += 1
    else:
        status = "PRESENT"
        detail = ""
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
    "semantic_failed": semantic_failed,
    "pending": 0,
    "blocking_failures": blocking_failures,
    "closure_valid": closure_valid,
    "categories": results,
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(computed, f, indent=2)

print(f"ECC complete: {present}/{len(categories)} PRESENT")
print(f"blocking_failures: {blocking_failures}")
print(f"closure_valid: {closure_valid}")
print(json.dumps({
    "total": len(categories),
    "present": present,
    "missing": missing,
    "zero_bytes": zero_bytes,
    "blocking_failures": blocking_failures,
    "closure_valid": closure_valid,
}, indent=2))
