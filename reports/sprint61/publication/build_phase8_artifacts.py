"""Build Phase 8 artifacts: correction package ledger + publication blockers."""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SPRINT61_DIR = Path(__file__).parent.parent

# I/O correction plan from Phase 4
README_CORRECTIONS_PATH = SPRINT61_DIR / "readme" / "readme-io-correction-plan.json"

# Scenarios with no local package (deferred/blocked)
DEFERRED_SCENARIOS = {
    "pdf-pdf-aconverter": "No local package — deferred to next sprint",
    "pdf-text-extractor": "Output is stdout (no output file) — manual README needed",
}

# Scenarios with INPUT_DOC_MISSING after correction
INPUT_MISSING_AFTER = {
    "words-mail-merger":  "Input uses data source (no input.EXT literal in Program.cs)",
    "words-report-builder": "Input uses data source + template (no input.EXT literal)",
}

# All 42 scenario IDs
ALL_SCENARIO_IDS = [
    "cells-html-converter", "cells-image-converter", "cells-json-converter",
    "cells-pdf-converter", "cells-spreadsheet-converter", "cells-spreadsheet-locker",
    "cells-spreadsheet-merger", "cells-spreadsheet-splitter", "cells-text-converter",
    "words-comparer", "words-converter", "words-mail-merger", "words-merger",
    "words-replacer", "words-report-builder", "words-splitter", "words-watermarker",
    "pdf-doc-converter", "pdf-form-editor", "pdf-form-exporter", "pdf-form-flattener",
    "pdf-html", "pdf-image-extractor", "pdf-jpeg", "pdf-merger", "pdf-optimizer",
    "pdf-pdf-aconverter", "pdf-png", "pdf-security", "pdf-signature", "pdf-splitter",
    "pdf-table-generator", "pdf-text-extractor", "pdf-tiff", "pdf-toc-generator",
    "pdf-xls-converter",
    "diagram-diagram-converter", "diagram-pdf-converter",
    "email-converter",
    "slides-compress", "slides-convert", "slides-merger",
]

FAMILY_FOR = {sid: sid.split("-")[0] for sid in ALL_SCENARIO_IDS}

# Current publication state (from MEMORY.md + Sprint 55 evidence)
PUBLICATION_STATE = {
    "cells":   {"status": "PUBLISHED_CURRENT",       "version": "26.5.1", "pr_merged": True},
    "words":   {"status": "PUBLISHED_VERSION_DRIFT", "version": "26.4.0", "pr_merged": True},
    "pdf":     {"status": "PUBLISHED_CURRENT",       "version": "26.5.0", "pr_merged": True},
    "diagram": {"status": "PUBLISHED_VERSION_DRIFT", "version": "26.4.0", "pr_merged": True},
    "email":   {"status": "PUBLISHED_CURRENT",       "version": "26.4.0", "pr_merged": True},
    "slides":  {"status": "PUBLISHED_CURRENT",       "version": "26.5.0", "pr_merged": True},
}


def build_ledger():
    # Load corrections from Phase 4
    corrections_by_sid = {}
    if README_CORRECTIONS_PATH.exists():
        plan = json.loads(README_CORRECTIONS_PATH.read_text(encoding="utf-8"))
        for c in plan.get("corrections", []):
            corrections_by_sid[c["scenario_id"]] = c

    ledger_entries = []
    for sid in ALL_SCENARIO_IDS:
        family = FAMILY_FOR[sid]
        pub = PUBLICATION_STATE.get(family, {})
        correction = corrections_by_sid.get(sid)

        # Determine what corrections are needed
        readme_correction_needed = correction is not None
        programcs_io_known = sid not in DEFERRED_SCENARIOS and sid not in INPUT_MISSING_AFTER
        manual_classification_needed = sid in INPUT_MISSING_AFTER or sid in DEFERRED_SCENARIOS

        # Determine blockers for this scenario's correction push
        blockers = []
        if pub.get("status") == "PUBLISHED_VERSION_DRIFT":
            blockers.append(f"version_drift: family {family} is at {pub['version']} (not latest NuGet)")
        if sid in DEFERRED_SCENARIOS:
            blockers.append(f"no_local_package: {DEFERRED_SCENARIOS[sid]}")
        if sid in INPUT_MISSING_AFTER:
            blockers.append(f"input_format_unknown: {INPUT_MISSING_AFTER[sid]}")
        if readme_correction_needed:
            blockers.append("readme_update_required: I/O section must be added")
            blockers.append("requires_APPROVE_README_PUSH: live push needs approval gate")

        entry = {
            "scenario_id": sid,
            "family": family,
            "publication_status": pub.get("status"),
            "published_version": pub.get("version"),
            "readme_io_correction_needed": readme_correction_needed,
            "readme_correction_text": correction.get("correction_text_to_add") if correction else None,
            "programcs_io_known": programcs_io_known,
            "manual_classification_needed": manual_classification_needed,
            "correction_blockers": blockers,
            "correction_ready_to_push": readme_correction_needed and not manual_classification_needed and len(blockers) <= 2,
        }
        ledger_entries.append(entry)

    return ledger_entries


