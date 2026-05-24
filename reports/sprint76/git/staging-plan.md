# Sprint 76 Staging Plan

**Date:** 2026-05-24

## Rule: Exact-path staging only. No broad `git add .` or `git add -A`.

## Files to Stage for Sprint 76 Bundle Commit

### Source / Test Changes (if any from Phase 4 EV hardening)

After adding EV rules 94-101:

| File | Reason |
|------|--------|
| src/plugin_examples/evidence_validator.py | New EV rules 94-101 |
| tests/unit/test_evidence_validator.py | New test methods for rules 94-101 |
| tests/unit/test_pipeline_evidence_gate.py | Updated _make_valid_bundle fixtures |

Stage with:
```
git add src/plugin_examples/evidence_validator.py
git add tests/unit/test_evidence_validator.py
git add tests/unit/test_pipeline_evidence_gate.py
```

### Sprint 76 Bundle

| Path | Reason |
|------|--------|
| reports/sprint76/ | All sprint76 artifacts |

Stage with:
```
git add reports/sprint76/
```

### Excluded (not staged)

| File | Reason |
|------|--------|
| workspace/verification/latest/*.json | GENERATED_WORKSPACE_STATE governance exception |

## Final Commit Message Pattern

```
feat(sprint76): EV 101/101, ECC {N}/{N}, {TESTS} tests — slides-compress validated, dirty-state repaired, sprint75 closure confirmed
```

## Second Commit (final-clean-proof.txt update)

After first commit, update reports/sprint76/git/final-clean-proof.txt with real SHA,
then:
```
git add reports/sprint76/git/final-clean-proof.txt
git commit -m "feat(sprint76): capture final-clean-proof.txt — sprint75 reopened, slides-compress validated, dirty-state repaired"
```
