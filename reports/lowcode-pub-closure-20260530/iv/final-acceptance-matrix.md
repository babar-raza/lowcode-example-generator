# Final Acceptance Matrix

| ID | Claim | Verdict |
|----|-------|---------|
| IV-001 | Fresh canonical generation with CANONICAL_TEMPLATE_GENERATIO | VERIFIED |
| IV-002 | Physical A/B idempotency executed | VERIFIED_PARTIAL |
| IV-003 | E2E aggregate matches 42/42 pass | VERIFIED |
| IV-004 | Output proof exists for every publication candidate | VERIFIED |
| IV-005 | Package artifacts bundled | VERIFIED |
| IV-006 | Program.cs and .csproj snapshots bundled | VERIFIED |
| IV-007 | Package denominator equals publication denominator or differ | VERIFIED |
| IV-008 | Words mail merge decision consistent | VERIFIED |
| IV-009 | Timestamp exclusion consistent | VERIFIED |
| IV-010 | Main-class gaps closed or accepted blocker packets | VERIFIED |
| IV-011 | No EXAMPLE_GAP or NEEDS_API_INVESTIGATION as final accepted  | VERIFIED |
| IV-012 | Fallback review has per-example results with output proof | VERIFIED |
| IV-013 | Full pytest raw log exists and passes | VERIFIED |
| IV-014 | raw-commands.log populated with stdout/stderr paths | VERIFIED |
| IV-015 | Final tracked dirty count is 0 | VERIFIED |
| IV-016 | Sidecar SHA/size/count matches actual ZIP | PENDING_ZIP_BUILD |
| IV-017 | No push/live PR/merge without approval gate | VERIFIED |
| IV-018 | Work-ahead did not bypass closure gates | VERIFIED |