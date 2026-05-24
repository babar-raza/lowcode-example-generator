# Sprint 81 -- Handoff Diff Summary

## What Changes When README I/O PRs are Created

For each example in each family, the PR will update:
- `examples/{family}/lowcode/{example}/README.md`
  - Add `## Input and Output` section from local handoff

Root README changes (if included):
- `README.md` (repo root) -- already has open PRs for cells, words, diagram
  - pdf, email, slides root READMEs may be included in Sprint 81 PR

Package version changes:
- Words: remote=26.5.0, handoff=26.5.0 -- NO VERSION CHANGE NEEDED
- Cells: version confirmed same
- All families: no version bump required

## Files NOT Changing

- Program.cs files: NOT touched (code was published in Sprints 72-74)
- .csproj files: NOT touched
- global.json: NOT touched
- bin/obj: excluded

## Change Scope

| Family | README files changed |
|--------|---------------------|
| cells | 9 + 1 root = 10 |
| words | 8 + 1 root = 9 |
| pdf | 19 + 1 root = 20 |
| diagram | 2 + 1 root = 3 |
| email | 1 + 1 root = 2 |
| slides | 3 + 1 root = 4 |
| **Total** | **42 examples + 6 root = 48 files** |

Note: cells/words/diagram root READMEs already have open PRs.
Sprint 81 README I/O PRs would update example READMEs + remaining root READMEs.
