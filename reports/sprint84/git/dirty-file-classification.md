Sprint 84 — Dirty File Classification
========================================
Date: 2026-05-24
Author: Lane H

## Dirty Files at Sprint Start (git status --short)

| File | Category | Classification |
|------|----------|----------------|
| workspace/verification/latest/cells-readme-backfill-simulation.json | GENERATED_WORKSPACE_STATE | Expected — gitignored, pipeline-managed |
| workspace/verification/latest/cells-root-readme-audit.json | GENERATED_WORKSPACE_STATE | Expected — gitignored, pipeline-managed |
| workspace/verification/latest/cells-root-readme-render-result.json | GENERATED_WORKSPACE_STATE | Expected — gitignored, pipeline-managed |
| workspace/verification/latest/release-status.json | GENERATED_WORKSPACE_STATE | Expected — gitignored, pipeline-managed |
| workspace/verification/latest/words-readme-backfill-simulation.json | GENERATED_WORKSPACE_STATE | Expected — gitignored, pipeline-managed |
| workspace/verification/latest/words-root-readme-audit.json | GENERATED_WORKSPACE_STATE | Expected — gitignored, pipeline-managed |
| workspace/verification/latest/words-root-readme-render-result.json | GENERATED_WORKSPACE_STATE | Expected — gitignored, pipeline-managed |

## Classification Summary
- GENERATED_WORKSPACE_STATE: 7 files (ALL dirty files)
- Source file changes: 0
- Unexpected dirty files: 0

## Governance Exception
workspace/verification/latest/ is covered by the GENERATED_WORKSPACE_STATE governance exception.
These files are gitignored and expected to show as dirty after pipeline runs.
See: Historical Evidence Exception Policy v1.0 (Sprint 75).

## Sprint 84 Source Changes
Files modified as part of Sprint 84 bundle:
- src/plugin_examples/evidence_validator.py (4 new rules 116-119, updated docstring)
- tests/unit/test_evidence_validator.py (8 new tests, 5 count assertions updated)
These will be staged for the bundle commit.
