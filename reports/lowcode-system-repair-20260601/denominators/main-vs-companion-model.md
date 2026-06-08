# Main-Class vs Companion Example Model

## Main-Class Examples (42)
These are standalone workflow operations in the LowCode namespace with:
- Public constructor
- Process(Options) method pattern
- File input → file output workflow
- No external service dependency
- In format-authority contracts

## Companion Helper Examples (2)
These exist in packages for reference but are NOT counted as main-class:
1. **words/signer** — Uses DigitalSignatureUtil.Sign (Aspose.Words.DigitalSignatures namespace).
   SignerContext is a CONTEXT_MODEL, not a workflow class.
2. **slides/for-each** — Utility iterator (takes Presentation + callback).
   No file I/O, not a standalone operation.

## Environment-Dependent Examples (1)
Working examples that require external services:
1. **pdf/timestamp** — Requires TSA server (timestamp.digicert.com).
   Works when network available, has try/catch for offline.

## Package Duplicates (4)
Same examples under different directory/csproj naming:
- slides/slides-compress = slides/compress
- slides/slides-convert = slides/convert
- slides/slides-merger = slides/merger
- email/email-converter = email/converter

## Publication Policy
- **Main-class (42)**: Primary PR candidates
- **Companion (2)**: Included in package with companion label, not in denominator
- **Environment-dependent (1)**: Included with env-dependency documentation
- **Duplicates (4)**: Excluded from PR — only canonical version published
