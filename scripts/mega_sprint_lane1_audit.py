"""Lane 1: Prior bundle audit — reclassify previous sprint, record contradictions."""
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).parent.parent
SPRINT_ID = "full-system-qualification-repair-20260529"
SPRINT_ROOT = REPO_ROOT / "reports" / SPRINT_ID
PREV_SPRINT = "system-qualification"
NOW = "2026-05-29T00:00:00Z"

CONTRADICTIONS = [
    {
        "id": "C-001",
        "category": "SKIP_RUN_ENABLED",
        "description": "All 6 LowCode E2E runs used --skip-run + --template-mode. Validation, reviewer, and publisher stages were explicitly skipped.",
        "evidence": "reports/system-qualification/products/{family}/e2e/e2e-run-summary.md shows 'validation: skipped (template mode)' for all 6 families.",
        "impact": "No dotnet build, dotnet restore, or dotnet run was executed. Build stage NOT RUN.",
        "severity": "FATAL_FOR_FULL_QUALIFICATION",
        "resolved_by": "This sprint runs replay_from=validation with template_mode=False for all 6 families."
    },
    {
        "id": "C-002",
        "category": "BUILD_NOT_RUN",
        "description": "Build logs say build NOT RUN for all 6 LowCode products in the prior sprint.",
        "evidence": "reports/system-qualification/products/{family}/e2e/build.log contains 'BUILD_NOT_RUN: template-mode dry-run' for all families.",
        "impact": "No compilation evidence exists from the prior sprint.",
        "severity": "FATAL_FOR_FULL_QUALIFICATION",
        "resolved_by": "This sprint produces real dotnet build logs for all 42 examples."
    },
    {
        "id": "C-003",
        "category": "VALIDATION_SKIPPED",
        "description": "Validation stage (stage 15) was skipped in template-mode for all 6 products.",
        "evidence": "pilot-report.json for all 6 final runs shows validation stage as skipped.",
        "impact": "No validation-results.json from a real run exists in the prior sprint evidence.",
        "severity": "FATAL_FOR_FULL_QUALIFICATION",
        "resolved_by": "This sprint re-runs validation stage with template_mode=False."
    },
    {
        "id": "C-004",
        "category": "REVIEWER_SKIPPED",
        "description": "Reviewer stage was skipped in template-mode. No governed fallback was documented.",
        "evidence": "reviewer-results.json in prior sprint shows 'available: false' with no fallback proof.",
        "impact": "No evidence of reviewer validation or explicitly accepted fallback.",
        "severity": "REQUIRES_GOVERNED_FALLBACK",
        "resolved_by": "This sprint documents reviewer unavailability with explicit governed fallback proof per Lane 3 protocol."
    },
    {
        "id": "C-005",
        "category": "PUBLISHER_SKIPPED",
        "description": "Publisher/local package dry-run was not executed in the prior sprint.",
        "evidence": "package-dry-run-result.json in prior sprint shows 'dry_run_skipped: template-mode'.",
        "impact": "No local PR dry-run evidence from the prior sprint.",
        "severity": "FATAL_FOR_FULL_QUALIFICATION",
        "resolved_by": "This sprint runs publisher stage (dry_run=True) for all 6 families."
    },
    {
        "id": "C-006",
        "category": "UNBUNDLED_PRODUCTION_EVIDENCE",
        "description": "Prior sprint final verdict relied on workspace/verification/latest paths for production evidence, but those paths were not bundled in the evidence ZIP.",
        "evidence": "Prior ZIP (system-qualification-evidence-20260528.zip) contains only machinery evidence. No raw generated C# code, build logs, or runtime outputs.",
        "impact": "Evidence is not self-contained. Reviewer cannot verify claims without external workspace.",
        "severity": "FATAL_FOR_FULL_QUALIFICATION",
        "resolved_by": "This sprint bundles raw E2E evidence including build logs, runtime logs, and validation results."
    },
    {
        "id": "C-007",
        "category": "VALIDATOR_TESTS_NOT_RUN",
        "description": "pytest was not run in the prior sprint. Test suite status unknown.",
        "evidence": "No tests/ directory in prior sprint evidence. No full-pytest.log.",
        "impact": "No test coverage evidence. Validator correctness unproven.",
        "severity": "REQUIRES_REPAIR",
        "resolved_by": "This sprint runs full pytest suite and targeted validator tests."
    },
    {
        "id": "C-008",
        "category": "HTML_SVG_CONTRADICTION_PARTIAL",
        "description": "HTML and SVG were classified NO_LOWCODE_CONFIRMED but had dependency blockers (missing transitive deps). Resolution was documented in workspace but not in the sprint evidence.",
        "evidence": "workspace/verification/latest/html-reflection-blocker.json shows blocker_severity=RESOLVED but this file was not in the evidence ZIP.",
        "impact": "Reviewer cannot verify NO_LOWCODE claim without resolution proof.",
        "severity": "REQUIRES_BUNDLING",
        "resolved_by": "This sprint includes fresh DllReflector runs for HTML and SVG with resolution proof in evidence."
    },
    {
        "id": "C-009",
        "category": "PRODUCT_QUEUE_NOT_TRACKED",
        "description": "Prior sprint did not maintain a formal product queue with PENDING/RUNNING/PASSED/BLOCKED states.",
        "evidence": "No product-queue-start.json or product-queue-final.json in prior sprint evidence.",
        "impact": "Cannot verify no product remained PENDING.",
        "severity": "REQUIRES_REPAIR",
        "resolved_by": "This sprint maintains a formal product queue per Lane 4 protocol."
    },
]

