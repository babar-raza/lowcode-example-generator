# Post-Publication Validator Rules — lowcode-post-pub-patrol-20260603

## V01: E2E Aggregate Backed by Raw Logs
FAIL if `patrol-e2e-aggregate.json` exists without corresponding files in `e2e/raw-logs/`.
Current: 132 raw log files (44 restore + 44 build + 44 run).

## V02: README Lists All Published Examples
FAIL if any of the 44 published example directory names is absent from its repo README.
Checked via case-insensitive content match.

## V03: No Dangling Publication/Repair Branches
FAIL if any repo has branches other than `main`.

## V04: No Static Certificate/Private Key Files
FAIL if any .pfx/.p12/.key/.pem/.cer/.crt file is committed (excluding .git/bin/obj).

## V05: Diagram Converter Creates Output File
FAIL if `diagram/diagram-converter` `dotnet run` produces no `output.vdx`.

## V06: Timestamp Has Environment-Dependent Documentation
FAIL if pdf/timestamp Program.cs lacks TSA server comment and graceful-failure catch block.

## V07: FormImporter Retry Status Not Stale
FAIL if `upstream-bug-status.md` last-checked date is more than 7 days ago.

## V08: Every Example Has Program.cs and Exactly One .csproj
FAIL if any example directory lacks Program.cs or has != 1 .csproj file.

## V09: No Missing Required Fixture
FAIL if any example references an input file that is neither committed nor generated at runtime.

## V10: Monitoring Bundle Has Command Ledger
FAIL if evidence bundle lacks `commands/raw-commands.log` or `e2e/e2e-command-index.json`.
