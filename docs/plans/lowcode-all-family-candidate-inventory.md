# LowCode Example Generator: All-Family Candidate Inventory

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** INVENTORY_COMPLETE_DISCOVERY_PENDING

---

## Group A: LOWCODE_CONFIRMED_RUNNABLE (Active Production)

### A1. cells
- **Package ID:** Aspose.Cells
- **Config:** `pipeline/configs/families/cells.yml` (active)
- **Namespace:** Aspose.Cells.LowCode (VERIFIED)
- **Total types:** 22 | **Workflow roots:** 9 | **Non-runnable:** 13
- **Denominator basis:** FULL_SOT
- **Published:** 9/9 POST_MERGE_VERIFIED
- **Coverage:** 100% of FULL_SOT
- **Evidence:** `pipeline/configs/denominators/cells.json`, `workspace/verification/latest/families/cells/`
- **Confidence:** HIGH
- **Roadmap phase:** R7 (reconciliation only)

### A2. words
- **Package ID:** Aspose.Words
- **Config:** `pipeline/configs/families/words.yml` (active)
- **Namespace:** Aspose.Words.LowCode (VERIFIED)
- **Total types:** 25 | **Workflow roots:** NULL (unclassified) | **Pilot allowed:** 4
- **Denominator basis:** PILOT_ALLOWED
- **Published:** 4/4 pilot POST_MERGE_VERIFIED | **Deferred:** 21
- **Coverage:** 100% of pilot, ~16% of total
- **Evidence:** `pipeline/configs/denominators/words.json`, `workspace/verification/latest/families/words/`
- **Confidence:** HIGH (pilot), LOW (full classification)
- **Open taskcards:** 5 expansion + NEW-07 (workflow_root classification)
- **Roadmap phase:** R7 (reconciliation), R9 (expansion)

