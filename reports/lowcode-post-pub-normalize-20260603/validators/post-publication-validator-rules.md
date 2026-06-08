# Post-Publication Validator Rules — lowcode-post-pub-normalize-20260603

## V01: E2E Aggregate Backed by Raw Logs
FAIL if `patrol-e2e-aggregate.json` exists without corresponding files in `e2e/raw-logs/`.

## V02: README Lists All Published Examples
FAIL if any of 44 published example names is absent from its repo README.

## V03: No Dangling Branches
FAIL if any repo has branches other than `main`.

## V04: No Static Certificate Files
FAIL if any .pfx/.p12/.key/.pem/.cer/.crt committed (excluding .git/bin/obj).

## V05: Diagram Converter Creates Output
FAIL if `diagram/diagram-converter` produces no output.vdx.

## V06: Timestamp Environment Documentation
FAIL if pdf/timestamp lacks TSA documentation and graceful-failure handling.

## V07: FormImporter Retry Status Current
FAIL if upstream-bug-status.md last-checked > 7 days old.

## V08: Program.cs + Exactly One .csproj
FAIL if any example lacks Program.cs or has != 1 .csproj.

## V09: No Missing Required Fixture
FAIL if any example references unavailable input.

## V10: Command Ledger Actually Exists
FAIL if `commands/raw-commands.log` is absent OR `commands/stdout-stderr/` is absent OR `commands/command-index.json` is absent.
Convention: `commands/stdout-stderr/` contains flat copies of all E2E logs. `e2e/raw-logs/` contains per-family structured copies.

## V11: No Unclassified Extra Folders
FAIL if live folder count exceeds intended count without explicit classification in decision board.

## V12: PDF pdfa-converter vs pdf-aconverter
FAIL if both exist without documented decision. (RESOLVED: pdf-aconverter removed via PR #25)

## V13: Diagram Prefixed vs Unprefixed
FAIL if both prefixed (diagram-diagram-converter) and unprefixed (diagram-converter) exist without documented decision. (RESOLVED: prefixed removed via PR #4)

## V14: Validator References Valid Evidence Paths
FAIL if validator log references any path not actually present in evidence bundle.
