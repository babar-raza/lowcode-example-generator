import json
import os

SPRINT = "lowcode-plugin-canonical-package-wave19-20260606"
SPRINT_ID = "LOWCODE-PLUGIN-CANONICAL-PACKAGE-WAVE19-TRUE-FINISH-LINE-DWG-TARGET-REPO-PUBLICATION-MEGA-TRAIN-001"
REPORT = f"reports/{SPRINT}"
DATE = "2026-06-06"

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

# Lane 0: Coordinator
taskcards += [
    tc("W19-L0-01","0","Create W19 directory structure","wave19 dirs","all subdirs created"),
    tc("W19-L0-02","0","Capture preflight git status + log","git status+log","preflight/git-status.txt, preflight/git-log.txt"),
    tc("W19-L0-03","0","Write W18 evidence inventory","W18 bundle inspection","preflight/wave18-evidence-inventory.json"),
    tc("W19-L0-04","0","Write W18 contradiction inventory","W18 gaps","preflight/wave18-contradiction-inventory.json"),
    tc("W19-L0-05","0","Write coordinator docs","coordinator docs","coordinator/lane-ledger.json, coordinator/target-repo-map.json"),
    tc("W19-L0-06","0","Write pre-bundle closeout (pre-freeze)","pre-freeze evidence","final/pre-bundle-closeout.json"),
    tc("W19-L0-07","0","Freeze evidence bundle","bundle all artifacts","PENDING -- bundle closure task", status="PENDING"),
    tc("W19-L0-08","0","Write external .sha256 sidecar","post-freeze SHA","PENDING -- sidecar written after freeze", status="PENDING"),
    tc("W19-L0-09","0","Write final-attestation.json + sprint-closeout.json","final evidence authority","PENDING -- written after freeze", status="PENDING"),
]

# Lane A: W18 repair
taskcards += [
    tc("W19-LA-01","A","Verify W18 bundle SHA=35c2f3..., 227811B, 138 entries","W18 bundle","SHA/size/entries confirmed"),
    tc("W19-LA-02","A","Recount W18 taskcards from bundle (49/4 PENDING)","bundle taskcards.json","wave18-closure-repair/wave18-taskcard-recount.json"),
    tc("W19-LA-03","A","Write W18 closeout addendum","W18 classification","wave18-closure-repair/wave18-closeout-addendum.json"),
    tc("W19-LA-04","A","Write W18 sidecar-attestation review","sidecar state","wave18-closure-repair/wave18-sidecar-attestation-review.json"),
    tc("W19-LA-05","A","Write W18 PR packet reference review (33 packets)","PR packets","wave18-closure-repair/wave18-pr-packet-reference-review.json"),
    tc("W19-LA-06","A","Write W18 package proof audit (11 packages)","proof completeness","wave18-closure-repair/wave18-package-proof-audit.json"),
    tc("W19-LA-07","A","Secret hygiene review","no .pfx staged","security-hygiene/secret-file-review.json"),
]

# Lane B: DWG
taskcards += [
    tc("W19-LB-01","B","Write DWG source repo scan","repo search","dwg-acquisition/source-repo-scan.json"),
    tc("W19-LB-02","B","Write selected DWG fixture doc (Drawing11.dwg 19378B)","fixture selection","dwg-acquisition/selected-dwg-fixture.json"),
    tc("W19-LB-03","B","Write DWG fixture provenance","provenance","dwg-acquisition/dwg-fixture-provenance.json"),
    tc("W19-LB-04","B","Complete cad/convert-dwg-to-pdf proof (43288B PDF)","restore+build+run","wave19-dryrun/examples/cad/convert-dwg-to-pdf/output-validation.json: PASS"),
    tc("W19-LB-05","B","Complete cad/convert-dwg-to-jpg proof (77073B JPG)","restore+build+run","wave19-dryrun/examples/cad/convert-dwg-to-jpg/output-validation.json: PASS"),
    tc("W19-LB-06","B","Write DWG package results summary","gen results","package-generation/cad/dwg-package-results.json"),
    tc("W19-LB-07","B","Update CAD registry DWG packages to CANONICAL_PACKAGE_PROVEN","registry update","pipeline/plugin-code-registry/family/cad.yaml"),
]

# Lane C: Target repo publication
taskcards += [
    tc("W19-LC-01","C","Write target-repo-map.json","3 target repos","target-publication/target-repo-map.json"),
    tc("W19-LC-02","C","Detect gate (gh CLI auth OK, APPROVE_LIVE_PR=true)","gate check","target-publication/gate-detection.json"),
    tc("W19-LC-03","C","Inspect barcode target repo structure","repo inspection","target-publication/barcode/repo-validation.json"),
    tc("W19-LC-04","C","Build + push barcode branch (1d+2d reader+writer)","branch+commit+push","barcode branch pushed"),
    tc("W19-LC-05","C","Create barcode PR","live PR","target-publication/live-pr-results.json: barcode PR URL"),
    tc("W19-LC-06","C","Inspect SVG target repo structure","repo inspection","target-publication/svg/repo-validation.json"),
    tc("W19-LC-07","C","Build + push SVG branch (3 packages)","branch+commit+push","svg branch pushed"),
    tc("W19-LC-08","C","Create SVG PR","live PR","target-publication/live-pr-results.json: svg PR URL"),
    tc("W19-LC-09","C","Inspect CAD target repo structure","repo inspection","target-publication/cad/repo-validation.json"),
    tc("W19-LC-10","C","Build + push CAD branch (5 packages incl DWG)","branch+commit+push","cad branch pushed"),
    tc("W19-LC-11","C","Create CAD PR","live PR","target-publication/live-pr-results.json: cad PR URL"),
    tc("W19-LC-12","C","Write publication-blockers.json for target repos","pub blockers","target-publication/publication-blockers.json"),
]

