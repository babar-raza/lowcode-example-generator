# EPUB: Product vs Format Decision — lowcode-systemization-pass3-20260530
Date: 2026-05-30

## Question
Is epub a product (standalone Aspose package) or a format capability?

## Evidence
1. NuGet search: No package named `Aspose.Epub` exists on nuget.org
   - Restore probe gives NU1101: Unable to find package Aspose.Epub
2. Aspose.HTML: Supports EPUB reading and writing as an HTML-adjacent format
   - Namespace: Aspose.Html (not LowCode)
3. Aspose.Words: Supports EPUB export via SaveFormat.Epub
   - Namespace: Aspose.Words.LowCode (IS LowCode — covered by words family)
4. products.aspose.com: No standalone Aspose.EPUB product listed

## Decision
epub = FORMAT_CAPABILITY_OF_OTHER_PRODUCT

epub as a document FORMAT is supported by:
- Aspose.Words (LowCode API — covered in words family)
- Aspose.HTML (no LowCode namespace)

There is no standalone Aspose.EPUB SDK. epub cannot be an independent example
generation family. However, it remains in the user-required-26 list with this
explicit classification.

## Classification
- NuGet status: NO_STANDALONE_PACKAGE
- Format support: CAPABILITY_OF_WORDS_AND_HTML
- LowCode coverage: COVERED_BY_WORDS_FAMILY (Aspose.Words.LowCode)
- Universe classification: FORMAT_CAPABILITY_OF_OTHER_PRODUCT
- Example generation: NOT_APPLICABLE (no standalone package)