KNOWN_GOOD_CARRYFORWARD = [
    {
        "item": "HEAL-001 PDF include_all_tfm_groups",
        "description": "runner.py DependencyResolution now passes include_all_tfm_groups=True for PDF family. Fix verified by clean re-run in prior sprint.",
        "files_affected": [
            "src/plugin_examples/family_config/models.py",
            "src/plugin_examples/family_config/loader.py",
            "src/plugin_examples/runner.py",
            "pipeline/configs/families/pdf.yml",
            "pipeline/schemas/family-config.schema.json",
        ],
        "test_status": "VERIFIED_BY_CLEAN_RERUN_IN_PRIOR_SPRINT",
        "action_in_this_sprint": "Used as-is; re-verified by running full validation stage for PDF."
    },
    {
        "item": "HEAL-002 Words denominator canonical hash",
        "description": "words.json denominator api_catalog_sha256 reverted to canonical value after stale-cache false positive.",
        "files_affected": ["pipeline/configs/denominators/words.json"],
        "test_status": "VERIFIED_BY_CLEAN_RERUN_IN_PRIOR_SPRINT",
        "action_in_this_sprint": "Used as-is; re-verified by running scenario_planning stage for Words."
    },
    {
        "item": "25-product universe classification",
        "description": "25 products classified across all categories. Universe reconciliation against expected 26 documented with evidence.",
        "test_status": "ACCEPTED_IN_PRIOR_SPRINT",
        "action_in_this_sprint": "Fresh discovery re-run for all 25 products to update classification."
    },
    {
        "item": "External blocker evidence for epub/ocr/psd",
        "description": "Three products blocked by external NuGet unavailability.",
        "test_status": "ACCEPTED_IN_PRIOR_SPRINT",
        "action_in_this_sprint": "Rechecked fresh in Lane 7."
    },
]


