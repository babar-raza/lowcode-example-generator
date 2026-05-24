"""Two-pass ECC for Sprint 82."""
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from plugin_examples.evidence_contract_computer import EvidenceContractComputer

contract_path = Path("reports/sprint82/evidence-contract.json")
evidence_path = Path("reports/sprint82/evidence/evidence-contract-computed.json")

# Pass 1: placeholder
placeholder = {"sprint_id": "sprint82", "status": "PLACEHOLDER", "blocking_failures": 999, "closure_valid": False}
evidence_path.write_text(json.dumps(placeholder, indent=2), encoding="utf-8")
print("Pass 1: placeholder written")

# Pass 2: real ECC
comp = EvidenceContractComputer(contract_path=contract_path, repo_root=Path("."))
result = comp.compute()
data = result.to_dict()
evidence_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("Pass 2: ECC computed")
print(f"total_categories: {data.get('total_categories')}")
print(f"present: {data.get('present')}")
print(f"missing: {data.get('missing')}")
print(f"blocking_failures: {data.get('blocking_failures')}")
print(f"closure_valid: {data.get('closure_valid')}")
failures = [c for c in data.get('categories', []) if c['status'] != 'PRESENT']
if failures:
    print("FAILURES:")
    for f in failures:
        print(f"  {f['id']}: {f['name']} -- {f['status']} -- {f.get('detail')}")
