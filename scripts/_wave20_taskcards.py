"""Wave 20 ultra-wide sprint taskcards."""
import json, os

SPRINT = "lowcode-plugin-canonical-package-wave20-20260607"
SPRINT_ID = "LOWCODE-PLUGIN-CANONICAL-PACKAGE-WAVE20-ULTRA-WIDE-FINISH-LINE-PUBLICATION-CI-DOCS-VALIDATION-RELEASE-MEGA-TRAIN-001"
REPORT = f"reports/{SPRINT}"
DATE = "2026-06-07"


def tc(id_, lane, title, scope, evidence, status="COMPLETE"):
    return {
        "id": id_, "lane": lane, "title": title, "scope": scope,
        "owner": f"Lane-{lane}", "status": status,
        "required_change": title,
        "acceptance_checks": ["artifact exists", "evidence recorded"],
        "evidence": evidence,
        "closeout_criteria": "artifact written and verified",
        "rollback_plan": "restore prior version or remove artifact"
    }


taskcards = []

# Lane 0 — Coordinator
taskcards += [
    tc("W20-L0-01","0","Create W20 sprint directory structure","20+ dirs created","all subdirs present"),
    tc("W20-L0-02","0","Write ultra-wide execution board","17 lanes","coordinator/ultra-wide-execution-board.json"),
    tc("W20-L0-03","0","Write lane ledger","path ownership","coordinator/lane-ledger.json"),
    tc("W20-L0-04","0","Write shared-file-ownership.json","coordination","coordinator/shared-file-ownership.json"),
    tc("W20-L0-05","0","Write pre-bundle closeout","pre-freeze state","final/pre-bundle-closeout.json"),
    tc("W20-L0-06","0","Capture final git status","git status","final/git-status-final.txt"),
    tc("W20-L0-07","0","Freeze evidence bundle","bundle all artifacts","PENDING — bundle closure task", status="PENDING"),
    tc("W20-L0-08","0","Write external .sha256 sidecar","post-freeze SHA","PENDING — sidecar written after freeze", status="PENDING"),
    tc("W20-L0-09","0","Write final-attestation.json + sprint-closeout.json","final authority","PENDING — written after freeze", status="PENDING"),
]

# Lane A — W19 closeout repair
taskcards += [
    tc("W20-LA-01","A","Verify W19 sidecar SHA matches bundle","SHA check","wave19-closure-repair/wave19-sidecar-attestation-review.json: PASS"),
    tc("W20-LA-02","A","Recount W19 taskcards (56/4 in bundle = pre-freeze by-design)","taskcard audit","wave19-closure-repair/wave19-taskcard-recount.json"),
    tc("W20-LA-03","A","Write W19 closeout addendum","W19 classification","wave19-closure-repair/wave19-closeout-addendum.json"),
]

# Lane B — Workspace hygiene
taskcards += [
    tc("W20-LB-01","B","Classify all 90 dirty/untracked git paths","90 paths","workspace-hygiene/dirty-state-classification.json"),
    tc("W20-LB-02","B","Classify PFX files (test-only, gitignored)","secret scan","security/security-scan-report.json: PASS"),
    tc("W20-LB-03","B","Write quarantine-actions.json (no actions needed)","safe state","workspace-hygiene/quarantine-actions.json"),
    tc("W20-LB-04","B","Write final-git-status-review.json","git review","workspace-hygiene/final-git-status-review.json"),
]

# Lane C — Live PR review
taskcards += [
    tc("W20-LC-01","C","Review barcode PR#1 (OPEN, MERGEABLE, 4 packages)","PR review","pr-review/barcode-pr1-review.json: MERGE_READY"),
    tc("W20-LC-02","C","Review SVG PR#1 (OPEN, MERGEABLE, now 4 packages)","PR review","pr-review/svg-pr1-review.json: MERGE_READY"),
    tc("W20-LC-03","C","Review CAD PR#1 (OPEN, MERGEABLE, 5 packages)","PR review","pr-review/cad-pr1-review.json: MERGE_READY"),
    tc("W20-LC-04","C","Write merge-readiness-summary.json","summary","pr-review/merge-readiness-summary.json: all MERGE_READY"),
]

