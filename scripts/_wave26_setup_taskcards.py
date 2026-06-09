"""Wave 26 taskcard, lane-ledger, execution-board generator."""
import json
from datetime import datetime, timezone

now = datetime.now(timezone.utc).isoformat(timespec="seconds")
sprint = "lowcode-plugin-production-heal-wave26-20260609"
report_root = f"reports/{sprint}"

lanes = {
    "L0": {"desc": "Coordinator, evidence authority repair, W25 correction, taskcards", "status": "IN_PROGRESS"},
    "LA": {"desc": "Source evidence materialization - diffs, snapshots, commit ledger", "status": "PENDING"},
    "LB": {"desc": "DRYRUN scaffold generation for 28 packages", "status": "PENDING"},
    "LC": {"desc": "DRYRUN build/prove - restore, build, run, output validation", "status": "PENDING"},
    "LD": {"desc": "Fixture fetch/live cache validation with provenance", "status": "PENDING"},
    "LE": {"desc": "Discovery freshness and drift validation", "status": "PENDING"},
    "LF": {"desc": "Provenance/version-drift/NuGet SHA validation", "status": "PENDING"},
    "LG": {"desc": "Non-LowCode real E2E runner dry-runs", "status": "PENDING"},
    "LH": {"desc": "PR lifecycle live merge gate execution", "status": "PENDING"},
    "LI": {"desc": "Raw test execution with full logs", "status": "PENDING"},
    "LJ": {"desc": "State truth repair - accurate counts, blockers", "status": "PENDING"},
    "LK": {"desc": "Security and provenance scan", "status": "PENDING"},
    "LL": {"desc": "Independent verification and adversarial review", "status": "PENDING"},
    "LZ": {"desc": "Bundle freeze, external sidecar, final attestation", "status": "PENDING"},
}

tasks = []
tc_id = [0]

def tc(lane, desc, scope, owned_paths, forbidden_paths, required_change, acceptance_checks, evidence_path, rollback, closeout):
    tc_id[0] += 1
    return {
        "id": f"W26-{lane}-{tc_id[0]:02d}",
        "lane": lane,
        "description": desc,
        "scope": scope,
        "owner": "agent",
        "owned_paths": owned_paths,
        "forbidden_paths": forbidden_paths,
        "required_change": required_change,
        "acceptance_checks": acceptance_checks,
        "evidence_path": evidence_path,
        "rollback_plan": rollback,
        "closeout_criteria": closeout,
        "status": "PENDING",
        "blocker_class": None,
        "completed_at": None,
    }

rr = report_root

# L0 - Coordinator
tasks.append(tc("L0", "W25 addendum and contradiction analysis", "W25 correction", [f"{rr}/wave25-correction/"], [], "Produce addendum + contradiction JSON", ["Files exist, valid JSON, contradictions enumerated"], f"{rr}/wave25-correction/wave25-addendum.json", "Delete files", "Addendum written with all 8 contradictions"))
tasks.append(tc("L0", "W26 taskcards created with full metadata", "Coordinator", [f"{rr}/taskcards/"], [], "Create taskcards.json with scope/owner/evidence/rollback per task", ["All tasks have non-null evidence_path at closeout"], f"{rr}/taskcards/taskcards.json", "Delete file", "All taskcards have evidence_path, status, closeout"))
tasks.append(tc("L0", "Lane-ledger maintained and updated as lanes close", "Coordinator", [f"{rr}/coordinator/"], [], "Update lane-ledger.json as each lane completes", ["Lane-ledger agrees with taskcards"], f"{rr}/coordinator/lane-ledger.json", "Delete file", "All lanes reflect actual completion state"))
tasks.append(tc("L0", "Execution-board maintained", "Coordinator", [f"{rr}/coordinator/"], [], "Update execution-board.json", ["Agrees with lane-ledger"], f"{rr}/coordinator/execution-board.json", "Delete file", "lanes_complete matches reality"))
tasks.append(tc("L0", "Closure consistency validator", "Validator", [f"{rr}/validators/"], [], "Run validator that fails on tc/ledger disagreement, null evidence, missing sidecar", ["Validator passes"], f"{rr}/validators/closure-consistency-validator-results.json", "N/A", "Validator PASS"))

