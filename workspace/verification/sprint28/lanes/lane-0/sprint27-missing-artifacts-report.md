# Sprint 27 Missing Artifacts Report

**Sprint:** 27
**Date:** 2026-05-17
**Bundle path:** `workspace/verification/sprint27-evidence-gated-publication-pr3-pr9-and-final-pdf-closeout-20260517-165525.zip`
**File count:** 17 (supervisor required: ~40+)
**Supervisor verdict:** `SPRINT27_EVIDENCE_BUNDLE_PRESENT_BUT_CONTRACT_TOO_WEAK`

## Present Artifacts (17)

| Artifact | Lane | Status |
|----------|------|--------|
| sprint26-evidence-bundle-audit.json | lane-0 | PRESENT |
| sprint26-bundle-contract-validation-report.json | lane-0 | PRESENT |
| sprint26-commit-proof.json | lane-1 | PRESENT |
| publication-mode-decision.json | lane-p0 | PRESENT |
| pdf-formimporter-defect-repro-report.json | lane-pdf-a | PRESENT |
| pdf-formimporter-upstream-issue-draft.md | lane-pdf-a | PRESENT |
| pdf-final-denominator-closeout-matrix.json | lane-pdf-b | PRESENT |
| email-converttohtml-cleanup-hardening-report.json | lane-email-a | PRESENT |
| slides-target-runtime-verification-report.json | lane-slides-a | PRESENT |
| test-summary.json | lane-test | PRESENT |
| sprint26 lane evidence (7 files carried forward) | sprint26 | PRESENT |

## Missing Artifacts (17 critical gaps)

| Artifact | Required By | Reconstructible? |
|----------|-------------|-----------------|
| git-status-final.txt | contract | YES (from commit record) |
| git-diff-final.patch | contract | YES (git diff on commit) |
| changed-files.txt | contract | YES (git diff --name-only) |
| final-state-summary.yaml | contract | YES (reconstruct from evidence) |
| final-verdict.md | contract | YES (from commit message) |
| bundle-contract-definition.json | contract | NO (never defined in sprint27) |
| bundle-contract-validation-report.json | contract | NO (never run in sprint27) |
| pdf-pr3-approval-blocked.md | PR audit | YES |
| pdf-pr5-approval-blocked.md | PR audit | YES |
| pdf-pr6-approval-blocked.md | PR audit | YES |
| pdf-pr7-approval-blocked.md | PR audit | YES |
| pdf-pr8-approval-blocked.md | PR audit | YES |
| pdf-pr9-approval-blocked.md | PR audit | YES |
| post-publication-not-run-approval-blocked.md | post-pub | YES |
| all-family-launch-scoreboard.json | scoreboard | YES |
| taskcard-reconciliation-report.json | taskcards | YES |
| test-full.log | test | UNAVAILABLE (not captured) |

## Root Cause

Sprint 27 was executed without a strict evidence contract. The contract was referenced in sprint 27 docs but never implemented as code. This made it possible to create a ZIP with only lane evidence JSON files while missing git state, PR audit proofs, test logs, and final verdict documents.

## Sprint 28 Remediation

Sprint 28 implements `src/plugin_examples/evidence_contract.py` with a `StrictEvidenceContract` class that:
- Defines all required artifacts
- Validates presence and non-emptiness
- Validates no raw secrets
- Validates final verdict is present
- Fails with BUNDLE_CONTRACT_FAILED if any required artifact is missing
- Includes tests proving thin bundles fail validation
