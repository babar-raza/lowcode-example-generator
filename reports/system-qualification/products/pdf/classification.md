# Product Classification: pdf

**Run ID:** sysqual-20260528-001
**Product:** Aspose.PDF for .NET
**Package:** Aspose.PDF
**Version:** 26.5.0
**Classification:** LOWCODE_CONFIRMED
**Discovery Verdict:** LOWCODE_CONFIRMED
**E2E Required:** True

## Evidence

- Source: `workspace/verification/latest/pdf-source-of-truth-proof.json`
- Scan Method: `dll_reflection_via_dllreflector`
- LowCode Namespace Found: `True`
- Matched Namespaces: `[{'namespace': 'Aspose.Pdf.LowCode', 'matched_by_pattern': 'Aspose.Pdf.LowCode', 'public_type_count': 101, 'public_method_count': 71}]`
- Public Plugin Types: `101`

## Justification

Aspose.Pdf confirmed to have LowCode namespace via DLL reflection. 101 plugin types found. Product is in active pipeline status.
