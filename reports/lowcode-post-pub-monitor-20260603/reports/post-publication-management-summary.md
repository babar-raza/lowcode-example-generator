# Post-Publication Management Summary

Date: 2026-06-03
Sprint: lowcode-post-pub-monitor-20260603

## 1. What Was Published
44 LowCode C# examples across 6 Aspose product families, demonstrating SDK-style usage
of the Aspose LowCode plugin APIs (.NET 8.0).

## 2. Repositories Touched

| Repository | Org |
|-----------|-----|
| Aspose.Cells.LowCode-for-.NET-Examples | aspose-cells-net |
| Aspose.Diagram.LowCode-for-.NET-Examples | aspose-diagram-net |
| Aspose.Email.LowCode-for-.NET-Examples | aspose-email-net |
| Aspose.PDF.LowCode-for-.NET-Examples | aspose-pdf-net |
| Aspose.Slides.LowCode-for-.NET-Examples | aspose-slides-net |
| Aspose.Words.LowCode-for-.NET-Examples | aspose-words-net |

## 3. Examples Per Family

| Family | Count | Examples |
|--------|-------|----------|
| cells | 9 | html-converter, image-converter, json-converter, pdf-converter, spreadsheet-converter, spreadsheet-locker, spreadsheet-merger, spreadsheet-splitter, text-converter |
| diagram | 2 | diagram-converter, pdf-converter |
| email | 1 | converter |
| pdf | 20 | doc-converter, form-editor, form-exporter, form-flattener, html, image-extractor, jpeg, merger, optimizer, pdfa-converter, png, security, signature, splitter, table-generator, text-extractor, tiff, timestamp, toc-generator, xls-converter |
| slides | 3 | compress, convert, merger |
| words | 9 | comparer, converter, mail-merger, merger, replacer, report-builder, signer, splitter, watermarker |
| **Total** | **44** | |

## 4. What Remains Excluded and Why

| Excluded | Reason |
|----------|--------|
| words/Processor | PERMANENTLY_BLOCKED — no public constructor |
| words/OFD | UNSUPPORTED_FORMAT — OFD not supported |
| pdf/FormImporter | UPSTREAM_BUG — NullReferenceException in Aspose.PDF 26.5.0 |
| cells/SpreadsheetPrinter | NOT_IN_API_CATALOG — class doesn't exist |
| slides/ForEach | NON_RUNNABLE_HELPER — utility iterator, not a main class |
| words/Signer | NOT_A_LOWCODE_MAIN_CLASS — published as companion helper (included in 44 count) |
| pdf/Timestamp | ENVIRONMENT_DEPENDENT_PASS — needs TSA server (included in 44 count, works online) |

## 5. Only Upstream Blocker
**FormImporter** (Aspose.PDF 26.5.0): `Form.ImportJson(Stream)` throws `NullReferenceException`.
No newer package version available. Retry when Aspose.PDF > 26.5.0 releases.

## 6. Monitoring In Place
- **Live repo state monitoring**: Example count, README completeness, branch hygiene
- **E2E patrol**: Smoke run of all 44 examples from fresh clones
- **Output validation**: Diagram converter, PDF timestamp, PDF signature, Words signer
- **FormImporter watch**: NuGet version probe on each monitoring run
- **8 post-publication validators**: README, Program.cs/csproj, certificates, outputs, branches, retry status, carryforward

## 7. What Would Trigger a New Publication Sprint
- Aspose.PDF > 26.5.0 released and FormImporter bug fixed → add FormImporter example
- New LowCode API class added to any family → generate and publish new example
- Existing example breaks on newer SDK version → repair PR
- README drift detected → repair PR
- New family promoted to LOWCODE_CONFIRMED → full publication for that family
