# Evidence Contract Repair — Sprint 63 Phase 1

**Sprint:** 63
**Defect:** Sprint 62 evidence-contract.json had 31/37 categories PENDING despite files existing
**Root cause:** Contract created at sprint start with all categories hardcoded PENDING; no process updated statuses
**Fix:** New EvidenceContractComputer module computes status from actual file state

---

## Root Cause Analysis

Sprint 62 evidence-contract.json was created at the start of the sprint with categories
initialised to PENDING. As each phase completed and files were created, the contract was
never updated. The contract itself says `"PENDING = INVALID_CLOSURE"`, yet Sprint 62 claimed
closure with 31/37 categories PENDING.

This is a process failure: the contract was treated as documentation, not as a gating mechanism.

---

## Fix: EvidenceContractComputer

New module: `src/plugin_examples/evidence_contract_computer.py`

The computer:
1. Reads `evidence-contract.json` for the list of required categories
2. For each category, checks:
   - `file_exists` → MISSING if false
   - `file_nonzero` → ZERO_BYTES if false
   - `semantic_validation` → SEMANTIC_FAILED if defined and fails
3. Returns computed status (never PENDING at closure)
4. `closure_valid=True` only if `blocking_failures==0`

### Semantic Validators Supported

| Semantic keyword | What it checks |
|-----------------|---------------|
| `must not contain IN_PROGRESS` | Fails if file contains "IN_PROGRESS" |
| `must have no unchecked [ ] items` | Fails if file contains `- [ ]` |
| `must show 0 failed` | Fails if no "0 failed" in test output |
| `must show overall_valid=false` | JSON: `overall_valid` must be false |
| `must show overall_valid=true, no internal contradiction` | JSON: `overall_valid=true` AND no FAILURE rule with `passed=false` |
| `must have 42 entries with output_format, api_type, readme_status` | JSON array with 42+ records and required fields |
| `must list 6 families with file counts` | JSON with 6+ family entries |
| `must show 0 PENDING blocking categories` | Computed contract result has 0 blocking failures |
| `nonzero, git header present, captured AFTER final commit` | File contains git status header line |

---

## Usage

```python
from plugin_examples.evidence_contract_computer import EvidenceContractComputer
from pathlib import Path

computer = EvidenceContractComputer(
    contract_path=Path("reports/sprint63/evidence-contract.json"),
    repo_root=Path("."),
)
result = computer.compute()
print(f"Closure valid: {result.closure_valid}")
print(f"Blocking failures: {result.blocking_failures}")
```

---

## Tests

File: `tests/unit/test_evidence_contract_computer.py`
Result: 13 passed, 0 failed
See: `reports/sprint63/evidence/evidence-contract-test-results.txt`
