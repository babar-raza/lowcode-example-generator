# Family Manual Analysis: finance

## Date: 2026-06-04
## Evidence: GitHub repo aspose-finance/Aspose.Finance-for-.NET, code: ConvertXbrlToIXbrl.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. XbrlDocument class.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `XbrlDocument` — loads and represents XBRL financial documents
- `SaveOptions` — output save options
- `InlineXbrlDocument` — iXBRL document type

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. `XbrlDocument.Save(outPath, saveOptions)`.
## 7. Document Object Model Workflow? Yes. XbrlDocument has XbrlInstances, schemas, context.
## 8. Recognition/Extraction APIs? Yes. XbrlDocument parsing exposes financial data nodes.
## 9. Rendering/Export APIs? No.

## 10. Fixtures Needed?
Yes. Both plugins need input XBRL (.xbrl or .xml) files.

## 11. License-Sensitive?
Trial limitations.

## 12. Official Snippets?
- `ConvertXbrlToIXbrl.cs` — `XbrlDocument doc = new XbrlDocument(srcFile)` + `doc.Save(outFile, new SaveOptions(...))`

## 13. Classes/Methods?
- `XbrlDocument document = new XbrlDocument(sourceDir + "xbrlFile.xbrl");`
- `SaveOptions saveOptions = new SaveOptions();`
- `saveOptions.SaveFormat = SaveFormat.IXBRL;`
- `document.Save(outDir + "output.html", saveOptions);`

## 14. Plugins Sharing API Pattern?
convert-xbrl: XbrlDocument.Load + Save with format options
parse-xbrl: XbrlDocument.Load + navigate XbrlInstances for data extraction

## 15. Plugins Needing Unique Mapping?
parse-xbrl: Needs XbrlDocument DOM navigation (XbrlInstance.Facts, Contexts).

## 16. Plugins with No Code?
- parse-xbrl: No match fetched. NEEDS_MANUAL_MAPPING.

## 17. Can Be Transformed Next Sprint?
- convert-xbrl: YES (needs XBRL fixture file)
- parse-xbrl: NEEDS_MANUAL_MAPPING

## 18. Blockers?
XBRL fixture file needed. XBRL is domain-specific format.

## 19. Registry Strategy?
1 READY_FOR_TRANSFORMATION; 1 NEEDS_MANUAL_MAPPING.

## 20. First Transformation Candidates?
1. convert-xbrl

## Implementation Model
`LOAD_SAVE_OPTIONS` — XbrlDocument.Load() + Save(options).
parse-xbrl: `DOCUMENT_OBJECT_MODEL_WORKFLOW`.
