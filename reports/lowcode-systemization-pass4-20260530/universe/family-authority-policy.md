# Family Universe Authority Policy — lowcode-systemization-pass3-20260530
Date: 2026-05-30

## Policy Statement
The authoritative family list is the USER-REQUIRED list of 26 families. No family
may be silently added or removed from this list without an explicit policy decision
and evidence trail.

## Pass2 Violation
Pass2 silently removed `epub` and added `medical` to maintain a count of 26.
This was not acceptable because:
1. No policy decision was documented
2. epub is a user-required family — even if it has no standalone package, it must
   appear in the universe with an explicit classification
3. medical was added without a scope decision or investigation

## Pass3 Resolution

### epub
- epub IS in the user-required-26 list
- No standalone `Aspose.Epub` NuGet package exists on nuget.org
- EPUB document support exists in TWO Aspose products:
  - Aspose.HTML (EPUB reading/writing as HTML-adjacent format)
  - Aspose.Words (EPUB export as SaveFormat.Epub)
- Classification: FORMAT_CAPABILITY_OF_OTHER_PRODUCT
- LowCode impact: EPUB as a format is covered by the LowCode APIs of Aspose.HTML
  and Aspose.Words; no separate LowCode namespace for EPUB
- Universe position: INCLUDED in user-required-26; classified FORMAT_CAPABILITY_OF_OTHER_PRODUCT

### medical (Aspose.Medical)
- NOT in the user-required-26 list
- IS a real Aspose product (26.3.0, NuGet restore succeeds)
- Scope: DICOM and medical imaging file formats
- Reflection probe: fails due to System.IO.Pipelines dependency (same as psd/ocr)
- Classification: NO_LOWCODE_CONFIRMED (no LowCode namespace; DICOM-specialized)
- Universe position: 27th CANDIDATE — requires separate taskcard and config before
  it can enter example generation pipeline
- Decision: INCLUDE in universe as 27th family (medical_scope_decision.md)

### pub (Aspose.PUB)
- IN user-required-26 list
- Real product: Aspose.PUB 25.12.0, NuGet restore success
- 2320 types, no LowCode namespace
- Classification: NO_LOWCODE_CONFIRMED
- Universe position: INCLUDED in user-required-26

## Summary
Total families tracked: 27 (26 user-required + 1 candidate)
User-required-26: all present with explicit classification
27th (medical): included with candidate status and scope decision
