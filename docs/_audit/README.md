# Documentation Audit Staging Area

This folder is a **staging area** for audit artifacts, analysis snapshots, and migration plans.

Files here are either:
- **Pending promotion** to active docs (once reviewed and accepted)
- **Pending archival** to `docs/_archive/plans/` (once superseded)

Staging artifacts are **not active documentation** — do not link to them from guides, runbooks, or reference pages.

---

## Current Files

This staging area is now empty of audit artifacts. Only this `README.md` remains.

All 2026-05-30 artifacts were processed in sprint **DOC-CONSOLIDATION-20260617**:

| File | Disposition | Archive path |
|------|-------------|-------------|
| `docs_inventory.md` | ARCHIVED | `docs/_archive/plans/docs-inventory-2026-05-30.md` |
| `docs_migration_plan.md` | ARCHIVED | `docs/_archive/plans/docs-migration-plan-2026-05-30.md` |
| `README_IA_PROPOSAL.md` | ARCHIVED (IA adopted) | `docs/_archive/plans/IA-proposal-2026-05-30.md` |
| `root_orphans.md` | ARCHIVED | `docs/_archive/plans/root-orphans-2026-05-30.md` |
| `style_guide.md` | PROMOTED to active docs | `docs/development/style-guide.md` |
| `system_audit.md` | ARCHIVED | `docs/_archive/plans/system-audit-2026-05-30.md` |
| `traceability.md` | ARCHIVED | `docs/_archive/plans/traceability-2026-05-30.md` |

---

## Promotion Criteria

A file is promoted from `_audit/` to active docs when:
1. Its content is reviewed against current source code
2. The corresponding IA location is confirmed and stable
3. The file passes link check at the new path
4. `docs/README.md` (or equivalent navigation) is updated to link to it

## Archival Criteria

A file is archived from `_audit/` to `docs/_archive/plans/` when:
1. A newer document supersedes its content
2. The file is a point-in-time snapshot (audit report, migration plan, preflight result)
3. No active navigation links to it

After archival, `_audit/` should contain only this `README.md`.

---

## Sprint Summary — DOC-CONSOLIDATION-20260617

**Status**: COMPLETE — all taskcards closed (2026-06-17).

Key outcomes:

| Category | Actions |
|---|---|
| Staleness remediation | operator-quickstart.md (SDK 10.0, 18 families, LLM guidance), cli.md (+7 commands → 27 total), repo-structure.md (+5 packages) |
| Near-duplicate consolidation | post-merge-verification merged into single canonical (operations/); publishing/ runbook removed |
| Conflict resolution | ollama correctly documented as approved local-dev provider in AGENTS.md and operator-quickstart.md |
| Audit artifact promotion | style_guide.md → docs/development/style-guide.md |
| Audit artifact archival | 6 files archived to docs/_archive/plans/ with 2026-05-30 date suffix |
| New documentation | probe-registry-guide.md, ADR-009 (documentation governance) |
| Automation | 3 new scripts: check_cli_docs_drift.py, check_doc_freshness.py, check_doc_links.py |
| CI gates (advisory) | docs-link-check, docs-freshness-check added to .gitlab-ci.yml |
| Schema coverage | schemas-and-contracts.md covers all 11 schemas |
| Environment variables | environment-variables.md covers all discovered env vars |

**Final verification**: 0 broken links · 0 CLI drift · all gate scripts exit 0