# LA - Source evidence
tasks.append(tc("LA", "Changed-file manifest for W25+W26", "Source evidence", [f"{rr}/source-evidence/"], [], "git log/diff to enumerate all changed files with commit SHAs", ["Manifest exists, lists all modified files"], f"{rr}/source-evidence/changed-files-manifest.json", "Delete file", "Manifest covers all claimed changes"))
tasks.append(tc("LA", "Source diff patch", "Source evidence", [f"{rr}/source-evidence/"], [], "git diff patch for key source files", ["Patch file exists"], f"{rr}/source-evidence/source-diff.patch", "Delete file", "Diff captures implementation"))
tasks.append(tc("LA", "Important source snapshots", "Source evidence", [f"{rr}/source-evidence/important-source-snapshots/"], [], "Copy key source files to evidence", ["Snapshots exist for critical files"], f"{rr}/source-evidence/important-source-snapshots/", "Delete dir", "All listed files have snapshots"))
tasks.append(tc("LA", "Commit ledger", "Source evidence", [f"{rr}/source-evidence/"], [], "Record commit SHAs, messages, timestamps", ["Valid JSON"], f"{rr}/source-evidence/commit-ledger.json", "Delete file", "All W25+W26 commits listed"))

# LB - Scaffold generation
tasks.append(tc("LB", "Re-derive DRYRUN backlog from registry", "Generation", [f"{rr}/generation/"], [], "Scan registry YAMLs for TRANSFORMED_TO_EXAMPLE_DRYRUN", ["Backlog matches registry"], f"{rr}/generation/dryrun-backlog-wave26.json", "Delete file", "Backlog derived at runtime"))
tasks.append(tc("LB", "Generate scaffolds for all 28 DRYRUN packages", "Generation", [f"{rr}/generation/"], [], "Create Program.cs, csproj, README, manifest, expected-output per package", ["scaffold-generation-matrix.json with per-package status"], f"{rr}/generation/scaffold-generation-matrix.json", "Delete generated dirs", "Each package has SCAFFOLD_GENERATED or classified blocker"))
tasks.append(tc("LB", "Scaffold files index", "Generation", [f"{rr}/generation/"], [], "Index all generated files", ["Valid JSON"], f"{rr}/generation/scaffold-files-index.json", "Delete file", "Index matches disk"))
tasks.append(tc("LB", "Scaffold blockers documentation", "Generation", [f"{rr}/generation/"], [], "Document why any package could not be scaffolded", ["Valid JSON"], f"{rr}/generation/scaffold-blockers.json", "Delete file", "Each blocked package has reason"))

# LC - Build/prove
tasks.append(tc("LC", "Build matrix for scaffolded packages", "Proving", [f"{rr}/generation/"], [], "dotnet restore/build/run + output validation", ["build-matrix-wave26.json exists"], f"{rr}/generation/build-matrix-wave26.json", "Delete file", "Per-package result with exact blocker"))
tasks.append(tc("LC", "Registry transition ledger", "Proving", [f"{rr}/generation/"], [], "Update registry for packages that pass all checks", ["Ledger matches build outcomes"], f"{rr}/generation/registry-transition-ledger.json", "Delete file", "Only proven packages promoted"))
tasks.append(tc("LC", "Per-package proof folders", "Proving", [f"{rr}/generation/package-proofs/"], [], "Restore/build/run logs per package", ["Logs exist for each attempted package"], f"{rr}/generation/package-proofs/", "Delete dirs", "At least one package proven or all blocked with reason"))
tasks.append(tc("LC", "Blockers by package", "Proving", [f"{rr}/generation/"], [], "Classify each failed package", ["Valid JSON"], f"{rr}/generation/blockers-by-package.json", "Delete file", "Each failure has exact blocker class"))

# LD - Fixture fetch
tasks.append(tc("LD", "Live fixture fetch for barcode/cad/svg", "Fixtures", [f"{rr}/fixtures/"], [], "Run fixture_fetcher for 3 families", ["Results JSON exists"], f"{rr}/fixtures/live-fetch-results.json", "Delete file", "At least one real fetch or EXTERNAL_NETWORK_BLOCKED"))
tasks.append(tc("LD", "Cache hit validation", "Fixtures", [f"{rr}/fixtures/"], [], "Re-run fetcher to prove cache hit", ["Cache results JSON"], f"{rr}/fixtures/cache-hit-results.json", "Delete file", "Cache hit count > 0 or network blocked"))
tasks.append(tc("LD", "Fixture provenance sidecars", "Fixtures", [f"{rr}/fixtures/provenance-sidecars/"], [], "Provenance sidecar for each fetched file", ["Sidecars exist"], f"{rr}/fixtures/provenance-sidecars/", "Delete dir", "Each fetched file has provenance"))