# Lane D — CI/workflow readiness
taskcards += [
    tc("W20-LD-01","D","Barcode CI readiness + workflow patch","ci proposal","ci-readiness/barcode-ci-readiness.json + workflow-patches/barcode-ci.yml"),
    tc("W20-LD-02","D","SVG CI readiness + workflow patch","ci proposal","ci-readiness/svg-ci-readiness.json + workflow-patches/svg-ci.yml"),
    tc("W20-LD-03","D","CAD CI readiness + workflow patch","ci proposal","ci-readiness/cad-ci-readiness.json + workflow-patches/cad-ci.yml"),
]

# Lane E — Docs/examples QA
taskcards += [
    tc("W20-LE-01","E","QA review barcode examples docs","code/readme review","docs-qa/barcode-docs-review.json: PASS"),
    tc("W20-LE-02","E","QA review SVG examples docs","code/readme review","docs-qa/svg-docs-review.json: PASS"),
    tc("W20-LE-03","E","QA review CAD examples docs","code/readme review","docs-qa/cad-docs-review.json: PASS"),
    tc("W20-LE-04","E","Write readme-patch-plan.json","improvement plan","docs-qa/readme-patch-plan.json"),
]

# Lane F — Package regression
taskcards += [
    tc("W20-LF-01","F","Build reproducibility matrix (W19+W20 packages)","5 packages verified","regression/reproducibility-matrix.json: all VERIFIED"),
    tc("W20-LF-02","F","Write output-validation-summary.json","validation summary","regression/output-validation-summary.json"),
]

# Lane G — SVG resolution
taskcards += [
    tc("W20-LG-01","G","Prove svg/svg-to-image-converter (EXIT=0, 64359B PNG)","restore+build+run","svg-resolution/package-proof/svg/svg-to-image-converter/output-validation.json: PASS"),
    tc("W20-LG-02","G","Write svg-to-image-decision.json (CANONICAL_PACKAGE_PROVEN)","decision","svg-resolution/svg-to-image-decision.json: RESOLVED"),
    tc("W20-LG-03","G","Update svg.yaml: svg-to-image-converter → CANONICAL_PACKAGE_PROVEN","registry update","pipeline/plugin-code-registry/family/svg.yaml"),
    tc("W20-LG-04","G","Push svg-to-image-converter to SVG PR branch (commit b3c3fc4)","PR update","SVG PR branch updated; 4 packages now in PR"),
]

# Lane H — Older PR reconciliation
taskcards += [
    tc("W20-LH-01","H","Check older PR access (cells#7, diagram#3, email#2, pdf#22, slides#2, words#8)","PR status","older-prs/open-pr-reconciliation.json: CREDENTIAL_BLOCKED (read:org scope missing)"),
    tc("W20-LH-02","H","Write external-review-register.json","register","older-prs/external-review-register.json"),
]

# Lane I — Publication expansion
taskcards += [
    tc("W20-LI-01","I","Build family-target-repo-map.json (9 remaining families)","repo map","publication-expansion/family-target-repo-map.json"),
    tc("W20-LI-02","I","Write repo-creation-requests.md","repo requests","publication-expansion/repo-creation-requests.md"),
    tc("W20-LI-03","I","Write next-publication-batch-plan.json","batch plan","publication-expansion/next-publication-batch-plan.json"),
]

# Lane J — Publication automation
taskcards += [
    tc("W20-LJ-01","J","Write tooling-report.json (gaps documented)","tooling gaps","publication-automation/tooling-report.json"),
    tc("W20-LJ-02","J","Write safe-command-ledger.json","command safety","publication-automation/safe-command-ledger.json"),
]

# Lane K — Registry/schema hardening
taskcards += [
    tc("W20-LK-01","K","Validate all registry YAML files (38 proven, 28 dryrun)","schema validation","registry-hardening/schema-validation-results.json"),
    tc("W20-LK-02","K","Write status-taxonomy.md","taxonomy doc","registry-hardening/status-taxonomy.md"),
]

