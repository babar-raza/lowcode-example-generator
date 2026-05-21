# Sprint 60 Next-Work Register

**Date:** 2026-05-21
**Sprint:** sprint60-sprint59-false-complete-repair-destination-readme-gate-20260521

Non-blocking items carried forward from Sprint 59 and Sprint 60.

---

## Carried from Sprint 59

| Item | Classification | Priority |
|------|---------------|----------|
| Words root README version drift (26.4.0 in repo, 26.5.0 latest NuGet) | Version policy: `version_intentionally_omitted` for root README; needs `Directory.Packages.props` push | P2 |
| Diagram root README version drift (26.4.0 in repo, 26.5.0 latest NuGet) | Same as Words | P2 |
| FormImporter (pdf family, Wave H) | DEFERRED — blocked by Aspose.PDF library bug in 26.5.0. Retry on 26.6.0+ | P3 |
| OCR/PSD examples | DEPENDENCY_BLOCKED — NuGet 404 for required packages. Recheck monthly | P3 |
| report-builder fixture | Missing `input.docx` for Words regeneration. Needs csproj fix or regeneration | P2 |

## Carried from Sprint 60

| Item | Classification | Priority |
|------|---------------|----------|
| README gate wiring into `publish-pr` CLI | Gate module exists; needs CLI integration in `batch_publisher.py` or `release_status.py` | P1 |
| `io-authority/api-catalog-snippets/` population | Per-family API catalog excerpts not yet added (Phase 6 acceptance deferred) | P2 |
| EvidenceValidator integration in pipeline | Validator exists as standalone; needs wiring into `run` or `release-status` commands | P1 |

---

## Version Drift — Publication Plan

Words and Diagram are at v26.4.0 in target repos. Latest NuGet is v26.5.0/26.5.1.
Publication requires:
1. Regenerate examples at 26.5.x
2. Push `Directory.Packages.props` to destination repos
3. Approval: `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`

Blocked by: none technical; approval policy requires explicit `APPROVE_LIVE_PR`.
