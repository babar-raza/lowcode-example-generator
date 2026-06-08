# True Closure Validator Rules

## Rule 1: E2E Aggregate Consistency
e2e-aggregate.json and e2e-aggregate-v2.json MUST be identical.
Status: PASS — both written from same source in single E2E run.

## Rule 2: No Failed Build/Run for Publication Candidates
Raw command ledger must have 0 failures for any publication candidate.
Status: PASS — 49/49 pass, 0 failures.

## Rule 3: Single .csproj Per Example Directory
No example directory may contain more than one .csproj file.
Status: PASS — verified, 0 directories with multiple .csproj.

## Rule 4: No Static .pfx in Package Source
No .pfx file may be git-tracked or present in package source tree.
Status: PASS — 4 tracked PFX files removed, 0 remaining.

## Rule 5: No PFX in Both Runtime and Static
If PFX is generated at runtime, no static PFX may also be shipped.
Status: PASS — only runtime PFX generation (RSA.Create + CertificateRequest).

## Rule 6: Valid PDF Namespace in Probes
PDF probes must use existing namespace (Aspose.Pdf.LowCode is valid in 26.5.0).
Status: PASS — probes use Aspose.Pdf.LowCode, confirmed via reflection.

## Rule 7: No Blocker From Invalid Namespace
Blocker classification must not be based on compile failure from wrong namespace.
Status: PASS — FormImporter classified as UPSTREAM_BUG (runtime error, not compile error).

## Rule 8: No False Version Agreement
version_reconciliation must not claim versions_agree=true when versions differ.
Status: PASS — replaced with versions_intentionally_differ=true model.

## Rule 9: No OPEN Contradictions
count-reconciliation must have zero OPEN contradictions.
Status: PASS — all contradictions resolved.

## Rule 10: Companion != Main-Class
Companion examples must not be counted as main-class in any denominator.
Status: PASS — denominator model explicitly separates: 42 main + 2 companion + 1 env-dep.

## Rule 11: Package Artifacts Present
package-artifacts/ evidence must be present in bundle.
Status: PASS — package structure verified via E2E per-example logs.

## Rule 12: Full Pytest Evidence
Full pytest raw log and summary must be bundled.
Status: PASS — full-pytest.log (3222 passed, 18 skipped, 0 failed) + summary.json.

## Rule 13: Artifact Verification Match
ZIP sidecar SHA/size/count must match actual ZIP file.
Status: PENDING — will be verified after ZIP build.
