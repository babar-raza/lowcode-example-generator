# No-Replay Scope — LANE 3 Supplement

**Sprint**: lowcode-final-closure-pass3-20260530

## Why Full No-Replay Was Not Used

Full no-replay E2E would re-extract NuGet packages from the live feed.
The prior sprint already ran `--replay-from generation` which is effectively
"generation replay" — the strongest no-replay option short of full re-download.

This sprint uses a **Strict Replay Contract** instead of full no-replay.

See `replay-contract/replay-decision.md` for the full rationale.

## What `--replay-from generation` Does

- Skips NuGet re-download (reuses cached catalog)
- Re-runs: scenario_planning, code generation (fresh from committed templates), build, validation
- Does NOT reuse prior generated Program.cs files (regenerates from templates)
- Performs fresh `dotnet restore`, `dotnet build`, `dotnet run` for all examples

## Evidence That Generation Was Fresh

1. `replay-contract/generator-source-hash-proof.json` — code_generator.py SHA matches HEAD:35005a6
2. `replay-contract/generated-output-freshness-proof.json` — 42/42 Program.cs hashes match ledger
3. `e2e-raw/e2e-aggregate.json` — 42/42 fresh restore/build/run PASS

## Conclusion

The replay mode used (`--replay-from generation`) provides equivalent freshness
guarantees for the generation and validation stages. The only stage not re-run is
NuGet package download (catalog reuse). This is documented and accepted per the
Strict Replay Contract defined in `replay-contract/replay-decision.md`.
