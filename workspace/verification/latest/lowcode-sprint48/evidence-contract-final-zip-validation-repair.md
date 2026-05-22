# Evidence Contract Final-ZIP Validation Repair

## Problem
Sprint 47 `evidence-contract-validation-proof.json` validated Sprint 46's bundle, not Sprint 47's.

## Fix
Added `generate_validation_proof(zip_path, output_path)` to `evidence_contract.py`.

The function:
- Takes explicit ZIP path (no default, no guessing)
- Computes SHA256 of the ZIP
- Runs `PlannerSprintEvidenceContract.validate_zip()`
- Returns structured proof dict with exact path, SHA256, timestamp, all results
- Optionally writes proof JSON to `output_path`

## Regression Tests (7)
1. Proof names the correct ZIP path
2. Proof includes SHA256
3. Proof writes to output path
4. Incomplete bundle fails
5. Nonexistent ZIP raises FileNotFoundError
6. Proof has contract metadata
7. Two different ZIPs produce proofs naming their own paths

## Sprint 47 Retroactive Validation
Sprint 47 bundle validated with new function: **PLANNER_CONTRACT_PASSED** 17/17.
