# Skill: Non-LowCode Family Manual Analysis

## Purpose
Analyze a non-LowCode Aspose family to determine its implementation model, API patterns, and transformation readiness.

## Inputs
- family_slug
- GitHub repo (fetched tree + sample files)
- products.aspose.net page inventory for this family
- Fetched code files from code harvest
- Prior reflection data (if available)

## Outputs
- reports/.../manual-analysis/family/{family}.md
- Updated manual-family-summary-matrix.json with this family's entry

## Prerequisites
- Code harvest completed for family (or explicitly blocked)
- Plugin page inventory for family exists

## Step-by-Step Method

1. Read 2-3 representative code files from .local/code-cache/{family}/
2. Identify API entry points: what class/method is the main starting point?
3. Determine implementation model (choose one):
   - LOAD_SAVE_OPTIONS: universal Image.Load()/Save() or Document(path)/Save() pattern
   - STATIC_CONVERTER_CLASS: Converter.ConvertX(doc, options, path) static method
   - DEDICATED_PLUGIN_CLASS: dedicated Plugins namespace class with Process()
   - RECOGNITION_EXTRACTION_API: recognize/read API returning data objects
   - RENDERING_API: Bitmap/Graphics rendering surface
   - DOCUMENT_OBJECT_MODEL_WORKFLOW: DOM traversal to extract/modify content
   - FIXTURE_HEAVY_WORKFLOW: requires complex template + scanned input
   - LICENSE_GATED_WORKFLOW: trial mode blocks all meaningful operations
4. Answer all 20 questions in the family analysis template
5. For each plugin, determine:
   - Transformation-ready? (page URL + code + pattern known)
   - Needs fixture? (what type of file is needed)
   - Blocked? (why)
6. Write recommendations: first transformation candidates
7. Update manual-family-summary-matrix.json

## Family Analysis Template (20 Questions)
1. LowCode namespace?
2. Plugins namespace?
3. Regular product APIs?
4. Dedicated plugin-like classes?
5. Static converter classes?
6. Load/Save with format options?
7. Document object model workflow?
8. Recognition/extraction APIs?
9. Rendering/export APIs?
10. Fixtures needed?
11. License-sensitive behavior?
12. Official snippets available?
13. Classes/methods in official snippets?
14. Plugins sharing same API pattern?
15. Plugins needing unique mapping?
16. Plugins with no code?
17. Which can be transformed next sprint?
18. Which are blocked and why?
19. Recommended registry strategy?
20. First transformation candidates?

## Checks
- [ ] All 20 questions answered
- [ ] Implementation model assigned
- [ ] Evidence paths cited (code files, GitHub URLs)
- [ ] First transformation candidates named
- [ ] Blockers classified with blocker codes

## Failure Modes
- No code at all: Assign UNKNOWN_NEEDS_MANUAL_REVIEW; note in blocker ledger
- Code is unclear: Check GitHub repo README; look for docs.aspose.com examples
- Multiple patterns exist: Choose primary + note secondary in analysis

## Evidence Requirements
- manual-analysis/family/{family}.md with all 20 questions answered
- Evidence citations: code file paths and/or GitHub URLs

## Example Output
See: reports/lowcode-plugin-code-registry-20260604/manual-analysis/family/barcode.md

## Stop Rules
- Do not assign implementation model without reading at least 1 code file or docs example
- Do not claim READY_FOR_TRANSFORMATION in analysis if code evidence is missing

## Continue Rules
- NEEDS_MANUAL_MAPPING is a valid analysis outcome
- Document what code would be needed even when none was found
