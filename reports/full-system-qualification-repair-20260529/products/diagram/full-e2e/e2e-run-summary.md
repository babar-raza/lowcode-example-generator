# E2E Run Summary: diagram

**Sprint ID:** full-system-qualification-repair-20260529
**Family:** diagram
**template_mode:** False
**skip_run:** False
**Verdict:** BLOCKED_BUILD_FAILED
**Failure Class:** GENERATOR_API_MISMATCH

## Result Summary

| Example | Restore | Build | Run | Status |
|---|---|---|---|---|
| diagram-diagram-converter | PASS | FAIL (7 errors) | N/A | BLOCKED |
| diagram-pdf-converter | PASS | FAIL (6 errors) | N/A | BLOCKED |

## Root Cause

Generated fixture code uses Aspose.Diagram API types that do not exist:
- `Aspose.Diagram.ShapeType` (enum not present in package)
- `XForm` constructor with 0 arguments (no default constructor)
- Implicit conversion of `double` to `Aspose.Diagram.DoubleValue`

## Halt Record

This family was HALTED per Lane 4 protocol. No heal was possible without
LLM re-generation of fixture code (out of scope).

## Prior Sprint Note

Prior sprint showed diagram as PASS but used `template_mode=True, skip_run=True`.
That validation was skipped — the prior PASS was not a real build result.
This sprint is the FIRST sprint to confirm diagram build failure.