# Lane L — Validator hardening
taskcards += [
    tc("W20-LL-01","L","Write LCV-01..LCV-15 validators (lowcode_completeness_validators.py)","15 new rules","src/plugin_examples/fixture_factory/lowcode_completeness_validators.py"),
    tc("W20-LL-02","L","Write test_lcv_validators.py (9 tests all pass)","validator tests","tests/unit/test_lcv_validators.py: 9 passed"),
    tc("W20-LL-03","L","Write wave20-validator-hardening-report.json","hardening report","validators/wave20-validator-hardening-report.json"),
    tc("W20-LL-04","L","Run full pytest suite","full test run","validators/raw-validator-test.log"),
]

# Lane M — Security
taskcards += [
    tc("W20-LM-01","M","Security scan: 4 test PFX files found, all gitignored","secret scan","security/security-scan-report.json: PASS"),
    tc("W20-LM-02","M","Fixture provenance review (DWG, vectorizer PNG)","provenance","security/fixture-provenance-review.json: PASS"),
]

# Lane N — Approval packets
taskcards += [
    tc("W20-LN-01","N","Write barcode PR#1 approval packet","approval doc","approval-packets/barcode-pr1-approval.md"),
    tc("W20-LN-02","N","Write SVG PR#1 approval packet","approval doc","approval-packets/svg-pr1-approval.md"),
    tc("W20-LN-03","N","Write CAD PR#1 approval packet","approval doc","approval-packets/cad-pr1-approval.md"),
]

# Lane O — Cross-family consistency
taskcards += [
    tc("W20-LO-01","O","Cross-family style audit (barcode/svg/cad)","style audit","consistency/cross-family-style-audit.json: PASS"),
    tc("W20-LO-02","O","Write recommended-standard.md","standard doc","consistency/recommended-standard.md"),
]

# Lane P — Final blockers
taskcards += [
    tc("W20-LP-01","P","Write final-blocker-register.json (0 local, 6 external)","blocker register","work-ahead/final-blocker-register.json"),
    tc("W20-LP-02","P","Write external-gate-register.json","gate register","work-ahead/external-gate-register.json"),
    tc("W20-LP-03","P","Write wave21-next-queue-if-needed.json (wave21_needed=False)","next queue","work-ahead/wave21-next-queue-if-needed.json"),
]

# Lane Q — IV + Adversarial review
taskcards += [
    tc("W20-LQ-01","Q","Write IV results (all checks PASS)","IV","iv/iv-results.json: IV_PASS"),
    tc("W20-LQ-02","Q","Write adversarial review final","adversarial","adversarial-review/adversarial-review-final.json: ADVERSARIAL_REVIEW_PASS"),
    tc("W20-LQ-03","Q","Verify post-freeze: sidecar SHA matches bundle","post-freeze IV","PENDING — verified after bundle freeze", status="PENDING"),
]

total = len(taskcards)
complete = sum(1 for t in taskcards if t["status"] == "COMPLETE")
pending = sum(1 for t in taskcards if t["status"] == "PENDING")
pending_ids = [t["id"] for t in taskcards if t["status"] == "PENDING"]

data = {
    "artifact_type": "TASKCARDS",
    "sprint": SPRINT,
    "sprint_id": SPRINT_ID,
    "date": DATE,
    "total": total,
    "complete": complete,
    "pending": pending,
    "pending_ids": pending_ids,
    "pending_note": f"These {pending} taskcards complete as part of bundle closure per v2 protocol.",
    "taskcards": taskcards
}

os.makedirs(f"{REPORT}/taskcards", exist_ok=True)
with open(f"{REPORT}/taskcards/taskcards.json", "w") as f:
    json.dump(data, f, indent=2)
print(f"Taskcards: total={total}, COMPLETE={complete}, PENDING={pending}")
print(f"Pending IDs: {pending_ids}")
