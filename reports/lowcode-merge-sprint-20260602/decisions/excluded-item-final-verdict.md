# Excluded Item Final Verdict

Sprint: lowcode-merge-sprint-20260602
Items audited: 12
Decisions changed: 0

- email/email-converter: KEEP_EXCLUDED_DUPLICATE — Confirmed duplicate. Original publishable example exists with same Program.cs.
- pdf/form-importer: KEEP_EXCLUDED_UPSTREAM_BUG — NullReferenceException in Aspose.PDF 26.5.0 Process(). Latest NuGet is 26.5.0. No newer version available.
- slides/for-each: KEEP_EXCLUDED_HELPER — ForEach is a utility iterator, not a standalone file I/O example.
- slides/slides-compress: KEEP_EXCLUDED_DUPLICATE — Confirmed duplicate. Original publishable example exists with same Program.cs.
- slides/slides-convert: KEEP_EXCLUDED_DUPLICATE — Confirmed duplicate. Original publishable example exists with same Program.cs.
- slides/slides-merger: KEEP_EXCLUDED_DUPLICATE — Confirmed duplicate. Original publishable example exists with same Program.cs.
- words/processor: KEEP_EXCLUDED_NOT_MAIN_CLASS — No public constructor (CS1729). Cannot instantiate. Confirmed via prior build test.
- words/ofd: KEEP_EXCLUDED_UNSUPPORTED_FORMAT — Format not supported by the LowCode API. Runtime ArgumentException confirmed.
- cells/spreadsheet-printer: KEEP_EXCLUDED_NOT_IN_CATALOG — No such type exists in the Aspose.Cells.LowCode namespace.
- pdf/pdf-extractor: KEEP_EXCLUDED_NOT_MAIN_CLASS — Abstract base class. Concrete implementations (TextExtractor, ImageExtractor, Jpeg, Png, Tiff) are published.
- pdf/pdf-to-image: KEEP_EXCLUDED_NOT_MAIN_CLASS — Abstract base class. Concrete implementations (TextExtractor, ImageExtractor, Jpeg, Png, Tiff) are published.
- pdf/ofd: KEEP_EXCLUDED_UNSUPPORTED_FORMAT — Format not supported by the LowCode API. Runtime ArgumentException confirmed.

## Conclusion
All 12 exclusions confirmed correct. No items reclassified to PUBLISH.
