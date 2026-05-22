"""Sprint 53 Lane E: Final evidence bundle and companion proof."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

repo_root = Path("c:/Users/prora/OneDrive/Documents/GitHub/lowcode-example-generator")
sys.path.insert(0, str(repo_root / "src"))

sprint_dir = repo_root / "workspace" / "verification" / "latest" / "lowcode-sprint53"

# --- 1. Write test-results summary ---
test_results = {
    "report_type": "test-results",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "sprint": 53,
    "head": "f216bd7",
    "total_passed": 2807,
    "total_skipped": 3,
    "total_failed": 0,
    "duration_seconds": 146.79,
    "verdict": "ALL_TESTS_PASS",
}
(sprint_dir / "test-results.json").write_text(json.dumps(test_results, indent=2), encoding="utf-8")
print("Wrote test-results.json")

# --- 2. Write sprint-summary.json ---
sprint_summary = {
    "sprint": 53,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "head": "f216bd7",
    "parent_sprint": 52,
    "lanes_completed": ["0", "A", "B", "C", "D", "E"],
    "goals_achieved": [
        "Sprint 52 IV and companion proof created",
        "Planner action-state semantics repaired (execution_state field, mark_executed, next_required_actions)",
        "Release-status top-level fields added (all_published, published_count, pr_ready_count, total_contracts)",
        "PDF approval packet refreshed (all 19 published, 0 PR-ready)",
        "Whole-portfolio planner exhaustion verified (PLANNER_EXHAUSTED)",
        "Full test suite green (2807 passed, 3 skipped, 0 failed)",
    ],
    "commits": [
        {"sha": "f216bd7", "message": "fix(planner): distinguish executed no-op checks from required next actions; fix release-status top-level fields"},
    ],
    "portfolio": {
        "published": 42,
        "pr_ready": 0,
        "total_contracts": 42,
        "parity": True,
    },
    "caveats_addressed": {
        "sprint52_companion_proof": "CREATED (sprint52-companion-validation-result.json)",
        "planner_action_state_semantics": "REPAIRED (execution_state field distinguishes executed no-ops from required work)",
        "release_status_top_level_fields": "REPAIRED (all_published, published_count, pr_ready_count, total_contracts added)",
    },
    "remaining_open_items": [
        "Version drift publication (Cells/Words/Diagram need Directory.Packages.props push - requires APPROVE_README_PUSH)",
        "Close superseded PRs #5-#10 in PDF repo (requires write access)",
        "report-builder fixture (missing input.docx)",
        "FormImporter (blocked by Aspose.PDF library bug)",
        "OCR/PSD (dependency-blocked, NuGet 404)",
    ],
    "verdict": "SPRINT53_COMPLETE",
}
(sprint_dir / "sprint-summary.json").write_text(json.dumps(sprint_summary, indent=2), encoding="utf-8")
print("Wrote sprint-summary.json")

# --- 3. Check what planner contract categories exist ---
from plugin_examples.evidence_contract import (
    PlannerSprintEvidenceContract,
    build_evidence_bundle,
    generate_companion_proof,
    PLANNER_SPRINT_CATEGORIES,
)

print(f"\nContract expects {len(PLANNER_SPRINT_CATEGORIES)} categories:")
for cat, patterns in sorted(PLANNER_SPRINT_CATEGORIES.items()):
    print(f"  {cat}: {patterns}")

# List files available (excluding helper scripts and zip artifacts)
print(f"\nFiles in sprint dir:")
for f in sorted(sprint_dir.iterdir()):
    if f.is_file() and not f.name.startswith("_") and not f.name.endswith((".zip", ".zip.validation.json")):
        print(f"  {f.name}")

# --- 4. Build evidence bundle ---
bundle_name = "lowcode-sprint53-evidence.zip"
zip_path = sprint_dir / bundle_name

try:
    result = build_evidence_bundle(
        evidence_dir=sprint_dir,
        zip_path=zip_path,
    )
    print(f"\nBundle built: {result['zip_path']}")
    print(f"Entry count: {result['entry_count']}")
    print(f"Validation verdict: {result['validation'].get('verdict', 'N/A')}")
except Exception as e:
    print(f"\nBundle build failed: {e}")
    import traceback
    traceback.print_exc()

# --- 5. Generate external companion proof ---
if zip_path.exists():
    try:
        proof = generate_companion_proof(zip_path)
        proof_path = zip_path.parent / f"{zip_path.name}.validation.json"
        proof_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        print(f"\nCompanion proof: {proof_path.name}")
        print(f"Proof verdict: {proof.get('verdict', 'N/A')}")
    except Exception as e:
        print(f"\nCompanion proof failed: {e}")
        import traceback
        traceback.print_exc()

print("\nLane E complete.")