### A3. pdf
- **Package ID:** Aspose.PDF
- **Config:** `pipeline/configs/families/pdf.yml` (active)
- **Namespace:** Aspose.Pdf.LowCode (VERIFIED)
- **Total types:** 101 | **Workflow roots:** 25 | **Non-runnable:** 76 | **Pilot allowed:** 4
- **Denominator basis:** PILOT_ALLOWED
- **Published:** 2/4 pilot | **PR-ready:** 1 (Splitter) | **Reviewed:** 1 (Optimizer, needs 2nd PASS)
- **Coverage:** 50% of pilot, 8% of workflow roots, 2% of total
- **Evidence:** `workspace/verification/latest/pdf-pr1-merge-result.json`, `workspace/verification/latest/pdf-pr3-package-validation.json`
- **Confidence:** HIGH (PR#1), MEDIUM (PR#3/PR#4 pending)
- **Open taskcards:** followup-pdf-pr3-review-and-merge, followup-pdf-remaining-candidate-classification
- **Roadmap phase:** R8 (PR#3/PR#4), R10 (expansion)

---

## Group B: DISCOVERY_BLOCKED (Config exists, discovery not running)

### B1. email
- **Package ID:** Aspose.Email
- **Config:** `pipeline/configs/families/disabled/email.yml` (enabled=true, in disabled/ dir)
- **Namespace:** Aspose.Email.LowCode (CLAIMED, not reflection-proven)
- **Blocker 1:** Config not in active scan path (`discovery_sweep.py` scans root `*.yml` only)
- **Blocker 2:** LowCode namespace existence unproven
- **Contradiction:** `enabled: true` but in `disabled/` directory
- **Prior run:** 2 template-mode examples 2026-04-29 (not production artifacts)
- **Denominator:** NONE
- **Confidence:** LOW
- **Taskcard:** NEW-02 (followup-email-blocker-investigation)
- **Roadmap phase:** R2

### B2. slides
- **Package ID:** Aspose.Slides.NET
- **Config:** `pipeline/configs/families/disabled/slides.yml` (enabled=true, in disabled/ dir)
- **Namespace:** Aspose.Slides.LowCode (CLAIMED, not reflection-proven)
- **Blocker 1:** Config not in active scan path
- **Blocker 2:** DLL name mismatch — package is `Aspose.Slides.NET` but DLL is `Aspose.Slides.dll`
- **Prior run:** FAIL_PACKAGE_UNSUPPORTED_TFM 2026-04-29
- **Denominator:** NONE
- **Confidence:** MEDIUM (failure well-documented)
- **Taskcard:** NEW-03 (followup-slides-dll-name-fix)
- **Roadmap phase:** R2

---

## Group C: DISCOVERY_NOT_ATTEMPTED (No YAML config)

All entries below require YAML creation (R1) before discovery can run.
NuGet package IDs must be verified before creating configs.

| Family Key | Likely Package ID | Namespace Pattern | Priority | Notes |
|-----------|-------------------|-------------------|----------|-------|
| imaging | Aspose.Imaging | Aspose.Imaging.LowCode? | MEDIUM | Image processing/conversion |
| barcode | Aspose.BarCode | Aspose.BarCode.LowCode? | MEDIUM | Barcode generation/recognition |
| diagram | Aspose.Diagram | Aspose.Diagram.LowCode? | MEDIUM | Visio/diagram operations |
| cad | Aspose.CAD | Aspose.CAD.LowCode? | MEDIUM | CAD file processing |
| ocr | Aspose.OCR | Aspose.OCR.LowCode? | LOW | OCR operations |
| omr | Aspose.OMR | Aspose.OMR.LowCode? | LOW | Optical mark recognition |
| tasks | Aspose.Tasks | Aspose.Tasks.LowCode? | LOW | Project file processing |
| note | Aspose.Note | Aspose.Note.LowCode? | LOW | OneNote processing |
| zip | Aspose.ZIP | Aspose.ZIP.LowCode? | LOW | Archive operations |
| page | Aspose.Page | Aspose.Page.LowCode? | LOW | XPS/PostScript processing |
| psd | Aspose.PSD | Aspose.PSD.LowCode? | LOW | Photoshop file processing |
| html | Aspose.HTML | Aspose.HTML.LowCode? | LOW | HTML document processing |
| gis | Aspose.GIS | Aspose.GIS.LowCode? | LOW | GIS/geospatial operations |
| finance | Aspose.Finance | Aspose.Finance.LowCode? | LOW | Financial file formats |
| threed | Aspose.3D | Aspose.3D.LowCode? | LOW | 3D model processing |
| tex | Aspose.TeX | Aspose.TeX.LowCode? | LOW | LaTeX/TeX processing |
| font | Aspose.Font | Aspose.Font.LowCode? | LOW | Font file operations |
| drawing | Aspose.Drawing | Aspose.Drawing.LowCode? | LOW | Drawing/graphics operations |
| svg | Aspose.SVG | Aspose.SVG.LowCode? | LOW | SVG file processing |
| epub | Aspose.Epub | Aspose.Epub.LowCode? | LOW | eBook/EPUB processing |

**Note:** Package IDs marked with "?" must be verified against NuGet.org before YAML creation. Some products may not have .NET SDK releases.

---

## Summary Statistics

| Group | Count | Description |
|-------|-------|-------------|
| A: LOWCODE_CONFIRMED_RUNNABLE | 3 | Active production families |
| B: DISCOVERY_BLOCKED | 2 | Config exists but blocked |
| C: DISCOVERY_NOT_ATTEMPTED | 20 | No YAML config |
| **Total candidates** | **25** | **All Aspose .NET product families** |

---

## Discovery Prerequisites Checklist

Before R3 (all-family discovery) can run:

- [ ] R1: NuGet package IDs verified for all Group C families
- [ ] R1: discovery_only YAML configs created for all verified Group C families
- [ ] R1: OUT_OF_SCOPE documentation created for any families without .NET SDK
- [ ] R2: Email blocker resolved (config moved or disabled)
- [ ] R2: Slides DLL name fix applied
- [ ] R2: Email and Slides configs moved to active scan path if unblocked
