"""Two-pass ECC for Sprint 80."""
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from plugin_examples.evidence_contract_computer import EvidenceContractComputer

contract_path = Path("reports/sprint80/evidence-contract.json")
evidence_path = Path("reports/sprint80/evidence/evidence-contract-computed.json")

# Pass 1: write placeholder so EC34 can find a file
placeholder = {
    "sprint_id": "sprint80",
    "status": "PLACEHOLDER_FOR_SELF_REFERENCE",
    "blocking_failures": 999,
    "closure_valid": False
}
evidence_path.write_text(json.dumps(placeholder, indent=2), encoding="utf-8")
print("Pass 1: placeholder written")

# Pass 2: run ECC — EC34 now points to a real file (the placeholder)
comp = EvidenceContractComputer(
    contract_path=contract_path,
    repo_root=Path(".")
)
result = comp.compute()
data = result.to_dict()

# Write final result
evidence_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("Pass 2: ECC computed")
print(f"blocking_failures: {data.get('blocking_failures')}")
print(f"closure_valid: {data.get('closure_valid')}")
print(f"categories_total: {data.get('categories_total')}")
print(f"categories_present: {data.get('categories_present')}")
print(f"categories_missing: {data.get('categories_missing')}")

# Print any failures
failures = data.get("failures", [])
if failures:
    print(f"\nFAILURES ({len(failures)}):")
    for f in failures:
        print(f"  {f}")
else:
    print("No blocking failures.")
