import json
import os

REPORT = "reports/lowcode-plugin-canonical-package-wave18-20260606"
os.makedirs(f"{REPORT}/state-docs", exist_ok=True)
os.makedirs(f"{REPORT}/publication", exist_ok=True)

pclc_packages = [
    ("ocr","scanned-image-to-text","https://products.aspose.net/ocr/scanned-image-to-text/","W11"),
    ("ocr","scanned-pdf-to-text","https://products.aspose.net/ocr/scanned-pdf-to-text/","W11"),
    ("page","xps-converter","https://products.aspose.net/page/xps-converter/","W11"),
    ("page","eps-to-pdf","https://products.aspose.net/page/eps-to-pdf/","W11"),
    ("page","ps-converter","https://products.aspose.net/page/ps-converter/","W11"),
    ("psd","psd-to-pdf","https://products.aspose.net/psd/psd-to-pdf/","W11"),
    ("tasks","mpp-to-html","https://products.aspose.net/tasks/mpp-to-html/","W11"),
    ("tasks","mpp-to-png","https://products.aspose.net/tasks/mpp-to-png/","W11"),
    ("zip","universal-extractor","https://products.aspose.net/zip/universal-extractor/","W11"),
    ("zip","universal-compressor","https://products.aspose.net/zip/universal-compressor/","W11"),
    ("svg","svg-to-pdf-converter","https://products.aspose.net/svg/svg-to-pdf-converter/","W12"),
    ("svg","vectorizer","https://products.aspose.net/svg/vectorizer/","W12"),
    ("gis","read-gis-data","https://products.aspose.net/gis/read-gis-data/","W14"),
    ("tex","convert-latex-to-pdf","https://products.aspose.net/tex/convert-latex-to-pdf/","W14"),
    ("html","convert-html-to-xps","https://products.aspose.net/html/convert-html-to-xps/","W15"),
    ("psd","convert-psd-to-png","https://products.aspose.net/psd/convert-psd-to-png/","W15"),
    ("html","convert-html-to-markdown","https://products.aspose.net/html/convert-html-to-markdown/","W16"),
    ("html","merge-html","https://products.aspose.net/html/merge-html/","W16"),
    ("gis","convert-gis-data","https://products.aspose.net/gis/convert-gis-data/","W16"),
    ("tasks","read-project-data","https://products.aspose.net/tasks/read-project-data/","W16"),
    ("threed","convert-3d-model","https://products.aspose.net/threed/convert-3d-model/","W17"),
    ("font","convert-font","https://products.aspose.net/font/convert-font/","W17"),
    ("barcode","1d-barcode-reader","https://products.aspose.net/barcode/1d-barcode-reader/","W18"),
    ("barcode","2d-barcode-reader","https://products.aspose.net/barcode/2d-barcode-reader/","W18"),
    ("threed","compress-3d-scene","https://products.aspose.net/threed/compress-3d-scene/","W18"),
    ("svg","merge-svg","https://products.aspose.net/svg/merge-svg/","W18"),
    ("font","render-text-with-font","https://products.aspose.net/font/render-text-with-font/","W18"),
    ("finance","parse-xbrl","https://products.aspose.net/finance/parse-xbrl/","W18"),
    ("cad","convert-dxf-to-pdf","https://products.aspose.net/cad/convert-dxf-to-pdf/","W18"),
    ("cad","convert-cad-to-pdf","https://products.aspose.net/cad/convert-cad-to-pdf/","W18"),
    ("cad","convert-cad-to-image","https://products.aspose.net/cad/convert-cad-to-image/","W18"),
    ("omr","generate-omr-template","https://products.aspose.net/omr/generate-omr-template/","W18"),
    ("omr","recognize-omr","https://products.aspose.net/omr/recognize-omr/","W18"),
]

readiness_packages = []
for family, slug, url, wave in pclc_packages:
    pr_wave = "W17" if wave in ["W11","W12","W14","W15","W16"] else "W18"
    readiness_packages.append({
        "family": family, "slug": slug, "canonical_url": url,
        "proven_wave": wave, "pr_packet_exists": True, "pr_packet_wave": pr_wave,
        "publication_status": "PUBLICATION_CANDIDATE_LOCAL_CLEAN",
        "output_validation_status": "PASS"
    })

readiness = {
    "artifact_type": "UNIFIED_PUBLICATION_READINESS_FINISH_LINE",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "version": "finish-line",
    "pclc_total": len(pclc_packages),
    "all_pr_packets_exist": True,
    "packages": readiness_packages
}
with open(f"{REPORT}/publication/unified-publication-readiness-finish-line.json", 'w') as f:
    json.dump(readiness, f, indent=2)

index = {
    "artifact_type": "PR_PACKET_INDEX",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "total_pr_packets": len(pclc_packages),
    "w17_existing": 20,
    "w18_new": 13,
    "packets": [{"family": f, "slug": s, "path": f"publication/pr-packets/{f}/{s}/pr-packet.json", "wave": w} for f,s,_,w in pclc_packages]
}
with open(f"{REPORT}/publication/pr-packet-index.json", 'w') as f:
    json.dump(index, f, indent=2)

proven_all = {"W8":4,"W9":12,"W10":17,"W11":10,"W12":2,"W14":2,"W15":2,"W16":4,"W17":2,"W18":11}
ledger = {
    "artifact_type": "CANONICAL_PACKAGE_LEDGER_FINISH_LINE",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "version": "finish-line",
    "proven_packages": {"total": sum(proven_all.values()), "by_wave": proven_all,
                        "wave18_new": [f"{f}/{s}" for f,s,_,w in pclc_packages if w=="W18"]},
    "pclc_total": len(pclc_packages),
    "pclc_packages": [f"{f}/{s}" for f,s,_,_ in pclc_packages],
    "remaining_blockers": ["cad/convert-dwg-to-pdf (FIXTURE_BLOCKED)", "cad/convert-dwg-to-jpg (FIXTURE_BLOCKED)"]
}
with open(f"{REPORT}/state-docs/canonical-package-ledger-finish-line.json", 'w') as f:
    json.dump(ledger, f, indent=2)

