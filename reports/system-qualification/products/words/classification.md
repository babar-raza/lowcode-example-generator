# Product Classification: words

**Run ID:** sysqual-20260528-001
**Product:** Aspose.Words for .NET
**Package:** Aspose.Words
**Version:** 26.5.0
**Classification:** LOWCODE_CONFIRMED
**Discovery Verdict:** LOWCODE_CONFIRMED
**E2E Required:** True

## Evidence

- Source: `workspace/verification/latest/words-source-of-truth-proof.json`
- Scan Method: `dll_reflection_via_dllreflector`
- LowCode Namespace Found: `True`
- Matched Namespaces: `[{'namespace': 'Aspose.Words.LowCode', 'matched_by_pattern': 'Aspose.Words.LowCode', 'public_type_count': 25, 'public_method_count': 230}]`
- Public Plugin Types: `25`

## Justification

Aspose.Words confirmed to have LowCode namespace via DLL reflection. 25 plugin types found. Product is in active pipeline status.
