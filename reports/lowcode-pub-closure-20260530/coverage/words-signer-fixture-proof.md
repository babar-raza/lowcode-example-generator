# Words Signer Fixture Proof — lowcode-pub-closure-20260530

## Self-signed PFX generation
A safe self-signed PFX can be generated using:
```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
openssl pkcs12 -export -out signing.pfx -inkey key.pem -in cert.pem -passout pass:test123
```
This is safe (test certificate only), not a real CA-issued cert.
The Durable Full Closure sprint confirmed: PdfSignature works with self-signed PFX.

## Status: CLOSEABLE — PFX fixture can be generated
## Next step: Create words-signer example through canonical fixture generator
