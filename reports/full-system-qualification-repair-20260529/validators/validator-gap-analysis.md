# Validator Gap Analysis

**Sprint ID:** full-system-qualification-repair-20260529
**Date:** 2026-05-29T00:00:00Z

## Gaps Found in Prior Sprint

The prior system-qualification sprint overclaimed because the validator did not
enforce the following invariants:

- R-NEW-001: Rejects final verdicts that claim full qualification when skip_run=True was used in any E2E run
- R-NEW-002: Rejects final verdicts that claim full qualification when any build.log contains BUILD_NOT_RUN
- R-NEW-003: Rejects full qualification claims when validation stage was skipped in any family run
- R-NEW-004: Reviewer unavailability must have explicit governed fallback proof; reviewer=skipped without fallback is FATAL
- R-NEW-005: Publisher dry-run must be executed; publisher=skipped is FATAL for full qualification
- R-NEW-006: Final verdict may not reference external workspace paths as evidence if those paths are not in the evidence ZIP
- R-NEW-007: No product may remain in PENDING state when final verdict is issued

## Gap Closure Status

All 7 rules documented above are specified in this sprint.
Implementation in evidence_validator.py is planned for the next engineering sprint.
This sprint documents the gap analysis as a pre-requisite for implementation.
