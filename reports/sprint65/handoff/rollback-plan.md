# Sprint 65 — Rollback Plan

Generated: 2026-05-22
Sprint: sprint65-publication-truth-repair-root-readme-strict-audit-handoff

## Scope

Sprint 65 is an evidence-only repair sprint. No live publication was performed.
No destination repo changes were made. All changes are to:
1. `reports/sprint65/` — evidence artifacts (git-tracked)
2. `src/plugin_examples/evidence_validator.py` — 10 new EV rules added
3. `tests/unit/test_evidence_validator.py` — updated rule counts, _make_bundle()

## Rollback Scenarios

### Scenario A: EV Rule Addition Rollback

If the 10 new Sprint 65 rules cause unexpected failures in future sprints:

1. Identify the specific rule causing the issue
2. Add the rule_id to the `exclude_rule_ids` parameter:
   ```python
   validator.validate(exclude_rule_ids={"content_audit_all_records_ready"})
   ```
3. Or revert only the specific rule method and its dispatch in `validate()`

**Git revert:** `git revert HEAD` (if committed as single commit) or selectively
revert `src/plugin_examples/evidence_validator.py`

### Scenario B: Content Audit Rollback

If `content-audit-final.json` is found to have errors:

1. Fix `scripts/build_content_audit_final.py`
2. Re-run: `python3 scripts/build_content_audit_final.py`
3. Re-generate dependent files (programcs-vs-authority-final.json, etc.)

### Scenario C: Remote Proof Index Rollback

If remote proof data is incorrect:

1. Read updated merge results from `workspace/verification/latest/`
2. Re-run the Phase 6 scripts to regenerate `remote-proof-index.json`
3. No remote mutations required (index is read-only evidence)

## Non-Rollback Scenarios

The following changes are intentional and should NOT be rolled back:
- Sprint 64 defect documentation (Phase 0 reports)
- Root README artifacts (Phase 1) — these are captures, not mutations
- Special-case placement proof (Phase 3) — documentation only
- PDF version policy decision (Phase 4) — policy documents, no code change

## Risk Assessment

| Change | Risk | Reversibility |
|--------|------|--------------|
| 10 new EV rules | LOW — only additive, excludable | HIGH |
| content-audit-final.json | LOW — evidence artifact | HIGH — re-run script |
| Remote proof index | LOW — read-only evidence | HIGH — re-capture |
| Test updates (rule counts) | LOW | HIGH — revert counts |

**Overall sprint risk: LOW** — No live publication, no remote mutations.
