# Sprint 80 -- Dirty File Classification

## Source Files (MUST commit)

| File | Classification | Reason |
|------|---------------|---------|
| src/plugin_examples/evidence_validator.py | SPRINT_SOURCE_CHANGE | EV Rule 111 added (closes S79-B1) |
| tests/unit/test_evidence_validator.py | SPRINT_TEST_CHANGE | 5 new tests for Rule 111, count assertions updated |

## Workspace State Files (GENERATED_WORKSPACE_STATE governance exception)

| File | Classification |
|------|---------------|
| workspace/verification/latest/cells-readme-backfill-simulation.json | GENERATED_WORKSPACE_STATE |
| workspace/verification/latest/cells-root-readme-audit.json | GENERATED_WORKSPACE_STATE |
| workspace/verification/latest/cells-root-readme-render-result.json | GENERATED_WORKSPACE_STATE |
| workspace/verification/latest/family-repo-access-resolution.json | GENERATED_WORKSPACE_STATE |
| workspace/verification/latest/release-status.json | GENERATED_WORKSPACE_STATE |
| workspace/verification/latest/words-readme-backfill-simulation.json | GENERATED_WORKSPACE_STATE |
| workspace/verification/latest/words-root-readme-audit.json | GENERATED_WORKSPACE_STATE |
| workspace/verification/latest/words-root-readme-render-result.json | GENERATED_WORKSPACE_STATE |

## Report Directory (SPRINT_REPORT)

| Item | Classification |
|------|---------------|
| reports/sprint80/ | SPRINT_REPORT — untracked directory, will be committed in sprint bundle |

---
**Classification authority**: Sprint 80 dirty-file-classification.md  
**Policy**: workspace/verification/latest/ files are always GENERATED_WORKSPACE_STATE and are not committed per governance exception.  
**Source changes**: 2 files — evidence_validator.py (+Rule 111) and test_evidence_validator.py (+5 tests, count updates).
