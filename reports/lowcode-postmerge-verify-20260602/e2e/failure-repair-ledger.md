# E2E Failure Repair Ledger

## Defect 1: Duplicate .csproj files (25 examples across 5 repos)

**Root cause:** Publication script copied both the family-prefixed csproj (from workspace) and the short-name csproj (from prior PRs), creating ambiguity for MSBuild.

**Affected repos:** cells (9), email (1), pdf (4), slides (3), words (8) = 25 examples
**Repair PRs:**
- cells #8: merged, sha=c8c2a4e1
- email #3: merged, sha=e63e497b
- pdf #23: merged, sha=98cc5998
- slides #3: merged, sha=dc144db0
- words #9: merged, sha=29ed820b

**Resolution:** Removed unprefixed duplicates, kept family-prefixed convention.

## Defect 2: Static .pfx files (2 repos)

**Root cause:** Runtime-generated test certificates were included in publication push as static files.

**Affected repos:** pdf (test.pfx), words (test-cert.pfx)
**Repair PRs:** Included in defect 1 PRs (#23 and #9).

**Resolution:** Removed static PFX files. Both examples generate PFX at runtime.

## Defect 3: Missing CopyToOutputDirectory (5 examples across 2 repos)

**Root cause:** csproj files missing CopyToOutputDirectory for input files that are referenced via AppContext.BaseDirectory.

**Affected examples:**
- cells/text-converter: missing input.xlsx
- words/converter: missing input.docx
- words/replacer: missing input.docx
- words/splitter: missing input.docx
- words/watermarker: missing input.docx

**Repair PRs:**
- cells #9: merged, sha verified
- words #10: merged, sha verified

**Resolution:** Added CopyToOutputDirectory for input files.

## Post-Repair E2E

All 44 examples: 44/44 build, 44/44 run (exit=0).
