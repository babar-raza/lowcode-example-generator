# Sprint 46 Contradiction Map

Reviewed by: Sprint 47 Lane 0
HEAD: fe5fb4e

## CAVEAT-01: 14 package artifacts misclassified as evidence (MEDIUM)

**Source**: final-dirty-state.json reports `evidence_dirty_count=21`
**Actual**: 7 are workspace/verification/latest JSON files (true evidence), 14 are workspace/pr-dry-run PDF/PFX files (package artifacts)
**Fix**: Lane A — add `package_artifact_count` to DirtyState, classify `workspace/pr-dry-run/` separately

## CAVEAT-02: Cycle 2 executes handlers before idempotency stop (LOW)

**Source**: planner-loop-ledger.json shows 12 total executions across 2 cycles
**Actual**: Cycle 2 fingerprint matches cycle 1 before any handlers run. All 6 cycle-2 handlers are wasted no-ops.
**Fix**: Lane C — pre-execution fingerprint check

## CAVEAT-03: Evidence contract proof is aspirational (MEDIUM)

**Source**: evidence-contract-validation-proof.txt says "Validation will be run against the final bundle"
**Actual**: No actual PASS/FAIL result recorded against the ZIP
**Fix**: Lane D — run real validation, record result

## CAVEAT-04: PDF recovery packet lacks operational detail (LOW)

**Source**: pdf-conflict-free-recovery-packet.md
**Actual**: Commands present but no phased execution, validation gates, or rollback plan
**Fix**: Lane E — produce approval-ready runbook

## CAVEAT-05: 14 dirty pr-dry-run binaries have unknown provenance (LOW)

**Source**: git diff --stat shows 14 modified binary files
**Actual**: 13/14 have identical byte size (metadata-only changes). 1 file (signature/output.pdf) changed by 36 bytes.
**Fix**: Lane B — inspect provenance and classify each file
