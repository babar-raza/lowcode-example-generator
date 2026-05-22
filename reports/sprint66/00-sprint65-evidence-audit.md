# Sprint 66 — Sprint 65 Evidence Audit

Sprint: sprint66-remote-truth-repair-self-contained-artifacts-readme-io-publication-proof
Audit Date: 2026-05-22
Audited: reports/sprint65/

## Audit Summary

Sprint 65 is NOT ACCEPTED. 5 blocking defects were found.

| Item | Sprint 65 Claim | Audit Result | Status |
|------|----------------|--------------|--------|
| 1 | 42/42 remote publication via 6 PRs (one per family) | Words PR#6=1 example, PDF PR#4=1 example; claims all proved by multi-PR history | CONTRADICTED |
| 2 | Remote READMEs have I/O sections | Remote READMEs show only API Symbols Used + Run, no I/O section | CONTRADICTED |
| 3 | Self-contained bundle (handoff/per-family/) | handoff/per-family/ is empty; no Program.cs/README/csproj in bundle | CONTRADICTED |
| 4 | All output_kind fields present | 3 records blank: pdf-html-converter, pdf-pdfa-converter, pdf-text-extractor | CONTRADICTED |
| 5 | Final verdict cleanly separates published vs approval-blocked | Verdict mixes "42/42 already published" + "APPROVAL_BLOCKED" without per-field separation | CONTRADICTED |

Accepted Sprint 65 progress:
- Sprint 64 was audited and corrected ✓
- Root README artifacts present for 6 families ✓
- Destination audit has 42 records ✓
- Special-case placement proof exists for pdf-pdfa-converter and pdf-text-extractor ✓
- EV/ECC reports: 46/46 present, 32/32 rules pass ✓
- Tests: 2993 passed, 3 skipped, 0 failed ✓
- Final clean proof non-empty ✓

## Blocking Defect Detail

### S65-D1: Remote Proof Index Overclaims

Sprint 65 `reports/sprint65/publication/remote-proof-index.json` lists:
- words: PR #6 (merged=true)
- pdf: PR #4 (merged=true)
And claims these 6 PRs prove all 42 examples are published.

**Contradiction verified by GitHub API:**
- Words PR #6: `examples_count=1, example_names=["report-builder"]` — covers 1 of 8 examples
- PDF PR #4: `examples_count=1, example_names=["optimizer"]` — covers 1 of 19 examples

All 42 examples ARE present in remote repos (confirmed: cells=9, words=8, pdf=19, diagram=2, email=1, slides=3).
But they were published via MULTIPLE PRs (words: 6 total PRs; pdf: 9 total PRs).
Sprint 65 compressed 6+ PRs-per-family into 1 PR per family without per-example coverage proof.

### S65-D2: Remote READMEs Have No I/O Sections

Sampled remote READMEs:
- `examples/words/lowcode/report-builder/README.md`: API Symbols Used + Run only
- `examples/pdf/lowcode/optimizer/README.md`: API Symbols Used + Run only

No "## Input and Output" section found. Remote READMEs are old-format.
Sprint 64 packages have corrected READMEs with I/O sections, but these were never pushed.

### S65-D3: Bundle Not Self-Contained

`reports/sprint65/handoff/per-family/` — EMPTY (confirmed by `ls`)
`reports/sprint65/` contains no destination-packages/ directory.
Audit records reference Program.cs/README/csproj paths under `reports/sprint64/destination-packages/`
but those paths are outside the sprint65 bundle.

### S65-D4: Missing output_kind Fields (3 records)

`reports/sprint65/destination/content-audit-final.json`:
- `pdf-html-converter`: output_kind = "" (blank)
- `pdf-pdfa-converter`: output_kind = "" (blank)
- `pdf-text-extractor`: output_kind = "" (blank)

Correct values: converter, converter, extractor (respectively).

### S65-D5: Mixed Publication/Approval State in Verdict

`reports/sprint65/final-verdict.md` states:
> "all 42 examples are already published (Sprint 62)"
AND
> "Publication is BLOCKED_BY_APPROVAL"

These two states are contradictory without a separation model.
No per-example state fields (`remote_example_present`, `remote_readme_has_io_docs`, etc.).

## Reclassification

Sprint 65 verdict: `LOWCODE_DRY_RUN_PUBLICATION_HANDOFF_READY_42_OF_42_APPROVAL_BLOCKED`

Corrected Sprint 65 state: `LOWCODE_REMOTE_EXAMPLE_PATHS_PRESENT_README_IO_NOT_PUBLISHED_HANDOFF_MISSING`

Reason: Examples exist in remote repos but READMEs are old-format. Handoff bundle is incomplete.
The "42/42 published" claim is historically accurate for example paths, but overstated for README I/O state.
