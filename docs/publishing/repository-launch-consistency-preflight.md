# Repository Launch Consistency — Preflight Review

**Date:** 2026-05-03
**Sprint:** Repository Launch Consistency, Root README Backfill, and Reproducibility Verification
**Verdict:** PREFLIGHT_PASS

---

## Context

Both Cells PR #1 and Words PR #1 were merged. The root README Sprint (Sprint 1) ran after
the merges, so neither PR included a pipeline-generated README. Both remote repos currently
have 40-byte GitHub auto-init stub READMEs. This sprint backfills the pipeline-generated
READMEs through the repeatable PR system.

---

## Questions and Answers

| # | Question | Answer |
|---|----------|--------|
| Q1 | `readme_renderer.py` exists? | YES — `build_readme_context()`, `render_readme()`, `write_readme()` all present |
| Q2 | `readme_auditor.py` exists? | YES — 7-check audit; cross-family contamination guard |
| Q3 | Jinja2 template exists? | YES — `templates/root-readme/lowcode-family-readme.md.j2` |
| Q4 | Cells dry-run README exists? | YES — 5081 bytes, 9 examples, v26.4.0, AUDIT PASS |
| Q5 | Words dry-run README exists? | YES — 4337 bytes, 4 examples, v26.4.0, AUDIT PASS |
| Q6 | Remote Cells README state? | STUB (40 bytes) — needs backfill |
| Q7 | Remote Words README state? | STUB (40 bytes) — needs backfill |
| Q8 | PR #1 included pipeline README? | NO — README Sprint ran after PR #1 merges |
| Q9 | `publish-readme` command exists? | NO — must be implemented in Phase 2 |
| Q10 | `collect_package_files()` works with README-only dir? | YES — README.md is not in `_EXCLUDED_FILENAMES` |
| Q11 | Approval gate intact? | YES — `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` required |
| Q12 | Audit failure blocks live publish? | YES — fixed in Sprint 2 manual review |
| Q13 | `render-root-readme` produces audit JSON? | YES — both audit JSONs present, both `passed: true` |
| Q14 | `publish-readme` tests exist? | NO — 9 tests needed in Phase 2 |
| Q15 | Generation policy unchanged? | YES — Words/PDF generation still blocked |

---

## Key Finding

**Neither remote repo has a pipeline-generated README.** The 40-byte stubs
(`# Aspose.Cells.LowCode-for-.NET-Examples` and `# Aspose.Words.LowCode-for-.NET-Examples`)
are GitHub's auto-created init files, not pipeline output. The post-merge clean-checkout
validations listed "README.md" in `expected_root_files` — that was the pre-existing stub,
not a pipeline README.

---

## Design Decisions

1. `publish-readme` creates a temp dir containing only `README.md`, then calls `create_github_pr()`
2. **NO_CHANGE detection**: compare rendered content hash against remote SHA; skip PR if identical
3. **Dry-run**: render + audit + simulate (no remote write)
4. **Live**: requires `APPROVE_LIVE_PR` token; approval checked BEFORE any remote write
5. PR branch naming: `plugin-examples/{family}/readme/{date}`
6. PR title: `Add pipeline-generated README for {display_name} LowCode Examples`
7. Both Cells and Words need backfill PRs

---

## Generation Policy (Immutable)

| Family | Generation | README Render | README Backfill PR |
|--------|-----------|---------------|--------------------|
| Cells | Allowed | Allowed | Allowed (with APPROVE_LIVE_PR) |
| Words | BLOCKED | Allowed | Allowed (with APPROVE_LIVE_PR) |
| PDF | BLOCKED | Blocked | Blocked |

---

## Next Phases

- **Phase 1**: Create `remote-root-readme-status.json` and `.md` ✓
- **Phase 2**: Implement `publish-readme` CLI command with 9 tests
- **Phase 3**: Re-run `render-root-readme` for both families; verify audit passes
- **Phase 4**: Run README-only dry-run simulations
- **Phase 5**: Create live README-only PRs (with approval token)
- **Phase 6**: Verify PRs remotely — confirm changed files = `["README.md"]` only
