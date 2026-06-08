# Runtime Certificate Generation Proof

## PDF Signature (examples/pdf/lowcode/signature/)
- Program.cs creates RSA.Create(2048) + CertificateRequest + CreateSelfSigned
- Writes test.pfx to working directory at runtime
- File is untracked (not committed to git)
- No static PFX in repo

## Words Signer (examples/words/lowcode/signer/)
- Program.cs creates RSA.Create(2048) + CertificateRequest + CreateSelfSigned
- Writes test-cert.pfx to working directory at runtime
- File is untracked (not committed to git)
- No static PFX in repo

## Verification
- Full scan of all 6 repos for .pfx/.p12/.key/.pem/.cer/.crt: 0 files found
- Both examples generate deterministic self-signed test certificates
- No production/private credentials in any repo
