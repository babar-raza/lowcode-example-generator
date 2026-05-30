"""Pass4 A1: Pass3 truth normalization and contradiction register."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPRINT_ID = "lowcode-systemization-pass4-20260530"
PRIOR_SPRINT = "lowcode-systemization-pass3-20260530"
BASE = REPO_ROOT / "reports" / SPRINT_ID / "audit"
BASE.mkdir(parents=True, exist_ok=True)

def main():
    print(f"=== A1 Truth Normalization: {SPRINT_ID} ===\n")

    # Pass3 truth normalization
    norm_md = f"""# Pass3 Truth Normalization — {SPRINT_ID}
Date: 2026-05-30

## Prior Sprint
Sprint ID: {PRIOR_SPRINT}
Prior claimed verdict: LOWCODE_REPEATABLE_SYSTEM_READY_MAIN_CLASS_GAPS_DOCUMENTED
Pass4 reclassification: SYSTEMIZATION_PROGRESS_ACCEPTED_CANONICAL_GENERATION_AND_EVIDENCE_REPAIR_REQUIRED

## Normalization
Pass3 is reclassified. The pass3 verdict is NOT accepted as repeatable closure because:
1. Fresh canonical generation failed or was blocked for all 6 families
2. E2E aggregate was borrowed from prior durable-full-closure sprint (not fresh)
3. Package results had contradictions (47 workspace vs 42 canonical vs 41 candidates)
4. final-clean-proof showed 30 tracked dirty files (DIRTY state)
5. Evidence ZIP lacked Program.cs, .csproj, package archives, raw restore/build/run logs
6. Main-class coverage had EXAMPLE_GAP and NEEDS_API_INVESTIGATION items

