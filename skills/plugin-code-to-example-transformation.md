# Skill: Plugin-Code to Example Transformation

## Purpose
Transform official plugin code into a runnable Aspose SDK example using the format established by existing published examples.

## Inputs
- family_slug + plugin_slug
- Registry entry (must be READY_FOR_TRANSFORMATION or CODE_HARVESTED)
- Official code file from .local/code-cache/{family}/{plugin_slug}/
- Implementation model from registry
- Fixture plan from registry
- Family config (pipeline/configs/families/{family}.yml) — DO NOT MODIFY

## Outputs
- Example folder: src/plugin_examples/{family}/{plugin_slug}/
- Example .csproj file
- Program.cs with runnable code
- Input fixtures
- Expected output
- README.md (following published example format)
- Updated registry entry: status → TRANSFORMED_TO_EXAMPLE

## Prerequisites
- Registry status = CODE_HARVESTED or READY_FOR_TRANSFORMATION
- Official code file available in .local/code-cache/
- Family analysis complete
- NuGet package available (check pipeline/plugin-capability-registry/package-aliases.json)
- DllReflector or probe confirmed classes exist (preferred)

## Step-by-Step Method

1. Read official code from .local/code-cache/{family}/{plugin_slug}/*.cs
2. Extract the core operation (the Run() method or equivalent)
3. Adapt for example format:
   a. Wrap in Main() or Program entry
   b. Add Aspose license setup (trial-safe approach)
   c. Replace hardcoded paths with fixture references
   d. Ensure output path is deterministic and testable
4. Create example folder structure:
   - src/plugin_examples/{family}/{plugin_slug}/
   - {plugin_slug}.csproj (with NuGet package reference from aliases)
   - Program.cs (adapted code)
   - input/ (fixtures)
   - expected/ (expected output checksums)
5. Run: dotnet restore + dotnet build + dotnet run
6. Verify output exists and matches expected type
7. Record diff from official code in validation report
8. Update registry entry to TRANSFORMED_TO_EXAMPLE
9. Update registry history

## Checks
- [ ] Official code cited in transformation
- [ ] No API invented beyond official code
- [ ] Fixtures documented
- [ ] Output validated (file exists + correct extension)
- [ ] Diff from official code recorded
- [ ] Registry entry updated

## Failure Modes
- Build fails: Check NuGet package ID; verify DLL version compatibility
- Runtime fails: Check fixture format; check trial license restriction
- Output empty: May be trial watermark limitation
- API not found: Downgrade to NEEDS_MANUAL_MAPPING; do NOT guess alternative API

## Evidence Requirements
- validation/snippets/{family}-{plugin}/original-code.cs
- validation/snippets/{family}-{plugin}/diff-from-official-snippet.md
- validation/snippets/{family}-{plugin}/build.log
- validation/snippets/{family}-{plugin}/run.log
- validation/snippets/{family}-{plugin}/final-verdict.md

## Example Reference
See: existing published LowCode examples in src/plugin_examples/

## Stop Rules
- Do NOT publish to external repos (hard constraint)
- Do NOT modify published LowCode examples
- Do NOT modify protected family YAMLs
- If official API pattern fails, record failure — do NOT silently substitute
- If output is empty/watermarked, note ENVIRONMENT_DEPENDENT

## Continue Rules
- ENVIRONMENT_DEPENDENT result is acceptable; document and continue
- Partial success (build OK but output watermarked) = PARTIAL_PASS
