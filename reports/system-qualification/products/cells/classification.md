# Product Classification: cells

**Run ID:** sysqual-20260528-001
**Product:** Aspose.Cells for .NET
**Package:** Aspose.Cells
**Version:** 26.5.1
**Classification:** LOWCODE_CONFIRMED
**Discovery Verdict:** LOWCODE_CONFIRMED
**E2E Required:** True

## Evidence

- Source: `workspace/verification/latest/cells-source-of-truth-proof.json`
- Scan Method: `dll_reflection_via_dllreflector`
- LowCode Namespace Found: `True`
- Matched Namespaces: `[{'namespace': 'Aspose.Cells.LowCode', 'matched_by_pattern': 'Aspose.Cells.LowCode', 'public_type_count': 22, 'public_method_count': 33}]`
- Public Plugin Types: `22`

## Justification

Aspose.Cells confirmed to have LowCode namespace via DLL reflection. 22 plugin types found. Product is in active pipeline status.
