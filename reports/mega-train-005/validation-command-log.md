# Lane J: Validation Command Log

**Sprint:** LOWCODE-MEGA-TRAIN-005
**Date:** 2026-05-20

## Full Regression

```
PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/ -q --tb=no
Result: 2636 passed, 3 skipped, 0 failed (83.90s)
```

## Targeted Tests (FormatAuthority + Evidence + Planner)

```
PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/unit/test_format_authority_store.py tests/unit/test_format_authority_no_stale_maps.py tests/unit/test_code_contract_validator.py tests/unit/test_format_capability.py tests/unit/test_format_map_completeness.py tests/unit/test_code_quality_sprint.py tests/unit/test_evidence_contract.py tests/unit/test_planner_loop.py -v --tb=short
Result: 602 passed, 0 failed (41.81s)
```

## Conservation / Denominator Tests

```
PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/unit/ -k "conservation or denominator" -v --tb=short
Result: 160 passed, 3 skipped, 0 failed (2.21s)
```

## Evidence Contract

- StrictEvidenceContractV8: 70 categories, 70 required
- All evidence contract tests pass (from targeted run)

## FormatContract Store Verification

```python
from plugin_examples.format_authority.store import load_contracts_from_json
n = load_contracts_from_json()
# Result: Loaded 42 contracts
# All 6 families covered: cells(9), words(8), pdf(19), diagram(2), email(1), slides(3)
```

## Test Fix Applied

- File: tests/unit/test_code_quality_sprint.py
- Fix: Added family="cells" to _infer_input_format calls to activate FormatContract path
- Verification: 4/4 tests pass after fix
