# Family-Scoped Evidence Layout Plan

**Date:** 2026-05-05
**Sprint:** Family-Scoped Evidence Promotion and Latest-State Isolation

---

## Evidence Layout Policy

### 1. Run-Scoped (canonical, never promoted automatically)
```
workspace/runs/{run_id}/evidence/latest/{file}
```
Always authoritative. Never deleted. One directory per run.

### 2. Family-Scoped Promoted (primary — NEW)
```
workspace/verification/latest/families/{family}/{file}
```
Written by `promote_latest`. Each family writes only to its own subdirectory. Cross-family contamination impossible. Includes `_evidence_metadata.json`.

### 3. Global Promoted (unchanged)
```
workspace/verification/latest/{file}
```
Written by multi-family commands only (`discover-lowcode --all`, `release-status`, etc.). NOT written by single-family runs.

### 4. Backward-Compat Alias (deprecated)
```
workspace/verification/latest/{file}        ← still written for legacy readers
workspace/verification/latest/_last_promoted_by.json  ← deprecation notice
```
Legacy readers continue to work. New readers prefer `families/{family}/`.

---

## Files by Scope

### Always Family-Scoped (→ `families/{family}/`)
| File | Why |
|---|---|
| validation-results.json | build/run results for one family run |
| pr-candidate-manifest.json | PR candidates for one family run |
| example-gate-results.json | per-example gates for one family run |
| example-reviewer-results.json | reviewer output for one family run |
| aggregate-gate-results.json | aggregate gates for one family run |
| api-consumer-relationships.json | API consumers for one family |
| api-delta-report.json | API delta for one family version |
| blocked-scenarios.json | blocked scenarios for one family |
| example-impact-report.json | impact for one family |
| fixture-strategy-plan.json | fixture strategy for one family |
| gate-results.json | overall verdict for one family run |
| generated-fixtures.json | fixtures for one family run |
| llm-fewshot-patterns.json | LLM patterns for one family |
| llm-preflight.json | LLM preflight for one family run |
| plugin-type-role-classification.json | role classification for one family |
| publishing-report.json | publishing status for one family run |
| repair-attempts.json | repair history for one family run |
| reviewer-preflight.json | reviewer preflight for one family run |
| runnable-entrypoint-scores.json | entrypoint scores for one family |
| scenario-feedback-updates.json | scenario feedback for one family run |
| scenario-input-format-map.json | input format map for one family run |
| stale-existing-examples.json | stale detection for one family |

### Already Family-Prefixed (safe at top-level, no collision)
`{family}-source-of-truth-proof.json`, `{family}-live-pr-result.json`, etc.

### Global (top-level only)
`all-family-lowcode-discovery.json`, `open-taskcard-closure-matrix.json`, `family-generation-readiness-rank.json`, `release-status.json`, etc.

---

## Reader Preference Policy

```python
def resolve_family_evidence_path(verification_dir, family, filename) -> Path:
    """Prefer families/{family}/ over top-level legacy path."""
    family_path = verification_dir / "latest" / "families" / family / filename
    if family_path.exists():
        return family_path
    legacy = verification_dir / "latest" / filename
    if legacy.exists():
        logger.warning("Reading %s from deprecated top-level path", filename)
        return legacy
    return family_path  # caller handles missing
```

---

## Implementation Files

| File | Action |
|---|---|
| `src/plugin_examples/evidence_layout.py` | NEW — layout constants + `promote_family_evidence()` + `resolve_family_evidence_path()` |
| `src/plugin_examples/runner.py` | MODIFY — call `promote_family_evidence()` in promote_latest block |
| `src/plugin_examples/publisher/publisher.py` | MODIFY — `_verify_evidence` uses `resolve_family_evidence_path()` |
| `tests/unit/test_discovery_readiness_preservation.py` | MODIFY — add 9 family isolation tests |
