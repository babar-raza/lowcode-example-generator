# Replay Decision — LANE 3

**Sprint**: lowcode-final-closure-pass3-20260530

## Decision: Strict Replay Contract (not full no-replay)

Full no-replay E2E would re-extract NuGet packages from the live feed and take 2-4 hours.
The prior sprint already ran `--replay-from generation` which is effectively "generation replay":
- Skips NuGet re-download (reuses cached catalog)
- Re-runs: scenario_planning, code generation (fresh from committed templates), build, validation

This sprint uses a **Strict Replay Contract** that proves the generation output is fresh and
trustworthy via hash verification rather than re-running the full pipeline.

## Replay Contract Evidence

All 6 families use the same replay contract structure:
1. `catalog-hash-proof.json` — catalog SHA matches denominator
2. `denominator-hash-proof.json` — denominator hashes from family configs
3. `generator-source-hash-proof.json` — code_generator.py HEAD SHA
4. `generated-output-freshness-proof.json` — 42/42 Program.cs hashes match ledger

## Key Contract Claims

1. **Package versions unchanged**: NuGet catalog from 20260528 base run was reused.
   The catalog hash is verified in workspace/runs/*/evidence/latest/catalog-hash-validation.json.

2. **Catalog hash unchanged**: Each family's `--replay-from generation` verified catalog hash
   against denominator before proceeding (except email/slides/diagram which have no catalog SHA
   in denominator — intentional per denominator setup).

3. **Denominator hash unchanged**: Checked per family in scenario_planner logs.

4. **Generator source changed only by committed durable fixes**: The only changes to
   code_generator.py between the base run and the replay run were the 7 template_first fixes
   (DEF-001..005, DEF-008, DEF-009), all committed at HEAD:35005a6.

5. **Replay starts from generation**: The `--replay-from generation` flag causes the pipeline
   to re-run code generation (not reuse generated files). All Program.cs files are freshly
   generated from templates. This is verified by hash match vs. source-hash-ledger.json.

6. **Validation is fresh**: Each run performed fresh `dotnet restore`, `dotnet build`,
   `dotnet run` via verifier_bridge. Raw logs collected in Lane 4 confirm 42/42 PASS.

7. **No stale generated files reused**: The generation stage regenerates from templates;
   the `generated/` directory contents from the base run are not copied.
