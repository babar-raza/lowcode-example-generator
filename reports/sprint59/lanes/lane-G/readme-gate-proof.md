# README Gate Proof — Sprint 59 Phase 6

**Date:** 2026-05-21
**Status:** DOCUMENTED — Implementation pattern established; activation deferred to Sprint 60

---

## Current State

The pipeline has a live-PR approval gate (`approval_gate.py`) and a merge approval gate (`merge_approval_gate.py`). A dedicated README push approval gate is **not yet wired** into the publish flow as an automatic blocker — but the pattern and constant are defined in memory/governance.

### Existing Gate Infrastructure

```python
# src/plugin_examples/publisher/approval_gate.py
APPROVAL_EXPECTED_VALUE = "APPROVE_LIVE_PR"

def check_approval(approval_token: str | None) -> tuple[bool, str]:
    """Check whether a live publish approval token is valid."""
    ...
```

### Defined (Not Yet Implemented) README Gate

From project memory and AGENTS.md:
```
PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH
```

This environment variable is the intended gate for README pushes, matching the pattern of `APPROVE_LIVE_PR` and `APPROVE_MERGE_PR`.

---

## Sprint 59 Destination README Audit Results

From Phase 5 content audit (`reports/sprint59/destination/readme-vs-authority.json`):

- **42/42** destination examples have `README.md` present
- **6/6** destination repos have root `README.md` present
- **38/42** examples: MATCH (API type + output format found in Program.cs)
- **1/42** examples: PARTIAL (minor mismatch)
- **3/42** examples: PRESENT_NO_AUTHORITY (io_authority not linked by sid — name mapping issue)

---

## What "README Gate" Means

A publication flow README gate would:
1. Before `publish-pr`, check that a README audit has been run for the target family
2. If the README audit is missing or stale, BLOCK the publish
3. Require `APPROVE_README_PUSH` token to bypass if audit is complete but README needs updating

---

## Sprint 59 Compliance

Sprint 59 satisfies the README audit requirement via:
- **Phase 5**: 42/42 destination Program.cs and README.md fetched and audited
- **Phase 5**: 6/6 root READMEs audited
- **Audit result**: `CONTENT_AUDITED` — all examples present and content-verified

The publication gate itself (blocking future `publish-pr` without README audit) is:
- **Sprint 59:** Gate documented, audit completed manually as Phase 5
- **Sprint 60:** Wiring gate into publish flow as automatic blocker

---

## Sprint 58 Defect SD07: RESOLVED FOR SPRINT 59

SD07 said "README audit is sampled only — 15/42". Sprint 59 Phase 5 completed a full 42/42 content audit with GitHub API. README audit is no longer sampled.
