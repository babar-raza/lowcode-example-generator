# New Family Controlled Pilot Readiness Assessment

**Run ID:** 20260511-105914
**Date:** 2026-05-11
**Sprint:** new-family-classification-readiness-parallel
**Overall Verdict:** ALL_THREE_FAMILIES_READY_FOR_PILOT_WITH_PREREQUISITES

## Recommended Pilot Order

1. **Diagram** (LOW risk) - Simplest API. Static Process(file, file). XML docs present.
2. **Slides** (MEDIUM risk) - Convert.ToPdf(string, string) is clean. XML docs missing.
3. **Email** (MEDIUM risk) - Novel async + Stream + IOutputHandler callback pattern.

---

## Diagram (Aspose.Diagram.LowCode)

**Readiness:** READY_FOR_PILOT_AFTER_CONFIG_PROMOTION
**API Pattern:** STATIC_PROCESS (same as Cells/Words)
**Risk:** LOW
**Pilot Complexity:** SIMPLE

### Workflow Root Types
| Type | Methods | Pattern |
|------|---------|---------|
| DiagramConverter | Process(string, string), Process(LoadOptions, SaveOptions) | Static, file-to-file |
| PdfConverter | Process(string, string), Process(LoadOptions, SaveOptions) | Static, file-to-file |

### Smallest Safe First Example
- **Type:** PdfConverter
- **Method:** `Process(string templateFile, string resultFile)`
- **Code:** `PdfConverter.Process("input.vsdx", "output.pdf")`
- **Fixture:** programmatic_vsdx_single (1 page, 1 shape)
- **Validation:** output.pdf exists, starts with %PDF

### Prerequisites for Tier-5
1. Change YAML status: `discovery_only` -> `experimental`
2. Set `allowed_types: [DiagramConverter, PdfConverter]`
3. Register programmatic_vsdx_single fixture
4. Provision target repo: `aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples`
5. GPT_OSS_* + EXAMPLE_REVIEWER_PATH credentials

---

## Email (Aspose.Email.LowCode)

**Readiness:** READY_FOR_PILOT_AFTER_CONFIG_PROMOTION_AND_TEMPLATE_WORK
**API Pattern:** STATIC_ASYNC_STREAM_CALLBACK (novel)
**Risk:** MEDIUM
**Pilot Complexity:** MEDIUM

### Workflow Root Types
| Type | Methods | Pattern |
|------|---------|---------|
| Converter | 7 static async methods | All take (Stream, string, IOutputHandler), return Task |

### Support Types
| Type | Role | Purpose |
|------|------|---------|
| FolderOutputHandler | provider_callback | Concrete IOutputHandler that writes to folder |
| IOutputHandler | interface | Output callback contract |

### Smallest Safe First Example
- **Type:** Converter
- **Method:** `ConvertToMsg(Stream input, string nameWithExtension, IOutputHandler handler)`
- **Fixture:** programmatic_eml_single (minimal EML with From/To/Subject/Body)
- **Validation:** output .msg file exists, non-zero size
- **Code Template NEEDED:** Yes - async pattern + Stream + FolderOutputHandler is novel

### Key Risks
- **Async:** All methods return `Task` - code must use `.GetAwaiter().GetResult()` or `async Main`
- **Stream input:** Methods take `Stream`, not file path - must open `FileStream`
- **Callback output:** `FolderOutputHandler(outputDir)` required, not simple file path
- **No Options class:** All configuration via method selection (ConvertToMsg vs ConvertToEml etc.)

### Prerequisites for Tier-5
1. Change YAML status: `discovery_only` -> `experimental`
2. Set `allowed_types: [Converter]`
3. Create Email-specific code template for packet builder (async + Stream + FolderOutputHandler)
4. Register programmatic_eml_single or programmatic_msg_single fixture
5. Provision target repo: `aspose-email-net/Aspose.Email.LowCode-for-.NET-Examples`
6. GPT_OSS_* + EXAMPLE_REVIEWER_PATH credentials

---

## Slides (Aspose.Slides.LowCode)

**Readiness:** READY_FOR_PILOT_AFTER_CONFIG_PROMOTION_AND_TEMPLATE_WORK
**API Pattern:** STATIC_CLASS (all types are static classes)
**Risk:** MEDIUM
**Pilot Complexity:** MEDIUM

### Workflow Root Types
| Type | Methods | Safe for Pilot | Notes |
|------|---------|----------------|-------|
| Convert | 18 | YES (tier 1) | ToPdf(string, string) is simplest |
| Merger | 4 | YES (tier 1) | Process(string[], string) is straightforward |
| Compress | 3 | MAYBE (tier 2) | Takes Presentation object, modifies in-place |
| Collect | 1 | NO (tier 3) | Returns IEnumerable<Shape>, not file output |
| ForEach | 10 | NO (tier 3) | Requires delegate callbacks |

### Smallest Safe First Example
- **Type:** Convert
- **Method:** `ToPdf(string presPath, string outPath)`
- **Code:** `Convert.ToPdf("input.pptx", "output.pdf")`
- **Fixture:** programmatic_pptx_single (1 slide with title)
- **Validation:** output.pdf exists, starts with %PDF

### Key Risks
- **XML docs MISSING** - LLM has reduced context for 36 methods across 5 types
- **18 overloads on Convert** - LLM may pick wrong one without guidance
- **ForEach/Collect require delegates** - too complex for initial pilot
- **Some methods need Presentation object** - not just file path input

### Prerequisites for Tier-5
1. Change YAML status: `discovery_only` -> `experimental`
2. Set `allowed_types: [Convert, Merger]` (defer ForEach, Collect, Compress initially)
3. Set `preferred_methods_per_type: {Convert: ToPdf, Merger: Process}`
4. Create few-shot code templates to compensate for missing XML docs
5. Register programmatic_pptx_single and programmatic_pptx_pair fixtures
6. Provision target repo: `aspose-slides-net/Aspose.Slides.LowCode-for-.NET-Examples`
7. GPT_OSS_* + EXAMPLE_REVIEWER_PATH credentials
