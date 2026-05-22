# Sprint 39 — Overlap Control

## File Overlap Matrix

| File | Lane 0 | Lane A | Lane B | Lane C | Lane D | Lane E | Lane F |
|------|--------|--------|--------|--------|--------|--------|--------|
| denominators/email.json | COMMIT | - | - | - | - | READ | READ |
| denominators/slides.json | COMMIT | - | - | - | - | READ | READ |
| denominators/words.json | COMMIT | - | - | - | - | READ | READ |
| denominators/pdf.json | COMMIT | WRITE | - | READ | - | READ | READ |
| denominators/cells.json | - | - | WRITE | - | - | READ | READ |
| denominators/diagram.json | - | - | WRITE | - | - | READ | READ |
| pipeline/contracts/pdf/* | - | WRITE | - | READ | - | READ | READ |

## Conflict Resolution

- Lane A writes pdf.json (pr_dry_run_ready_count update after contracts added)
- Lane B writes cells.json and diagram.json (source_version updates)
- Lane E reads after A/B complete — no conflict
- Lane F reads after all — no conflict
