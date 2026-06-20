# Healing Intelligence — Known Failure Patterns

Audience: Pipeline engineer, Operator
Last updated: 2026-06-20
Source of truth: `workspace/verification/latest/healing-intelligence/failure-pattern-registry.json`

**TC-SRHP-07** — This file documents the 5 most common generation and validation failure
patterns observed across real pipeline runs.

---

## Framework Overview

The healing intelligence framework (`src/plugin_examples/healing_intelligence/loader.py`)
provides:

- **Failure patterns**: Known reasons why generation or validation fails, and repair hints.
- **Repair patterns**: Confirmed repair strategies that resolve specific failure IDs.
- **Semantic steering**: Per-family, per-type REQUIRED and FORBIDDEN constraints injected
  into generation prompts to prevent known failure classes.
- **Validator rules**: Extra validation rules derived from historical failures.

The loader is wired into the pipeline at the generation stage via `ctx.healing_intelligence`.
It degrades gracefully — missing registry files are warned about but do not block the run.

---

## Known Failure Patterns

### FP-001 — Missing Namespace / Using Directive

**Pattern name**: `missing_namespace_using_directive`

**Description**: Generated C# code references an Aspose type but omits the corresponding
`using` directive. The build fails with `CS0246: The type or namespace '<Type>' could not be found`.

**Affected families**: words, cells, pdf, imaging, and others

**Root cause**: LLM generates code using the short type name (e.g., `Document`) without
adding `using Aspose.Words;` at the top of the file.

**Repair strategy**: The steering constraints for each family include a `global_required`
entry for the primary using directive. Example for `words`:
```
REQUIRED: using Aspose.Words;
```

**Evidence source**: Sprint wave W12–W15 build failures.

---

### FP-002 — NotImplementedException Stub

**Pattern name**: `not_implemented_exception_stub`

**Description**: Generated code contains `throw new NotImplementedException()` or `// TODO`
comments, indicating the LLM produced a partial answer instead of a working example.

**Affected families**: all (non-specific; affects new family generation more often)

**Root cause**: LLM hedges when it is uncertain about the correct API call. Typically
occurs for newer or less-documented API surfaces.

**Repair strategy**:
1. The `example_scorer.py` quality scorer detects this as a `NO_TODO_STUBS` failure.
2. The generation prompt explicitly forbids `NotImplementedException`.
3. If it appears, re-run generation with `--require-llm` and a more specific prompt.

**Evidence source**: Observed in tex family initial generation (2026-06-17).

---

### FP-003 — Hardcoded Absolute Path

**Pattern name**: `hardcoded_absolute_path_in_example`

**Description**: Generated code contains hardcoded paths like `C:\Users\foo\input.docx`
or `/home/user/input.docx`. These fail on all machines except the LLM's training data.

**Affected families**: all

**Root cause**: LLM is trained on examples from documentation that use hardcoded paths.
Without explicit steering, it reproduces this pattern.

**Repair strategy**:
1. All family prompt templates include: `Use AppContext.BaseDirectory for all file paths.`
2. The `example_scorer.py` quality scorer flags this as a `PATH_SAFETY` failure.
3. Steering constraint: `REQUIRED: AppContext.BaseDirectory`, `FORBIDDEN: C:\`.

**Evidence source**: Consistently present in initial generation; resolved by prompt steering.

---

### FP-004 — Missing Output File (advisory_no_output)

**Pattern name**: `advisory_no_output_validation`

**Description**: The example runs successfully (`dotnet run` exits 0) but produces no
console output and no output file that can be semantically validated.

**Affected families**: imaging, cad, page (conversion-heavy families)

**Root cause**: Some Aspose conversion examples write to a file but print nothing to stdout.
The expected-output contract may not be set up for the output file type.

**Repair strategy**:
1. Add `Console.WriteLine($"Saved to {outputPath}");` after the main operation.
2. Add an `expected-output.json` contract specifying the output file extension and
   minimum file size.
3. If the family has known file-only output, use `--no-strict-output` to allow advisory
   status to pass through to PR creation.

**Evidence source**: imaging family — 3 of 10 examples initially produced no stdout.

---

### FP-005 — Missing Sibling DLL at Reflection Time

**Pattern name**: `missing_sibling_dll_reflection_failure`

**Description**: `DllReflector` silently skips types when a referenced assembly is
missing from `MetadataLoadContext`. The reflected catalog has fewer types than expected,
causing `PROBE_FAILED_API` for types that actually exist in the package.

**Affected families**: ocr (Aspose.Drawing.Common), omr (Newtonsoft.Json)

**Root cause**: Some Aspose packages reference sibling DLLs that are not in the default
NuGet resolution chain for the `netstandard2.0` TFM group. `MetadataLoadContext` requires
all referenced assemblies at reflection time.

**Repair strategy**: Add the missing package to `extra_packages` in the family config:
```yaml
nuget:
  dependency_resolution:
    extra_packages:
      - Aspose.Drawing   # for OCR
```

See `docs/operations/dll-sibling-fixes.md` for the full per-family table.

**Evidence source**: PSAL Probe Pipeline Sprint (2026-06-16).

---

## Adding New Patterns

When a new failure occurs in a real run:

1. `auto_learn_from_run()` in `loader.py` detects it and adds a `CANDIDATE` entry to
   `failure-pattern-registry.json`.
2. After the same failure appears in 3+ runs, promote it to `CONFIRMED`:
   ```json
   { "status": "CONFIRMED", "repair_hint": "..." }
   ```
3. Add the corresponding repair pattern to `repair-pattern-registry.json`.
4. Update this doc with a new FP-NNN entry.
5. Add a unit test to `tests/unit/test_healing_intelligence_wiring.py` or a new file.

**Important**: Only CONFIRMED patterns trigger the automatic repair loop.
CANDIDATE patterns are observation-only.

---

## Testing Healing Patterns

Run the existing healing intelligence tests to verify the framework is wired correctly:

```bash
PYTHONPATH=src python -m pytest tests/unit/test_healing_intelligence_wiring.py -v
PYTHONPATH=src python -m pytest tests/unit/test_healing_auto_learn.py -v
PYTHONPATH=src python -m pytest tests/unit/test_healing_intelligence_loader.py -v
```

---

## Related Documentation

- [DLL Sibling Fixes](dll-sibling-fixes.md) — FP-005 root cause per family
- [Validation and Reviewer](../reference/validation-and-reviewer.md) — output validation context
- [New Family Onboarding](new-family-onboarding.md) — where healing patterns apply in onboarding
