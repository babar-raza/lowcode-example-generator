# PFX Runtime Generation Policy

## Policy
All PFX certificate files used by examples MUST be generated at runtime via self-signed test certificates.
No static PFX file may be committed to git or included in publication packages.

## Affected Examples
1. **words/signer** — generates `test-cert.pfx` at runtime via `RSA.Create(2048)` + `CertificateRequest` + `CreateSelfSigned`
2. **pdf/signature** — generates `test.pfx` at runtime via same mechanism

## Runtime Generation Pattern
```csharp
using var rsa = RSA.Create(2048);
var req = new CertificateRequest("CN=Test", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
var cert = req.CreateSelfSigned(DateTimeOffset.Now, DateTimeOffset.Now.AddYears(1));
File.WriteAllBytes("test.pfx", cert.Export(X509ContentType.Pfx, "testpassword"));
```

## Security Properties
- Key: RSA 2048-bit (test-only)
- Subject: Test CN only (no real identity)
- Password: Public test-only value ("test-password" or "testpassword")
- Validity: 1 year from generation
- No production/CA certificate used

## Enforcement
1. Git-tracked PFX files removed: 4 files `git rm`'d in this sprint
2. Untracked PFX files deleted from package directories
3. PFX files regenerated at runtime during E2E runs are expected but not packaged
4. Validator added to fail any `.pfx` in package source tree

## Previous Violation
- `workspace/pr-dry-run/pdf-controlled-pilot-pr9/examples/pdf/lowcode/signature/test.pfx` was git-tracked
- `workspace/fixture-validation/pdf-signature-harness/test.pfx` was git-tracked
- `workspace/fixture-validation/pdf-timestamp-harness/test-ts.pfx` was git-tracked
- `reports/lowcode-final-closure-pass3-20260530/generated-source/pdf/pdf-signature/test.pfx` was git-tracked
- All removed via `git rm` in this sprint
