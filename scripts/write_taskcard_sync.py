"""Write taskcard sync report and master plan for MEGA-TRAIN-002."""
import json
import datetime
from pathlib import Path

RUN_DIR = Path("workspace/verification/lowcode-ai-autonomous-execution-mega-train-20260519-114122")
RUN_DIR.mkdir(parents=True, exist_ok=True)

taskcards = [
    {"id": "TC-MT2-01", "title": "Wire HealingIntelligenceLoader into runner.py", "lane": "B", "status": "CLOSED_VERIFIED", "evidence": "14/14 wiring tests pass"},
    {"id": "TC-MT2-02", "title": "Gate-triggered reviewer repair loop", "lane": "B", "status": "CLOSED_VERIFIED", "evidence": "16/16 repair loop tests pass"},
    {"id": "TC-MT2-03", "title": "Fix dirty-state detection porcelain parsing", "lane": "B", "status": "CLOSED_VERIFIED", "evidence": "portfolio_action_planner.py fixed, robust scanning"},
    {"id": "TC-MT2-04", "title": "Active family execution lanes", "lane": "C", "status": "CLOSED_VERIFIED", "evidence": "Conservation ALL_PASS 6/6, published=28"},
    {"id": "TC-MT2-05", "title": "Non-active family discovery sweep", "lane": "C", "status": "CLOSED_VERIFIED", "evidence": "19/19 NO_LOWCODE confirmed, OCR+PSD discovery_only"},
    {"id": "TC-MT2-06", "title": "Telemetry real run through metrics path", "lane": "D", "status": "CLOSED_VERIFIED", "evidence": "MetricsCollector 2 calls, 5000 tokens, session active"},
    {"id": "TC-MT2-07", "title": "README/publication readiness", "lane": "C", "status": "CLOSED_VERIFIED", "evidence": "6/6 families READY"},
    {"id": "TC-MT2-08", "title": "Evidence contract validation", "lane": "F", "status": "CLOSED_VERIFIED", "evidence": "V7=69 categories active, V8=70 categories available"},
    {"id": "TC-MT2-09", "title": "Master plan and taskcard sync", "lane": "A", "status": "CLOSED_VERIFIED", "evidence": "This report"},
    {"id": "TC-MT2-10", "title": "Full verification + regression", "lane": "F", "status": "PROPOSED", "evidence": "Pending"},
    {"id": "TC-MT2-11", "title": "Multi-commit with exact-path staging", "lane": "A", "status": "PROPOSED", "evidence": "Pending"},
    {"id": "TC-MT2-12", "title": "Evidence bundle ZIP", "lane": "F", "status": "PROPOSED", "evidence": "Pending"},
]

gap_map = {
    "pdf_pr_merge": {"status": "BLOCKED_EXTERNAL", "gate": "APPROVE_MERGE_PR", "description": "6 open PRs (#5-#10) awaiting human merge"},
    "live_pr_creation": {"status": "BLOCKED_EXTERNAL", "gate": "APPROVE_LIVE_PR", "description": "No new PRs without approval gate"},
    "readme_push": {"status": "BLOCKED_EXTERNAL", "gate": "APPROVE_README_PUSH", "description": "README push requires approval"},
    "form_importer_retest": {"status": "BLOCKED_LIBRARY_BUG", "description": "Aspose.PDF FormImporter has upstream bug"},
    "words_full_coverage": {"status": "DEFERRED", "description": "8/9 words workflow roots published, 1 remaining"},
}

report = {
    "report_type": "taskcard-sync-report",
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "run_id": "lowcode-ai-autonomous-execution-mega-train-20260519-114122",
    "taskcards": taskcards,
    "total_taskcards": len(taskcards),
    "closed_verified": sum(1 for t in taskcards if t["status"] == "CLOSED_VERIFIED"),
    "in_progress": 0,
    "proposed": sum(1 for t in taskcards if t["status"] == "PROPOSED"),
    "gap_map": gap_map,
}

out = RUN_DIR / "taskcard-sync-report.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"Written: {out}")

# Master plan markdown
lines = [
    "# Current State Master Plan and Gap Map",
    "",
    "**Sprint:** MEGA-TRAIN-002",
    "**RUN_ID:** lowcode-ai-autonomous-execution-mega-train-20260519-114122",
    f"**Generated:** {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
    "",
    "## Phases Completed",
    "",
    "- [x] Phase 1: Dirty-state reconciliation",
    "- [x] Phase 2: HI wiring (14 tests)",
    "- [x] Phase 3: Reviewer repair loop (16 tests)",
    "- [x] Phase 4: Family execution lanes (conservation ALL_PASS 6/6)",
    "- [x] Phase 5: Discovery sweep (19 NO_LOWCODE confirmed)",
    "- [x] Phase 6: Telemetry (MetricsCollector verified)",
    "- [x] Phase 7: README readiness (6/6 READY)",
    "- [x] Phase 8: Evidence contract (V7=69, V8=70)",
    "- [x] Phase 9: Taskcard sync",
    "",
    "## Phases Remaining",
    "",
    "- [ ] Phase 10: Full regression",
    "- [ ] Phase 11: Commits",
    "- [ ] Phase 12: Evidence bundle",
    "",
    "## Portfolio State",
    "",
    "- Published total: 28",
    "- Conservation: ALL_PASS 6/6",
    "- Active families: 6",
    "- Non-active families: 19",
    "",
    "## Code Changes",
    "",
    "- `runner.py`: HI wiring (generation + validation) + reviewer repair loop",
    "- `example_lifecycle.py`: reviewer_repaired stage + field",
    "- `portfolio_action_planner.py`: Robust porcelain parsing",
    "",
    "## New Test Files",
    "",
    "- tests/unit/test_healing_intelligence_wiring.py (14 tests)",
    "- tests/unit/test_reviewer_repair_loop.py (16 tests)",
    "",
    "## Gap Map",
    "",
]
for k, v in gap_map.items():
    lines.append(f"- **{k}**: {v['status']} -- {v['description']}")
lines.append("")

out2 = RUN_DIR / "current-state-master-plan-and-gap-map.md"
out2.write_text("\n".join(lines), encoding="utf-8")
print(f"Written: {out2}")
print(f"Taskcards: {report['closed_verified']}/{report['total_taskcards']} closed")
