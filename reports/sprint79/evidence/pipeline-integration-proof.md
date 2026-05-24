# Pipeline Integration Proof — Sprint 79

**Date:** 2026-05-24
**Sprint:** 79 (Sprint 78 evidence authority repair)
**Supersedes:** Sprint 78 one-line assertion (S78-E4)

---

## Source Location

**File:** `src/plugin_examples/__main__.py`
**Line:** 1477
**Import:** `from plugin_examples.evidence_validator import EvidenceValidator as _EV`

---

## CLI Integration

The EvidenceValidator is wired into the `release-status` command via the `--validate-bundle` flag:

```
src/plugin_examples/__main__.py:309-313:
    rs_parser.add_argument(
        "--validate-bundle", metavar="BUNDLE_DIR", default=None,
        help=(
            "Run EvidenceValidator on a sprint bundle directory after computing release status. "
            "Prints a validation summary; exits 1 if the bundle fails any FAILURE-severity rule."
        ),
    )
```

**Execution path** (`src/plugin_examples/__main__.py:1475-1489`):
```python
# Optional: validate sprint evidence bundle
if getattr(args, "validate_bundle", None):
    from plugin_examples.evidence_validator import EvidenceValidator as _EV
    _bundle_dir = _Path(args.validate_bundle)
    _source_root = _Path(__file__).resolve().parent
    print(f"\nValidating bundle: {_bundle_dir}")
    _ev_result = _EV(bundle_dir=_bundle_dir, source_root=_source_root).validate()
    print(f"  Rules: {_ev_result.passed} passed, {_ev_result.failed} failed / {_ev_result.total_rules} total")
    for _r in _ev_result.rule_results:
        if not _r.passed:
            print(f"  [FAIL] {_r.rule_id}: {_r.failure_detail[:100]}")
    if not _ev_result.overall_valid:
        print(f"  Bundle INVALID — {_ev_result.failed} rule(s) failed")
        return 1
    print(f"  Bundle VALID — all {_ev_result.total_rules} rules pass")
```

---

## Key Integration Properties

1. **Import is lazy** (inside the if-block) — avoids circular import issues
2. **source_root is passed** — enables `evidence_validator_wired_in_pipeline` rule to scan source and confirm import exists
3. **Exit code 1 on failure** — validation is a hard gate, not advisory-only
4. **source_root = `__main__.py`'s parent** — resolves to `src/plugin_examples/`

---

## Verification: EvidenceValidator IS imported by pipeline source

```
src/plugin_examples/__main__.py:1477:
    from plugin_examples.evidence_validator import EvidenceValidator as _EV
```

This satisfies Rule `evidence_validator_wired_in_pipeline` (Rule 16).

---

## No Change from Sprint 77

The integration has been unchanged since Sprint 77 committed it. The Sprint 78 one-line assertion was correct in substance but insufficient as evidence. Sprint 79 makes the proof durable and inspectable.

---

## Source Hash

SHA256 of `src/plugin_examples/__main__.py` (Sprint 79 HEAD):
See `pipeline-integration-source-map.json` for exact hash.
