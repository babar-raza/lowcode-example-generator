# Probe Registry Guide

Audience: Operator, Contributor

Purpose: Use `probe-registry` to validate non-LowCode capability registry entries by generating and executing C# probe code, then promote confirmed entries.

Canonical references: [CLI Reference](../reference/cli.md), [Repository Structure](../development/repo-structure.md)

Last verified: 2026-06-17

---

## What Probe Registry Does

The probe pipeline validates entries in `pipeline/plugin-capability-registry/{family}.yaml` by:

1. **Generating** a minimal C# project for each eligible registry entry (via `src/plugin_examples/probe_generator/registry_probe.py`)
2. **Executing** `dotnet restore`, `dotnet build`, and `dotnet run` for each generated project (via `src/plugin_examples/probe_executor/executor.py`)
3. **Classifying** results as `PROBE_CONFIRMED` or `PROBE_FAILED_*`
4. **Promoting** confirmed entries back into the registry YAML (via `src/plugin_examples/probe_executor/promoter.py`)

This is the primary mechanism for advancing non-LowCode family entries from discovery status (`REFLECTION_CANDIDATE`, `WEBSITE_DISCOVERED`, `PROBE_CANDIDATE`) to `PROBE_CONFIRMED` — the gate for further example generation.

---

## Prerequisites

- Python environment active: `source .venv/Scripts/activate`
- .NET SDK 8.0 or newer installed and on PATH (`dotnet --version` must succeed)
- Registry file exists: `pipeline/plugin-capability-registry/{family}.yaml`
- Entries have status `REFLECTION_CANDIDATE`, `WEBSITE_DISCOVERED`, or `PROBE_CANDIDATE`

---

## Eligible Entry Statuses

| Status | Meaning | Probe eligible |
|---|---|---|
| `REFLECTION_CANDIDATE` | Found via NuGet reflection | YES |
| `WEBSITE_DISCOVERED` | Found via catalog discovery | YES |
| `PROBE_CANDIDATE` | Manually designated for probing | YES |
| `PROBE_CONFIRMED` | Already confirmed | NO (skipped) |
| `PROBE_FAILED_*` | Already failed | NO (skipped unless re-run) |

---

## Running the Probe

### Step 1: Dry Run (no execution)

Generate probe code without running it. No network or dotnet calls:

```powershell
python -m plugin_examples probe-registry --family drawing
```

Output shows generated file paths under `.local/psal/probes/{family}/{slug}/`. No registry is modified.

### Step 2: Execute Probes

Run dotnet restore/build/run for all eligible entries:

```powershell
python -m plugin_examples probe-registry --family drawing --execute
```

Output table shows per-entry status and duration. Registry is NOT modified yet.

### Step 3: Execute and Promote

Execute probes and write results back to the registry YAML:

```powershell
python -m plugin_examples probe-registry --family drawing --execute --promote
```

`--promote` requires `--execute`. The registry YAML is updated in-place.

### Probe a Single Entry

```powershell
python -m plugin_examples probe-registry --family drawing --slug drawing-converter --execute --promote
```

### JSON Output

```powershell
python -m plugin_examples probe-registry --family drawing --execute --json
```

### Timeout Override

Increase the per-phase timeout for slow builds (default: 120 seconds):

```powershell
python -m plugin_examples probe-registry --family drawing --execute --timeout 300
```

---

## Output and Evidence

Generated probe projects are written to:

```
.local/psal/probes/{family}/{slug}/
  Program.cs        # Generated C# probe code
  {slug}.csproj     # Project file with NuGet references
```

Probe evidence JSON is recorded per entry. When `--promote` is used, the registry YAML is updated with:

- `status`: `PROBE_CONFIRMED` or `PROBE_FAILED_*`
- `probe_evidence_path`: path to the evidence JSON
- `next_action`: set by the promoter based on failure taxonomy (see below)

---

## Result Classification

| Outcome status | Meaning | `next_action` set by promoter |
|---|---|---|
| `PROBE_CONFIRMED` | restore + build + run all passed | — |
| `PROBE_FAILED_BUILD` | Build failed (C# compile error) | `NEEDS_API_MAPPING_FIX` |
| `PROBE_FAILED_API` | Runtime error (wrong API usage) | `NEEDS_RUNTIME_FIX` |
| `PROBE_FAILED_LICENSE` | License-restricted NuGet | `BLOCKED_LICENSE_RESTRICTED` |
| `PROBE_FAILED_RESTORE` | NuGet restore failed | `NEEDS_DEPENDENCY_FIX` |
| `PROBE_FAILED_TIMEOUT` | dotnet phase timed out | `NEEDS_TIMEOUT_INCREASE` |

---

## Interpreting the Output Table

```text
Family       Slug                           Status                    Duration
--------------------------------------------------------------------------------
drawing      drawing-converter              PROBE_CONFIRMED               4823ms
drawing      image-processing              PROBE_FAILED_BUILD             2104ms

Summary: 1 confirmed, 1 failed, 2 total
```

Entries with `PROBE_CONFIRMED` are ready for example generation via the main `run` pipeline. Entries with `PROBE_FAILED_*` require investigation per the `next_action` field.

---

## Flags Summary

| Flag | Required | Default | Purpose |
|---|---|---|---|
| `--family` | YES | — | Family slug (matches `pipeline/plugin-capability-registry/{family}.yaml`) |
| `--slug` | NO | all eligible | Probe only one specific `plugin_slug` |
| `--execute` | NO | false (dry-run) | Actually run dotnet restore/build/run |
| `--promote` | NO | false | Write probe results back to registry YAML (requires `--execute`) |
| `--timeout` | NO | 120 | Per-phase subprocess timeout in seconds |
| `--json` | NO | false | Output results as JSON instead of table |

---

## Integration with PSAL

The PSAL multi-family loop (`psal-run`) calls the probe pipeline automatically for families that have entries in probeable status. For manual one-off probing or debugging individual families, use `probe-registry` directly as shown above.

See [CLI Reference](../reference/cli.md) for `psal-run` flags.
