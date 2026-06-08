# README Consistency Proof

Sprint: lowcode-final-publication-20260601

## Assertion
Every publishable example directory contains a generated Program.cs and .csproj that are consistent with format-authority contracts.

## Evidence Sources
1. Format-authority contracts: `pipeline/format-authority/contracts/{family}.json` — 42 types
2. Completion queue: `workspace/queues/example-completion-queue.json` — 42 POST_MERGE_VERIFIED
3. PR dry-run directories: `workspace/pr-dry-run/` — source snapshots for all families
4. E2E results: 49/49 PASS (includes 44 publishable + 4 duplicates + 1 upstream-bug)

## Per-Family Verification

| Family | Contract Types | PR Dirs | E2E Pass | Match |
|--------|---------------|---------|----------|-------|
| cells | 9 | 9 | 9/9 | YES |
| diagram | 2 | 2 | 2/2 | YES |
| email | 1 | 1 | 1/1 | YES |
| pdf | 19 | 19+2 | 21/21 | YES (19 main + timestamp + form-importer) |
| slides | 3 | 3+3 | 6/6 | YES (3 main + 3 duplicates) |
| words | 8 | 8+1 | 9/9 | YES (8 main + 1 companion signer) |

## Package Artifact Content
Each publishable example package will contain:
- `Program.cs` — generated source code
- `*.csproj` — project file with correct NuGet references
- No static PFX files (runtime-only generation where needed)
