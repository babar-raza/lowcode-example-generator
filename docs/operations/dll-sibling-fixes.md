# Per-Family DLL Sibling Fix Requirements

Audience: Operator, Pipeline engineer
Source of truth: This file + `pipeline/configs/families/*.yml`

Some Aspose NuGet packages declare runtime dependencies on assemblies that are not
automatically included in the standard NuGet resolution chain. DllReflector uses
`MetadataLoadContext` which requires all referenced assemblies to be available at
reflection time. Missing assemblies cause reflection to silently skip types or fail
entirely.

This file documents all known per-family sibling DLL requirements and the fixes applied.

---

## How the Fix Works

In any family config YAML, add `extra_packages` under `dependency_resolution`:

```yaml
nuget:
  dependency_resolution:
    enabled: true
    max_depth: 3
    extra_packages:
      - Aspose.SiblingPackage
```

The pipeline downloads these additional packages and passes their DLL paths to
DllReflector via `--deps`, making them available to `MetadataLoadContext` during reflection.

DllReflector `--deps` flag (see [tools/DllReflector/Program.cs](../../tools/DllReflector/Program.cs)):
```
DllReflector --dll <primary.dll> --output <catalog.json> --deps <dep1.dll> <dep2.dll>
```

---

## Known Per-Family Sibling Issues

| Family | Package | Issue | Root Cause | Fix Applied | Evidence |
|---|---|---|---|---|---|
| OCR | `Aspose.OCR` | `Aspose.Drawing.Common` assembly missing at reflection time | `Aspose.OCR.dll` references `Aspose.Drawing.Common` which is provided by the `Aspose.Drawing` NuGet package (NOT Microsoft's `System.Drawing.Common`) | `extra_packages: [Aspose.Drawing, Aspose.LLM]` in `pipeline/configs/families/ocr.yml` | `pipeline/configs/families/ocr.yml:26` |
| OMR | `Aspose.OMR` | `Newtonsoft.Json.dll` missing at reflection time | `Aspose.OMR.dll` references Json.NET which is not in the default NuGet resolution for the netstandard2.0 TFM group | `extra_packages: [Newtonsoft.Json]` in `pipeline/configs/families/omr.yml` | `pipeline/configs/families/omr.yml:22` |
| Drawing | `Aspose.Drawing` | CS0433 ambiguity between `Aspose.Drawing.Common` and `System.Drawing.Common` | Both `Aspose.Drawing` and `System.Drawing.Common` define `System.Drawing.*` types. Adding `System.Drawing.Common` as a dep causes CS0433 type conflicts at build time. | Do NOT add `System.Drawing.Common` as a dep. `Aspose.Drawing` IS the System.Drawing replacement — use it alone. | MEMORY.md PSAL Probe Pipeline Sprint 20260616 |

---

## Symptom: How to Detect a Missing Sibling DLL

**During reflection:**
- `reflection-catalog.json` has fewer types than expected (types silently skipped).
- DllReflector log shows `Could not load assembly` warnings.
- Probe fails with `PROBE_FAILED_API` because the required type is not in the catalog.

**During build (after generation):**
- CS0433 error: type defined in multiple assemblies.
- Build fails with missing type/method from a namespace that should be present.

**Diagnostic steps:**
1. Run DllReflector directly to see assembly resolution errors:
   ```bash
   dotnet run --project tools/DllReflector -- \
     --dll <path-to-primary.dll> \
     --output /tmp/catalog-test.json
   ```
2. Check output JSON — if `types` array has fewer entries than expected, a sibling DLL is missing.
3. Use `ildasm` or `dotnet-ildasm` to inspect the primary DLL's assembly references:
   ```bash
   # On Linux/macOS with .NET tools
   dotnet-dump analyze <dll>
   # Or use dotnet-ilrepack / simple grep on strings
   strings <primary.dll> | grep "Aspose\.\|System\.Drawing"
   ```
4. Identify the missing reference, find its NuGet package ID, add to `extra_packages`.

---

## Advisory: Type-Count Drop Validator

The pipeline includes an advisory validator that warns when the reflected catalog for a
family has fewer types than the previous run. This can indicate a missing sibling DLL
after a package update.

See: `src/plugin_examples/reflection_catalog/catalog_builder.py` — `_warn_type_count_drop()`

If this warning fires after a package version bump:
1. Check `reflection-catalog.json` for the previous run (in `workspace/evidence/latest/`).
2. Compare type counts.
3. Check if the package update changed assembly references.
4. Update `extra_packages` in the family config if needed.

---

## How to Add a New Sibling Fix

1. Identify the missing assembly (see Diagnostic steps above).
2. Find the NuGet package ID that provides it (search on nuget.org).
3. Add to `extra_packages` in `pipeline/configs/families/<family>.yml`.
4. Rerun the probe: `python -m plugin_examples probe-registry --family <family> --execute`.
5. Confirm the type count increases.
6. Update this file with the new entry in the table above.

---

## Related Configuration

The `collect_all_tfm_deps` flag (also in `dependency_resolution`) forces the resolver
to collect dependencies from ALL TFM groups in the nuspec, not just the best-matching
group. This is required for packages where the `netstandard2.0` nuspec group omits
dependencies that the DLL actually references at runtime.

Example (from `pipeline/schemas/family-config.schema.json`):
```yaml
nuget:
  dependency_resolution:
    collect_all_tfm_deps: true
```

Use when: the package has different dep lists per TFM and reflection under netstandard2.0
fails while the net8.0 group has additional required deps.
