# Lane B3 — Obsolete API Review

Sprint: `lowcode-multi-mega-train-20260530`
Date: 2026-05-30

## Subject: `Page.DrawEllipse()` vs `Page.DrawOwal()` in Aspose.Diagram

### Claim Under Review

Reviewer flagged that `Page.DrawEllipse` is reportedly obsolete in Aspose.Diagram, with replacement `Page.DrawOwal`.

### Evidence

#### Build/Run Results for Diagram Examples

Both diagram examples (`diagram-diagram-converter`, `diagram-pdf-converter`) **PASS** with exit_code=0:

From `workspace/verification/latest/families/diagram/validation-results.json`:
```json
{
  "total": 2,
  "passed": 2,
  "failed": 0
}
```

Both restore, build, and run with no failures. This means `DrawEllipse` compiles without error.

#### Current Code

`workspace/runs/pilot-diagram-20260529-221021/generated/diagram/diagram-diagram-converter/Program.cs`:
```csharp
long shapeId = page.DrawEllipse(1.0, 1.0, 2.0, 2.0);
```

#### Analysis

1. **Not a build error**: `DrawEllipse` produces at most a CS0618 `[Obsolete]` warning. CS0618 is a warning, not an error. The build succeeds (exit_code=0).

2. **`DrawOwal` name is unusual**: The Aspose.Diagram API for drawing oval shapes uses `DrawEllipse`. The name `DrawOwal` does not appear in the Aspose.Diagram public API surface as documented. "Owal" appears to be a non-standard spelling (Polish: "owal" = oval). If this method exists, it is not confirmed in any harness run.

3. **Durable Fix was specifically `DrawEllipse` returning `long`**: The DEF-009 durable fix in the prior sprint established `page.DrawEllipse(1.0, 1.0, 2.0, 2.0)` returning `long` shapeId as the CORRECT pattern. This fix was harness-validated.

4. **Risk of blind replacement**: Replacing `DrawEllipse` with `DrawOwal` or `DrawOval` without a successful build+run proof would introduce a regression. The existing examples already pass.

### Decision: NO CHANGE

- `DrawEllipse` is retained as the verified working pattern.
- If a future API version enforces `DrawEllipse` as a hard error ([Obsolete(error: true)]), this should be addressed with a fresh harness run.
- `DrawOwal` is unverified. No harness evidence that this method name exists in the installed package version.

### Action Item (Future)

If a future sprint's build produces CS0618 warning promotion to error, or if `DrawEllipse` is removed from the API:
1. Run `dotnet build` and check for CS0618 warning on DrawEllipse
2. Try `page.DrawOval(...)` (not DrawOwal — likely the correct spelling) in a fresh harness
3. Update the template in `code_generator.py` if confirmed

### Status: CLOSED — NO CHANGE REQUIRED
