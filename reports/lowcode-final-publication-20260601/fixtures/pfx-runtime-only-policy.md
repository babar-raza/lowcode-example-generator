# PFX Runtime-Only Policy Evidence

## Policy
No static .pfx files are committed to git or packaged in publication artifacts.
All examples requiring certificates generate them at runtime using:
```csharp
using var rsa = RSA.Create(2048);
var req = new CertificateRequest("CN=Test", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
var cert = req.CreateSelfSigned(DateTimeOffset.Now, DateTimeOffset.Now.AddYears(1));
File.WriteAllBytes("test.pfx", cert.Export(X509ContentType.Pfx, "password"));
```

## Affected Examples
| Example | Status |
|---------|--------|
| pdf/signature | Runtime PFX generation in Program.cs |
| pdf/timestamp | Runtime PFX generation in Program.cs |
| words/signer | Runtime PFX generation in Program.cs |

## Git History
- Commit `97e1173`: Removed 4 static PFX files via `git rm`
- Files removed:
  - `reports/lowcode-final-closure-pass3-20260530/generated-source/pdf/pdf-signature/test.pfx`
  - `workspace/fixture-validation/pdf-signature-harness/test.pfx`
  - `workspace/fixture-validation/pdf-timestamp-harness/test-ts.pfx`
  - `workspace/pr-dry-run/pdf-controlled-pilot-pr9/examples/pdf/lowcode/signature/test.pfx`

## Verification
No `.pfx` files exist in tracked git state. Runtime-generated PFX files may appear in working directories during E2E runs but are gitignored artifacts.
