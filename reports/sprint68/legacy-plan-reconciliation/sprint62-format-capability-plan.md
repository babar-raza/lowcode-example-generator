# Sprint 62 — Format Capability Extension Plan

Source: reports/sprint62/ (sprint62-readme-io-publication-42-42-closure)
Reconciliation Date: 2026-05-22

## Plan Items from Sprint 62 Scope

| # | Item | Sprint 62 Disposition | Status |
|---|------|-----------------------|--------|
| 1 | Special-case I/O authority (9 cases) | CLOSED in Sprint 62 Phase 2 | CLOSED |
| 2 | 42/42 README I/O correction packages | CLOSED in Sprint 62 Phase 3 | CLOSED |
| 3 | 6/6 destination dry-run packages | Staged in workspace/pr-dry-run/ | SUPERSEDED_BY_SPRINT66_HANDOFF |
| 4 | Words/Diagram version drift (dry-run) | Corrected in dry-run packages (26.4→26.5) | CARRIED_FORWARD |
| 5 | README gate hardening (SD61-06) | CLOSED: APPROVE_README_PUSH cannot bypass failed audit | CLOSED |
| 6 | EV execution mandatory (SD61-05) | CLOSED: bundle_validation_result_present_and_valid rule added | CLOSED |
| 7 | Package authority API backfill | CLOSED: api_verified=CONFIRMED_FROM_PROGRAMCS for all 42 | CLOSED |
| 8 | Live publication (if approved) | BLOCKED_BY_APPROVAL — 0 PRs created | CARRIED_FORWARD |
| 9 | Sprint 62 evidence bundle validation | CLOSED: sprint62-bundle-validation-result.json present | CLOSED |

## Open Items Carried Forward to Sprint 67

### CF-S62-1: Words/Diagram Version Drift Push

- Sprint 62 dry-run packages: Words 26.4→26.5, Diagram 26.4→26.5 corrected
- Sprint 63-66: These version corrections were carried through handoff packages
- Sprint 66: handoff/per-family/words/Directory.Packages.props = 26.5.0; diagram = 26.5.0
- Sprint 67 action: Confirm in version-truth-matrix.json. Publish with README I/O updates when approved.

### CF-S62-2: Live README I/O Publication

- Sprint 62: all 42 correction packages ready; BLOCKED_BY_APPROVAL
- Sprint 63-66: sprint evolved to self-contained handoff; still BLOCKED_BY_APPROVAL
- Sprint 67 Phase 8: Activate or document explicit BLOCKED state

## Superseded Items

| Item | Superseded by |
|------|--------------|
| workspace/pr-dry-run/ packages (Sprint 62) | reports/sprint66/handoff/per-family/ (Sprint 66 self-contained handoff) |
| Sprint 62 README correction text format | Sprint 66 corrected packages (Program.cs + README + csproj) |

## Extension Items (OCR/PSD/FormImporter — Open Follow-ups)

These were not Sprint 62 plan items but appear in the pipeline backlog:

| Item | Current Status |
|------|----------------|
| FormImporter (pdf) | PERMANENTLY_DEFERRED: Aspose.PDF library bug in 26.5.0. Retry on 26.6.0+. |
| OCR types | DISCOVERY_BLOCKED: No Aspose LowCode namespace for OCR confirmed. Recheck monthly. |
| PSD types | DISCOVERY_BLOCKED: No Aspose LowCode namespace for PSD confirmed. Recheck monthly. |

Sprint 67 decision: FormImporter/OCR/PSD remain DISCOVERY_BLOCKED/PERMANENTLY_DEFERRED.
No Sprint 67 action required. Carry as backlog items with monthly recheck.
