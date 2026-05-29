# IV Findings

**Sprint ID:** full-system-qualification-repair-20260529

## Finding 1: Diagram GENERATOR_API_MISMATCH

The diagram examples produced by the prior sprint use `Aspose.Diagram.ShapeType`
which does not exist in the installed package. This is a generator defect, not
an infrastructure defect. The prior sprint's 'PASS' for diagram was fabricated
(template_mode=True bypassed actual compilation).

**Classification:** BLOCKED — out of scope for this sprint

## Finding 2: 5 Families Confirmed Valid

cells, email, pdf, slides, words: real dotnet build+run succeeded.
The template generator produces valid compilable C# for these families.

## Finding 3: Prior Sprint validation-results.json Was Fabricated

workspace/verification/latest/families/diagram/validation-results.json showed
passed=2 but this was produced with template_mode=True (no actual build).
This was the core overclaim that this sprint exists to resolve.