## What Pass3 Got Right
- 27-family universe authority (26 user-required + medical)
- epub classification (FORMAT_CAPABILITY_OF_OTHER_PRODUCT)
- Restore logs and reflection for all 27 families
- Sidecar artifact convention introduced
- 17 validators defined (framework valuable even if some results were wrong)
- Work-ahead documents prepared
"""
    (BASE / "pass3-truth-normalization.md").write_text(norm_md, encoding="utf-8")

    # Accepted vs rejected claims
    accepted = [
        {"claim": "27-family universe tracking established", "evidence": "universe/final-family-universe.json", "status": "ACCEPTED"},
        {"claim": "epub=FORMAT_CAPABILITY_OF_OTHER_PRODUCT", "evidence": "universe/epub-product-vs-format-decision.md", "status": "ACCEPTED"},
        {"claim": "medical=27th candidate with scope decision", "evidence": "universe/medical-scope-decision.md", "status": "ACCEPTED"},
        {"claim": "Restore logs present for 27 families", "evidence": "discovery/restore-logs/", "status": "ACCEPTED"},
        {"claim": "ZIP SHA-256: 503759abeb...", "evidence": ".local/evidence-bundles/...zip.sha256", "status": "ACCEPTED"},
        {"claim": "ZIP size: 199,597 bytes, 252 entries", "evidence": "sidecar files", "status": "ACCEPTED"},
        {"claim": "Sidecar convention introduced", "evidence": "artifact/artifact-protocol.md", "status": "ACCEPTED"},
        {"claim": "Work-ahead documents created", "evidence": "workahead/", "status": "ACCEPTED"},
    ]
    rejected = [
        {"claim": "Repeatable system closure", "reason": "Fresh generation blocked for all 6 families", "status": "REJECTED"},
        {"claim": "42/42 E2E PASS", "reason": "E2E from prior sprint (not fresh); actual fails: cells 1/9, diagram 2/2, pdf 1/19, words 2/8", "status": "REJECTED"},
        {"claim": "17/17 validators PASS", "reason": "V-012 (pytest log) was DEFERRED then claimed PASS without actual log", "status": "REJECTED_PARTIAL"},
        {"claim": "Final clean proof CLEAN", "reason": "final-clean-proof: 30 tracked dirty files (all bin/obj)", "status": "REJECTED"},
        {"claim": "Package-ready", "reason": "Bundle lacks Program.cs, .csproj, package archives, raw logs", "status": "REJECTED"},
        {"claim": "Publication-ready", "reason": "Canonical generation blocked, E2E not fresh", "status": "REJECTED"},
        {"claim": "Main-class gaps accepted", "reason": "EXAMPLE_GAP and NEEDS_API_INVESTIGATION not valid accepted blockers", "status": "REJECTED"},
        {"claim": "Denominator consistent (47=42=41)", "reason": "47 workspace != 42 canonical != 41 candidates", "status": "REJECTED"},
        {"claim": "Idempotency covers generation", "reason": "A/B idempotency was canonical_packager only, not full generation", "status": "REJECTED"},
        {"claim": "Self-contained evidence bundle", "reason": "No Program.cs, .csproj, package dirs, raw restore/build/run logs", "status": "REJECTED"},
        {"claim": "Fresh canonical generation blocked by catalog hash mismatch (pass4 B1 investigation)", "reason": "B1 investigation shows hash currently MATCHES for cells (b4fa821f). Mismatch may have been transient or caused by pass3 template-mode interaction.", "status": "UNDER_INVESTIGATION"},
    ]

    (BASE / "accepted-vs-rejected-claims.json").write_text(
        json.dumps({
            "sprint_id": SPRINT_ID,
            "prior_sprint": PRIOR_SPRINT,
            "accepted": accepted,
            "rejected": rejected,
        }, indent=2),
        encoding="utf-8"
    )

    # Contradiction register
    contradictions = [
        {
            "id": "CR-001",
            "claim": "final-clean DIRTY vs accepted verdict",
            "detail": "Pass3 final-clean-proof: 30 tracked dirty files, Status: DIRTY. Yet verdict claimed LOWCODE_REPEATABLE_SYSTEM_READY.",
            "severity": "HIGH",
            "resolution": "pass4 classifies bin/obj artifacts as non-blocking; uses isolated workspace"
        },
        {
            "id": "CR-002",
            "claim": "E2E aggregate failures vs 42/42 claim",
            "detail": "Pass3 H1 used durable-full-closure E2E summaries, not fresh runs. Actual failures: cells 1/9, diagram 2/2, pdf 1/19, words 2/8 = 35/42 not 42/42.",
            "severity": "CRITICAL",
            "resolution": "pass4 runs real E2E from fresh canonical generation with per-example logs"
        },
        {
            "id": "CR-003",
            "claim": "Package incomplete false vs package-ready claim",
            "detail": "pdf-controlled-pilot, pdf-pr5, pdf-pr6 marked incomplete. Yet verdict claimed package-ready.",
            "severity": "HIGH",
            "resolution": "pass4 rebuilds all packages from fresh canonical generation"
        },
        {
            "id": "CR-004",
            "claim": "Fresh generation blocked vs repeatability claim",
            "detail": "All 6 families: cells=BLOCKED_SCENARIO_PLANNING, diagram/email/slides=DATA_FLOW_PROTOTYPE_ONLY, pdf/words=BLOCKED_SOURCE_OF_TRUTH. Repeatability cannot be claimed.",
            "severity": "CRITICAL",
            "resolution": "pass4 B1 investigation + B2 fresh generation"
        },
        {
            "id": "CR-005",
            "claim": "Package-included 47 vs publication candidates 41",
            "detail": "47 examples in workspace, 42 canonical (4 duplicate-excluded), 41 publication candidates (1 timestamp). Inconsistency not resolved.",
            "severity": "HIGH",
            "resolution": "pass4 D1 defines strict denominator model with clear accounting"
        },
        {
            "id": "CR-006",
            "claim": "Evidence bundle lacks generated source",
            "detail": "Pass3 ZIP has no Program.cs, .csproj, package directories, or raw restore/build/run logs. Claimed self-contained.",
            "severity": "HIGH",
            "resolution": "pass4 J2 self-contained bundle includes all required file types"
        },
    ]

    (BASE / "contradiction-register.json").write_text(
        json.dumps({
            "sprint_id": SPRINT_ID,
            "prior_sprint": PRIOR_SPRINT,
            "total_contradictions": len(contradictions),
            "contradictions": contradictions,
        }, indent=2),
        encoding="utf-8"
    )

    # State/taskcard sync proof
    (BASE / "state-taskcard-sync-proof.md").write_text(
        f"""# State/Taskcard Sync Proof — {SPRINT_ID}

## Pass3 Reclassification
- Pass3 sprint ID: {PRIOR_SPRINT}
- Pass3 claimed verdict: LOWCODE_REPEATABLE_SYSTEM_READY_MAIN_CLASS_GAPS_DOCUMENTED
- Pass4 reclassification: SYSTEMIZATION_PROGRESS_ACCEPTED_CANONICAL_GENERATION_AND_EVIDENCE_REPAIR_REQUIRED

## Taskcard Status
Pass3 cannot be treated as publication-ready:
- Canonical generation is blocked/prototype-only for all 6 families
- E2E evidence is from prior sprint (not fresh)
- Evidence bundle is not self-contained

## Pass4 Position
Pass4 inherits the 27-family universe and accepted claims from pass3.
Pass4 must prove: fresh generation, real E2E, self-contained evidence.
""",
        encoding="utf-8"
    )

    print(f"  A1: {len(accepted)} accepted, {len(rejected)} rejected, {len(contradictions)} contradictions")
    print(f"  Reports written to {BASE}/")

if __name__ == "__main__":
    main()