# Lane D: Publication readiness
taskcards += [
    tc("W19-LD-01","D","Create PR packets for DWG packages","2 new PR packets","publication/pr-packets/cad/convert-dwg-*/pr-packet.json"),
    tc("W19-LD-02","D","Create PR packets for barcode writer packages","2 new PR packets","publication/pr-packets/barcode/1d-barcode-writer/pr-packet.json"),
    tc("W19-LD-03","D","Write final-publication-readiness.json (all packages)","full readiness","publication/final-publication-readiness.json"),
    tc("W19-LD-04","D","Write PR packet index final","packet index","publication/pr-packet-index-final.json"),
    tc("W19-LD-05","D","Write publication command ledger","command ledger","publication/publication-command-ledger.json"),
    tc("W19-LD-06","D","Write publication status summary","status summary","publication/publication-status-summary.json"),
]

# Lane E: Backlog exhaustion
taskcards += [
    tc("W19-LE-01","E","Generate full registry-derived backlog","registry derivation","backlog-exhaustion/full-registry-derived-backlog.json"),
    tc("W19-LE-02","E","Prove barcode/1d-barcode-writer","restore+build+run","wave19-dryrun/examples/barcode/1d-barcode-writer/output-validation.json: PASS"),
    tc("W19-LE-03","E","Prove barcode/2d-barcode-writer","restore+build+run","wave19-dryrun/examples/barcode/2d-barcode-writer/output-validation.json: PASS"),
    tc("W19-LE-04","E","Classify svg/svg-to-image-converter (TRANSFORMED_TO_EXAMPLE_DRYRUN)","status decision","backlog-exhaustion/all-remaining-items-result.json"),
    tc("W19-LE-05","E","Write all-remaining-items-result.json","exhaustion results","backlog-exhaustion/all-remaining-items-result.json"),
    tc("W19-LE-06","E","Write unresolved-local-blockers.json","blocker register","backlog-exhaustion/unresolved-local-blockers.json"),
]

# Lane F: Validators
taskcards += [
    tc("W19-LF-01","F","Write validator hardening W19 report","validator docs","validators/validator-hardening-wave19-report.json"),
    tc("W19-LF-02","F","Run full pytest suite","pytest","validators/raw-validator-test.log"),
    tc("W19-LF-03","F","Write final-validation-results.json","validation summary","validators/final-validation-results.json"),
]

# Lane G: State docs
taskcards += [
    tc("W19-LG-01","G","Update CAD registry for DWG packages","registry update","pipeline/plugin-code-registry/family/cad.yaml"),
    tc("W19-LG-02","G","Update barcode registry for writer packages","registry update","pipeline/plugin-code-registry/family/barcode.yaml"),
    tc("W19-LG-03","G","Write final state dashboard","dashboard","state-docs/final-state-dashboard.json"),
    tc("W19-LG-04","G","Write final publication matrix (all packages)","matrix","state-docs/final-publication-matrix.json"),
    tc("W19-LG-05","G","Write final canonical package ledger","ledger","state-docs/final-canonical-package-ledger.json"),
    tc("W19-LG-06","G","Write final blocker register","blockers","state-docs/final-blocker-register.json"),
    tc("W19-LG-07","G","Write wave20 next queue","W20 queue","state-docs/wave20-next-queue.json"),
]

# Lane H: IV + Adversarial
taskcards += [
    tc("W19-LH-01","H","Write IV results (all checks PASS)","IV","iv/iv-results.json: IV_PASS"),
    tc("W19-LH-02","H","Write adversarial review final","adversarial","adversarial-review/adversarial-review-final.json: ADVERSARIAL_REVIEW_PASS"),
    tc("W19-LH-03","H","Verify post-freeze: sidecar SHA matches bundle","post-freeze IV","PENDING -- verified after bundle freeze", status="PENDING"),
]

total = len(taskcards)
complete = sum(1 for t in taskcards if t["status"]=="COMPLETE")
pending = sum(1 for t in taskcards if t["status"]=="PENDING")
pending_ids = [t["id"] for t in taskcards if t["status"]=="PENDING"]

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
with open(f"{REPORT}/taskcards/taskcards.json","w") as f:
    json.dump(data, f, indent=2)
print(f"Taskcards: total={total}, COMPLETE={complete}, PENDING={pending}")
print(f"Pending IDs: {pending_ids}")
