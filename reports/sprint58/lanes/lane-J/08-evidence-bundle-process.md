# Process: Evidence Bundle Creation and Validation

**Process ID:** LANE-J-08
**Version:** Sprint 58
**Date:** 2026-05-21

---

## Overview

Every sprint must close with a validated evidence bundle. The bundle contains all evidence files with SHA256 checksums, a bundle manifest, and a final verdict document.

---

## Bundle Requirements

| Requirement | Value |
|-------------|-------|
| Minimum file count | 25 files |
| Manifest format | JSON with SHA256 per file + overall bundle SHA256 |
| Blocking EC categories | All must be PRESENT at closure |
| Non-blocking EC | Can be PRESENT or PENDING |

---

## Bundle Creation Process

### Step 1: Collect All Evidence Files

Enumerate all files in `reports/sprint58/` recursively. Include:
- All `.md`, `.json`, `.log`, `.txt` files
- Per-example directory files
- Lane-specific evidence files

### Step 2: Compute SHA256 per File

For each file:
```python
import hashlib
with open(path, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()
```

### Step 3: Validate Evidence Contract

Run bundle validator before writing manifest:

```python
def validate_bundle(contract, files):
    errors = []
    # Rule: no_pending_blocking_categories
    for ec in contract["required_evidence_categories"]:
        if ec["blocking"] and ec["status"] == "PENDING":
            errors.append(f"FAILURE: {ec['id']} is blocking but PENDING")
    # Rule: bundle_has_min_25_files
    if len(files) < 25:
        errors.append(f"FAILURE: Only {len(files)} files (min 25 required)")
    # Rule: test_log_required
    if not any("test-run.log" in f for f in files):
        errors.append("FAILURE: test-run.log missing")
    return errors
```

### Step 4: Write Bundle Manifest

Write to: `reports/sprint58/bundle-manifest.json`

```json
{
  "bundle_id": "sprint58-closure-repair-42-42-regeneration-20260521",
  "created_at": "...",
  "total_files": 50,
  "overall_sha256": "...",
  "files": [
    {"path": "reports/sprint58/...", "sha256": "...", "size_bytes": 1234}
  ]
}
```

### Step 5: Write Final Verdict

Write to: `reports/sprint58/final-verdict.md`

---

## Bundle Validation Rules (All Must Pass)

| Rule | Severity |
|------|----------|
| `bundle_has_min_25_files` | FAILURE |
| `no_pending_blocking_categories` | FAILURE |
| `no_metadata_only_bundle` | FAILURE |
| `test_log_required` | FAILURE |
| `regeneration_ledger_per_example` | FAILURE |
| `package_authority_no_contract_only` | FAILURE |
| `lane_j_not_pending` | FAILURE |
| `git_status_end_required` | FAILURE |
| `commands_log_complete` | FAILURE |

---

## Acceptance Criteria

- `bundle-manifest.json` present with SHA256 per file
- `validate_bundle()` returns 0 errors
- Total file count ≥ 25
- `final-verdict.md` present with scorecard
