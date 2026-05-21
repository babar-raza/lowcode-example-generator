# Sprint 61 Staging Plan

## Phase 1: Source Changes (commit 1)

Files to stage:
- `src/plugin_examples/evidence_validator.py` (modified — new semantic rules)
- `src/plugin_examples/__main__.py` (modified — EvidenceValidator + readme_audit_gate wiring)
- `tests/unit/test_evidence_validator.py` (modified — new semantic rule tests)
- `tests/unit/test_publish_pr_readme_gate.py` (new — publish-pr gate wiring tests)
- `tests/unit/test_pipeline_evidence_gate.py` (new — pipeline integration tests)

Commit message: `feat(sprint61): harden EvidenceValidator semantics + wire gates into pipeline`

## Phase 2: Sprint 61 Evidence Bundle (commit 2)

Files to stage:
- `reports/sprint61/` (all evidence files)

Commit message: `docs(sprint61): Sprint 61 closure bundle — false closure killed, pipeline gates active`

## Phase 3: Final Clean Proof (commit 3, micro-commit)

Files to stage:
- `reports/sprint61/git/final-clean-proof.txt` (captured AFTER commit 2)

Commit message: `chore(sprint61): final-clean-proof.txt — nonzero, branch+status confirmed`