def main():
    audit = SPRINT_ROOT / "audit"
    audit.mkdir(parents=True, exist_ok=True)

    # previous-bundle-audit.md
    with open(audit / "previous-bundle-audit.md", "w") as f:
        f.write(f"# Previous Bundle Audit\n\n")
        f.write(f"**Sprint ID:** {SPRINT_ID}\n")
        f.write(f"**Audited Bundle:** system-qualification-evidence-20260528.zip\n")
        f.write(f"**Previous Sprint ID:** sysqual-20260528-001\n")
        f.write(f"**Audit Date:** {NOW}\n\n")
        f.write(f"## Reclassification\n\n")
        f.write(f"Previous verdict was: `LOWCODE_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS`\n\n")
        f.write(f"**Reclassified as:** `PARTIAL_MACHINERY_QUALIFICATION_ACCEPTED_FULL_SYSTEM_QUALIFICATION_NOT_ACCEPTED`\n\n")
        f.write(f"### Reasons\n\n")
        for c in CONTRADICTIONS:
            f.write(f"- **{c['id']} ({c['category']}):** {c['description']}\n")
        f.write(f"\n## Known Good Items (carried forward)\n\n")
        for kg in KNOWN_GOOD_CARRYFORWARD:
            f.write(f"- **{kg['item']}:** {kg['description']}\n")

    # overclaim-correction.md
    with open(audit / "overclaim-correction.md", "w") as f:
        f.write(f"# Overclaim Correction\n\n")
        f.write(f"**Sprint ID:** {SPRINT_ID}\n")
        f.write(f"**Date:** {NOW}\n\n")
        f.write(f"## Previous Sprint Overclaims\n\n")
        f.write(f"The previous sprint's final verdict stated 'LOWCODE_SYSTEM_QUALIFICATION_ACCEPTED' but:\n\n")
        f.write(f"1. All E2E runs used `--template-mode --skip-run --tier 3`. This means stages 15-17 (validation, reviewer, publisher) were **skipped by design**.\n")
        f.write(f"2. Build logs explicitly contain 'BUILD_NOT_RUN: template-mode dry-run'.\n")
        f.write(f"3. The verdict 'full system qualification' does not apply when validation/build/run/reviewer/publisher are not executed.\n")
        f.write(f"4. Production evidence from `workspace/verification/latest/` was referenced but not bundled.\n\n")
        f.write(f"## Correction Applied\n\n")
        f.write(f"- Previous sprint reclassified as: `PARTIAL_MACHINERY_QUALIFICATION`\n")
        f.write(f"- This sprint runs real validation (dotnet build + run) for all 6 LowCode products.\n")
        f.write(f"- This sprint bundles all raw E2E evidence in the final ZIP.\n")
        f.write(f"- This sprint runs pytest to verify the validator itself.\n")
        f.write(f"- This sprint adds validator rules to prevent future overclaiming of this class.\n")

    # state-correction-proof.md
    with open(audit / "state-correction-proof.md", "w") as f:
        f.write(f"# State Correction Proof\n\n")
        f.write(f"**Sprint ID:** {SPRINT_ID}\n")
        f.write(f"**Date:** {NOW}\n\n")
        f.write(f"## Actions Taken\n\n")
        f.write(f"1. `reports/system-qualification/final-verdict.md` is NOT modified by this sprint (preserved as historical record).\n")
        f.write(f"2. A new `reports/system-qualification/RECLASSIFIED.md` file is added documenting the reclassification.\n")
        f.write(f"3. New validator rules (Lane 5) will prevent future final verdicts from claiming full qualification without real validation evidence.\n")
        f.write(f"4. This sprint's own final-verdict.md will use the correct verdict enum from the allowed list.\n\n")
        f.write(f"## Files Modified By This Correction\n\n")
        f.write(f"- None of the previous sprint's evidence files are modified.\n")
        f.write(f"- A RECLASSIFIED.md addendum is added to the prior sprint report directory.\n")

    # known-good-carryforward.md
    with open(audit / "known-good-carryforward.md", "w") as f:
        f.write(f"# Known Good Carryforward\n\n")
        f.write(f"**Sprint ID:** {SPRINT_ID}\n")
        f.write(f"**Date:** {NOW}\n\n")
        for kg in KNOWN_GOOD_CARRYFORWARD:
            f.write(f"## {kg['item']}\n\n")
            f.write(f"**Description:** {kg['description']}\n\n")
            f.write(f"**Test Status:** {kg['test_status']}\n\n")
            f.write(f"**Action in this sprint:** {kg['action_in_this_sprint']}\n\n")
            if kg.get('files_affected'):
                f.write(f"**Files:** {', '.join(kg['files_affected'])}\n\n")

    # contradiction-register.json
    with open(audit / "contradiction-register.json", "w") as f:
        json.dump({
            "sprint_id": SPRINT_ID,
            "generated_at": NOW,
            "previous_sprint_id": "sysqual-20260528-001",
            "previous_verdict": "LOWCODE_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS",
            "reclassified_as": "PARTIAL_MACHINERY_QUALIFICATION_ACCEPTED_FULL_SYSTEM_QUALIFICATION_NOT_ACCEPTED",
            "contradiction_count": len(CONTRADICTIONS),
            "contradictions": CONTRADICTIONS,
            "known_good_count": len(KNOWN_GOOD_CARRYFORWARD),
            "known_good": KNOWN_GOOD_CARRYFORWARD,
        }, f, indent=2)

    # Add RECLASSIFIED.md to prior sprint
    reclassified = REPO_ROOT / "reports" / PREV_SPRINT / "RECLASSIFIED.md"
    with open(reclassified, "w") as f:
        f.write(f"# RECLASSIFIED\n\n")
        f.write(f"**Original Verdict:** LOWCODE_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS\n\n")
        f.write(f"**Reclassified As:** PARTIAL_MACHINERY_QUALIFICATION_ACCEPTED_FULL_SYSTEM_QUALIFICATION_NOT_ACCEPTED\n\n")
        f.write(f"**Reclassified By:** {SPRINT_ID}\n\n")
        f.write(f"**Date:** {NOW}\n\n")
        f.write(f"## Reason\n\n")
        f.write(f"All 6 LowCode E2E runs used `--template-mode --skip-run --tier 3`. ")
        f.write(f"Validation, reviewer, and publisher stages were skipped by design. ")
        f.write(f"Build logs say BUILD_NOT_RUN. Production evidence was not bundled.\n\n")
        f.write(f"This was a correct machinery qualification but does not constitute full system qualification.\n\n")
        f.write(f"See: `reports/{SPRINT_ID}/audit/contradiction-register.json` for full audit.\n")

    print("Lane 1 complete — audit files written")
    for p in sorted(audit.iterdir()):
        print(f"  {p.name}")
    print(f"  (also: reports/system-qualification/RECLASSIFIED.md)")

if __name__ == "__main__":
    main()
