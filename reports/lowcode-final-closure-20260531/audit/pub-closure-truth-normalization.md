# Previous Bundle Truth Normalization — lowcode-pub-closure-20260530
Generated: 2026-05-31T13:27:01

## Reclassification
lowcode-pub-closure-20260530 is reclassified as:
LOWCODE_PUBLICATION_CLOSURE_PROGRESS_ACCEPTED_EVIDENCE_AND_SYSTEMIZATION_REPAIR_REQUIRED

It is NOT accepted as publication-ready closure.

## Accepted Claims
- ZIP SHA-256: ccff8fce74c9cf664b42760b30239b2a33c29c539d4b25b963e4411f56939848
- ZIP size: 1,314,494 bytes, 620 entries
- 42 generated Program.cs files bundled
- 42 generated .csproj files bundled
- 42 generated example.manifest.json files bundled
- E2E folders exist for 42 examples
- per-example-output-proof.json exists (has 42 entries)
- fallback-review-results.json exists
- evaluator/model source changes bundled
- Physical A/B idempotency: 30/30 hash matches (CONFIRMED from prior sprint)

## Rejected Claims
See contradiction-register.json for full details.
Key rejections:
1. pytest raw log had 2 failures (not 0)
2. artifact-verification.json SHA/size/entries mismatch
3. IV had pending/partial checks
4. Command index had only 14 commands, no stdout/stderr files
5. Package artifacts contained only dependency manifests
6. pdf-image-extractor and pdf-text-extractor had has_output=false
7. words-converter/replacer/splitter had forbidden overload comments in snapshots
8. Denominator contradictions (pr=41 claimed but mail-merger is self-contained)
9. Per-family counts were wrong (claimed 7 email but actual is 1)
