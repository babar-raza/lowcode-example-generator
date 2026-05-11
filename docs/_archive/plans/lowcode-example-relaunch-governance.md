# LowCode Example Generator: Example Relaunch Governance

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** GOVERNANCE_ACTIVE

---

## Relaunch Workflow State Machine

```
PLANNED_NOT_ATTEMPTED
  --[generate]--> GENERATION_ATTEMPTED
    --[LLM success]--> CODE_GENERATED
      --[build pass]--> BUILD_PASSED
        --[run pass]--> RUN_PASSED
          --[reviewer pass]--> REVIEWED (PASS)
            --[package]--> PR_DRY_RUN_READY
              --[APPROVE_LIVE_PR]--> PUBLISHED
                --[post-merge checkout]--> POST_MERGE_VERIFIED
    --[LLM fail]--> GENERATION_FAILED --> backlog entry created
    --[build fail]--> BUILD_FAILED --> repair attempt
    --[run fail]--> RUN_FAILED --> repair attempt
    --[reviewer fail]--> REVIEWED (FAIL) --> repair attempt

GENERATION_FAILED / BUILD_FAILED / RUN_FAILED
  --[root cause identified, fix applied]--> RELAUNCH_READY
  --[relaunch, max 3 attempts]--> RELAUNCH_ATTEMPTED
    --[pass all gates]--> RELAUNCH_PASSED --> PR_DRY_RUN_READY --> ...
    --[fail after 3 attempts]--> RELAUNCH_FAILED
      --[product API proven insufficient]--> DROPPED_WITH_EVIDENCE
      --[fix not yet available]--> BLOCKED (with taskcard + evidence)

NON_RUNNABLE_WITH_SOURCE_OF_TRUTH (permanent; no relaunch path)
DROPPED_WITH_EVIDENCE (no relaunch unless evidence is formally challenged)
```

---

## Relaunch Rules

1. **Root cause required:** No relaunch without a documented root cause in the backlog entry.
2. **Fix required:** No relaunch without a specific code/fixture/prompt fix applied and verified.
3. **Max 3 attempts:** After 3 relaunch failures with the same root cause, escalate to BLOCKED or DROPPED.
4. **Audit trail:** Every attempt recorded in backlog with `attempt_count`, `last_failure_stage`, `fix_applied`.
5. **Dry-run first:** RELAUNCH_PASSED examples go through PR dry-run packaging before live PR creation.
6. **Denominator sync:** After PR merge, denominator `published_count` must be updated.
7. **DROPPED governance:** DROPPED_WITH_EVIDENCE requires backlog entry with evidence file path (not just a comment).

---

## Relaunch Readiness Table

### Words Deferred Examples

| Example | State | Blocker | Relaunch Allowed | Prerequisite |
|---------|-------|---------|-----------------|-------------|
| words-comparer | DROPPED_WITH_EVIDENCE | RC-007: MISSING_PAIR_FIXTURE | NO | Implement pair fixture in fixture_registry.py |
| words-merger | DROPPED_WITH_EVIDENCE | RC-007: MISSING_PAIR_FIXTURE | NO | Same as comparer |
| words-mailmerger | DROPPED_WITH_EVIDENCE | RC-008: MISSING_TEMPLATE_FIXTURE | NO | Create template DOCX fixture |
| words-splitter-split | DROPPED_WITH_EVIDENCE | RC-009: MISSING_ENUM_STRATEGY | NO | SplitCriteria enum discovery |
| words-processor | DROPPED_WITH_EVIDENCE | CLASSIFICATION_GAP | NO | NEW-07 full classification |
| words-reportbuilder | DROPPED_WITH_EVIDENCE | CLASSIFICATION_GAP | NO | NEW-07 full classification |

### PDF Deferred Examples (pilot deferred)

| Example | State | Blocker | Relaunch Allowed | Prerequisite |
|---------|-------|---------|-----------------|-------------|
| pdf-docconverter | PLANNED_NOT_ATTEMPTED | pilot_deferred | YES (after R8) | R10 sprint; format-specific validation |
| pdf-formeditor | PLANNED_NOT_ATTEMPTED | MISSING_FIXTURE | NO | Form-fields PDF fixture |
| pdf-formexporter | PLANNED_NOT_ATTEMPTED | MISSING_FIXTURE + CLASSIFICATION_GAP | NO | Fixture + classification |
| pdf-formflattener | PLANNED_NOT_ATTEMPTED | MISSING_FIXTURE | NO | Form-fields PDF fixture |
| pdf-formimporter | PLANNED_NOT_ATTEMPTED | MISSING_PAIR_FIXTURE | NO | Pair fixture for form import |
| pdf-html | PLANNED_NOT_ATTEMPTED | WRONG_FIXTURE_SHAPE | MAYBE | Define HTML input strategy |
| pdf-imageextractor | PLANNED_NOT_ATTEMPTED | CLASSIFICATION_GAP | MAYBE | Image output validation |
| pdf-jpeg | PLANNED_NOT_ATTEMPTED | CLASSIFICATION_GAP | MAYBE | JPEG format validation |
| pdf-ofd | PLANNED_NOT_ATTEMPTED | MISSING_FIXTURE (OFD format) | NO | OFD format fixture |
| ~8 more converters | PLANNED_NOT_ATTEMPTED | CLASSIFICATION_GAP | MAYBE | Format-specific validation |
| pdf-barcode, pdf-qrcode | PLANNED_NOT_ATTEMPTED | CLASSIFICATION_GAP | MAYBE | Barcode output validation |
| pdf-signaturevalidator | PLANNED_NOT_ATTEMPTED | MISSING_FIXTURE (signed PDF) | NO | Signed PDF fixture |

---

## R6.5 Actions Required

**This sprint adds all missing tracking entries:**

1. **PDF completion queue:** Add 21 WORKFLOW_ROOT types with state `PLANNED_NOT_ATTEMPTED`
2. **Words completion queue:** Add 6 explicitly deferred types with state `DROPPED_WITH_EVIDENCE`; add 15 unclassified types with state `PLANNED_NOT_ATTEMPTED` (pending classification)
3. **Supersede RC-005:** Mark stale Splitter runtime failure record
4. **Verify denominator equations** for all 3 families using 9-term formula
5. **Run tests** to confirm no regressions from queue expansion

---

## Post-Merge Failure Policy

If a future post-merge checkout validation fails:
1. **Immediately:** Open incident record in `workspace/verification/latest/families/{family}/post-merge-failure-incident.json`
2. **Rollback:** Document merge SHA; request revert from maintainer if critical
3. **Root cause:** Run `dotnet build` and `dotnet run` locally on the merged branch
4. **Fix:** Create new branch, fix example, PR, re-review, re-merge
5. **Re-verify:** Run post-merge checkout validation again on new merge
6. **Evidence:** Update post-merge clean checkout validation JSON with resolution

---

## Relaunch Command Templates

```bash
# Relaunch for specific family (tier 5 = full LLM + build + run + reviewer)
PYTHONPATH=src EXAMPLE_REVIEWER_PATH="$EXAMPLE_REVIEWER_PATH" \
  .venv/Scripts/python.exe -m plugin_examples run \
  --family {family} --tier 5 --promote-latest

# Relaunch with dry-run only (no reviewer)
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family {family} --tier 5 --dry-run --promote-latest

# Verify post-relaunch state
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples release-status \
  --families {family} --promote-latest

# Run denominator tests
PYTHONPATH=src .venv/Scripts/python.exe -m pytest \
  tests/unit/test_denominator_model.py tests/unit/test_completion_queue.py -v
```
