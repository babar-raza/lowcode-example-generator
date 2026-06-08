# PFX Generation Proof

## words/signer Program.cs (lines 16-31)
Generates `test-cert.pfx` at runtime:
- RSA.Create(2048)
- CertificateRequest("CN=Aspose Test Signer, O=Test, C=US")
- CreateSelfSigned(Now-1day, Now+1year)
- Export(X509ContentType.Pfx, "test-password")
- File.WriteAllBytes("test-cert.pfx", bytes)

## pdf/signature Program.cs (lines 10-15)
Generates `test.pfx` at runtime:
- RSA.Create(2048)
- CertificateRequest("cn=TestSign")
- X509BasicConstraintsExtension added
- CreateSelfSigned(Now, Now+1year)
- Export(X509ContentType.Pfx, "testpassword")
- File.WriteAllBytes("test.pfx", bytes)

## E2E Evidence
Both examples build=0, run=0 in E2E suite (49/49 PASS).
PFX files are regenerated on each run and consumed immediately.
No static PFX required for build or run.

## No-Static-PFX Check
After removing all tracked PFX and deleting untracked:
- `git ls-files '*.pfx'` returns empty
- `find workspace/pr-dry-run/ -name '*.pfx'` returns empty (before E2E run)
- PFX regenerated during E2E is runtime artifact only
