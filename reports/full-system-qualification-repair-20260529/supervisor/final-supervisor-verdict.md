# Final Supervisor Verdict

**Sprint ID:** full-system-qualification-repair-20260529
**Date:** 2026-05-29T00:00:00Z

## Summary

| Family | Verdict | Passed | Failed | Total |
|---|---|---|---|---|
| cells | PARTIAL_PR_DRY_RUN_READY | 7 | 2 | 9 |
| diagram | BLOCKED_BUILD_FAILED | 0 | 2 | 2 |
| email | PR_DRY_RUN_READY | 1 | 0 | 1 |
| pdf | PARTIAL_PR_DRY_RUN_READY | 17 | 2 | 19 |
| slides | PR_DRY_RUN_READY | 3 | 0 | 3 |
| words | PARTIAL_PR_DRY_RUN_READY | 7 | 1 | 8 |

## Passing Families (5)

- **cells**: PARTIAL_PR_DRY_RUN_READY — 7/9 examples built and ran successfully; 2 had runtime output mismatches
- **email**: PR_DRY_RUN_READY — 1/1 example built and ran successfully
- **pdf**: PARTIAL_PR_DRY_RUN_READY — 17/19 examples built and ran successfully; 2 had runtime issues
- **slides**: PR_DRY_RUN_READY — 3/3 examples built and ran successfully
- **words**: PARTIAL_PR_DRY_RUN_READY — 7/8 examples built and ran successfully; 1 had runtime output mismatch

## Blocked Families (1)

- **diagram**: BLOCKED_BUILD_FAILED — Both examples failed build. Root cause: GENERATOR_API_MISMATCH — generated fixture code uses Aspose.Diagram.ShapeType (does not exist), incorrect XForm constructor, double->DoubleValue type mismatch. Requires LLM re-generation (out of scope).

## Statistics

- Total examples: 42
- Total passed: 35
- Total failed: 7
- Passing families: 5/6
- Blocked families: 1/6

## Verdict

**FULL_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS**

5 of 6 LowCode families passed real validation (dotnet restore + build + run).
diagram is BLOCKED by a generator API mismatch (out of scope to heal).
External blockers: epub, ocr, psd (NuGet package unavailability — unchanged).