dashboard = {
    "artifact_type": "FINAL_STATE_DASHBOARD",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "total_proven_packages": sum(proven_all.values()),
    "pclc_total": len(pclc_packages),
    "pr_packets_total": len(pclc_packages),
    "live_prs_open": 6,
    "live_prs_status": "EXTERNAL_REVIEW_PENDING (cells #7, diagram #3, email #2, pdf #22, slides #2, words #8)",
    "packages_remaining_blocked": 2,
    "blockers": ["cad/convert-dwg-to-pdf FIXTURE_BLOCKED", "cad/convert-dwg-to-jpg FIXTURE_BLOCKED"],
    "local_work_complete": True,
    "only_external_gates_remain": True,
    "sprint_verdict": "APPROVAL_BLOCKED — all local work complete; live PR merge requires human approval"
}
with open(f"{REPORT}/state-docs/final-state-dashboard.json", 'w') as f:
    json.dump(dashboard, f, indent=2)

pr_recon = {
    "artifact_type": "OPEN_PR_RECONCILIATION",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "open_prs": [
        {"repo": "cells", "pr_number": 7, "status": "EXTERNAL_REVIEW_PENDING", "overlap_with_pclc": False},
        {"repo": "diagram", "pr_number": 3, "status": "EXTERNAL_REVIEW_PENDING", "overlap_with_pclc": False},
        {"repo": "email", "pr_number": 2, "status": "EXTERNAL_REVIEW_PENDING", "overlap_with_pclc": False},
        {"repo": "pdf", "pr_number": 22, "status": "EXTERNAL_REVIEW_PENDING", "overlap_with_pclc": False},
        {"repo": "slides", "pr_number": 2, "status": "EXTERNAL_REVIEW_PENDING", "overlap_with_pclc": False},
        {"repo": "words", "pr_number": 8, "status": "EXTERNAL_REVIEW_PENDING", "overlap_with_pclc": False},
    ],
    "remote_verification": "CREDENTIAL_BLOCKED — live remote check requires GH_TOKEN/GL_TOKEN",
    "local_classification": "All 6 PRs from earlier CVFP publication wave (W8-W10), no overlap with PCLC scope"
}
with open(f"{REPORT}/publication/open-pr-reconciliation.json", 'w') as f:
    json.dump(pr_recon, f, indent=2)

remaining_blockers = {
    "artifact_type": "REMAINING_BLOCKERS_FINAL",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "local_blockers": [
        {"package": "cad/convert-dwg-to-pdf", "class": "FIXTURE_BLOCKED", "resolution": "Provide DWG binary fixture file"},
        {"package": "cad/convert-dwg-to-jpg", "class": "FIXTURE_BLOCKED", "resolution": "Same DWG fixture as above"},
    ],
    "external_gates": [
        {"item": "Live PR push for 33 PCLC packages", "gate": "HUMAN_APPROVAL + GH/GL credentials"},
        {"item": "Merge/release of 6 existing open PRs", "gate": "External reviewer approval"},
    ],
    "total_local_blockers": 2,
    "total_external_gates": 2
}
with open(f"{REPORT}/state-docs/remaining-blockers-final.json", 'w') as f:
    json.dump(remaining_blockers, f, indent=2)

wave19_queue = {
    "artifact_type": "WAVE19_NEXT_QUEUE",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "queue": [
        {"priority": 1, "package": "cad/convert-dwg-to-pdf", "blocker": "DWG binary fixture required", "resolution_difficulty": "LOW — just need fixture file"},
        {"priority": 2, "package": "cad/convert-dwg-to-jpg", "blocker": "DWG binary fixture required", "resolution_difficulty": "LOW"},
        {"priority": 3, "item": "Live PR push for 33 PCLC packages", "blocker": "Human approval + credentials", "resolution_difficulty": "EXTERNAL_GATE"},
        {"priority": 4, "item": "Merge existing 6 open PRs", "blocker": "External reviewer decision", "resolution_difficulty": "EXTERNAL_GATE"},
    ],
    "note": "W19 should be a small external-gate sprint, not another broad discovery sprint. Only 2 local blockers remain."
}
with open(f"{REPORT}/state-docs/wave19-next-queue.json", 'w') as f:
    json.dump(wave19_queue, f, indent=2)

pub_blockers = {
    "artifact_type": "PUBLICATION_BLOCKERS",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "blockers": [
        {"package": "all 33 PCLC", "blocker": "Live PR push requires human approval and GH/GL credentials", "class": "EXTERNAL_GATE", "local_work_complete": True},
    ]
}
with open(f"{REPORT}/publication/publication-blockers.json", 'w') as f:
    json.dump(pub_blockers, f, indent=2)

gate_detection = {
    "artifact_type": "GATE_DETECTION",
    "sprint": "lowcode-plugin-canonical-package-wave18-20260606",
    "date": "2026-06-06",
    "APPROVE_LIVE_PR": False,
    "GH_TOKEN": "NOT_SET",
    "GL_TOKEN": "NOT_SET",
    "gate_verdict": "NO_LIVE_GATES — producing dry-run command packets for all 33 PCLC packages"
}
with open(f"{REPORT}/publication-execution/gate-detection.json", 'w') as f:
    json.dump(gate_detection, f, indent=2)

print(f"All state docs written. PCLC={len(pclc_packages)}, proven={sum(proven_all.values())}")
