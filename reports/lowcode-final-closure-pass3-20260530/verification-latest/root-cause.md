# Root Cause — LANE 6: Diagram Publisher Stale State

**Sprint**: lowcode-final-closure-pass3-20260530

## Root Cause

The `workspace/verification/latest/families/diagram/` directory retained evidence files
from the pre-durable-fix run `pilot-diagram-final-20260528`. In that run:

- `gate_generation` was **BLOCKED** because `new Shape()` / `XForm.PinX.Value` patterns
  were missing required API calls (`DrawEllipse`, `XForm.PinX.Value = ...`).
- The pipeline stored this stale evidence in the family workspace directory.
- The diagram family was subsequently fixed via DEF-004 (DrawEllipse) and DEF-005
  (XForm.PinX.Value) in the generator source (code_generator.py HEAD:35005a6).
- The canonical durable-fix run `pilot-diagram-20260529-221021` produced `gate_generation: passed`
  and validated 2/2 examples (restore/build/run all exit_code=0).
- However, the canonical run's evidence was **never promoted** to the family workspace
  directory after the durable-fix sprint. The workspace remained stale.

## Impact

The stale state caused:
1. `publishing-report.json` to show `evidence_verified: false` and
   `blocked_reason: "gate verdict not publishable: BLOCKED_GENERATION"`
2. The publication dry-run for diagram appeared blocked due to generator failure,
   rather than the correct reason (approval gate not set).
3. Any audit reading the workspace family directory would see a false failure state.

## Fix Applied

Promoted canonical run evidence files from
`workspace/runs/pilot-diagram-20260529-221021/evidence/latest/` to
`workspace/verification/latest/families/diagram/`:

| File | Before (stale) | After (canonical) |
|------|---------------|-------------------|
| gate-results.json | gate_generation: blocked | gate_generation: passed |
| publishing-report.json | evidence_verified: false, BLOCKED_GENERATION | evidence_verified: true |
| validation-results.json | not verified | 2/2 passed |
| pr-candidate-manifest.json | diagram paths → pilot-diagram-final-20260528 | diagram paths → pilot-diagram-20260529-221021 |

## Post-Fix State

- `gate_generation`: **passed**
- `gate_build`: **passed**
- `gate_run`: **passed**
- `gate_reviewer`: failed (non-required — reviewer unavailable)
- `validation`: 2/2 passed (diagram-diagram-converter, diagram-pdf-converter)
- `publishing_report.status`: blocked (reason: approval gate — expected)
- Stale BLOCKED_GENERATION: **RESOLVED**
