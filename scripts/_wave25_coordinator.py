"""Wave 25 — Coordinator (Lane 0 + utility for all lanes).

Sprint: LOWCODE-PLUGIN-PRODUCTION-HEAL-WAVE25-20260609
Uses _coordinator_base.py (Lane H pilot — new for W25).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _coordinator_base import CoordinatorBase

SPRINT = "lowcode-plugin-production-heal-wave25-20260609"
REPORT_DIR = Path(f"reports/{SPRINT}")
DATE = "2026-06-09"

SUBDIRS = [
    "coordinator",
    "taskcards",
    "governance",
    "fixtures",
    "discovery",
    "provenance",
    "generation",
    "nonlowcode",
    "healing",
    "validators",
    "pr-lifecycle",
    "security",
    "iv",
    "adversarial-review",
    "state-truth",
    "evidence-authority",
    "final",
    "scaling",
]

LANES = {
    "L0": {"status": "IN_PROGRESS", "desc": "Coordinator, taskcards, hard-stop manifest, repo separation"},
    "LA": {"status": "PENDING", "desc": "Governance repair — AGENTS.md, merge_approval_gate.py AMG, PLV-16/17"},
    "LB": {"status": "PENDING", "desc": "Fixture system — schema, 17 family YAMLs, production-safe fetcher, provenance sidecars"},
    "LC": {"status": "PENDING", "desc": "Discovery freshness — metadata, drift detection, mode-aware gate, GitHub Actions workflow"},
    "LD": {"status": "PENDING", "desc": "Provenance hardening — version drift hard-stop, NuGet SHA manifest, API delta auto-steering"},
    "LE": {"status": "PENDING", "desc": "DRYRUN batch prove — dynamic backlog, build-and-prove script, registry transition ledger"},
    "LF": {"status": "PENDING", "desc": "Non-LowCode wiring — fallback_strategy configs, SDE routing, PR builder alignment, NLV-15"},
    "LG": {"status": "PENDING", "desc": "Healing architecture — additive auto-learn CANDIDATE, capped repair loop, scenario difficulty index"},
    "LH": {"status": "PENDING", "desc": "Coordinator automation pilot — _coordinator_base.py, new_sprint.py, template"},
    "LI": {"status": "PENDING", "desc": "Scaling pilots — --family-config flag, stage-registry YAML, family templates"},
    "LJ": {"status": "PENDING", "desc": "Full test suite — all new tests for every lane, actual counts from raw logs"},
    "LK": {"status": "PENDING", "desc": "State truth and registry transition ledger"},
    "LL": {"status": "PENDING", "desc": "PR lifecycle — AMG evaluation for 3 open PRs, merge if APPROVE_LIVE_MERGE=1"},
    "LM": {"status": "PENDING", "desc": "Security hygiene — SHV validators, fixture provenance check, binary audit"},
    "LN": {"status": "PENDING", "desc": "IV + adversarial review — 15 IV checks + 12 AR checks + 15 W25-specific IV"},
    "LZ": {"status": "PENDING", "desc": "Bundle freeze — ZIP, SHA-256 sidecar, final attestation"},
}

TASKS: list[tuple[str, str, str]] = [
    # Lane 0
    ("W25-L0-01", "L0", "Coordinator setup: dirs, taskcards, hard-stop manifest, repo separation"),
    ("W25-L0-02", "L0", "Lane ledger and execution board written"),
    # Lane A — Governance
    ("W25-LA-01", "LA", "AGENTS.md — surgical merge-authority language update"),
    ("W25-LA-02", "LA", "merge_approval_gate.py — AMG state machine (AMG-01..10)"),
    ("W25-LA-03", "LA", "publication_lifecycle_validators.py — PLV-16 fixture/publication repo separation"),
    ("W25-LA-04", "LA", "publication_lifecycle_validators.py — PLV-17 PR URL allowlist check"),
    ("W25-LA-05", "LA", "Tests: test_auto_merge_gate.py (10 AMG conditions)"),
    ("W25-LA-06", "LA", "Tests: test_wrong_repo_validator_plv16_17.py"),
    # Lane B — Fixtures
    ("W25-LB-01", "LB", "family-config.schema.json — add official_examples_repo field"),
    ("W25-LB-02", "LB", "17 non-LowCode family YAMLs — add official_examples_repo"),
    ("W25-LB-03", "LB", "fixture_fetcher.py — production-safe fetcher with provenance sidecars"),
    ("W25-LB-04", "LB", "fixture_fetcher.py — cache hit/miss logic with manifest"),
    ("W25-LB-05", "LB", "fixture_fetcher.py — extension allowlist + size limits"),
    ("W25-LB-06", "LB", "scenario_planner/planner.py — fixture resolution wiring"),
    ("W25-LB-07", "LB", "Tests: test_fixture_fetcher.py (cache, filter, limits)"),
    ("W25-LB-08", "LB", "Tests: test_fixture_provenance.py (sidecar format)"),
    ("W25-LB-09", "LB", "Tests: test_fixture_synthetic_fallback.py"),
    # Lane C — Discovery
    ("W25-LC-01", "LC", "discovery_sweep.py — discovery_metadata (validated_at, expires_at, run_id)"),
    ("W25-LC-02", "LC", "drift_detector.py — implement prior vs current comparison"),
    ("W25-LC-03", "LC", "drift_detector.py — DriftReport: added/removed/changed/unchanged"),
    ("W25-LC-04", "LC", "runner.py — mode-aware discovery freshness gate (read_only/dry_run/publication)"),
    ("W25-LC-05", "LC", ".github/workflows/weekly-discovery.yml — new GitHub Actions workflow"),
    ("W25-LC-06", "LC", "Tests: test_discovery_freshness_gate.py"),
    ("W25-LC-07", "LC", "Tests: test_drift_detection.py"),
    # Lane D — Provenance
    ("W25-LD-01", "LD", "runner.py — version drift hard-stop in publication mode + ACCEPT_VERSION_DRIFT env gate"),
    ("W25-LD-02", "LD", "nuget_fetcher/fetcher.py — local SHA-256 manifest + revalidation (not ETag)"),
    ("W25-LD-03", "LD", "api_delta/delta_engine.py — removed symbols auto-added as CANDIDATE (not CONFIRMED)"),
    ("W25-LD-04", "LD", "Tests: test_nuget_sha_manifest.py (corrupted file triggers re-download)"),
    ("W25-LD-05", "LD", "Tests: test_api_delta_auto_steering.py (removed symbol = CANDIDATE only)"),
    # Lane E — DRYRUN batch prove
    ("W25-LE-01", "LE", "scripts/_wave25_batch_prove.py — dynamic backlog from registry (never hardcoded)"),
    ("W25-LE-02", "LE", "dryrun-backlog.json written as first evidence artifact"),
    ("W25-LE-03", "LE", "Per-package restore/build/run with exact blocker classes"),
    ("W25-LE-04", "LE", "build-matrix.json — all package results with exit codes"),
    ("W25-LE-05", "LE", "Registry updated — PASS→CANONICAL_PACKAGE_PROVEN, FAIL→blocker recorded"),
    ("W25-LE-06", "LE", "registry-transition-ledger.json written"),
    ("W25-LE-07", "LE", "code_generator.py — generation_strategy + unified contract validation"),
    # Lane F — Non-LowCode wiring
    ("W25-LF-01", "LF", "18 non-LowCode family configs — fallback_strategy: capability_registry"),
    ("W25-LF-02", "LF", "runner.py — _stage_fallback_registry_lookup elevates to ctx.fallback_candidates (PROBE_CONFIRMED only)"),
    ("W25-LF-03", "LF", "runner.py — _stage_generation routes to _generate_nonlowcode_examples"),
    ("W25-LF-04", "LF", "runner.py — _generate_nonlowcode_examples wires SharedDownstreamExecutor"),
    ("W25-LF-05", "LF", "shared_downstream_executor.py — confirm PluginCandidate schema handles both namespace_source values"),
    ("W25-LF-06", "LF", "pr_builder.py — non-LowCode PR routing (branch, title, folder convention)"),
    ("W25-LF-07", "LF", "evidence_validator/rules/non_lowcode.py — NLV-15 PROBE_CONFIRMED requirement"),
    ("W25-LF-08", "LF", "Disabled family dry-run safety check — no PROBE_CONFIRMED = SKIPPED not crash"),
    ("W25-LF-09", "LF", "E2E dry-run: barcode — artifact contract PASS (5 files)"),
    ("W25-LF-10", "LF", "E2E dry-run: svg — artifact contract PASS (5 files)"),
    ("W25-LF-11", "LF", "E2E dry-run: cad — artifact contract PASS (5 files)"),
    ("W25-LF-12", "LF", "Tests: test_nonlowcode_end_to_end.py"),
    ("W25-LF-13", "LF", "Tests: test_fallback_to_generation_wiring.py"),
    # Lane G — Healing
    ("W25-LG-01", "LG", "healing_intelligence/loader.py — auto_learn_from_run (additive-only, CANDIDATE status)"),
    ("W25-LG-02", "LG", "runner.py — call auto_learn_from_run at end of _stage_reviewer"),
    ("W25-LG-03", "LG", "runner.py — repair loop: capped at 2 retries, CONFIRMED repairs only, evidence written"),
    ("W25-LG-04", "LG", "scenario-difficulty-index.json — new workspace verification file"),
    ("W25-LG-05", "LG", "scenario_planner/planner.py — deprioritize scenarios where success_rate < 0.3"),
    ("W25-LG-06", "LG", "Tests: test_healing_auto_learn.py"),
    # Lane H — Coordinator pilot
    ("W25-LH-01", "LH", "_coordinator_base.py — CoordinatorBase class (already created for L0)"),
    ("W25-LH-02", "LH", "scripts/new_sprint.py — sprint scaffold generator"),
    ("W25-LH-03", "LH", "scripts/templates/sprint_coordinator_template.py — template with substitution"),
    ("W25-LH-04", "LH", "Tests: test_new_sprint_launcher.py (no overwrite without --force)"),
    # Lane I — Scaling pilots
    ("W25-LI-01", "LI", "__main__.py — --family-config CLI flag with schema validation"),
    ("W25-LI-02", "LI", "pipeline/configs/stage-registry.yml — optional stage registry pilot"),
    ("W25-LI-03", "LI", "runner.py — load stage-registry.yml if present, fall back to hardcoded"),
    ("W25-LI-04", "LI", "pipeline/family-templates/ — directory created (initially empty, no behavior change)"),
    ("W25-LI-05", "LI", "Tests: test_stage_registry_fallback.py (invalid YAML → hardcoded list, no crash)"),
    # Lane J — Full test suite
    ("W25-LJ-01", "LJ", "Full pytest suite run — actual count from raw log (not hardcoded)"),
    ("W25-LJ-02", "LJ", "All new tests from Lanes A-I pass"),
    ("W25-LJ-03", "LJ", "No existing test regresses"),
    # Lane K — State truth
    ("W25-LK-01", "LK", "state-truth.json — PCLC, proven_packages, dryrun_packages (from registry)"),
    ("W25-LK-02", "LK", "state-truth.json — nonlowcode_enabled_families list"),
    ("W25-LK-03", "LK", "state-truth.json — discovery_freshness, version_drift_status"),
    ("W25-LK-04", "LK", "state-truth.json — external_gates with AMG vocabulary"),
    # Lane L — PR lifecycle
    ("W25-LL-01", "LL", "Verify 3 PRs against APPROVED_PUBLICATION_REPOS allowlist"),
    ("W25-LL-02", "LL", "Evaluate all AMG gates (AMG-01..10) for each PR"),
    ("W25-LL-03", "LL", "barcode PR: merge-result-barcode.json (MERGED or CREDENTIAL_BLOCKED)"),
    ("W25-LL-04", "LL", "svg PR: merge-result-svg.json (MERGED or CREDENTIAL_BLOCKED)"),
    ("W25-LL-05", "LL", "cad PR: merge-result-cad.json (MERGED or CREDENTIAL_BLOCKED)"),
    ("W25-LL-06", "LL", "Branch deletion: BDG gates evaluated; BRANCH_DELETE_AUTHORIZED or BRANCH_DELETE_SKIPPED_POLICY"),
    ("W25-LL-07", "LL", "pr-lifecycle-final.json — per-PR state using AMG vocabulary (not APPROVAL_BLOCKED)"),
    # Lane M — Security
    ("W25-LM-01", "LM", "SHV-01..03 validators run on all generated files"),
    ("W25-LM-02", "LM", "No .pfx/.pem/.key/.p12 in generated examples"),
    ("W25-LM-03", "LM", "Fixture provenance sidecars for all downloaded binary files"),
    ("W25-LM-04", "LM", "No executable code in fixtures from official repos (data files only)"),
    ("W25-LM-05", "LM", "security-hygiene-report.json"),
    # Lane N — IV + AR
    ("W25-LN-01", "LN", "Standard IV checks (15) — all pass"),
    ("W25-LN-02", "LN", "Standard AR checks (12) — all pass"),
    ("W25-LN-03", "LN", "W25-specific IV checks (IV-W25-01..15) — all pass"),
    ("W25-LN-04", "LN", "iv-results.json written"),
    ("W25-LN-05", "LN", "adversarial-review-final.json written"),
    # Lane Z — Bundle freeze
    ("W25-LZ-01", "LZ", "Evidence directory complete — all mandatory bundle contents present"),
    ("W25-LZ-02", "LZ", "Bundle ZIP frozen to .local/evidence-bundles/"),
    ("W25-LZ-03", "LZ", "SHA-256 computed AFTER freeze"),
    ("W25-LZ-04", "LZ", "External .sha256 sidecar written"),
    ("W25-LZ-05", "LZ", "final-attestation.json written with SHA, size, entry_count, phases_promoted"),
    ("W25-LZ-06", "LZ", "Post-freeze SHA verified against sidecar"),
    ("W25-LZ-07", "LZ", "SPRINT_COMPLETE declared"),
]

HARD_STOP_CONDITIONS = [
    {"id": "HS-01", "desc": "Auto-merge attempted without APPROVE_LIVE_MERGE=1 present in env"},
    {"id": "HS-02", "desc": "Auto-merge attempted against repo not in APPROVED_PUBLICATION_REPOS allowlist"},
    {"id": "HS-03", "desc": "Branch deletion attempted without APPROVE_DELETE_BRANCH=1 present in env"},
    {"id": "HS-04", "desc": "Non-LowCode claimed 'pipeline enabled' without real barcode/svg/cad dry-run through runner"},
    {"id": "HS-05", "desc": "DRYRUN backlog claimed complete without registry-derived per-package result for each entry"},
    {"id": "HS-06", "desc": "Discovery claimed Green without freshness metadata and drift report as evidence"},
    {"id": "HS-07", "desc": "Provenance claimed Green without NuGet SHA-256 revalidation evidence"},
    {"id": "HS-08", "desc": "Generation claimed Green without build/run/output files for each promoted package"},
    {"id": "HS-09", "desc": "Healing claimed Green if auto-learn writes CONFIRMED directly without threshold check"},
    {"id": "HS-10", "desc": "SPRINT_COMPLETE claimed without all taskcards COMPLETE + raw logs + bundle + sidecar + attestation"},
    {"id": "HS-11", "desc": "Fixture source repos confused with publication target repos in any code path"},
    {"id": "HS-12", "desc": "APPROVAL_BLOCKED used for new internal decision-making (compatibility alias only)"},
]

APPROVED_PUBLICATION_REPOS = [
    "aspose-barcode-net/Aspose.BarCode.Plugins-for-.NET-Examples",
    "aspose-svg-net/Aspose.SVG.Plugins-for-.NET-Examples",
    "aspose-cad-net/Aspose.CAD.Plugins-for-.NET-Examples",
]

FIXTURE_SOURCE_REPOS = [
    "aspose-barcode/Aspose.BarCode-for-.NET",
    "aspose-svg/Aspose.SVG-for-.NET",
    "aspose-cad/Aspose.CAD-for-.NET",
    "aspose-cells/Aspose.Cells-for-.NET",
    "aspose-words/Aspose.Words-for-.NET",
    "aspose-html/Aspose.HTML-for-.NET",
    "aspose-font/Aspose.Font-for-.NET",
    "aspose-imaging/Aspose.Imaging-for-.NET",
    "aspose-gis/Aspose.GIS-for-.NET",
    "aspose-finance/Aspose.Finance-for-.NET",
    "aspose-omr/Aspose.OMR-for-.NET",
    "aspose-note/Aspose.Note-for-.NET",
    "aspose-tasks/Aspose.Tasks-for-.NET",
    "aspose-page/Aspose.TeX-for-.NET",
    "aspose-ocr/Aspose.OCR-for-.NET",
    "aspose-3d/Aspose.3D-for-.NET",
    "aspose-psd/Aspose.PSD-for-.NET",
    "aspose-zip/Aspose.ZIP-for-.NET",
]

FILE_OWNERSHIP = [
    {"file": "AGENTS.md", "owner": "LA", "action": "surgical-edit"},
    {"file": "src/plugin_examples/publisher/merge_approval_gate.py", "owner": "LA", "action": "rewrite"},
    {"file": "src/plugin_examples/publisher/approval_gate.py", "owner": "LA", "action": "edit"},
    {"file": "src/plugin_examples/fixture_factory/publication_lifecycle_validators.py", "owner": "LA", "action": "edit-add-PLV16-17"},
    {"file": "pipeline/schemas/family-config.schema.json", "owner": "LB", "action": "edit"},
    {"file": "pipeline/configs/families/*.yml (17 non-LowCode)", "owner": "LB", "action": "edit-add-official_examples_repo"},
    {"file": "src/plugin_examples/fixture_registry/fixture_fetcher.py", "owner": "LB", "action": "rewrite"},
    {"file": "src/plugin_examples/scenario_planner/planner.py", "owner": "LB+LG", "joint": True, "action": "edit"},
    {"file": "src/plugin_examples/discovery_sweep.py", "owner": "LC", "action": "edit"},
    {"file": "src/plugin_examples/website_catalog/drift_detector.py", "owner": "LC", "action": "edit"},
    {"file": ".github/workflows/weekly-discovery.yml", "owner": "LC", "action": "new"},
    {"file": "src/plugin_examples/nuget_fetcher/fetcher.py", "owner": "LD", "action": "edit"},
    {"file": "src/plugin_examples/api_delta/delta_engine.py", "owner": "LD", "action": "edit"},
    {"file": "scripts/_wave25_batch_prove.py", "owner": "LE", "action": "new"},
    {"file": "pipeline/plugin-code-registry/family/*.yaml", "owner": "LE", "action": "edit-status-updates"},
    {"file": "src/plugin_examples/generator/code_generator.py", "owner": "LE", "action": "edit"},
    {"file": "pipeline/configs/families/*.yml (18 non-LowCode)", "owner": "LF", "action": "edit-add-fallback_strategy"},
    {"file": "src/plugin_examples/evidence_validator/rules/non_lowcode.py", "owner": "LF", "action": "edit-add-NLV15"},
    {"file": "src/plugin_examples/publisher/pr_builder.py", "owner": "LF", "action": "edit"},
    {"file": "src/plugin_examples/fixture_factory/shared_downstream_executor.py", "owner": "LF", "action": "confirm-schema"},
    {"file": "src/plugin_examples/healing_intelligence/loader.py", "owner": "LG", "action": "edit"},
    {"file": "workspace/verification/latest/healing-intelligence/scenario-difficulty-index.json", "owner": "LG", "action": "new"},
    {"file": "src/plugin_examples/runner.py", "owner": "LC+LD+LF+LG", "joint": True, "action": "multi-edit"},
    {"file": "scripts/_coordinator_base.py", "owner": "LH", "action": "new-already-created"},
    {"file": "scripts/new_sprint.py", "owner": "LH", "action": "new"},
    {"file": "scripts/templates/sprint_coordinator_template.py", "owner": "LH", "action": "new"},
    {"file": "src/plugin_examples/__main__.py", "owner": "LI", "action": "edit"},
    {"file": "pipeline/configs/stage-registry.yml", "owner": "LI", "action": "new-optional"},
]


def lane0_main() -> None:
    print("=== Wave 25 — Lane 0: Coordinator ===")
    coord = CoordinatorBase(SPRINT, REPORT_DIR, DATE)

    coord.setup_dirs(SUBDIRS)
    coord.write_taskcards(TASKS)
    coord.write_hard_stop_conditions(HARD_STOP_CONDITIONS)
    coord.write_repo_separation_manifest(APPROVED_PUBLICATION_REPOS, FIXTURE_SOURCE_REPOS)
    coord.write_shared_file_ownership(FILE_OWNERSHIP)
    coord.write_lane_ledger(LANES)
    coord.write_execution_board(LANES)

    coord.bulk_complete({
        "W25-L0-01": str(REPORT_DIR / "coordinator/hard-stop-conditions.json"),
        "W25-L0-02": str(REPORT_DIR / "coordinator/lane-ledger.json"),
    })

    import json
    tc = json.loads((REPORT_DIR / "taskcards/taskcards.json").read_text("utf-8"))
    print(f"[L0] Taskcards: {tc['complete']}/{len(tc['taskcards'])} COMPLETE")
    print(f"[L0] Hard-stop conditions: {len(HARD_STOP_CONDITIONS)}")
    print(f"[L0] Publication repos: {len(APPROVED_PUBLICATION_REPOS)}")
    print(f"[L0] Fixture source repos: {len(FIXTURE_SOURCE_REPOS)}")
    print(f"[L0] File ownership entries: {len(FILE_OWNERSHIP)}")
    print(f"[L0] Lane 0 COMPLETE")


if __name__ == "__main__":
    lane0_main()
