# New Family Type-Role Classification Summary

**Run ID:** 20260511-105914
**Date:** 2026-05-11
**Sprint:** new-family-classification-readiness-parallel

## Diagram (Aspose.Diagram.LowCode)

| Type | Role | Confidence | Methods | Static | Instance | Constructors |
|------|------|-----------|---------|--------|----------|-------------|
| DiagramConverter | workflow_root | 0.95 | 2 | Yes | No | No |
| PdfConverter | workflow_root | 0.95 | 2 | Yes | No | No |
| LowCodeLoadOptions | options | 0.90 | 0 | No | No | Yes |
| LowCodePdfSaveOptions | options | 0.90 | 0 | No | No | Yes |
| LowCodeSaveOptions | options | 0.90 | 0 | No | No | Yes |

**Workflow-root types:** DiagramConverter, PdfConverter
**Pattern:** Static `Process(string templateFile, string resultFile)` and `Process(LowCodeLoadOptions, LowCodeSaveOptions)`
**Input:** VSD/VSDX diagram files
**Output:** Converted files (PDF for PdfConverter, various formats for DiagramConverter via SaveFormat)

## Email (Aspose.Email.LowCode)

| Type | Role | Confidence | Methods | Static | Instance | Constructors |
|------|------|-----------|---------|--------|----------|-------------|
| Converter | workflow_root | 0.95 | 7 | Yes | No | Yes |
| FolderOutputHandler | provider_callback | 0.95 | 2 | No | Yes | Yes |
| IOutputHandler | interface_contract | 1.00 | 2 | No | No | No |

**Workflow-root types:** Converter
**Pattern:** Async static methods returning `Task`. All take `Stream input, string nameWithExtension, IOutputHandler handler` plus format hint.
**Methods:** Convert, ConvertEmlOrMsg, ConvertToEml, ConvertToHtml, ConvertToMht, ConvertToMhtml, ConvertToMsg
**Input:** MSG/EML via Stream
**Output:** Via IOutputHandler callback (FolderOutputHandler writes to disk)
**Complexity note:** Async pattern + Stream-based I/O + callback handler is more complex than Cells/Words/PDF patterns.

## Slides (Aspose.Slides.LowCode)

| Type | Role | Confidence | Methods | Static | Instance | Constructors |
|------|------|-----------|---------|--------|----------|-------------|
| Convert | workflow_root | 0.70 | 18 | Yes | No | No |
| Merger | workflow_root | 0.95 | 4 | Yes | No | No |
| Compress | workflow_root | 0.70 | 3 | Yes | No | No |
| Collect | workflow_root | 0.70 | 1 | Yes | No | No |
| ForEach | workflow_root | 0.70 | 10 | Yes | No | No |

**Workflow-root types:** Convert, Merger, Compress, Collect, ForEach (all 5 types)
**Pattern:** All are static_class with static methods only. No constructors, no instance methods.
**Simplest entry points:**
- `Convert.ToPdf(string presPath, string outPath)` — simplest overload
- `Convert.AutoByExtension(string presPath, string outPath)` — auto-detect
- `Merger.Process(string[] inputFileNames, string outputFileName)` — merge files
- `Compress.CompressEmbeddedFonts(Presentation pres)` — modifies in-place

**Input:** PPTX files
**Output:** Varies (PDF, JPEG, PNG, SVG, TIFF, merged PPTX)
**Complexity notes:**
- Many overloads take `Presentation` object (not just file path) — requires loading presentation first
- ForEach requires delegate callbacks (ForEachSlideCallback, etc.) — may be hard for LLM to generate correctly
- Convert.ToSvg requires GetOutPathCallback delegate
- XML docs are MISSING — LLM will have reduced context for method signatures

## Summary

| Family | Total Types | Workflow Root | Options | Other | Simplest Pilot Method |
|--------|------------|--------------|---------|-------|-----------------------|
| diagram | 5 | 2 | 3 | 0 | DiagramConverter.Process(string, string) |
| email | 3 | 1 | 0 | 2 | Converter.ConvertToMsg(Stream, string, IOutputHandler) |
| slides | 5 | 5 | 0 | 0 | Convert.ToPdf(string, string) |

## Recommended Pilot Order

1. **Diagram** — Simplest API surface. 2 workflow roots with straightforward Process(file, file) pattern. Similar to existing Cells/Words pattern.
2. **Slides** — Rich API surface but Convert.ToPdf(string, string) is a clean entry point. Merger.Process is also straightforward.
3. **Email** — Async + Stream + callback pattern is the most novel. Needs careful fixture and code template design.
