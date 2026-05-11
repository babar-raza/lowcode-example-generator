"""Add taskcards NEW-19 through NEW-28 to open-taskcard-closure-matrix.json."""
import json
from pathlib import Path

matrix_path = Path("workspace/verification/latest/open-taskcard-closure-matrix.json")
with open(matrix_path, encoding="utf-8") as f:
    data = json.load(f)

new_taskcards = [
    {
        "id": "NEW-19-followup-email-controlled-pilot-planning",
        "title": "Plan and configure Email controlled pilot: fixture strategy, allowed_types, target repo",
        "status": "OPEN",
        "priority": "MEDIUM",
        "opened_in": "Post-Discovery Next Sprint Phase H",
        "opened_date": "2026-05-09",
        "evidence": "email.json denominator created; Converter=1 WORKFLOW_ROOT; namespace Aspose.Email.LowCode confirmed",
        "scope": "Define EML/MSG fixture strategy (programmatic via Aspose.Email API); set allowed_types=[Converter]; set controlled_pilot_approved=true in email.yml; provision target repo aspose-email-net/Aspose.Email.LowCode-for-.NET-Examples",
        "acceptance": "email.yml has status=active, controlled_pilot_approved=true; fixture_type=programmatic_email_message; target repo accessible via GITHUB_TOKEN; generation runs without config errors",
        "blocking": False,
        "roadmap_phase": "H",
        "category": "pilot_planning"
    },
    {
        "id": "NEW-20-followup-slides-controlled-pilot-planning",
        "title": "Plan and configure Slides controlled pilot: fixture strategy, allowed_types, target repo",
        "status": "OPEN",
        "priority": "MEDIUM",
        "opened_in": "Post-Discovery Next Sprint Phase H",
        "opened_date": "2026-05-09",
        "evidence": "slides.json denominator created; workflow_roots=[Compress, Convert, Merger]; XML docs missing (Aspose.Slides.xml found, not Aspose.Slides.NET.xml)",
        "scope": "Define PPTX fixture strategy (programmatic via Aspose.Slides API); set allowed_types=[Compress, Convert, Merger]; set controlled_pilot_approved=true; move slides.yml from disabled/ to active; provision target repo aspose-slides-net/Aspose.Slides.LowCode-for-.NET-Examples",
        "acceptance": "slides.yml in active path; controlled_pilot_approved=true; fixture_type=programmatic_pptx; target repo accessible; generation runs without config errors",
        "blocking": False,
        "roadmap_phase": "H",
        "category": "pilot_planning"
    },
    {
        "id": "NEW-21-followup-diagram-controlled-pilot-planning",
        "title": "Plan and configure Diagram controlled pilot: fixture strategy, allowed_types, target repo",
        "status": "OPEN",
        "priority": "MEDIUM",
        "opened_in": "Post-Discovery Next Sprint Phase H",
        "opened_date": "2026-05-09",
        "evidence": "diagram.json denominator created; workflow_roots=[DiagramConverter, PdfConverter]; 4 total methods across 2 WORKFLOW_ROOT types",
        "scope": "Define VSDX fixture strategy (programmatic via Aspose.Diagram API); set allowed_types=[DiagramConverter, PdfConverter]; set controlled_pilot_approved=true; provision target repo aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples",
        "acceptance": "diagram.yml exists with status=active; controlled_pilot_approved=true; fixture_type=programmatic_diagram; target repo accessible; generation runs without config errors",
        "blocking": False,
        "roadmap_phase": "H",
        "category": "pilot_planning"
    },
    {
        "id": "NEW-22-followup-epub-reflection-blocker-investigation",
        "title": "Investigate Aspose.Epub NuGet package availability and correct package ID",
        "status": "OPEN",
        "priority": "LOW",
        "opened_in": "Post-Discovery Next Sprint Phase D",
        "opened_date": "2026-05-09",
        "evidence": "epub-reflection-blocker.json: PACKAGE_DOWNLOAD_FAILED; run dir completely empty; Aspose.Epub not available via standard NuGet API lookup",
        "scope": "Research correct NuGet package ID for Aspose.Epub; if found: update epub.yml package_id; if not found: document as OUT_OF_SCOPE",
        "acceptance": "epub either has correct package_id with successful download, OR is documented as OUT_OF_SCOPE with evidence",
        "blocking": False,
        "roadmap_phase": "D_extension",
        "category": "discovery_blocker"
    },
    {
        "id": "NEW-23-followup-html-reflection-blocker-investigation",
        "title": "CLOSED: html confirmed CONFIRMED_NO_LOWCODE after manual DllReflector run",
        "status": "CLOSED_VERIFIED",
        "priority": "CLOSED",
        "opened_in": "Post-Discovery Next Sprint Phase D",
        "opened_date": "2026-05-09",
        "closed_in": "Post-Discovery Next Sprint Phase D (same sprint)",
        "closed_date": "2026-05-09",
        "evidence": "html-reflection-blocker.json: ran DllReflector with explicit dep; 49 namespaces found, none LowCode; html.yml updated to disabled=true, enabled=false",
        "scope": "N/A - closed immediately after investigation confirmed CONFIRMED_NO_LOWCODE",
        "acceptance": "html.yml status=disabled; html-reflection-blocker.json records CONFIRMED_NO_LOWCODE verdict",
        "blocking": False,
        "roadmap_phase": "D",
        "category": "discovery_blocker"
    },
    {
        "id": "NEW-24-followup-ocr-reflection-blocker-investigation",
        "title": "Fix OCR reflection blocker: Aspose.Drawing.Common missing transitive dep",
        "status": "OPEN",
        "priority": "LOW",
        "opened_in": "Post-Discovery Next Sprint Phase D",
        "opened_date": "2026-05-09",
        "evidence": "ocr-reflection-blocker.json: MISSING Aspose.Drawing.Common 26.3.0.0; max_depth=3 insufficient due to resolved-libs population gap in extractor.py",
        "scope": "Fix extractor.py resolved-libs to include ALL deps/ packages (not just dep_nupkg_paths); rerun OCR discovery",
        "acceptance": "OCR reflection completes without FileNotFoundException; LowCode namespace existence determined",
        "blocking": False,
        "roadmap_phase": "D_extension",
        "category": "discovery_blocker"
    },
    {
        "id": "NEW-25-followup-omr-reflection-blocker-investigation",
        "title": "Fix OMR reflection blocker: Newtonsoft.Json missing transitive dep",
        "status": "OPEN",
        "priority": "LOW",
        "opened_in": "Post-Discovery Next Sprint Phase D",
        "opened_date": "2026-05-09",
        "evidence": "omr-reflection-blocker.json: MISSING Newtonsoft.Json 13.0.0.0; same root cause as psd; resolved-libs population gap in extractor.py",
        "scope": "Fix extractor.py resolved-libs population (shared fix with OCR, PSD); rerun OMR discovery",
        "acceptance": "OMR reflection completes; LowCode namespace existence determined",
        "blocking": False,
        "roadmap_phase": "D_extension",
        "category": "discovery_blocker"
    },
    {
        "id": "NEW-26-followup-psd-reflection-blocker-investigation",
        "title": "Fix PSD reflection blocker: Newtonsoft.Json missing transitive dep",
        "status": "OPEN",
        "priority": "LOW",
        "opened_in": "Post-Discovery Next Sprint Phase D",
        "opened_date": "2026-05-09",
        "evidence": "psd-reflection-blocker.json: MISSING Newtonsoft.Json 13.0.0.0; same root cause as omr; resolved-libs population gap in extractor.py",
        "scope": "Fix extractor.py resolved-libs population (shared fix with OCR, OMR); rerun PSD discovery",
        "acceptance": "PSD reflection completes; LowCode namespace existence determined",
        "blocking": False,
        "roadmap_phase": "D_extension",
        "category": "discovery_blocker"
    },
    {
        "id": "NEW-27-followup-svg-reflection-blocker-investigation",
        "title": "CLOSED: svg confirmed CONFIRMED_NO_LOWCODE after manual DllReflector run",
        "status": "CLOSED_VERIFIED",
        "priority": "CLOSED",
        "opened_in": "Post-Discovery Next Sprint Phase D",
        "opened_date": "2026-05-09",
        "closed_in": "Post-Discovery Next Sprint Phase D (same sprint)",
        "closed_date": "2026-05-09",
        "evidence": "svg-reflection-blocker.json: ran DllReflector with explicit dep; 36 namespaces found, none LowCode; svg.yml updated to disabled=true, enabled=false",
        "scope": "N/A - closed immediately after investigation confirmed CONFIRMED_NO_LOWCODE",
        "acceptance": "svg.yml status=disabled; svg-reflection-blocker.json records CONFIRMED_NO_LOWCODE verdict",
        "blocking": False,
        "roadmap_phase": "D",
        "category": "discovery_blocker"
    },
    {
        "id": "NEW-28-followup-confirmed-no-lowcode-documentation",
        "title": "Create formal evidence registry for all 15 CONFIRMED_NO_LOWCODE families",
        "status": "OPEN",
        "priority": "MEDIUM",
        "opened_in": "Post-Discovery Next Sprint Phase I",
        "opened_date": "2026-05-09",
        "evidence": "15 families confirmed no LowCode: barcode, cad, drawing, finance, font, gis, imaging, note, page, tasks, tex, threed, zip + html + svg; YAMLs already disabled",
        "scope": "Create workspace/verification/latest/confirmed-no-lowcode-family-registry.json with per-family evidence",
        "acceptance": "confirmed-no-lowcode-family-registry.json exists; covers all 15 families; each entry has verification evidence; yaml_disabled=true for all",
        "blocking": False,
        "roadmap_phase": "I",
        "category": "documentation"
    }
]

# Check for duplicates
existing_ids = {t["id"] for t in data["taskcards"]}
added = 0
for tc in new_taskcards:
    if tc["id"] not in existing_ids:
        data["taskcards"].append(tc)
        added += 1
    else:
        print(f"  SKIP (already exists): {tc['id']}")

data["matrix_date"] = "2026-05-09"
data["sprint"] = "Post-Discovery Next Sprint (Phases A-H) — state board update"

with open(matrix_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

open_count = sum(1 for t in data["taskcards"] if t["status"] == "OPEN")
closed_count = sum(1 for t in data["taskcards"] if t["status"].startswith("CLOSED"))
print(f"Added {added} new taskcards")
print(f"Total: {len(data['taskcards'])}, OPEN: {open_count}, CLOSED: {closed_count}")
