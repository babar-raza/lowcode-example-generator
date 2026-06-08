# ZIP Family — End-to-End Pilot Report

**Date:** 2026-06-04  
**Family:** zip  
**Package:** Aspose.ZIP 26.5.0  
**Pilot verdict:** PILOT_PASS_PROBE_CONFIRMED

## Flow Executed (12 steps)

1. **Catalog discovery**: `products.aspose.net/zip/net/` identified via package-aliases.json → Aspose.ZIP
2. **NuGet check**: `https://api.nuget.org/v3-flatcontainer/aspose.zip/index.json` → available, latest 26.5.0
3. **Package download**: `aspose.zip.26.5.0.nupkg` (SHA256: 57e69b4e6a8e0525917bc24ff1b1c1d7b5e1fb27b90088b68e91c8d232dc9492)
4. **DLL extraction**: `lib/netstandard2.0/Aspose.Zip.dll` (3,069,336 bytes)
5. **DllReflector**: Ran against Aspose.Zip.dll → output written to `.local/reflection-runs/zip/zip-reflection.json`
6. **Namespace classification**: No LowCode namespace found → `NO_LOWCODE_BUT_PLUGIN_SITE_PRESENT`
7. **Heuristic matcher**: `Archive.Save` matched via verb 'archive', score 0.90, status `PROBE_CANDIDATE`
8. **Manual mapping**: MANUAL_MAPPING confirmed, HallucinationValidator passed (Archive + Save both in reflection)
9. **Probe generation**: `Program.cs` + `zip-probe.csproj` generated — PR-01 through PR-10 verified
10. **Probe execution**: restore OK, build OK, run OK → `probe-output.zip` (319 bytes)
11. **Output validation**: ZIP opened, entry `probe-content.txt` present with correct content → `PROBE_CONFIRMED`
12. **Runner dry-run**: `_stage_fallback_registry_lookup` → OK, 1 PROBE_CONFIRMED candidate loaded

## Key Evidence

| artifact | path |
|----------|------|
| Reflection JSON | `.local/reflection-runs/zip/zip-reflection.json` |
| Probe restore log | `prototypes/zip/probe-restore.log` |
| Probe build log | `prototypes/zip/probe-build.log` |
| Probe run log | `prototypes/zip/probe-run.log` |
| Output validation | `prototypes/zip/output-validation.json` |
| Registry entry | `pipeline/plugin-capability-registry/zip.yaml` |
| Runner dry-run | `pilots/zip/runner-dry-run-result.json` |

## Protected Files — Unchanged

- `pipeline/configs/families/cells.yml` — unchanged
- `pipeline/configs/families/words.yml` — unchanged
- `pipeline/format-authority/manifest.json` — unchanged
- All 6 LowCode family YAMLs — unchanged

## Verdict

**PILOT_PASS_PROBE_CONFIRMED** — full e2e flow succeeded for the ZIP family.
