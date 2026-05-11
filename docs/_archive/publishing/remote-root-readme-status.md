# Remote Root README Status Audit

**Date:** 2026-05-03
**Method:** `gh api repos/{owner}/{repo}/contents/README.md`
**Verdict:** BACKFILL_REQUIRED (both families)

---

## Findings

### Cells — aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples

| Field | Value |
|-------|-------|
| Remote README size | 40 bytes |
| Remote README SHA | `04d2b668aed45811a8e41b00e12c469efa70557f` |
| Remote README content | `# Aspose.Cells.LowCode-for-.NET-Examples` |
| Is pipeline-generated? | NO |
| Source | GitHub auto-init stub |
| Pipeline README size | 5081 bytes |
| Pipeline README audit | PASS |
| PR #1 included README? | NO |
| Needs backfill? | **YES** |

### Words — aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples

| Field | Value |
|-------|-------|
| Remote README size | 40 bytes |
| Remote README SHA | `ba21da69c5c03691ecdb59b74bcd1eece347e93c` |
| Remote README content | `# Aspose.Words.LowCode-for-.NET-Examples` |
| Is pipeline-generated? | NO |
| Source | GitHub auto-init stub |
| Pipeline README size | 4337 bytes |
| Pipeline README audit | PASS |
| PR #1 included README? | NO |
| Needs backfill? | **YES** |

---

## Root Cause

PR #1 for both families was created on 2026-05-02 before the Root README Sprint (Sprint 1,
executed 2026-05-03). The PR packages submitted to GitHub included 57 files (Cells) and
23 files (Words) — none of them README.md.

GitHub auto-creates a single-line README stub when a repository is initialized. These stubs
were present before PR #1 was merged and remain unchanged after the merge.

---

## Required Action

Implement `publish-readme` command. For each family:
1. Render pipeline README via `render-root-readme`
2. Audit rendered README
3. Compare against remote stub SHA
4. Since remote content ≠ pipeline README, create a README-only PR
5. Requires `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`