# LE - Discovery
tasks.append(tc("LE", "Discovery evidence with freshness metadata", "Discovery", [f"{rr}/discovery/"], [], "Validate current discovery evidence freshness", ["discovery-evidence.json exists"], f"{rr}/discovery/discovery-evidence.json", "Delete file", "validated_at and expires_at present"))
tasks.append(tc("LE", "Drift report", "Discovery", [f"{rr}/discovery/"], [], "Compare current vs prior discovery", ["drift-report.json exists"], f"{rr}/discovery/drift-report.json", "Delete file", "Drift analysis complete"))
tasks.append(tc("LE", "Freshness gate test results", "Discovery", [f"{rr}/discovery/"], [], "Test all 3 modes", ["Gate results JSON"], f"{rr}/discovery/freshness-gate-results.json", "Delete file", "publication mode blocks stale"))

# LF - Provenance
tasks.append(tc("LF", "Version drift check results", "Provenance", [f"{rr}/provenance/"], [], "Run version drift checker", ["Results JSON"], f"{rr}/provenance/version-drift-results.json", "Delete file", "Drift status determined"))
tasks.append(tc("LF", "NuGet SHA manifest", "Provenance", [f"{rr}/provenance/"], [], "Generate/validate NuGet SHA manifest", ["Manifest JSON"], f"{rr}/provenance/nuget-sha-manifest.json", "Delete file", "SHA-256 used, not ETag"))
tasks.append(tc("LF", "API delta steering results", "Provenance", [f"{rr}/provenance/"], [], "Test auto-steering candidate flow", ["Results JSON"], f"{rr}/provenance/api-delta-steering-results.json", "Delete file", "CANDIDATE only, never CONFIRMED"))

# LG - Non-LowCode E2E
tasks.append(tc("LG", "Non-LowCode E2E barcode dry-run", "E2E", [f"{rr}/nonlowcode-e2e/barcode-run/"], [], "Run pipeline dry-run for barcode", ["Run evidence exists"], f"{rr}/nonlowcode-e2e/barcode-run/", "Delete dir", "Pipeline stages executed or blocked with reason"))
tasks.append(tc("LG", "Non-LowCode E2E svg dry-run", "E2E", [f"{rr}/nonlowcode-e2e/svg-run/"], [], "Run pipeline dry-run for svg", ["Run evidence exists"], f"{rr}/nonlowcode-e2e/svg-run/", "Delete dir", "Pipeline stages executed or blocked"))
tasks.append(tc("LG", "Non-LowCode E2E cad dry-run", "E2E", [f"{rr}/nonlowcode-e2e/cad-run/"], [], "Run pipeline dry-run for cad", ["Run evidence exists"], f"{rr}/nonlowcode-e2e/cad-run/", "Delete dir", "Pipeline stages executed or blocked"))
tasks.append(tc("LG", "E2E summary", "E2E", [f"{rr}/nonlowcode-e2e/"], [], "Summarize all E2E runs", ["Summary JSON"], f"{rr}/nonlowcode-e2e/e2e-summary.json", "Delete file", "All 3 families attempted"))

# LH - PR lifecycle
tasks.append(tc("LH", "Live PR state check", "PR lifecycle", [f"{rr}/pr-lifecycle/"], [], "Check 3 plugin PRs via gh api", ["live-pr-state.json"], f"{rr}/pr-lifecycle/live-pr-state.json", "Delete file", "All 3 PRs checked"))
tasks.append(tc("LH", "AMG gate evaluation", "PR lifecycle", [f"{rr}/pr-lifecycle/"], [], "Evaluate merge gates", ["amg-results.json"], f"{rr}/pr-lifecycle/amg-results.json", "Delete file", "Gate results recorded"))
tasks.append(tc("LH", "Merge execution or gate classification", "PR lifecycle", [f"{rr}/pr-lifecycle/"], [], "Merge if gate passes, or classify as EXECUTION_ENV_GATE_NOT_SET", ["merge-results.json"], f"{rr}/pr-lifecycle/merge-results.json", "Delete file", "Each PR has final state"))

# LI - Testing
tasks.append(tc("LI", "Full pytest raw log", "Testing", [f"{rr}/verification/raw-test-logs/"], [], "Run full pytest with stdout captured", ["Raw log file exists"], f"{rr}/verification/raw-test-logs/full-pytest.log", "Delete file", "Raw log with pass/fail counts"))
tasks.append(tc("LI", "Test command ledger", "Testing", [f"{rr}/verification/"], [], "Record command, env, exit code, duration", ["Ledger JSON"], f"{rr}/verification/test-command-ledger.json", "Delete file", "All test runs documented"))

# LJ - State truth
tasks.append(tc("LJ", "Accurate state-truth with real blockers", "State truth", [f"{rr}/state-truth/"], [], "Recompute all counts from actual evidence", ["state-truth JSON"], f"{rr}/state-truth/state-truth-wave26.json", "Delete file", "Counts match evidence, blockers listed"))
tasks.append(tc("LJ", "Final blocker register", "State truth", [f"{rr}/state-truth/"], [], "List all local and external blockers", ["Blocker register JSON"], f"{rr}/state-truth/final-blocker-register.json", "Delete file", "No false local_blockers=[]"))

