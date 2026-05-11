"""
Patch completion queue to add 21 PDF deferred WORKFLOW_ROOT entries
and 5 Words deferred scenario entries (Phase H / R6.5).

All new entries use BACKLOGGED state (valid per queue state machine).
Run: .venv/Scripts/python.exe scripts/patch_completion_queue.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = REPO_ROOT / "workspace" / "queues" / "example-completion-queue.json"


def make_pdf_deferred(type_name: str, blocking_reason: str, blocking_taskcard: str) -> dict:
    scenario_id = "pdf-" + type_name.lower().replace("converter", "-converter").replace("extractor", "-extractor").replace("editor", "-editor").replace("exporter", "-exporter").replace("flattener", "-flattener").replace("importer", "-importer").replace("generator", "-generator").lstrip("-")
    # Simplify: just lowercase the type name with hyphens
    scenario_id = "pdf-" + "".join(
        "-" + c.lower() if c.isupper() and i > 0 else c.lower()
        for i, c in enumerate(type_name)
    )
    return {
        "scenario_id": scenario_id,
        "family": "pdf",
        "type_name": type_name,
        "state": "BACKLOGGED",
        "blocking_reason": blocking_reason,
        "blocking_taskcard": blocking_taskcard,
        "contract_path": None,
        "lifecycle_record_path": "workspace/verification/latest/families/pdf/example-lifecycle-records.json",
        "pr_number": None,
        "merge_sha": None,
        "last_state_change": "2026-05-09T00:00:00Z",
        "post_merge_validation": None,
        "notes": f"WORKFLOW_ROOT type deferred from pilot scope. Classification source: pdf-type-role-classification.json. Pilot scope covers only Merger, Splitter, Optimizer, TextExtractor.",
    }


def make_words_deferred(scenario_id: str, type_name: str, blocking_reason: str, blocking_taskcard: str, notes: str) -> dict:
    return {
        "scenario_id": scenario_id,
        "family": "words",
        "type_name": type_name,
        "state": "BACKLOGGED",
        "blocking_reason": blocking_reason,
        "blocking_taskcard": blocking_taskcard,
        "contract_path": None,
        "lifecycle_record_path": "workspace/verification/latest/families/words/example-lifecycle-records.json",
        "pr_number": None,
        "merge_sha": None,
        "last_state_change": "2026-05-09T00:00:00Z",
        "post_merge_validation": None,
        "notes": notes,
    }


# 21 PDF deferred WORKFLOW_ROOT types (from pdf-type-role-classification.json pilot_deferred list)
PDF_DEFERRED = [
    ("DocConverter", "PILOT_SCOPE_DEFERRED: format-specific DOC output validation not yet implemented", "followup-pdf-remaining-candidate-classification"),
    ("FormEditor", "PILOT_SCOPE_DEFERRED: requires PDF with pre-existing form fields fixture", "followup-pdf-remaining-candidate-classification"),
    ("FormExporter", "PILOT_SCOPE_DEFERRED: requires form-fields PDF fixture + output format specification", "followup-pdf-remaining-candidate-classification"),
    ("FormFlattener", "PILOT_SCOPE_DEFERRED: requires PDF with form fields fixture", "followup-pdf-remaining-candidate-classification"),
    ("FormImporter", "PILOT_SCOPE_DEFERRED: requires pair input (PDF + data source) fixture strategy", "followup-pdf-remaining-candidate-classification"),
    ("Html", "PILOT_SCOPE_DEFERRED: HTML input fixture strategy differs from PDF input strategy", "followup-pdf-remaining-candidate-classification"),
    ("ImageExtractor", "PILOT_SCOPE_DEFERRED: output validation for extracted images not yet defined", "followup-pdf-remaining-candidate-classification"),
    ("Jpeg", "PILOT_SCOPE_DEFERRED: JPEG output format-specific validation not yet implemented", "followup-pdf-remaining-candidate-classification"),
    ("Ofd", "PILOT_SCOPE_DEFERRED: OFD format fixture not available", "followup-pdf-remaining-candidate-classification"),
    ("PdfAConverter", "PILOT_SCOPE_DEFERRED: PDF/A compliance validation not yet implemented", "followup-pdf-remaining-candidate-classification"),
    ("PdfExtractor", "PILOT_SCOPE_DEFERRED: output validation for extracted content not yet defined", "followup-pdf-remaining-candidate-classification"),
    ("PdfToImage", "PILOT_SCOPE_DEFERRED: image output validation strategy not yet defined", "followup-pdf-remaining-candidate-classification"),
    ("Png", "PILOT_SCOPE_DEFERRED: PNG output format-specific validation not yet implemented", "followup-pdf-remaining-candidate-classification"),
    ("Security", "PILOT_SCOPE_DEFERRED: encrypted PDF fixture and password management not yet implemented", "followup-pdf-remaining-candidate-classification"),
    ("SelectField", "PILOT_SCOPE_DEFERRED: requires PDF with select form fields fixture", "followup-pdf-remaining-candidate-classification"),
    ("Signature", "PILOT_SCOPE_DEFERRED: requires digitally signed PDF fixture", "followup-pdf-remaining-candidate-classification"),
    ("TableGenerator", "PILOT_SCOPE_DEFERRED: table structure fixture and output validation not yet defined", "followup-pdf-remaining-candidate-classification"),
    ("Tiff", "PILOT_SCOPE_DEFERRED: TIFF output format-specific validation not yet implemented", "followup-pdf-remaining-candidate-classification"),
    ("Timestamp", "PILOT_SCOPE_DEFERRED: timestamp authority fixture not yet implemented", "followup-pdf-remaining-candidate-classification"),
    ("TocGenerator", "PILOT_SCOPE_DEFERRED: TOC generation output validation not yet defined", "followup-pdf-remaining-candidate-classification"),
    ("XlsConverter", "PILOT_SCOPE_DEFERRED: XLS output validation not yet implemented", "followup-pdf-remaining-candidate-classification"),
]

# 5 Words deferred scenarios
WORDS_DEFERRED = [
    (
        "words-comparer",
        "Comparer",
        "MISSING_PAIR_FIXTURE: Comparer requires 2 input documents; no paired fixture strategy implemented",
        "followup-words-pair-fixture-strategy",
        "Requires 2-file input strategy. Backlog entry: backlog/words/excluded-scenarios.json",
    ),
    (
        "words-merger",
        "Merger",
        "MISSING_PAIR_FIXTURE: Merger requires 2 input documents; no paired fixture strategy implemented",
        "followup-words-pair-fixture-strategy",
        "Requires 2-file input strategy. Backlog entry: backlog/words/excluded-scenarios.json",
    ),
    (
        "words-mail-merger",
        "MailMerger",
        "MISSING_TEMPLATE_FIXTURE: MailMerger requires template DOCX with merge fields; no template fixture strategy implemented",
        "followup-words-mail-merger-fixture-documentation",
        "Requires template DOCX with named merge fields. Backlog entry: backlog/words/excluded-scenarios.json",
    ),
    (
        "words-splitter-split",
        "SplitCriteria",
        "MISSING_ENUM_STRATEGY: SplitCriteria enum values not discoverable from DllReflector catalog",
        "followup-words-split-criteria-enumeration",
        "SplitCriteria is a parameter enum for Splitter.Split(). Needs enum value discovery in scenario planner. Backlog entry: backlog/words/excluded-scenarios.json",
    ),
    (
        "words-report-builder",
        "ReportBuilder",
        "CLASSIFICATION_GAP: ReportBuilder classification as standalone WORKFLOW_ROOT type not confirmed; requires template data-source fixture",
        "followup-words-full-coverage-expansion",
        "Pilot scope restricted to 4 approved types. ReportBuilder deferred to expansion sprint. Backlog entry: backlog/words/excluded-scenarios.json",
    ),
]


def main():
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    existing_ids = {e["scenario_id"] for e in queue["entries"]}

    new_entries = []

    for type_name, blocking_reason, blocking_taskcard in PDF_DEFERRED:
        entry = make_pdf_deferred(type_name, blocking_reason, blocking_taskcard)
        if entry["scenario_id"] in existing_ids:
            print(f"  SKIP (already exists): {entry['scenario_id']}")
            continue
        new_entries.append(entry)

    for scenario_id, type_name, blocking_reason, blocking_taskcard, notes in WORDS_DEFERRED:
        if scenario_id in existing_ids:
            print(f"  SKIP (already exists): {scenario_id}")
            continue
        entry = make_words_deferred(scenario_id, type_name, blocking_reason, blocking_taskcard, notes)
        new_entries.append(entry)

    if not new_entries:
        print("No new entries to add.")
        return

    queue["entries"].extend(new_entries)
    queue["total_entries"] = len(queue["entries"])

    # Recompute state summary
    state_counts: dict[str, int] = {}
    for e in queue["entries"]:
        state_counts[e["state"]] = state_counts.get(e["state"], 0) + 1
    queue["state_summary"] = state_counts

    QUEUE_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Added {len(new_entries)} entries. Total: {queue['total_entries']}")
    for e in new_entries:
        print(f"  + {e['scenario_id']} ({e['family']}) [{e['state']}]")


if __name__ == "__main__":
    main()