def build_publication_blockers(ledger_entries):
    blockers = {
        "readme_io_push_required": [],
        "manual_classification_required": [],
        "version_drift_families": [],
        "no_local_package": [],
    }

    version_drift_families = set()
    for e in ledger_entries:
        if e["readme_io_correction_needed"]:
            blockers["readme_io_push_required"].append(e["scenario_id"])
        if e["manual_classification_needed"]:
            blockers["manual_classification_required"].append(e["scenario_id"])
        for b in e["correction_blockers"]:
            if "version_drift" in b:
                version_drift_families.add(e["family"])
            if "no_local_package" in b:
                blockers["no_local_package"].append(e["scenario_id"])

    blockers["version_drift_families"] = sorted(version_drift_families)
    return blockers


if __name__ == "__main__":
    out_dir = Path(__file__).parent

    ledger_entries = build_ledger()
    ready_count = sum(1 for e in ledger_entries if e["correction_ready_to_push"])
    blocked_count = sum(1 for e in ledger_entries if e["correction_blockers"])

    ledger = {
        "sprint": "sprint61",
        "audit_type": "correction_package_ledger",
        "total": len(ledger_entries),
        "readme_corrections_needed": sum(1 for e in ledger_entries if e["readme_io_correction_needed"]),
        "ready_to_push": ready_count,
        "blocked": blocked_count,
        "entries": ledger_entries,
    }
    (out_dir / "correction-package-ledger.json").write_text(
        json.dumps(ledger, indent=2), encoding="utf-8"
    )
    print(f"Written: correction-package-ledger.json")
    print(f"  Total: {len(ledger_entries)}, corrections_needed: {ledger['readme_corrections_needed']}")
    print(f"  ready_to_push: {ready_count}, blocked: {blocked_count}")

    pub_blockers = build_publication_blockers(ledger_entries)
    blockers_doc = {
        "sprint": "sprint61",
        "audit_type": "live_publication_blockers",
        "total_scenarios_needing_readme_io_push": len(pub_blockers["readme_io_push_required"]),
        "manual_classification_required": pub_blockers["manual_classification_required"],
        "version_drift_families": pub_blockers["version_drift_families"],
        "no_local_package": pub_blockers["no_local_package"],
        "required_approval": "PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH",
        "deferred_to": "sprint62",
        "reason": (
            "Adding I/O format documentation to published READMEs is a publication operation. "
            "Sprint 61 delivers audit evidence and correction plan only. "
            "Actual README push is deferred to Sprint 62 per readme-io-documentation-policy.md."
        ),
        "scenarios_needing_push": pub_blockers["readme_io_push_required"],
    }
    (out_dir / "live-publication-blockers.json").write_text(
        json.dumps(blockers_doc, indent=2), encoding="utf-8"
    )
    print(f"\nWritten: live-publication-blockers.json")
    print(f"  readme_io_push_needed: {len(pub_blockers['readme_io_push_required'])} scenarios")
    print(f"  manual_classification: {pub_blockers['manual_classification_required']}")
    print(f"  version_drift_families: {pub_blockers['version_drift_families']}")
    print(f"  no_local_package: {pub_blockers['no_local_package']}")

    # README update package summary
    summary = {
        "sprint": "sprint61",
        "audit_type": "readme_update_package_summary",
        "total_examples": 42,
        "io_doc_match_before": 0,
        "io_doc_match_after_correction": 38,
        "input_doc_missing_after": 3,
        "both_doc_missing_after": 1,
        "correction_plan_file": "../readme/readme-io-correction-plan.json",
        "corrections_with_known_io": sum(1 for e in ledger_entries if e["readme_io_correction_needed"]),
        "publication_gate": "PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH",
        "status": "AUDIT_COMPLETE_PUSH_DEFERRED_TO_SPRINT62",
        "families_covered": sorted(set(e["family"] for e in ledger_entries)),
    }
    (out_dir / "readme-update-package-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"\nWritten: readme-update-package-summary.json")
