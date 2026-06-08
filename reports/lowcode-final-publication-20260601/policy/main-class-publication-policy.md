# Main-Class Publication Policy

## Scope
Governs publication of examples where the primary demonstrated type is a LowCode main class (WORKFLOW_ROOT).

## Criteria for PUBLISH_MAIN_CLASS_EXAMPLE
1. The type exists in the format-authority contract for its family.
2. The generated Program.cs compiles (`dotnet build` exit 0).
3. The generated Program.cs runs (`dotnet run` exit 0) and produces non-empty output.
4. The example is not a duplicate of another published example.
5. E2E status is POST_MERGE_VERIFIED or equivalent pass.

## Denominator Contribution
Each main-class example counts as 1 toward the canonical denominator (42 total).

## Decision Authority
Agent-delegated per sprint `lowcode-final-publication-20260601`.
