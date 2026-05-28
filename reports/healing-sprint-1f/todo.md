# Healing Sprint 1F -- Task List

## Sprint Goal
Adopt MANDATORY ARTIFACT-STAGING CONVENTION: commit tracked files, build artifact-metadata
outside tracked repo, ensure git status CLEAN before ZIP build. No tracked file modification
after final commit.

## Tasks

| # | Task | Status |
|---|------|--------|
| 1 | Restore Sprint 1E dirty tracked files to committed state (clean working tree) | DONE |
| 2 | Document Sprint 1E rejection → 00-1e-rejection.md | DONE |
| 3 | Create todo.md (this file) | DONE |
| 4 | Create commands.log | DONE |
| 5 | Create final-verdict.md | DONE |
| 6 | Create sprint-state.json (no final_commit_sha -- artifact-only convention) | DONE |
| 7 | Create evidence/evidence-contract.json (10 categories) | DONE |
| 8 | Create evidence/evidence-contract-computed.json | DONE |
| 9 | Create evidence/healing-validation-result.json | DONE |
| 10 | Create review/final-consistency-check.json | DONE |
| 11 | Create iv/independent-verification-report.md | DONE |
| 12 | Update .gitignore to add .local/ | DONE |
| 13 | Create scripts/build_healing_sprint_1f_bundle.py | DONE |
| 14 | Commit all tracked Sprint 1F files (exact-path staging) | DONE |
| 15 | Verify git status --short is CLEAN after commit | DONE |
| 16 | Run build script: generate artifact-metadata, build ZIP to .local/evidence-bundles/ | DONE |
| 17 | Verify: ZIP entry count, clean proof, no placeholders, artifact-verification.json | DONE |
| 18 | Publication gate check (APPROVAL_BLOCKED -- gate not set) | APPROVAL_BLOCKED |

## Publication Gate
- `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`: NOT SET → publication action APPROVAL_BLOCKED
- No PR creation or live push taken

## Sprint Verdict
LOWCODE_MACHINERY_HEALING_ACCEPTED
