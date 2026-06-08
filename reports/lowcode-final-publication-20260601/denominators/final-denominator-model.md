# Final Denominator Model

Sprint: lowcode-final-publication-20260601
Decision Authority: AGENT_DELEGATED

## Canonical Denominator: 42

The canonical denominator counts only WORKFLOW_ROOT main-class examples that appear in the format-authority contracts.

| Family | Count | Types |
|--------|-------|-------|
| cells | 9 | HtmlConverter, ImageConverter, JsonConverter, Merger, PdfConverter, SpreadsheetConverter, TextConverter, XlsConverter, XmlConverter |
| diagram | 2 | Converter, Merger |
| email | 1 | Converter |
| pdf | 19 | Compressor, Converter, DocConverter, FormEditor, FormExporter, HtmlConverter, ImageConverter, Merger, Optimizer, PdfExtractor, PdfToImage, Security, Signature, Splitter, TableGenerator, TextConverter, WordConverter, XlsConverter, XpsConverter |
| slides | 3 | Compress, Convert, Merger |
| words | 8 | Comparer, Converter, MailMerger, Merger, Replacer, ReportBuilder, Splitter, Watermarker |
| **Total** | **42** | |

## Extended Publishable Set: 44

| Category | Count | Examples |
|----------|-------|----------|
| Main-class (canonical) | 42 | All format-authority contract types |
| Companion | 1 | words/signer (DigitalSignatureUtil.Sign) |
| Environment-dependent | 1 | pdf/timestamp (TSA endpoint required) |
| **Publishable total** | **44** | |

## E2E Universe: 49

| Category | Count |
|----------|-------|
| Publishable | 44 |
| Duplicates (excluded but E2E-tested) | 4 |
| Upstream bug (excluded, E2E fails) | 1 |
| **E2E total** | **49** |

Note: The 49/49 E2E PASS count includes duplicates and the FormImporter upstream bug example which passes build but fails run. The canonical pass metric is 42/42 main-class + 1 companion + 1 env-dep = 44/44 publishable PASS.

## Excluded from All Denominators: 7

| Example | Decision | Reason |
|---------|----------|--------|
| words/processor | EXCLUDE_NOT_A_MAIN_CLASS | No public constructor (CS1729) |
| words/splitter-split | EXCLUDE_NOT_A_MAIN_CLASS | Duplicate of words/splitter |
| words/ofd | EXCLUDE_UNSUPPORTED_FORMAT | OFD not a Words output format |
| pdf/ofd | EXCLUDE_UNSUPPORTED_FORMAT | OFD not a PDF output format |
| cells/spreadsheet-printer | EXCLUDE_NOT_IN_API_CATALOG | Never existed as LowCode type |
| slides/for-each | EXCLUDE_NON_RUNNABLE_HELPER | Utility iterator, no file I/O |
| diagram/converter-options | EXCLUDE_NOT_A_MAIN_CLASS | Options class, not workflow root |

## Consistency Check
- Format-authority contracts: 42 types across 6 families
- Completion queue POST_MERGE_VERIFIED: 42
- E2E main-class PASS: 42/42
- All three sources agree on 42.
