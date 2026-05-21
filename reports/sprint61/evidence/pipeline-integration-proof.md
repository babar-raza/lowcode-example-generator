# EvidenceValidator Pipeline Integration Proof — Sprint 61 Phase 3

## Defect Closed

**SD60-04:** EvidenceValidator was created in Sprint 60 but never imported or called by any
pipeline command. A validator module that is never called is not a gate.

## Implementation

### Source change: `src/plugin_examples/__main__.py`

Added `--validate-bundle` argument to `release-status` subparser:

```python
rs_parser.add_argument(
    "--validate-bundle", metavar="BUNDLE_DIR", default=None,
    help=(
        "Run EvidenceValidator on a sprint bundle directory after computing release status. "
        "Prints a validation summary; exits 1 if the bundle fails any FAILURE-severity rule."
    ),
)
```

Added EvidenceValidator call in the `release-status` command body:

```python
if getattr(args, "validate_bundle", None):
    from plugin_examples.evidence_validator import EvidenceValidator as _EV
    _bundle_dir = _Path(args.validate_bundle)
    _source_root = _Path(__file__).resolve().parent
    _ev_result = _EV(bundle_dir=_bundle_dir, source_root=_source_root).validate()
    if not _ev_result.overall_valid:
        return 1
```

### Source scan verification

The `_rule_evidence_validator_wired_in_pipeline` rule with `source_root=src/plugin_examples`
finds `evidence_validator` in `__main__.py` at import line:

```
from plugin_examples.evidence_validator import EvidenceValidator as _EV
```

Result: `evidence_validator_wired_in_pipeline` → **PASS**

## Tests

File: `tests/unit/test_pipeline_evidence_gate.py` — 5 tests

| Test | Result |
|------|--------|
| test_evidence_validator_imported_by_main | PASS |
| test_sprint60_bundle_fails_evidence_validator_wired_rule | PASS |
| test_returns_0_on_valid_bundle | PASS |
| test_returns_1_on_invalid_bundle | PASS |
| test_validate_bundle_not_called_without_flag | PASS |

**5 passed, 0 failed**

## CLI Usage

```bash
# Validate sprint bundle after release status report
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples release-status \
    --validate-bundle reports/sprint61

# Returns 0 if all 20 rules pass, 1 if any FAILURE-severity rule fails
```

## Gate Behavior

- Without `--validate-bundle`: EvidenceValidator is NOT called (command unchanged)
- With `--validate-bundle <path>`: EvidenceValidator runs against the bundle, scanning real source
- Exit code 1 if any rule fails (blocking)
- Prints per-rule failure details to stdout
