# Lane D — PDF Next-Expansion Report

**Status:** ALL_GAPS_BLOCKED

## PDF Workflow Root Denominator

- Total LowCode types: 101
- Workflow roots: 22
- Pilot-allowed: 19
- Contracts: 19
- Published: 5
- Pending (in open PRs): 14
- Gap (workflow roots not in pilot): 3

## Reclassified Types (excluded from 22 count)

The type-role-classification.json lists 25 types as WORKFLOW_ROOT, but 3 were reclassified:

| Type | Reclassified To | Sprint | Reason |
|------|----------------|--------|--------|
| PdfExtractor | ABSTRACT_BASE | Sprint 7 | Abstract class, not instantiable |
| PdfToImage | ABSTRACT_BASE | Sprint 22 | Abstract base for Jpeg/Png/Tiff |
| SelectField | PROVIDER_CALLBACK | Sprint 24 | DELEGATE type (Invoke/BeginInvoke/EndInvoke only) |

## The 3 Workflow Root Gaps

### 1. FormImporter — BLOCKED (Library Bug)

- **Full name:** Aspose.Pdf.LowCode.FormImporter
- **Options:** FormImporterJsonOptions (confirmed Sprint 26)
- **Block reason:** Aspose.PDF 26.5.0 contains a defect affecting FormImporter
- **NuGet check:** Latest Aspose.PDF is 26.5.0, no newer version available
- **Retest condition:** Aspose.PDF > 26.5.0 released with fix
- **Taskcard:** TC-PDF-FORMIMPORTER-RETEST
- **State:** BLOCKED

### 2. Timestamp — PERMANENTLY_BLOCKED

- **Full name:** Aspose.Pdf.LowCode.Timestamp
- **Block reason:** Requires external TSA (Time Stamping Authority) ServerUrl
- **No programmatic fixture possible** — needs live network TSA endpoint
- **Cannot be made deterministic** for example generation
- **Taskcard:** TC-PDF-TIMESTAMP-PERMANENTLY-BLOCKED
- **State:** PERMANENTLY_BLOCKED

### 3. Ofd — PERMANENTLY_BLOCKED

- **Full name:** Aspose.Pdf.LowCode.Ofd
- **Block reason:** Requires OFD (Open Fixed-layout Document) input format
- **No programmatic fixture possible** — cannot create valid OFD documents programmatically via Aspose
- **Taskcard:** TC-PDF-OFD-PERMANENTLY-BLOCKED
- **State:** PERMANENTLY_BLOCKED

## Safe Runnable Candidates

**None.** All 3 gaps are blocked:
- 1 blocked by library bug (may become unblocked with package update)
- 2 permanently blocked (architectural impossibility)

## Projected PDF State After PR Merge

| Metric | Current | After Merge |
|--------|---------|-------------|
| Published | 5 | 19 |
| Pending | 14 | 0 |
| Pilot coverage | 26.3% | 100% |
| Workflow root coverage | 22.7% | 86.4% (19/22) |
| Gap | 3 blocked | 3 blocked (unchanged) |
