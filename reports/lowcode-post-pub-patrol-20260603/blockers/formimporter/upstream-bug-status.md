# FormImporter Upstream Bug Status

Status: **UPSTREAM_BUG** (unchanged)
Package: Aspose.PDF 26.5.0
Latest available: 26.5.0 (same)
Retry possible: NO (no newer version)
Last checked: 2026-06-03 (lowcode-post-pub-patrol-20260603)

Bug: `Aspose.Pdf.LowCode.FormImporter.Process()` throws `NullReferenceException`
in `Form.ImportJson(Stream)` for all 3 JSON fixture formats:
1. Flat key-value: `{"field1": "value1"}`
2. Array format: `[{"field": "field1", "value": "value1"}]`
3. Nested format: `{"form": {"fields": [{"name": "field1", "value": "value1"}]}}`

Does NOT block the 44 published examples.
Next action: Retry when Aspose.PDF > 26.5.0 releases.
