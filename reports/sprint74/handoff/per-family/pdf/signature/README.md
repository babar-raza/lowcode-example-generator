# Signature — Apply Digital Signature to PDF

This example demonstrates how to digitally sign a PDF using the Aspose.PDF LowCode `Signature` plugin.

## What This Example Does

1. Creates a self-signed PFX certificate programmatically using `RSA.Create` and `CertificateRequest` (no external CA or TSA server required)
2. Creates a programmatic PDF input fixture containing sample text
3. Uses `SignOptions` to configure the signing operation (signer reason, contact, location, page number)
4. Calls `new Signature().Process(signOptions)` to apply the digital signature
5. Produces a signed PDF with an embedded digital signature (`/ByteRange` marker confirms valid PKCS#7 signature structure)

## API Used

- `Aspose.Pdf.LowCode.Signature` — LowCode plugin for applying digital signatures to PDF documents
- `Aspose.Pdf.LowCode.SignOptions` — Options class for configuring signature parameters (PFX path, password, signer metadata)
- `Aspose.Pdf.LowCode.FileDataSource` — File-based input/output data source

## Run

```bash
dotnet run
```

## Output

- `output.pdf` — PDF with embedded digital signature (PKCS#7 format, `/ByteRange` confirmed)

## Input and Output

The example takes a PDF file (`input.pdf`) as input.
The digitally signed PDF is saved as `output.pdf`.
