# Slides Compress — Fixture Generation

**Date:** 2026-05-24
**Sprint 75 Gap:** No input.pptx was available during sprint75 validation.
**Sprint 76 Fix:** Real .pptx fixture sourced from existing workspace.

---

## Fixture Source

**Path:** `workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/compress/input.pptx`

This fixture was created by `create_fixture.csx` during the slides controlled-pilot dry-run
(sprint era 2026-05-18). It was generated programmatically using Aspose.Slides:
- Creates a new Presentation
- Adds one slide with a Rectangle shape containing text "LowCode Compress Demo"
- Saves as input.pptx

**Size:** 34,242 bytes
**SHA-256:** b14bd40bf4e338a238c86c5491aa08ead44b799f1af444de24750d4635bbf427

---

## Fixture Placement

Copied to: `reports/sprint75/handoff/per-family/slides/compress/input.pptx`

Command:
```
cp workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/compress/input.pptx \
   reports/sprint75/handoff/per-family/slides/compress/input.pptx
```

This is the same fixture used by the dry-run pipeline, confirming the example works with
a real Aspose.Slides-generated PPTX file.

---

## Why This Fixture Was Missing in Sprint 75

Sprint 75 runtime validation ran the compress example without placing input.pptx in the
working directory. The program's guard clause (`if (!File.Exists(inputPath))`) fired and
exited cleanly. This was incorrectly classified as sufficient for `post_merge_validated=true`.

Sprint 76 places the real fixture and runs end-to-end compression, confirming the
`Compress.RemoveUnusedLayoutSlides()` API is actually called and produces output.
