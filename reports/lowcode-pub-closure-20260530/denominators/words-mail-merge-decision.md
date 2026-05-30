# Words Mail-Merge PR Candidate Decision — lowcode-pub-closure-20260530

## Decision: DEFERRED — not a PR candidate yet

## Rationale
- words-mail-merge generates successfully (Program.cs uses MailMerger API)
- Build OK, run OK
- However: mail merge requires external data source (data table/XML for merge fields)
- Current fixture is minimal; does not demonstrate realistic mail merge scenario
- Adding to PR now would create a low-quality example

## Status
- package_included: YES (generates, builds, runs)
- pr_candidate: NO (fixture incomplete)
- retry_condition: Create realistic mail merge fixture with data source

## Effect on counts
- words package_included: 8
- words pr_candidates: 7
- total package_included: 42
- total pr_candidates: 41
- Denominator is now internally consistent (no contradiction)
