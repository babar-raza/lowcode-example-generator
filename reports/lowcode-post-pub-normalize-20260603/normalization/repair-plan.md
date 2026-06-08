# Extra-Folder Removal Repair Plan

## PR 1: Diagram repo — remove 2 legacy duplicate folders
- Repo: aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples
- Branch: `fix/remove-legacy-duplicate-examples`
- Remove: `examples/diagram/lowcode/diagram-diagram-converter/` (all files)
- Remove: `examples/diagram/lowcode/diagram-pdf-converter/` (all files)
- After merge: 2 folders remain (diagram-converter, pdf-converter)

## PR 2: PDF repo — remove 1 legacy duplicate folder
- Repo: aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples
- Branch: `fix/remove-legacy-pdf-aconverter`
- Remove: `examples/pdf/lowcode/pdf-aconverter/` (all files)
- After merge: 20 folders remain (matching intended denominator)

## Post-merge
- Delete feature branches
- Re-clone and verify folder counts
- Rerun E2E for affected families
