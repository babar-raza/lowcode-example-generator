# Phase 2 — ECC Semantic Rule Repair

## Background

Sprint 63 ECC (`evidence_contract_computer.py`) had three brittle semantic validators
that produced false `SEMANTIC_FAILED` results for valid evidence files.
These bugs contributed to the EV/ECC disagreement documented in Phase 1.

## Bug 1: pytest "0 failed" Detection

### Old behavior
```python
_TEST_ZERO_FAILED_PATTERN = re.compile(r"\b0 failed\b|\b0\s+fail", re.IGNORECASE)
...
if "0 failed" in semantic.lower():
    if not _TEST_ZERO_FAILED_PATTERN.search(text):
        return "File does not contain '0 failed' test result indicator"
```

### Problem
pytest only prints `"N failed"` when there ARE failures. With zero failures:
```
2976 passed, 3 skipped, 10 subtests passed in 96.19s
```
There is no `"0 failed"` string. The old pattern always returned SEMANTIC_FAILED
for passing pytest test logs.

### Fix
```python
_TEST_ZERO_FAILED_LITERAL_PATTERN = re.compile(r"\b0 failed\b|\b0\s+fail", re.IGNORECASE)
_TEST_PASSED_PATTERN = re.compile(r"\b\d+ passed\b", re.IGNORECASE)
_TEST_FAILED_COUNT_PATTERN = re.compile(r"\b\d+ failed\b", re.IGNORECASE)
...
# Accept either literal "0 failed" OR "N passed" with no "N failed"
has_literal_zero_failed = bool(_TEST_ZERO_FAILED_LITERAL_PATTERN.search(text))
has_passed_no_failures = (
    bool(_TEST_PASSED_PATTERN.search(text))
    and not bool(_TEST_FAILED_COUNT_PATTERN.search(text))
)
if not has_literal_zero_failed and not has_passed_no_failures:
    return "File does not contain passing test result indicator"
```

### Tests added
- `test_pytest_passed_no_failed_line_is_passing` — `"2976 passed, 3 skipped in 96.19s"` → PRESENT
- `test_pytest_n_passed_in_Xs_passes` — `"76 passed in 12.07s"` → PRESENT
- `test_log_with_failures_still_fails` — `"10 passed, 3 failed in 5s"` → SEMANTIC_FAILED
- `test_empty_log_no_passed_no_failed_fails` — no test indicators → SEMANTIC_FAILED

## Bug 2: "6 families" Dict-Key Check

### Old behavior
```python
if "6 families" in semantic.lower():
    data = json.loads(text)
    families = data.get("families", [])  # Returns [] for dict-keyed JSON
    if len(families) < 6:
        return f"Only {len(families)} families listed (expected 6)"
```

### Problem
`package-artifact-index.json` uses family names as top-level keys:
```json
{"cells": {...}, "diagram": {...}, "email": {...}, "pdf": {...}, "slides": {...}, "words": {...}}
```
`data.get("families", [])` returns `[]` → always SEMANTIC_FAILED.

### Fix
```python
_KNOWN_FAMILY_NAMES = {"cells", "diagram", "email", "pdf", "slides", "words"}
...
families_val = data.get("families", None)
if families_val is not None:
    count = len(families_val) if isinstance(families_val, (list, dict)) else 0
else:
    # New format: top-level string keys are family names
    count = sum(1 for k in data if isinstance(k, str) and k in _KNOWN_FAMILY_NAMES)
if count < 6:
    return f"Only {count} families listed (expected 6)"
```

### Tests added
- `test_dict_keyed_6_families_passes` — 6 top-level family keys → PRESENT
- `test_dict_keyed_only_4_families_fails` — 4 keys → SEMANTIC_FAILED
- `test_legacy_families_list_key_still_works` — `"families": [...]` format → PRESENT

## Bug 3: Contract Format Field Names

### Old behavior
```python
contract_id = contract.get("sprint_id", "unknown")
for cat in contract.get("required_evidence_categories", []):
```

### Problem
Sprint 64 evidence-contract.json uses `"contract_id"` and `"categories"` but ECC
only read `"sprint_id"` and `"required_evidence_categories"`.

### Fix
```python
contract_id = contract.get("sprint_id") or contract.get("contract_id", "unknown")
cat_list = contract.get("required_evidence_categories") or contract.get("categories", [])
```

Both formats now supported. Sprint 63 (legacy) and Sprint 64 (new) contracts both work.

### Tests added
- `test_new_format_contract_id_and_categories` — new format reads correctly
- `test_legacy_format_still_works` — old format still works

## Test Results

See `semantic-rule-test-results.txt`. All ECC tests pass (0 failed).

## Acceptance

No valid evidence fails semantic validation due to brittle string matching.
Valid pytest test logs (pytest format) are accepted. Dict-keyed package artifact
indexes with 6 families are accepted. Both contract formats are supported.