# LK - Security
tasks.append(tc("LK", "Security scan", "Security", [f"{rr}/security/"], [], "Scan for secrets, keys, certificates", ["Scan report JSON"], f"{rr}/security/security-scan-report.json", "Delete file", "No secrets found or violations documented"))
tasks.append(tc("LK", "Binary fixture provenance review", "Security", [f"{rr}/security/"], [], "Verify fixture provenance", ["Review JSON"], f"{rr}/security/binary-fixture-provenance-review.json", "Delete file", "All binary fixtures have provenance"))

# LL - Verification
tasks.append(tc("LL", "IV results", "Verification", [f"{rr}/iv/"], [], "Run IV checks", ["iv-results.json"], f"{rr}/iv/iv-results.json", "Delete file", "All checks pass or documented"))
tasks.append(tc("LL", "Adversarial review", "Verification", [f"{rr}/adversarial-review/"], [], "Run AR checks", ["AR JSON"], f"{rr}/adversarial-review/adversarial-review-final.json", "Delete file", "All AR checks pass or documented"))
tasks.append(tc("LL", "Final claim audit", "Verification", [f"{rr}/verification/"], [], "Audit all final claims against evidence", ["Audit JSON"], f"{rr}/verification/final-claim-audit.json", "Delete file", "No false claims"))

# LZ - Bundle
tasks.append(tc("LZ", "Pre-bundle closeout", "Bundle", [f"{rr}/final/"], [], "Write pre-bundle-closeout.json", ["Closeout JSON exists"], f"{rr}/final/pre-bundle-closeout.json", "Delete file", "All lanes documented"))
tasks.append(tc("LZ", "Final git status", "Bundle", [f"{rr}/final/"], [], "Capture git status", ["git-status-final.txt exists"], f"{rr}/final/git-status-final.txt", "Delete file", "Git state classified"))
tasks.append(tc("LZ", "Bundle ZIP frozen", "Bundle", [".local/evidence-bundles/"], [], "Create ZIP from reports dir", ["ZIP exists"], ".local/evidence-bundles/lowcode-plugin-production-heal-wave26-20260609.zip", "Delete ZIP", "ZIP created"))
tasks.append(tc("LZ", "External .sha256 sidecar", "Bundle", [".local/evidence-bundles/"], [], "Compute SHA after freeze, write sidecar", ["Sidecar file exists"], ".local/evidence-bundles/lowcode-plugin-production-heal-wave26-20260609.sha256", "Delete sidecar", "SHA matches bundle"))
tasks.append(tc("LZ", "Final-attestation.json", "Bundle", [".local/evidence-bundles/"], [], "Write attestation with SHA, size, entry count", ["Attestation exists"], ".local/evidence-bundles/lowcode-plugin-production-heal-wave26-20260609-final-attestation.json", "Delete file", "SHA/size/entries match"))
tasks.append(tc("LZ", "Post-freeze validation", "Bundle", [f"{rr}/validators/"], [], "Verify sidecar SHA matches bundle", ["Validation passes"], f"{rr}/validators/closure-consistency-validator-results.json", "N/A", "SHA verified"))

# Write files
taskcards_doc = {
    "sprint": sprint,
    "date": "2026-06-09",
    "generated_at": now,
    "complete": 0,
    "pending": len(tasks),
    "blocked": 0,
    "taskcards": tasks,
}

with open(f"{report_root}/taskcards/taskcards.json", "w", encoding="utf-8") as f:
    json.dump(taskcards_doc, f, indent=2)

lane_ledger = {
    "sprint": sprint,
    "date": "2026-06-09",
    "generated_at": now,
    "lanes": {k: v for k, v in lanes.items()},
}
with open(f"{report_root}/coordinator/lane-ledger.json", "w", encoding="utf-8") as f:
    json.dump(lane_ledger, f, indent=2)

exec_board = {
    "sprint": sprint,
    "date": "2026-06-09",
    "generated_at": now,
    "total_lanes": len(lanes),
    "lanes_complete": 0,
    "lanes_in_progress": 1,
    "lanes_pending": len(lanes) - 1,
    "lanes": {k: v for k, v in lanes.items()},
}
with open(f"{report_root}/coordinator/execution-board.json", "w", encoding="utf-8") as f:
    json.dump(exec_board, f, indent=2)

print(f"Taskcards: {len(tasks)}")
print(f"Lanes: {len(lanes)}")
print("Files written: taskcards.json, lane-ledger.json, execution-board.json")
