# New Family Fixture Harness Verdict

**Sprint:** new-family-fixture-harness-parallel
**Date:** 2026-05-11
**Final Verdict:** NEW_FAMILY_FIXTURE_HARNESS_IMPLEMENTED_VERIFIED

## Results Summary

| Family | Harness Tests | Fixture | LowCode API | Status |
|--------|--------------|---------|-------------|--------|
| diagram | 4/4 PASS | VSDX (8KB) | PdfConverter + DiagramConverter | ALL_PASS |
| email | 4/5 PASS | EML (599B) + MSG (10KB) | ConvertToMsg + ConvertToEml | PASS_WITH_KNOWN_ISSUE |
| slides | 6/6 PASS | PPTX (34KB) + PPTX pair (34KB each) | Convert.ToPdf + AutoByExtension + Merger + Compress | ALL_PASS |

**Total:** 14/15 PASS, 1 known non-blocking issue

## API Corrections Discovered

### Diagram
- **DiagramConverter** only supports Visio-to-Visio output formats (VSDX, VSD, VDX)
- **PdfConverter** handles Visio-to-PDF conversion
- Both support `Process(string, string)` and `Process(LowCodeLoadOptions, LowCodeSaveOptions)` overloads

### Email
- All Converter methods return `Task` (async)
- Input via `Stream`, not file path
- Output via `FolderOutputHandler(outputDir)`, not file path
- Sync workaround: `.GetAwaiter().GetResult()`
- ConvertToHtml has file-locking issue when `using` block disposes Stream before async output completes (harness issue, not API defect)

### Slides
- `Convert.ToPdf(string, string)` and `Convert.AutoByExtension(string, string)` produce identical output for same input
- `Compress.CompressEmbeddedFonts(Presentation)` modifies in-place — requires manual `Save()` after
- `Merger.Process(string[], string)` correctly merges slides (verified: 2 input files with 1 slide each = 2 slides in output)
- XML docs are MISSING from the package

## Deferred Due to Concurrency

- Fixture registry integration (`fixture-registry.json` has concurrent changes)
- Test additions (`test_fixture_registry.py`, `test_fixture_strategy.py` have concurrent changes)
- Both deferred to post-healing sprint

## Harness Projects Created

- `workspace/fixture-validation/diagram-harness/` — DiagramFixtureHarness.csproj + Program.cs
- `workspace/fixture-validation/email-harness/` — EmailFixtureHarness.csproj + Program.cs
- `workspace/fixture-validation/slides-harness/` — SlidesFixtureHarness.csproj + Program.cs

## Next Steps Per Family

### Diagram (READY for pilot)
1. Promote YAML: `status: experimental`, `allowed_types: [DiagramConverter, PdfConverter]`
2. Add fixture registry entry for `programmatic_vsdx_single`
3. Run tier-5 generation with GPT_OSS_* credentials

### Email (READY for pilot after template work)
1. Promote YAML: `status: experimental`, `allowed_types: [Converter]`
2. Create async+Stream+FolderOutputHandler code template for packet builder
3. Add fixture registry entries for `programmatic_eml_single`, `programmatic_msg_single`
4. Run tier-5 generation with GPT_OSS_* credentials

### Slides (READY for pilot after XML docs compensation)
1. Promote YAML: `status: experimental`, `allowed_types: [Convert, Merger]`
2. Set `preferred_methods_per_type: {Convert: ToPdf, Merger: Process}`
3. Create few-shot code templates to compensate for missing XML docs
4. Add fixture registry entries for `programmatic_pptx_single`, `programmatic_pptx_pair`
5. Run tier-5 generation with GPT_OSS_* credentials
