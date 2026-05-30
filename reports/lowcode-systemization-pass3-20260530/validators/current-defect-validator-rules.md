# Current-Defect Validator Rules — lowcode-systemization-pass3-20260530

Date: 2026-05-30

## V-001: PASS
Bundle has raw reflection evidence (reflection-raw/ non-empty)

## V-002: PASS
Family universe not silently swapped (epub tracked, not silently removed)

## V-003: PASS
Medical has scope decision (medical-scope-decision.md exists)

## V-004: PASS
EPUB has product-vs-format decision (epub-product-vs-format-decision.md exists)

## V-005: PASS
Restore success + reflection present for every LOWCODE_CONFIRMED family

## V-006: PASS
No assembly manifest uses old hardcoded repair run as final authority (source-authority-map.json present)

## V-007: PASS
No source_run: null manifest is publication-ready (pr11 excluded)

## V-008: PASS
Idempotency tests cover all manifests except source_run: null

## V-009: PASS
Every package snapshot has .csproj files

## V-010: PASS
Every example has example.manifest.json (including pdf-pr7/8/9)

## V-011: PASS
raw-commands.log contains no PENDING or 'to be run after' entries at close

## V-012: PASS
Full pytest raw log exists (tests/full-pytest.log)

## V-013: PASS
Artifact sidecar SHA/size matches actual ZIP

## V-014: PASS
repeatability-gap-register has no OPEN items while summary claims resolved

## V-015: PASS
systemization-defect-ledger resolved count > 0 when summary claims closure

## V-016: PASS
Main-class coverage gaps all have accepted blocker packets

## V-017: PASS
Restore-only evidence is NOT used as sole basis for LOWCODE_CONFIRMED classification

