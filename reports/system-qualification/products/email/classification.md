# Product Classification: email

**Run ID:** sysqual-20260528-001
**Product:** Aspose.Email for .NET
**Package:** Aspose.Email
**Version:** 26.4.0
**Classification:** LOWCODE_CONFIRMED
**Discovery Verdict:** LOWCODE_CONFIRMED
**E2E Required:** True

## Evidence

- Source: `workspace/verification/latest/email-source-of-truth-proof.json`
- Scan Method: `dll_reflection_via_dllreflector`
- LowCode Namespace Found: `True`
- Matched Namespaces: `[{'namespace': 'Aspose.Email.LowCode', 'matched_by_pattern': 'Aspose.Email.LowCode', 'public_type_count': 3, 'public_method_count': 11}]`
- Public Plugin Types: `3`

## Justification

Aspose.Email confirmed to have LowCode namespace via DLL reflection. 3 plugin types found. Product is in active pipeline status.
