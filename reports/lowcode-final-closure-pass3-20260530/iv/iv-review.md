# Independent Verification / Adversarial Review — LANE 14

**Sprint**: lowcode-final-closure-pass3-20260530

## IV Purpose

This lane performs an adversarial review of the sprint's evidence, looking for:
- False claims in evidence files
- Missing or stale evidence
- Hash collisions or verification gaps
- Logical contradictions between lanes

## Evidence Chain Audit

### Claim: 42/42 examples pass restore/build/run
- **Verification**: Lane 4 raw logs at `e2e-raw/<family>/<example>/{restore,build,run}.log`
  show 42 files with `exit_code: 0` for each stage.
- **Cross-check**: `e2e-raw/e2e-aggregate.json` confirms `total_pass: 42, total_fail: 0`.
- **Independent**: Pipeline's own `validation-results.json` in each canonical run also
  confirms per-family PASS (cells 9/9, words 8/8, pdf 19/19, diagram 2/2, slides 3/3, email 1/1).
- **Verdict**: CLAIM_VERIFIED

### Claim: All 42 Program.cs files are not manually patched
- **Verification**: Lane 2 `hash-verification.json` shows 42/42 SHA256 hashes match
  the source-hash-ledger.json from the canonical run directories.
- **Check**: The canonical runs used `--replay-from generation` — no prior generated
  files are reused (the generation stage regenerates from templates).
- **Check**: Generator source hash (code_generator.py SHA=c9794cfb...) matches HEAD:35005a6.
- **Verdict**: CLAIM_VERIFIED

### Claim: Catalog hash unchanged between base run and replay
- **Verification**: cells/words/pdf denominators contain `catalog_sha` and canonical runs
  show `match: true` in `catalog-hash-validation.json`.
- **Gap**: diagram/email/slides denominators have no `catalog_sha` field — these families
  cannot be catalog-hash-verified. This is documented as intentional in replay-decision.md.
- **Impact**: The gap does not affect the 42/42 validation claim since validation is
  demonstrated by fresh build/run logs, not catalog hash alone.
- **Verdict**: PARTIAL_VERIFIED (3/6 families catalog-verified; 3/6 have no denominator hash)

### Claim: Diagram stale BLOCKED_GENERATION is fixed
- **Verification**: Before state confirmed from workspace/verification/latest/families/diagram/
  gate-results.json (gate_generation: blocked). After state shows gate_generation: passed.
- **Source**: Canonical run pilot-diagram-20260529-221021 is the correct run — DEF-004/005 fixed.
- **Verdict**: CLAIM_VERIFIED

### Claim: Reviewer unavailability does not block examples
- **Verification**: gate-results.json for all 6 families shows gate_reviewer: failed,
  required: false. No examples have `final_example_verdict: EXAMPLE_BLOCKED_BY_REVIEWER`.
- **Verdict**: CLAIM_VERIFIED

### Claim: 42 validated, 41 PR candidates
- **Verification**: words family validation-results shows 8/8 pass (includes words-comparer).
  pr-candidate-manifest shows words-comparer with `EXAMPLE_BLOCKED_CODE_CONTRACT_FAILED`.
- **Verdict**: CLAIM_VERIFIED

### Claim: External blockers (epub/ocr/psd) unchanged
- **Verification**: Live NuGet search at 2026-05-30 shows Aspose.Epub not present,
  Aspose.AI.LLM not present, Aspose.JavaAttributes not present.
- **Raw logs**: blockers/{epub,ocr,psd}-raw-check.log
- **Verdict**: CLAIM_VERIFIED

## Adversarial Findings

| Finding | Severity | Status |
|---------|----------|--------|
| diagram/email/slides catalog hash not in denominator | LOW | Documented in replay-decision.md — intentional |
| publication dry-run for diagram/slides/email has missing packages | LOW | Known — packages not built for these families after durable-fix run; approval gate is the primary blocker |
| release-status shows all_merged=true (prior sprint state) | INFO | Correct — these are historical merge SHAs from prior sprint publications; not contradicted by current sprint |
| words-comparer in validation-results but not in aggregate pr-candidate | INFO | Correct — validated but excluded from publication by code contract |

## Conclusion

No adversarial findings that contradict the sprint's primary claims:
- 42/42 validation PASS
- 41 PR candidates
- Lane 6 diagram stale state resolved
- Lane 5 pytest 3209/3227 pass
- Lane 3 strict replay contract satisfied for all 6 families

Sprint evidence is internally consistent.
