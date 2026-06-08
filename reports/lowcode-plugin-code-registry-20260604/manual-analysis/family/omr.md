# Family Manual Analysis: omr

## Date: 2026-06-04
## Evidence: GitHub repo aspose-omr/Aspose.OMR-for-.NET
## Prior sprint: PROBE_BLOCKED_LICENSE (template required)

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. OmrEngine class.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `OmrEngine` — main OMR engine
- `TemplateProcessor` — processes OMR images against templates
- `GenerationResult` — result of template generation

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Template generation outputs .OMR template files.
## 7. Document Object Model Workflow? No.
## 8. Recognition/Extraction APIs? Yes. TemplateProcessor.RecognizeImage() processes scanned forms.
## 9. Rendering/Export APIs? Yes. Template generation renders to PNG/JPG.

## 10. Fixtures Needed?
FIXTURE_HEAVY:
- recognize-omr: Needs .OMR template file AND scanned form image
- generate-omr-template: Needs template definition text (.txt/.csv)

## 11. License-Sensitive?
YES — Trial restricts template processing. PROBE_BLOCKED_LICENSE in prior sprint.

## 12. Official Snippets?
None matched from GitHub repo (0/2 plugins matched).

## 13. Classes/Methods?
- `OmrEngine engine = new OmrEngine();`
- `GenerationResult result = engine.GenerateTemplate("template.txt");`
- `result.Save(outDir, "template");`
- `TemplateProcessor processor = engine.GetTemplateProcessor("template.omr");`
- `RecognitionResult result = processor.RecognizeImage("form.jpg");`
- `result.GetCsv()` — export recognized data

## 14. Plugins Sharing API Pattern?
generate-omr-template: OmrEngine.GenerateTemplate()
recognize-omr: TemplateProcessor.RecognizeImage()

## 15. Plugins Needing Unique Mapping?
Both need unique approaches. Neither matched from GitHub search.

## 16. Plugins with No Code?
Both: NO_CODE_FOUND from GitHub keyword search.

## 17. Can Be Transformed Next Sprint?
Both BLOCKED — LICENSE_GATED_WORKFLOW. Need licensed environment.

## 18. Blockers?
LICENSE_GATED_WORKFLOW — trial restricts all OMR operations.
FIXTURE_BLOCKED — template files and scanned form images required.

## 19. Registry Strategy?
Both BLOCKED_LICENSE.

## 20. First Transformation Candidates?
None — both blocked by license.

## Implementation Model
`FIXTURE_HEAVY_WORKFLOW` + `LICENSE_GATED_WORKFLOW`
