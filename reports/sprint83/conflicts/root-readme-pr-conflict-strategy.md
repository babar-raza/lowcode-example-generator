# Root README PR Conflict Strategy — Sprint 83

## Summary

Three open root-README-only PRs exist from Sprint 72 backfill:
- cells#5 (`plugin-examples/cells/readme/20260519-143139`)
- words#7 (`plugin-examples/words/readme/20260519-143151`)
- diagram#2 (`plugin-examples/diagram/readme/20260519-143201`)

These PRs touch ONLY the repository root `README.md` — not example-level files.

## Strategy: EXCLUDE_ROOT_README_FROM_SPRINT83_PRS

Sprint 83 README I/O PRs (if created, pending approval) target only `examples/{family}/lowcode/{example}/README.md` paths — never the root `README.md`. This avoids any diff conflict with the open root-README PRs.

### Rationale

1. **No functional conflict**: Root README is organizational documentation; example READMEs are the delivery artifact. They are separate files with separate commit histories.
2. **Approval-blocked anyway**: `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=NOT_SET` — no new PRs are being created this sprint regardless. This strategy becomes operational when approval is granted.
3. **Carry-forward from Sprint 82**: Sprint 82 adopted this same strategy (`root_readme_exclusion_reason: "Deconflict with cells#5, words#7, diagram#2"`). Sprint 83 formalizes it as Lane B owned documentation.
4. **Root README PRs remain open**: They are not abandoned. They will be merged as part of a separate root-README merge sprint once all example I/O PRs are merged.

## Per-Family Conflict Status

| Family | Open Root README PR | Example README PRs (Sprint 83) | Conflict Risk |
|--------|--------------------|---------------------------------|---------------|
| cells  | #5                 | Would target examples/ only     | NONE          |
| words  | #7                 | Would target examples/ only     | NONE          |
| diagram| #2                 | Would target examples/ only     | NONE          |
| pdf    | (none)             | Would target examples/ only     | NONE          |
| email  | (none)             | Would target examples/ only     | NONE          |
| slides | (none)             | Would target examples/ only     | NONE          |

## Resolution Path

1. Merge all 42 example-level README I/O PRs (requires `APPROVE_LIVE_PR` + `APPROVE_MERGE_PR`)
2. Verify remote state shows all 42 examples with I/O README
3. Separately update and merge root README PRs (cells#5, words#7, diagram#2) in a root-README-only sprint
4. Close stale branches

---
*Lane B — Sprint 83 — 2026-05-24*
