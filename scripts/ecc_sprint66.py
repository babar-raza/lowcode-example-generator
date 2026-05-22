"""Run EvidenceContractComputer on Sprint 66 bundle."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plugin_examples.evidence_contract_computer import EvidenceContractComputer

repo_root = Path(__file__).resolve().parents[1]
contract_path = repo_root / "reports" / "sprint66" / "evidence-contract.json"

computer = EvidenceContractComputer(contract_path=contract_path, repo_root=repo_root)
result = computer.compute()

print(f"ECC: total={result.total_categories}, present={result.present_count}, "
      f"missing={result.missing_count}, zero_bytes={result.zero_bytes_count}, "
      f"semantic_failed={result.semantic_failed_count}, blocking_failures={result.blocking_failures}, "
      f"closure_valid={result.closure_valid}")

if not result.closure_valid:
    print("\nFailing categories:")
    for c in result.categories:
        if c.status != "PRESENT":
            print(f"  [{c.status}] {c.id} ({c.file}): {c.detail}")

out_path = repo_root / "reports" / "sprint66" / "evidence" / "evidence-contract-computed.json"
out_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
print(f"\nWrote: {out_path}")

if not result.closure_valid:
    sys.exit(1)
